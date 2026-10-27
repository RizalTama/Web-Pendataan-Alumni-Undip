# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

**Prerequisites:** MySQL running (locally via XAMPP), Python 3.12+

```bash
# 1. Import schema.sql into MySQL/phpMyAdmin (creates the alumni_db database)

# 2. Set up environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Run
python run.py            # http://localhost:5005 (override with PORT env var)
python seed.py           # optional: inserts demo alumni/berita/galeri (idempotent — skips rows that exist)
```

`.env` holds `SECRET_KEY`, `MYSQL_HOST/USER/PASSWORD/DB`, `MAX_CONTENT_LENGTH`; all have defaults in `create_app()`.

Default admin: `admin` / `admin123` — created (or its password reset) by `init_admin()` in `run.py`, which runs at **import time**, not under `__main__`, so it also fires under gunicorn.

There is no test suite, linter, or frontend build step. Tailwind and Chart.js come from CDNs; there is nothing to compile.

**Deploy:** VPS via Docker Compose (`web` + MariaDB) with Caddy on the host — see `DEPLOY.md`. `Procfile` is the older Railway path and is excluded from the image.

Two packaging details worth knowing before touching the `Dockerfile`:

- `Flask-MySQLdb` declares `mysqlclient` as a dependency, and `mysqlclient` ships **no manylinux wheel** — it compiles from source. Hence the multi-stage build: `build-essential` + `default-libmysqlclient-dev` in the builder, only `libmariadb3` at runtime. It is never actually imported (the `install_as_MySQLdb()` shim wins), but pip still installs it.
- gunicorn runs with `--preload` so `init_admin()` executes once in the master rather than once per worker.

**Init dump** (`alumni_db.sql`, MariaDB 10.4 export) is mounted into `/docker-entrypoint-initdb.d/` and runs **only when the `db_data` volume is empty**. It has no `CREATE DATABASE`/`USE`; that is fine because the entrypoint applies it with `--database=$MARIADB_DATABASE`. If the import fails, the container restarts, skips init because the datadir now exists, and comes back **healthy but empty** — always verify `SELECT COUNT(*) FROM alumni` after a first boot.

## Architecture

**Flask App Factory** (`app/__init__.py`) initializes extensions (`mysql`, `login_manager`), then registers 6 blueprints:

| Blueprint | Prefix | Purpose |
|-----------|--------|---------|
| `public_bp` | none | Public pages (no auth) |
| `admin_auth_bp` | `/admin` | Login/logout |
| `admin_dashboard_bp` | `/admin` | Stats dashboard |
| `admin_alumni_bp` | `/admin` | Alumni CRUD + Excel export |
| `admin_berita_bp` | `/admin` | News/announcements CRUD |
| `admin_galeri_bp` | `/admin` | Gallery CRUD |

`pymysql.install_as_MySQLdb()` runs at the top of `app/__init__.py` before any other import — `Flask-MySQLdb` is backed by pure-Python PyMySQL, so no `mysqlclient` C build is needed.

**No ORM** — all DB queries use raw SQL with parameterized `%s` placeholders. Results are always dicts (`MYSQL_CURSORCLASS = 'DictCursor'`). Every write needs `mysql.connection.commit()`.

```python
cur = mysql.connection.cursor()
cur.execute("SELECT * FROM alumni WHERE id = %s", (id,))
row = cur.fetchone()   # dict: row['nama'], row['angkatan']
cur.close()
```

## Key Patterns

**Image uploads** go through `save_image(file, subfolder, max_size)` in `app/utils/helpers.py` — validates extension, generates a UUID filename, resizes with Pillow, saves to `app/static/uploads/{subfolder}/`. The DB stores only the bare filename; templates rebuild the path. Call `delete_image(filename, subfolder)` when replacing or deleting a record.

| Subfolder | Used by | Max size |
|-----------|---------|----------|
| `alumni` | alumni photos | 800×800 |
| `news` | news thumbnails | 1200×800 |
| `gallery` | gallery photos | 1200×900 |

**Pagination is in-memory** — every list route `SELECT`s the full filtered set and slices it in Python via `paginate(rows, page, per_page)`; there is no SQL `LIMIT`/`OFFSET`. The returned dict includes `page_range` (windowed page numbers with `None` marking ellipsis gaps), which templates iterate directly.

**Search/filter routes build a WHERE clause** by appending to `conditions`/`params` lists and f-stringing the joined clause into the query. Only the static clause text is interpolated — user values always stay in `params`. Preserve that split when editing.

**News slugs** use `generate_unique_slug()` in `admin_berita.py` (not in helpers); it appends `-1`, `-2`, … on collision and only regenerates on edit when the title actually changed.

**Jurusan page** (`/jurusan`) renders hardcoded department profiles from `JURUSAN_PROFILES` / `PASCASARJANA_PROFILES` in `app/routes/public.py`. Alumni counts are joined at request time by matching each profile's `db_aliases` (normalized lowercase) against the messy real values in `alumni.jurusan`. Each profile also exposes `jurusan_query` — the raw DB spelling — because the directory filter is an exact `WHERE jurusan = %s` match. Adding a department means adding its profile *and* every spelling variant that appears in the data.

**Homepage slider** reads `app/static/slider/slider{1..6}.jpeg` by index in `beranda.html`; the filenames are the contract, there is no DB table for it.

## Database Tables

- `admins` — admin accounts (username, password_hash, email, nama_lengkap)
- `alumni` — nama, angkatan (YEAR), jurusan, foto, pekerjaan, perusahaan, kota_domisili, email, linkedin, bio, is_unggulan
- `berita` — judul, slug, konten (HTML), thumbnail, kategori ENUM('berita','pengumuman'), status ENUM('draft','published'), admin_id
- `galeri` — judul, deskripsi, foto, tanggal_kegiatan

`berita.konten` holds raw HTML rendered with `|safe`; public routes filter on `status='published'`.

## Flask-Login Setup

`Admin` in `app/models/admin.py` extends `UserMixin` and registers the `@login_manager.user_loader` there. `create_app()` does a side-effect import (`from app.models import admin`) so the loader exists before any request. Admin routes are guarded with `@login_required`.

## Conventions

UI text, flash messages, route names, form fields, and DB columns are all in Indonesian (`tambah`, `edit`, `hapus`, `judul`, `angkatan`). Keep new code in the same language. The public site is branded **IKA FIB UNDIP** (Fakultas Ilmu Budaya, Universitas Diponegoro); `README.md` and `penjelasan.md` still use the older "AlumniConnect" name and a stale port 5000.
