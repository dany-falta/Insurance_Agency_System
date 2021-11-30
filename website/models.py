from sqlalchemy import create_engine
from flask_login import UserMixin
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, Query

#from . import db

engine = create_engine(f"mssql+pyodbc://sa:test@DESKTOP-DANI/Insurance_agency_management?driver=SQL+Server", echo=False)
Base = automap_base()
session = Session(engine)

from . import login_manager

@login_manager.user_loader
def load_user(id):
    from .auth import role
    Base.prepare(engine, reflect=True)
    if role == "Clients":
        return session.query(Clients).get(int(id))
    elif role == "Agent":
        return session.query(Agent).get(int(id))
    elif role == "Admin":
        return session.query(Admin).get(int(id))
    else:
        return None
    #print(session.query(Clients).get(int(id)), role)

"""
Admin = Base.classes.Admin
Agent = Base.classes.Agent
Clients = Automapper.classes.Clients
Policies = Base.classes.Policies
Purchases = Base.classes.Purchases
"""



class Admin(Base, UserMixin):
    __tablename__ = 'Admin'

    def get_id(self):
           return (self.AdminID)

class Agent(Base, UserMixin):
    __tablename__ = 'Agent'

    def get_id(self):
           return (self.AgentID)

class Clients(Base, UserMixin):
    __tablename__ = 'Clients'

    def get_id(self):
           return (self.ClientID)

class Policies(Base):
    __tablename__ = 'Policies'

class Purchases(Base):
    __tablename__ = 'Purchases'

Base.prepare(engine, reflect=True)





if __name__ == '__main__':
    from sqlalchemy.orm import Session, Query
    session = Session(engine)
    for item in session.query( Admin.PhoneNo):
        print(item)
    print(session.query(Clients.ClientID).filter_by(Email='testing@testing.ru').scalar() is not None)
