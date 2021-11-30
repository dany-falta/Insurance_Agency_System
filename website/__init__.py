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
app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc://sa:test@DESKTOP-DANI/{DB_NAME}?driver=SQL+Server"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

from .views import views
from .auth import auth

app.register_blueprint(views, url_prefix='/')
app.register_blueprint(auth, url_prefix='/')

#from .models import Base, engine, session, Clients, Admin, Agent

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    from .auth import role
    from .models import Base, engine, session, Clients, Admin, Agent
    Base.prepare(engine, reflect=True)
    print(session.query(Clients).get(int(id)))
    if role == "Clients":
        return session.query(Clients).get(int(id))
    elif role == "Agent":
        return session.query(Agent).get(int(id))
    elif role == "Admin":
        return session.query(Admin).get(int(id))
    else:
        return None
