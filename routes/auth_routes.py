# Auth_Routes
from flask import Blueprint, request, jsonify, session, render_template, redirect
from models import User, Category, Account, db
from flask_login import login_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.get('/signup')
def signup_page():
    return render_template('signup.html')


@auth_bp.post('/signup')
def signup():
    from_form = False
    try:
        data = request.get_json()
        full_name = data.get('fullName')
        email = data.get('email')
        password = data.get('password')
    except Exception as e:
        from_form = True
        full_name = request.form['fullName']
        email = request.form['email']
        password = request.form['password']

    if not full_name or not email or not password:
        return jsonify({'error': 'full name, email, and password are required'}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'User with this email already exists'}), 409

    new_user = User(full_name=full_name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    create_default_account_and_categories(new_user.id)
    session['_user_id'] = new_user.id
    if from_form:
        return redirect('/dashboard')
    return jsonify({'message': 'User registered successfully'}), 201


def create_default_account_and_categories(user_id):
    default_account = Account(
        name='Cash',
        balance=0.0,
        user_id=user_id
    )
    db.session.add(default_account)

    default_categories = [
        Category(name='Salary', type='income', user_id=user_id),
        Category(name='Food & Dining', type='expense', user_id=user_id),
        Category(name='Transportation', type='expense', user_id=user_id),
        Category(name='Utilities', type='expense', user_id=user_id),
        Category(name='Entertainment', type='expense', user_id=user_id)
    ]

    db.session.add_all(default_categories)
    db.session.commit()


@auth_bp.get('/login')
def login_page():
    return render_template('login.html')


@auth_bp.post('/login')
def login():
    from_form = False
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
    except:
        from_form = True
        email = request.form['email']
        password = request.form['password']
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        session['_user_id'] = user.id
        if from_form:
            return redirect('/dashboard')
        return jsonify({'message': 'Login successful'}), 200

    return jsonify({'error': 'Invalid email or password'}), 401


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('_user_id', None)
    return jsonify({'message': 'Logout successful'}), 200
