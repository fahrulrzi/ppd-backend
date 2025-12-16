from flask import Blueprint, request, jsonify, current_app
from . import db
from .models import Prediction, User
import jwt
from functools import wraps
import numpy as np
import pandas as pd
import datetime

bp = Blueprint('predict', __name__)

REQUIRED_COLS = [
    "age","sex","chest pain type","resting bp s","cholesterol",
    "fasting blood sugar","resting ecg","max heart rate",
    "exercise angina","oldpeak","ST slope"
]

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Ambil token dari header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.replace('Bearer ', '')
            else:
                token = auth_header
        
        # Debug: log token status
        if not token:
            current_app.logger.warning("No token provided in request")
            return jsonify({'msg':'token missing'}), 401
        
        try:
            # Decode token dengan timezone-aware datetime
            data = jwt.decode(
                token, 
                current_app.config['JWT_SECRET'], 
                algorithms=['HS256'],
                options={"verify_exp": True} 
            )
            
            # Cek apakah 'sub' ada dalam payload
            if 'sub' not in data:
                current_app.logger.error("Token missing 'sub' claim")
                return jsonify({'msg':'invalid token structure'}), 401
            
            user_id = int(data['sub'])
            
            user = User.query.get(user_id)
            if user is None:
                current_app.logger.error(f"User with id {data['sub']} not found")
                return jsonify({'msg':'user not found'}), 401
            
            current_app.logger.info(f"User {user.username} authenticated successfully")
            
        except jwt.ExpiredSignatureError:
            current_app.logger.warning("Token has expired")
            return jsonify({'msg':'token expired'}), 401
        except jwt.InvalidTokenError as e:
            current_app.logger.error(f"Invalid token: {str(e)}")
            return jsonify({'msg':'token invalid', 'err': str(e)}), 401
        except Exception as e:
            current_app.logger.error(f"Token verification failed: {str(e)}")
            return jsonify({'msg':'token verification failed', 'err': str(e)}), 401
        
        return f(user, *args, **kwargs)
    
    return decorated

@bp.route('/predict', methods=['POST'])
@token_required
def predict(user):
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({'msg': 'invalid json'}), 400

    if 'features' in payload:
        features = payload['features']
        if not isinstance(features, list):
            return jsonify({'msg': 'features must be a list'}), 400
        if len(features) != len(REQUIRED_COLS):
            return jsonify({'msg': f'features must have length {len(REQUIRED_COLS)}'}), 400
        row = dict(zip(REQUIRED_COLS, features))

    elif 'row' in payload:
        row = payload['row']
        if not isinstance(row, dict):
            return jsonify({'msg': 'row must be an object/dict'}), 400
    else:
        return jsonify({'msg': 'provide features (list) or row (dict)'}), 400

    missing = [c for c in REQUIRED_COLS if c not in row]
    if missing:
        return jsonify({'msg': 'missing columns', 'missing': missing}), 400

    try:
        X = pd.DataFrame(
            [[float(row[c]) for c in REQUIRED_COLS]],
            columns=REQUIRED_COLS
        )
    except Exception as e:
        return jsonify({'msg': 'invalid feature values', 'err': str(e)}), 400

    pipeline = getattr(current_app, "pipeline", None)
    if pipeline is None:
        return jsonify({'msg': 'pipeline not loaded on server'}), 500

    try:
        pred = pipeline.predict(X)

        prob = None
        if hasattr(pipeline, "predict_proba"):
            prob = pipeline.predict_proba(X).tolist()

        output = {
            'prediction': pred.tolist(),
            'probability': prob
        }

    except Exception as e:
        return jsonify({'msg': 'prediction failed', 'err': str(e)}), 500

    try:
        rec = Prediction(
            user_id=user.id,
            input_json=row,
            output_json=output
        )
        db.session.add(rec)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error("failed to save prediction: %s", e)

    return jsonify(output), 200
