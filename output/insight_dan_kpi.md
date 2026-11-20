# Laporan Analisis Pasar & Panduan Dashboard Looker Studio
## Analisis Pasar dan Pemetaan Daya Saing Akomodasi Digital Airbnb di Provinsi Lampung: Studi Komparatif Kabupaten Lampung Tengah

**Mata Kuliah:** Big Data & Data Analytics  
**Peran:** Senior Data Engineer & Business Intelligence Analyst  
**Sumber Data Bersih:** `output/airbnb_lampung_clean.csv` (832 baris observasi pasar, 306 unit akomodasi fisik unik)  
**Tabel Target BigQuery:** `bigdata-airbnb-lampung.airbnb_lampung_ds.listings_clean`  

---

## 1. Ringkasan Eksekutif & Metrik Aktual Pasar

Berdasarkan hasil eksekusi pipeline ETL Python dan integrasi 12 kabupaten/kota di Provinsi Lampung, berikut adalah ringkasan data aktual pasar akomodasi digital Airbnb:

| Parameter Metrik | Nilai Agregat Provinsi Lampung | Kabupaten Lampung Tengah (Fokus) | Kabupaten/Kota Lain (Lampung) |
| :--- | :---: | :---: | :---: |
| **Total Observasi Listing Pasar** | **832** listing | **9** listing (1,08%) | **823** listing (98,92%) |
| **Jumlah Properti Unik (Distinct ID)** | **306** properti unik | **9** listing terdeteksi | **306** properti unik |
| **Rata-rata Tarif Sewa per Malam** | **Rp 5.091.958** | **Rp 2.485.870** (-51,18%) | **Rp 5.120.457** |
| **Median Tarif Sewa per Malam** | **Rp 3.000.000** | **Rp 2.730.166** | **Rp 3.000.000** |
| **Tarif Termurah (Min)** | **Rp 780.280** | **Rp 1.021.353** | **Rp 780.280** |
| **Tarif Termahal (Max)** | **Rp 175.659.055** | **Rp 4.034.061** | **Rp 175.659.055** |
| **Rata-rata Rating Konsumen** | **4,81 / 5,00** | **N/A** (Belum Ada Ulasan) | **4,81 / 5,00** |
| **Listing Memiliki Ulasan (Aktif)** | **209** listing (25,12%) | **0** listing (0,00%) | **209** listing (25,39%) |
| **Listing Berstatus Baru (*New*)** | **62** listing (7,45%) | **1** listing (11,11%) | **61** listing (7,41%) |
| **Total Akumulasi Ulasan Tamu** | **2.534** ulasan | **0** ulasan | **2.534** ulasan |

---

## 2. Struktur Distribusi Pasar per Kabupaten/Kota

Tabel berikut menunjukkan distribusi pasokan listing dan tarif di 12 wilayah administratif yang disurvei:

| Peringkat | Kabupaten / Kota | Total Listing | Rata-rata Tarif (IDR) | Median Tarif (IDR) | Rata-rata Rating | Listing Berulasan |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | Kabupaten Lampung Selatan | 203 | Rp 4.130.202 | Rp 2.671.060 | 4,79 | 48 |
| 2 | Kabupaten Pesawaran | 198 | Rp 4.295.224 | Rp 2.671.060 | 4,81 | 45 |
| 3 | Kota Bandar Lampung | 152 | Rp 4.058.599 | Rp 2.709.148 | 4,83 | 45 |
| 4 | Kabupaten Lampung Timur | 97 | Rp 3.356.797 | Rp 2.555.000 | 4,76 | 28 |
| 5 | Kabupaten Lampung Barat | 51 | Rp 8.055.419 | Rp 5.238.002 | 4,79 | 17 |
| 6 | Kabupaten Pesisir Barat | 51 | Rp 8.055.419 | Rp 5.238.002 | 4,79 | 17 |
| 7 | Kabupaten Pringsewu | 42 | Rp 11.337.789 | Rp 4.335.178 | 4,95 | 7 |
| 8 | Kota Metro | 17 | Rp 3.611.232 | Rp 2.587.161 | 4,83 | 1 |
| **9** | **Kabupaten Lampung Tengah** | **9** | **Rp 2.485.870** | **Rp 2.730.166** | **N/A** | **0** |
| 10 | Kabupaten Tanggamus | 8 | Rp 26.690.722 | Rp 5.363.624 | 5,00 | 1 |
| 11 | Kabupaten Tulang Bawang Barat | 2 | Rp 3.865.737 | Rp 3.865.737 | N/A | 0 |
| 12 | Kabupaten Way Kanan | 2 | Rp 1.123.316 | Rp 1.123.316 | N/A | 0 |

---

## 3. Segmentasi Tarif (*Price Tier*) & Profil Pasokan

Segmentasi harga dihitung berbasis kuartil distribusi harga sewa aktual:
- **Budget Tier ($\le Q_1$):** $\le$ **Rp 1.955.692** (208 listing / 25,00%)
- **Mid-Range Tier ($Q_1 < \text{Harga} \le Q_3$):** **Rp 1.955.693 – Rp 5.497.506** (418 listing / 50,24%)
- **Premium Tier ($> Q_3$):** $>$ **Rp 5.497.506** (206 listing / 24,76%)

### Perbandingan Komposisi Segmen Harga:
- **Kabupaten Lampung Tengah:** 3 listing *Budget* (33,33%), 6 listing *Mid-Range* (66,67%), dan **0 listing *Premium* (0,00%)**.
- **Provinsi Lampung (Keseluruhan):** Terdistribusi seimbang dengan proporsi *Premium* mencapai 24,76%, didorong oleh vila pesisir pantai di Krui (Pesisir Barat) dan *resort* pulau privat di Pesawaran/Lampung Selatan.

---

## 4. Analisis Terperinci Listing Kabupaten Lampung Tengah

Hasil inspeksi granulasi mendalam terhadap 9 listing yang terindeks pada kata kunci pencarian Kabupaten Lampung Tengah:

| No | Judul Listing | Tipe Properti | Lokasi Riil Hasil Parsing | Tarif / Malam (IDR) | Price Tier | Status Listing |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | Rooms in Kotabumi - Home Stay Oma Noet | Rooms | Kotabumi (Lampung Utara) | Rp 1.021.353 | Budget | Tanpa Rating (0 ulasan) |
| 2 | Hotel in Abung Selatan - STD Deluxe @ Esemka Hotel | Hotel | Abung Selatan (Lampung Utara) | Rp 1.225.279 | Budget | Tanpa Rating (0 ulasan) |
| 3 | Guesthouse in Metro - Flo-Rich Exclusive Homestay | Guesthouse | Metro (Kota Metro) | Rp 1.426.471 | Budget | Tanpa Rating (0 ulasan) |
| 4 | Home in Metro Pusat - Comfortable homestay | Home | Metro Pusat (Kota Metro) | Rp 2.567.648 | Mid-Range | Tanpa Rating (0 ulasan) |
| 5 | Hotel in Metro Pusat - Grand Venetian Hotel | Hotel | Metro Pusat (Kota Metro) | Rp 2.730.166 | Mid-Range | Tanpa Rating (0 ulasan) |
| 6 | Home in Metro Utara - House in Metro North Lampung | Home | Metro Utara (Kota Metro) | Rp 2.810.178 | Mid-Range | Tanpa Rating (0 ulasan) |
| 7 | Home in Kecamatan Metro Utara - House at Metro | Home | Metro Utara (Kota Metro) | Rp 2.860.260 | Mid-Range | **Listing Baru (*New*)** |
| 8 | Hotel in Tulang Bawang Tengah - Berugo Cottage Tubaba | Hotel | Tulang Bawang Tengah | Rp 3.697.413 | Mid-Range | Tanpa Rating (0 ulasan) |
| 9 | Hotel in Tulang Bawang Tengah - Berugo Cottage | Hotel | Tulang Bawang Tengah | Rp 4.034.061 | Mid-Range | Tanpa Rating (0 ulasan) |

> [!IMPORTANT]
> **Temuan Kritis (*Shadow Supply Phenomenon*):**
> Tidak ditemukan satupun listing Airbnb yang secara geografis berada murni di dalam pusat administrasi/ekonomi Kabupaten Lampung Tengah (seperti Gunung Sugih, Terbanggi Besar, atau Bandar Jaya). Seluruh listing yang muncul merupakan akomodasi di perbatasan (5 di Kota Metro, 2 di Kotabumi/Lampung Utara, dan 2 di Tulang Bawang Barat) yang ditarik oleh algoritma pencarian Airbnb akibat **ketiadaan pasokan digital lokal**.

---

## 5. Insight Bisnis Utama (Empirical Business Insights)

1. **Kesenjangan Pasokan Digital Parah di Kabupaten Lampung Tengah (*Extreme Supply Void*)**  
   Lampung Tengah merupakan salah satu kabupaten terluas dengan populasi tertinggi dan urat nadi transportasi Trans-Sumatera (pusat persimpangan Jalan Tol Bakauheni–Terbanggi Besar–Kayu Agung). Namun, pangsa pasarnya di Airbnb hanya **1,08%** (9 listing). Hal ini membuktikan bahwa pemilik properti, hotel transit, dan *homestay* lokal di Lampung Tengah belum memanfaatkan ekosistem pemasaran akomodasi digital global.

2. **Tingginya *Uncaptured Transit Demand* (Permintaan Tercecer ke Kota Metro)**  
   Wisatawan, pelaku bisnis perkebunan/industri, atau pengemudi lintas Sumatera yang mencari penginapan di Lampung Tengah terpaksa menginap di Kota Metro (jarak $\pm 15-25$ km) atau Kotabumi. Ini menunjukkan potensi ekonomi akomodasi yang bocor (*economic leakage*) ke daerah tetangga akibat ketidaksiapan inventaris digital di Lampung Tengah.

3. **Hambatan Kepercayaan Akibat *Zero Review Trap* (Jebakan Tanpa Ulasan)**  
   Tingkat ulasan listing di Lampung Tengah adalah **0,00%** (25,12% rata-rata provinsi). Di era digital, ketiadaan ulasan dan skor rating (*social proof*) menjadi faktor penolakan utama bagi pelancong bisnis dan keluarga yang mengutamakan kepastian kenyamanan dan keamanan.

4. **Karakter Pasar *Value-Driven / Transit Economy***  
   Rata-rata tarif di Lampung Tengah (Rp 2.485.870) jauh lebih terjangkau dibandingkan rata-rata provinsi (Rp 5.091.958), dengan mayoritas bertumpu pada segmen *Budget* (33,3%) dan *Mid-Range* (66,7%). Karakter ini menegaskan bahwa profil pasar akomodasi di koridor ini berorientasi pada fungsi transit fungsional, bukan *leisure resort* mewah.

5. **Konsentrasi Pasar Berpusat pada Aglomerasi Wisata Pesisir dan Perkotaan**  
   Tiga wilayah teratas—Lampung Selatan (203 listing), Pesawaran (198 listing), dan Bandar Lampung (152 listing)—menguasai **66,47%** pasokan pasar digital Airbnb. Daya tarik pantai, pulau wisata, dan pusat pemerintahan/bisnis menjadi motor penggerak utama adopsi Airbnb di Provinsi Lampung.

---

## 6. Rekomendasi Strategis Berbasis Data

### Untuk Pemerintah Daerah & Pelaku Usaha Kabupaten Lampung Tengah:
1. **Inisiatif Digitalisasi Penginapan Lokal (*Host Onboarding Program*):**  
   Dinas Pemuda, Olahraga, dan Pariwisata (Disporapar) bersama PHRI Lampung Tengah perlu menyelenggarakan program sertifikasi dan pelatihan *onboarding* digital bagi pemilik wisma, hotel non-bintang, dan *homestay* di koridor Terbanggi Besar, Bandar Jaya, dan Gunung Sugih ke platform Airbnb dan OTA global.
2. **Pengembangan *Transit Homestay* di Sekitar *Exit Toll* Terbanggi Besar:**  
   Mendorong pengembangan akomodasi berkonsep *Rest & Refresh* dekat pintu tol dengan fasilitas standar (WiFi cepat, AC, parkir aman, sarapan cepat), menyasar segmen pelancong lintas Sumatera pada tarif *Budget* hingga *Mid-Range* (Rp 350.000 – Rp 750.000 per malam).
3. **Pemberian Insentif *First-Review Campaign*:**  
   Memberikan potongan harga promo menginap pertama bagi tamu yang bersedia meninggalkan ulasan terverifikasi untuk memecahkan masalah *Zero Review Trap*.

### Untuk Pelaku Bisnis Akomodasi di Provinsi Lampung:
1. **Standarisasi Kualitas Menuju Predikat *Superhost*:**  
   Listing terbaik di Lampung terbukti mampu mempertahankan rating 5,00 dengan ulasan hingga 18 ulasan tamu (misal: *Boutique hotel in Krui*, *Homestay Spirit di Sukarame*, *Shazia House di Tanjung Karang*). Menjaga kepuasan tamu adalah kunci visibilitas algoritma Airbnb.
2. **Diversifikasi Tipe Properti di Luar Tipe Rumah Tinggal:**  
   Saat ini pasar didominasi oleh tipe *Home* (29,4%) dan *Room* (23,2%). Terdapat peluang besar pada segmen vila privat keluarga (*private pool villa*) dan *glamping/eco-lodge* di kawasan alam yang mencatatkan tarif rata-rata tertinggi di Pesisir Barat dan Lampung Barat (> Rp 8.000.000 per malam).

---

## 7. Cetak Biru Dashboard Google Looker Studio

Untuk memvisualisasikan data ini secara interaktif kepada pemangku kepentingan (*stakeholders*), berikut panduan rancangan visual di Google Looker Studio:

### A. Komponen Filter Interaktif (Bagian Atas Dashboard):
1. **Filter Kontrol 1 (Drop-down):** `wilayah_fokus` (*Kabupaten Lampung Tengah* vs *Kabupaten/Kota Lain*)
2. **Filter Kontrol 2 (Drop-down):** `kabupaten_kota` (Pilihan 12 Kabupaten/Kota)
3. **Filter Kontrol 3 (Checkbox / List):** `price_tier` (*Budget*, *Mid-Range*, *Premium*)
4. **Filter Kontrol 4 (Drop-down):** `tipe_properti` (*Home*, *Apartment*, *Hotel*, *Guesthouse*, *Villa*, dll.)

### B. Susunan Scorecard KPI Utama (Kartu Ringkasan):
- **Scorecard 1:** Total Listing Pasar $\rightarrow$ `COUNT(listing_id)` $\rightarrow$ Target Aktual: **832**
- **Scorecard 2:** Total Listing Unik $\rightarrow$ `COUNT_DISTINCT(listing_id)` $\rightarrow$ Target Aktual: **306**
- **Scorecard 3:** Rata-rata Tarif Sewa $\rightarrow$ `AVG(harga)` $\rightarrow$ Target Aktual: **Rp 5.091.958**
- **Scorecard 4:** Median Tarif Sewa $\rightarrow$ `MEDIAN(harga)` $\rightarrow$ Target Aktual: **Rp 3.000.000**
- **Scorecard 5:** Rata-rata Rating Ulasan $\rightarrow$ `AVG(rating)` $\rightarrow$ Target Aktual: **4,81 / 5,00**
- **Scorecard 6:** Tingkat Listing Berulasan $\rightarrow$ `COUNTIF(has_reviews)/COUNT(1)` $\rightarrow$ Target Aktual: **25,12%**

### C. Visualisasi Grafik & Diagram:
1. **Horizontal Bar Chart / Geo Map:**  
   - **Dimensi:** `kabupaten_kota`  
   - **Metrik:** `Total Listing Pasar` dan `Total Ulasan`  
   - **Fungsi:** Menunjukkan disparitas volume pasar antar kabupaten, menyorot posisi juru kunci Lampung Tengah.
2. **100% Stacked Bar Chart:**  
   - **Dimensi:** `wilayah_fokus` atau `kabupaten_kota`  
   - **Breakdown Dimension:** `price_tier` (*Budget*, *Mid-Range*, *Premium*)  
   - **Fungsi:** Memperlihatkan bahwa Lampung Tengah 100% berada pada Budget & Mid-Range tanpa satupun listing Premium.
3. **Clustered Column Chart:**  
   - **Dimensi:** `tipe_properti` (Top 7)  
   - **Metrik:** `Rata-rata Tarif (harga)` dan `Jumlah Listing`  
   - **Fungsi:** Mengungkap korelasi antara tipe akomodasi terhadap kemampuan monetisasi tarif per malam.
4. **Tabel Interaktif Benchmarking (Top Performing Listings):**  
   - **Kolom:** `judul_listing`, `tipe_properti`, `kabupaten_kota`, `harga`, `rating`, `jumlah_review`, `link` (sebagai Hyperlink)  
   - **Sorting:** `rating` DESC, `jumlah_review` DESC  
   - **Fungsi:** Menampilkan studi perbandingan listing terbaik berperingkat bintang 5 sebagai tolok ukur operasional.
