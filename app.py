from flask import Flask, session, render_template
from models import init_db, db
from routes import register_routes
from flask_login import LoginManager, login_required, current_user
from models.user import User
from services import register_check_repeated_transactions, register_investment_service
from flask_migrate import Migrate
from config import Config
from flask_babel import Babel, gettext

app = Flask(__name__)

app.config.from_object(Config)
init_db(app)
migrate = Migrate(app, db)
# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Language selector
def get_locale():
    lang = 'en'
    try:
        lang = current_user.language
    except AttributeError:
        pass
    return lang
app.jinja_env.globals['get_locale'] = get_locale

babel = Babel(app, locale_selector=get_locale)

# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    user = User.query.filter_by(id=int(user_id)).first()
    return user


@app.before_request
def make_session_permanent():
    """ Set the session to be permanent only for authenticated users. """
    if current_user.is_authenticated:
        session.permanent = True  # Make the session permanent
        session.modified = True  # Update the session to extend its lifetime


@app.get('/signup')
def signup_page():
    return render_template('signup.html')


@app.get('/login')
def login_page():
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/accounts')
@login_required
def accounts():
    return render_template('accounts.html')


@app.route('/transactions')
@login_required
def transactions():
    return render_template('transactions.html')


@app.route('/categories')
@login_required
def categories():
    return render_template('categories.html')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/debts')
@login_required
def debts():
    return render_template('debts.html')


@app.route('/investments')
@login_required
def investments():
    return render_template('investments.html')


# Register routes
register_routes(app)

register_check_repeated_transactions(app)
register_investment_service(app)
