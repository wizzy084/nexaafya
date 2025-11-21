"""A module for constructing main page and page layouts"""
#GENERAL IMPORTS
import asyncio

#NiceGUI IMPORTS
from nicegui import html,ui

#APP IMPORTS
from services.provider.admin.models import User
from services.provider.admin.db import update_login

#UIX IMPORTS
from .configs import HEAD_LINKS,META_TAGS,BODY_LINKS
from .reception.widgets import *
from .consultation.widgets import *
from .imaging.widgets import *
from .nursing.widgets import *
from .management.widgets import ManagementDisplay
from .tools.animations import *
from .tools.widgets import Login



#BASE PAGE
class Page():
  """A class to construct a page layout for the admin panel"""

  def __init__(self,user:User=None,page_content=None,credentials:dict|None=None):
    
    #PAGE SETUP
    self.credentials,self.page_content,self.user = credentials,page_content,user
    ui.query('.nicegui-content').classes(f"absolute-full h-full overflow-y-auto overflow-x-hidden p-0 gap-0 {'dashboard-bg' if user else 'login-bg'} ")
    self.Metadata()
    self.Notifications()

    #USER DISPLAY
    if user and user.active:
      self.PageHeader()
      ui.separator().classes(add="#05002b")
      self.MainPageContent()

    #LOGIN DISPLAY
    else:
      with html.div().style(add="width:100%;height:100%;").classes(add=""):
        #Content
        with html.div().style(add="width:100%;height:100%;overflow-y:hidden;").classes(add="relative flex flex-row justify-center content-center"):
          Login()
    
  #PAGE SETUP
  def Metadata(self):
    """Inserts meta tags in the head of HTML document rendered by this class"""

    for META_TAG in META_TAGS:
      ui.add_head_html(code=META_TAG)
      
    for HEAD_LINK in HEAD_LINKS:
      ui.add_head_html(code=HEAD_LINK)
    
    for BODY_LINK in BODY_LINKS:
      ui.add_body_html(code=BODY_LINK)
  
  def Notifications(self):
    """Displays popup notification with name of user and contextual message"""
    if self.credentials:
      if self.credentials["user"]:
        if self.credentials["valid"]:
          user = self.credentials["user"]
          if user.active:
            if not self.credentials["logged"]:
              ui.notify(message=f"Welcome back {user.title.capitalize()}. {user.first_name.capitalize()} {user.last_name.capitalize()}",caption="Have a nice day with us!",timeout=5000,icon="fas fa-check-double fa-lg",color="light-blue-7",textColor="white",type="positive",position="top")
          else:
            ui.notify(message="Inactive Account!",caption="Contact Hospital Administration",progress=True,timeout=5000,icon="fas fa-circle-exclamation fa-beat-fade",textColor="white",type="secondary",position="top")
        else:
          ui.notify(message="Invalid password!",caption="Try Again or Contact System Admin",progress=True,timeout=3000,icon="fas fa-circle-exclamation fa-beat-fade",textColor="black",type="warning",position="top")
      else:
        ui.notify(message="No User Found!",caption="Check your username!",timeout=3000,icon="fas fa-circle-exclamation fa-beat-fade",textColor="white",type="negative",position="top")

  #FUNCTIONALITIES
  def user_icon(self,user:User)-> str:
    """A function to set 'user-slash' icon if no user:user is provided in AdminProfile function in widgets.py"""

    if user:
      if "doctor" in user.roles:
        return "user-doctor"
      elif "nurse" in user.roles or user.gender == "female":
        return "user-nurse"
      else:
        return "user-tie"
    else:
      return "user-large-slash"

  def dropdown_admin_icon(self,user:User)-> str:
    """A function to set 'user-slash' icon if no user:user is provided in AdminProfile function in widgets.py"""

    if user:
      return "user"
    else:
      return "user-large-slash"
  
  def dropdown_guest(self,user:User) -> str:
    """A function to set 'Guest' as username if no user:User is provided in AdminProfile function in widgets.py"""
  
    if user:
      if "doctor" in user.roles:
        return f"Dr. {user.username}, {user.qualification}"
      else:
        return f"{user.username}, {user.qualification}"
    else:
      return "Guest"

  def department(self,user:User):
    """Returns a string of department name of the user"""

    if user:
      if "director" in user.roles:
        return "administration"
      else:
        if "nurse" in user.roles:
          return "nursing"
        elif "radiographer" in user.roles or "radiologist" in user.roles:
          return "imaging"
        elif "receptionist" in user.roles:
          return "reception"
        elif "doctor":
          return "consultation"
    else:
      return "public"

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

      #Site Navigation
      with html.div().classes(add="w-full pb-0.5 pr-1.5 flex flex-row justify-center"):
        self.PageNavigation()

  def PageNavigation(self):
    """Returns display for page navigation"""
    
    ui.separator().classes(add="w-full bg-[#09026f]")
    with html.div().classes(add="w-full p-1 flex flex-row justify-between"):
      #Tabs
      with html.div().classes(add="grow flex flex-row justify-between lg:justify-center"):
        with ui.tabs().props(add="inline-label dense narrow-indicator align='center'").classes(add="w-fit text-yellow-500 text-bold") as self.tab_header:
          #Manager
          if "director" in self.user.roles:
            self.services = ui.tab("services",icon="fas fa-stethoscope").props(add="").classes(add="hover:scale-[1.1]")
            self.management = ui.tab("management",icon="fas fa-briefcase").classes(add=" text-xl hover:scale-[1.1]")
          #Reception
          elif "receptionist" in self.user.roles:
            self.clients = ui.tab(name="clients",icon="fas fa-users-rectangle").classes(add="hover:scale-[1.1]")
            self.reports = ui.tab("reports",icon="fas fa-file-lines").classes(add="hover:scale-[1.2]")
          #Doctor
          elif "doctor" in self.user.roles:
            self.services = ui.tab("services",icon="fas fa-stethoscope").classes(add="hover:scale-[1.1]")
            self.reports = ui.tab("reports",icon="fas fa-file-lines").classes(add="hover:scale-[1.1]")
          #Radiology
          elif "radiographer" in self.user.roles or "radiologist" in self.user.roles:
            self.studies = ui.tab(name="studies",icon="fas fa-x-ray").classes(add="hover:scale-[1.1]")
            self.reports = ui.tab("reports",icon="fas fa-file-lines").classes(add="hover:scale-[1.1]")
          #Nurse
          elif "nurse" in self.user.roles:
            self.nursing_services = ui.tab(name="services",icon="fa-solid fa-heart-pulse").classes(add="hover:scale-[1.1]")
            self.stores = ui.tab(name="stores",icon="fas fa-house-medical").classes(add="hover:scale-[1.1]")
            self.reports = ui.tab("reports",icon="fas fa-file-lines").classes(add="hover:scale-[1.1]")
      #User Profile
      with html.div().classes(add=""):
        self.AdminProfile(user=self.user)

  def MainPageContent(self):
    """Returns a display of page content"""

    if self.page_content:
      if "director" in self.user.roles:
        self.page_content(user=self.user,tab_header=self.tab_header,tab_header_labels=[self.services,self.management])
      elif "receptionist" in self.user.roles or "super" in self.user.roles:
        self.page_content(user=self.user,tab_header=self.tab_header,tab_header_labels=[self.clients,self.reports])
      elif "doctor" in self.user.roles:
        self.page_content(user=self.user,tab_header=self.tab_header,tab_header_labels=[self.services,self.reports])
      elif "radiographer" in self.user.roles or "radiologist" in self.user.roles:
        self.page_content(user=self.user,tab_header=self.tab_header,tab_header_labels=[self.studies,self.reports])
      elif "nurse" in self.user.roles:
        self.page_content(user=self.user,tab_header=self.tab_header,tab_header_labels=[self.nursing_services,self.stores,self.reports])
      else:
        self.page_content(user=self.user)

  def AdminProfile(self,user):
    """A function to construct a widget to notify Admin Profile"""

    #DROPDOWN BUTTON ON THE PAGE
    with ui.dropdown_button(color="#152046").props(add=f"glossy transition-show='jump-left' transition-hide='jump-right' transition-duration='500'" if user else "disable-dropdown").classes("py-0 rounded-full ring-1 ring-yellow-400 hover:shadow-sm hover:shadow-yellow-500 text-yellow-500") as profile_dropdown:
      #Label
      with profile_dropdown.add_slot("label"):
        with html.div().classes(add="rounded-l-full flex flex-row gap-x-2 text-yellow-500"):
          #Icon/Image
          with html.div().classes(add="flex flex-col justify-center p-1 "):
            html.span().classes(add=f"fas fa-{self.user_icon(user)} fa-xl md:fa-2xl")
          with html.div().classes(add="show-hide h-full"):
            #Title & Name
            with html.div().classes(add="w-full text-md text-bold uppercase"):
              ui.label(f"{user.title}. {user.last_name}, {user.designation}").classes(add="w-full text-center")
            #Allocation/department
            with html.div().classes(add="w-full text-xs uppercase italic text-yellow-200"):
              ui.label(self.department(user)).classes(add="w-full text-center")

      #User details
      with profile_dropdown.add_slot("default"):
        with html.div().classes(add="w-full bg-sky-50 flex flex-col gap-3"):
          if user:
            with html.div().style(add="min-width:40%;").classes(add="flex flex-row p-1 gap-1"):
              #Photo
              with html.div().classes(add="size-16 rounded-full ring-1 ring-[#152046] shadow-md shadow-[#152046]"):
                html.strong().classes(add=f"w-full h-full py-1 rounded-full bg-blue-50 text-[#152046] text-center text-5xl fas fa-{self.user_icon(user)}")
              #Working details
              with html.div().classes(add="grow grid grid-cols-1 gap-2 rounded-r p-1 bg-inherit"):
                #Name
                ui.label(text=f"{self.user.title.capitalize()}. {self.user.first_name.capitalize()} {self.user.middle_name.capitalize()} {self.user.last_name.capitalize()}").classes(add="w-full px-1.5 bg-inherit rounded shadow-sm shadow-[#152046] text-bold text-lg text-[#152046] ")
                #Designation & Title
                with html.div().classes(add="w-full"):
                  ui.label(self.user.roles[-1].title()).classes(add="w-fit p-1 ring-1 ring-blue-200 text-bold text-sm italic text-gray-800")
              
            #Logout functionality
            with html.form().props(add="action='/' target='_parent'").classes(add="w-fulll py-3 flex flex-row justify-center"):
              ui.separator().classes(add="w-full my-3")
              ui.button(text="logout",icon="fas fa-power-off",color="gray-900",on_click=lambda e:update_login({"login_id":self.user.logins[-1].login_id})).props(add="glossy type='submit'").classes(add="rounded ring-1 ring-offset-2 ring-red-500 text-bold text-red-500 text-lg")

  def SiteTitle(self):
    """A function to construct a VERO title for the admin panel"""

    with html.strong().props(add="style='font-family:Helvetica'").classes(add="small-caps text-2xl lg:text-4xl text-bold text-yellow-500"):
      for letter in ["Future","Specialized","Dental","Clinic"]:
        ui.label(text=letter).style(add="text-shadow:2px 2px #505050;").classes("inline mr-2 ")


#DASHBOARD
class Dashboard():
  """A class to display the user dashboard"""

  def __init__(self,user:User,tab_header,tab_header_labels:list):
    """Constructor method for Dashboard"""
    #DATA
    self.user = user
    
    #
    with html.div().classes(add="w-full h-full overflow-hidden bbg-inherit"):
      #Stats for VERO usage
      with ui.tab_panels(tabs=tab_header,value=tab_header_labels[0]).props(add="animated infinite transition-prev='jump-right' transition-next='jump-left' transition-duration='300'").classes(add="h-full bg-inherit"):
        #Director
        if "director" in user.roles:
          #Services
          with ui.tab_panel(name=tab_header_labels[0]).classes(add="h-screen p-0 gap-0.5 bg-inherit"):
            ServicesManagementDisplay(user=self.user)
          #Management
          with ui.tab_panel(name=tab_header_labels[1]).classes(add="h-screen w-screen p-0 gap-0.5 bg-sky-100"):
            ManagementDisplay(self.user)
      
        #Reception
        elif "receptionist" in user.roles:
          #Clients
          with ui.tab_panel(name=tab_header_labels[0]).classes(add="h-screen p-0 gap-0.5 bg-inherit"):
            ClientsManagementDisplay(user=self.user)
          #Reports
          #with ui.tab_panel(name=tab_header_labels[1]).classes(add="h-screen p-0 gap-0.5 bg-inherit"):
          #  ReportsDisplay()
        
        #Doctor
        elif "doctor" in user.roles:
          #Consultations
          with ui.tab_panel(name=tab_header_labels[0]).classes(add="h-screen p-0 gap-0.5 bg-inherit"):
            ServicesManagementDisplay(user=user)
          #Reports
          #with ui.tab_panel(name=tab_header_labels[1]).classes(add="h-screen p-0 gap-0.5 bg-inherit"):
          #  ClinicianReportsManagementDisplay()
        
        #Radiology
        elif "radiographer" in user.roles:
          #Studies
          with ui.tab_panel(name=tab_header_labels[0]).classes(add="h-screen p-0 gap-0.5 bg-inherit"):
            StudiesManagementDisplay(user=user)
          #Resources
          #with ui.tab_panel(name=tab_header_labels[1]).classes(add="h-screen p-0 gap-0.5 bg-inherit"):
           # ui.label("Resources!!")
          #Reports
          #with ui.tab_panel(name=tab_header_labels[1]).classes(add="h-screen p-0 gap-0.5 bg-inherit"):
          #  ImagingReportdisplay(user=user)
        
        #Nurse
        elif "nurse" in user.roles:
          #Services
          with ui.tab_panel(name=tab_header_labels[0]).classes(add="h-screen p-0 gap-0.5 bg-inherit"):
            NursingServicesManagementDisplay(user=user)
          #Stores
          with ui.tab_panel(name=tab_header_labels[1]).classes(add="h-screen p-0 gap-0.5 bg-inherit"):
            StoresManagementDisplay(user=user)
            pass
          #Orders & Reports
          #with ui.tab_panel(name=tab_header_labels[2]).classes(add="h-screen p-0 gap-0.5 bg-inherit"):
          #  PharmacyReportDisplay(user=user)
        
        

