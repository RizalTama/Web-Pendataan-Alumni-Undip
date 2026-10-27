from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import mysql
from app.utils.helpers import save_image, delete_image, slugify, paginate

admin_berita_bp = Blueprint('admin_berita', __name__)


def generate_unique_slug(judul, exclude_id=None):
    base_slug = slugify(judul)
    slug = base_slug
    counter = 1
    cur = mysql.connection.cursor()

    while True:
        if exclude_id:
            cur.execute("SELECT id FROM berita WHERE slug = %s AND id != %s", (slug, exclude_id))
        else:
            cur.execute("SELECT id FROM berita WHERE slug = %s", (slug,))
        if not cur.fetchone():
            break
        slug = f"{base_slug}-{counter}"
        counter += 1

    cur.close()
    return slug


@admin_berita_bp.route('/berita')
@login_required
def index():
    kategori = request.args.get('kategori', '').strip()
    page = int(request.args.get('page', 1))

    cur = mysql.connection.cursor()

    if kategori in ('berita', 'pengumuman'):
        cur.execute("SELECT * FROM berita WHERE kategori = %s ORDER BY created_at DESC", (kategori,))
    else:
        cur.execute("SELECT * FROM berita ORDER BY created_at DESC")

    all_berita = cur.fetchall()
    cur.close()

    pagination = paginate(all_berita, page, 10)

    return render_template('admin/berita/index.html',
                           pagination=pagination,
                           kategori_filter=kategori)


@admin_berita_bp.route('/berita/tambah', methods=['GET', 'POST'])
@login_required
def tambah():
    if request.method == 'POST':
        judul = request.form.get('judul', '').strip()
        konten = request.form.get('konten', '').strip()

        if not judul or not konten:
            flash('Judul dan konten wajib diisi.', 'danger')
            return render_template('admin/berita/form.html', berita=None)

        kategori = request.form.get('kategori', 'berita')
        status = request.form.get('status', 'draft')
        slug = generate_unique_slug(judul)

        thumbnail = None
        if 'thumbnail' in request.files and request.files['thumbnail'].filename:
            thumbnail = save_image(request.files['thumbnail'], 'news', (1200, 800))
            if not thumbnail:
                flash('Format file thumbnail tidak valid.', 'danger')
                return render_template('admin/berita/form.html', berita=None)

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO berita (judul, slug, konten, thumbnail, kategori, status, admin_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (judul, slug, konten, thumbnail, kategori, status, current_user.id))
        mysql.connection.commit()
        cur.close()

        flash('Berita berhasil ditambahkan.', 'success')
        return redirect(url_for('admin_berita.index'))

    return render_template('admin/berita/form.html', berita=None)


@admin_berita_bp.route('/berita/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM berita WHERE id = %s", (id,))
    berita = cur.fetchone()
    cur.close()

    if not berita:
        flash('Berita tidak ditemukan.', 'danger')
        return redirect(url_for('admin_berita.index'))

    if request.method == 'POST':
        judul = request.form.get('judul', '').strip()
        konten = request.form.get('konten', '').strip()

        if not judul or not konten:
            flash('Judul dan konten wajib diisi.', 'danger')
            return render_template('admin/berita/form.html', berita=berita)

        kategori = request.form.get('kategori', 'berita')
        status = request.form.get('status', 'draft')

        # Regenerate slug only if title changed
        if judul != berita['judul']:
            slug = generate_unique_slug(judul, exclude_id=id)
        else:
            slug = berita['slug']

        thumbnail = berita['thumbnail']
        if 'thumbnail' in request.files and request.files['thumbnail'].filename:
            new_thumb = save_image(request.files['thumbnail'], 'news', (1200, 800))
            if not new_thumb:
                flash('Format file thumbnail tidak valid.', 'danger')
                return render_template('admin/berita/form.html', berita=berita)
            if berita['thumbnail']:
                delete_image(berita['thumbnail'], 'news')
            thumbnail = new_thumb

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE berita SET judul=%s, slug=%s, konten=%s, thumbnail=%s,
                kategori=%s, status=%s WHERE id=%s
        """, (judul, slug, konten, thumbnail, kategori, status, id))
        mysql.connection.commit()
        cur.close()

        flash('Berita berhasil diperbarui.', 'success')
        return redirect(url_for('admin_berita.index'))

    return render_template('admin/berita/form.html', berita=berita)


@admin_berita_bp.route('/berita/hapus/<int:id>', methods=['POST'])
@login_required
def hapus(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT thumbnail FROM berita WHERE id = %s", (id,))
    berita = cur.fetchone()

    if berita:
        if berita['thumbnail']:
            delete_image(berita['thumbnail'], 'news')
        cur.execute("DELETE FROM berita WHERE id = %s", (id,))
        mysql.connection.commit()
        flash('Berita berhasil dihapus.', 'success')
    else:
        flash('Berita tidak ditemukan.', 'danger')

    cur.close()
    return redirect(url_for('admin_berita.index'))
