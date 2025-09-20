from . import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    entries = db.relationship('Entry', backref='user', lazy=True)

    def set_password(self, password, bcrypt):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password, bcrypt):
        return bcrypt.check_password_hash(self.password_hash, password)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)