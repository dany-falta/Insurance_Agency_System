from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from . import secret_key
import pyodbc
import sys


db = SQLAlchemy()
DB_NAME = 'Insurance_agency_management'


app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc://{secret_key.CON_CRD}@DESKTOP-DANI/{DB_NAME}?driver=SQL+Server"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

#from .views import views
from .auth import auth, admin, agent
#app.register_blueprint(views, url_prefix='/')
app.register_blueprint(auth, url_prefix='/')
app.register_blueprint(admin, url_prefix='/Admin')
app.register_blueprint(agent, url_prefix='/Agent')
from .models import User, Purchase, Policy, Client, Admin, Agent
with app.app_context():
    db.create_all()
    db.session.commit()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
