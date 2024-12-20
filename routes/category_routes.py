from flask import Blueprint, request, jsonify
from models import Category, db
from flask_login import login_required, current_user

category_bp = Blueprint('category', __name__, url_prefix='/api/category')


# Create a new category
@category_bp.post('/')
@login_required
def add_category():
    data = request.get_json()
    name = data.get('name')
    category_type = data.get('type')  # 'income' or 'expense'
    if not name or not category_type:
        return jsonify({'error': 'Category name and type are required'}), 400
    new_category = Category(name=name, type=category_type, user_id=current_user.id)
    db.session.add(new_category)
    db.session.commit()
    return jsonify({'message': 'Category created successfully', 'category': new_category.to_dict()}), 201


# Get all categories for the logged-in user
@category_bp.get('/')
@login_required
def get_categories():
    categories = [category.to_dict() for category in current_user.categories.all()]
    return jsonify({'categories': categories}), 200


# Get a category by ID
@category_bp.get('/<int:category_id>')
@login_required
def get_category_by_id(category_id):
    category = current_user.categories.filter_by(id=category_id).first()
    if not category:
        return jsonify({'error': 'Category not found or access denied'}), 404
    return jsonify({'category': category.to_dict()}), 200


# Get enabled categories
@category_bp.get('/enabled')
@login_required
def get_enabled_categories():
    categories = current_user.categories.filter_by(disabled=False).all()
    if not categories:
        return jsonify({'error': 'Categories not found or access denied'}), 404
    categories = [category.to_dict() for category in categories]
    return jsonify({'categories': categories}), 200


# Get categories by type ('income' or 'expense')
@category_bp.get('/type/<string:category_type>')
@login_required
def get_categories_by_type(category_type):
    if category_type not in ['income', 'expense']:
        return jsonify({'error': 'Invalid category type'}), 400
    categories = current_user.categories.filter_by(type=category_type).all()
    category_list = [category.to_dict() for category in categories]
    return jsonify({'categories': category_list}), 200


# Update an existing category
@category_bp.put('/<int:category_id>')
@login_required
def update_category(category_id):
    category = current_user.categories.filter_by(id=category_id).first()
    if not category:
        return jsonify({'error': 'Category not found or access denied'}), 404
    data = request.get_json()
    category.name = data.get('name', category.name)
    category.type = data.get('type', category.type)
    db.session.commit()
    return jsonify({'message': 'Category updated successfully', 'category': category.to_dict()}), 200


# enable a category
@category_bp.put('/enable/<int:category_id>')
@login_required
def enable_category(category_id):
    category = current_user.categories.filter_by(id=category_id).first()
    if not category:
        return jsonify({'error': 'Category not found or access denied'}), 404
    category.disabled = False
    db.session.commit()
    return jsonify({'message': 'Category enabled successfully'.title()}), 200


# disable a category
@category_bp.put('/disable/<int:category_id>')
@login_required
def disable_category(category_id):
    category = current_user.categories.filter_by(id=category_id).first()
    if not category:
        return jsonify({'error': 'Category not found or access denied'}), 404
    category.disabled = True
    db.session.commit()
    return jsonify({'message': 'Category Disable successfully'}), 200
