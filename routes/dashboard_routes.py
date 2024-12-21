# dashboard_routes.py
from flask import Blueprint, render_template, request, jsonify
from models import User, Account, Debt, Investment, db
from flask_login import login_required, current_user

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')
