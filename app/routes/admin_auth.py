from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.models.admin import Admin

admin_auth_bp = Blueprint('admin_auth', __name__)


@admin_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username dan password wajib diisi.', 'danger')
            return render_template('admin/login.html')

        row = Admin.get_by_username(username)
        if row and check_password_hash(row['password_hash'], password):
            admin = Admin(row['id'], row['username'], row['email'], row['nama_lengkap'])
            login_user(admin)
            next_page = request.args.get('next')
            flash(f'Selamat datang, {admin.nama_lengkap}!', 'success')
            return redirect(next_page or url_for('admin_dashboard.dashboard'))
        else:
            flash('Username atau password salah.', 'danger')

    return render_template('admin/login.html')


@admin_auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('admin_auth.login'))
