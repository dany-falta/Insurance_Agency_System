from sqlalchemy import create_engine
from flask_login import UserMixin
from .auth import login_user, logout_user, current_user
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, Query, relationship
#from .secret_key import CON_CRD
from sqlalchemy.sql import func
from functools import wraps

def login_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            from . import login_manager
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if args:
                if not current_user.urole in roles and "":
                    return login_manager.unauthorized()
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

if True:
    from . import db

class User(db.Model, UserMixin):
    """User account."""

    id = db.Column(db.Integer, primary_key=True, autoincrement="auto")
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    urole = db.Column(db.String(150), nullable=False)

    def get_id(self):
        return self.id

    def is_active(self):
        return self.is_active

    def activate_user(self):
        self.is_active = True

    def get_email(self):
        return self.email

    def get_urole(self):
        return self.urole



class Admin(db.Model):
    """Admins."""
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, autoincrement="auto")
    last_name = db.Column(db.NVARCHAR(255), nullable=False)
    first_name = db.Column(db.NVARCHAR(150), nullable=False)
    middle_name = db.Column(db.NVARCHAR(150))
    phone_no = db.Column(db.String(20))

    user = db.relationship("User", backref=db.backref("admins", cascade="all,delete", uselist=False))

    def get_id(self):
        return self.user_id



class Agent(db.Model):
    """ Agents."""
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, autoincrement="auto")
    last_name = db.Column(db.NVARCHAR(255), nullable=False)
    first_name = db.Column(db.NVARCHAR(150), nullable=False)
    middle_name = db.Column(db.NVARCHAR(150))
    license_no = db.Column(db.NVARCHAR(20))
    comission = db.Column(db.Float())


    user = db.relationship("User", backref=db.backref("agents"), uselist=False)

    admin_id = db.Column(db.Integer, db.ForeignKey('admin.user_id'))
    admin = db.relationship("Admin", backref=db.backref("agents"))

    def get_id(self):
        return self.user_id

class Client(db.Model):
    """Clients."""

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True, autoincrement="auto")
    first_name = db.Column(db.NVARCHAR(150), nullable=False)
    last_name = db.Column(db.NVARCHAR(255), nullable=False)
    middle_name = db.Column(db.NVARCHAR(150))
    date_of_birth = db.Column(db.Date, nullable=False)
    phone_no = db.Column(db.String(20))
    address = db.Column(db.NVARCHAR(150))

    user = db.relationship("User", backref=db.backref("clients", cascade="all,delete") , uselist=False)

    agent_id = db.Column(db.Integer, db.ForeignKey('agent.user_id'))
    agent = db.relationship("Agent", backref="clients")

    def get_id(self):
        return self.user_id

class Policy(db.Model):
    """Policies."""

    id = db.Column(db.Integer, primary_key=True, autoincrement="auto")
    ptype = db.Column(db.NVARCHAR(255), nullable=False)
    validity = db.Column(db.NVARCHAR(20), default= "Двенадцать месяцев", nullable=False)
    company_name = db.Column(db.NVARCHAR(255))
    amount_sum = db.Column(db.Numeric(15, 2))

    agent_id = db.Column(db.Integer, db.ForeignKey('agent.user_id'))
    agent = db.relationship("Agent", backref=db.backref("policies", cascade="all,delete"))



class Purchase(db.Model):
    """Policy purchases"""

    id = db.Column(db.Integer, primary_key=True, autoincrement="auto")
    purchase_date = db.Column(db.DateTime(timezone=True), default=func.now())

    policy_id = db.Column(db.Integer, db.ForeignKey('policy.id'))
    policy = db.relationship("Policy", backref=db.backref("purchases", cascade="all,delete"))

    client_id = db.Column(db.Integer, db.ForeignKey('client.user_id'))
    client = db.relationship("Client", backref=db.backref("purchases", cascade="all,delete"))
