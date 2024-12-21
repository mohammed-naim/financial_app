# Investment
from . import db, Account
from datetime import datetime
from services.investment_service import calculate_profit_or_loss, exchange_rates


class Investment(db.Model):
    __tablename__ = 'investments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    amount_invested = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    current_price = db.Column(db.Numeric(10, 2), nullable=False)
    profit_amount = db.Column(db.Numeric(10, 2), nullable=False)
    reference_currency = db.Column(db.String(3), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    sold = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(self, user_id, account_id, amount_invested, currency, purchase_price,
                 reference_currency, description=None, date=None, sold=False):
        self.user_id = user_id
        self.account_id = account_id
        self.amount_invested = amount_invested
        self.currency = currency
        self.purchase_price = purchase_price
        self.reference_currency = reference_currency
        self.current_price = exchange_rates[currency][reference_currency]
        self.profit_amount = calculate_profit_or_loss(self.amount_invested, self.purchase_price, self.current_price)
        self.description = description
        self.date = datetime.strptime(date, "%Y-%m-%d") if date is not None else datetime.utcnow()
        self.sold = sold

    def update(self, data: dict):
        old_purchase_price = self.purchase_price
        old_amount_invested = self.amount_invested
        self.amount_invested = data['amount_invested'] if data.get('amount_invested') else self.amount_invested
        self.currency = data['currency'] if data.get('currency') else self.currency
        self.purchase_price = data['purchase_price'] if data.get('purchase_price') else self.purchase_price
        self.reference_currency = data.get('reference_currency') if data.get(
            'reference_currency') else self.reference_currency
        self.current_price = exchange_rates[self.currency][self.reference_currency]
        self.description = data.get('description') if data.get('description') else self.description
        self.profit_amount = calculate_profit_or_loss(self.amount_invested, self.purchase_price, self.current_price)
        self.date = datetime.strptime(data['date'], "%Y-%m-%d") if data.get('date') else self.date
        account = Account.query.filter_by(user_id=self.user_id, id=self.account_id)
        if old_amount_invested != self.amount_invested:
            account.balance += (old_amount_invested - self.amount_invested)
        if old_purchase_price != self.purchase_price:
            account.balance += (old_purchase_price - self.purchase_price) * self.amount_invested

    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'amount_invested': str(self.amount_invested),
            'currency': self.currency,
            'purchase_price': str(self.purchase_price),
            'current_price': str(self.current_price),
            'reference_currency': self.reference_currency,
            'profit_amount': f'{calculate_profit_or_loss(self.amount_invested, self.purchase_price, self.current_price)}',
            'description': self.description,
            'date': self.date.isoformat(),
        }

    def __repr__(self):
        return f'<Investment of {self.amount_invested} {self.currency} on {self.date}>'
