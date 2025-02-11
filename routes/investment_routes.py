import datetime

from flask import Blueprint, request, jsonify
from models import Investment, db
from flask_login import login_required, current_user
from marshmallow import Schema, fields, ValidationError
from services.investment_service import exchange_rates
from decimal import Decimal
from flask_babel import lazy_gettext as _

investment_bp = Blueprint('investment', __name__, url_prefix='/api/investment')


def validate_currency(value):
    allowed_currencies = ["USD", "EUR", "JOD"]
    if value not in allowed_currencies:
        raise ValidationError("Invalid currency")


def validate_reference_currency(value):
    allowed_currencies = ["ILS"]
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
        return jsonify({'error': _('Currency, account, amount invested and purchase price are required')}), 400
    account_id = data.get('account_id')
    if current_user.accounts.filter_by(id=account_id).first() is None:
        return jsonify({'error': _('Account not found')}), 401
    currency = data.get('currency')
    amount_invested = data.get('amount_invested')
    purchase_price = data.get('purchase_price')
    reference_currency = data.get('reference_currency')
    description = data.get('description')
    date = data.get('date') if data.get('date') else datetime.datetime.now()
    account = current_user.accounts.filter_by(id=account_id).first()
    if account is None:
        return jsonify({'error': _('Account not found or Access denied')}), 404

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
    account.balance -= Decimal(purchase_price)

    db.session.add(new_investment)
    db.session.commit()

    return jsonify({'message': _('Investment added successfully'), 'investment': new_investment.to_dict()}), 201


# Get all investments for the logged-in user with pagination
@investment_bp.get('/')
@login_required
def get_investments():
    # Retrieve pagination parameters with default values
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    investment_id = request.args.get('id', None, type=int)
    investment_query = current_user.investments
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
    investment = current_user.investments.filter_by(id=investment_id).first()
    if not investment:
        return jsonify({'error': _('Investment not found or access denied')}), 404
    data = request.get_json()
    try:
        schema = InvestmentSchema()
        data = schema.load(data)
    except ValidationError:
        return jsonify({'error': _('Currency, account, amount invested and purchase price are required')}), 400
    if data.get('account_id') is not investment.account_id:
        return jsonify({'error': _("Account can't be updated")}), 400
    investment.update(data)
    db.session.commit()
    return jsonify({'message': _('Investment updated successfully'), 'investment': investment.to_dict()}), 200


# Delete an investment
@investment_bp.delete('/<int:investment_id>')
@login_required
def delete_investment(investment_id):
    investment = current_user.investments.filter_by(id=investment_id).first()
    if not investment:
        return jsonify({'error': _('Investment not found or access denied')}), 404
    db.session.delete(investment)
    db.session.commit()
    return jsonify({'message': _('Investment deleted successfully')}), 200


@investment_bp.put('/sell/<int:investment_id>')
@login_required
def sell_investment(investment_id):
    investment = current_user.investments.filter_by(id=investment_id).first()
    if not investment:
        return jsonify({'error': _('Investment not found or access denied')}), 404
    data = request.get_json()
    sell_price = data.get('sell_price')
    if not sell_price:
        return jsonify({'error': _("bad request")}), 400
    investment.sold = True
    account = current_user.accounts.filter_by(id=investment.account_id).first()
    investment.sell_price = sell_price
    investment.profit_amount = (Decimal(investment.sell_price) * Decimal(investment.bought_amount))
    account.balance += investment.profit_amount
    db.session.commit()
    return jsonify({'message': _('Investment updated successfully'), 'investment': investment.to_dict()}), 200


@investment_bp.get('/exchange_rates')
@login_required
def get_exchange_rates():
    return jsonify({"exchange_rates": exchange_rates}), 200
