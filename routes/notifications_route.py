from flask import Blueprint, jsonify
from models import db, Notification
from flask_login import login_required, current_user
from flask_babel import lazy_gettext as _

notification_bp = Blueprint('notification', __name__, url_prefix='/api/notification')


# Get all notifications
@notification_bp.get('/')
@login_required
def get_notifications():
    notifications = [n.to_dict() for n in current_user.notifications.filter_by(is_seen=False).all()]
    return jsonify({'notifications': notifications}), 200


# Update a notification to seen
@notification_bp.put('/<int:notification_id>')
@login_required
def update_notification(notification_id):
    notification = current_user.notifications.filter_by(id=notification_id).first()
    if not notification:
        return jsonify({'error': _('Notification not found or access denied')}), 404
    notification.is_seen = True
    db.session.commit()
    return jsonify({'message': _('Notification updated successfully')}), 200
