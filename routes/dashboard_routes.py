# dashboard_routes.py
from flask import Blueprint, render_template, request, jsonify
from models import User, Account, Debt, Investment, db
from flask_login import login_required, current_user

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


@dashboard_bp.route('/')
@login_required
def dashboard():
    user_id = current_user.id
    accounts = Account.query.filter_by(user_id=user_id).all()
    debts = Debt.query.filter_by(user_id=user_id).all()
    investments = Investment.query.filter_by(user_id=user_id).all()

    # Calculate net worth
    total_assets = sum(account.balance for account in accounts) + sum(investment.value for investment in investments)
    total_liabilities = sum(debt.amount for debt in debts)
    net_worth = total_assets - total_liabilities

    # Income vs Expenses
    income = sum(account.balance for account in accounts if account.type == 'income')
    expenses = sum(account.balance for account in accounts if account.type == 'expense')

    # Cash flow forecast
    cash_flow = income - expenses

    return render_template('dashboard.html', net_worth=net_worth, income=income, expenses=expenses, cash_flow=cash_flow)


@dashboard_bp.route('/account_balances')
@login_required
def account_balances():
    user_id = current_user.id
    accounts = Account.query.filter_by(user_id=user_id).all()
    return render_template('account_balances.html', accounts=accounts)


@dashboard_bp.route('/spending_insights')
@login_required
def spending_insights():
    user_id = current_user.id
    accounts = Account.query.filter_by(user_id=user_id).all()
    # Calculate spending by category
    spending_by_category = {}
    for account in accounts:
        if account.type == 'expense':
            category = account.category
            if category in spending_by_category:
                spending_by_category[category] += account.balance
            else:
                spending_by_category[category] = account.balance
    return render_template('spending_insights.html', spending_by_category=spending_by_category)


@dashboard_bp.route('/debt_liability')
@login_required
def debt_liability():
    user_id = current_user.id
    debts = Debt.query.filter_by(user_id=user_id).all()
    return render_template('debt_liability.html', debts=debts)


@dashboard_bp.route('/investment_tracking')
@login_required
def investment_tracking():
    user_id = current_user.id
    investments = Investment.query.filter_by(user_id=user_id).all()
    return render_template('investment_tracking.html', investments=investments)


@dashboard_bp.route('/financial_goal_tracking')
@login_required
def financial_goal_tracking():
    user_id = current_user.id
    # Calculate progress towards financial goals
    financial_goals = {}
    goals = current_user.goals.all()
    for goal in goals:
        financial_goals[goal.name] = goal.progress
    return render_template('financial_goal_tracking.html', financial_goals=financial_goals)


@dashboard_bp.route('/upcoming_transactions')
@login_required
def upcoming_transactions():
    user_id = current_user.id
    accounts = Account.query.filter_by(user_id=user_id).all()
    # Get upcoming transactions
    upcoming_transactions = []
    for account in accounts:
        transactions = account.transactions.filter_by(status='upcoming').all()
        for transaction in transactions:
            upcoming_transactions.append(transaction)
    return render_template('upcoming_transactions.html', upcoming_transactions=upcoming_transactions)


@dashboard_bp.route('/currency_conversion')
@login_required
def currency_conversion():
    user_id = current_user.id
    accounts = Account.query.filter_by(user_id=user_id).all()
    # Get currency conversion rates
    currency_conversion_rates = {}
    for account in accounts:
        if account.currency not in currency_conversion_rates:
            currency_conversion_rates[account.currency] = account.balance
    return render_template('currency_conversion.html', currency_conversion_rates=currency_conversion_rates)


@dashboard_bp.route('/personalized_recommendations')
@login_required
def personalized_recommendations():
    user_id = current_user.id
    # Get personalized recommendations
    personalized_recommendations = {}
    recommendations = current_user.recommendations.all()
    for recommendation in recommendations:
        personalized_recommendations[recommendation.name] = recommendation.description
    return render_template('personalized_recommendations.html',
                           personalized_recommendations=personalized_recommendations)


@dashboard_bp.route('/insights_predictions')
@login_required
def insights_predictions():
    user_id = current_user.id
    # Get insights and predictions
    insights_predictions = {}
    insights = current_user.insights.all()
    for insight in insights:
        insights_predictions[insight.name] = insight.description
    return render_template('insights_predictions.html', insights_predictions=insights_predictions)


@dashboard_bp.route('/net_worth')
@login_required
def net_worth():
    user_id = current_user.id
    accounts = Account.query.filter_by(user_id=user_id).all()
    debts = Debt.query.filter_by(user_id=user_id).all()
    investments = Investment.query.filter_by(user_id=user_id).all()

    # Calculate net worth
    total_assets = sum(account.balance for account in accounts) + sum(investment.value for investment in investments)
    total_liabilities = sum(debt.amount for debt in debts)
    net_worth = total_assets - total_liabilities

    return render_template('net_worth.html', net_worth=net_worth)


@dashboard_bp.route('/income_vs_expenses')
@login_required
def income_vs_expenses():
    user_id = current_user.id
    accounts = Account.query.filter_by(user_id=user_id).all()

    # Income vs Expenses
    income = sum(account.balance for account in accounts if account.type == 'income')
    expenses = sum(account.balance for account in accounts if account.type == 'expense')

    return render_template('income_vs_expenses.html', income=income, expenses=expenses)


@dashboard_bp.route('/cash_flow_forecast')
@login_required
def cash_flow_forecast():
    user_id = current_user.id
    accounts = Account.query.filter_by(user_id=user_id).all()

    # Cash flow forecast
    income = sum(account.balance for account in accounts if account.type == 'income')
    expenses = sum(account.balance for account in accounts if account.type == 'expense')
    cash_flow = income - expenses

    return render_template('cash_flow_forecast.html', cash_flow=cash_flow)


@dashboard_bp.route('/spending_by_category')
@login_required
def spending_by_category():
    user_id = current_user.id
    accounts = Account.query.filter_by(user_id=user_id).all()

    # Calculate spending by category
    spending_by_category = {}
    for account in accounts:
        if account.type == 'expense':
            category = account.category
            if category in spending_by_category:
                spending_by_category[category] += account.balance
            else:
                spending_by_category[category] = account.balance

    return render_template('spending_by_category.html', spending_by_category=spending_by_category)


@dashboard_bp.route('/budget_performance')
@login_required
def budget_performance():
    user_id = current_user.id
    accounts = Account.query.filter_by(user_id=user_id).all()

    # Calculate budget performance
    budget_performance = {}
    for account in accounts:
        if account.type == 'expense':
            category = account.category
            budget = account.budget
            actual = account.balance
            performance = (actual / budget) * 100
            budget_performance[category] = performance

    return render_template('budget_performance.html', budget_performance=budget_performance)


@dashboard_bp.route('/debt_repayment_plan')
@login_required
def debt_repayment_plan():
    user_id = current_user.id
    debts = Debt.query.filter_by(user_id=user_id).all()

    # Calculate debt repayment plan
    debt_repayment_plan = {}
    for debt in debts:
        debt_repayment_plan[debt.name] = debt.repayment_plan

    return render_template('debt_repayment_plan.html', debt_repayment_plan=debt_repayment_plan)


@dashboard_bp.route('/investment_portfolio')
@login_required
def investment_portfolio():
    user_id = current_user.id
    investments = Investment.query.filter_by(user_id=user_id).all()

    # Calculate investment portfolio
    investment_portfolio = {}
    for investment in investments:
        investment_portfolio[investment.name] = investment.value

    return render_template('investment_portfolio.html', investment_portfolio=investment_portfolio)


@dashboard_bp.route('/retirement_savings')
@login_required
def retirement_savings():
    user_id = current_user.id
    accounts = Account.query.filter_by(user_id=user_id).all()

    # Calculate retirement savings
    retirement_savings = 0
    for account in accounts:
        if account.type == 'retirement':
            retirement_savings += account.balance

    return render_template('retirement_savings.html', retirement_savings=retirement_savings)


@dashboard_bp.route('/emergency_fund')
@login_required
def emergency_fund():
    user_id = current_user.id
    accounts = Account.query.filter_by(user_id=user_id).all()

    # Calculate emergency fund
    emergency_fund = 0
    for account in accounts:
        if account.type == 'emergency':
            emergency_fund += account.balance

    return render_template('emergency_fund.html', emergency_fund=emergency_fund)
