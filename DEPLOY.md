# Deploy IKA FIB UNDIP ke VPS Biznet Gio — dari 0 sampai jalan

Panduan lengkap, urut dari VPS masih kosong sampai website hidup di HTTPS.
Target: **Ubuntu 22.04 / 24.04, 2 vCPU, 2GB RAM**.

## Arsitektur

```
Internet :443 → Caddy (di host, systemd) → 127.0.0.1:5005 → container web (gunicorn)
                                                                  ↓ jaringan docker
                                                             container db (MariaDB 10.11)
                                                                  ↓
                                                            volume db_data
                                       ./data/uploads ←→ /app/app/static/uploads (bind mount)
```

Caddy sengaja **di luar Docker**: sertifikat aman dari `down -v` yang tidak sengaja,
config gampang di-reload, dan kalau nanti ada aplikasi kedua tinggal tambah blok.

## Yang perlu disiapkan sebelum mulai

| | Keterangan |
|---|---|
| VPS | Biznet Gio, Ubuntu 22.04/24.04 |
| Key SSH | File `.pem` dari panel Biznet, sudah diunduh ke laptop |
| Domain | Sudah dibeli, dan kamu bisa mengubah DNS-nya |
| File dump | `alumni_db.sql` (~330KB) ada di laptop |
| Foto lama | Isi folder `app/static/uploads/` kalau ada — lihat [Catatan penting](#catatan-penting) |

---

# BAGIAN 1 — Menyiapkan server

## 1.1 Arahkan domain ke VPS (lakukan paling awal)

Domain: **ikafibundip.com** (registrar CV. Jogjacamp / Domainesia).

Kerjakan ini duluan karena propagasi DNS butuh waktu, sementara Caddy **tidak bisa
menerbitkan sertifikat sebelum domain benar-benar mengarah ke VPS**.

### a. Cek dulu domain didelegasikan ke mana

```bash
dig +short NS ikafibundip.com @8.8.8.8
whois ikafibundip.com | grep -i "name server"
```

Ini langkah yang gampang dilewatkan: record A harus dibuat di **penyedia yang
memegang nameserver**, bukan di registrar tempat domain dibeli. Keduanya sering
berbeda. (Domain ini awalnya mengarah ke `*.ns.cloudflare.com` padahal zonanya
tidak aktif di sana, sehingga domain tidak resolve sama sekali — dan mengisi
record di panel Domainesia tidak akan berefek apa pun.)

### b. Pastikan nameserver-nya Domainesia

client.domainesia.com → **Domain** → `ikafibundip.com` → **Kelola Nameserver**:

```
ns1.domainesia.com
ns2.domainesia.com
```

Domainesia hanya punya dua nameserver — `ns3`/`ns4` tidak ada, kosongkan saja.
Tunggu sampai perubahan tercatat (15–60 menit untuk `.com`):

```bash
dig +short NS ikafibundip.com @8.8.8.8      # harus ns1 & ns2.domainesia.com
```

### c. Tambahkan record A di Kelola DNS

| Type | Name | Value | TTL |
|---|---|---|---|
| A | `@` | `103.89.2.238` | 300 |
| A | `www` | `103.89.2.238` | 300 |

Hapus record A/AAAA lama untuk `@` dan `www` kalau ada, dan matikan fitur
**Web Forwarding / URL Redirect** — ketiganya bisa menimpa arah domain. Record
**MX** jangan disentuh kalau kamu memakai email di domain ini.

### d. Verifikasi

```bash
dig +short ikafibundip.com @1.1.1.1          # harus 103.89.2.238
dig +short www.ikafibundip.com @1.1.1.1      # harus 103.89.2.238
dig +short AAAA ikafibundip.com @1.1.1.1     # idealnya kosong
```

Kalau AAAA masih terisi menunjuk server lama, hapus — sebagian pengunjung dan
Let's Encrypt akan mencoba lewat IPv6 lalu gagal, dan gejalanya membingungkan
karena `dig` biasa terlihat normal.

## 1.2 Login ke VPS pakai file .pem

Simpan `.pem` dari panel Biznet, lalu kunci izinnya — SSH menolak key yang bisa
dibaca user lain:

```bash
mv ~/Downloads/alumni-web.pem ~/.ssh/
chmod 400 ~/.ssh/alumni-web.pem
```

Masuk:

```bash
ssh -i ~/.ssh/alumni-web.pem alumni.web@103.89.2.238
```

Biar tidak perlu mengetik `-i` terus, tambahkan di `~/.ssh/config` di **laptop**:

```
Host alumni-vps
    HostName 103.89.2.238
    User alumni.web
    IdentityFile ~/.ssh/alumni-web.pem
```

Sesudah itu cukup `ssh alumni-vps`, dan `scp` bisa memakai nama itu juga:
`scp file alumni-vps:~/web-alumni/`.

**Pastikan dulu user ini punya hak sudo** — hampir semua langkah berikutnya
membutuhkannya:

```bash
sudo whoami        # harus menjawab: root
```

Kalau malah muncul `alumni.web is not in the sudoers file`, minta akses sudo lewat
panel/support Biznet dulu sebelum lanjut.

## 1.3 Update sistem dan zona waktu

```bash
sudo apt update && sudo apt upgrade -y
sudo timedatectl set-timezone Asia/Jakarta
```

Zona waktu penting karena kolom `created_at` di berita/galeri memakai waktu server.

## 1.4 Bikin swap 2GB

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h                          # kolom Swap harus terisi 2.0Gi
```

Biznet tidak menyediakan swap secara default. Di RAM 2GB, tanpa swap proses
`docker build` atau lonjakan MariaDB bisa memicu OOM killer — dan yang biasanya
kena tebas justru MariaDB.

## 1.5 Install Docker

```bash
curl -fsSL https://get.docker.com | sudo sh

# Wajib: tanpa ini setiap perintah docker harus pakai sudo.
# newgrp membuat grup baru langsung berlaku tanpa perlu logout.
sudo usermod -aG docker $USER
newgrp docker

docker run --rm hello-world      # tes, harus jalan TANPA sudo
docker compose version           # plugin compose ikut terinstall
```

Kalau `hello-world` masih bilang *permission denied on docker.sock*, keluar lalu
SSH masuk lagi — perubahan grup baru benar-benar melekat di sesi login baru.

## 1.6 Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80,443/tcp
sudo ufw enable
sudo ufw status
```

> Kalau di panel Biznet ada Cloud Firewall / Security Group terpisah, port 80 dan
> 443 harus dibuka di sana juga — ufw saja tidak cukup.

---

# BAGIAN 2 — Menaruh aplikasi

## 2.1 Ambil kode

```bash
cd ~
git clone <URL_REPO_KAMU> web-alumni
cd web-alumni
```

## 2.2 Kirim file dump dari laptop

`alumni_db.sql` sengaja **tidak ikut Git** karena berisi nama dan email 1966 alumni
asli. Kirim manual. Dari **laptop** (perhatikan tanda kutip — path project-mu
mengandung spasi dan karakter `|`):

```bash
cd "/Users/linggaept/Documents/code/A-1237 | Hosting Web Alumni/alumni_system"
scp -i ~/.ssh/alumni-web.pem alumni_db.sql alumni.web@103.89.2.238:~/web-alumni/
```

Kalau punya foto berita/galeri lama, kirim juga:

```bash
scp -i ~/.ssh/alumni-web.pem -r app/static/uploads/* alumni.web@103.89.2.238:~/web-alumni/data/uploads/
```

## 2.3 Isi environment

```bash
cp .env.production.example .env.production
nano .env.production
```

Isi tiga nilai ini (jangan dibiarkan kosong — compose akan menolak start):

```bash
openssl rand -hex 32        # → SECRET_KEY
openssl rand -base64 24     # → DB_ROOT_PASSWORD
openssl rand -base64 24     # → DB_PASSWORD
```

`DB_USER` biarkan `alumni`. **Jangan diisi `root`** — entrypoint MariaDB akan
mencoba `CREATE USER 'root'` yang pasti gagal, dan container langsung exit 1.

> **Kenapa `.env.production`, bukan `.env`?**
> Repo ini punya dua skema environment yang berbeda:
> `.env` untuk dev di laptop (prefiks `MYSQL_*`, dibaca python-dotenv di dalam app),
> `.env.production` untuk deploy (prefiks `DB_*`, dibaca docker-compose).
> docker-compose otomatis memungut `.env` kalau ada, jadi namanya sengaja dibedakan
> supaya tidak tercampur. Semua perintah compose di bawah memakai `--env-file`.

## 2.4 Siapkan folder upload

```bash
mkdir -p data/uploads/{alumni,news,gallery}
sudo chown -R 1000:1000 data/uploads
```

UID 1000 itu user `alumni` di dalam container. Tanpa `chown`, semua upload dari
panel admin akan gagal dengan *permission denied*.

## 2.5 Nyalakan

```bash
docker compose --env-file .env.production up -d --build
```

Build pertama makan 2–4 menit (`mysqlclient` dikompilasi dari source). Lihat log:

```bash
docker compose --env-file .env.production logs -f web     # Ctrl+C untuk keluar
```

Biar perintah berikutnya pendek, bikin alias — tambahkan ke `~/.bashrc` supaya permanen:

```bash
cat >> ~/.bashrc <<'EOF'
alias dc='docker compose --env-file .env.production'
EOF
source ~/.bashrc
alias dc          # pastikan tampil sebagai SATU baris utuh
```

> Pakai bentuk heredoc di atas, jangan `echo "..."`. Kalau perintah `echo` terpotong
> saat di-paste ke terminal, alias-nya tersimpan dengan newline di tengah dan `dc`
> akan error `flag needs an argument: --env-file`. Kalau terlanjur:
> `sed -i "/alias dc=/d; /^\.env\.production'$/d" ~/.bashrc` lalu ulangi.

Alias ini memakai path relatif, jadi `dc` harus dijalankan dari dalam folder project
(tempat `docker-compose.yml` berada).

## 2.6 VERIFIKASI — jangan dilewat

```bash
curl -I http://127.0.0.1:5005/
source .env.production
dc exec -T db mariadb -u root -p"$DB_ROOT_PASSWORD" alumni_db \
   -e "SELECT COUNT(*) FROM alumni;"
```

Harapan: HTTP **200**, dan jumlah alumni **1966**.

**Kenapa langkah ini wajib:** kalau import dump gagal, `restart: unless-stopped`
akan menghidupkan ulang container; datadir sudah terlanjur dibuat sehingga import
di-skip, dan kamu dapat database **kosong yang statusnya `healthy`**. Dari luar
kelihatan sehat total. Ini benar-benar terjadi saat pengujian.

Kalau hasilnya `0` atau `Table doesn't exist`:

```bash
dc logs db | grep -i error
dc down -v && dc up -d --build      # -v menghapus volume, import diulang dari nol
```

---

# BAGIAN 3 — Caddy dan HTTPS

## 3.1 Install Caddy

Paket `caddy` **tidak ada di repo Ubuntu 22.04**, dan di 24.04 versinya sudah lawas
(2.6.2). Pakai repo resmi Caddy:

```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' \
  | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' \
  | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install -y caddy
```

## 3.2 Pasang konfigurasi

```bash
sudo cp ~/web-alumni/Caddyfile /etc/caddy/Caddyfile
# Caddyfile di repo sudah berisi ikafibundip.com + redirect www, jadi
# biasanya tidak perlu diedit lagi.
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

`caddy validate` menangkap salah ketik sebelum reload — biasakan menjalankannya.

## 3.3 Cek sertifikat terbit

```bash
sudo systemctl status caddy
sudo journalctl -u caddy -n 30 --no-pager | grep -i "certificate\|error"
curl -I https://ikafibundip.com
curl -I https://www.ikafibundip.com   # harus 301 ke ikafibundip.com
```

Caddy menerbitkan **dua** sertifikat (apex dan www). Biasanya beberapa detik. Redirect HTTP→HTTPS otomatis,
tidak perlu dikonfigurasi.

---

# BAGIAN 4 — Setelah live

## 4.1 Checklist

- [ ] `https://ikafibundip.com` terbuka, gembok hijau
- [ ] `http://ikafibundip.com` otomatis dialihkan ke HTTPS
- [ ] `https://www.ikafibundip.com` dialihkan ke tanpa-www
- [ ] Beranda menampilkan **1.966 alumni / 14 angkatan / 9 jurusan**
- [ ] Halaman `/jurusan` menampilkan angka per prodi (452, 423, 380, 336, 153, 30 …)
- [ ] `/alumni`, `/berita`, `/galeri`, `/statistik` terbuka normal
- [ ] Bisa login di `/admin/login`
- [ ] Upload foto dari panel admin berhasil (uji satu file)
- [ ] `curl -I http://103.89.2.238:5005` dari **laptop** harus **gagal** — port app tidak boleh publik

## 4.2 Ganti password admin

Password admin ikut isi dump lama, bukan `admin123`. Ganti:

```bash
cd ~/web-alumni && source .env.production
HASH=$(dc exec -T web python -c \
  "from werkzeug.security import generate_password_hash; print(generate_password_hash('PASSWORD_BARU'))" | tr -d '\r')
dc exec -T db mariadb -u root -p"$DB_ROOT_PASSWORD" alumni_db \
  -e "UPDATE admins SET password_hash='$HASH' WHERE username='admin';"
```

Aman dari penimpaan: `init_admin()` hanya me-reset password kalau hash-nya pendek
(< 30 karakter), sedangkan hash scrypt jauh lebih panjang.

## 4.3 Backup otomatis

```bash
mkdir -p ~/backup
crontab -e
```

Tambahkan (backup tiap hari jam 2 pagi, simpan 14 hari terakhir):

```cron
0 2 * * * cd ~/web-alumni && set -a && . ./.env.production && set +a && docker compose --env-file .env.production exec -T db mariadb-dump -u root -p"$DB_ROOT_PASSWORD" alumni_db | gzip > ~/backup/db_$(date +\%F).sql.gz
30 2 * * * tar czf ~/backup/uploads_$(date +\%F).tar.gz -C ~/web-alumni data/uploads
0 3 * * * find ~/backup -name "*.gz" -mtime +14 -delete
```

Sesekali **tarik backup-nya ke laptop** — backup yang cuma ada di server yang sama
tidak menolong kalau VPS-nya hilang:

```bash
scp -i ~/.ssh/alumni-web.pem alumni.web@103.89.2.238:~/backup/db_*.sql.gz ./
```

**Restore:**

```bash
gunzip -c ~/backup/db_2026-09-01.sql.gz \
  | dc exec -T db mariadb -u root -p"$DB_ROOT_PASSWORD" alumni_db
```

## 4.4 Update kode

```bash
cd ~/web-alumni
git pull
dc up -d --build
```

Data DB dan foto aman — keduanya di luar image.

## 4.5 Perintah harian

```bash
dc ps                    # status container
dc logs -f web           # log aplikasi
dc logs db               # log database
dc restart web           # restart app saja
docker stats --no-stream # pemakaian RAM/CPU
sudo journalctl -u caddy -f
```

## 4.6 Akses database dari laptop

Jangan buka port 3306 ke internet. Pakai SSH tunnel:

```bash
ssh -i ~/.ssh/alumni-web.pem -L 3307:127.0.0.1:3306 alumni.web@103.89.2.238
# lalu sambungkan TablePlus/Workbench ke 127.0.0.1:3307
```

Supaya tunnel tembus, tambahkan di service `db` pada `docker-compose.yml`:

```yaml
    ports:
      - "127.0.0.1:3306:3306"
```

---

# Troubleshooting

**`required variable DB_PASSWORD is missing a value`**
Lupa `--env-file .env.production`. Ini disengaja — compose berhenti berisik
daripada diam-diam memakai nilai lain.

**DB kosong padahal container `healthy`**
Import gagal saat boot pertama lalu di-skip karena datadir sudah ada. Lihat
`dc logs db | grep -i error`, perbaiki, lalu `dc down -v && dc up -d --build`.

**`ERROR: Can't read from a directory 'stdin'` di log db**
`alumni_db.sql` tidak ditemukan di path bind mount, jadi Docker membuatkan
direktori kosong. Pastikan file itu ada di `~/web-alumni/alumni_db.sql`
(`ls -la` untuk memastikan ukurannya ~330KB, bukan 0).

**Container db exit 1, log berisi `Creating user root`**
`DB_USER=root` di `.env.production`. Ganti jadi `alumni`, lalu `dc down -v && dc up -d`.

**Upload foto gagal / permission denied**
`sudo chown -R 1000:1000 ~/web-alumni/data/uploads`

**Sertifikat tidak terbit**
Cek DNS sudah mengarah (`dig +short ikafibundip.com @1.1.1.1`), port 80 terbuka di ufw
**dan** di firewall panel Biznet, lalu `sudo journalctl -u caddy -n 50 --no-pager`.

**Build kehabisan memori / server nge-hang saat build**
Swap belum aktif. Cek `free -h`, ulangi langkah 1.4.

**Website 502 Bad Gateway**
Container web mati. `dc ps` dan `dc logs web`.

---

# Catatan penting

- **Gambar berita & galeri saat ini broken.** Dump mereferensikan 5 thumbnail dan
  3 foto galeri yang nama filenya tidak ada di folder upload mana pun — file
  aslinya hanya ada di mesin tempat dump itu dibuat. Salin manual ke
  `data/uploads/news/` dan `data/uploads/gallery/`, atau upload ulang lewat panel
  admin. Data alumni tidak terpengaruh (kolom `foto` memang kosong semua).

- **Import dump hanya jalan sekali seumur volume.** `docker-entrypoint-initdb.d`
  dieksekusi hanya saat volume `db_data` masih kosong. Untuk memuat dump baru:
  restore manual (4.3), atau `dc down -v` yang **menghapus seluruh database**.

- **Port app diikat ke `127.0.0.1`.** Jangan diubah jadi `"5005:5005"`. Docker
  menulis aturan iptables sendiri yang **menembus ufw**, jadi port itu akan
  terbuka ke internet meskipun `ufw status` bilang deny.

- **`alumni_db.sql` jangan di-commit**, apalagi ke repo publik — isinya data
  pribadi 1966 alumni. Sudah masuk `.gitignore`.

- **Paginasi aplikasi ini in-memory.** Tiap membuka `/alumni`, seluruh baris
  ditarik ke Python dulu baru dipotong 12 per halaman. Aman di angka 1966, tapi
  bebannya tumbuh mengikuti jumlah alumni, bukan jumlah item per halaman.

- **`url_for(..., _external=True)` akan menghasilkan `http://`**, bukan `https://`,
  karena aplikasi belum memakai `ProxyFix` dari Werkzeug. Tidak masalah selama
  semua link internal masih relatif — dan saat ini memang begitu.
