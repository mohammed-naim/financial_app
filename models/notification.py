from . import db


class Notification(db.Model):
    __tablename__ = 'Notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_seen = db.Column(db.Boolean, nullable=False)

    def __init__(self, user_id: int, message: str, is_seen: bool):
        self.user_id = user_id
        self.message = message
        self.is_seen = is_seen

    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'is_seen': self.is_seen
        }

    def __repr__(self):
        return f'<Notification {self.message} - {self.is_seen}>'
