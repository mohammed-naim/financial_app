from flask import Blueprint, request, jsonify
from models import Debt, Account, db
from flask_login import login_required, current_user
from datetime import datetime
import traceback
from marshmallow import Schema, fields, ValidationError

debt_bp = Blueprint('debt', __name__, url_prefix='/api/debts')


def validate_type(value):
    allowed_currencies = ["creditor", "debtor"]
    if value not in allowed_currencies:
        raise ValidationError("Invalid currency")


class DebtSchema(Schema):
    person_name = fields.Str(required=True)
    type = fields.Str(required=True, validate=validate_type)
    amount = fields.Float(required=True)
    description = fields.Str(required=False)
    account_id = fields.Int(required=True)


# Create a new debt
@debt_bp.post('/')
@login_required
def add_debt():
    data = request.get_json()
    try:
        schema = DebtSchema()
        data = schema.load(data)
    except ValidationError:
        return jsonify({'error': 'Type, person name, amount, and account are required'}), 400
    debt_type = data.get('type')  # "creditor" or "debtor"
    person_name = data.get('person_name')
    amount = data.get('amount')
    description = data.get('description', '')
    account_id = data.get('account_id')
    account = current_user.accounts.filter_by(id=account_id).first()
    if not account:
        return jsonify({'error': 'Account not found or access denied'}), 404

    new_debt = Debt(
        user_id=current_user.id,
        type=debt_type,
        person_name=person_name,
        amount=amount,
        account_id=account_id,
        description=description,
    )
    db.session.add(new_debt)
    account.update_balance(amount, new_debt.type)
    db.session.commit()

    return jsonify({'message': 'Debt added successfully', 'success': True, 'debt': new_debt.to_dict()}), 201


# Unified GET endpoint for debts
@debt_bp.get('/')
@login_required
def get_debts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    debt_type = request.args.get('type')  # "creditor" or "debtor"
    debt_id = request.args.get('id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    person_name = request.args.get('person_name')

    try:
        # If debt ID is provided, return the specific debt
        if debt_id:
            debt = current_user.debts.filter_by(id=debt_id, user_id=current_user.id).first()
            if not debt:
                return jsonify({'error': 'Debt not found or access denied'}), 404
            return jsonify(debt.to_dict()), 200

        # Base query for current user's debts
        query = current_user.debts.filter_by(user_id=current_user.id)

        # If a date range is provided, filter debts by the date range
        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

            query = query.filter(Debt.date >= start_date, Debt.date <= end_date)

        # If a debt type is provided, filter debts by type
        if debt_type:
            query = query.filter_by(type=debt_type)

        # If a person's name is provided, filter debts by the name
        if person_name:
            query = query.filter(Debt.person_name.ilike(f"%{person_name}%"))

        # Paginate the filtered query
        debts = query.paginate(page=page, per_page=per_page, error_out=False)

        # Convert debts to dictionary format for JSON response
        debt_list = [debt.to_dict() for debt in debts.items]

        # Include pagination metadata in the response
        response = {
            'debts': debt_list,
            'page': debts.page,
            'per_page': debts.per_page,
            'total': debts.total,
            'pages': debts.pages
        }
        return jsonify(response), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# Update an existing debt
@debt_bp.put('/<int:debt_id>')
@login_required
def update_debt(debt_id):
    debt = current_user.debts.filter_by(id=debt_id).first()
    if not debt:
        return jsonify({'error': 'Debt not found or access denied'}), 404
    data = request.get_json()
    try:
        schema = DebtSchema()
        data = schema.load(data)
    except ValidationError:
        return jsonify({'error': 'Type, person name, amount, and account are required'}), 400

    account_id = data.get('account_id', debt.account_id)
    account = current_user.accounts.filter_by(id=account_id).first()
    if not account:
        return jsonify({'error': 'Account not found or access denied'}), 404
    previous_amount = debt.amount
    previous_type = debt.type
    debt.update(data)
    # Update account balance if type or amount changes
    if data.get('type') and debt.type != previous_type:
        # Adjust balance based on type change
        amount = float(debt.amount) + float(previous_amount)
    else:
        # Adjust balance based on amount change
        amount = float(debt.amount) - float(previous_amount)
    account.update_balance(amount, debt.type)
    db.session.commit()
    return jsonify({'message': 'Debt updated successfully', 'debt': debt.to_dict()}), 200


# Delete a debt
@debt_bp.delete('/<int:debt_id>')
@login_required
def delete_debt(debt_id):
    debt = current_user.debts.filter_by(id=debt_id).first()
    if not debt:
        return jsonify({'error': 'Debt not found or access denied'}), 404
    if debt.debtPayments.all():
        return jsonify({"error": "There are payments associated with this debt."}), 400
    account = Account.query.get(debt.account_id)
    amount = debt.amount * -1
    account.update_balance(amount, debt.type)
    db.session.delete(debt)
    db.session.commit()

    return jsonify({'message': 'Debt deleted successfully'}), 200
