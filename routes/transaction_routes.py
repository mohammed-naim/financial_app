from flask import Blueprint, request, jsonify
from models import db, Transaction, Category, Account
from flask_login import login_required, current_user
from datetime import datetime, timedelta

transaction_bp = Blueprint('transaction', __name__, url_prefix='/api/transaction')


# Create a new transaction
@transaction_bp.post('/')
@login_required
def add_transaction():
    data = request.get_json()
    amount = data.get('amount')
    category_id = data.get('category_id')
    account_id = data.get('account_id')
    description = data.get('description', '')
    transaction_date = data.get('transaction_date')
    if not amount or not category_id or not account_id:
        return jsonify({'error': 'Amount, category, and account are required'}), 400
    account = current_user.accounts.filter_by(id=account_id).first()
    category = current_user.categories.filter_by(id=category_id).first()
    if not account or not category:
        return jsonify({'error': 'Account or Category not found or access denied'}), 404
    new_transaction = Transaction(
        amount=amount,
        category_id=category_id,
        account_id=account_id,
        description=description,
        user_id=current_user.id,
        date=transaction_date,
    )
    db.session.add(new_transaction)
    account.update_balance(amount, category.type)
    db.session.commit()
    return jsonify({'message': 'Transaction created successfully', 'transaction': new_transaction.to_dict()}), 201


# Get filtered transactions with pagination
@transaction_bp.get('/')
@login_required
def get_transactions():
    # Get filter parameters from query parameters
    category_id = request.args.get('category_id', type=int)
    category_type = request.args.get('category_type', type=str)
    account_id = request.args.get('account_id', type=int)
    start_date = request.args.get('start_date', type=str)
    end_date = request.args.get('end_date', type=str)
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    # Base query for authenticated user
    query = current_user.transactions
    # Apply filters if provided
    if category_id:
        query = query.filter_by(category_id=category_id)
    elif category_type:
        query = query.join(Category).filter(Category.type == category_type)
    if account_id:
        query = query.filter_by(account_id=account_id)
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            start_date = start_date - timedelta(days=1)
            query = query.filter(Transaction.date >= start_date)
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(Transaction.date <= end_date)
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400
    # Order by newest to oldest
    query = query.order_by(Transaction.date.desc())
    # Paginate the results
    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    transactions = pagination.items
    # Convert transactions to dictionary format
    transaction_list = [transaction.to_dict() for transaction in transactions]
    return jsonify({
        'transactions': transaction_list,
        'totalPages': pagination.pages,
        'currentPage': page,
        'totalItems': pagination.total
    }), 200


# Update an existing transaction
@transaction_bp.put('/<int:transaction_id>')
@login_required
def update_transaction(transaction_id):
    transaction = current_user.transactions.filter_by(id=transaction_id).first()
    if not transaction:
        return jsonify({'error': 'Transaction not found or access denied'}), 404
    if transaction.category.user_id != current_user.id:
        return jsonify({'error': "Transaction Can't be edited because it's a transfer between accounts"})

    data = request.get_json()
    account_id = data.get('account_id', transaction.account_id)
    category_id = data.get('category_id', transaction.category_id)
    account = Account.query.filter_by(id=account_id, user_id=current_user.id).first()
    category = Category.query.filter_by(id=category_id, user_id=current_user.id).first()
    if not account or not category:
        return jsonify({'error': 'Account or Category not found or access denied'}), 404
    transaction.update(data)
    db.session.commit()
    return jsonify({'message': 'Transaction updated successfully', 'transaction': transaction.to_dict()}), 200


# Update the account for all transactions with the same account after filtering
# @transaction_bp.put('/update_account/<int:old_account_id>')
# @login_required
# def update_account_for_transactions(old_account_id):
#     data = request.get_json()
#     new_account_id = data.get('new_account_id')
#     if not new_account_id:
#         return jsonify({'error': 'New account ID is required'}), 400
#     new_account = Account.query.filter_by(id=new_account_id, user_id=current_user.id).first()
#     old_account = Account.query.filter_by(id=old_account_id, user_id=current_user.id).first()
#
#     if not new_account or not old_account:
#         return jsonify({'error': 'New account or old account not found or access denied'}), 404
#     # Update all transactions with the old account ID
#     current_user.transactions.filter_by(account_id=old_account_id).update({'account_id': new_account_id})
#     db.session.commit()
#     return jsonify({'message': 'Account updated for all filtered transactions successfully'}), 200
#

# Delete a transaction
@transaction_bp.delete('/<int:transaction_id>')
@login_required
def delete_transaction(transaction_id):
    transaction = current_user.transactions.filter_by(id=transaction_id).first()
    if not transaction:
        return jsonify({'error': 'Transaction not found or access denied'}), 404
    account = Account.query.get(transaction.account_id)
    category = Category.query.get(transaction.category_id)
    if category.user_id != current_user.id:
        return jsonify({'error': "Transaction Can't be deleted because because it's a transfer between accounts"})
    account.update_balance(-1*transaction.amount, category.type)
    db.session.delete(transaction)
    db.session.commit()
    return jsonify({'message': 'Transaction deleted successfully'}), 200


# Process an 'in processing' transaction
@transaction_bp.put('/process/<int:transaction_id>')
@login_required
def process_transaction(transaction_id):
    transaction = current_user.transactions.filter_by(id=transaction_id).first()
    if not transaction:
        return jsonify({'error': 'Transaction not found or access denied'}), 404
    if transaction.status != 'in processing':
        return jsonify({'error': 'Transaction is not in processing status'}), 400

    # Update the account balance
    account = Account.query.get(transaction.account_id)
    category = Category.query.get(transaction.category_id)
    account.update_balance(transaction.amount, category.type)
    db.session.commit()

    # Update the transaction status
    transaction.status = 'done'
    db.session.commit()

    return jsonify({'message': 'Transaction processed successfully'}), 200
