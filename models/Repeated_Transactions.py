from datetime import datetime

from . import db, Category, Account


class Repeated_Transaction(db.Model):
    __tablename__ = 'Repeated_Transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    end_date = db.Column(db.Date, default=None, nullable=True)
    next_transaction_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    period = db.Column(db.Integer, nullable=False)  # the number of days till next transaction

    def __init__(self, user_id, account_id, amount, category_id, description=None, start_date=None,
                 end_date=None, period="30"):
        self.user_id = user_id
        self.account_id = account_id
        self.amount = amount
        self.category_id = category_id
        self.description = description
        self.period = period
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date is not None else datetime.utcnow()
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date is not None else None
        self.next_transaction_date = self.start_date

    def update(self, data: dict):
        self.amount = data['amount'] if data.get('amount') else self.amount
        self.category_id = data['category_id'] if data.get('category_id') else self.category_id
        self.description = data.get('description') if data.get('description') else self.description
        self.start_date = datetime.strptime(data['start_date'], "%Y-%m-%d") if data.get(
            'start_date') else self.start_date
        self.end_date = datetime.strptime(data['end_date'], "%Y-%m-%d") if data.get('end_date') else self.end_date
        self.next_transaction_date = datetime.strptime(data['next_transaction_date'], "%Y-%m-%d") if data.get(
            'next_transaction_date') else self.next_transaction_date
        self.account_id = data['account_id'] if data.get('account_id') else self.account_id

    def to_dict(self):
        category = Category.query.filter_by(id=self.category_id, user_id=self.user_id).first()
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_id': self.account_id,
            'category_id': self.category_id,
            'description': self.description,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat() if self.end_date is not None else "forever",
            'next_transaction_date': self.next_transaction_date,
            'amount': str(self.amount),
            'period': self.period,
            'category_name': category.name,
            'type': category.type,
            'account_name': Account.query.filter_by(id=self.account_id, user_id=self.user_id).first().name
        }

    def __repr__(self):
        return f'< Repeated_Transaction {self.amount} on {self.start_date} , period {self.period} >'
