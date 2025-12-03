"""A module for constructing main page and page layouts"""
#GENERAL IMPORTS
import asyncio,uuid

#NiceGUI IMPORTS
from fastapi import Request
from nicegui import app,html,ui,APIRouter

#APP IMPORTS
from services.provider.auth.validate import authenticate_user
from services.provider.admin.db import register_login,update_login

#UIX IMPORTS
from .configs import HEAD_LINKS,META_TAGS,BODY_LINKS
from .consultation.widgets import *
from .imaging.widgets import *
from .nursing.widgets import *
from .management.widgets import AdministrationManagementDisplay
from .tools.animations import *
from .tools.widgets import *


#PAGE ROUTES
router = APIRouter(prefix="")

@ui.page("/",title="NexaClinic",api_router=router)
async def main_page():
  """A route to display login page by default"""

  login_credentials = {"new_login":True,"username":"","user_exists":False,"user":None,"password_match":False,"active":False}
  
  await ui.context.client.connected()
  
  if app.storage.user:
    login_credentials["new_login"] = False
    stored_credentials = {"username":app.storage.user["username"],"password":app.storage.user["password"]}
    login_credentials.update(authenticate_user(stored_credentials))

  #REGISTER LOGIN
  if login_credentials["user"]:
    user = login_credentials["user"]
    if user.active and not [log for log in user.logins if log.logged]:
      _login_id = f"{user.username}-log-{str(uuid.uuid4()).split('-')[0]}"
      register_login({"login_id":_login_id,"username":user.username})

  Page(login_credentials=login_credentials)


#MAIN PAGE
class Page():
  """A class to construct a page layout for the admin panel"""

  def __init__(self,login_credentials:dict):
    
    #PAGE SETUP
    self.login_credentials = login_credentials
    self.user = self.login_credentials["user"]
    self.initial_data()
    self.Metadata()
    self.Notifications()

    ##DISPLAYS
    #USER DASHBOARD
    if self.user and self.user.active:
      self.PageHeader()
      ui.separator().classes(add="#05002b")
      self.MainPageContent()

    #LOGIN DISPLAY
    else:
      with html.div().style(add="width:100%;height:100%;").classes(add=""):
        #Content
        with html.div().style(add="width:100%;height:100%;overflow-y:hidden;").classes(add="relative flex flex-row justify-center content-center"):
          Login(login_credentials=self.login_credentials)
    
  #PAGE SETUP
  def initial_data(self):
    #PAGE TAB SEC
    if self.user:
      if "director" in self.user.roles:
        self.sections = {"services":["fa-solid fa-stethoscope",ServicesManagementDisplay],"management":["fa-solid fa-briefcase",AdministrationManagementDisplay]}
      elif "receptionist" in self.user.roles:
        self.sections = {"clients":["fa-solid fa-users-rectangle",ReceptionManager],"triage & dispensing":["fa-solid fa-heart-pulse",NursingManager]}
      elif "doctor" in self.user.roles:
        self.sections = {"services":["fa-solid fa-stethoscope",ClinicianServicesManager]}
      elif "nurse" in self.user.roles:
        self.sections = {"services":["fa-solid fa-heart-pulse",NursingServicesManagementDisplay]}
      elif "radiographer" in self.user.roles or "radiologist" in self.user.roles:
        self.sections = {"studies":["fa-solid fa-x-ray",StudiesManagementDisplay]}

  def Metadata(self):
    """Inserts meta tags in the head of HTML document rendered by this class"""
    #Overall Styling
    ui.query('.nicegui-content').classes(f"absolute-full h-full flex flex-col overflow-y-auto overflow-x-hidden p-0 gap-0 {'dashboard-bg' if self.user and self.user.active else 'login-bg'} ")
    
    #Meta tags
    for META_TAG in META_TAGS:
      ui.add_head_html(code=META_TAG)
      
    for HEAD_LINK in HEAD_LINKS:
      ui.add_head_html(code=HEAD_LINK)
    
    for BODY_LINK in BODY_LINKS:
      ui.add_body_html(code=BODY_LINK)
  
  def Notifications(self):
    """Displays popup notification with name of user and contextual message"""

    if self.login_credentials["user_exists"]:
      if self.login_credentials["password_match"]:
        if self.user.active:
          ui.notify(message=f"Welcome back {self.user.title.capitalize()} {self.user.first_name.capitalize()} {self.user.last_name.capitalize()}",caption="Have a nice experience!",timeout=5000,icon="fas fa-check-double fa-lg",color="light-blue-7",textColor="white",type="positive",position="top")
        else:
          ui.notify(message="Inactive Account!",caption="Contact Clinic Administration",progress=True,timeout=5000,icon="fas fa-circle-exclamation fa-beat-fade",textColor="white",type="secondary",position="top")
      else:
        ui.notify(message="Invalid password!",caption="Try Again or Contact System Admin",progress=True,timeout=3000,icon="fas fa-circle-exclamation fa-beat-fade",textColor="black",type="warning",position="top")
  
    else:
      if not self.login_credentials["new_login"]:
        ui.notify(message=f"No User Found!",caption="Check your username!",timeout=3000,icon="fas fa-circle-exclamation fa-beat-fade",textColor="white",type="negative",position="top")

  #FUNCTIONALITITES
  def logout(self):
    """Logs out the current user and returns a login page"""

    #UPDATE STORAGE
    app.storage.user.clear()

    #UPDATE DATABASE
    for login in self.user.logins:
      if login.logged:
        update_login({"login_id":login.login_id})
    
    #NAVIGATE TO LOGIN PAGE
    ui.navigate.to("/")
  
  #DISPLAYS
  def PageHeader(self):
    """Displays the header of the page"""
  
    with ui.header().classes(add="p-0 gap-0 bg-[#07004d]"):
      #Site header
      with html.div().classes("w-full flex flex-row justify-between items-center pl-0 pr-1 py-0 gap-0"):
        #Logo
        with html.div().classes(add=""):
          ui.image(source="/images/logos/future1.PNG").classes(add="size-12 md:size-16")
        #Site title
        with html.div().classes(add="grow flex flex-row justify-center items-center"):
          self.SiteTitle()

      #Separator
      with html.div().classes(add="w-full pb-0.5 pr-1.5 flex flex-row justify-center"):
        ui.separator().classes(add="w-full bg-[#09026f]")

      #Page Navigation
      with html.div().classes(add="w-full p-1 flex flex-row justify-between"):
        #Tabs
        with html.div().classes(add="grow flex flex-row justify-between lg:justify-center"):
          with ui.tabs().props(add="inline-label dense narrow-indicator align='center'").classes(add="w-fit text-yellow-500 text-bold") as self.page_tabs:
            for title,content in self.sections.items():
              ui.tab(title,icon=content[0]).props(add="").classes(add="hover:scale-[1.1]")
            
        #User Profile
        with html.div().classes(add=""):
          self.AdminProfile(user=self.user)

      #Separator
      with html.div().classes(add="w-full pb-0.5 pr-1.5 flex flex-row justify-center"):
        ui.separator().classes(add="w-full bg-[#09026f]")

  def MainPageContent(self):
    """Returns display for page navigation"""
    
    #Main Page Content
    with html.div().classes(add="grow w-full overflow-hidden flex flex-col"):
      #Separator
      ui.separator().classes(add="w-full bg-[#09026f]")

      #Page Tab Panels
      with ui.tab_panels(tabs=self.page_tabs,value=list(self.sections.keys())[0]).props(add="animated infinite transition-prev='jump-right' transition-next='jump-left' transition-duration='300'").classes(add="grow w-full bg-inherit grid grid-cols-1"):
        #Director
        
        for title,content in self.sections.items():
          with ui.tab_panel(name=title).classes(add="h-full w-full p-0 bg-inherit"):
            content[1](user=self.user)
    
  def AdminProfile(self,user):
    """A function to construct a widget to notify Admin Profile"""
    #FXS
    def user_icon()-> str:
      if user:
        if "doctor" in self.user.roles:
          return "user-doctor"
        elif "nurse" in self.user.roles or self.user.gender == "female":
          return "user-nurse"
        else:
          return "user-tie"
      else:
        return "user-large-slash"

    def department()->str:
      if self.user:
        if "director" in self.user.roles:
          return "administration"
        else:
          if "nurse" in self.user.roles:
            return "nursing"
          elif "radiographer" in self.user.roles or "radiologist" in self.user.roles:
            return "imaging"
          elif "receptionist" in self.user.roles:
            return "reception"
          elif "doctor":
            return "consultation"
      else:
        return "public"


    #DROPDOWN BUTTON ON THE PAGE
    with ui.dropdown_button(color="#152046").props(add=f"glossy transition-show='jump-left' transition-hide='jump-right' transition-duration='500'" if user else "disable-dropdown").classes("p-0 rounded ring-1 ring-yellow-400 hover:shadow-sm hover:shadow-yellow-500 text-yellow-500") as profile_dropdown:
      #Label
      with profile_dropdown.add_slot("label"):
        with html.div().classes(add="rounded-l-full flex flex-row gap-x-2 text-yellow-500"):
          #Icon/Image
          with html.div().classes(add="flex flex-col justify-center p-1 "):
            html.span().classes(add=f"fas fa-{user_icon()} fa-xl md:fa-2xl")
          with html.div().classes(add="lg-show h-full"):
            #Title & Name
            with html.div().classes(add="w-full text-md text-bold uppercase"):
              ui.label(f"{user.title} {user.last_name}, {user.designation}").classes(add="w-full text-center")
            #Allocation/department
            with html.div().classes(add="w-full text-xs uppercase italic text-yellow-200"):
              ui.label(department()).classes(add="w-full text-center")

      #User details
      with profile_dropdown.add_slot("default"):
        with html.div().classes(add="w-full bg-sky-50 flex flex-col gap-3"):
          if user:
            with html.div().style(add="min-width:40%;").classes(add="flex flex-row p-1 gap-1"):
              #Photo
              with html.div().classes(add="size-16 rounded-full ring-1 ring-[#152046] shadow-md shadow-[#152046]"):
                html.strong().classes(add=f"w-full h-full py-1 rounded-full bg-blue-50 text-harmony text-center text-5xl fas fa-{user_icon()}")
              #Working details
              with html.div().classes(add="grow grid grid-cols-1 gap-2 rounded-r p-1 bg-inherit"):
                #Name
                ui.label(text=f"{self.user.title.capitalize()}. {self.user.first_name.capitalize()} {self.user.middle_name.capitalize() if self.user.middle_name else ''} {self.user.last_name.capitalize()}").classes(add="w-full px-1.5 bg-inherit rounded shadow-sm shadow-[07004d] text-bold text-lg text-harmony")
                #Designation & Title
                with html.div().classes(add="w-full"):
                  ui.label(self.user.roles[-1].title()).classes(add="w-fit p-1 rounded shadow-sm shadow-[#07004d] text-bold text-sm italic text-gray-800")
              
            #Logout functionality
            with html.div().classes(add="w-full py-3 flex flex-row justify-center"):
              ui.separator().classes(add="w-full my-3")
              ui.button(text="logout",icon="fas fa-power-off",color="",on_click=self.logout).props(add="dense glossy type='submit'").classes(add="rounded bg-harmony text-bold text-red-500 text-xl")

  def SiteTitle(self):
    """A function to construct a VERO title for the admin panel"""

    with html.strong().props(add="style='font-family:Helvetica'").classes(add="small-caps text-2xl lg:text-4xl text-bold text-yellow-500"):
      for letter in ["Future","Specialized","Dental","Clinic"]:
        ui.label(text=letter).style(add="text-shadow:2px 2px #505050;").classes("inline mr-2 ")



#RECEPTION WIDGETS
class ReceptionManager():
  """A class to display UI for managing studies"""

  def __init__(self,user):
    #DATA
    self.user = user

    #UI
    with html.div().classes(add="w-full h-full flex flex-col p-0 gap-1 bg-inherit animate__animated animate__fadeIn") as self.master_container:
      with ui.carousel(value="clients").style(add="overflow-y:hidden;").props(add="animated swipeable transition-prev='jump-right' transition-next='jump-left' transition-duration='300'").classes(add="grow flex flex-col q-pa-none w-full bg-inherit rounded shadow-md shadow-blue-500 animate__animated animate__fadeIn") as carousel:
        with carousel.add_slot("default"):
          with ui.carousel_slide(name="appointments").classes(add="q-pa-none p-0.5 gap-0 w-full h-full rounded light-blur"):
            with html.div().classes(add="w-full h-full ring-md ring-blue-500 shadow-md shadow-blue-500 blue-blur relative") as self.appointments_pad:
              AppointmentsManager(user=self.user,parent=self)

          with ui.carousel_slide(name="clients").classes(add="q-pa-none p-0.5 gap-0 w-full h-full rounded light-blur"):
            ClientsManager(user=self.user)

      #Controls
      ##Large Screen
      with html.div().classes(add="lg-show w-full py-1 text-center"):
        ui.toggle(options=["clients","appointments"]).props(add="glossy size='lg' toggle-color='bg-inherit' toggle-text-color='sky-500' text-color='yellow-500'").classes(add="bg-[#07004d] rounded-full ring-1 ring-blue-500 shadow-md shadow-sky-600 text-bold").bind_value(carousel)
      ##Small Screen
      with html.div().classes(add="lg:hidden w-full"):
        ui.toggle(options=["clients","appointments"]).props(add="glossy spread size='lg' toggle-color='bg-inherit' toggle-text-color='sky-500' text-color='yellow-500'").classes(add="w-full bg-[#07004d] rounded-none text-bold").bind_value(carousel)


class NursingManager():
  """Displays UI for nursing utilities"""

  def __init__(self,user):
    #DATA
    self.user = user

    #UI
    with html.div().classes(add="w-full h-full flex flex-col p-0 gap-1 bg-inherit animate__animated animate__fadeIn") as self.master_container:
      with ui.carousel(value="triage").style(add="overflow-y:hidden;").props(add="animated swipeable transition-prev='jump-right' transition-next='jump-left' transition-duration='300'").classes(add="grow flex flex-col q-pa-none w-full bg-inherit rounded shadow-md shadow-blue-500 animate__animated animate__fadeIn") as carousel:
        with carousel.add_slot("default"):
          with ui.carousel_slide(name="triage").classes(add="q-pa-none p-0.5 gap-0 w-full h-full rounded light-blur"):
            TriageManager(user=self.user)

          with ui.carousel_slide(name="dispensing").classes(add="q-pa-none p-0.5 gap-0 w-full h-full rounded light-blur"):
            DispensingManager(user=self.user)

      #Controls
      ##Large Screen
      with html.div().classes(add="lg-show w-full py-1 text-center"):
        ui.toggle(options=["triage","dispensing"]).props(add="glossy size='lg' toggle-color='bg-inherit' toggle-text-color='sky-500' text-color='yellow-500'").classes(add="bg-[#07004d] rounded-full ring-1 ring-blue-500 shadow-md shadow-sky-600 text-bold").bind_value(carousel)
      ##Small Screen
      with html.div().classes(add="lg:hidden w-full"):
        ui.toggle(options=["triage","dispensing"]).props(add="glossy spread size='lg' toggle-color='bg-inherit' toggle-text-color='sky-500' text-color='yellow-500'").classes(add="w-full bg-[#07004d] rounded-none text-bold").bind_value(carousel)


class ClinicianServicesManager():
  """A class of UI for managing consultations"""

  def __init__(self,user):
    #DATA
    self.user = user
    
    #UI
    with html.div().classes(add="w-full h-full flex flex-col p-0 gap-1 bg-inherit animate__animated animate__fadeIn"):
      with ui.carousel(value="consults").style(add="overflow-y:hidden;").props(add="animated transition-prev='jump-right' transition-next='jump-left' transition-duration='100'").classes(add="grow flex flex-col q-pa-none w-full bg-inherit rounded-none shadow-sm shadow-blue-500 animate__animated animate__fadeIn") as carousel:
        with carousel.add_slot("default"):
          #Consults
          with ui.carousel_slide(name="consults").classes(add="q-pa-none gap-0 w-full h-full p-0 rounded-none bg-sky-100 flex flex-col"):
            ConsultationsManager(user=self.user)
              
          with ui.carousel_slide(name="procedures").classes(add="q-pa-none gap-0 w-full h-full p-0 rounded-b bg-sky-100 flex flex-col"):
            ProceduresManager(user=self.user)
          
          with ui.carousel_slide(name="appointments").classes(add="q-pa-none p-0.5"):
            with html.div().classes(add="w-full h-full"):
              AppointmentsManager(user=self.user)

      #Controls
      #Controls
      ##Large Screen
      with html.div().classes(add="lg-show w-full py-1 text-center"):
        ui.toggle(options=["consults","procedures","appointments"]).props(add="glossy size='lg' toggle-color='bg-inherit' toggle-text-color='sky-500' text-color='yellow-500'").classes(add="bg-[#07004d] rounded-full ring-1 ring-blue-500 shadow-md shadow-sky-600 text-bold").bind_value(carousel)
      ##Small Screen
      with html.div().classes(add="lg:hidden w-full"):
        ui.toggle(options=["consults","procedures","appointments"]).props(add="glossy spread size='lg' toggle-color='bg-inherit' toggle-text-color='sky-500' text-color='yellow-500'").classes(add="w-full bg-[#07004d] rounded-none text-bold").bind_value(carousel)



