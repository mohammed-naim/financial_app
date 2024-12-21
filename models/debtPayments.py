from datetime import datetime
from . import db, Account, Debt
from sqlalchemy import func


class DebtPayments(db.Model):
    __tablename__ = 'debts_payments'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    debt_id = db.Column(db.Integer, db.ForeignKey('debts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def update(self, data: dict):
        old_amount = self.amount
        self.amount = data['amount'] if data.get('amount') else self.amount
        self.date = data['date'] if data.get('date') else self.date
        self.description = data.get('description') if data.get('description') else self.description
        old_account_id = self.account_id
        self.account_id = data['account_id'] if data.get('account_id') else self.account_id
        # updating the balance of accounts and the debts paid amount
        debt = Debt.query.get(self.debt_id)
        if old_account_id != self.account_id:
            old_account = Account.query.get(old_account_id)
            old_account.update_balance(old_amount, debt.type)
            new_account = Account.query.get(self.account_id)
            new_account.update_balance(self.amount * -1, debt.type)
        elif old_amount != self.amount:
            account = Account.query.get(self.account_id)
            account.update_balance(old_amount - self.amount, debt.type)
        # get the sum of the payments ammount of a debt
        paid_amount = (
                          db.session.query(func.sum(DebtPayments.amount))
                          .filter_by(debt_id=self.debt_id)
                          .scalar()  # Use scalar() to get the result as a single value
                      ) or 0
        debt.update({'paid': paid_amount})

    def to_dict(self):
        return {
            'id': self.id,
            'debt_id': self.debt_id,
            'account_id': self.account_id,
            'amount': str(self.amount),
            'description': self.description,
            'date': self.date
        }

    def __repr__(self):
        return f"<DebtsPayments(id={self.id}, amount={self.amount}, date={self.date}, account_id={self.account_id}, debt_id={self.debt_id})>"
