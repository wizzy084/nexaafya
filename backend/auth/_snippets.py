"""A module for base operations neccesary in processing semi during database updating and database querrying."""
#GENERAL IMPORTS
import os
from typing import Any
from dotenv import load_dotenv

#FASTAPI IMPORTS
from sqlalchemy import Boolean
from sqlmodel import Session,SQLModel,select

#VERO IMPORT
from services.provider.configs import database_engine

#CONSUL IMPORTS
from services.provider.admin.models import User


#ENVIRONMENT VARIABLES
load_dotenv()

SUPER_ADMIN=os.getenv("SUPER_ADMIN")
SUPER_PASSKEY=os.getenv("SUPER_PASSKEY")


#
def is_db_user(username:str|None) -> Any:
  """Returns True if the user is in the database, False otherwise"""

  with Session(database_engine) as session:
    #db_users = session.exec(select(User).where(User.username == username)).first()
    db_user=None

    return db_user


def is_superadmin(username:str|None):
  """Returns True if the user is the superadmin, False otherwise"""
  
  return username == SUPER_ADMIN


def get_db_user(username:str|None):
  """Retrieves the User details from database based on query 'username'."""

  with Session(database_engine) as session:
    db_user:User|None = session.exec(select(User).where(User.username==username)).first()
  
  return db_user




"""Miscellaneous code snippets for consul uix"""



#CLASSES
class User:
  def __init__(self, username:str|None=None):
    self.username = username
    self.title = None
    self.first_name = None
    self.middle_name = None
    self.last_name = None
    self.password = None
    self.logged_in = False
    self.is_admin = False
    self.logins = 0
    self.photo = None


class PageRoutes:
  def __init__(self, *args):
    self.login = None

#FUNCTIONS
def set_guest_in_dropdown(user=None):
  """A function to set 'Guest' as username if no user:User is provided in AdminProfile function in widgets.py"""
  
  if user:
    return user.username
  else:
    return "Guest"


def login():
  

  print("logina()")