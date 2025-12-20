"""A module for authorization of users logging into VERO"""

#GENERAL IMPORTS
import json
from collections import namedtuple

#FASTAPI IMPORTS
from sqlmodel import select,Session

#MISC IMPORTS
from ..admin._snippets import User,unmodel_user
from ..configs import database_engine




##
#PRIVATE FUNCTIONS
async def authenticate_user(data:dict):
  """Retrieves data from users table row and returns as a User class instance,if no user found"""
  requested_username,requested_password = data["username"],data["password"]

  credentials = {"user":None,"active":False,"username":None,"exists":None,"password_match":None,"logged":None}

  with Session(database_engine) as session:
    db_user:User = session.exec(select(User).where(User.username == requested_username)).first()

    if db_user:
      credentials["exists"] =True
      credentials["username"] = db_user.username
      credentials["active"] = db_user.active

      if db_user.password == requested_password:
        credentials["user"] = unmodel_user(db_user)._asdict()
        credentials["user"]["logins"] = [log._asdict() for log in credentials["user"]["logins"]]
        credentials["password_match"] = True
        credentials["logged"] = True

  return credentials

  
    