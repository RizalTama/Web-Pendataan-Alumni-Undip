from app import create_app, mysql
from werkzeug.security import generate_password_hash
from app.utils.helpers import slugify

app = create_app()

alumni_data = [
    ("Andi Prasetyo",        2018, "Teknik Informatika",   "Software Engineer",       "Gojek",             "Jakarta",    "andi.prasetyo@gmail.com",    1),
    ("Budi Santoso",         2019, "Sistem Informasi",      "Data Analyst",            "Tokopedia",         "Jakarta",    "budi.santoso@gmail.com",     0),
    ("Citra Dewi",           2017, "Teknik Informatika",   "UI/UX Designer",          "Traveloka",         "Bandung",    "citra.dewi@gmail.com",       1),
    ("Dian Rahayu",          2020, "Manajemen Informatika","Product Manager",          "Shopee",            "Jakarta",    "dian.rahayu@gmail.com",      0),
    ("Eko Firmansyah",       2018, "Teknik Komputer",      "Network Engineer",        "Telkom Indonesia",  "Surabaya",   "eko.firmansyah@gmail.com",   0),
    ("Farah Aulia",          2021, "Sistem Informasi",      "Business Analyst",        "Bank BCA",          "Jakarta",    "farah.aulia@gmail.com",      1),
    ("Gilang Ramadhan",      2019, "Teknik Informatika",   "Backend Developer",       "Bukalapak",         "Yogyakarta", "gilang.ramadhan@gmail.com",  0),
    ("Hana Pertiwi",         2020, "Ilmu Komputer",        "Machine Learning Engineer","Google",            "Jakarta",    "hana.pertiwi@gmail.com",     1),
    ("Irfan Maulana",        2017, "Teknik Elektro",       "IoT Engineer",            "Pertamina",         "Balikpapan", "irfan.maulana@gmail.com",    0),
    ("Joko Widodo",          2022, "Manajemen Informatika","Junior Developer",         "Startup Lokal",     "Semarang",   "joko.widodo@gmail.com",      0),
    ("Kartika Sari",         2018, "Sistem Informasi",      "Quality Assurance",       "Blibli",            "Jakarta",    "kartika.sari@gmail.com",     0),
    ("Lukman Hakim",         2019, "Teknik Informatika",   "DevOps Engineer",         "Grab",              "Jakarta",    "lukman.hakim@gmail.com",     1),
    ("Mega Wulandari",       2021, "Ilmu Komputer",        "Data Scientist",          "Akulaku",           "Bandung",    "mega.wulandari@gmail.com",   0),
    ("Nanda Rizky",          2020, "Teknik Komputer",      "Cybersecurity Analyst",   "Bank Mandiri",      "Jakarta",    "nanda.rizky@gmail.com",      0),
    ("Olivia Putri",         2022, "Teknik Informatika",   "Frontend Developer",      "Freelance",         "Bali",       "olivia.putri@gmail.com",     1),
]

berita_data = [
    (
        "Reuni Akbar Alumni 2024: Mempererat Tali Silaturahmi",
        """<p>Dengan bangga kami mengumumkan pelaksanaan <strong>Reuni Akbar Alumni 2024</strong> yang akan diselenggarakan pada bulan Desember mendatang. Acara ini merupakan momen yang sangat ditunggu-tunggu oleh seluruh keluarga besar alumni.</p>
        <p>Reuni akbar tahun ini akan menampilkan berbagai kegiatan menarik, mulai dari sesi networking, talkshow karir bersama alumni sukses, hingga hiburan yang meriah. Ini adalah kesempatan emas untuk kembali bertemu dengan teman-teman lama dan menjalin koneksi baru.</p>
        <p>Segera daftarkan diri Anda dan jadikan momen ini tak terlupakan!</p>""",
        "berita", "published"
    ),
    (
        "Alumni Hana Pertiwi Raih Posisi Machine Learning Engineer di Google",
        """<p>Kebanggaan besar bagi keluarga besar alumni! <strong>Hana Pertiwi</strong>, lulusan angkatan 2020 dari program studi Ilmu Komputer, berhasil meraih posisi bergengsi sebagai Machine Learning Engineer di Google.</p>
        <p>Hana merupakan salah satu alumni yang selama masa studinya dikenal aktif dalam berbagai kompetisi teknologi tingkat nasional maupun internasional. Prestasi ini menjadi inspirasi bagi seluruh mahasiswa dan alumni.</p>
        <p>"Teruslah belajar dan jangan takut untuk bermimpi besar," pesan Hana kepada adik-adik alumninya.</p>""",
        "berita", "published"
    ),
    (
        "Webinar Karir: Tips Lolos Seleksi di Perusahaan Teknologi Top",
        """<p>Program alumni kembali menghadirkan webinar menarik bertema <strong>"Tips Lolos Seleksi di Perusahaan Teknologi Top"</strong>. Webinar ini akan menghadirkan para alumni yang saat ini bekerja di perusahaan-perusahaan teknologi terkemuka.</p>
        <p>Pembicara yang akan hadir antara lain alumni dari Gojek, Tokopedia, Google, dan Grab. Mereka akan berbagi pengalaman dan tips konkret dalam menghadapi proses rekrutmen yang kompetitif.</p>
        <p>Webinar akan dilaksanakan secara online melalui platform Zoom. Pendaftaran gratis untuk seluruh alumni dan mahasiswa aktif.</p>""",
        "berita", "published"
    ),
    (
        "Pengumuman: Beasiswa Alumni untuk Mahasiswa Berprestasi",
        """<p>Ikatan Alumni dengan bangga mengumumkan program <strong>Beasiswa Alumni</strong> untuk tahun akademik 2024/2025. Program beasiswa ini merupakan bentuk kepedulian alumni terhadap adik-adik mahasiswa yang berprestasi namun membutuhkan dukungan finansial.</p>
        <p><strong>Persyaratan:</strong></p>
        <ul>
        <li>Mahasiswa aktif semester 3 ke atas</li>
        <li>IPK minimal 3,50</li>
        <li>Aktif dalam kegiatan kemahasiswaan</li>
        <li>Surat rekomendasi dari dosen pembimbing</li>
        </ul>
        <p>Pendaftaran dibuka hingga 31 Oktober 2024. Formulir dapat diunduh di website resmi kampus.</p>""",
        "pengumuman", "published"
    ),
    (
        "Pengumuman Perubahan Jadwal Pertemuan Rutin Alumni",
        """<p>Diberitahukan kepada seluruh anggota Ikatan Alumni bahwa <strong>pertemuan rutin bulanan</strong> yang sebelumnya dijadwalkan pada minggu pertama setiap bulan, akan diubah menjadi minggu kedua mulai bulan November 2024.</p>
        <p>Perubahan jadwal ini dilakukan untuk mengakomodasi kehadiran lebih banyak anggota alumni yang memiliki kesibukan di awal bulan.</p>
        <p>Untuk informasi lebih lanjut, silakan hubungi sekretariat Ikatan Alumni melalui email yang tertera di halaman kontak. Kami mohon maaf atas ketidaknyamanan yang ditimbulkan.</p>""",
        "pengumuman", "published"
    ),
]


def run_seed():
    with app.app_context():
        cur = mysql.connection.cursor()

        # Seed alumni
        print("Memasukkan data alumni...")
        for nama, angkatan, jurusan, pekerjaan, perusahaan, kota, email, unggulan in alumni_data:
            # Skip if already exists
            cur.execute("SELECT id FROM alumni WHERE nama = %s AND angkatan = %s", (nama, angkatan))
            if cur.fetchone():
                print(f"  [skip] {nama} sudah ada.")
                continue

            inisial = nama[0].upper()
            bio = f"{nama} adalah alumni {jurusan} angkatan {angkatan} yang saat ini bekerja sebagai {pekerjaan} di {perusahaan}, berdomisili di {kota}."

            cur.execute("""
                INSERT INTO alumni (nama, angkatan, jurusan, foto, pekerjaan, perusahaan,
                                    kota_domisili, email, linkedin, bio, is_unggulan)
                VALUES (%s, %s, %s, NULL, %s, %s, %s, %s, %s, %s, %s)
            """, (
                nama, angkatan, jurusan, pekerjaan, perusahaan,
                kota, email,
                f"https://linkedin.com/in/{nama.lower().replace(' ', '-')}",
                bio, unggulan
            ))
            print(f"  [+] {nama} ({jurusan} {angkatan})")

        # Seed berita
        print("\nMemasukkan data berita...")
        cur.execute("SELECT id FROM admins WHERE username = 'admin'")
        admin = cur.fetchone()
        admin_id = admin['id'] if admin else None

        for judul, konten, kategori, status in berita_data:
            cur.execute("SELECT id FROM berita WHERE judul = %s", (judul,))
            if cur.fetchone():
                print(f"  [skip] '{judul[:40]}...' sudah ada.")
                continue

            slug = slugify(judul)
            # Ensure unique slug
            base_slug = slug
            counter = 1
            while True:
                cur.execute("SELECT id FROM berita WHERE slug = %s", (slug,))
                if not cur.fetchone():
                    break
                slug = f"{base_slug}-{counter}"
                counter += 1

            cur.execute("""
                INSERT INTO berita (judul, slug, konten, thumbnail, kategori, status, admin_id)
                VALUES (%s, %s, %s, NULL, %s, %s, %s)
            """, (judul, slug, konten, kategori, status, admin_id))
            print(f"  [+] {judul[:50]}...")

        mysql.connection.commit()
        cur.close()
        print("\n✓ Seeding selesai!")


if __name__ == '__main__':
    run_seed()
