from flask import Blueprint, request, jsonify, current_app
from .models import User
from . import db
import jwt
import datetime

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data.get('username') or not data.get('password') or not data.get('full_name') or not data.get('date_of_birth') or not data.get('blood_type') or not data.get('gender'):
        return jsonify({'msg':'all data must be filled in'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'msg':'user exists'}), 400
    
    user = User(username=data['username'])
    user.set_password(data['password'])
    user.full_name = data['full_name']
    user.date_of_birth = datetime.datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
    user.blood_type = data['blood_type']
    user.gender = data['gender']
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'msg':'created'}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    
    if not user or not user.check_password(data.get('password')):
        return jsonify({'msg':'invalid credentials'}), 401
    
    payload = {
        'sub': str(user.id),
        'iat': datetime.datetime.now(datetime.timezone.utc),
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=12)
    }
    
    token = jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm='HS256')
    
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    return jsonify({
        'access_token': token,
        'token_type': 'Bearer',
        'expires_in': 43200  
    }), 200