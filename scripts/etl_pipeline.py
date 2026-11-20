"""
================================================================================
ETL Pipeline: Pengolahan Data Airbnb Provinsi Lampung & Kabupaten Lampung Tengah
Mata Kuliah: Big Data & Data Analytics
Target Data Warehouse: Google BigQuery
================================================================================
"""

import os
import glob
import json
import numpy as np
import pandas as pd


def run_etl(data_dir: str = 'datasets', output_dir: str = 'output'):
    print("=" * 80)
    print("🚀 MEMULAI PIPELINE ETL AIRBNB PROVINSI LAMPUNG")
    print("=" * 80)

    # Pastikan folder output ada
    os.makedirs(output_dir, exist_ok=True)

    # --------------------------------------------------------------------------
    # TAHAP 1: EXTRACT & MERGE DATA WILAYAH
    # --------------------------------------------------------------------------
    print("\n[TAHAP 1] EXTRACT & MERGE DATASET...")
    
    # Ambil 12 file kabupaten/kota, kecualikan file gabungan 'AirBnB_Lampung_All.csv'
    all_csv_files = glob.glob(os.path.join(data_dir, '*.csv'))
    regional_files = sorted([f for f in all_csv_files if 'Lampung_All' not in os.path.basename(f)])
    
    print(f"-> Ditemukan {len(regional_files)} file CSV per kabupaten/kota.")
    
    dfs = []
    file_stats = []
    for f in regional_files:
        df_temp = pd.read_csv(f)
        fname = os.path.basename(f)
        file_stats.append({
            'file': fname,
            'baris': len(df_temp),
            'wilayah': df_temp['wilayah'].iloc[0] if 'wilayah' in df_temp.columns and len(df_temp) > 0 else 'N/A'
        })
        dfs.append(df_temp)
    
    df_raw = pd.concat(dfs, ignore_index=True)
    initial_rows = len(df_raw)
    
    # Validasi terhadap file AirBnB_Lampung_All.csv
    all_file_path = os.path.join(data_dir, 'AirBnB_Lampung_All.csv')
    if os.path.exists(all_file_path):
        df_all_check = pd.read_csv(all_file_path)
        print(f"-> Validasi Baris:")
        print(f"   * Total gabungan 12 file kabupaten/kota : {initial_rows} baris")
        print(f"   * Total pada file AirBnB_Lampung_All.csv: {len(df_all_check)} baris")
        if initial_rows == len(df_all_check):
            print("   [VALID] Jumlah baris 100% konsisten antara gabungan 12 file vs file gabungan All.")
        else:
            print("   [PERINGATAN] Terdapat perbedaan jumlah baris!")
    
    # --------------------------------------------------------------------------
    # TAHAP 2: DATA CLEANING & STANDARISASI
    # --------------------------------------------------------------------------
    print("\n[TAHAP 2] DATA CLEANING & STANDARISASI...")
    
    # Standarisasi nama kolom ke snake_case BigQuery standard
    df_clean = df_raw.copy()
    df_clean.columns = [c.strip().lower().replace(' ', '_') for c in df_clean.columns]
    
    # Ubah nama kolom 'wilayah' menjadi 'kabupaten_kota'
    if 'wilayah' in df_clean.columns:
        df_clean = df_clean.rename(columns={'wilayah': 'kabupaten_kota'})
    
    # Bersihkan whitespace di seluruh kolom bertipe string/object
    for col in df_clean.select_dtypes(include=['object', 'string']).columns:
        df_clean[col] = df_clean[col].astype(str).str.strip()
    
    # Dokumentasi Missing Values Sebelum Cleaning
    missing_before = df_clean.isnull().sum()
    
    # Pengecekan & Penghapusan Duplikat Baris
    exact_duplicates_count = df_clean.duplicated().sum()
    print(f"-> Pengecekan Duplikat Persis (Exact Duplicates): {exact_duplicates_count} baris.")
    if exact_duplicates_count > 0:
        df_clean = df_clean.drop_duplicates().reset_index(drop=True)
    
    # Pembersihan Kolom Harga
    # Format asal: "Rp 1,957,119" -> ubah menjadi integer numerik
    df_clean['harga'] = (
        df_clean['harga']
        .str.replace('Rp', '', regex=False)
        .str.replace(',', '', regex=False)
        .str.strip()
    )
    df_clean['harga'] = pd.to_numeric(df_clean['harga'], errors='coerce')
    
    # Deteksi dan eliminasi harga anomali (<= 0 atau kosong)
    anomalous_prices = (df_clean['harga'] <= 0) | (df_clean['harga'].isna())
    num_anomalies = anomalous_prices.sum()
    print(f"-> Pengecekan Harga Anomali (<= 0 atau Null): {num_anomalies} baris ditemukan.")
    if num_anomalies > 0:
        df_clean = df_clean[~anomalous_prices].copy()
    df_clean['harga'] = df_clean['harga'].astype('int64')
    
    # Pembersihan Kolom Jumlah Review
    df_clean['jumlah_review'] = pd.to_numeric(df_clean['jumlah_review'], errors='coerce').fillna(0).astype('int64')
    
    # Pembersihan Kolom Rating
    # Rating 'New' adalah listing baru tanpa rating angka
    is_new = df_clean['rating'].str.lower() == 'new'
    df_clean['is_new_listing'] = is_new
    
    # Nilai rating numerik (NaN jika 'New', 'N/A', atau kosong)
    df_clean['rating'] = pd.to_numeric(
        df_clean['rating'].replace({'New': np.nan, 'N/A': np.nan, 'nan': np.nan, 'None': np.nan}),
        errors='coerce'
    )
    
    # --------------------------------------------------------------------------
    # TAHAP 3: FEATURE ENGINEERING (NILAI BISNIS & BIGQUERY)
    # --------------------------------------------------------------------------
    print("\n[TAHAP 3] FEATURE ENGINEERING...")
    
    # 1. Ekstraksi listing_id dari URL link
    df_clean['listing_id'] = df_clean['link'].apply(
        lambda x: str(x).split('rooms/')[-1].split('?')[0].strip()
    )
    
    # 2. Parsing nama menjadi tipe_properti, lokasi_spesifik, dan judul_listing
    def parse_listing_name(name_str):
        prop_type, loc, title = 'Other', 'Lampung', name_str
        if ' in ' in name_str:
            parts = name_str.split(' in ', 1)
            prop_type = parts[0].strip()
            rest = parts[1]
            if ' - ' in rest:
                loc_parts = rest.split(' - ', 1)
                loc = loc_parts[0].strip()
                title = loc_parts[1].strip()
            else:
                loc = rest.strip()
                title = rest.strip()
        elif ' - ' in name_str:
            parts = name_str.split(' - ', 1)
            loc = parts[0].strip()
            title = parts[1].strip()
        return pd.Series([prop_type, loc, title])
    
    df_clean[['tipe_properti', 'lokasi_spesifik', 'judul_listing']] = df_clean['nama'].apply(parse_listing_name)
    
    # 3. Label Wilayah Fokus (Studi Komparatif Lampung Tengah)
    df_clean['wilayah_fokus'] = np.where(
        df_clean['kabupaten_kota'] == 'Kabupaten Lampung Tengah',
        'Kabupaten Lampung Tengah',
        'Kabupaten/Kota Lain (Lampung)'
    )
    
    # 4. Segmentasi Harga (price_tier) Berdasarkan Kuartil
    q1_price = df_clean['harga'].quantile(0.25)
    q3_price = df_clean['harga'].quantile(0.75)
    print(f"-> Kuartil Harga Dataset:")
    print(f"   * Q1 (Batas Atas Budget)   : Rp {q1_price:,.0f}")
    print(f"   * Q3 (Batas Bawah Premium) : Rp {q3_price:,.0f}")
    
    def classify_price_tier(p):
        if p <= q1_price:
            return 'Budget'
        elif p <= q3_price:
            return 'Mid-Range'
        else:
            return 'Premium'
            
    df_clean['price_tier'] = df_clean['harga'].apply(classify_price_tier)
    
    # 5. Fitur has_reviews
    df_clean['has_reviews'] = df_clean['jumlah_review'] > 0
    
    # 6. Fitur rating_kategori
    def classify_rating_category(row):
        r = row['rating']
        if pd.isna(r):
            if row['is_new_listing']:
                return 'Listing Baru (New)'
            return 'Tanpa Rating'
        elif r >= 4.8:
            return 'Sangat Bagus (4.8 - 5.0)'
        elif r >= 4.5:
            return 'Bagus (4.5 - 4.79)'
        else:
            return 'Cukup (< 4.5)'
            
    df_clean['rating_kategori'] = df_clean.apply(classify_rating_category, axis=1)
    
    # Urutkan kolom secara logis dan terstruktur
    final_columns = [
        'listing_id',
        'nama',
        'tipe_properti',
        'lokasi_spesifik',
        'judul_listing',
        'kabupaten_kota',
        'wilayah_fokus',
        'harga',
        'rating',
        'rating_kategori',
        'is_new_listing',
        'jumlah_review',
        'has_reviews',
        'price_tier',
        'link'
    ]
    df_final = df_clean[final_columns].copy()
    
    # --------------------------------------------------------------------------
    # TAHAP 4: EXPORT DATA BERSIH & SKEMA BIGQUERY
    # --------------------------------------------------------------------------
    print("\n[TAHAP 4] EXPORT DATA FINAL & SKEMA BIGQUERY...")
    
    clean_csv_path = os.path.join(output_dir, 'airbnb_lampung_clean.csv')
    df_final.to_csv(clean_csv_path, index=False, encoding='utf-8')
    print(f"-> File dataset bersih tersimpan di: {clean_csv_path}")
    
    # Buat Schema JSON untuk Google BigQuery
    bq_schema = [
        {"name": "listing_id", "type": "STRING", "mode": "REQUIRED", "description": "ID unik listing Airbnb yang diekstrak dari URL tautan"},
        {"name": "nama", "type": "STRING", "mode": "REQUIRED", "description": "Nama lengkap listing akomodasi pada platform Airbnb"},
        {"name": "tipe_properti", "type": "STRING", "mode": "NULLABLE", "description": "Tipe akomodasi (Home, Apartment, Hotel, Guesthouse, Villa, dll.)"},
        {"name": "lokasi_spesifik", "type": "STRING", "mode": "NULLABLE", "description": "Lokasi spesifik, nama kecamatan, atau area properti"},
        {"name": "judul_listing", "type": "STRING", "mode": "NULLABLE", "description": "Judul deskriptif properti hasil parsing nama"},
        {"name": "kabupaten_kota", "type": "STRING", "mode": "REQUIRED", "description": "Nama resmi kabupaten atau kota di Provinsi Lampung"},
        {"name": "wilayah_fokus", "type": "STRING", "mode": "REQUIRED", "description": "Klasifikasi komparasi: Kabupaten Lampung Tengah vs Kabupaten/Kota Lain (Lampung)"},
        {"name": "harga", "type": "INT64", "mode": "REQUIRED", "description": "Harga sewa menginap per malam dalam mata uang Rupiah (IDR)"},
        {"name": "rating", "type": "FLOAT64", "mode": "NULLABLE", "description": "Skor rating ulasan pengguna Airbnb (skala 1.0 - 5.0)"},
        {"name": "rating_kategori", "type": "STRING", "mode": "REQUIRED", "description": "Kategori performa ulasan listing akomodasi"},
        {"name": "is_new_listing", "type": "BOOL", "mode": "REQUIRED", "description": "Penanda listing berstatus baru (New di Airbnb)"},
        {"name": "jumlah_review", "type": "INT64", "mode": "REQUIRED", "description": "Jumlah ulasan tamu yang diterima listing"},
        {"name": "has_reviews", "type": "BOOL", "mode": "REQUIRED", "description": "Penanda apakah listing telah memiliki ulasan tamu"},
        {"name": "price_tier", "type": "STRING", "mode": "REQUIRED", "description": "Segmentasi tarif sewa berbasis kuartil: Budget, Mid-Range, Premium"},
        {"name": "link", "type": "STRING", "mode": "REQUIRED", "description": "Tautan URL langsung menuju halaman listing di situs Airbnb"}
    ]
    
    schema_path = os.path.join(output_dir, 'bigquery_schema.json')
    with open(schema_path, 'w', encoding='utf-8') as f:
        json.dump(bq_schema, f, indent=2, ensure_ascii=False)
    print(f"-> Skema BigQuery tersimpan di: {schema_path}")
    
    # --------------------------------------------------------------------------
    # TAHAP 5: RINGKASAN VERIFIKASI TERMINAL
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("📊 RINGKASAN VERIFIKASI PIPELINE ETL (HASIL AKHIR)")
    print("=" * 80)
    
    print(f"1. Metrik Baris Data:")
    print(f"   * Jumlah Baris Awal       : {initial_rows} baris")
    print(f"   * Duplikat Terhapus       : {exact_duplicates_count} baris")
    print(f"   * Harga Anomali Terhapus  : {num_anomalies} baris")
    print(f"   * Jumlah Baris Akhir      : {len(df_final)} baris")
    print(f"   * Jumlah Listing Unik (ID): {df_final['listing_id'].nunique()} listing")
    
    print(f"\n2. Daftar Kolom Final & Tipe Data:")
    for col, dtype in df_final.dtypes.items():
        null_count = df_final[col].isnull().sum()
        print(f"   - {col:<18} | {str(dtype):<10} | Null: {null_count}")
        
    print(f"\n3. Distribusi Listing per Kabupaten/Kota:")
    counts = df_final['kabupaten_kota'].value_counts()
    for wilayah, count in counts.items():
        if wilayah == 'Kabupaten Lampung Tengah':
            print(f"   >>> {wilayah:<30}: {count:>3} listing (WILAYAH FOKUS STUDI) <<<")
        else:
            print(f"     - {wilayah:<30}: {count:>3} listing")
            
    print(f"\n4. Statistik Komparatif Kunci:")
    lt_data = df_final[df_final['wilayah_fokus'] == 'Kabupaten Lampung Tengah']
    other_data = df_final[df_final['wilayah_fokus'] == 'Kabupaten/Kota Lain (Lampung)']
    
    print(f"   * Kabupaten Lampung Tengah:")
    print(f"     - Rata-rata Harga : Rp {lt_data['harga'].mean():,.0f}")
    print(f"     - Median Harga    : Rp {lt_data['harga'].median():,.0f}")
    print(f"     - Rentang Harga   : Rp {lt_data['harga'].min():,.0f} - Rp {lt_data['harga'].max():,.0f}")
    print(f"     - Listing Ber-rating: {lt_data['rating'].notna().sum()} dari {len(lt_data)} ({lt_data['is_new_listing'].sum()} berlabel 'New')")
    
    print(f"   * Kabupaten/Kota Lain (Lampung):")
    print(f"     - Rata-rata Harga : Rp {other_data['harga'].mean():,.0f}")
    print(f"     - Median Harga    : Rp {other_data['harga'].median():,.0f}")
    print(f"     - Rentang Harga   : Rp {other_data['harga'].min():,.0f} - Rp {other_data['harga'].max():,.0f}")
    print(f"     - Rata-rata Rating: {other_data['rating'].mean():.2f}")
    
    print("\n" + "=" * 80)
    print("✅ PIPELINE ETL SELESAI DENGAN SUKSES!")
    print("=" * 80)

    return df_final


if __name__ == '__main__':
    run_etl()
