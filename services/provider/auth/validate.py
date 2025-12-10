"""A module for authorization of users logging into VERO"""

#GENERAL IMPORTS
import json
from collections import namedtuple

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

  Credentials = namedtuple("Credentials",["user","username","exists","password_match","logged"],defaults=[None,None,False,False,False])
  credentials = Credentials()

  with Session(database_engine) as session:
    db_user:User = session.exec(select(User).where(User.username == requested_username)).first()

    if db_user:
      credentials = credentials._replace(exists=True)
      credentials = credentials._replace(username=db_user.username)

      if db_user.password == requested_password:
        credentials = credentials._replace(user= unmodel_user(db_user))
        credentials = credentials._replace(password_match=True)
        credentials = credentials._replace(logged=True)
  return credentials

  
    