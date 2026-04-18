"""One-off utility: update the admin user's email in the local DB.

Usage:
    python3 update_admin_email.py
"""
from app import app, db
from models import User

NEW_EMAIL = 'mo5000316@gmail.com'

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        print('admin user not found')
    else:
        print(f'Before: {admin.username} -> {admin.email}')
        admin.email = NEW_EMAIL
        db.session.commit()
        print(f'After : {admin.username} -> {admin.email}')
