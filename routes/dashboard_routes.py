from flask import Blueprint, request, jsonify
from models import Transaction
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from flask_babel import lazy_gettext as _
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


@dashboard_bp.get('/overview')
@login_required
def get_overview():
    start_date = request.args.get('start_date', '1970-01-01')
    end_date = request.args.get('end_date', '9999-12-31')

    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': _('Invalid date format. Use YYYY-MM-DD')}), 400

    # Fetch total income and expenses
    transactions = current_user.transactions.filter(Transaction.date >= start_date, Transaction.date <= end_date).all()
    user_categories = current_user.categories.all()
    income = sum(
        float(tx.amount) for tx in transactions if tx.category.type == 'income' and tx.category in user_categories)
    expenses = sum(
        float(tx.amount) for tx in transactions if tx.category.type == 'expense' and tx.category in user_categories)

    # Fetch account balances
    accounts = current_user.accounts.all()
    enabled_accounts_balance = sum(float(acct.balance) for acct in accounts if not acct.disabled)
    disabled_accounts_balance = sum(float(acct.balance) for acct in accounts if acct.disabled)

    # Fetch total debts
    debts = current_user.debts.all()
    total_creditor = sum(float(debt.remaining) for debt in debts if debt.type == 'creditor')
    total_debtor = sum(float(debt.remaining) for debt in debts if debt.type == 'debtor')

    # Fetch investments summary
    investments = current_user.investments.all()
    total_invested = sum(float(inv.amount_invested) for inv in investments)
    total_profit = sum(float(inv.profit_amount) for inv in investments)

    return jsonify({
        'income': income,
        'expenses': expenses,
        'enabled_accounts_balance': enabled_accounts_balance,
        'disabled_accounts_balance': disabled_accounts_balance,
        'total_creditor_debts': total_creditor,
        'total_debtor_debts': total_debtor,
        'total_invested': total_invested,
        'total_profit': total_profit
    }), 200


@dashboard_bp.get('/cash-flow')
@login_required
def get_cash_flow():
    period = request.args.get('period', 'month')  # Options: day, week, month, year
    compare = request.args.get('compare', 'true').lower() == 'true'

    now = datetime.utcnow()
    period_delta = {
        'day': timedelta(days=1),
        'week': timedelta(weeks=1),
        'month': timedelta(days=30),
        'year': timedelta(days=365)
    }.get(period, timedelta(days=30))

    current_period_start = now - period_delta
    previous_period_start = current_period_start - period_delta

    current_transactions = current_user.transactions.filter(Transaction.date >= current_period_start).all()
    previous_transactions = current_user.transactions.filter(Transaction.date >= previous_period_start,
                                                             Transaction.date < current_period_start).all()

    user_categories = current_user.categories.all()

    current_income = sum(float(tx.amount) for tx in current_transactions if
                         tx.category.type == 'income' and tx.category in user_categories)
    current_expenses = sum(float(tx.amount) for tx in current_transactions if
                           tx.category.type == 'expense' and tx.category in user_categories)
    previous_income = sum(float(tx.amount) for tx in previous_transactions if
                          tx.category.type == 'income' and tx.category in user_categories)
    previous_expenses = sum(float(tx.amount) for tx in previous_transactions if
                            tx.category.type == 'expense' and tx.category in user_categories)

    return jsonify({
        'current_period': {
            'income': current_income,
            'expenses': current_expenses
        },
        'previous_period': {
            'income': previous_income,
            'expenses': previous_expenses
        } if compare else None
    }), 200


@dashboard_bp.get('/cash-flow/detailed')
@login_required
def get_detailed_cash_flow():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    interval = request.args.get('interval', 'day')  # Options: day, week, month

    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except (ValueError, TypeError):
        return jsonify({'error': _('Invalid or missing date format. Use YYYY-MM-DD')}), 400

    if interval not in ['day', 'week', 'month']:
        return jsonify({'error': _('Invalid interval. Choose from day, week, or month')}), 400

    delta = {
        'day': timedelta(days=1),
        'week': timedelta(weeks=1),
        'month': timedelta(days=30)
    }[interval]

    current_date = start_date
    detailed_cash_flow = []

    while current_date < end_date:
        next_date = current_date + delta
        transactions = current_user.transactions.filter(
            Transaction.date >= current_date,
            Transaction.date < next_date
        ).all()
        user_categories = current_user.categories.all()

        income = sum(
            float(tx.amount) for tx in transactions if tx.category.type == 'income' and tx.category in user_categories)
        expenses = sum(
            float(tx.amount) for tx in transactions if tx.category.type == 'expense' and tx.category in user_categories)

        detailed_cash_flow.append({
            'start_date': current_date.strftime('%Y-%m-%d'),
            'end_date': (next_date - timedelta(days=1)).strftime('%Y-%m-%d'),
            'income': income,
            'expenses': expenses
        })

        current_date = next_date

    return jsonify(detailed_cash_flow), 200


@dashboard_bp.get('/category-summary')
@login_required
def get_category_summary():
    start_date = request.args.get('start_date', '1970-01-01')
    end_date = request.args.get('end_date', '9999-12-31')

    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': _('Invalid date format. Use YYYY-MM-DD')}), 400
    user_categories = current_user.categories.all()
    transactions = current_user.transactions.filter(Transaction.date >= start_date, Transaction.date <= end_date).all()
    categories = {}
    for tx in transactions:
        category_name = tx.category.name
        if tx.category not in user_categories:
            continue
        if category_name not in categories:
            categories[category_name] = 0
        categories[category_name] += float(tx.amount)

    return jsonify(categories), 200
