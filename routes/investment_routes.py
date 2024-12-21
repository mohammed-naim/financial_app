from flask import Blueprint, request, jsonify
from models import Investment, db, Account
from flask_login import login_required, current_user
from marshmallow import Schema, fields, ValidationError
from services.investment_service import exchange_rates

investment_bp = Blueprint('investment', __name__, url_prefix='/api/investment')


def validate_currency(value):
    allowed_currencies = ["ILS"]
    if value not in allowed_currencies:
        raise ValidationError("Invalid currency")


def validate_reference_currency(value):
    allowed_currencies = ["ILS", "USD", "EUR", "JOD"]
    if value not in allowed_currencies:
        raise ValidationError("Invalid currency")


class InvestmentSchema(Schema):
    account_id = fields.Integer(required=True)
    currency = fields.String(required=True, validate=validate_currency)
    amount_invested = fields.Float(required=True)
    purchase_price = fields.Float(required=True)
    reference_currency = fields.String(required=True, validate=validate_reference_currency)
    date = fields.DateTime(required=False, format='%Y-%m-%d')
    description = fields.String(required=True)


# Create a new investment
@investment_bp.post('/')
@login_required
def add_investment():
    data = request.get_json()
    try:
        schema = InvestmentSchema()
        data = schema.load(data)
    except ValidationError as e:
        return jsonify({'error': 'Currency, account, amount invested and purchase price are required'}), 400
    account_id = data.get('account_id', type=int)
    currency = data.get('currency')
    amount_invested = data.get('amount_invested')
    purchase_price = data.get('purchase_price', type=float)
    reference_currency = data.get('reference_currency', 'USD')
    description = data.get('description')
    date = data.get('date')

    if current_user.accounts.get(account_id):
        return jsonify({'error': 'Account not found or Access denied'}), 404

    new_investment = Investment(
        user_id=current_user.id,
        account_id=account_id,
        currency=currency,
        amount_invested=amount_invested,
        purchase_price=purchase_price,
        reference_currency=reference_currency,
        description=description,
        date=date
    )
    # update account balance
    account = current_user.accounts.get(account_id)
    account.balance -= purchase_price

    db.session.add(new_investment)
    db.session.commit()

    return jsonify({'message': 'Investment added successfully', 'investment': new_investment.to_dict()}), 201


# Get all investments for the logged-in user with pagination
@investment_bp.get('/')
@login_required
def get_investments():
    # Retrieve pagination parameters with default values
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    investment_id = request.args.get('id', None, type=int)
    investment_query = current_user.investments.query
    if investment_id:
        investment = investment_query.filter_by(id=investment_id).first()
        return jsonify(investment.to_dict())
    # Query investments for the user with pagination
    pagination = investment_query.filter_by(sold=False).paginate(page=page, per_page=per_page, error_out=False)
    investments = pagination.items
    investment_list = [investment.to_dict() for investment in investments]
    return jsonify({
        'investments': investment_list,
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
        'per_page': pagination.per_page
    }), 200


# Update an existing investment
@investment_bp.put('/<int:investment_id>')
@login_required
def update_investment(investment_id):
    investment = current_user.investments.query.filter_by(id=investment_id).first()
    if not investment:
        return jsonify({'error': 'Investment not found or access denied'}), 404
    data = request.get_json()
    try:
        schema = InvestmentSchema()
        data = schema.load(data)
    except ValidationError as e:
        return jsonify({'error': 'Currency, account, amount invested and purchase price are required'}), 400
    investment.update(data)
    db.session.commit()
    return jsonify({'message': 'Investment updated successfully', 'investment': investment.to_dict()}), 200


# Delete an investment
@investment_bp.delete('/<int:investment_id>')
@login_required
def delete_investment(investment_id):
    investment = Investment.query.filter_by(id=investment_id, user_id=current_user.id).first()
    if not investment:
        return jsonify({'error': 'Investment not found or access denied'}), 404
    db.session.delete(investment)
    db.session.commit()
    return jsonify({'message': 'Investment deleted successfully'}), 200


@investment_bp.put('/sell/<int:investment_id>')
@login_required
def sell_investment(investment_id):
    investment = current_user.investments.query.filter_by(id=investment_id).first()
    if not investment:
        return jsonify({'error': 'Investment not found or access denied'}), 404
    data = request.get_json()
    sell_price = data['sell_price']
    investment.sold = True
    account = current_user.accounts.query.filter_by(id=investment.account_id)
    account.balance += (sell_price * investment.amount_invested)
    db.session.commit()
    return jsonify({'message': 'Investment updated successfully', 'investment': investment.to_dict()}), 200


@investment_bp.get('/exchange_rates')
@login_required
def exchange_rates():
    return jsonify(exchange_rates), 200
