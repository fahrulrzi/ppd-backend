from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from joblib import load

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    # load model once at startup
    model_path = os.path.join(app.root_path, 'ml', 'model.joblib')
    app.model = load(model_path)

    # register blueprints
    from .auth import bp as auth_bp
    from .predict import bp as predict_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(predict_bp, url_prefix='/api')

    return app
