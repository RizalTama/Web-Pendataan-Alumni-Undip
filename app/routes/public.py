import re

from flask import Blueprint, render_template, request, abort
from app import mysql
from app.utils.helpers import paginate

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def beranda():
    cur = mysql.connection.cursor()

    # Stats
    cur.execute("SELECT COUNT(*) as total FROM alumni")
    total_alumni = cur.fetchone()['total']

    cur.execute("SELECT COUNT(DISTINCT angkatan) as total FROM alumni")
    total_angkatan = cur.fetchone()['total']

    cur.execute("SELECT COUNT(DISTINCT jurusan) as total FROM alumni")
    total_jurusan = cur.fetchone()['total']

    # Alumni unggulan (max 6)
    cur.execute("SELECT * FROM alumni WHERE is_unggulan = 1 ORDER BY created_at DESC LIMIT 6")
    alumni_unggulan = cur.fetchall()

    # Berita terbaru (4)
    cur.execute("SELECT * FROM berita WHERE status='published' ORDER BY created_at DESC LIMIT 4")
    berita_terbaru = cur.fetchall()

    # Galeri terbaru (6)
    cur.execute("SELECT * FROM galeri ORDER BY created_at DESC LIMIT 6")
    galeri_terbaru = cur.fetchall()

    cur.close()

    return render_template('public/beranda.html',
                           total_alumni=total_alumni,
                           total_angkatan=total_angkatan,
                           total_jurusan=total_jurusan,
                           alumni_unggulan=alumni_unggulan,
                           berita_terbaru=berita_terbaru,
                           galeri_terbaru=galeri_terbaru)


@public_bp.route('/alumni')
def direktori():
    q = request.args.get('q', '').strip()
    angkatan = request.args.get('angkatan', '').strip()
    jurusan = request.args.get('jurusan', '').strip()
    page = int(request.args.get('page', 1))

    cur = mysql.connection.cursor()

    conditions = []
    params = []

    if q:
        conditions.append("(nama LIKE %s OR pekerjaan LIKE %s OR perusahaan LIKE %s OR kota_domisili LIKE %s)")
        params += [f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%']
    if angkatan:
        conditions.append("angkatan = %s")
        params.append(angkatan)
    if jurusan:
        conditions.append("jurusan = %s")
        params.append(jurusan)

    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    cur.execute(f"SELECT * FROM alumni {where} ORDER BY nama", params)
    all_alumni = cur.fetchall()

    cur.execute("SELECT DISTINCT angkatan FROM alumni ORDER BY angkatan DESC")
    angkatan_list = [r['angkatan'] for r in cur.fetchall()]

    cur.execute("SELECT DISTINCT jurusan FROM alumni ORDER BY jurusan")
    jurusan_list = [r['jurusan'] for r in cur.fetchall()]

    cur.close()

    pagination = paginate(all_alumni, page, 12)

    return render_template('public/direktori.html',
                           pagination=pagination,
                           q=q,
                           angkatan_filter=angkatan,
                           jurusan_filter=jurusan,
                           angkatan_list=angkatan_list,
                           jurusan_list=jurusan_list)


@public_bp.route('/alumni/<int:id>')
def profil_alumni(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM alumni WHERE id = %s", (id,))
    alumni = cur.fetchone()
    cur.close()

    if not alumni:
        abort(404)

    return render_template('public/profil_alumni.html', alumni=alumni)


@public_bp.route('/berita')
def berita():
    kategori = request.args.get('kategori', '').strip()
    page = int(request.args.get('page', 1))

    cur = mysql.connection.cursor()

    if kategori in ('berita', 'pengumuman'):
        cur.execute("SELECT * FROM berita WHERE status='published' AND kategori=%s ORDER BY created_at DESC", (kategori,))
    else:
        cur.execute("SELECT * FROM berita WHERE status='published' ORDER BY created_at DESC")

    all_berita = cur.fetchall()
    cur.close()

    pagination = paginate(all_berita, page, 9)

    return render_template('public/berita.html',
                           pagination=pagination,
                           kategori_filter=kategori)


@public_bp.route('/berita/<slug>')
def detail_berita(slug):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM berita WHERE slug = %s AND status='published'", (slug,))
    berita = cur.fetchone()

    if not berita:
        cur.close()
        abort(404)

    cur.execute("SELECT * FROM berita WHERE status='published' AND id != %s ORDER BY created_at DESC LIMIT 4", (berita['id'],))
    berita_lainnya = cur.fetchall()
    cur.close()

    return render_template('public/detail_berita.html',
                           berita=berita,
                           berita_lainnya=berita_lainnya)


@public_bp.route('/galeri')
def galeri():
    page = int(request.args.get('page', 1))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM galeri ORDER BY created_at DESC")
    all_galeri = cur.fetchall()
    cur.close()

    pagination = paginate(all_galeri, page, 12)

    return render_template('public/galeri.html', pagination=pagination)


# Profil jurusan (statis) — jumlah alumni diambil dari DB berdasarkan nama.
# `db_aliases` menampung variasi penulisan kolom `jurusan` di database (mis.
# ada tambahan "(S1)"/"(S2)" atau penulisan singkat) supaya tetap bisa
# dicocokkan dengan profil di bawah walau tidak identik persis.
JURUSAN_PROFILES = [
    {
        'nama': 'Sastra Indonesia',
        'akreditasi': 'Unggul',
        'deskripsi': 'Mengkaji bahasa, sastra, dan filologi Indonesia secara mendalam — dari kajian teks klasik Nusantara hingga sastra modern. Lulusan berkarier sebagai editor, penulis, peneliti bahasa, jurnalis, hingga praktisi industri kreatif.',
        'db_aliases': ['sastra indonesia', 'sastra indonesia (s1)'],
    },
    {
        'nama': 'Sastra Inggris',
        'akreditasi': 'A',
        'deskripsi': 'Mempelajari bahasa, sastra, dan budaya Inggris serta kajian penerjemahan dan linguistik terapan. Lulusan banyak berkiprah sebagai penerjemah, pengajar, praktisi media, dan profesional di perusahaan multinasional.',
        'db_aliases': ['sastra inggris', 'sastra inggris (s1)'],
    },
    {
        'nama': 'Sejarah',
        'akreditasi': 'Unggul',
        'deskripsi': 'Menelaah dinamika sejarah Indonesia dan dunia dengan pendekatan riset arsip dan historiografi. Lulusan berkarier sebagai sejarawan, peneliti, kurator museum, arsiparis, dan penulis.',
        'db_aliases': ['sejarah', 'sejarah (s1)'],
    },
    {
        'nama': 'Antropologi Sosial',
        'akreditasi': 'Unggul',
        'deskripsi': 'Mengkaji keragaman budaya dan masyarakat melalui riset etnografi. Lulusan bekerja di lembaga riset, NGO, pemerintahan, konsultan sosial, dan pengembangan masyarakat.',
        'db_aliases': ['antropologi sosial', 'antropologi sosial (s1)'],
    },
    {
        'nama': 'Ilmu Perpustakaan dan Informasi',
        'akreditasi': 'A',
        'deskripsi': 'Memadukan pengelolaan informasi, kearsipan, dan teknologi informasi modern. Lulusan menjadi pustakawan, information specialist, pengelola arsip digital, dan data curator.',
        'db_aliases': ['ilmu perpustakaan', 'ilmu perpustakaan (s1)', 'ilmu perpustakaan dan informasi', 'ilmu perpustakaan dan informasi (s1)'],
    },
    {
        'nama': 'Bahasa dan Kebudayaan Jepang',
        'akreditasi': 'A',
        'deskripsi': 'Mempelajari bahasa, sastra, dan budaya Jepang secara komprehensif. Lulusan berkarier sebagai penerjemah, pengajar, serta profesional di perusahaan dan lembaga kerja sama Indonesia–Jepang.',
        'db_aliases': ['bahasa dan kebudayaan jepang', 'bahasa dan kebudayaan jepang (s1)'],
    },
]

PASCASARJANA_PROFILES = [
    {'nama': 'Magister Ilmu Susastra', 'akreditasi': 'B',
     'db_aliases': ['susastra', 'susastra (s2)', 'magister ilmu susastra', 'magister ilmu susastra (s2)']},
    {'nama': 'Magister Sejarah', 'akreditasi': 'Unggul',
     'db_aliases': ['sejarah (s2)', 'magister sejarah', 'magister sejarah (s2)']},
    {'nama': 'Magister Linguistik', 'akreditasi': 'A',
     'db_aliases': ['ilmu linguistik', 'ilmu linguistik (s2)', 'magister linguistik', 'magister linguistik (s2)']},
    {'nama': 'Doktor Sejarah', 'akreditasi': 'Unggul',
     'db_aliases': ['sejarah (s3)', 'doktor sejarah', 'doktor sejarah (s3)']},
]


def _normalize_jurusan(value):
    """Lowercase + collapse whitespace so DB values like 'Ilmu Perpustakaan  (S1)'
    can be matched against a clean alias like 'ilmu perpustakaan (s1)'."""
    return re.sub(r'\s+', ' ', (value or '')).strip().lower()


def _resolve_jurusan_profiles(profiles):
    cur = mysql.connection.cursor()
    cur.execute("SELECT jurusan, COUNT(*) as jumlah FROM alumni GROUP BY jurusan")
    rows = cur.fetchall()
    cur.close()

    # normalized alias -> (jumlah alumni, salah satu nilai asli di DB)
    counts = {}
    raw_values = {}
    for r in rows:
        if not r['jurusan']:
            continue
        key = _normalize_jurusan(r['jurusan'])
        counts[key] = counts.get(key, 0) + r['jumlah']
        raw_values.setdefault(key, r['jurusan'])

    resolved = []
    for p in profiles:
        aliases = p.get('db_aliases', [p['nama'].lower()])
        jumlah = sum(counts.get(a, 0) for a in aliases)
        # nilai asli di kolom `jurusan` (dengan suffix "(S1)" dsb) dipakai
        # untuk filter di halaman direktori, karena filter di sana adalah
        # pencocokan persis (WHERE jurusan = %s).
        raw_value = next((raw_values[a] for a in aliases if a in raw_values), p['nama'])
        resolved.append({**p, 'jumlah_alumni': jumlah, 'jurusan_query': raw_value})

    return resolved


@public_bp.route('/jurusan')
def jurusan():
    profiles = _resolve_jurusan_profiles(JURUSAN_PROFILES)
    pascasarjana = _resolve_jurusan_profiles(PASCASARJANA_PROFILES)

    return render_template('public/jurusan.html',
                           jurusan_list=profiles,
                           pascasarjana_list=pascasarjana)


@public_bp.route('/statistik')
def statistik():
    cur = mysql.connection.cursor()

    # Alumni per angkatan
    cur.execute("SELECT angkatan, COUNT(*) as jumlah FROM alumni GROUP BY angkatan ORDER BY angkatan")
    per_angkatan = cur.fetchall()

    # Per jurusan
    cur.execute("SELECT jurusan, COUNT(*) as jumlah FROM alumni GROUP BY jurusan ORDER BY jumlah DESC")
    per_jurusan = cur.fetchall()

    # Top 10 pekerjaan
    cur.execute("""
        SELECT pekerjaan, COUNT(*) as jumlah FROM alumni
        WHERE pekerjaan IS NOT NULL AND pekerjaan != ''
        GROUP BY pekerjaan ORDER BY jumlah DESC LIMIT 10
    """)
    top_pekerjaan = cur.fetchall()

    # Top 10 kota
    cur.execute("""
        SELECT kota_domisili, COUNT(*) as jumlah FROM alumni
        WHERE kota_domisili IS NOT NULL AND kota_domisili != ''
        GROUP BY kota_domisili ORDER BY jumlah DESC LIMIT 10
    """)
    top_kota = cur.fetchall()

    cur.close()

    return render_template('public/statistik.html',
                           per_angkatan=per_angkatan,
                           per_jurusan=per_jurusan,
                           top_pekerjaan=top_pekerjaan,
                           top_kota=top_kota)
