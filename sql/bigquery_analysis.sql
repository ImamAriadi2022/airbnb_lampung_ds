-- ==============================================================================================
-- Proyek Akhir Big Data & Data Analytics
-- Judul: Analisis Pasar dan Pemetaan Daya Saing Akomodasi Digital Airbnb di Provinsi Lampung:
--        Studi Komparatif Kabupaten Lampung Tengah
-- Data Warehouse: Google BigQuery
-- Dataset Target: `bigdata-airbnb-lampung.airbnb_lampung_ds.listings_clean`
-- Dialek: Google BigQuery Standard SQL
-- ==============================================================================================

-- ----------------------------------------------------------------------------------------------
-- KUERI 1: Ringkasan Pasar Akomodasi Digital per Kabupaten/Kota di Provinsi Lampung
-- Tujuan: Mengetahui ukuran pasar, tarif sewa (rata-rata, median, min, max), serta kualitas ulasan
--         di setiap kabupaten/kota untuk melihat konsentrasi pasar.
-- ----------------------------------------------------------------------------------------------
SELECT
    kabupaten_kota,
    COUNT(1) AS total_listing_pasar,
    COUNT(DISTINCT listing_id) AS total_listing_unik,
    ROUND(AVG(harga), 0) AS rata_rata_harga_idr,
    APPROX_QUANTILES(harga, 2)[OFFSET(1)] AS median_harga_idr,
    MIN(harga) AS min_harga_idr,
    MAX(harga) AS max_harga_idr,
    ROUND(AVG(rating), 2) AS rata_rata_rating,
    COUNTIF(rating IS NOT NULL) AS listing_ber_rating,
    COUNTIF(is_new_listing = TRUE) AS listing_baru_new,
    SUM(jumlah_review) AS total_ulasan_konsumen,
    ROUND(SAFE_DIVIDE(COUNTIF(has_reviews = TRUE) * 100.0, COUNT(1)), 2) AS pct_listing_memiliki_ulasan
FROM
    `bigdata-airbnb-lampung.airbnb_lampung_ds.listings_clean`
GROUP BY
    kabupaten_kota
ORDER BY
    total_listing_pasar DESC,
    rata_rata_harga_idr DESC;


-- ----------------------------------------------------------------------------------------------
-- KUERI 2: Studi Komparatif Kabupaten Lampung Tengah vs Kabupaten/Kota Lain di Lampung
-- Tujuan: Membandingkan secara langsung parameter pasar utama antara Kabupaten Lampung Tengah
--         (wilayah fokus studi) terhadap agregat seluruh wilayah lain di Provinsi Lampung.
-- ----------------------------------------------------------------------------------------------
SELECT
    wilayah_fokus,
    COUNT(1) AS total_listing,
    ROUND(COUNT(1) * 100.0 / SUM(COUNT(1)) OVER(), 2) AS pangsa_pasar_pct,
    COUNT(DISTINCT listing_id) AS jumlah_listing_unik,
    ROUND(AVG(harga), 0) AS rata_rata_harga_idr,
    APPROX_QUANTILES(harga, 2)[OFFSET(1)] AS median_harga_idr,
    MIN(harga) AS harga_termurah_idr,
    MAX(harga) AS harga_termahal_idr,
    ROUND(AVG(rating), 2) AS rata_rata_rating,
    ROUND(AVG(jumlah_review), 2) AS rata_rata_ulasan_per_listing,
    SUM(jumlah_review) AS total_ulasan_pasar,
    ROUND(SAFE_DIVIDE(COUNTIF(has_reviews = TRUE) * 100.0, COUNT(1)), 2) AS pct_listing_aktif_berulasan,
    COUNTIF(is_new_listing = TRUE) AS listing_baru_belum_ada_ulasan
FROM
    `bigdata-airbnb-lampung.airbnb_lampung_ds.listings_clean`
GROUP BY
    wilayah_fokus
ORDER BY
    total_listing DESC;


-- ----------------------------------------------------------------------------------------------
-- KUERI 3: Distribusi Segmentasi Tarif (Price Tier) Berdasarkan Wilayah Fokus
-- Tujuan: Menganalisis komposisi keterjangkauan harga (Budget, Mid-Range, Premium) di Lampung Tengah
--         dibandingkan dengan wilayah lainnya di Provinsi Lampung.
-- ----------------------------------------------------------------------------------------------
WITH tier_calc AS (
    SELECT
        wilayah_fokus,
        kabupaten_kota,
        price_tier,
        COUNT(1) AS jumlah_listing,
        ROUND(AVG(harga), 0) AS rata_rata_harga_tier
    FROM
        `bigdata-airbnb-lampung.airbnb_lampung_ds.listings_clean`
    GROUP BY
        wilayah_fokus,
        kabupaten_kota,
        price_tier
)
SELECT
    wilayah_fokus,
    kabupaten_kota,
    COALESCE(SUM(CASE WHEN price_tier = 'Budget' THEN jumlah_listing END), 0) AS tier_budget_count,
    COALESCE(SUM(CASE WHEN price_tier = 'Mid-Range' THEN jumlah_listing END), 0) AS tier_mid_range_count,
    COALESCE(SUM(CASE WHEN price_tier = 'Premium' THEN jumlah_listing END), 0) AS tier_premium_count,
    SUM(jumlah_listing) AS total_listing_wilayah,
    ROUND(COALESCE(SUM(CASE WHEN price_tier = 'Budget' THEN jumlah_listing END), 0) * 100.0 / SUM(jumlah_listing), 1) AS pct_budget,
    ROUND(COALESCE(SUM(CASE WHEN price_tier = 'Mid-Range' THEN jumlah_listing END), 0) * 100.0 / SUM(jumlah_listing), 1) AS pct_mid_range,
    ROUND(COALESCE(SUM(CASE WHEN price_tier = 'Premium' THEN jumlah_listing END), 0) * 100.0 / SUM(jumlah_listing), 1) AS pct_premium
FROM
    tier_calc
GROUP BY
    wilayah_fokus,
    kabupaten_kota
ORDER BY
    CASE WHEN wilayah_fokus = 'Kabupaten Lampung Tengah' THEN 0 ELSE 1 END,
    total_listing_wilayah DESC;


-- ----------------------------------------------------------------------------------------------
-- KUERI 4: Analisis Dominasi Tipe Properti & Akomodasi
-- Tujuan: Mengidentifikasi ragam bentuk akomodasi (Home, Apartment, Hotel, Guesthouse, Villa, dll.)
--         beserta metrik penetrasi pasar, rata-rata tarif, dan performa ulasannya.
-- ----------------------------------------------------------------------------------------------
SELECT
    tipe_properti,
    COUNT(1) AS total_listing,
    ROUND(COUNT(1) * 100.0 / SUM(COUNT(1)) OVER(), 2) AS persentase_kontribusi,
    ROUND(AVG(harga), 0) AS rata_rata_tarif_idr,
    APPROX_QUANTILES(harga, 2)[OFFSET(1)] AS median_tarif_idr,
    ROUND(AVG(rating), 2) AS rata_rata_rating,
    SUM(jumlah_review) AS total_ulasan,
    COUNTIF(kabupaten_kota = 'Kabupaten Lampung Tengah') AS listing_di_lampung_tengah
FROM
    `bigdata-airbnb-lampung.airbnb_lampung_ds.listings_clean`
GROUP BY
    tipe_properti
ORDER BY
    total_listing DESC;


-- ----------------------------------------------------------------------------------------------
-- KUERI 5: Top 10 Listing Terbaik di Provinsi Lampung (Listing Unik Berperforma Tertinggi)
-- Tujuan: Memberikan benchmarking listing terbaik berdasarkan ulasan tertinggi (rating 5.0)
--         dan volume review terbesar untuk dipelajari strategi layanannya oleh host lokal.
-- ----------------------------------------------------------------------------------------------
SELECT
    listing_id,
    ANY_VALUE(nama) AS nama_listing,
    ANY_VALUE(tipe_properti) AS tipe_properti,
    ANY_VALUE(lokasi_spesifik) AS lokasi_spesifik,
    ANY_VALUE(kabupaten_kota) AS kabupaten_kota_utama,
    ANY_VALUE(harga) AS harga_per_malam_idr,
    ANY_VALUE(rating) AS skor_rating,
    ANY_VALUE(jumlah_review) AS total_ulasan_tamu,
    ANY_VALUE(price_tier) AS kategori_harga,
    ANY_VALUE(link) AS url_listing
FROM
    `bigdata-airbnb-lampung.airbnb_lampung_ds.listings_clean`
WHERE
    rating IS NOT NULL
GROUP BY
    listing_id
ORDER BY
    skor_rating DESC,
    total_ulasan_tamu DESC,
    harga_per_malam_idr ASC
LIMIT 10;


-- ----------------------------------------------------------------------------------------------
-- KUERI 6: Profil Terperinci Listing Pasar Kabupaten Lampung Tengah & Titik Lokasi
-- Tujuan: Mengkaji seluruh listing yang muncul pada pencarian Kabupaten Lampung Tengah secara mendalam,
--         menganalisis harga, tipe properti, lokasi spesifik, dan potensi diversifikasi akomodasi.
-- ----------------------------------------------------------------------------------------------
SELECT
    listing_id,
    judul_listing,
    tipe_properti,
    lokasi_spesifik,
    harga AS harga_sewa_idr,
    price_tier,
    is_new_listing,
    rating_kategori,
    jumlah_review,
    link
FROM
    `bigdata-airbnb-lampung.airbnb_lampung_ds.listings_clean`
WHERE
    kabupaten_kota = 'Kabupaten Lampung Tengah'
ORDER BY
    harga ASC;
