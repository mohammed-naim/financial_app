from flask import Blueprint, request, jsonify
from models import DebtPayments, db, Account, Debt
from datetime import datetime
from flask_login import login_required, current_user
from decimal import Decimal
from marshmallow import Schema, fields, ValidationError
from flask_babel import lazy_gettext as _

# Create a blueprint for debts payments
debt_payments_bp = Blueprint('debt_payments', __name__, url_prefix='/api/debt-payments')


class DebtPaymentSchema(Schema):
    amount = fields.Float(required=True)
    description = fields.Str(required=False)
    date = fields.DateTime(required=False, format='%Y-%m-%d')
    account_id = fields.Integer(required=True)
    debt_id = fields.Integer(required=False)


# Unified GET endpoint for debts payments
@debt_payments_bp.get('/<int:debt_id>')
@login_required
def get_payments(debt_id):
    # Check for query parameters
    payment_id = request.args.get('id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    debt = current_user.debts.filter_by(id=debt_id).first()
    if debt is None:
        return jsonify({"error": _("debt not found")}), 404
    # If payment ID is provided, return payment by ID
    if payment_id:
        payment = debt.debtPayments.filter_by(id=payment_id).first()
        if payment is None:
            return jsonify({'error': _('Payment not found or access denied')}), 404
        return jsonify(payment.to_dict()), 200
    payments = debt.debtPayments
    if not payments:
        return jsonify({'error': _('Payment not found or access denied')}), 404
    # If date period is provided, filter payments by date range
    if start_date:
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            return jsonify({'error': _('Invalid date format. Use YYYY-MM-DD')}), 400

        payments = payments.filter(
            DebtPayments.date >= start_date,
        )
    if end_date:
        try:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return jsonify({'error': _('Invalid date format. Use YYYY-MM-DD')}), 400

        payments = payments.filter(
            DebtPayments.date <= end_date
        )

    # Apply pagination
    payments = payments.paginate(page=page, per_page=per_page, error_out=False)

    # Create the result response with pagination
    result = {
        'total': payments.total,
        'pages': payments.pages,
        'current_page': payments.page,
        'payments': [payment.to_dict() for payment in payments.items]
    }
    return jsonify(result), 200


@debt_payments_bp.post('/')
@login_required
def add_payment():
    data = request.get_json()
    try:
        schema = DebtPaymentSchema()
        data = schema.load(data)
    except ValidationError as e:
        return jsonify({'error': _('request body is empty or some data lost')}), 400
    # based on the debt type add or remove the amount from the account
    account = current_user.accounts.filter_by(id=data.get('account_id')).first()
    debt = current_user.debts.filter_by(id=data.get('debt_id')).first()
    if not account or not debt:
        return jsonify({'error': _('Account or Debt not found or access denied')}), 404

    if debt.paid >= debt.amount:
        return jsonify({'error': _('You have paid all the debts')}), 400
    if data['amount'] > debt.remaining:
        return jsonify({'error': _('You cannot pay more than the remaining amount')}), 400

    new_payment = DebtPayments(
        amount=data['amount'],
        description=data.get('description'),
        date=data.get('date') if data.get('date') else datetime.utcnow(),
        account_id=data['account_id'],
        debt_id=data['debt_id']
    )
    account.update_balance(new_payment.amount * -1, debt.type)
    paid_amount = float(debt.paid) + float(new_payment.amount)
    debt.update({'paid': paid_amount})
    db.session.add(new_payment)
    db.session.commit()
    return jsonify(new_payment.to_dict()), 201


# Delete a payment by ID
@debt_payments_bp.delete('/<int:debt_payment_id>')
@login_required
def delete_payment(debt_payment_id):
    payment = current_user.debts.join(DebtPayments).filter(DebtPayments.id == debt_payment_id).first()
    if not payment:
        return jsonify({'error': _('Payment not found or access denied')}), 404
    payment = DebtPayments.query.filter(DebtPayments.id == debt_payment_id).first()
    account = current_user.accounts.filter_by(id=payment.account_id).first()
    debt = current_user.debts.filter_by(id=payment.debt_id).first()
    account.update_balance(payment.amount, debt.type)
    paid_amount = debt.paid - Decimal(payment.amount)
    debt.update({'paid': paid_amount})
    db.session.delete(payment)
    db.session.commit()
    return jsonify({'message': _('Payment deleted successfully')}), 200


# Update a payment by ID
@debt_payments_bp.put('/<int:debt_payment_id>')
@login_required
def update_payment(debt_payment_id):
    data = request.get_json()
    try:
        schema = DebtPaymentSchema()
        data = schema.load(data)
    except ValidationError as e:
        return jsonify({'error': _('request body is empty or some data lost'),'errors':e.messages}), 400
    account = current_user.accounts.filter_by(id=data.get('account_id')).first()
    debt = current_user.debts.filter_by(id=data.get('debt_id')).first()
    if account is None:
        return jsonify({'error': _('account not found')}), 404
    if 'debt_id' in data:
        if debt is None:
            return jsonify({'error': _('debt not found')}), 404
    payment = current_user.debts.join(DebtPayments).filter(DebtPayments.id == debt_payment_id).first()
    if not payment:
        return jsonify({'error': _('payment not found or access denied')}), 404
    payment = DebtPayments.query.filter(DebtPayments.id == debt_payment_id).first()
    payment.update(data)
    db.session.commit()

    return jsonify(payment.to_dict()), 200
