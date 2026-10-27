# Penjelasan Lengkap — AlumniConnect

Dokumen ini menjelaskan seluruh sistem AlumniConnect secara detail dan mudah dipahami, mulai dari cara kerja, struktur kode, database, hingga alur fitur satu per satu.

---

## Daftar Isi

1. [Gambaran Umum](#1-gambaran-umum)
2. [Teknologi yang Digunakan](#2-teknologi-yang-digunakan)
3. [Cara Menjalankan Aplikasi](#3-cara-menjalankan-aplikasi)
4. [Struktur Folder](#4-struktur-folder)
5. [Cara Kerja Aplikasi (Arsitektur)](#5-cara-kerja-aplikasi-arsitektur)
6. [Database — Tabel dan Kolom](#6-database--tabel-dan-kolom)
7. [Penjelasan File Kode Satu per Satu](#7-penjelasan-file-kode-satu-per-satu)
8. [Alur Fitur Lengkap](#8-alur-fitur-lengkap)
9. [Halaman Publik vs Halaman Admin](#9-halaman-publik-vs-halaman-admin)
10. [Pengelolaan Gambar/Foto](#10-pengelolaan-gamberfoto)
11. [Sistem Paginasi](#11-sistem-paginasi)
12. [Ekspor Excel](#12-ekspor-excel)

---

## 1. Gambaran Umum

**AlumniConnect** adalah sistem informasi alumni berbasis web. Ada **dua sisi** dalam aplikasi ini:

- **Sisi Publik** — Siapa saja bisa mengakses tanpa login. Berisi direktori alumni, berita, galeri foto, dan statistik.
- **Sisi Admin** — Hanya bisa diakses setelah login. Admin bisa mengelola semua data: tambah/edit/hapus alumni, berita, dan galeri.

Analoginya seperti website sekolah: pengunjung bisa membaca berita dan melihat profil alumni, tapi hanya guru/admin yang bisa mengedit datanya.

---

## 2. Teknologi yang Digunakan

| Teknologi | Fungsi | Keterangan |
|-----------|--------|------------|
| **Python + Flask** | Backend (logika aplikasi) | Framework web Python |
| **MySQL (XAMPP)** | Database | Menyimpan semua data |
| **Flask-MySQLdb** | Penghubung Flask ke MySQL | Pakai driver PyMySQL |
| **Flask-Login** | Sistem autentikasi/sesi login | Melindungi halaman admin |
| **Flask-WTF / WTForms** | Form handling & proteksi CSRF | Keamanan form |
| **Werkzeug** | Hash password | Menyimpan password secara aman |
| **Pillow** | Resize gambar otomatis | Agar foto tidak terlalu besar |
| **openpyxl** | Generate file Excel (.xlsx) | Untuk fitur ekspor data alumni |
| **Tailwind CSS (CDN)** | Styling / tampilan | Tidak perlu build, langsung dari internet |
| **Chart.js (CDN)** | Grafik statistik | Grafik batang/pie di dashboard |
| **python-dotenv** | Baca file `.env` | Konfigurasi rahasia (password DB, dll) |

> **CDN** = file CSS/JS dimuat langsung dari internet, tidak perlu diinstall atau di-build.

---

## 3. Cara Menjalankan Aplikasi

### Langkah-langkah setup awal:

**1. Siapkan Database**
- Buka phpMyAdmin (XAMPP)
- Import file `schema.sql` → ini akan membuat database `alumni_db` beserta semua tabelnya secara otomatis

**2. Buat file `.env`**
```
SECRET_KEY=ganti-dengan-string-acak-panjang
MYSQL_HOST=127.0.0.1
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DB=alumni_db
MAX_CONTENT_LENGTH=5242880
```
> `MAX_CONTENT_LENGTH=5242880` artinya batas upload file adalah 5 MB (5 × 1024 × 1024 bytes)

**3. Install dependency Python**
```bash
pip install -r requirements.txt
```

**4. Jalankan aplikasi**
```bash
python run.py
```

**5. Buka di browser**
```
http://localhost:5005
```

**6. Login admin pertama kali**
- URL: `http://localhost:5005/admin/login`
- Username: `admin`
- Password: `admin123`

> Akun admin dibuat otomatis saat `run.py` dijalankan pertama kali. Ini dilakukan oleh fungsi `init_admin()`.

---

## 4. Struktur Folder

```
alumni_system/
│
├── run.py                      ← TITIK MULAI aplikasi
├── seed.py                     ← Script untuk mengisi data awal (opsional)
├── schema.sql                  ← Script SQL untuk membuat database & tabel
├── requirements.txt            ← Daftar library Python yang dibutuhkan
├── .env                        ← Konfigurasi rahasia (tidak di-commit ke Git)
│
└── app/                        ← Folder utama aplikasi Flask
    ├── __init__.py             ← APP FACTORY: tempat aplikasi dibuat & dikonfigurasi
    │
    ├── models/
    │   └── admin.py            ← Class Admin untuk sistem login
    │
    ├── routes/                 ← Semua halaman/endpoint aplikasi
    │   ├── public.py           ← Halaman publik (tanpa login)
    │   ├── admin_auth.py       ← Login & logout admin
    │   ├── admin_dashboard.py  ← Dashboard utama admin
    │   ├── admin_alumni.py     ← Kelola data alumni (CRUD + export)
    │   ├── admin_berita.py     ← Kelola berita & pengumuman (CRUD)
    │   └── admin_galeri.py     ← Kelola galeri foto (CRUD)
    │
    ├── utils/
    │   └── helpers.py          ← Fungsi-fungsi pembantu (upload foto, slug, pagination)
    │
    ├── static/
    │   └── uploads/            ← Folder penyimpanan file yang diupload user
    │       ├── alumni/         ← Foto profil alumni
    │       ├── news/           ← Thumbnail berita
    │       └── gallery/        ← Foto galeri
    │
    └── templates/              ← File HTML (tampilan)
        ├── admin/              ← Template halaman admin
        │   ├── base.html       ← Layout dasar admin (navbar, sidebar)
        │   ├── login.html
        │   ├── dashboard.html
        │   ├── alumni/
        │   │   ├── index.html  ← Daftar alumni (admin)
        │   │   └── form.html   ← Form tambah/edit alumni
        │   ├── berita/
        │   │   ├── index.html
        │   │   └── form.html
        │   └── galeri/
        │       ├── index.html
        │       └── form.html
        └── public/             ← Template halaman publik
            ├── base.html       ← Layout dasar publik (navbar, footer)
            ├── beranda.html    ← Homepage
            ├── direktori.html  ← Daftar alumni publik
            ├── profil_alumni.html
            ├── berita.html
            ├── detail_berita.html
            ├── galeri.html
            └── statistik.html
```

---

## 5. Cara Kerja Aplikasi (Arsitektur)

### Pola Request-Response Flask

Setiap kali browser meminta halaman, alurnya seperti ini:

```
Browser → URL → Blueprint/Route → Query ke MySQL → Render Template HTML → Browser
```

**Contoh nyata:**
1. User membuka `http://localhost:5005/alumni`
2. Flask mencocokkan URL `/alumni` → ditemukan di `public.py` fungsi `direktori()`
3. Fungsi tersebut query database: `SELECT * FROM alumni ...`
4. Hasilnya dikirim ke template `direktori.html`
5. HTML yang sudah berisi data dikirim balik ke browser

### App Factory Pattern

`app/__init__.py` menggunakan pola **App Factory** — artinya aplikasi Flask tidak langsung dibuat di level global, tapi dibuat melalui fungsi `create_app()`. Manfaatnya: lebih mudah dikonfigurasi dan lebih aman.

```python
# run.py
app = create_app()   # ← memanggil factory
```

```python
# app/__init__.py
def create_app():
    app = Flask(__name__)
    # ... konfigurasi ...
    # ... daftarkan blueprint ...
    return app
```

### Blueprint

Blueprint adalah cara Flask memisahkan route menjadi file-file terpisah agar kode rapi. Setiap file di `routes/` adalah satu Blueprint.

```
public.py        → semua URL publik (/, /alumni, /berita, dll)
admin_auth.py    → /admin/login, /admin/logout
admin_dashboard  → /admin/dashboard
admin_alumni.py  → /admin/alumni, /admin/alumni/tambah, dll
admin_berita.py  → /admin/berita, /admin/berita/tambah, dll
admin_galeri.py  → /admin/galeri, /admin/galeri/tambah, dll
```

Semua blueprint admin didaftarkan dengan `url_prefix='/admin'`, sehingga semua URL admin otomatis diawali `/admin/`.

### Koneksi Database

Tidak ada ORM (seperti SQLAlchemy). Semua query dilakukan **langsung dengan SQL**:

```python
cur = mysql.connection.cursor()          # Buka koneksi
cur.execute("SELECT * FROM alumni")      # Jalankan SQL
data = cur.fetchall()                    # Ambil hasilnya
cur.close()                              # Tutup koneksi
```

Untuk INSERT/UPDATE/DELETE, wajib panggil `mysql.connection.commit()` agar perubahan tersimpan ke database.

Karena konfigurasi pakai `MYSQL_CURSORCLASS = 'DictCursor'`, hasil query berbentuk **dictionary** (bisa diakses dengan nama kolom), bukan tuple:
```python
row['nama']      # ← bisa akses dengan nama kolom
row['angkatan']
```

---

## 6. Database — Tabel dan Kolom

### Tabel `admins`
Menyimpan akun admin yang bisa login.

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `id` | INT | Primary key, auto increment |
| `username` | VARCHAR(50) | Username unik untuk login |
| `password_hash` | VARCHAR(255) | Password yang sudah di-hash (tidak disimpan polos) |
| `email` | VARCHAR(100) | Email admin |
| `nama_lengkap` | VARCHAR(100) | Nama lengkap admin |
| `created_at` | TIMESTAMP | Waktu akun dibuat |

### Tabel `alumni`
Menyimpan data semua alumni.

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `id` | INT | Primary key |
| `nama` | VARCHAR(150) | Nama alumni (wajib isi) |
| `angkatan` | YEAR | Tahun angkatan, misal 2020 (wajib) |
| `jurusan` | VARCHAR(100) | Nama jurusan (wajib) |
| `foto` | VARCHAR(255) | Nama file foto (disimpan di `uploads/alumni/`) |
| `pekerjaan` | VARCHAR(150) | Jabatan/profesi saat ini |
| `perusahaan` | VARCHAR(150) | Nama perusahaan/instansi |
| `kota_domisili` | VARCHAR(100) | Kota tempat tinggal sekarang |
| `email` | VARCHAR(100) | Email alumni |
| `linkedin` | VARCHAR(255) | URL profil LinkedIn |
| `bio` | TEXT | Deskripsi singkat tentang alumni |
| `is_unggulan` | TINYINT(1) | `1` = alumni unggulan (tampil di homepage), `0` = biasa |
| `created_at` | TIMESTAMP | Waktu data dibuat |
| `updated_at` | TIMESTAMP | Waktu data terakhir diubah (otomatis) |

### Tabel `berita`
Menyimpan artikel berita dan pengumuman.

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `id` | INT | Primary key |
| `judul` | VARCHAR(255) | Judul berita (wajib) |
| `slug` | VARCHAR(255) | URL-friendly dari judul, harus unik. Contoh: `"Berita Wisuda 2024"` → `"berita-wisuda-2024"` |
| `konten` | LONGTEXT | Isi artikel (wajib) |
| `thumbnail` | VARCHAR(255) | Nama file gambar thumbnail |
| `kategori` | ENUM | Hanya boleh: `'berita'` atau `'pengumuman'` |
| `status` | ENUM | `'draft'` (belum tayang) atau `'published'` (tayang) |
| `admin_id` | INT | FK ke tabel `admins` — siapa yang membuat |
| `created_at` | TIMESTAMP | Waktu dibuat |
| `updated_at` | TIMESTAMP | Waktu diubah |

### Tabel `galeri`
Menyimpan foto-foto kegiatan.

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `id` | INT | Primary key |
| `judul` | VARCHAR(255) | Judul/keterangan foto (wajib) |
| `deskripsi` | TEXT | Deskripsi lebih panjang (opsional) |
| `foto` | VARCHAR(255) | Nama file foto (wajib) |
| `tanggal_kegiatan` | DATE | Tanggal foto diambil/kegiatan berlangsung (opsional) |
| `created_at` | TIMESTAMP | Waktu data dibuat |

---

## 7. Penjelasan File Kode Satu per Satu

### `run.py` — Titik Mulai Aplikasi

File ini adalah yang pertama dijalankan (`python run.py`).

```python
app = create_app()   # Buat aplikasi Flask

def init_admin():
    # Cek apakah admin 'admin' sudah ada di database
    # Kalau belum → buat otomatis dengan password 'admin123'
    # Kalau password hash terlalu pendek → update (berarti data lama/placeholder)

init_admin()         # Jalankan inisialisasi admin
app.run(debug=True, port=5005)  # Jalankan server di port 5005
```

---

### `app/__init__.py` — Konfigurasi Utama

Ini adalah **inti** dari aplikasi. Fungsi `create_app()` melakukan:

1. Membaca konfigurasi dari `.env` (SECRET_KEY, konfigurasi MySQL, dll)
2. Menginisialisasi ekstensi: MySQL dan Flask-Login
3. Mengatur bahwa jika user belum login dan akses halaman admin, otomatis diarahkan ke `/admin/login`
4. Import model `admin` — ini penting agar `@login_manager.user_loader` terdaftar
5. Mendaftarkan semua blueprint (file route)

---

### `app/models/admin.py` — Model Admin

Class `Admin` merepresentasikan data admin yang sedang login.

```python
class Admin(UserMixin):
    # UserMixin dari Flask-Login → otomatis punya property:
    # is_authenticated, is_active, is_anonymous, get_id()

    def __init__(self, id, username, email, nama_lengkap):
        self.id = id
        self.username = username
        ...

    @staticmethod
    def get_by_id(admin_id):
        # Query: SELECT * FROM admins WHERE id = ?
        # Dipakai oleh user_loader (Flask-Login)

    @staticmethod
    def get_by_username(username):
        # Query: SELECT * FROM admins WHERE username = ?
        # Dipakai saat proses login (verifikasi username)
```

**`@login_manager.user_loader`** adalah fungsi spesial Flask-Login. Setiap request, Flask-Login memanggil fungsi ini dengan `user_id` dari sesi browser untuk mendapatkan objek Admin:

```python
@login_manager.user_loader
def load_user(user_id):
    return Admin.get_by_id(int(user_id))
```

---

### `app/utils/helpers.py` — Fungsi Pembantu

#### `allowed_file(filename)`
Mengecek apakah ekstensi file diizinkan untuk diupload.
```
File yang diterima: .png, .jpg, .jpeg, .gif, .webp
```

#### `save_image(file, subfolder, max_size=(800, 800))`
Menyimpan gambar yang diupload. Alurnya:
1. Cek apakah file valid (`allowed_file`)
2. Buat nama file baru menggunakan UUID (nama acak unik), misalnya `a3f9c12b...jpg`
3. Tentukan folder tujuan: `app/static/uploads/{subfolder}/`
4. Buka gambar dengan Pillow, resize agar tidak melebihi `max_size`
5. Simpan ke disk
6. Kembalikan nama file (yang disimpan ke database)

> Mengapa UUID? Agar tidak ada konflik nama file walau ada dua alumni dengan nama sama.

#### `delete_image(filename, subfolder)`
Menghapus file gambar dari disk. Dipanggil saat data dihapus atau foto diganti.

#### `slugify(text)`
Mengubah teks biasa menjadi URL-friendly.
```
"Wisuda Angkatan 2024!" → "wisuda-angkatan-2024"
```
Caranya: huruf kecil semua → hapus karakter selain huruf/angka/spasi/dash → ganti spasi dengan dash.

#### `paginate(query_result, page, per_page)`
Memotong list data untuk ditampilkan per halaman.

```
Total data: 100 alumni
Per halaman: 12
Halaman 1: data ke 1-12
Halaman 2: data ke 13-24
... dst
```

Mengembalikan dictionary berisi:
```python
{
    'data': [...],        # Data yang ditampilkan di halaman ini
    'total': 100,         # Total semua data
    'page': 2,            # Halaman saat ini
    'per_page': 12,       # Jumlah per halaman
    'total_pages': 9,     # Total halaman
    'has_prev': True,     # Ada halaman sebelumnya?
    'has_next': True,     # Ada halaman berikutnya?
}
```

> **Penting:** Paginasi dilakukan di memory (Python), bukan di SQL. Artinya semua data diambil dulu dari database, baru dipotong. Ini cukup untuk data yang tidak terlalu besar.

---

### `app/routes/public.py` — Halaman Publik

Tidak ada `@login_required` di sini. Semua bisa diakses siapa saja.

| Fungsi | URL | Yang ditampilkan |
|--------|-----|-----------------|
| `beranda()` | `/` | Homepage: statistik total, alumni unggulan (maks 6), 4 berita terbaru, 6 galeri terbaru |
| `direktori()` | `/alumni` | Daftar semua alumni, bisa dicari & difilter |
| `profil_alumni()` | `/alumni/<id>` | Profil lengkap satu alumni, abort 404 jika tidak ada |
| `berita()` | `/berita` | Daftar berita yang sudah `published`, bisa filter by kategori |
| `detail_berita()` | `/berita/<slug>` | Isi berita lengkap + 4 berita terkait lainnya |
| `galeri()` | `/galeri` | Semua foto galeri |
| `statistik()` | `/statistik` | Data untuk grafik: per angkatan, per jurusan, top pekerjaan, top kota |

**Pencarian di direktori alumni** menggunakan `LIKE` query:
```sql
WHERE (nama LIKE '%kata%' OR pekerjaan LIKE '%kata%' OR perusahaan LIKE '%kata%' OR kota_domisili LIKE '%kata%')
```

---

### `app/routes/admin_auth.py` — Login & Logout

**Login:**
1. Tampilkan form username & password
2. User submit form
3. Cari admin di database: `Admin.get_by_username(username)`
4. Verifikasi password: `check_password_hash(hash_dari_db, password_yang_diketik)`
5. Jika cocok → `login_user(admin)` → sesi login dibuat → redirect ke dashboard
6. Jika tidak cocok → tampilkan pesan error

**Logout:**
- `logout_user()` → sesi dihapus → redirect ke halaman login

---

### `app/routes/admin_dashboard.py` — Dashboard Admin

Halaman pertama setelah login. Menampilkan:
- **Kartu statistik:** Total alumni, total berita published, total foto galeri
- **Grafik Chart.js:** Alumni per tahun angkatan (data dikirim dari server)
- **Top 8 bidang pekerjaan:** Pekerjaan yang paling banyak dimiliki alumni
- **5 alumni terbaru:** Yang paling baru ditambahkan

---

### `app/routes/admin_alumni.py` — Kelola Data Alumni

Semua route dilindungi `@login_required`.

**Daftar alumni (`/admin/alumni`):**
- Mendukung pencarian (nama, pekerjaan, perusahaan) dan filter (angkatan, jurusan)
- Tampil 15 alumni per halaman

**Tambah alumni (`/admin/alumni/tambah`):**
1. GET → tampilkan form kosong
2. POST → validasi field wajib (nama, angkatan, jurusan)
3. Jika ada foto → `save_image()` → simpan nama filenya
4. INSERT ke database → redirect ke daftar

**Edit alumni (`/admin/alumni/edit/<id>`):**
1. GET → ambil data alumni dari DB → tampilkan form sudah terisi
2. POST → jika ada foto baru → hapus foto lama (`delete_image`) → simpan foto baru
3. UPDATE di database → redirect ke daftar

**Hapus alumni (`/admin/alumni/hapus/<id>`):**
- Hanya menerima POST (form dengan method POST)
- Hapus file foto dari disk jika ada
- DELETE dari database

**Export Excel (`/admin/alumni/export`):**
- Query semua alumni
- Buat file `.xlsx` menggunakan openpyxl
- Header berwarna biru navy dengan teks putih tebal
- Kolom otomatis menyesuaikan lebar konten
- File dikirim langsung sebagai download (tidak disimpan ke disk server)

---

### `app/routes/admin_berita.py` — Kelola Berita

Sama polanya dengan alumni, tapi ada fitur tambahan: **slug**.

**`generate_unique_slug(judul, exclude_id=None)`**
Fungsi ini memastikan tidak ada dua berita dengan slug yang sama:
```
Judul: "Berita Wisuda"
Slug pertama: "berita-wisuda"
Jika "berita-wisuda" sudah ada → coba "berita-wisuda-1"
Jika masih ada → coba "berita-wisuda-2" ... dst
```

Parameter `exclude_id` dipakai saat edit: agar slug milik berita yang sedang diedit tidak dianggap konflik dengan dirinya sendiri.

**Status berita:** `draft` berarti tidak tampil di halaman publik. `published` berarti tampil. Admin bisa pilih status saat tambah/edit.

---

### `app/routes/admin_galeri.py` — Kelola Galeri

Pola CRUD yang sama. Perbedaannya:
- Foto **wajib** saat tambah (tidak bisa simpan tanpa foto)
- Saat edit, foto lama tetap dipertahankan jika tidak ada foto baru yang diupload
- Max size gambar: `(1200, 900)` — lebih besar dari foto alumni `(800, 800)`

---

## 8. Alur Fitur Lengkap

### Alur: Pengunjung melihat profil alumni

```
1. Pengunjung buka http://localhost:5005/alumni
2. Flask panggil fungsi direktori() di public.py
3. Query: SELECT * FROM alumni ORDER BY nama
4. Hasil dikembalikan ke paginate() → dipotong 12 data
5. Template direktori.html dirender dengan data tersebut
6. Pengunjung klik nama alumni
7. Buka /alumni/5 (misalnya id = 5)
8. Flask panggil profil_alumni(id=5)
9. Query: SELECT * FROM alumni WHERE id = 5
10. Jika tidak ada → abort(404) → halaman error
11. Jika ada → render profil_alumni.html
```

### Alur: Admin tambah berita baru

```
1. Admin buka /admin/berita/tambah
2. Tampil form kosong (GET request)
3. Admin isi judul, konten, pilih kategori, status, upload thumbnail
4. Admin klik Simpan (POST request)
5. Flask validasi: judul dan konten wajib ada
6. Jika ada thumbnail → save_image() → file disimpan, dapat nama UUID
7. generate_unique_slug("Judul Berita") → dapat slug unik
8. INSERT INTO berita (judul, slug, konten, thumbnail, kategori, status, admin_id)
9. mysql.connection.commit() → data tersimpan
10. Flash message: "Berita berhasil ditambahkan"
11. Redirect ke /admin/berita
```

### Alur: Admin hapus alumni

```
1. Admin klik tombol Hapus di tabel alumni
2. Form POST ke /admin/alumni/hapus/5
3. Flask cek: SELECT foto FROM alumni WHERE id = 5
4. Jika ada foto → delete_image(nama_foto, 'alumni') → file dihapus dari disk
5. DELETE FROM alumni WHERE id = 5
6. mysql.connection.commit()
7. Flash message + redirect ke daftar alumni
```

### Alur: Login admin

```
1. User buka /admin/login
2. Isi username + password → submit
3. Admin.get_by_username('admin') → ambil data dari DB
4. check_password_hash(hash_db, password_input) → cek kecocokan
5. Jika cocok → login_user(admin) → session dibuat di browser
6. Redirect ke /admin/dashboard
7. Untuk request selanjutnya, Flask-Login otomatis panggil load_user()
   agar tahu siapa yang sedang login
```

---

## 9. Halaman Publik vs Halaman Admin

### Halaman Publik (tanpa login)

| URL | Halaman |
|-----|---------|
| `/` | Beranda / homepage |
| `/alumni` | Direktori alumni (bisa cari & filter) |
| `/alumni/<id>` | Profil detail satu alumni |
| `/berita` | Daftar berita & pengumuman (published saja) |
| `/berita/<slug>` | Isi berita lengkap |
| `/galeri` | Galeri foto kegiatan |
| `/statistik` | Statistik & grafik alumni |

### Halaman Admin (wajib login)

| URL | Halaman |
|-----|---------|
| `/admin/login` | Form login |
| `/admin/logout` | Logout |
| `/admin/dashboard` | Dashboard utama |
| `/admin/alumni` | Daftar alumni (admin) |
| `/admin/alumni/tambah` | Form tambah alumni baru |
| `/admin/alumni/edit/<id>` | Form edit alumni |
| `/admin/alumni/hapus/<id>` | Hapus alumni (POST) |
| `/admin/alumni/export` | Download Excel semua alumni |
| `/admin/berita` | Daftar berita |
| `/admin/berita/tambah` | Form tulis berita baru |
| `/admin/berita/edit/<id>` | Form edit berita |
| `/admin/berita/hapus/<id>` | Hapus berita (POST) |
| `/admin/galeri` | Daftar foto galeri |
| `/admin/galeri/tambah` | Upload foto baru |
| `/admin/galeri/edit/<id>` | Edit data foto |
| `/admin/galeri/hapus/<id>` | Hapus foto (POST) |

> Jika user belum login dan mencoba akses halaman admin, Flask-Login otomatis redirect ke `/admin/login` dengan pesan "Silakan login terlebih dahulu."

---

## 10. Pengelolaan Gambar/Foto

Semua gambar yang diupload diproses oleh fungsi `save_image()` di `helpers.py`.

### Alur upload foto:
```
User pilih file → Flask terima file → Cek ekstensi valid?
→ Buat nama UUID unik (misal: a3b9c12d4e5f6789.jpg)
→ Buka dengan Pillow
→ Resize agar tidak melebihi batas maksimal
→ Simpan ke folder uploads/
→ Kembalikan nama file (disimpan ke kolom `foto` di database)
```

### Batas ukuran gambar:
| Jenis | Max Size |
|-------|----------|
| Foto alumni | 800 × 800 px |
| Thumbnail berita | 1200 × 800 px |
| Foto galeri | 1200 × 900 px |

> `thumbnail()` dari Pillow menggunakan mode **proporsional** — gambar tidak terdistorsi, hanya diperkecil agar masuk dalam batas yang ditentukan.

### Lokasi penyimpanan:
```
app/static/uploads/alumni/   ← foto alumni
app/static/uploads/news/     ← thumbnail berita
app/static/uploads/gallery/  ← foto galeri
```

File bisa diakses dari browser via URL:
```
http://localhost:5005/static/uploads/alumni/a3b9c12d.jpg
```

### Saat data dihapus atau foto diganti:
- `delete_image()` dipanggil untuk menghapus file lama dari disk agar tidak menumpuk.

---

## 11. Sistem Paginasi

Paginasi adalah fitur "halaman 1, 2, 3..." agar tidak semua data ditampilkan sekaligus.

### Cara kerjanya:
```python
# Di route:
cur.execute("SELECT * FROM alumni")   # Ambil SEMUA data dari DB
all_alumni = cur.fetchall()           # Misal: 100 data

page = int(request.args.get('page', 1))   # Halaman berapa? (dari URL ?page=2)
pagination = paginate(all_alumni, page, 12)  # Potong 12 per halaman
```

### Hasil `paginate()` yang dikirim ke template:
```python
pagination['data']         # List 12 alumni untuk halaman ini
pagination['total']        # 100 (total semua)
pagination['page']         # 2 (halaman saat ini)
pagination['total_pages']  # 9 (total halaman)
pagination['has_prev']     # True (ada halaman sebelumnya)
pagination['has_next']     # True (ada halaman berikutnya)
```

### Jumlah per halaman di tiap section:
| Section | Per halaman |
|---------|-------------|
| Direktori alumni (publik) | 12 |
| Berita (publik) | 9 |
| Galeri (publik) | 12 |
| Alumni (admin) | 15 |
| Berita (admin) | 10 |
| Galeri (admin) | 12 |

---

## 12. Ekspor Excel

Fitur ini menghasilkan file `.xlsx` yang bisa langsung dibuka di Microsoft Excel atau Google Sheets.

### Prosesnya:
```python
# 1. Query semua alumni
cur.execute("SELECT nama, angkatan, jurusan, ... FROM alumni ORDER BY angkatan DESC, nama")

# 2. Buat workbook Excel di memory (bukan file fisik)
wb = openpyxl.Workbook()
ws = wb.active

# 3. Tulis header kolom
ws.append(['Nama', 'Angkatan', 'Jurusan', ...])

# 4. Isi data baris per baris
for a in alumni_list:
    ws.append([a['nama'], a['angkatan'], ...])

# 5. Styling: header bold, background biru navy, teks putih
# 6. Auto-width: lebar kolom otomatis menyesuaikan isi

# 7. Simpan ke BytesIO (bukan ke disk), lalu kirim sebagai download
output = io.BytesIO()
wb.save(output)
return send_file(output, as_attachment=True, download_name="data_alumni_20240506_143000.xlsx")
```

> File langsung dikirim ke browser sebagai download tanpa pernah tersimpan ke disk server.

---

## Ringkasan Cepat

| Hal | Detail |
|-----|--------|
| Port aplikasi | 5005 |
| URL publik | `http://localhost:5005` |
| URL admin | `http://localhost:5005/admin/login` |
| Login default | `admin` / `admin123` |
| Database | `alumni_db` (MySQL) |
| Setup DB | Import `schema.sql` via phpMyAdmin |
| Jalankan | `python run.py` |
| Max upload | 5 MB |
| Format foto | PNG, JPG, JPEG, GIF, WEBP |
