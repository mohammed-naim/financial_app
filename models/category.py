from . import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    disabled = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    transactions = db.relationship('Transaction', backref='category', lazy=True)

    def __init__(self, user_id, name, type):
        self.user_id = user_id
        self.name = name
        self.type = type

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'disabled': self.disabled
        }

    def __repr__(self):
        return f'<Category {self.name} - {self.type}>'
