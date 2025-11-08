"""A module for authorization of users logging into VERO"""

#GENERAL IMPORTS
import json,os
from dotenv import load_dotenv


#FASTAPI IMPORTS
from fastapi.requests import Request
from sqlmodel import select,Session

#MISC IMPORTS
from services.provider.admin.models import Login,User
from services.provider.configs import database_engine

#ENVIRONMENT VARIABLES
load_dotenv()

SUPER_ADMIN = os.getenv("SUPER_ADMIN")
SUPER_FIRST_NAME = os.getenv("SUPER_FIRST_NAME")
SUPER_MIDDLE_NAME = os.getenv("SUPER_MIDDLE_NAME")
SUPER_LAST_NAME = os.getenv("SUPER_LAST_NAME")
SUPER_PASSKEY = os.getenv("SUPER_PASSKEY")




#DECORATORS
"""Under construction"""


#CLASSES
class AuthStaff():
  """A class to handle user authentication"""
  
  def __init__(self,request:Request):
    """Initialize the user object with the request object"""
    
    #REQUEST DETAILS
    self.username:str|None = request.query_params.get("username")
    self.password = request.query_params.get("password")
    
    self.user = self.__getuser()
  
  def __login(self,db_login:Login):
    return Login(
      login_id=db_login.login_id,
      username=db_login.username,
      logged=db_login.logged,
      login_time=db_login.login_time,
      logout_time=db_login.logout_time,
      login_ip=db_login.login_ip,
      logout_ip=db_login.logout_ip
    )
    
  def __user(self,db_user:User):
    return User(
      first_name=db_user.first_name,
      middle_name=db_user.middle_name,
      last_name=db_user.last_name,
      username=db_user.username,
      password=db_user.password,
      title=db_user.title,
      qualification=db_user.qualification,
      designation=db_user.designation,
      birthdate=db_user.birthdate,
      gender=db_user.gender,
      email=db_user.email,
      mobile=db_user.mobile,
      roles=json.loads(db_user.roles),
      is_super=db_user.is_super,
      registered_on=db_user.registered_on,
      active=db_user.active,
      suspended=db_user.suspended,
      logins=[self.__login(db_login) for db_login in db_user.logins]
      )
  
  def __getuser(self):
    """Retrieves data from users table row and returns as a User class instance,if no user found"""

    try:
      with Session(database_engine) as session:
        #User availability
        db_user:User = list(session.exec(select(User).where(User.username == self.username)))[0]
        user = self.__user(db_user)
        if user.logins:
          _last_login = user.logins[-1]
          _logged = _last_login.logged
        else:
          _logged = False
        #Active status checking
        if user.active:
          #Password checking
          if user.password == self.password:
            return {"user":user,"valid":True,"active":user.active,"logged":_logged}
          else:
            return {"user":user,"valid":False,"active":user.active,"logged":_logged,"login":[self.username,self.password]}

        else:
          return {"user":user,"valid":True,"active":user.active,"logged":_logged,"login":[self.username,self.password]}
        
        
    except:
      return None


  
  
    