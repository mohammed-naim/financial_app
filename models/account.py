# Account
from . import db
from decimal import Decimal


class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    balance = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    disabled = db.Column(db.Boolean, default=False, nullable=False)
    # Relationships
    transactions = db.relationship('Transaction', backref='account', lazy=True)
    debts = db.relationship('Debt', backref='account', lazy=True)
    debts_payments = db.relationship('DebtPayments', backref='account', lazy=True)

    def __init__(self, user_id, name, balance=0.0, currency="ILS"):
        self.user_id = user_id
        self.name = name
        self.balance = balance
        self.currency = currency  # Set default currency to ILS

    def update_balance(self, amount, transaction_type: str):
        amount = Decimal(amount)
        if transaction_type == 'income':
            self.balance += amount
        elif transaction_type == 'expense':
            self.balance -= amount
        elif transaction_type == 'creditor':
            self.balance -= amount
        elif transaction_type == 'debtor':
            self.balance += amount

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'balance': str(self.balance),  # Convert to string for JSON serialization
            'currency': self.currency,
            'user_id': self.user_id,
            'disabled': self.disabled
        }

    def __repr__(self):
        return f'<Account {self.name}: Balance {self.balance} {self.currency}>'
