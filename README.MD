# README.MD untuk dua project: image_compression dan route_planner

# 1. Image Compression

Aplikasi web untuk kompresi gambar menggunakan algoritma K-Means, dibangun dengan Python (Flask) dan SQLAlchemy. Aplikasi ini memungkinkan pengguna mengunggah gambar, mengompres gambar tersebut, serta menyimpan metadata gambar ke database PostgreSQL.

## Fitur Utama

- Kompresi gambar berbasis K-Means (scikit-learn)
- Upload gambar melalui web (drag & drop)
- Penyimpanan metadata gambar (nama file, ukuran, hash) ke database
- Pembuatan thumbnail otomatis
- Tampilan hasil kompresi dan perbandingan ukuran

## Cara Menjalankan

1. Pastikan sudah menginstall dependensi:
   ```bash
   pip install -r image_compression/requirements.txt
   ```
2. Jalankan database PostgreSQL dan buat database `image_compression`.
3. Jalankan aplikasi Flask:
   ```bash
   cd image_compression
   python -m flask --debug run
   ```
4. Buka browser ke `http://127.0.0.1:5000` untuk mengakses aplikasi.

## Struktur Folder

- `app.py` : Main Flask app
- `model.py` : Model SQLAlchemy untuk metadata gambar
- `kmeans/kmeans.py` : Algoritma kompresi gambar
- `templates/index.html` : UI upload gambar
- `static/uploads/` : Folder penyimpanan gambar hasil upload & kompresi

---

# 2. Route Planner

Aplikasi perencana rute bus berbasis data bus stop kota Rio de Janeiro. Menggunakan Python (Flask) dan PostgreSQL untuk menyimpan graph rute bus. Dapat mencari rute terpendek antar halte dengan algoritma Dijkstra.

## Fitur Utama

- Pencarian rute bus terpendek antar halte
- Data graph bus stop dari dataset Kaggle
- Penyimpanan graph ke database PostgreSQL
- Konversi data CSV ke JSON dan database

## Cara Menjalankan

1. Install dependensi (Flask, psycopg2):
   ```bash
   pip install flask psycopg2-binary
   ```
2. Siapkan database PostgreSQL `route_planner` dan import data dengan script di `insert_db/insert.py`.
3. Jalankan aplikasi Flask:
   ```bash
   cd route_planner
   flask run
   ```
4. Endpoint utama: `http://127.0.0.1:5000/`

## Struktur Folder

- `app.py` : Main Flask app & logic pencarian rute
- `bus_graph.json` : Data graph bus stop
- `convert_csv/` : Script konversi CSV ke JSON
- `insert_db/` : Script insert data ke database

---

# Kontak

Dikembangkan oleh: **Habib Fatkhul Rohman aka Huang - 2025**

Untuk pertanyaan atau kontribusi, silakan hubungi via email atau LinkedIn.
