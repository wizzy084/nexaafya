"""A module for authorization of users logging into VERO"""

#GENERAL IMPORTS
import json

#FASTAPI IMPORTS
from sqlmodel import select,Session

#MISC IMPORTS
from services.provider.admin.models import User
from services.provider.admin._snippets import unmodel_user
from services.provider.configs import database_engine




##
#PRIVATE FUNCTIONS
def authenticate_user(data:dict):
  """Retrieves data from users table row and returns as a User class instance,if no user found"""
    
  requested_username,requested_password = data["username"],data["password"]

  _data = {"user_exists":False,"user":None,"password_match":False,"username":requested_username,"active":False}

  with Session(database_engine) as session:
    db_user:User = session.exec(select(User).where(User.username == requested_username)).first()

    if db_user:
      _data["user_exists"] = True

      if db_user.password == requested_password:
        _data["user"] = unmodel_user(db_user)
        _data["password_match"] = True
        _data["active"] = True if db_user.active else False
    
  return _data

  
    