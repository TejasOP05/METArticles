import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# Create the app
app = Flask(__name__)
# Ensure a secret key is always set for sessions/CSRF
_secret = os.environ.get("SESSION_SECRET")
if not _secret:
    logging.warning("SESSION_SECRET not set; using insecure development default. Set SESSION_SECRET in the environment for production.")
    _secret = "dev-secret-change-me"
app.secret_key = _secret
app.config["WTF_CSRF_SECRET_KEY"] = _secret
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
# Prefer DATABASE_URL if provided; otherwise use SQLite at /data for persistence in containers
database_url = os.environ.get("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
else:
    # Use a persistent path if available (e.g., Fly.io volume mounted at /data)
    sqlite_path = os.environ.get("SQLITE_PATH", "/data/app.db")
    # Fallback to local file when /data is not present
    if not os.path.isdir(os.path.dirname(sqlite_path)):
        sqlite_path = os.path.join(os.getcwd(), "app.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{sqlite_path}"
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# File upload configuration
# Persist uploads to /data/uploads when available
default_upload_dir = os.path.join(os.getcwd(), 'uploads')
data_upload_dir = "/data/uploads"
app.config['UPLOAD_FOLDER'] = data_upload_dir if os.path.isdir('/data') else default_upload_dir
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

with app.app_context():
    # Import models to ensure they're registered
    import models  # noqa: F401
    db.create_all()
    logging.info("Database tables created")
