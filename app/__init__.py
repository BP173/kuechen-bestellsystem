from flask import Flask
from .models import db
from .routes import main

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)   # ← DAS ist der entscheidende Punkt

    app.register_blueprint(main)

    return app