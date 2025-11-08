""" """
#GENERAL IMPORTS
from nicegui import ui,APIRouter
from fastapi import Request

#SERVICES IMPORTS
from services.provider.admin.db import register_login
from services.provider.auth.users import AuthStaff
from .pages import Page,Dashboard



#PAGE ROUTES
router = APIRouter(prefix="")

@ui.page("/",title="NexaHIMS | Login",api_router=router)
def login_page():
  """A route to display login page"""
  
  return Page()


@ui.page("/dashboard",title="NexaHIMS | Dashboard")
def dashboard(request:Request):
  """A route to display the page based on request's login credentials and permissions"""
  
  staff = AuthStaff(request)
  if staff.user:
    data = staff.user
    if data["valid"]:
      user = data["user"]
      #Register login
      if not data["logged"]:
        _login_id = f"{user.username}log{len(user.logins) + 1}"
        register_login({"login_id":_login_id,"username":user.username})
      #Return the page
      return Page(credentials=data,page_content=Dashboard,user=user)

      
    else:
      return Page(credentials=staff.user)
  else:
    return Page(credentials={"user":False,"login":[request.query_params.get("username"),request.query_params.get("password")]})

