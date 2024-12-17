from flask import current_app
import datetime
import time
from models import Repeated_Transaction, Transaction, db

def check_repeated_transactions():
    today = datetime.date.today()
    repeated_transactions = Repeated_Transaction.query.filter(
        Repeated_Transaction.start_date <= today,
        (Repeated_Transaction.end_date.is_(None)) | (Repeated_Transaction.end_date >= today),
        Repeated_Transaction.next_transaction_date <= today
    ).all()
    new_transactions = []
    repeated_transactions_to_update = []
    for repeated_transaction in repeated_transactions:
        new_transaction = Transaction(
            amount=repeated_transaction.amount,
            category_id=repeated_transaction.category_id,
            account_id=repeated_transaction.account_id,
            description=repeated_transaction.description,
            date=today,
            status="processing",
            user_id=repeated_transaction.user_id
        )
        new_transactions.append(new_transaction)
        repeated_transaction.next_transaction_date = today + datetime.timedelta(days=repeated_transaction.period)
        repeated_transactions_to_update.append(repeated_transaction)
    db.session.bulk_insert(new_transactions)
    db.session.bulk_update(repeated_transactions_to_update)
    db.session.commit()
def run_repeated_transaction_service():
    with current_app.app_context():
        while True:
            try:
                check_repeated_transactions()
            except Exception as e:
                current_app.logger.error("Repeated Transaction Service Error: %s", e)
            time.sleep(60 * 60 * 6)  # Sleep for 6 hours

