from flask import Blueprint, render_template
from flask_login import login_required
from app import mysql

admin_dashboard_bp = Blueprint('admin_dashboard', __name__)


@admin_dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor()

    # Stats
    cur.execute("SELECT COUNT(*) as total FROM alumni")
    total_alumni = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) as total FROM berita WHERE status='published'")
    total_berita = cur.fetchone()['total']

    cur.execute("SELECT COUNT(*) as total FROM galeri")
    total_galeri = cur.fetchone()['total']

    # Alumni per angkatan
    cur.execute("SELECT angkatan, COUNT(*) as jumlah FROM alumni GROUP BY angkatan ORDER BY angkatan")
    alumni_per_angkatan = cur.fetchall()

    # Top 8 bidang pekerjaan
    cur.execute("""
        SELECT pekerjaan, COUNT(*) as jumlah
        FROM alumni
        WHERE pekerjaan IS NOT NULL AND pekerjaan != ''
        GROUP BY pekerjaan
        ORDER BY jumlah DESC
        LIMIT 8
    """)
    top_pekerjaan = cur.fetchall()

    # 5 alumni terbaru
    cur.execute("SELECT * FROM alumni ORDER BY created_at DESC LIMIT 5")
    alumni_terbaru = cur.fetchall()

    cur.close()

    return render_template('admin/dashboard.html',
                           total_alumni=total_alumni,
                           total_berita=total_berita,
                           total_galeri=total_galeri,
                           alumni_per_angkatan=alumni_per_angkatan,
                           top_pekerjaan=top_pekerjaan,
                           alumni_terbaru=alumni_terbaru)
