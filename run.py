from app import create_app, mysql
from werkzeug.security import generate_password_hash

import os

app = create_app()


def init_admin():
    """Create default admin account if not exists."""
    with app.app_context():
        try:
            cur = mysql.connection.cursor()

            cur.execute("SELECT id, password_hash FROM admins WHERE username = 'admin'")
            existing = cur.fetchone()

            if not existing:
                password_hash = generate_password_hash('admin123')
                cur.execute("""
                    INSERT INTO admins (username, password_hash, email, nama_lengkap)
                    VALUES ('admin', %s, 'admin@alumni.com', 'Administrator')
                """, (password_hash,))
                mysql.connection.commit()
                print("[✓] Admin default dibuat: username=admin, password=admin123")
            else:
                # Update if password hash looks like a placeholder
                if len(existing['password_hash']) < 30:
                    password_hash = generate_password_hash('admin123')
                    cur.execute("UPDATE admins SET password_hash = %s WHERE username = 'admin'", (password_hash,))
                    mysql.connection.commit()
                    print("[✓] Password admin diperbarui.")
                else:
                    print("[✓] Admin sudah ada, tidak perlu dibuat ulang.")

            cur.close()
        except Exception as e:
            print(f"[!] Gagal inisialisasi admin: {e}")
            print("    Pastikan database alumni_db sudah dibuat dan schema.sql sudah dijalankan.")


init_admin()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5005))
    app.run(host='0.0.0.0', port=port)
