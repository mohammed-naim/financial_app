from flask import Blueprint, jsonify
from flask_login import login_required, current_user

from models import db

settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')


@settings_bp.put('/<string:language>')
@login_required
def change_language(language):
    if not language or language not in ['en', 'ar']:
        return jsonify({'error': 'language not found'}), 404
    current_user.language = language
    db.session.commit()
    return jsonify({'message': 'Language changed successfully'}), 200
