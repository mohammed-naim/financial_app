# Account_Routes
from flask import Blueprint, request, jsonify, current_app
from models import Account, db, Transaction
from flask_login import login_required, current_user
from marshmallow import Schema, fields, ValidationError
from decimal import Decimal
from flask_babel import lazy_gettext as _

account_bp = Blueprint('account', __name__, url_prefix='/api/account')

  
def validate_currency(value):
    allowed_currencies = ["ILS"]
    if value not in allowed_currencies:
        raise ValidationError("Invalid currency")


class AccountSchema(Schema):
    name = fields.Str(required=True)
    balance = fields.Float(required=True)
    currency = fields.Str(required=False, validate=validate_currency)


# Create a new account
@account_bp.post('/')
@login_required
def add_account():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": _("No data provided")}), 400
        schema = AccountSchema()
        validated_data = schema.load(data)
        name = validated_data.get('name')
        balance = validated_data.get('balance', 0.0)
        currency = validated_data.get('currency', 'ILS')  # Default to ILS if no currency provided
        if not name:
            return jsonify({'error': _('Account name is required')}), 400
        if not currency:
            return jsonify({'error': _('Currency is required')}), 400
        new_account = Account(name=name, balance=balance, currency=currency, user_id=current_user.id)
        db.session.add(new_account)
        db.session.commit()
        return jsonify({'message': _('Account created successfully'), 'account': new_account.to_dict()}), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        current_app.logger.warning(f"Filed to save account data {e}.")
        return jsonify({"error": _("An unexpected error occurred")}), 500


@account_bp.get('/')
@login_required
def get_accounts():
    accounts = [account.to_dict() for account in current_user.accounts.all()]
    return jsonify({'accounts': accounts}), 200


@account_bp.get('/enabled')
@login_required
def get_enabled_accounts():
    accounts = current_user.accounts.filter_by(disabled=False).all()
    accounts = [account.to_dict() for account in accounts]
    return jsonify({'accounts': accounts}), 200


@account_bp.get('/disabled')
@login_required
def get_disabled_accounts():
    accounts = current_user.accounts.filter_by(disabled=True).all()
    accounts = [account.to_dict() for account in accounts]
    return jsonify({'accounts': accounts}), 200


# Get a single account by ID
@account_bp.get('/<int:account_id>')
@login_required
def get_account_by_id(account_id: int):
    account = current_user.accounts.filter_by(id=account_id).first()
    if not account:
        return jsonify({'error': _('Account not found or access denied')}), 404
    return jsonify({'account': account.to_dict()}), 200


# Update an existing account
@account_bp.put('/<int:account_id>')
@login_required
def update_account(account_id: int):
    account = current_user.accounts.filter_by(id=account_id, user_id=current_user.id).first()
    if not account:
        return jsonify({'error': _('Account not found or access denied')}), 404
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": _("No data provided")}), 400
        schema = AccountSchema()
        validated_data = schema.load(data)
        account.name = validated_data.get('name', account.name)
        account.balance = validated_data.get('balance', account.balance)
        account.currency = validated_data.get('currency', account.currency)
        db.session.commit()
        return jsonify({'message': _('Account updated successfully'), 'account': account.to_dict()}), 200
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except Exception as e:
        current_app.logger.warning(f"Filed to update account data {e}.")
        return jsonify({"error": _("An unexpected error occurred")}), 500


# Delete an account
@account_bp.put('/enable/<int:account_id>')
@login_required
def enable_account(account_id: int):
    account = current_user.accounts.filter_by(id=account_id, user_id=current_user.id).first()
    if not account:
        return jsonify({'error': _('Account not found or access denied')}), 404
    account.disabled = False
    db.session.commit()
    return jsonify({'message': _('Account Enabled Successfully')}), 200


# disable an account
@account_bp.put('/disable/<int:account_id>')
@login_required
def disable_account(account_id: int):
    account = current_user.accounts.filter_by(id=account_id, user_id=current_user.id).first()
    if not account:
        return jsonify({'error': _('Account not found or access denied')}), 404
    account.disabled = True

    db.session.commit()
    return jsonify({'message': _('Account Disabled Successfully')}), 200


@account_bp.delete('/<int:account_id>')
@login_required
def delete_account(account_id: int):
    account = current_user.accounts.filter_by(id=account_id).first()
    if not account:
        return jsonify({'error': _('Account not found or access denied')}), 404
    if account.transactions.first() or account.debts.first() or account.debts_payments.first() or account.investments.first():
        return jsonify({"error": _("There are operations associated with this account.")}), 400
    db.session.delete(account)
    db.session.commit()
    return jsonify({'message': _('Account Deleted Successfully')}), 200


# Transfer between accounts
@account_bp.post('/transfer')
@login_required
def transfer_between_accounts():
    data = request.get_json()
    from_account_id = data.get('from_account_id')
    to_account_id = data.get('to_account_id')
    amount = data.get('amount')
    if not from_account_id or not to_account_id or not amount:
        return jsonify({'error': _('Missing required fields')}), 400
    amount = float(amount)
    if amount <= 0:
        return jsonify({'error': _('Amount must be greater than zero')}), 400
    from_account = current_user.accounts.filter_by(id=from_account_id).first()
    to_account = current_user.accounts.filter_by(id=to_account_id).first()
    if not from_account:
        return jsonify({'error': _('Source account not found or access denied')}), 404
    if not to_account:
        return jsonify({'error': _('Destination account not found or access denied')}), 404
    if from_account.balance < amount:
        return jsonify({'error': _('Insufficient funds in source account')}), 400
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
    from_account.balance -= Decimal(amount)
    to_account.balance += Decimal(amount)
    db.session.commit()

    return jsonify({'message': _('Transfer completed successfully')}), 200
