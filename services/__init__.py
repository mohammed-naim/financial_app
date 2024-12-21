# __Init__
import traceback

from flask import Flask
from .investment_service import run_investment_service
from .check_repeated_transaction import run_schedule
# from .check_repeated_transaction import run_repeated_transaction_service
import threading


def register_investment_service(app: Flask):
    """
    Register the investment service with the Flask app.
    This allows the service to run its initialization when the app starts.
    """
    # Create and start the thread
    thread = threading.Thread(target=run_investment_service, args=[app, ])
    thread.daemon = True  # Allow the thread to exit when the main program exits
    thread.start()


def register_check_repeated_transactions(app: Flask):
    thread = threading.Thread(target=run_schedule, args=[app, ])
    thread.daemon = True
    thread.start()
