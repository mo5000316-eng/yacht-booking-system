import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'tw-yacht-dev-key-change-in-production')

    # Database: 線上部署用 PostgreSQL (DATABASE_URL 由 Render/Railway 自動注入)
    # 本地開發用 SQLite
    _db_url = os.environ.get('DATABASE_URL', '')
    if _db_url.startswith('postgres://'):
        # Render 給的是 postgres:// 但 SQLAlchemy 需要 postgresql://
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _db_url or (
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'tw_yacht.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Connection-pool tuning — critical on Render free tier where idle DB connections
    # get closed server-side after inactivity. Without pre_ping, stale connections
    # cause "connection already closed" errors on the first request after idle.
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,   # verify connection is alive before using it
        'pool_recycle': 280,     # recycle connections every ~5 min (shorter than Render's idle timeout)
        'pool_size': 5,
        'max_overflow': 5,
    }

    # Email (可選，不設定則略過 Email 功能)
    # 預設用 Gmail port 465 (SSL)，比 587 (STARTTLS) 更不容易被網路擋
    # 如要切回 STARTTLS：設 MAIL_PORT=587 + MAIL_USE_TLS=true + MAIL_USE_SSL=false
    MAIL_SERVER   = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT     = int(os.environ.get('MAIL_PORT', 465))
    MAIL_USE_SSL  = os.environ.get('MAIL_USE_SSL', 'true').lower() == 'true'
    MAIL_USE_TLS  = os.environ.get('MAIL_USE_TLS', 'false').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@tomorrowworld.com')
    # 連線 timeout，避免無限卡住
    MAIL_TIMEOUT  = 15

    # 公司資料
    COMPANY_NAME  = 'Tomorrow World'
    COMPANY_EMAIL = 'info@tomorrowworld.com'
    COMPANY_PHONE = '+852 1234 5678'
    ADMIN_EMAIL   = os.environ.get('ADMIN_EMAIL', 'mo5000316@gmail.com')

    # 初始 Admin 密碼（部署後請立即更改！）
    INIT_ADMIN_PASSWORD = os.environ.get('INIT_ADMIN_PASSWORD', 'Admin@123')
