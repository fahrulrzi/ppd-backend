from . import db
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'user'  # Explicit table name
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(200), nullable=False, default='')
    date_of_birth = db.Column(db.Date, nullable=True)
    blood_type = db.Column(db.String(3), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    password_hash = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    # Relationship
    predictions = db.relationship('Prediction', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Prediction(db.Model):
    __tablename__ = 'prediction'  # Explicit table name
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=True, index=True)
    input_json = db.Column(db.JSON, nullable=False)
    output_json = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Prediction {self.id} by User {self.user_id}>'