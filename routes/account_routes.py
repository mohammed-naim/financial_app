# Account_Routes
from flask import Blueprint, request, jsonify
from models import Account, db, Transaction
from flask_login import login_required, current_user

account_bp = Blueprint('account', __name__, url_prefix='/api/account')


# Create a new account
@account_bp.post('/')
@login_required
def add_account():
    data = request.get_json()
    name = data.get('name')
    balance = data.get('balance', 0.0)
    currency = data.get('currency', 'ILS')  # Default to ILS if no currency provided
    if not name:
        return jsonify({'error': 'Account name is required'}), 400
    if not currency:
        return jsonify({'error': 'Currency is required'}), 400
    new_account = Account(name=name, balance=balance, currency=currency, user_id=current_user.id)
    db.session.add(new_account)
    db.session.commit()
    return jsonify({'message': 'Account created successfully', 'account': new_account.to_dict()}), 201


@account_bp.get('/')
@login_required
def get_accounts():
    accounts = [account.to_dict() for account in current_user.accounts.all()]
    return jsonify({'accounts': accounts}), 200

@account_bp.get('/enabled')
@login_required
def get_enabled_accounts():
    accounts = current_user.accounts.filter_by(disabled=False).all()
    if not accounts:
        return jsonify({'error': 'Accounts not found or access denied'}), 404
    accounts = [account.to_dict() for account in accounts]
    return jsonify({'accounts': accounts}), 200


# Get a single account by ID
@account_bp.get('/<int:account_id>')
@login_required
def get_account_by_id(account_id):
    account = current_user.accounts.filter_by(id=account_id).first()
    if not account:
        return jsonify({'error': 'Account not found or access denied'}), 404
    return jsonify({'account': account.to_dict()}), 200


# Update an existing account
@account_bp.put('/<int:account_id>')
@login_required
def update_account(account_id):
    account = current_user.accounts.filter_by(id=account_id,user_id=current_user.id).first()
    if not account:
        return jsonify({'error': 'Account not found or access denied'}), 404
    data = request.get_json()
    account.name = data.get('name', account.name)
    account.balance = data.get('balance', account.balance)
    account.currency = data.get('currency', account.currency)  # Update currency if provided
    db.session.commit()
    return jsonify({'message': 'Account updated successfully', 'account': account.to_dict()}), 200

# Delete an account
@account_bp.put('/enable/<int:account_id>')
@login_required
def enable_account(account_id):
    account = current_user.accounts.filter_by(id=account_id,user_id=current_user.id).first()
    if not account:
        return jsonify({'error': 'Account not found or access denied'}), 404
    account.disabled = False
    db.session.commit()
    return jsonify({'message': 'Account Enabled Successfully'}), 200

# disable an account
@account_bp.put('/disable/<int:account_id>')
@login_required
def disable_account(account_id):
    account = current_user.accounts.filter_by(id=account_id,user_id=current_user.id).first()
    if not account:
        return jsonify({'error': 'Account not found or access denied'}), 404
    account.disabled = True

    db.session.commit()
    return jsonify({'message': 'Account Disabled Successfully'}), 200


# Transfer between accounts
@account_bp.post('/transfer')
@login_required
def transfer_between_accounts():
    data = request.get_json()
    from_account_id = data.get('from_account_id')
    to_account_id = data.get('to_account_id')
    amount = data.get('amount')
    if not from_account_id or not to_account_id or not amount:
        return jsonify({'error': 'Missing required fields'}), 400
    amount = int(amount)
    if amount <= 0:
        return jsonify({'error': 'Amount must be greater than zero'}), 400
    from_account = current_user.accounts.get(from_account_id)
    to_account = current_user.accounts.get(to_account_id)
    if not from_account:
        return jsonify({'error': 'Source account not found or access denied'}), 404
    if not to_account:
        return jsonify({'error': 'Destination account not found or access denied'}), 404
    if from_account.balance < amount:
        return jsonify({'error': 'Insufficient funds in source account'}), 400
    new_transaction = Transaction(
        amount=amount,
        category_id=1,
        account_id=from_account.id,
        description=f"transfer from {from_account.name} to {to_account.name}",
        user_id=current_user.id,
    )
    db.session.add(new_transaction)
    new_transaction = Transaction(
        amount=amount,
        category_id=2,
        account_id=to_account.id,
        description=f"transfer from {from_account.name} to {to_account.name}",
        user_id=current_user.id,
    )
    db.session.add(new_transaction)
    # Transfer the amount+
    from_account.balance -= amount
    to_account.balance += amount
    db.session.commit()

    return jsonify({'message': 'Transfer completed successfully'}), 200
