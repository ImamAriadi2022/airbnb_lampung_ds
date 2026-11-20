# Analisis Pasar dan Pemetaan Daya Saing Akomodasi Digital Airbnb di Provinsi Lampung
### Studi Komparatif Kabupaten Lampung Tengah

**Mata Kuliah:** Big Data & Data Analytics  
**Fokus Penelitian:** Evaluasi Lanskap Pasar Digital Airbnb Provinsi Lampung dan Pemetaan Potensi Daya Saing Kabupaten Lampung Tengah  
**Teknologi:** Python (Pandas, NumPy), Google BigQuery, Google Looker Studio, Jupyter Notebook / Google Colab  

---

## 📌 Ringkasan Proyek

Proyek ini bertujuan untuk menganalisis penetrasi, tarif, performa ulasan, serta struktur penawaran akomodasi digital (Airbnb) di seluruh wilayah Provinsi Lampung, dengan fokus komparatif mendalam terhadap **Kabupaten Lampung Tengah**.

Data mentah bersumber dari hasil *web scraping* pasar Airbnb di 12 kabupaten/kota di Provinsi Lampung. Melalui pipeline ETL yang terstandarisasi, data dibersihkan, diintegrasikan, diperkaya dengan rekayasa fitur bisnis (*feature engineering*), serta disiapkan untuk dimuat ke Data Warehouse **Google BigQuery** dan divisualisasikan pada **Google Looker Studio**.

---

## 📁 Struktur Direktori Proyek

```text
airbnb_lampung_ds/
│
├── datasets/                                 # Kumpulan data mentah (raw data)
│   ├── AirBnB_Kab_Lampung_Barat.csv
│   ├── AirBnB_Kab_Lampung_Selatan.csv
│   ├── AirBnB_Kab_Lampung_Tengah.csv         # File fokus studi komparatif (9 baris)
│   ├── AirBnB_Kab_Lampung_Timur.csv
│   ├── AirBnB_Kab_Pesawaran.csv
│   ├── AirBnB_Kab_Pesisir_Barat.csv
│   ├── AirBnB_Kab_Pringsewu.csv
│   ├── AirBnB_Kab_Tanggamus.csv
│   ├── AirBnB_Kab_Tulang_Bawang_Barat.csv
│   ├── AirBnB_Kab_Way_Kanan.csv
│   ├── AirBnB_Kota_Bandar_Lampung.csv
│   ├── AirBnB_Kota_Metro.csv
│   └── AirBnB_Lampung_All.csv                # File gabungan referensi (832 baris)
│
├── notebooks/
│   └── ETL_Airbnb_Lampung_BigData.ipynb      # Notebook utama ETL interaktif (Colab-ready)
│
├── scripts/
│   └── etl_pipeline.py                       # Script Python ETL modular untuk terminal
│
├── output/
│   ├── airbnb_lampung_clean.csv              # Dataset final bersih siap BigQuery (832 baris)
│   ├── bigquery_schema.json                  # Definisi skema resmi kolom Google BigQuery
│   └── insight_dan_kpi.md                    # Laporan temuan aktual & panduan Looker Studio
│
├── sql/
│   └── bigquery_analysis.sql                 # 6 Kueri BigQuery Standard SQL siap pakai
│
├── requirements.txt                          # Daftar pustaka Python yang dibutuhkan
└── README.md                                 # Dokumentasi lengkap proyek
```

---

## ⚙️ Tahapan Pipeline Data Engineering (ETL)

### 1. Extract & Merge (Integrasi Multi-Sumber)
- Membaca 12 berkas CSV kabupaten/kota secara dinamis.
- Mengecualikan `AirBnB_Lampung_All.csv` pada proses penggabungan untuk mencegah penggandaan data.
- Memvalidasi total baris gabungan 12 berkas (832 baris) terhadap `AirBnB_Lampung_All.csv` (832 baris) dengan integritas data 100% konsisten.

### 2. Data Cleaning & Standarisasi
- **Standarisasi Kolom:** Mengubah nama kolom menjadi huruf kecil format `snake_case` (standar BigQuery). Mengubah kolom `wilayah` menjadi `kabupaten_kota`.
- **Whitespace Sanitization:** Menghilangkan kelebihan spasi di awal dan akhir seluruh data teks.
- **Pembersihan Kolom Harga (`harga`):** Menghapus simbol `"Rp"`, pemisah ribuan `","`, dan spasi, mengonversi ke tipe bilangan bulat (`int64`), serta memvalidasi tidak ada harga $\le 0$ atau kosong.
- **Pembersihan Kolom Rating (`rating`):** Menandai listing baru (`New`), mengonversi nilai numerik ke `float64`, dan mengalihkan nilai `'New'` serta `'N/A'` menjadi `NaN` (`NULL` di BigQuery).
- **Pembersihan Kolom Ulasan (`jumlah_review`):** Mengonversi ke `int64` dengan penanganan nilai kosong menjadi `0`.

### 3. Feature Engineering (Nilai Tambah Bisnis)
- **`listing_id`:** Ekstraksi nomor ID unik listing Airbnb dari URL tautan properti.
- **`tipe_properti`, `lokasi_spesifik`, `judul_listing`:** Dekomposisi struktural dari kolom teks `nama`.
- **`wilayah_fokus`:** Label komparasi (`"Kabupaten Lampung Tengah"` vs `"Kabupaten/Kota Lain (Lampung)"`).
- **`price_tier`:** Segmentasi harga sewa berbasis kuartil:
  - **Budget:** $\le$ Rp 1.955.692 ($Q_1$)
  - **Mid-Range:** Rp 1.955.693 – Rp 5.497.506 ($Q_1$ s.d. $Q_3$)
  - **Premium:** $>$ Rp 5.497.506 ($> Q_3$)
- **`has_reviews`:** Penanda boolean listing aktif yang telah memiliki ulasan tamu (`jumlah_review > 0`).
- **`rating_kategori`:** Klasifikasi kualitas ulasan (`"Sangat Bagus (4.8 - 5.0)"`, `"Bagus (4.5 - 4.79)"`, `"Cukup (< 4.5)"`, `"Listing Baru (New)"`, `"Tanpa Rating"`).

---

## 📊 Metrik Aktual & Temuan Kunci Analisis

Berdasarkan eksekusi pada dataset bersih (`output/airbnb_lampung_clean.csv`):

| Metrik Kunci | Agregat Provinsi Lampung | Kabupaten Lampung Tengah |
| :--- | :---: | :---: |
| **Total Listing Observasi Pasar** | 832 | 9 (1,08% pasar) |
| **Jumlah Properti Fisik Unik** | 306 | 9 |
| **Rata-rata Tarif per Malam** | Rp 5.091.958 | Rp 2.485.870 |
| **Median Tarif per Malam** | Rp 3.000.000 | Rp 2.730.166 |
| **Rata-rata Rating Ulasan** | 4,81 / 5,00 | N/A (Belum ada ulasan) |
| **Listing Memiliki Ulasan** | 209 listing (25,12%) | 0 listing (0,00%) |
| **Komposisi Price Tier** | Budget (25%), Mid (50%), Prem (25%) | Budget (33,3%), Mid (66,7%), Prem (0%) |

### *Highlight Temuan Utama (Shadow Supply)*:
9 listing yang terindeks di Kabupaten Lampung Tengah secara geografis berlokasi di wilayah perbatasan (5 di Kota Metro, 2 di Kotabumi, 2 di Tulang Bawang Barat). Hal ini mengindikasikan adanya **kekosongan pasokan digital murni (*supply void*)** di pusat Lampung Tengah (Terbanggi Besar, Bandar Jaya, Gunung Sugih), sehingga permintaan transit saat ini mengalir ke daerah penyangga seperti Kota Metro.

Dokumentasi analisis lengkap dan rekomendasi strategis dapat dibaca pada:  
👉 **[`output/insight_dan_kpi.md`](file:///c:/programming/airbnb_lampung_ds/output/insight_dan_kpi.md)**

---

## 🚀 Panduan Menjalankan Proyek

### 1. Prasyarat & Instalasi Lingkungan
Pastikan Python 3.10+ telah terpasang, lalu instal paket dependensi:
```bash
pip install -r requirements.txt
```

### 2. Eksekusi Script Pipeline ETL (Terminal)
Jalankan script ETL dari *root* direktori proyek:
```bash
python scripts/etl_pipeline.py
```
Script akan memproses seluruh data mentah, mengekspor berkas ke folder `output/`, dan menampilkan ringkasan verifikasi otomatis di terminal.

### 3. Menjalankan Jupyter Notebook
Buka dan jalankan notebook melalui JupyterLab, VS Code, atau unggah ke Google Colab:
```bash
jupyter notebook notebooks/ETL_Airbnb_Lampung_BigData.ipynb
```

---

## ☁️ Integrasi Google BigQuery

### Skema Tabel Data Warehouse
Skema formal tersimpan di `output/bigquery_schema.json` yang memuat 15 atribut kolom dengan tipe data BigQuery yang tepat (`STRING`, `INT64`, `FLOAT64`, `BOOL`).

### Memuat Data Menggunakan Google Cloud SDK (`bq` CLI)
```bash
# 1. Buat Dataset BigQuery (jika belum ada)
bq --location=asia-southeast2 mk -d \
    --description "Dataset Analisis Pasar Airbnb Provinsi Lampung" \
    bigdata-airbnb-lampung:airbnb_lampung_ds

# 2. Muat dataset bersih menggunakan skema JSON
bq load \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --replace \
    bigdata-airbnb-lampung:airbnb_lampung_ds.listings_clean \
    ./output/airbnb_lampung_clean.csv \
    ./output/bigquery_schema.json
```

### Menjalankan Kueri Analisis Bisnis
File **`sql/bigquery_analysis.sql`** memuat 6 kueri Standard SQL siap pakai:
1. Ringkasan Pasar Airbnb per Kabupaten/Kota.
2. Studi Komparatif Kabupaten Lampung Tengah vs Wilayah Lain di Lampung.
3. Distribusi Segmentasi Tarif (*Price Tier*) per Wilayah.
4. Analisis Dominasi Tipe Properti & Akomodasi.
5. Top 10 Listing Terbaik Berperingkat Bintang 5 di Provinsi Lampung.
6. Profil Terperinci Listing Pasar Kabupaten Lampung Tengah.

---

## 📈 Visualisasi Google Looker Studio

Panduan konfigurasi dashboard Looker Studio:
- **Scorecards:** Total Listing Pasar (832), Listing Unik (306), Rata-rata Tarif (Rp 5.091.958), Rata-rata Rating (4,81).
- **Interactive Filters:** `wilayah_fokus`, `kabupaten_kota`, `price_tier`, `tipe_properti`.
- **Charts:**
  - *Geo Map / Bar Chart:* Persebaran listing per kabupaten/kota.
  - *100% Stacked Bar Chart:* Komposisi keterjangkauan tarif (*Price Tier*).
  - *Clustered Bar Chart:* Rata-rata tarif per tipe akomodasi (*Home*, *Apartment*, *Villa*, dll.).
  - *Leaderboard Table:* Daftar listing berkinerja terbaik dengan tautan langsung ke Airbnb.

---
**Tim Peneliti:** Mahasiswa Big Data & Data Analytics  
**Tahun:** 2026
