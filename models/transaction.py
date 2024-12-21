# Transaction
from . import db, Category, Account
from datetime import datetime


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(10), nullable=False)  # processing or done

    def __init__(self, user_id, account_id, amount, category_id, description=None, date=None, status="done"):
        self.user_id = user_id
        self.account_id = account_id
        self.amount = amount
        self.category_id = category_id
        self.description = description
        self.status = status
        self.date = datetime.strptime(date, "%Y-%m-%d") if date is not None else datetime.utcnow()

    def update(self, data: dict):
        account = Account.query.filter_by(id=self.account_id, user_id=self.user_id).first()
        category = Category.query.filter_by(id=self.category_id, user_id=self.user_id).first()
        is_account_changed = False
        previous_amount = self.amount
        print(data.get('account_id'))
        print(data.get('account_id') != self.account_id)
        if data.get('account_id') and data.get('account_id') != self.account_id:
            account.update_balance(self.amount * -1, category.type)
            is_account_changed = True
        self.amount = data['amount'] if data.get('amount') else self.amount
        self.category_id = data['category_id'] if data.get('category_id') else self.category_id
        self.description = data.get('description') if data.get('description') else self.description
        self.date = datetime.strptime(data['date'], "%Y-%m-%d") if data.get('date') else self.date
        self.account_id = data['account_id'] if data.get('account_id') else self.account_id
        if is_account_changed:
            account = Account.query.filter_by(id=self.account_id, user_id=self.user_id).first()
            category = Category.query.filter_by(id=self.category_id, user_id=self.user_id).first()
            account.update_balance(self.amount, category.type)
        else:
            account.update_balance(float(self.amount) - float(previous_amount), category.type)

    def to_dict(self):
        # category = Category.query.filter_by(id=self.category_id, user_id=self.user_id).first()
        category = self.category.query.filter_by(id=self.category_id).first()
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_id': self.account_id,
            'category_id': self.category_id,
            'description': self.description,
            'date': self.date.isoformat(),
            'amount': str(self.amount),
            'peroid': self.status,
            'category_name': category.name,
            'type': category.type,
            'account_name': Account.query.filter_by(id=self.account_id, user_id=self.user_id).first().name
        }

    def __repr__(self):
        return f'<Transaction {self.amount} on {self.date} , peroid {self.status}>'
