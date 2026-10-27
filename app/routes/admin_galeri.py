from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import mysql
from app.utils.helpers import save_image, delete_image, paginate

admin_galeri_bp = Blueprint('admin_galeri', __name__)


@admin_galeri_bp.route('/galeri')
@login_required
def index():
    page = int(request.args.get('page', 1))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM galeri ORDER BY created_at DESC")
    all_galeri = cur.fetchall()
    cur.close()

    pagination = paginate(all_galeri, page, 12)

    return render_template('admin/galeri/index.html', pagination=pagination)


@admin_galeri_bp.route('/galeri/tambah', methods=['GET', 'POST'])
@login_required
def tambah():
    if request.method == 'POST':
        judul = request.form.get('judul', '').strip()

        if not judul:
            flash('Judul wajib diisi.', 'danger')
            return render_template('admin/galeri/form.html', galeri=None)

        if 'foto' not in request.files or not request.files['foto'].filename:
            flash('Foto wajib diunggah.', 'danger')
            return render_template('admin/galeri/form.html', galeri=None)

        foto = save_image(request.files['foto'], 'gallery', (1200, 900))
        if not foto:
            flash('Format file foto tidak valid.', 'danger')
            return render_template('admin/galeri/form.html', galeri=None)

        deskripsi = request.form.get('deskripsi', '').strip()
        tanggal_kegiatan = request.form.get('tanggal_kegiatan', '') or None

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO galeri (judul, deskripsi, foto, tanggal_kegiatan)
            VALUES (%s, %s, %s, %s)
        """, (judul, deskripsi, foto, tanggal_kegiatan))
        mysql.connection.commit()
        cur.close()

        flash('Foto berhasil diunggah.', 'success')
        return redirect(url_for('admin_galeri.index'))

    return render_template('admin/galeri/form.html', galeri=None)


@admin_galeri_bp.route('/galeri/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM galeri WHERE id = %s", (id,))
    galeri = cur.fetchone()
    cur.close()

    if not galeri:
        flash('Foto tidak ditemukan.', 'danger')
        return redirect(url_for('admin_galeri.index'))

    if request.method == 'POST':
        judul = request.form.get('judul', '').strip()
        if not judul:
            flash('Judul wajib diisi.', 'danger')
            return render_template('admin/galeri/form.html', galeri=galeri)

        deskripsi = request.form.get('deskripsi', '').strip()
        tanggal_kegiatan = request.form.get('tanggal_kegiatan', '') or None

        foto = galeri['foto']
        if 'foto' in request.files and request.files['foto'].filename:
            new_foto = save_image(request.files['foto'], 'gallery', (1200, 900))
            if not new_foto:
                flash('Format file foto tidak valid.', 'danger')
                return render_template('admin/galeri/form.html', galeri=galeri)
            delete_image(galeri['foto'], 'gallery')
            foto = new_foto

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE galeri SET judul=%s, deskripsi=%s, foto=%s, tanggal_kegiatan=%s
            WHERE id=%s
        """, (judul, deskripsi, foto, tanggal_kegiatan, id))
        mysql.connection.commit()
        cur.close()

        flash('Data foto berhasil diperbarui.', 'success')
        return redirect(url_for('admin_galeri.index'))

    return render_template('admin/galeri/form.html', galeri=galeri)


@admin_galeri_bp.route('/galeri/hapus/<int:id>', methods=['POST'])
@login_required
def hapus(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT foto FROM galeri WHERE id = %s", (id,))
    galeri = cur.fetchone()

    if galeri:
        delete_image(galeri['foto'], 'gallery')
        cur.execute("DELETE FROM galeri WHERE id = %s", (id,))
        mysql.connection.commit()
        flash('Foto berhasil dihapus.', 'success')
    else:
        flash('Foto tidak ditemukan.', 'danger')

    cur.close()
    return redirect(url_for('admin_galeri.index'))
