from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
from joblib import load

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    # ===== FIX CORS =====
    # Tambahkan CORS untuk allow semua origin
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Alternative: Manual CORS headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    # ===== LOAD MODEL =====
    # Load model once at startup with error handling
    try:
        model_path = os.path.join(app.root_path, 'ml', 'model.joblib')
        if os.path.exists(model_path):
            app.model = load(model_path)
            print(f"✅ Model loaded successfully from {model_path}")
        else:
            print(f"⚠️  Model file not found at {model_path}")
            app.model = None
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        app.model = None
    
    # ===== HEALTH CHECK ENDPOINTS =====
    @app.route('/')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Flask API is running',
            'model_loaded': app.model is not None
        }), 200
    
    @app.route('/health')
    def health():
        try:
            # Test database connection
            db.session.execute('SELECT 1')
            db_status = 'connected'
        except Exception as e:
            db_status = f'error: {str(e)}'
        
        return jsonify({
            'status': 'ok',
            'database': db_status,
            'model': 'loaded' if app.model else 'not loaded'
        }), 200
    
    # ===== REGISTER BLUEPRINTS =====
    from .auth import bp as auth_bp
    from .predict import bp as predict_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(predict_bp, url_prefix='/api')
    
    return app