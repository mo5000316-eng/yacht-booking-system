from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random
import string

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default='staff')  # admin | staff
    name = db.Column(db.String(100))
    department = db.Column(db.String(100))
    job_title = db.Column(db.String(100))
    phone = db.Column(db.String(30))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', backref='staff_user', lazy=True,
                               foreign_keys='Booking.user_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_staff(self):
        return self.role in ['admin', 'staff']

    def __repr__(self):
        return f'<User {self.username}>'


class Yacht(db.Model):
    __tablename__ = 'yachts'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100))
    capacity = db.Column(db.Integer, default=10)
    length_m = db.Column(db.Float)
    description = db.Column(db.Text)
    price_per_hour = db.Column(db.Float, default=0)
    image_url = db.Column(db.String(500))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', backref='yacht', lazy=True)

    def __repr__(self):
        return f'<Yacht {self.name}>'


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    booking_ref = db.Column(db.String(20), unique=True, nullable=False)
    booking_type = db.Column(db.String(20), default='customer')  # customer | internal

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Project
    project = db.Column(db.String(100))        # Tomorrow-166 / Tomorrow Commercial Tower / Non-exclusive member
    unit_number = db.Column(db.String(50))     # Unit number (for Tomorrow-166 / Commercial Tower)

    # Customer / Applicant info
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(30))
    client_company = db.Column(db.String(150))

    # Internal staff fields
    department = db.Column(db.String(100))
    job_title = db.Column(db.String(100))
    supervisor = db.Column(db.String(100))

    # Booking details
    yacht_id = db.Column(db.Integer, db.ForeignKey('yachts.id'), nullable=True)
    booking_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    num_passengers = db.Column(db.Integer, default=1)
    destination = db.Column(db.String(255))

    # Special requests
    has_alcohol = db.Column(db.Boolean, default=False)
    has_pizza = db.Column(db.Boolean, default=False)
    has_vegetarian = db.Column(db.Boolean, default=False)
    is_offshore = db.Column(db.Boolean, default=False)
    food_allergies = db.Column(db.String(255))
    marketing_support = db.Column(db.Boolean, default=False)
    other_requests = db.Column(db.Text)

    # Status
    status = db.Column(db.String(20), default='pending')  # pending | approved | rejected | cancelled
    rejection_reason = db.Column(db.Text)
    admin_notes = db.Column(db.Text)

    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    approver = db.relationship('User', foreign_keys=[approved_by_id],
                               backref='approved_bookings')

    @staticmethod
    def generate_ref():
        chars = string.ascii_uppercase + string.digits
        while True:
            ref = 'TW' + ''.join(random.choices(chars, k=8))
            if not Booking.query.filter_by(booking_ref=ref).first():
                return ref

    @property
    def status_badge_class(self):
        return {
            'pending':   'warning',
            'approved':  'success',
            'rejected':  'danger',
            'cancelled': 'secondary',
        }.get(self.status, 'secondary')

    @property
    def status_label(self):
        return {
            'pending':   'Pending',
            'approved':  'Approved',
            'rejected':  'Rejected',
            'cancelled': 'Cancelled',
        }.get(self.status, self.status.capitalize())

    @property
    def type_label(self):
        return 'Customer Booking' if self.booking_type == 'customer' else 'Internal Request'

    def __repr__(self):
        return f'<Booking {self.booking_ref}>'

    @property
    def total_expenses(self):
        """Sum of all expenses attached to this booking, in the booking currency."""
        return sum((e.amount or 0) for e in self.expenses)


class Expense(db.Model):
    """A cost line-item recorded against a completed booking (fuel, crew, catering, etc.)."""
    __tablename__ = 'expenses'

    CATEGORIES = [
        'Fuel',
        'Crew',
        'Catering',
        'Marina Fee',
        'Cleaning',
        'Maintenance',
        'Marketing',
        'Other',
    ]

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id', ondelete='CASCADE'),
                           nullable=False, index=True)
    category = db.Column(db.String(40), nullable=False, default='Other')
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    currency = db.Column(db.String(8), nullable=False, default='AED')
    expense_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    receipt_ref = db.Column(db.String(80))
    notes = db.Column(db.Text)

    recorded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    booking = db.relationship('Booking', backref=db.backref(
        'expenses', lazy=True, cascade='all, delete-orphan',
        order_by='Expense.expense_date.desc()'))
    recorded_by = db.relationship('User', foreign_keys=[recorded_by_id])

    def __repr__(self):
        return f'<Expense {self.category} {self.amount} {self.currency} on {self.expense_date}>'
