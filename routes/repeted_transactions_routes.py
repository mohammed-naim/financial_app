from flask import Blueprint, request, jsonify
from models import Repeated_Transaction, db, Notification, Transaction,Account,Category
from flask_login import login_required, current_user
from datetime import datetime, date
import datetime

repeated_transactions_bp = Blueprint('repeated_transactions', __name__, url_prefix='/api/repeated_transactions')


# Create a new repeated transaction
@repeated_transactions_bp.post('/')
@login_required
def add_repeated_transaction():
    data = request.get_json()
    account_id = data.get('account_id')
    category_id = data.get('category_id')
    amount = data.get('amount')
    period = data.get('period')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    description = data.get('description')

    if not account_id or not category_id or not amount or not period or not start_date or not description:
        return jsonify({'error': 'Missing required fields'}), 400
    account = current_user.accounts.filter_by(id=account_id).first()
    category = current_user.categories.filter_by(id=account_id).first()
    if not account or not category:
        return jsonify({'error': 'Account or Category not found or access denied'}), 404
    new_repeated_transaction = Repeated_Transaction(
        user_id=current_user.id,
        account_id=account_id,
        category_id=category_id,
        amount=amount,
        period=period,
        start_date=start_date,
        end_date=end_date,
        description=description
    )
    db.session.add(new_repeated_transaction)

    # Check if start date is today and create a transaction if true
    if new_repeated_transaction.start_date == date.today():
        create_transaction(new_repeated_transaction)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()

        return jsonify({'error': 'Something went wrong while adding repeated transaction'}), 500
    return jsonify({'message': 'Repeated transaction created successfully'}), 201


# Get all repeated transactions
@repeated_transactions_bp.get('/')
@login_required
def get_repeated_transactions():
    repeated_transactions = [rt.to_dict() for rt in current_user.Repeated_Transactions.all()]
    return jsonify({'repeated_transactions': repeated_transactions}), 200


# Get a single repeated transaction by ID
@repeated_transactions_bp.get('/<int:repeated_transaction_id>')
@login_required
def get_repeated_transaction_by_id(repeated_transaction_id):
    repeated_transaction = current_user.Repeated_Transactions.filter_by(id=repeated_transaction_id).first()
    if not repeated_transaction:
        return jsonify({'error': 'Repeated transaction not found or access denied'}), 404
    return jsonify({'repeated_transaction': repeated_transaction.to_dict()}), 200


# Update an existing repeated transaction
@repeated_transactions_bp.put('/<int:repeated_transaction_id>')
@login_required
def update_repeated_transaction(repeated_transaction_id):
    repeated_transaction = current_user.Repeated_Transactions.filter_by(id=repeated_transaction_id).first()
    if not repeated_transaction:
        return jsonify({'error': 'Repeated transaction not found or access denied'}), 404
    data = request.get_json()
    repeated_transaction.account_id = data.get('account_id', repeated_transaction.account_id)
    repeated_transaction.category_id = data.get('category_id', repeated_transaction.category_id)
    repeated_transaction.amount = data.get('amount', repeated_transaction.amount)
    repeated_transaction.period = data.get('period', repeated_transaction.period)
    repeated_transaction.start_date = data.get('start_date', repeated_transaction.start_date)
    repeated_transaction.end_date = data.get('end_date', repeated_transaction.end_date)
    repeated_transaction.description = data.get('description', repeated_transaction.description)
    db.session.commit()
    return jsonify({'message': 'Repeated transaction updated successfully'}), 200


# Delete a repeated transaction
@repeated_transactions_bp.delete('/<int:repeated_transaction_id>')
@login_required
def delete_repeated_transaction(repeated_transaction_id):
    repeated_transaction =current_user.Repeated_Transactions.filter_by(id=repeated_transaction_id).first()
    if not repeated_transaction:
        return jsonify({'error': 'Repeated transaction not found or access denied'}), 404
    db.session.delete(repeated_transaction)
    db.session.commit()
    return jsonify({'message': 'Repeated transaction deleted successfully'}), 200


def create_transaction(repeated_transaction):
    # Create a new transaction with 'processing' status
    new_transaction = Transaction(
        user_id=current_user.id,
        account_id=repeated_transaction.account_id,
        category_id=repeated_transaction.category_id,
        amount=repeated_transaction.amount,
        status='processing',
        description=repeated_transaction.description
    )
    db.session.add(new_transaction)

    # Update the next transaction date
    repeated_transaction.next_transaction_date = repeated_transaction.start_date + datetime.timedelta(
        days=int(repeated_transaction.period))

    # Add a notification to the user
    new_notification = Notification(
        user_id=current_user.id,
        message=f'Transaction of {repeated_transaction.amount} is pending for {repeated_transaction.description}',
        is_seen=False
    )
    db.session.add(new_notification)
