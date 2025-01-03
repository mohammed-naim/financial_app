from flask import Blueprint, request, jsonify
from models import Category, db
from flask_login import login_required, current_user
from marshmallow import Schema, fields, ValidationError

category_bp = Blueprint('category', __name__, url_prefix='/api/category')


def validate_type(value):
    allowed_types = ["income", "expense"]
    if value not in allowed_types:
        raise ValidationError("Invalid types")


class CategorySchema(Schema):
    name = fields.Str(required=True)
    category_type = fields.Str(required=False, validate=validate_type)


# Create a new category
@category_bp.post('/')
@login_required
def add_category():
    data = request.get_json()
    try:
        schema = CategorySchema()
        data = schema.load(data)
    except ValidationError as err:
        return jsonify({'error': 'Category name and type are required'}), 400
    name = data.get('name')
    category_type = data.get('category_type', 'expense')  # 'income' or 'expense'
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
    categories = [category.to_dict() for category in categories]
    return jsonify({'categories': categories}), 200


@category_bp.get('/disabled')
@login_required
def get_disabled_categories():
    categories = current_user.categories.filter_by(disabled=True).all()
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
    try:
        schema = CategorySchema()
        data = schema.load(data)
    except ValidationError as err:
        return jsonify({'error': 'Category name and type are required'}), 400

    category.name = data.get('name', category.name)
    # category.type = data.get('type', category.type)
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


@category_bp.delete('/<int:category_id>')
@login_required
def delete_account(category_id: int):
    category = current_user.categories.filter_by(id=category_id).first()
    if not category:
        return jsonify({'error': 'Account not found or access denied'}), 404
    if category.transactions.first():
        return jsonify({"error": "There are operations associated with this category."}), 400
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category Deleted Successfully'}), 200
