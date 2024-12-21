# models/debt.py
from . import db
from datetime import datetime


class Debt(db.Model):
    __tablename__ = 'debts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    remaining = db.Column(db.Numeric(10, 2), nullable=False)
    paid = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    description = db.Column(db.String(255), nullable=True)
    person_name = db.Column(db.String(50), nullable=True)
    type = db.Column(db.String(50), nullable=False)  # "creditor" or "debtor"

    debtPayments = db.relationship('DebtPayments', backref='debts', lazy=True)

    def __init__(self, user_id, account_id, amount, person_name, type, description=None, paid=0.0):
        self.user_id = user_id
        self.account_id = account_id
        self.amount = amount
        self.paid = paid
        self.remaining = float(self.amount) - paid
        self.type = type
        self.person_name = person_name
        self.description = description

    def update(self, data: dict):
        self.amount = data['amount'] if data.get('amount') else self.amount
        self.paid = data['paid'] if data.get('paid') else self.paid
        self.remaining = self.amount - self.paid
        self.type = data['type'] if data.get('type') else self.type
        self.description = data.get('description') if data.get('description') else self.description

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_id': self.account_id,
            'amount': str(self.amount),
            'remaining': str(self.remaining),
            'paid': str(self.paid),
            'person_name': self.person_name,
            'description': self.description,
            'type': self.type
        }

    def __repr__(self):
        return f'<Debt {self.type} of {self.amount}>'
