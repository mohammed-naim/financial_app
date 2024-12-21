# User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    language = db.Column(db.String(5), nullable=False, default="en")
    # Relationships
    accounts = db.relationship('Account', backref='user', lazy='dynamic')
    categories = db.relationship('Category', backref='user', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    Repeated_Transactions = db.relationship('Repeated_Transaction', backref='user', lazy='dynamic')
    debts = db.relationship('Debt', backref='user', lazy='dynamic')
    investments = db.relationship('Investment', backref='user', lazy='dynamic')
    debts_payments = db.relationship('DebtPayments', backref='user', lazy='dynamic')

    def __init__(self, full_name, email, password, language="en"):
        self.full_name = full_name
        self.email = email
        self.set_password(password)
        self.language = language

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.full_name}>'
