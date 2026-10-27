import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask
from flask_mysqldb import MySQL
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv()

mysql = MySQL()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # Config
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
    app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
    app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '')
    app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'alumni_db')
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 5242880))

    # Init extensions
    mysql.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin_auth.login'
    login_manager.login_message = 'Silakan login terlebih dahulu.'
    login_manager.login_message_category = 'warning'

    # Import model to register user_loader
    from app.models import admin  # noqa: F401

    # Register blueprints
    from app.routes.public import public_bp
    from app.routes.admin_auth import admin_auth_bp
    from app.routes.admin_dashboard import admin_dashboard_bp
    from app.routes.admin_alumni import admin_alumni_bp
    from app.routes.admin_berita import admin_berita_bp
    from app.routes.admin_galeri import admin_galeri_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_auth_bp, url_prefix='/admin')
    app.register_blueprint(admin_dashboard_bp, url_prefix='/admin')
    app.register_blueprint(admin_alumni_bp, url_prefix='/admin')
    app.register_blueprint(admin_berita_bp, url_prefix='/admin')
    app.register_blueprint(admin_galeri_bp, url_prefix='/admin')

    return app
