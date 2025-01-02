# Auth_Routes
from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from models import User, Category, Account, db
from flask_login import login_required
from marshmallow import Schema, fields, ValidationError

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


class UserSchema(Schema):
    fullName = fields.Str(required=False)
    email = fields.Email(required=True)
    password = fields.Str(required=True)


@auth_bp.get('/signup')
def signup_redirect():
    return redirect(url_for('signup_page', next=request.args.get('next')))


@auth_bp.post('/signup')
def signup():
    data = {}
    try:
        data = request.get_json()
    except Exception as e:
        return jsonify({"error": "No data provided"}), 400
    finally:
        try:
            schema = UserSchema()
            validated_data = schema.load(data)
            full_name = validated_data.get('fullName')
            email = validated_data.get('email')
            password = validated_data.get('password')
        except ValidationError:
            return jsonify({'error': 'full name, email, and password are required'}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'User with this email already exists'}), 409

    new_user = User(full_name=full_name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    create_default_account_and_categories(new_user.id)
    session['_user_id'] = new_user.id

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
def login_redirect():
    return redirect(url_for('login_page', next=request.args.get('next')))


@auth_bp.post('/login')
def login():
    data = {}
    try:
        data = request.get_json()
    except:
        return jsonify({"error": "No data provided"}), 400
    finally:
        try:
            if not data:
                return redirect("/login")
            schema = UserSchema()
            validated_data = schema.load(data)
            email = validated_data.get('email')
            password = validated_data.get('password')
        except ValidationError:
            return jsonify({"errors": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        session['_user_id'] = user.id
        return jsonify({'message': 'Login successful'}), 200

    return jsonify({'error': 'Invalid email or password'}), 401


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('_user_id', None)
    return jsonify({'message': 'Logout successful'}), 200
