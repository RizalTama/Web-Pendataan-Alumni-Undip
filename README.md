# AlumniConnect — Sistem Informasi Alumni

Website informasi alumni berbasis Flask + MySQL dengan fitur manajemen data alumni, berita, galeri, dan visualisasi statistik.

## Persyaratan

- Python 3.12+
- XAMPP (MySQL + phpMyAdmin)
- pip

## Cara Setup

### 1. Setup Database

1. Buka XAMPP dan jalankan **Apache** dan **MySQL**
2. Buka **phpMyAdmin** di browser
3. Pilih tab **SQL** dan paste isi file `schema.sql`, lalu klik **Go**
4. Database `alumni_db` beserta tabelnya akan dibuat otomatis

### 2. Setup Environment

Buat virtual environment dan install dependencies:

```bash
cd alumni_system
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 3. Konfigurasi .env

Edit file `.env` sesuai konfigurasi database Anda:

```
SECRET_KEY=ganti-dengan-string-acak-panjang
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=          # kosongkan jika tidak ada password
MYSQL_DB=alumni_db
MAX_CONTENT_LENGTH=5242880
```

### 4. Jalankan Aplikasi

```bash
python run.py
```

Saat pertama dijalankan, akun admin default akan dibuat otomatis:
- **Username:** `admin`
- **Password:** `admin123`

Buka browser dan akses: `http://localhost:5000`

## Struktur Halaman

### Publik (tanpa login)
| URL | Halaman |
|-----|---------|
| `/` | Beranda |
| `/alumni` | Direktori Alumni |
| `/alumni/<id>` | Profil Detail Alumni |
| `/berita` | Daftar Berita & Pengumuman |
| `/berita/<slug>` | Detail Berita |
| `/galeri` | Galeri Foto |
| `/statistik` | Statistik Alumni |

### Admin (wajib login)
| URL | Halaman |
|-----|---------|
| `/admin/login` | Login Admin |
| `/admin/dashboard` | Dashboard |
| `/admin/alumni` | Kelola Data Alumni |
| `/admin/berita` | Kelola Berita |
| `/admin/galeri` | Kelola Galeri |

## Fitur Utama

- **CRUD Alumni** — tambah, edit, hapus data alumni dengan upload foto
- **CRUD Berita** — kelola berita dan pengumuman dengan thumbnail
- **CRUD Galeri** — upload dan kelola foto kegiatan alumni
- **Export Excel** — unduh data alumni ke file `.xlsx`
- **Statistik Grafik** — visualisasi data alumni menggunakan Chart.js
- **Lightbox Galeri** — tampilan foto fullscreen di halaman galeri publik
- **Pencarian & Filter** — cari dan filter alumni/berita berdasarkan berbagai kriteria
- **Pagination** — pembatasan data per halaman di semua daftar

## Stack Teknologi

| Komponen | Teknologi |
|----------|-----------|
| Backend | Python 3.12 + Flask |
| Database | MySQL (XAMPP) |
| ORM/Driver | Flask-MySQLdb |
| Auth | Flask-Login |
| Styling | Tailwind CSS (CDN) |
| Chart | Chart.js (CDN) |
| Font | Plus Jakarta Sans |
| Export | openpyxl |
| Upload | Pillow |
