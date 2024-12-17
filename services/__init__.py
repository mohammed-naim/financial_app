from .check_repeated_transaction import run_repeated_transaction_service
import threading


def register_check_repeated_transactions():
    thread = threading.Thread(target=run_repeated_transaction_service)
    thread.daemon = True
    thread.start()
