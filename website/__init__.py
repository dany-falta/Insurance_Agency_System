from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from . import secret_key
import pyodbc


db = SQLAlchemy()
DB_NAME = 'Insurance_agency_management'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secret_key.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc://sa:test@DESKTOP-DANI/{DB_NAME}?driver=SQL+Server"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')


    return app
