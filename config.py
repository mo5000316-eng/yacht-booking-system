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

    # Email (可選，不設定則略過 Email 功能)
    MAIL_SERVER   = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT     = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS  = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@tomorrowworld.com')

    # 公司資料
    COMPANY_NAME  = 'Tomorrow World'
    COMPANY_EMAIL = 'info@tomorrowworld.com'
    COMPANY_PHONE = '+852 1234 5678'
    ADMIN_EMAIL   = os.environ.get('ADMIN_EMAIL', 'admin@tomorrowworld.com')

    # 初始 Admin 密碼（部署後請立即更改！）
    INIT_ADMIN_PASSWORD = os.environ.get('INIT_ADMIN_PASSWORD', 'Admin@123')
