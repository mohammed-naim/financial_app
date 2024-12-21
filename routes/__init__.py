# __Init__
from flask import Blueprint

# Import individual route modules
from .auth_routes import auth_bp
from .account_routes import account_bp
from .category_routes import category_bp
from .transaction_routes import transaction_bp
from .dashboard_routes import dashboard_bp
from .debt_routes import debt_bp
from .investment_routes import investment_bp
from .debtPayments_routes import debt_payments_bp
from .dashboard_routes import dashboard_bp

# Create a Blueprint for the main app routes
main_bp = Blueprint('main', __name__)


# Function to register blueprints with the app
def register_routes(app):
    # Register each blueprint with the Flask app instance
    app.register_blueprint(auth_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(debt_bp)
    app.register_blueprint(investment_bp)
    app.register_blueprint(debt_payments_bp)
    # Additional main routes can be added here if needed.
    # Example: app.add_url_rule('/', 'index', some_view_function)
