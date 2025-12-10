from flask import Blueprint, request, jsonify, current_app
from . import db
from .models import User
import jwt
from functools import wraps

bp = Blueprint('user', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].replace('Bearer ', '')
        if not token:
            return jsonify({'msg':'token missing'}), 401
        try:
            data = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=['HS256'])
            user = User.query.get(data['sub'])
        except Exception as e:
            return jsonify({'msg':'token invalid', 'err':str(e)}), 401
        return f(user, *args, **kwargs)
    return decorated

@bp.route('/profile', methods=['GET'])
@token_required
def profile():
    user = request.user
    user_data = {
        'id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
        'blood_type': user.blood_type,
        'gender': user.gender,
        'created_at': user.created_at.isoformat()
    }
    return jsonify(user_data)

@bp.route('/dashboard', methods=['GET'])
@token_required
def dashboard(user):
    total_predictions = user.predictions.count()
    latest_prediction = user.predictions.order_by(db.desc('created_at')).first()
    
    latest_prediction_data = {
        'id': latest_prediction.id,
        'input_json': latest_prediction.input_json,
        'output_json': latest_prediction.output_json,
        'created_at': latest_prediction.created_at.isoformat()
    } if latest_prediction else None
    
    dashboard_data = {
        'total_predictions': total_predictions,
        'latest_prediction': latest_prediction_data
    }
    
    return jsonify(dashboard_data)