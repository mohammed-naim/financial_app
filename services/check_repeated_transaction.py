from flask import Flask
import schedule
import datetime
from models import Repeated_Transaction, Transaction, db, Notification
import time


def check_repeated_transactions():
    print("Checking repeated transactions...")
    today = datetime.date.today()
    repeated_transactions = Repeated_Transaction.query.filter(
        Repeated_Transaction.start_date <= today,
        (Repeated_Transaction.end_date.is_(None)) | (Repeated_Transaction.end_date >= today),
        Repeated_Transaction.next_transaction_date <= today
    ).all()
    new_transactions = []
    repeated_transactions_to_update = []
    new_notifications = []
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
        new_notification = Notification(user_id=repeated_transaction.user_id,
                                        message=f'Transaction of {repeated_transaction.amount} is pending for {repeated_transaction.description}',
                                        is_seen=False)
        new_transactions.append(new_transaction)
        new_notifications.append(new_notification)
        repeated_transaction.next_transaction_date = today + datetime.timedelta(days=repeated_transaction.period)
        repeated_transactions_to_update.append(repeated_transaction)

    db.session.add_all(new_transactions)
    db.session.add_all(new_notifications)
    db.session.commit()
    print("Repeated Transactions updated")


def run_schedule(app: Flask):
    with app.app_context():
        schedule.every(1).hours.do(check_repeated_transactions)
        check_repeated_transactions()
        while True:
            schedule.run_pending()
            time.sleep(60 * 60)
