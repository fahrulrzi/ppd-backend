from flask import Blueprint, request, jsonify, current_app
from . import db
from .models import User, Prediction
import jwt
from functools import wraps
from datetime import date

bp = Blueprint('user', __name__)

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

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

@bp.route('/profile', methods=['GET', 'OPTIONS'])
@token_required
def profile(user):
    age = calculate_age(user.date_of_birth) if user.date_of_birth else None
    user_data = {
        'id': user.id,
        'username': user.username,
        'full_name': user.full_name,
        'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
        'age': age,
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

@bp.route('/history', methods=['GET', 'OPTIONS'])
@token_required
def history(user):
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = user.predictions.order_by(db.desc(Prediction.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )

    history_data = []
    for pred in pagination.items:
        history_data.append({
            'id': pred.id,
            'input_json': pred.input_json,
            'output_json': pred.output_json,
            'created_at': pred.created_at.isoformat()
        })

    return jsonify({
        'status': 'success',
        'current_page': page,
        'total_pages': pagination.pages,
        'total_items': pagination.total,
        'history': history_data
    }), 200