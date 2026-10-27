from flask_login import UserMixin
from app import mysql, login_manager


class Admin(UserMixin):
    def __init__(self, id, username, email, nama_lengkap):
        self.id = id
        self.username = username
        self.email = email
        self.nama_lengkap = nama_lengkap

    @staticmethod
    def get_by_id(admin_id):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admins WHERE id = %s", (admin_id,))
        row = cur.fetchone()
        cur.close()
        if row:
            return Admin(row['id'], row['username'], row['email'], row['nama_lengkap'])
        return None

    @staticmethod
    def get_by_username(username):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admins WHERE username = %s", (username,))
        row = cur.fetchone()
        cur.close()
        return row


@login_manager.user_loader
def load_user(user_id):
    return Admin.get_by_id(int(user_id))
