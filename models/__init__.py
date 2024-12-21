from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy database instance
db = SQLAlchemy()

# Import all models to ensure they are registered with SQLAlchemy
from .user import User
from .account import Account
from .category import Category
from .transaction import Transaction
from .Repeated_Transactions import Repeated_Transaction
from .notification import Notification
from .debt import Debt
from .debtPayments import DebtPayments
from .investment import Investment


def init_db(app):
    # Set the database URI. Change this for production (e.g., to MySQL)

    # Initialize the app with the database
    db.init_app(app)

    with app.app_context():
        # Create all database tables
        db.create_all()
        print('db created with all tables')

        if Category.query.get(1) is None:
            _category = Category(user_id=0, type='expense', name='Transfer from account')
            db.session.add(_category)
            db.session.commit()
        if Category.query.get(2) is None:
            _category = Category(user_id=0, type='income', name='Transfer to account')
            db.session.add(_category)
            db.session.commit()
