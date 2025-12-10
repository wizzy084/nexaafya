
#GENERAL IMPORTS
import asyncio,calendar,json,math,random,time as time_delay,types,uuid
from collections import namedtuple
from pathlib import Path
from datetime import date,datetime,timedelta
from nicegui import app,html,ui

#SERVICES IMPORTS
from services.provider.admin import constants
from services.provider.admin.db import *
from services.provider.admin.constants import *
from services.provider.admin.processor import *
from services.provider.clients import db as clients_db
from services.provider.admin import db as admin_db
from services.provider.admin import processor as admin_processor
from services.provider.clients import processor as clients_processor
from services.provider.clients.processor import get_appointments,get_clients,get_active_visits,get_consultation_diagnoses

#UIX IMPORTS
from .components import *
from ._snippets import *



#WIDGETS
class Login():
  """"""

  def __init__(self,credentials=None):
    #DATA
    self.credentials = credentials
    self.data()


    #UI
    if self.credentials:
      with html.div().classes(add="login-blur w-[75%] lg:w-[60%] ring-1 ring-green-900 rounded shadow-md shadow-green-600 animate__animated animate__fadeIn animate__slow flex flex-col") as self.master_panel:
        #Large Screen
        with html.div().classes(add="rounded grow w-full lg-flex flex-col"):
          with ui.splitter(value=50).props(add="before-class='rounded-l' after-class='rounded-r' separator-class='bg-gradient-to-b from-sky-600 to-green-600'").classes(add="grow w-full rounded") as splitter:
            #Posters
            with splitter.before:
              with html.div().classes(add="w-full h-full rounded-l bg-black") as self.noticeboard:
                self.LoginPosters()
            
            #Login
            with splitter.after:
              with html.div().classes(add="w-full h-full rounded-r flex flex-col justify-between items-center gap-1") as self.login_display:
                self.LoginForm()
          
        #Small Screen
        with html.div().classes(add="lg:hidden grow rounded w-full flex flex-col"):
          with ui.splitter(value=1).props(add="after-class='rounded' separator-class='bg-inherit'").classes(add="grow w-full rounded") as splitter:
            #Login
            with splitter.after:
              with html.div().classes(add="w-full h-full rounded flex flex-col justify-between items-center gap-1") as self.login_display:
                self.LoginForm()


  #FUNCTIONALITIES
  def data(self):
    #POSTERS
    login_posters_path = Path("./uix/web/assets/images/login")
    self.login_posters =[img_poster for img_poster in [poster for poster in login_posters_path.iterdir() if login_posters_path.exists() and login_posters_path.is_dir()] if img_poster.suffix.lower() in [".png",".jpg"]]

  def login(self,credentials:dict):
    """"""
    
    if credentials["username"] and credentials["password"]:
      #STORAGE
      app.storage.user.update(credentials)

      #NAVIGATE
      ui.navigate.reload()

  def LoginPosters(self):
    """"""
    #UI
    self.noticeboard.clear()
    with self.noticeboard:
      with ui.carousel(value=random.choice(self.login_posters).name).props(add="animated autoplay infinite swipeable transition-prev='jump-right' transition-next='jump-right' transition-duration='3000'").style(add="overflow:hidden;").classes(add="w-full lg-show grow q-pa-none bg-inherit") as carousel:
        for login_poster in self.login_posters:
          with ui.carousel_slide(name=login_poster.name).classes(add="bg-inherit p-0"):
            with html.picture().classes(add="w-full h-full"):
              ui.image(source=login_poster).classes(add="w-full h-full")
  
  def LoginForm(self):
    """"""
    #DATA
    credentials = {"username":self.credentials.username,"password":""}

    #FXS
    def password_input_autofocus():
      return "autofocus" if self.credentials.exists and not self.credentials.password_match else "" 

    #UI
    self.login_display.clear()
    with self.login_display:
      #Title
      with html.section().classes(add="w-full pb-3 flex flex-col gap-3"):
        with html.div().classes(add="py-3 text-center"):
          BrandName(size="text-5xl")
      
      ui.space()

      #Header
      ui.label("STAFF LOGIN").style(add="").classes(add="select-none text-2xl text-sky-200 font-bold lg:text-3xl")

      #Login Form
      with html.form().props(add="onsubmit='event.preventDefault();'").classes(add="w-full rounded-sm flex flex-col items-center content-center gap-5 py-5"):
        #Username Input
        with ui.input(label="USERNAME").props(add="hide-bottom-space required stack-label standout outlined label-color='#07004d' bg-color='light-blue-1' input-class='text-base text-blue-10 font-medium italic' type='text' id='username' name='username'").classes(add="w-52").bind_value(credentials,"username",forward=lambda username:username.strip() if username else "") as username_input:
          with username_input.add_slot("prepend"):
            ui.icon(name="fa-solid fa-user fa-sm").classes(add="m-0 mr-2 text-harmony")
            ui.separator().props(add="vertical")

        #Password Input
        with ui.input(label="PASSWORD",password_toggle_button=True).props(add=f"{ password_input_autofocus()} hide-bottom-space required stack-label standout outlined label-color='#07004d' color='light-blue-9' bg-color='light-blue-1' input-class='text-base text-blue-10 font-medium italic' type='password' id='password' name='password'").classes(add="w-52").bind_value(credentials,"password",forward=lambda password:password.strip() if password else "") as password_input:
          with password_input.add_slot("prepend"):
            ui.icon(name="fa-solid fa-user-lock fa-sm").classes(add="m-0 mr-2 text-harmony")
            ui.separator().props(add="vertical")

        #Submit button
        with html.span():
          ui.button(text="log in",color="",on_click=lambda e:self.login(credentials)).props(add="dense glossy padding='sm' type='submit'").classes(add="w-32 bg-harmony shadow-sm shadow-green-500 text-2xl text-sky-200")
        
      #Company name
      with html.section().classes(add="w-full px-1 flex flex-row justify-end"):
        CompanyName()

#RECEPTION
class ClientsManager():
  """A class for registratio of clients, new + revisits"""

  def __init__(self,user=None):
    #DATA
    self.user = user
    self.initial_data()

    #UI
    with html.div().classes(add="w-full h-full flex flex-col rounded"):
      #Header
      with html.header().classes(add="w-full pl-0 pr-2 flex flex-col lg:flex-row justify-between items-center rounded-t bg-[#07004d]"):
        with html.section().classes(add="w-full lg:w-fit flex flex-row gap-1 items-center"):
          #Registration button
          #Small screen           
          ui.button(text="",icon="fa-solid fa-circle-plus",color="",on_click=lambda e:self.ClientDialog()).classes(add="lg:hidden bg-inherit p-1 text-lg text-yellow-500")
          #Large screen
          ui.button(text="",icon="fa-solid fa-circle-plus fa-md",color="",on_click=lambda e:self.ClientDialog()).classes(add="lg-show bg-inherit p-1 text-lg text-yellow-500")

          ui.label(text="CLIENTS DASHBOARD").style(add="text-shadow:2px 2px #505050;").classes(add="grow bg-inherit text-yellow-500 text-xl lg:text-2xl text-bold")
          
        #Stats
        with html.section().classes(add="w-full lg:w-fit bg-inherit"):
          with html.div().classes(add="px-3") as self.stats_panel:
            self.ClientsStats()
          
      #Body
      with html.div().classes(add="grow w-full bg-sky-50 rounded-b flex flex-col") as self.clients_listing_panel:
        self.ClientsListing()

  def initial_data(self):
    self.basics = get_facility_data()
    self.consultants = [staff for staff in get_staffs(short=True) if "doctor" in staff.roles]
    self.services = {
      "Consultation":["consultant",[service.name.split(" ")[0] for service in get_services() if service.type == "consultation"]],
      "Imaging":["imaging study",[service.name for service in get_services() if service.type == "imaging"]],
      "Procedure":["procedure",[service.name for service in get_services() if service.type == "procedure"]]
    }
    self.raw_clients = get_clients()
    self.visited_clients = sorted([client for client in self.raw_clients if client.visits],key=lambda client:self.last_visit(client).start_time,reverse=True)
    self.new_clients = sorted([client for client in self.raw_clients if not client.visits],key=lambda client:client.created_on,reverse=True)
    self.clients = self.new_clients + self.visited_clients

  def last_visit(self,client):
    """Returns the last visit of client as a namedtuple object"""

    return sorted(client.visits,key=lambda visit:visit.start_time,reverse=True)[0]

  def payment_status(self,visit:dict):
    """Returns a string representing payment status of services"""

    statuses = set()

    consultations = visit["consultations"]
    anthropometrics = visit["anthropometrics"]
    vitals =  visit["vital_signs"]
    labs = visit["labs"]
    imagings = visit["imagings"]
    procedures = visit["procedures"]
    surgeries = visit["surgeries"]
    medications = visit["medications"] + visit["medical_items"]
    nonpharmacologicals = visit["nonpharmacologicals"]

    all_services = consultations + imagings + procedures + medications
    
    for service in all_services:
      if service["payment"]["paid"] and not service["payment"]["billed"]:
        statuses.add("paid")
      if service["payment"]["billed"] and not service["payment"]["paid"]:
        statuses.add("billed")
      if not service["payment"]["billed"] and not service["payment"]["paid"] and not service["payment"]["cancelled"]:
        statuses.add("not paid")
      if service["payment"]["cancelled"]:
        statuses.add("cancelled")
    
    if len(statuses) == 1:
      for status in statuses:
        return status.title()
    else:
      return "Partial"
    
  def _services(self,visit):
    consultations = visit.consultations
    anthropometrics = visit.anthropometrics
    vitals =  visit.vital_signs
    labs = visit.labs


    imagings = visit.imagings
    done_imagings = [imaging for imaging in imagings if imaging.processed]
    not_done_imagings = [imaging for imaging in imagings if not (imaging.cancelled or imaging.processed)]
    cancelled_imagings = [imaging for imaging in imagings if imaging.cancelled]

    procedures = visit.procedures
    done_procedures = [procedure for procedure in procedures if procedure.done]
    not_done_procedures = [procedure for procedure in procedures if not (procedure.done or procedure.cancelled)]
    cancelled_procedures = [procedure for procedure in procedures if procedure.cancelled]

    medicines = visit.medications
    dispensed_medicines = [medicine for medicine in medicines if medicine.dispensed]
    not_dispensed_medicines = [medicine for medicine in medicines if not (medicine.dispensed or medicine.cancelled)]
    cancelled_medicines = [medicine for medicine in medicines if medicine.cancelled]

    all_services = consultations + imagings + procedures + medicines
    paid_services = [service for service in all_services if service.payment.paid]
    billed_services = [service for service in all_services if service.payment.billed and not service.payment.cancelled]
    unpaid_services = [service for service in all_services if not (service.payment.paid or service.payment.billed)]
    cancelled_services = [service for service in all_services if service.payment.cancelled]
    services = unpaid_services + billed_services + paid_services + cancelled_services

    return {
      "services":{"all":services,"paid":paid_services,"billed":billed_services,"unpaid":unpaid_services,"cancelled":cancelled_services},
      "consultation":consultations[0] if consultations else None,
      "imagings":{"all":imagings,"done":done_imagings,"not_done":not_done_imagings,"cancelled":cancelled_imagings},
      "procedures":{"all":procedures,"done":done_procedures,"not_done":not_done_procedures,"cancelled":cancelled_procedures},
      "medicines":{"all":medicines,"done":dispensed_medicines,"not_done":not_dispensed_medicines,"cancelled":cancelled_medicines}
    }

  def formatted_services(self,services):
    """A method to format services in a form presentable in payments dialog"""
    formatted_services = []

    for service in services:
      service = service._asdict()

      #Consultation
      if "consultant_id" in service:
        service["service_id"] = service["consultation_id"]
        service["attendee_id"] = self.user.username
        service["done"] = service["initiated"]
        service["done_on"] = service["clinical_history"].history_time
        service["done_by"] = service["consultant_id"]
        service["cancelled"] = False
        service["service_time"] = service["start_time"]

      #Imaging
      if "study" in service:
        service["service_id"] = service["imaging_id"]
        service["name"] = service["study"]
        service["done"] = service["processed"]
        service["done_by"] = service["radiographer"]
      if "request_time" in service:
        service["service_time"] = service["request_time"]
        service["done_on"] = service["results_time"]

      #Procedure
      if "ordered_on" in service:
        service["service_id"] = service["procedure_id"]
        service["service_time"] = service["ordered_on"]
        service["done_by"] = service["performer"]

      #Medication
      if "prescribed_on" in service:
        service["service_id"] = service["medication_id"]
        service["service_time"] = service["prescribed_on"]
        service["attendee_id"] = service["prescriber_id"]
        service["done"] = service["dispensed"]
        service["dont_time"] = service["dispensing_time"]
        service["done_by"] = service["dispenser_id"]
      
      formatted_services.append(service)

    return formatted_services

  def fetch_insured_client(self,data):
    #Fetching data from API
    client_data = clients_processor.fetch_insured_client(data)
  
    #Notification & Intergration
    with self.id_number_input.add_slot("append"):
      if client_data:
        ui.icon(name="fas fa-user-check",color="green-600").classes(add="mx-3")
        #Feeding data to registration form
        for var,value in client_data.items():
          self.client_data[var] = value.capitalize()
      else:
        #Indication of failure to fetch user from insurance database/API
        ui.icon(name="fas fa-user-xmark",color="red-600").classes(add="mx-3")
        ui.notify(f"User not found in {data['scheme'].upper()} database! \n"
        "Try the following: \n"
        "1. Recheck ID Type or ID Number and try again. \n" 
        f"2. If you are sure the user is insured, advise the client to contact {data['scheme'].upper()} offices for clarification.",
        position="top",type="negative",multi_line=True,classes="multi-line")
  
  def initiate_visit(self,visit_data:dict):
    """A method called from the dialog and create a row in 'visit' table"""
    
    #Visit
    visit = {
      "client_id":visit_data["client_id"],
      "visit_id":visit_data["visit_id"].lower(),
      "payment_mode":visit_data["payment_mode"].lower(),
      "appointment_id":visit_data["appointment_id"].lower() if visit_data["appointment_id"] else None,
      "package":visit_data["package"],
      "attendee_id":self.user.username,
    }
    
    #Service & Payment
    selected_service = [service for service in get_services() if service.name.startswith(visit_data["service_option"].lower())][0]
    selected_service_scheme = [scheme for scheme in selected_service.schemes if scheme.scheme_name == visit_data["payment_mode"].lower()][0]
    if selected_service_scheme.active:
      service_prices = [price for price in selected_service_scheme.prices if price.active][0]
    else:
      ui.notify(message=f"Visit cannot be started via {visit_data['payment_mode'].upper()}",caption=f"Try another payment mode!",type="warning",position="top")

    #CONSULTATION
    if selected_service.type == "consultation":
      
      #Consultation
      consultation = {
        "visit_id":visit_data["visit_id"].lower(),
        "name":selected_service.name,
        "payment":{
          "payment_mode":visit_data["payment_mode"].lower(),
          "cost":service_prices._asdict()[visit_data['package'].lower()],
          "billed":True,
          "billed_amount":service_prices._asdict()[visit_data['package'].lower()],
          "authorization_no":visit_data["authorization_no"]
        },
        "hx":{},"ge":{},"orodental":{},"cns":{},"cvs":{},"rs":{},"abd":{},"gus":{},"mss":{},"derma":{},"dx":{}
      }
      #Triage
      vitals = {
        "visit_id":visit_data["visit_id"].lower(),
        "vitals_id":f"{visit_data['visit_id'].lower()}vs1",
        "payment":{
          "visit_id":visit_data["visit_id"].lower(),
          "payment_id":f"{visit_data['visit_id'].lower()}pay{str(uuid.uuid4()).split('-')[1]}",
          "payment_mode":visit_data["payment_mode"].lower(),
          "cost":0,
          "authorization_no":visit_data["authorization_no"],
          "billed":True
        }
      }
      anthrops = {
        "visit_id":visit_data["visit_id"].lower(),
        "anthropometrics_id":f"{visit_data['visit_id'].lower()}anp1",
        "payment":{
          "visit_id":visit_data["visit_id"].lower(),
          "payment_id":f"{visit_data['visit_id'].lower()}pay{str(uuid.uuid4()).split('-')[1]}",
          "payment_mode":visit_data["payment_mode"].lower(),
          "cost":0,
          "authorization_no":visit_data["authorization_no"],
          "billed":True
        }
      }
      status = clients_db.register_visit(visit)
      clients_db.register_consultation(consultation)
      clients_db.register_triage(triage={"vitals":vitals,"anthropometrics":anthrops},initial=True)
        
    #TRIAGE
    if selected_service.type == "triage":
      vitals = {
        "visit_id":visit_data["visit_id"].lower(),
        "vitals_id":f"{visit_data['visit_id'].lower()}vs1",
        "payment":{
          "visit_id":visit_data["visit_id"].lower(),
          "payment_id":f"{visit_data['visit_id'].lower()}pay{str(uuid.uuid4()).split('-')[1]}",
          "payment_mode":visit_data["payment_mode"].lower(),
          "cost":service_prices._asdict()[f"{visit_data['payment_mode']}_{visit_data['package']}".lower()]/2,
          "authorization_no":None,
          "billed":True
        }
      }
      anthrops = {
        "visit_id":self.visit_data["visit_id"].lower(),
        "anthropometrics_id":f"{self.visit_data['visit_id'].lower()}anp1",
        "payment":{
          "visit_id":self.visit_data["visit_id"].lower(),
          "payment_id":f"{self.visit_data['visit_id'].lower()}pay{str(uuid.uuid4()).split('-')[1]}",
          "payment_mode":self.visit_data["payment_mode"].lower(),
          "cost":service_prices._asdict()[f"{visit_data['payment_mode']}_{visit_data['package']}".lower()]/2,
          "authorization_no":None,
          "billed":True
        }
      }
      status = clients_db.register_visit(visit)
      clients_db.register_triage({"vitals":vitals,"anthropometrics":anthrops})
      
    #LABWORK
    elif selected_service.type == "laboratory":
      pass

    #Notification
    ui.notify(message=status["message"],position=status["position"],type=status["type"])
    
    #UI UPDATE
    self.initial_data()
    _client = [client for client in self.clients if client.client_id == visit_data["client_id"]][0]
    self.VisitsPanel(client=_client)

  def register_appointment(self,appointment:dict):
    """Register a new appointment and store data to database"""

    if appointment["date"].date() == datetime.now().date():
      ui.notify(message="Appointment date is the same as today!",position="top",type="info")
      return

    status = clients_db.register_appointment(appointment)

    #Notification
    ui.notify(message=status["message"],type=status["type"],position="center")
    
    #UI Update
    self.initial_data()
    self.ClientsStats()
    self.ClientsListing()
      
  def register_client(self,edit:bool=False):
    """A method takes 'client_data' and executes a function from clients.processor module to store client's details in the database."""
    client = self.client_data

    #Personal details
    for key,value in client.items():
      if type(value) == str:
        client[key] = value.lower()

    b_day,b_month,b_year = client["birthdate"].split("-")[0],client["birthdate"].split("-")[1],client["birthdate"].split("-")[2]
    client["birthdate"] = datetime.fromisoformat(f"{b_year}-{b_month}-{b_day}")
    
    if edit:
      status = clients_db.update_client(client=client)
    else:
      status = clients_db.register_client(client=client)

    ui.notify(message=status["message"],type=status["type"],position=status["position"])

    #Displays
    updated_client = clients_processor.get_client(client_id=client["client_id"])
    self.ClientPanel(client=updated_client)
    
  def process_payment(self,service,complete:bool=False):
    pay_data = {
      "payment_id":service["payment"].payment_id,
      "visit_id":service["visit_id"],
      "consultation":True if "triages" in service else False,
      "triages":service["triages"] if "triages" in service else None,
      "paid_amount":service["payment"].cost,
      "billed_amount":0,
      "refunded_amount":0,
      "cancelled":False
    }
    status = clients_db.update_payment(pay_data)

    ui.notify(message=status["message"],type=status["type"],position=status["position"])
    
    #UI Update
    self.initial_data()

    visit =[visit for visit in [client for client in self.clients if client.client_id == int(pay_data["visit_id"].split("v")[0])][0].visits if visit.visit_id == pay_data["visit_id"]][0]
    services = self.formatted_services(self._services(visit)["services"]["all"])
    self.PaymentsPanel(services=services)

  #GENERAL DISPLAYS  
  def ClientsStats(self):
    """Displays stats for clients"""
    #DATA
    stats = clients_processor.count_today_visits_and_appointments()

    #UI
    self.stats_panel.clear()
    with self.stats_panel:
      with html.span().classes(add="flex flex-row gap-3 animate__animated animate__zoomIn"):
        #Visits
        with ui.label("VISITS").classes(add="text-sm lg:text-base text-yellow-500 text-bold"):
          ui.label(str(stats.visits)).classes(add="ml-1 inline text-sky-300")
        #Consultations
        with ui.label("APPOINTMENTS").classes(add="text-sm lg:text-base text-yellow-500 text-bold"):
          ui.label(str(stats.appointments)).classes(add="ml-1 inline text-sky-300")

  def ClientsListing(self):
    """Displays aggrid with clients details"""
    #MODS
    def StatusDot(client):
      """A function to return a styled icon based on status of client's last visit"""
      if client.visits:
        cancelled = self.last_visit(client).cancelled
      else:
        cancelled = True

      return f"<span class='fa-solid fa-circle { 'text-red-600' if cancelled else 'text-green-600'}'></span>"
    
    def GenderIcon(client):
      """Returns a styled gender icon based on client's gender"""

      genders = {"male":"mars","female":"venus"}
      colors = {"male":"sky-600","female":"pink-600"}
      return f"<span class='fa-solid fa-{genders[client.gender.lower()]} text-{colors[client.gender.lower()]}'></span>"

    #UI
    self.clients_listing_panel.clear()
    with self.clients_listing_panel:
      if self.clients:
        #Large Screen
        ui.aggrid(
          {
            "columnDefs":[
              {"headerName":"","field":"sno","width":75},
              {"headerName":"CLIENT ID","field":"client_id","filter":"agTextColumnFilter","floatingFilter":True,"width":200},
              {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","floatingFilter":True,"width":350},
              {"headerName":"AGE","field":"age"},
              {"headerName":"GENDER","field":"gender","width":150},
              {"headerName":"ADDRESS","field":"address"},
              {"headerName":"PAYMENT","field":"payment_mode","filter":"agTextColumnFilter"},
              {"headerName":"CARD NO.","field":"card_no","filter":"agTextColumnFilter"},
              {"headerName":"LAST VISIT","field":"last_visit"},
              {"headerName":"STATUS","field":"status","width":150,"cellClassRules":{
                "text-green-600 text-bold":"x == 'Active'",
                "text-red-600 text-bold":"x == 'Inactive'"
              }}
            ],
            "rowData":[
              {
                "sno":self.clients.index(client) + 1,
                "client_id":client.client_id,
                "name":f"{client.first_name.capitalize()} {client.middle_name.capitalize() if client.middle_name else ''} {client.last_name.capitalize()}",
                "age":f"{format_age(client.birthdate).split(' ')[0]} {format_age(client.birthdate).split(' ')[1]}",
                "gender":client.gender.capitalize(),
                "address":client.address.title(),
                "payment_mode":client.payment_mode.upper(),
                "card_no":client.card_no if client.card_no else "---",
                "last_visit":format_age(self.last_visit(client).start_time) if client.visits else "---",
                "status":"---" if not client.visits else "Inactive" if self.last_visit(client).cancelled else "Active"
              } for client in self.clients
            ],
          },theme="quartz"
        ).classes(add="lg-show grow w-full animate__animated animate__fadeIn animate__slow").on("cellClicked",lambda e:self.ClientDialog(client=[client for client in self.clients if client.client_id == e.args["data"]["client_id"]][0]))
        
        #Small Screen
        ui.aggrid(
          {
            "columnDefs":[
              {"headerName":"","field":"status","width":75},
              {"headerName":"CLIENT ID","field":"client_id","filter":"agTextColumnFilter","floatingFilter":True,"width":160},
              {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","floatingFilter":True,"width":300},
              {"headerName":"","field":"gender","align":"left","width":75},
              {"headerName":"AGE","field":"age","width":150}
            ],
            "rowData":[
              {
                "status":StatusDot(client),
                "client_id":client.client_id,
                "name":f"{client.first_name} {client.middle_name[0] if client.middle_name else ''} {client.last_name.capitalize()}".title(),
                "age":f"{format_age(client.birthdate).split(' ')[0]} {format_age(client.birthdate).split(' ')[1]}",
                "gender":GenderIcon(client)
              } for client in self.clients
            ],
          },
          html_columns=[0,3],
          theme="quartz"
        ).classes(add="lg:hidden grow w-full animate__animated animate__fadeIn animate__slow").on("cellClicked",lambda e:self.ClientDialog(client=[client for client in self.clients if client.client_id == e.args["data"]["client_id"]][0]))
  
      
      else:
        with html.div().classes(add="grow w-full flex flex-row justify-center items-center text-bold"):
          with html.div().classes(add="flex flex-col items-center"):
            ui.label("No Clients registered!").classes(add="text-2xl text-gray-500 text-bold")
            ui.html(content="<em >Start registering by clicking <strong class='fa-solid fa-circle-plus fa-lg mx-1 text-yellow-600' ></strong> on CLIENTS DASHBOARD</em>",sanitize=False).classes(add="text-base text-gray-400 italic")
  
  def ClientDialog(self,client:dict|None=None):
    """"""
    #UI
    with ui.dialog().props(add=f"transition-show='jump-up' transition-hide='jump-down' transition-duration='100'") as self.client_dialog,html.div().style(add="min-width:75%;min-height:50%;").classes(add="bg-sky-50 flex flex-col"):
      with html.div().classes(add="grow w-full flex flex-col") as self.client_panel:
        self.ClientPanel(client=client)
      
    
    self.client_dialog.open()
  
  def ClientPanel(self,client:dict|None=None):
    """"""
    #DATA
    if client:
      details = {
        "name":f"{client.first_name} {client.middle_name if client.middle_name else ''} {client.last_name}",
        "short_name":f"{client.first_name} {client.middle_name[0] if client.middle_name else ''} {client.last_name}".title(),
        "age":format_age(client.birthdate),
        "gender":client.gender,
        "address":client.address,
        "last_visit":"---" if not client.visits else f"{format_age(self.last_visit(client).start_time)} ago"
      }
    
    def close_dialog():
      self.ClientsStats()
      self.ClientsListing()
      self.client_dialog.close()


    #UI
    self.client_panel.clear()
    with self.client_panel:
      #Header
      with html.div().classes(add="bg-harmony p-1 flex flex-row justify-between"):
        #Client Edit & details
        if client:
          with html.span().classes(add="bg-inherit flex items-center") as self.edit_view_button_panel:
            ui.button(color="",icon="fas fa-user-pen fa-xl",on_click=lambda e:self.ClientDetailsForm(client=client)).props(add="compact").classes(add="bg-inherit text-yellow-500 hover:scale-[1.1]")
          with html.div().classes(add="grow"):
            ClientCard(details=details)
        #New details
        else:
          ui.label(f"CLIENT{ '' if client else ' REGISTRATION'} PANEL").classes(add="p-2 grow text-yellow-500 text-xl lg:text-3xl text-bold text-center")
        ui.button(icon="fa-regular fa-circle-xmark fa-xl",color="",on_click=close_dialog).classes(add="bg-inherit text-red-500 text-bold text-base")
      #Details
      with html.div().classes(add="grow w-full h-full flex flex-col gap-0") as self.client_details_panel:
        #Client
        if client:
          self.VisitsPanel(client=client)
        #New client
        else:
          self.ClientDetailsForm(client=client)
  
  def ClientDetailsForm(self,client:dict|None=None):
    """A method to display dialog with registration form"""
    #DATA
    id_number_types = json.loads(self.basics.id_number_types)
    payment_modes = json.loads(self.basics.active_payment_modes)
    marital_statuses = json.loads(self.basics.marital_statuses)
    occupations = json.loads(self.basics.occupations)

    self.client_data = {
      "client_id":client.client_id if client else clients_processor.format_client_id(),
      "payment_mode":client.payment_mode if client else payment_modes[0],
      "card_no":client.card_no if client else "",
      "first_name":client.first_name.capitalize() if client else "",
      "middle_name":client.middle_name.capitalize() if (client and client.middle_name) else "",
      "last_name":client.last_name.capitalize() if client else "",
      "birthdate":client.birthdate.strftime("%d-%m-%Y") if client else "",
      "gender":client.gender.capitalize() if client else "",
      "marital_status":client.marital_status.capitalize() if client else "",
      "occupation":client.occupation.capitalize() if client else "",
      "address":client.address.capitalize() if client else "",
      "mobile":client.mobile if client else None
    }
    insurance_data = {
      "scheme":self.client.payment_mode if client else payment_modes[0],
      "id_type":"",
      "id_number":self.client_data.card_no if client else ""
      }
    
    #UI
    #Buttons
    if client:
      self.edit_view_button_panel.clear()
      with self.edit_view_button_panel:
        ui.button(color="",icon="fas fa-eye fa-xl",on_click=lambda e:self.VisitsPanel(client=client)).props(add="compact").classes(add="bg-inherit text-yellow-500 hover:scale-[0.9] animate__animated animate__zoomIn")
    #Display
    self.client_details_panel.clear()
    with self.client_details_panel.classes(add=""):
      with html.div().classes(add="w-full h-full flex flex-col lg:grid grid-cols-3 gap-3 bg-sky-100"):
        #Payment
        with html.form().classes(add="lg:col-span-3 w-full grid grid-cols-6 gap-3 p-2 animate__animated animate__fadeIn"):
          #Scheme
          self.scheme_selectable = ui.select(options=json.loads(self.basics.active_payment_modes),label="SCHEME",value=insurance_data["scheme"]).props(add="bordered popup-content-class='uppercase'").classes(add="col-span-3 md:col-span-1 shadow-md shadow-[#07004d] px-2 bg-white rounded-sm text-lg uppercase").bind_value_to(insurance_data,"scheme").bind_value_to(self.client_data,"payment_mode")
          #ID Type
          ui.select(options=id_number_types,label="ID TYPE",value=id_number_types[0]).props(add="bordered popup-content-class='uppercase'").classes(add="col-span-3 md:col-span-1 shadow-md shadow-[#07004d] px-3 bg-white rounded-sm text-lg uppercase").bind_value_to(insurance_data,"id_type").bind_visibility_from(self.scheme_selectable,"value",lambda v: v.lower() != "cash")
          #ID No input
          self.id_number_input = ui.input(label="ID NUMBER").props(add="bordered").classes(add="col-span-4 md:col-span-3  shadow-md shadow-[#07004d] bg-white rounded-sm px-3 text-lg").bind_value(self.client_data,"card_no").bind_visibility_from(self.scheme_selectable,"value",lambda v: v.lower() != "cash")
          #Data Button
          ui.button(text="FETCH CLIENT",color="",on_click=lambda e:self.fetch_insured_client(insurance_data)).props(add="bordered glossy type='button'").classes(add="col-span-2 md:col-span-1 bg-harmony text-yellow-8 text-base text-bold").bind_visibility_from(self.scheme_selectable,"value",lambda v: v.lower() != "cash")

        #Personal details
        with html.form().props(add="").classes(add="lg:col-start-1 lg:col-span-3 grow flex flex-col gap-3 w-full p-2 animate__animated animate__fadeIn"):
          #Client ID
          with ui.label("Client ID").props(add="glossy").classes(add="w-full rounded-sm shadow-md shadow-[#07004d] p-2 small-caps text-2xl text-bold text-gray-500"):
            ui.label().style(add="text-shadow:1px 1px #505050;").classes(add="inline ml-2").bind_text(self.client_data,"client_id")
          #Details
          with html.div().classes(add="w-full grid grid-cols-2 lg:grid-cols-3 gap-3"):
            #First Name
            ui.input(label="FIRST NAME").props(add="bordered stack-label").classes(add="shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value(self.client_data,"first_name")
            #Middle Name
            ui.input(label="MIDDLE NAME").props(add="bordered stack-label").classes(add="shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value(self.client_data,"middle_name")
            #Last Name
            ui.input(label="LAST NAME").props(add="bordered stack-label").classes(add="shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value(self.client_data,"last_name")
            #Birthdate
            with ui.input(label="BIRTHDATE").props(add="bordered readonly stack-label").classes(add="shadow-md shadow-[#07004d] bg-white rounded px-2 text-lg") as bdate_display:
              with ui.dialog() as calendar:
                ui.date(mask="DD-MM-YYYY",on_change=lambda e:calendar.close()).props(add=f"bordered square today-btn color='harmony' event-color='orange' first-day-of-week='1' navigation-max-year-month='{datetime.now().strftime("%Y/%m")}'").bind_value(bdate_display).bind_value(self.client_data,"birthdate")
                with bdate_display.add_slot("append"):
                  ui.icon("fas fa-cake-candles",color="pink-500").on("click",calendar.open)
            #Gender
            ui.select(options=["Male","Female"],value="Female",label="GENDER").props(add="bordered stack-label popup-content-class='uppercase'").classes(add="shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value(self.client_data,"gender")
            #Marital status
            ui.select(options=marital_statuses,label="MARITAL STATUS",value=marital_statuses[0]).props(add=" bordered stack-label popup-content-class='uppercase'").classes(add="shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg uppercase").bind_value(self.client_data,"marital_status")
            #Occupation
            ui.select(options=occupations,label="OCCUPATION",with_input=True).props(add="bordered stack-label popup-content-class='uppercase'").classes(add="shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg uppercase").bind_value(self.client_data,"occupation")
            #Address
            ui.input(label="ADDRESS").props(add="bordered stack-label type='text'").classes(add="shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value(self.client_data,"address")
            #Mobile No
            ui.input(label="MOBILE NO",placeholder="eg.0787000111").props(add="bordered stack-label type='tel' minlength=10 maxlength=10").classes(add="shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value(self.client_data,"mobile")

        #Buttons
        with html.div().classes(add="lg:col-span-3 w-full flex flex-row justify-center p-2 rounded-sm shadow-sm shadow-[#07004d]"):
          ui.button(text="SAVE EDITING" if client else "REGISTER CLIENT",on_click=lambda e:self.register_client(edit=True if client else False),color="#07004d").props(add="glossy type='button'").classes(add="text-yellow-500 text-bold text-lg rounded-md ring-1 ring-blue-400 shadow-md shadow-blue-400")
    
  def ClientMiniDisplay(self,client:dict|None=None,clients:bool=False,visits:bool=False):
    """Displays client details for registered client and registration form for new client"""
    #DATA
    if client:
      details = {
        "name":f"{client['first_name'].capitalize()} {client['middle_name'].capitalize() if client['middle_name'] else ''} {client['last_name'].capitalize()}",
        "short_name":f"{client['first_name'].capitalize()} {client['middle_name'][0].capitalize() if client['middle_name'] else ''} {client['last_name'].capitalize()}",
        "age":format_age(client["birthdate"],short=True),
        "gender":client["gender"].capitalize(),
        "address":client["address"].capitalize(),
        "last_visit":self.last_visit(client)["duration"] if client["visits"] else self.last_visit(client)["time"]
      }

    #UI
    self.master_container.clear()
    with self.master_container.classes(add="bg-sky-100 flex flex-col"):
      #Header
      with html.div().classes(add="bg-[#07004d] flex flex-row justify-between"):
        #Client Edit & details
        if client:
          with html.span().classes(add="bg-inherit flex items-center") as self.edit_view_button_panel:
            ui.button(color="",icon="fas fa-user-pen fa-xl",on_click=lambda e:self.ClientDetailsForm(client=client)).props(add="compact").classes(add="bg-inherit text-yellow-500 hover:scale-[0.9]")
          with html.div().classes(add="grow"):
            ClientCard(details=details)
        #New details
        else:
          ui.label(f"REGISTRATION PANEL").style(add="text-shadow:2px 2px #505050;").classes(add="p-2 grow text-yellow-500 text-3xl text-bold text-center")
        with html.span().classes(add="bg-inherit flex items-center"):
          ui.button(icon="fa-regular fa-circle-xmark fa-xl",color="",on_click=lambda e:self.Carousel(clients=clients,visits=visits)).classes(add="bg-inherit text-red-500 text-bold text-base hover:scale-[0.9]")
      #Body
      with html.div().classes(add="grow w-full flex flex-col gap-0.5") as self.client_details_panel:
        #Client
        if client:
          self.VisitsPanel(client=client,from_clients=clients,from_visits=visits) 
        #New client
        else:
          self.ClientDetailsForm(client=client) 

  def VisitsPanel(self,client:dict,from_clients:bool=True,from_visits:bool=False):
    #DATA
    if client.visits:
      visits = sorted(client.visits,key=lambda visit:visit.start_time,reverse=True)

    #UI
    #Button
    self.edit_view_button_panel.clear()
    with self.edit_view_button_panel:
      ui.button(color="",icon="fas fa-user-pen fa-xl",on_click=lambda e:self.ClientDetailsForm(client=client)).props(add="compact").classes(add="bg-inherit text-yellow-500 hover:scale-[1.1] animate__animated animate__zoomIn")
    
    #Preview visits
    self.client_details_panel.clear()
    with self.client_details_panel.classes(add="flex flex-col gap-0"):
      if client.visits:
        #Visits
        with html.fieldset().classes(add="grow w-full flex flex-col rounded-none bg-inherit p-0.5 shadow-sm shadow-[#07004d] animate__animated animate__fadeIn"):
          html.legend(f"{len(client.visits)} VISIT{'' if len(client.visits) == 1 else 'S'}").classes(add="rounded bg-sky-100 px-3 text-[#07004d] text-xl text-bold")
          with ui.scroll_area().classes(add="grow w-full bg-sky-50 rounded-b") as self.visits_exapansions_panel:
            #Visits
            for visit in visits:
              with html.div().classes(add="w-full") as self.visit_expansion_panel:
                self.VisitExpansion(visit)
                
      else:
        with html.div().classes(add="grow w-full flex flex-row justify-center items-center shadowsm shadow-[#07004d]"):
          ui.label("This client has no recorded visits here!").classes(add="bg-inherit text-gray-400 text-bold text-xl")
      
      #Buttons
      with html.div().classes(add="rounded-b w-full p-2 flex flex-row justify-center gap-5 animate__animated animate__fadeIn"):
        if not client.visits or self.last_visit(client).cancelled:
          ui.button(text="new visit",icon="fas fa-circle-plus fa-xl",color="#07004d",on_click=lambda e:self.NewVisitPanel(client=client)).props(add="bordered dense glossy").classes(add="rounded shadow-md shadow-[#07004d] text-sky-300 text-xl text-bold")    #New Visit
        ui.button(text="appointment",icon="fas fa-circle-plus fa-lg",color="#07004d",on_click=lambda e:self.NewAppointmentPanel(client=client)).props(add="dense glossy").classes(add="rounded shadow-md shadow-[#07004d] text-sky-300 text-xl text-bold")      #Appointments

  def VisitExpansion(self,visit:dict):
    """Shows a dialog for initiating or ending visit"""
    #DATA
    all_services,cancelled_services = self._services(visit)["services"]["all"],self._services(visit)["services"]["cancelled"]
    paid_services,billed_services = self._services(visit)["services"]["paid"],self._services(visit)["services"]["billed"]
    unpaid_services = self._services(visit)["services"]["unpaid"]
    consultation = self._services(visit)["consultation"]
    imagings = self._services(visit)["imagings"]
    procedures = self._services(visit)["procedures"]
    medicines = self._services(visit)["medicines"]
    

    #UI
    self.visit_expansion_panel.clear()
    with self.visit_expansion_panel:
      with ui.expansion(
        text=f"{visit.start_time.strftime('%d %b %Y %H:%M')}".upper(),
        caption=f"{len(all_services):,.0f} Service{'' if len(all_services) == 1 else 's'} {len(all_services) - len(cancelled_services) } Valid {len(cancelled_services):,.0f} Cancelled",
        group="visits_group"
      ).props(add=f"dense icon='fas fa-notes-medical' header-class='rounded p-1 bg-sky-100 {'bg-sky-100 text-sky-900' if visit.cancelled else 'text-green-600'}'").classes(add="w-full my-2 bg-sky-50 rounded shadow-md shadow-[#07004d] text-bold text-xl text-black"):
        with html.div().classes(add="w-full grid gap-3 grid-cols-2 lg:grid-cols-4"):
          #Payments
          with ui.button(color="",on_click=lambda e:self.PaymentsDialog(services=all_services)).props(add="bordered glossy dense").classes(add="w-full p-1 rounded-md bg-harmony shadow-md shadow-[#07004d] flex flex-row gap-5") as payments_button:
            with payments_button.add_slot("default"):
              with html.div().classes(add="w-full grid grid-cols-5"):
                with html.div().classes(add="col-span-4 w-full"):
                  ui.label("PAYMENTS").classes(add="w-full text-start text-sky-500 text-xl text-bold")
                  with html.div().classes(add="w-full flex flex-row"):
                    #Paid
                    ui.chip(text=str(len(paid_services)),icon="fas fa-check",text_color="green",color="").props(add="dense").classes(add=f"{'' if paid_services else 'hidden'} m-0 bg-inherit text-lg text-bold").tooltip("Paid")
                    #Billed
                    ui.chip(text=str(len(billed_services)),icon="fas fa-spinner",text_color="orange",color="").props(add="dense text-color='purple-12'").classes(add=f"{'' if billed_services else 'hidden'} m-0 bg-inherit text-lg text-bold").tooltip("Billed")
                    #Not Paid
                    ui.chip(text=str(len(unpaid_services)),icon="fas fa-xmark",text_color="red",color="").props(add="dense").classes(add=f"{'' if unpaid_services else 'hidden'} m-0 bg-inherit text-lg text-bold").tooltip("Unpaid")
              
                with html.div().classes(add="col-span-1 w-full grid grid-cols-1"):
                  ui.label(len(all_services)).classes(add="rounded-full py-0.5 ring-1 ring-sky-500 shadow-md shadow-sky-500 size-8 self-center text-sky-500 text-bold text-xl")
          #Consultations
          if consultation:
            ui.button(text="CONSULTATION",color="").props(add=f"bordered glossy dense unelevated padding='0px 0px' icon-right='fa-regular {'fa-circle-check' if consultation.initiated else 'fa-circle-xmark'} fa-xs' padding='5px 5px'").classes(add=f"w-full bg-harmony p-0 rounded-md text-{'green-500' if consultation.initiated else 'red-500'} font-semibold text-xl")
          #Imagings
          if imagings["all"]:
            with ui.button(color="").props(add="bordered glossy").classes(add="w-full p-1 rounded-md bg-harmony flex flex-row gap-5") as imagings_button:
              with imagings_button.add_slot("default"):
                with html.div().classes(add="w-full grid grid-cols-5"):
                  with html.div().classes(add="col-span-4 w-full"):
                    ui.label("IMAGINGS").classes(add="w-full text-start text-sky-500 text-xl text-bold")
                    with html.div().classes(add="w-full flex flex-row"):
                      #Processed
                      ui.chip(text=str(len(imagings["done"])),icon="fas fa-check",text_color="green",color="").props(add="dense").classes(add=f"{'' if imagings['done'] else 'hidden'} m-0 bg-inherit text-lg text-bold").tooltip("Processed")
                      #Not Done
                      ui.chip(text=str(len(imagings["not_done"])),icon="fas fa-xmark",text_color="red",color="").props(add="dense").classes(add=f"{'' if imagings['not_done'] else 'hidden'} m-0 bg-inherit text-lg text-bold").tooltip("Not Processed")
                      #Cancelled
                      ui.chip(text=str(len(imagings["cancelled"])),icon="fas fa-ban",text_color="grey",color="").props(add="dense").classes(add=f"{'' if imagings['cancelled'] else 'hidden'} m-0 bg-inherit text-lg text-bold").tooltip("Cancelled")
                
                  with html.div().classes(add="col-span-1 w-full grid grid-cols-1"):
                    ui.label(len(imagings["all"])).classes(add="rounded-full py-0.5 ring-1 ring-sky-500 shadow-md shadow-sky-500 size-8 self-center text-sky-500 text-bold text-xl")
          #Procedures
          if procedures["all"]:
            with ui.button(color="").props(add="bordered glossy").classes(add="w-full p-1 rounded-md bg-harmony flex flex-row gap-5") as procedures_button:
              with procedures_button.add_slot("default"):
                with html.div().classes(add="w-full grid grid-cols-5"):
                  with html.div().classes(add="col-span-4 w-full"):
                    ui.label("PROCEDURES").classes(add="w-full text-start text-sky-500 text-xl text-bold")
                    with html.div().classes(add="w-full flex flex-row"):
                      #Processed
                      ui.chip(text=str(len(procedures["done"])),icon="fas fa-check",text_color="green",color="").props(add="dense").classes(add=f"{'' if procedures['done'] else 'hidden'} m-0 bg-inherit text-lg text-bold").tooltip("Done")
                      #Not Done
                      ui.chip(text=str(len(procedures["not_done"])),icon="fas fa-xmark",text_color="red",color="").props(add="dense").classes(add=f"{'' if procedures['not_done'] else 'hidden'} m-0 bg-inherit text-lg text-bold").tooltip("Not Done")
                      #Cancelled
                      ui.chip(text=str(len(procedures["cancelled"])),icon="fas fa-ban",text_color="grey",color="").props(add="dense").classes(add=f"{'' if procedures['cancelled'] else 'hidden'} m-0 bg-inherit text-lg text-bold").tooltip("Cancelled")
                
                  with html.div().classes(add="col-span-1 w-full grid grid-cols-1"):
                    ui.label(len(procedures["all"])).classes(add="rounded-full py-0.5 ring-1 ring-sky-500 shadow-md shadow-sky-500 size-8 self-center text-sky-500 text-bold text-xl")
          #Pharmacy
          if medicines["all"]:
            with ui.button(color="").props(add="glossy").classes(add="w-full p-1 rounded-md bg-harmony flex flex-row gap-5") as medicines_button:
              with medicines_button.add_slot("default"):
                with html.div().classes(add="w-full grid grid-cols-5"):
                  with html.div().classes(add="col-span-4 w-full"):
                    ui.label("MEDICINES").classes(add="w-full text-start text-sky-500 text-xl text-bold")
                    with html.div().classes(add="w-full flex flex-row"):
                      #Dispensed
                      ui.chip(text=str(len(medicines["done"])),icon="fas fa-check",text_color="green",color="").props(add="dense").classes(add=f"{'' if medicines['done'] else 'hidden'} m-0 bg-inherit text-lg text-bold").tooltip("Dispensed")
                      #Not Dispensed
                      ui.chip(text=str(len(medicines["not_done"])),icon="fas fa-xmark",text_color="red",color="").props(add="dense").classes(add=f"{'' if medicines['not_done'] else 'hidden'} m-0 bg-inherit text-lg text-bold").tooltip("Not Dispensed")
                      #Cancelled
                      ui.chip(text=str(len(medicines["cancelled"])),icon="fas fa-ban",text_color="grey",color="").props(add="dense").classes(add=f"{'' if medicines['cancelled'] else 'hidden'} m-0 bg-inherit text-lg text-bold").tooltip("Cancelled")
                
                  with html.div().classes(add="col-span-1 w-full grid grid-cols-1"):
                    ui.label(len(medicines["all"])).classes(add="rounded-full py-0.5 ring-1 ring-sky-500 shadow-md shadow-sky-500 size-8 self-center text-sky-500 text-bold text-xl")
  
  def NewVisitPanel(self,client:dict,appointment_id:str|None=None):
    """Shows a dialog for initiating or ending visit"""
    #DATA
    def format_visit_id():
      if client.visits:
        return f"{client.client_id}v{int(self.last_visit(client).visit_id.split('v')[1]) + 1}"
      else:
        return f"{client.client_id}v1"

    details = {
      "name":f"{client.first_name} {client.middle_name if client.middle_name else ''} {client.last_name}",
      "short_name":f"{client.first_name} {client.middle_name[0] if client.middle_name else ''} {client.last_name}",
      "age":format_age(client.birthdate,short=True),
      "gender":client.gender,
      "address":client.address,
      "last_visit":format_age(self.last_visit(client).start_time) if client.visits else "---"
    }

    visit_data = {
      "client_id":client.client_id,
      "visit_id":format_visit_id(),
      "appointment_id":appointment_id,
      "payment_mode":"",
      "package":"",
      "service":"",
      "service_option":"",
      "attending_clinician":"",
      "card_no":"",
      "authorization_no":"",
      "auth_button_clicked":False
      }

    payment_options = ["cash"] if client.payment_mode.lower() == "cash" else [client.payment_mode.upper(),"cash"]
    payment_packages = json.loads(self.basics.payment_packages)
    
    #MODS
    def get_authorization_number():
      """Retrives authorization number for insured clients and inserts it into visit_data"""

      auth = clients_processor.authorize_visit({"scheme":visit_data["payment_mode"],"card_no":visit_data["card_no"]})

      ui.notify(message=auth["message"],position="center" if auth["type"] == "negative" else "top",type=auth["type"])
      with self.auth_number.add_slot("append"):
        if auth["type"] == "positive":
          ui.icon(name="fas fa-user-check",color="green-600").classes(add="mx-3")
        else:
          ui.icon(name="fas fa-user-xmark",color="red-600").classes(add="mx-3")
    
      #Binding data
      visit_data["authorization_no"] = auth["auth_no"]
    
    def ServiceOptions(service_category:str):
      """Dynamically loads a selection element for service options based on the service_categgory value"""
      service = service_category
      options = [_service.title() for _service in self.services[service][1]]
      value = self.services[service][1][0].title()
      label = self.services[service][0].upper()

      self.service_options_pad.clear()
      with self.service_options_pad:
        ui.select(options=options,value=value,label=label).classes(add="w-full shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value_to(visit_data,"service_option")

    #UI
    self.client_details_panel.clear()
    with self.client_details_panel:
      #Visit details
      with html.div().classes(add="grow w-full flex flex-col justify-between gap-3 p-1 bg-sky-100"):
        #Services
        with html.div().classes(add="w-full p-1 grid grid-cols-2 gap-3 animate__animated animate__fadeIn"):
          #Service
          with html.div().classes(add="col-span-2 w-full grid grid-cols-2 gap-3"):
            #Service type
            self.service_category = ui.select(options=list(self.services),label="SERVICE",value="Consultation",on_change=lambda e:ServiceOptions(e.value)).classes(add="shadow-md shadow-[#07004d] bg-sky-50 rounded-sm px-2 text-lg").bind_value_to(visit_data,"service")
            #Service Options
            with html.div().classes(add="") as self.service_options_pad:
              ui.select(options=[_service.title() for _service in self.services["Consultation"][1]],value=self.services["Consultation"][1][0].title(),label="CONSULTANT").classes(add="shadow-md shadow-[#07004d] bg-sky-50 rounded-sm px-2 text-lg").bind_value_to(visit_data,"service_option")
            
          #Payment
          with html.div().classes(add="col-span-2 w-full grid grid-cols-2 gap-3"):
            ui.select(options=payment_options,value=payment_options[0],label="PAYMENT MODE").props(add="bordered popup-content-class='uppercase'").classes(add="shadow-md shadow-[#07004d] bg-sky-50 rounded px-2 text-lg uppercase").bind_value_to(visit_data,"payment_mode")   #payment mode
            ui.select(options=payment_packages,value=payment_packages[0],label="PACKAGE").props(add="bordered popup-content-class='uppercase'").classes(add="shadow-md shadow-[#07004d] bg-sky-50 rounded px-2 text-lg uppercase").bind_value_to(visit_data,"package")
            ui.input(label="CARD/NIDA NO",value=client.card_no).props(add="type='text' bordered readonly").bind_visibility_from(visit_data,"payment_mode",lambda v:v != "cash").classes(add="bg-white shadow-md shadow-[#07004d] rounded-sm px-2 text-lg").bind_value_to(visit_data,"card_no")     #Card No
            ui.button(text="authorize",color="#07004d",on_click=get_authorization_number).props(add="bordered glossy").bind_visibility_from(visit_data,"payment_mode",lambda v:v != "cash").classes(add="rounded shadow-md shadow-[#07004d] text-sky-300 text-lg lg:text-xl text-bold")   #Authorize button
            self.auth_number = ui.input(label="AUTHORIZATION NO").props(add="bordered glossy readonly").bind_visibility_from(visit_data,"payment_mode",lambda v:v != "cash").classes(add="col-span-2 w-3/4 justify-self-center bg-white shadow-md shadow-[#07004d] rounded-sm px-2 text-xl text-green-700").bind_value(visit_data,"authorization_no")          #Authorization Number
          
        #Action buttons
        with html.div().classes(add="w-full p-1 flex flex-row justify-center"):
          #Initiate visit
          ui.button(text="start visit",color="#07004d",on_click=lambda e:self.initiate_visit(visit_data=visit_data)).props(add="bordered dense glossy").classes(add="w-auto shadow-md shadow-[#07004d] text-sky-300 text-xl lg:text-2xl text-bold")

  def PaymentsDialog(self,services:dict|None=None):
    #DATA
    if not services:
      ui.notify(message="No payments requested!",type="warning",position="top")
      return
  
    #FXS
    def close_dialog():
      client =  [client for client in self.clients if client.client_id == int(services[0].visit_id.split("v")[0])][0]
      self.VisitsPanel(client=client)
      self.payments_dialog.close()
      
    #UI
    with ui.dialog().props(add=f"transition-show='jump-up' transition-hide='jump-down' transition-duration='500'") as self.payments_dialog,html.div().style(add="min-width:100%;").classes(add="bg-sky-50"):
      #Header
      with html.div().classes(add="bg-[#07004d] p-1 flex flex-row justify-between"):
        #Client Edit & details
        with html.div().classes(add="grow"):
          ui.label("PAYMENTS DASHBOARD").style(add="text-shadow:2px 2px #505050").classes(add="grow text-yellow-500 text-3xl text-bold text-center")
        #Buttons
        with html.div().classes(add="flex flex-col justify-center"):
          ui.button(icon="fa-regular fa-circle-xmark fa-xl",color="",on_click=close_dialog).classes(add="bg-inherit text-red-500 text-bold text-base hover:scale-[0.9]")
      #Details
      with html.div().classes(add="w-full h-full bg-sky-50 rounded-b") as self.payments_panel:
        self.PaymentsPanel(services=self.formatted_services(services))
    
    self.payments_dialog.open()
  
  def PaymentsPanel(self,services):
    """"""
    #DATA
    #Formatting imagings
    payable_services = [service for service in services if service["payment"].payment_mode.lower() == "cash" and not (service["payment"].paid or service["cancelled"])]
    paid_services = [service for service in services if service["payment"].paid]
    total_bill = sum([service["payment"].cost for service in services if not service["payment"].cancelled])
    paid_bill = sum([service["payment"].paid_amount for service in paid_services])
    pending_bill = total_bill - paid_bill
    ticked_services = []
    
    #FXS
    def update_cost(payment_id,cost):
      b4,aft = 'a','b'
      for service in payable_services:
        if service.payment.payment_id == payment_id:
          service.payment._replace(cost = cost)

    def display_bills():
      #Total Bill
      with ui.label("TOTAL").classes(add="text-gray-900"):
        ui.label(f"{total_bill:,.2f} TZS" if total_bill else "-----").classes(add="ml-2 inline text-sky-700")
      #Paid Bill
      with ui.label("PAID").classes(add="col-span-1 col-start-1 row-span-1 row-start-2 text-gray-900"):
        ui.label(f"{paid_bill:,.2f} TZS" if paid_bill else "-----").classes(add="col-span-1 col-start-2 row-span-1 row-start-2 ml-2 inline text-green-700")
      #Pending Bill
      if pending_bill:
        with ui.label("PENDING").classes(add="col-span-1 col-start-1 row-span-1 row-start-3 text-gray-900"):
          ui.label(f"{pending_bill:,.2f} TZS" if pending_bill else "-----").classes(add="col-span-1 col-start-2 row-span-1 row-start-3 ml-2 inline text-red-600")

    def pick_ticked_service(ticked_service:str,ticked:bool):
      """Returns a list of ticked medicines"""
      if ticked:
        for service in payable_services:
          if service["payment"].payment_id == ticked_service:
            ticked_services.append(service)
      else:
        for service in ticked_services:
          if service["payment"].payment_id == ticked_service:
            ticked_services.remove(service)
      #UI
      selected_pays.clear()
      with selected_pays:
        if ticked_services:
          ui.label(f"{sum([service['payment'].cost for service in ticked_services]):,.2f} TZS").classes(add="inline ml-2 text-purple-600 animate__animated animate__fadeIn")
        else:
          ui.label("-----").classes(add="inline ml-2 text-gray-600")

    def pay_all(services:list):
      """Dispenses all medicines in the ticked_medicines list"""
      if services:
        for service in services:
          self.process_payment(service=service)
      else:
        ui.notify(message="No medicine selected",type="warning",position="center")
    
    #UI
    self.payments_panel.clear()
    with self.payments_panel.classes(add="p-1 flex flex-col"):
      with ui.scroll_area().classes(add="grow w-full h-[400px] pb-2 bg-white rounded-none shadow-sm shadow-[#07004d] animate__animated animate__fadeIn animate__slow"):
        for service in services:
          with html.div().classes(add=f"w-full p-0.5 rounded grid grid-cols-7 gap-0.5 content-center {'bg-gray-200 shadow-md shadow-gray-500 text-red-600' if service['payment'].cancelled else 'bg-sky-100 shadow-md shadow-[#07004d]'}"):
            #Service
            with html.div().classes(add="col-span-7 lg:col-span-3 flex flex-row gap-1"):
              if service["cancelled"]:
                ui.chip(icon="fas fa-ban",color="").classes(add="bg-inherit mx-0 ml-1 px-0")
              #Checkbox
              ui.checkbox(text=f"{services.index(service) + 1}.",on_change=lambda e:pick_ticked_service(
                ticked_service=e.sender.parent_slot.parent.slots["default"].children[1].slots["default"].children[0].props["id"],
                ticked=e.value
              )).props(add="dense").classes(add=f"{'hidden' if service['payment'].payment_mode != 'cash' or service['payment'].paid or service['cancelled'] else ''} text-sky-700 text-bold text-md lg:text-lg")
              #Name
              with html.div().props(add=f"").classes(add="grow bg-inherit flex flex-row items-center"):
                html.em(f"{service['name']}".upper()).props(add=f"id={service['payment'].payment_id} name={'consult' if 'consultant_id' in service else ''}").classes(add=f"bg-inherit {'text-gray-600' if service['cancelled'] else 'text-sky-700'} text-bold text-md lg:text-lg")
              
            #Details
            with html.div().classes(add=f"col-span-7 lg:col-span-4 grid grid-cols-7 gap-1"):
              #Timeframe
              ui.chip(text=f"{format_age((service['service_time']),short=True) } ago" if service['service_time'] else "---",icon="fa-regular fa-clock fa-lg",text_color=f"{'gray-600' if service['cancelled'] else 'sky-900'}",color="").props(add="dense").classes(add="mx-0 col-span-2 lg:col-span-1 bg-inherit text-md lg:text-base font-semibold")
              #Amount
              if service["payment"].cost:
                ui.chip(text=f"{service['payment'].cost:,.2f} TZS",icon="fas fa-coins",color="",text_color=f"{'gray-600' if service['cancelled'] else 'amber-10'}").props(add="dense").classes(add=f"mx-0 col-span-2 lg:col-span-2 lg:justify-self-end bg-inherit text-md lg:text-base text-bold text-wrap")
              else:
                with html.span().classes(add="col-span-2 w-full justify-self-end text-end"):
                  serv = [s for s in get_services() if s["name"] == service["name"]][0]
                  min_cost,max_cost = int(serv["payment"].min_cash),int(serv["payment"].max_cash)+1
                  html.i().props(add=f"id={service['payment'].payment_id}").classes(add="hidden")
                  ui.select(options=[i for i in range(min_cost,max_cost,10000)],with_input=True,on_change=lambda e:update_cost(
                    payment_id=e.sender.parent_slot.parent.slots["default"].children[0].props["id"],
                    cost=e.value
                  )).props(add=f"dense hide-dropdown-icon").classes(add=f"justify-self-end w-[60%] bg-white ring-2 ring-blue-300 rounded pl-2 text-md lg:text-xl")
              #Payment Status
              if not service["cancelled"]:
                ui.chip(text="Paid" if service["payment"].paid else "Billed" if service["payment"].billed else "Not Paid",icon=f"{'fa-regular fa-circle-check' if service['payment'].paid else 'fa-solid fa-file-invoice' if service['payment'].billed else 'fa-regular fa-circle-xmark'} fa-lg",text_color="green" if service["payment"].paid else "purple" if service["payment"].billed else "red",color="").props(add="dense").classes(add=f"mx-0 col-span-2 lg:col-span-1 justify-self-center lg:justify-self-end bg-inherit text-md lg:text-base text-bold")

              #Pay button
              ui.button(text="pay",color="#07004d",on_click=lambda e:self.process_payment(
                service=[service for service in services if service["payment"].payment_id == e.sender.parent_slot.parent.parent_slot.parent.slots["default"].children[0].slots["default"].children[1].slots["default"].children[0].props["id"]][0]
              )).props(add="dense glossy").classes(add=f"{'hidden' if service['payment'].payment_mode.lower() != 'cash' or service['payment'].paid or service['cancelled'] else ''} col-span-1 lg:col-span-3 justify-self-end w-12 lg:w-20 ring-1 ring-blue-200 text-sky-300 text-md text-bold")
              #Payment information
              if service["payment"].paid:
                #Payment Processor
                ui.chip(text=f"{get_staff(self.user.username).last_name}".title(),icon="fa-solid fa-hospital-user fa-lg",text_color="green-600",color="").props(add="dense").classes(add="mx-0 col-span-1 justify-self-center lg:justify-self-end bg-inherit text-md lg:text-base text-bold")
                #Timeframe
                ui.chip(text=f"{format_age(service['payment'].payment_time)} ago",icon="fa-regular fa-clock",text_color="green-600",color="").props(add="dense").classes(add="col-span-3 lg:col-span-2 lg:justify-self-end rounded-sm mx-0  bg-inherit text-md lg:text-base text-bold")
                
      #Bills & Buttons
      with html.div().classes(add="w-full pt-2 flex flex-row animate__animated animate__zoomIn"):
        #Bills
        with html.div().classes(add="lg:px-1 flex flex-col justify-center"):
          if payable_services:
            with ui.label("SELECTED COST").classes(add="block  text-md lg:text-lg text-gray-900 text-bold") as selected_pays:
              ui.label("-----").classes(add="inline ml-2 text-gray-600")
          with html.div().classes(add="flex flex-col lg:flex-row gap-0.5 lg:gap-10 lg:items-center text-md lg:text-lg text-bold") as bills_panel:
            display_bills()
        #Buttons
        with html.div().classes(add="grow flex flex-col lg:flex-row justify-around items-end"):
          #Pay all button
          if payable_services:
            ui.button(text="COLLECT",color="#07004d",on_click=lambda e:pay_all(services=ticked_services)).props(add="dense glossy").classes(add="w-32 rounded ring-1 ring-sky-600 ring-offset-1 shadow-md shadow-sky-600 text-sky-300 text-md lg:text-lg text-bold animate__animated animate__zoomIn")
          #Prin Button
          if paid_services:
            ui.button(text="RECEIPT",icon="fas fa-receipt",color="#07004d",on_click=lambda e:self.print_receipt(medicines=services)).props(add="dense glossy").classes(add="w-32 rounded ring-1 ring-sky-600 ring-offset-1 shadow-md shadow-sky-600 text-sky-300 text-md lg:text-lg text-bold animate__animated animate__zoomIn")
  
  def NewAppointmentPanel(self,client):
    """Shows a dialog for initiating or ending visit"""
    #DATA
    consultants = {staff.name:staff.username for staff in self.consultants}
    details = {
      "name":f"{client.first_name} {client.middle_name if client.middle_name else ''} {client.last_name}",
      "short_name":f"{client.first_name} {client.middle_name[0] if client.middle_name else ''} {client.last_name}".title(),
      "age":format_age(client.birthdate,short=True),
      "gender":client.gender,
      "address":client.address,
      "last_visit":"---" if not client.visits else f"{format_age(self.last_visit(client).start_time)} ago"
    }
    
    appointment_data = {
      "consultant":"",
      "date":"",
      "client_id":client.client_id,
      "appointment_id":f"{client.client_id}apt{str(uuid.uuid4()).split('-')[1]}",
      "attendee_id":self.user.username
    }
    
    _tomorrow = datetime.now() + timedelta(days=1)
    if _tomorrow.month >9:
      tomorrow = f"{_tomorrow.year}/{_tomorrow.month}/{_tomorrow.day}"
    else:
      tomorrow = f"{_tomorrow.year}/0{_tomorrow.month}/{_tomorrow.day}"
    
    def close_dialog():
      self.ClientsStats()
      self.ClientsListing()
      self.client_dialog.close()
    
    def consultant_username(name:str|None):
      if not name:
        return
      else:
        return consultants[name.lower()]

    def returned_date(val):
      if not val:
        return
      
      if type(val) == str:
        return datetime.fromisoformat(val)
      else:
        return val

    #UI
    self.client_panel.clear()
    with self.client_panel:
      pass
      #Header
      with html.div().classes(add="w-full bg-harmony p-1 flex flex-row justify-between"):
        #Client Details
        with html.div().classes(add="grow flex flex-col"):
          with html.span().classes(add="w-full bg-inherit flex flex-row justify-center items-center"):
            ClientCard(details=details)
          ui.label("APPOINTMENT PANEL").classes(add="w-full text-center text-2xl text-yellow-500 font-bold")
        #Close button
        ui.button(icon="fa-regular fa-circle-xmark fa-xl",color="",on_click=close_dialog).classes(add="bg-inherit text-red-500 text-bold text-base")
      
      #Details
      with html.div().classes(add="grow w-full flex flex-col gap-1"):
        ui.date(value=datetime.now()).props(add=f"bordered square today-btn color='harmony' event-color='orange' first-day-of-week='1' navigation-min-year-month='{_tomorrow.strftime("%Y/%m")}'").classes(add="w-full").bind_value_to(appointment_data,"date",forward=lambda e:returned_date(e))
        #Buttons
        with html.div().classes(add="w-full p-1 grid grid-cols-3 gap-1"):
          ui.select(label="CONSULTANT",options=list(consultants.keys()),value=list(consultants.keys())[0]).props(add="popup-content-class='uppercase'").bind_value_to(appointment_data,"consultant",forward=lambda e:consultant_username(e)).classes(add="col-span-2 shadow-md shadow-[#07004d] bg-white rounded px-2 text-lg uppercase")
          ui.button(text="plan",color="#07004d",on_click=lambda e:self.register_appointment(appointment=appointment_data)).props(add="dense glossy").classes(add="ring-1 ring-blue-400 shadow-sm shadow-blue-400 text-sky-300 text-bold text-lg")

class AppointmentsManager():
  """A class for display and amangemet of appoitments"""
  
  def __init__(self,user,parent=None):
    #DATA
    self.user = user
    if parent:
      self.parent = parent

    self.initial_data()

    self.visit_data = {"client_id":"","visit_id":"","appointment_id":None,"payment_mode":"","service":"","service_option":"","attending_clinician":"","card_no":"","authorization_no":""}

    #UI
    with html.div().style(add="overflow-y:hidden;").classes(add="w-full h-full flex flex-col"):
      self.MainPanel()
    
  #FUNCTIONALITIES
  def initial_data(self):
    self._appointments = get_appointments()
    self.appointments = [appointment._asdict() for appointment in self._appointments] if self._appointments else []
    self.clients = get_clients()
    self.services = {
      "Consultation":["consultant",[service.name.split(" ")[0] for service in get_services() if service.type == "consultation"]],
      "Imaging":["imaging stugy",[service.name for service in get_services() if service.type == "imaging"]],
      "Procedure":["procedure",[service.name for service in get_services() if service.type == "procedure"]]
    }
    self.min_period = [staff for staff in get_staffs() if staff.title == "master"][0].registered_on.strftime("%Y/%m")
    #Weekly view data
    self.target_year = datetime.now().year
    self.today = datetime.now().date()
    self.last_week = self.today + timedelta(days=-7)

    #Monthly view data
    self.picked_year,self.picked_month = datetime.now().year,list(calendar.month_name[1:])[int(datetime.now().month)-1]
    
    self.today_appointments = [appointment for appointment in self.appointments if self.is_in_range(start_date=self.today.strftime("%Y-%m-%d"),end_date=self.today.strftime("%Y-%m-%d"),target_date=appointment["appointment_time"].date())]

  def is_in_range(self,start_date:str,end_date:str,target_date:date):
    """Returns True if 'target_date' is between 'start_date' and 'end_date'"""
    
    start_date,end_date,target_date = datetime.fromisoformat(start_date).date(),datetime.fromisoformat(end_date).date(),target_date

    if target_date >= start_date and target_date <= end_date:
      return True
    else:
      return False
  
  def last_visit(self,client):
    """Returns the last visit of client as a namedtuple object"""

    return sorted(client.visits,key=lambda visit:visit.start_time,reverse=True)[0]


  def cancel_appointment(self,appointment:dict):
    """"""
    appointment["cancelled"] = True
    
    status = clients_db.update_appointment_status(appointment)
    
    ui.notify(message=status["message"],type=status["type"],position=status["position"])
    
    self.initial_data()
    self.AppointmentsCarousel()

  def reschedule_appointment(self,appointment:dict):
    """A method to reschedule an appointment"""
    
    status = clients_db.reschedule_appointment(appointment)

    ui.notify(message=status["message"],position=status["position"],type=status["type"])
    self.initial_data()
    self.AppointmentsCarousel()
  
  def initiate_visit(self,visit_data:dict):
    """A method called from the dialog and create a row in 'visit' table"""
    
    #Visit
    visit = {
      "client_id":visit_data["client_id"],
      "visit_id":visit_data["visit_id"].lower(),
      "payment_mode":visit_data["payment_mode"].lower(),
      "appointment_id":visit_data["appointment_id"].lower() if visit_data["appointment_id"] else None,
      "package":visit_data["package"],
      "attendee_id":self.user.username,
    }
    
    #Service & Payment
    selected_service = [service for service in get_services() if service.name.startswith(visit_data["service_option"].lower())][0]
    selected_service_scheme = [scheme for scheme in selected_service.schemes if scheme.scheme_name == visit_data["payment_mode"].lower()][0]
    if selected_service_scheme.active:
      service_prices = [price for price in selected_service_scheme.prices if price.active][0]
    else:
      ui.notify(message=f"Visit cannot be started via {visit_data['payment_mode'].upper()}",caption=f"Try another payment mode!",type="warning",position="top")

    #CONSULTATION
    if selected_service.type == "consultation":
      
      #Consultation
      consultation = {
        "visit_id":visit_data["visit_id"].lower(),
        "name":selected_service.name,
        "payment":{
          "payment_mode":visit_data["payment_mode"].lower(),
          "cost":service_prices._asdict()[visit_data['package'].lower()],
          "billed":True,
          "billed_amount":service_prices._asdict()[visit_data['package'].lower()],
          "authorization_no":visit_data["authorization_no"]
        },
        "hx":{},"ge":{},"orodental":{},"cns":{},"cvs":{},"rs":{},"abd":{},"gus":{},"mss":{},"derma":{},"dx":{}
      }
      #Triage
      vitals = {
        "visit_id":visit_data["visit_id"].lower(),
        "vitals_id":f"{visit_data['visit_id'].lower()}vs1",
        "payment":{
          "visit_id":visit_data["visit_id"].lower(),
          "payment_id":f"{visit_data['visit_id'].lower()}pay{str(uuid.uuid4()).split('-')[1]}",
          "payment_mode":visit_data["payment_mode"].lower(),
          "cost":0,
          "authorization_no":visit_data["authorization_no"],
          "billed":True
        }
      }
      anthrops = {
        "visit_id":visit_data["visit_id"].lower(),
        "anthropometrics_id":f"{visit_data['visit_id'].lower()}anp1",
        "payment":{
          "visit_id":visit_data["visit_id"].lower(),
          "payment_id":f"{visit_data['visit_id'].lower()}pay{str(uuid.uuid4()).split('-')[1]}",
          "payment_mode":visit_data["payment_mode"].lower(),
          "cost":0,
          "authorization_no":visit_data["authorization_no"],
          "billed":True
        }
      }
      status = clients_db.register_visit(visit)
      clients_db.register_consultation(consultation)
      clients_db.register_triage(triage={"vitals":vitals,"anthropometrics":anthrops},initial=True)
        
    #TRIAGE
    if selected_service.type == "triage":
      vitals = {
        "visit_id":visit_data["visit_id"].lower(),
        "vitals_id":f"{visit_data['visit_id'].lower()}vs1",
        "payment":{
          "visit_id":visit_data["visit_id"].lower(),
          "payment_id":f"{visit_data['visit_id'].lower()}pay{str(uuid.uuid4()).split('-')[1]}",
          "payment_mode":visit_data["payment_mode"].lower(),
          "cost":service_prices._asdict()[f"{visit_data['payment_mode']}_{visit_data['package']}".lower()]/2,
          "authorization_no":None,
          "billed":True
        }
      }
      anthrops = {
        "visit_id":self.visit_data["visit_id"].lower(),
        "anthropometrics_id":f"{self.visit_data['visit_id'].lower()}anp1",
        "payment":{
          "visit_id":self.visit_data["visit_id"].lower(),
          "payment_id":f"{self.visit_data['visit_id'].lower()}pay{str(uuid.uuid4()).split('-')[1]}",
          "payment_mode":self.visit_data["payment_mode"].lower(),
          "cost":service_prices._asdict()[f"{visit_data['payment_mode']}_{visit_data['package']}".lower()]/2,
          "authorization_no":None,
          "billed":True
        }
      }
      status = clients_db.register_visit(visit)
      clients_db.register_triage({"vitals":vitals,"anthropometrics":anthrops})
      
    #LABWORK
    elif selected_service.type == "laboratory":
      pass

    #Notification
    ui.notify(message=status["message"],position=status["position"],type=status["type"])
    
    #UI UPDATE
    self.initial_data()
    _client = [client for client in self.clients if client.client_id == visit_data["client_id"]][0]
    self.VisitsPanel(client=_client)


  #UI
  def MainPanel(self):
    #Header
    with html.div().classes(add="w-full bg-[#07004d] p-1 rounded-t flex grid lg:grid-cols-4 gap-0.5"):
      #Title
      with html.div().classes(add="lg:col-span-2 w-full rounded-t px-1 py-0.5 bg-inherit"):
        ui.label("APPOINTMENTS").style(add="text-shadow:2px 2px #505050").classes(add="bg-inherit text-yellow-500 text-bold text-2xl")
    
      #Toggle buttons
      with html.div().classes(add="lg:col-span-2 w-full bg-inherit lg:grid grid-cols-2 gap-1"):
        self.duration_toggle = ui.toggle(options=["daily","weekly","monthly","annual"],value="daily",on_change=lambda e:self.SelectionPanel(duration=e.value)).props(add="glossy spread color='bg-inherit' size='md' toggle-color='bg-inherit' text-color='yellow-400' toggle-text-color='sky-400'").classes(add="lg:justify-self-end align-self-center w-full lg:w-fit lg:rounded-full lg:ring-1 ring-blue-500 text-bold")
      
        #Default selection panel
        with html.div().classes(add="w-full flex flex-row justify-center") as self.selection_panel:
          self.SelectionPanel(duration=self.duration_toggle.value)

    #Appointments panel
    with html.div().classes(add="grow w-full rounded-b") as self.appointments_carousel_pad:
      self.AppointmentsCarousel()
  
  def AppointmentsCarousel(self):
    #DATA
    default_month_start_date = f"{datetime.now().strftime('%Y-%m')}-01"
    default_month_end_date = f"{datetime.now().strftime('%Y-%m')}-{calendar.monthrange(datetime.now().year,datetime.now().month)[1]}"
    default_year_start_date = f"{self.picked_year}-01-01"
    default_year_end_date = f"{self.picked_year}-12-31"
    #UI
    self.appointments_carousel_pad.clear()
    with self.appointments_carousel_pad:
      with ui.carousel().props(add="animated transition-prev='jump-right' transition-next='jump-left' transition-duration='500'").classes(add="w-full h-full rounded-b").bind_value(self.duration_toggle) as self.appointments_carousel:
        
        with ui.carousel_slide(name="daily").classes(add="q-pa-none"):
          with html.div().classes(add="w-full h-full rounded-b") as self.daily_appointments_panel:
            self.AppointmentsDisplay(start_date=self.default_picked_date.value,end_date=self.default_picked_date.value)
            
        with ui.carousel_slide(name="weekly").classes(add="q-pa-none"):
          with html.div().classes(add="w-full h-full") as self.weekly_appointments_panel:
            self.AppointmentsDisplay(start_date=self.last_week.strftime("%Y-%m-%d"),end_date=self.today.strftime("%Y-%m-%d"))
        
        with ui.carousel_slide(name="monthly").classes(add="q-pa-none"):
          with html.div().classes(add="w-full h-full") as self.monthly_appointments_panel:
            self.AppointmentsDisplay(start_date=default_month_start_date,end_date=default_month_end_date)
        
        with ui.carousel_slide(name="annual").classes(add="q-pa-none"):
          with html.div().classes(add="w-full h-full") as self.annual_appointments_panel:
            self.AppointmentsDisplay(start_date=default_year_start_date,end_date=default_year_end_date)

  def SelectionPanel(self,duration:str):
    """"""
    #UI
    self.selection_panel.clear()
    with self.selection_panel:
      if duration == "daily":
        with ui.input(label="PICK DATE",value=datetime.now().strftime("%Y-%m-%d"),on_change=lambda e:self.load_appointments(duration=self.duration_toggle.value,date=e.value)).props(add="autogrow dense filled hidden-bottom-space readonly standout input-class='text-white text-bold' label-color='sky-300'").classes(add="w-fit bg-inherit rounded-full lg:ring-1 ring-blue-400 text-sky-50 text-xl animate__animated animate__zoomIn") as self.default_picked_date:
          with ui.dialog().props(add=" transition-show='jump-up' transition-hide='jump-down' transition-duration='300'").classes(add="ring-1 ring-blue-500") as daily_calendar:
            ui.date(value=datetime.now(),on_change=daily_calendar.close).props(add=f"bordered square today-btn color='harmony' event-color='orange' no-unset today-btn first-day-of-week='1'").bind_value(self.default_picked_date)
          with self.default_picked_date.add_slot("prepend"):
            ui.icon("fas fa-calendar-check fa-xl",color="sky-500").on("click",daily_calendar.open).classes(add="hover:scale-[1.1]")

      if duration == "weekly":
        now = datetime.now()
        today = now.date().strftime("%Y-%m-%d")
        last_week = (now.date() + timedelta(days=-7)).strftime("%Y-%m-%d")
        input_range:str = f"{last_week} | {today}"
        
        #Date range picker
        with ui.input(label="DATE RANGE",value=input_range,on_change=lambda e:self.load_appointments(duration=self.duration_toggle.value,date_range=e.value)).props(add="autogrow dense hidden-bottom-space readonly standout input-class='text-white text-bold' label-color='sky-300'").classes(add="w-3/4 lg:w-full bg-inherit rounded-full lg:ring-1 ring-blue-500 px-7 text-lg animate__animated animate__zoomIn") as date_range_input:
          with ui.dialog() as weekly_calendar:
            ui.date(value=datetime.now(),on_change=weekly_calendar.close).props(add=f"bordered square today-btn color='harmony' event-color='orange' range no-unset today-btn first-day-of-week='1'").bind_value(
              date_range_input,
              forward=lambda x:f'{x["from"]} | {x["to"]}' if x else None,
              backward=lambda x:{'from':x.split(' | ')[0],'to':x.split(' | ')[1]} if ' | ' in (x or '') else None
            )
          with date_range_input.add_slot("prepend"):
            ui.icon("fas fa-calendar-check",color="sky-400").on("click",weekly_calendar.open).classes(add="hover:scale-[1.1]")
    
      if duration == "monthly":
        with ui.button_group().classes(add="bg-inherit w-3/5 lg:w-4/5 flex flex-row gap-3 rounded-full ring-1 ring-blue-400 shadow-md shadow-sky-500 px-3 animate__animated animate__zoomIn"):
          year_label = ui.select(label="YEAR",options=constants.YEARS,on_change=lambda e:self.load_appointments(duration=self.duration_toggle.value)).props(add="dark dense").classes(add="grow pl-2 rounded-l-full text-lg").bind_value(self,"picked_year")
          with year_label.add_slot("prepend"):
            ui.icon("fa-regular fa-calendar-check",color="sky-400")
          month_label = ui.select(label="MONTH",options=list(calendar.month_name)[1:],on_change=lambda e:self.load_appointments(duration=self.duration_toggle.value)).props(add="dark dense").classes(add="grow pl-2 rounded-r-full text-lg").bind_value(self,"picked_month")
          with month_label.add_slot("prepend"):
            ui.icon("fa-regular fa-calendar-check",color="sky-400")
        
      if duration == "annual":
        ui.select(label="YEAR",options=constants.YEARS,on_change=lambda e:self.load_appointments(duration=self.duration_toggle.value)).props(add="dark dense hide-bottom-space").classes(add="bg-inherit ring-1 ring-blue-400 shadow-md shadow-sky-500 w-fit rounded-full px-5 text-lg animate__animated animate__zoomIn").bind_value(self,"picked_year")        
    
  def load_appointments(self,duration:str,date=None,date_range=None):
    #Daily
    if duration == "daily":
      self.daily_appointments_panel.clear()
      with self.daily_appointments_panel:
        self.AppointmentsDisplay(start_date=date,end_date=date)
    
    #Weekly
    if duration == "weekly":
      start_date,end_date = date_range.split(" | ")[0],date_range.split(" | ")[1]
      self.weekly_appointments_panel.clear()
      with self.weekly_appointments_panel:
        self.AppointmentsDisplay(start_date=start_date,end_date=start_date)
    
    #Monthly
    if duration == "monthly":
      _month = list(calendar.month_name).index(self.picked_month)
      if _month >=10:
        start_date = f"{self.picked_year}-{_month}-01"
        end_date = f"{self.picked_year}-{_month}-{calendar.monthrange(self.picked_year,_month)[1]}"
      else:
        start_date = f"{self.picked_year}-0{_month}-01"
        end_date = f"{self.picked_year}-0{_month}-{calendar.monthrange(self.picked_year,_month)[1]}"
      
      self.monthly_appointments_panel.clear()
      with self.monthly_appointments_panel:
        self.AppointmentsDisplay(start_date=start_date,end_date=end_date)

    #Annual
    if duration == "annual":
      start_date = f"{self.picked_year}-01-01"
      end_date = f"{self.picked_year}-12-31"

      self.annual_appointments_panel.clear()
      with self.annual_appointments_panel:
        self.AppointmentsDisplay(start_date=start_date,end_date=end_date)
      
  def AppointmentsDisplay(self,start_date:str,end_date:str):
    """"""
    #DATA
    appointments = sorted([appointment for appointment in self.appointments if self.is_in_range(start_date=start_date,end_date=end_date,target_date=appointment["appointment_time"].date())],key=lambda e:e["appointment_time"].date(),reverse=True)
    #MODS
    def StatusDot(appointment):
      """A function to return a styled icon based on status of client's last visit"""

      status = "active" if appointment["made"] and not (appointment["done"] or appointment["cancelled"]) else "completed" if appointment["done"] else "cancelled" if appointment["cancelled"] else "---"
      return f"<span class='text-bold fa-solid fa-circle { 'text-green-600' if status == 'active' else 'text-yellow-500' if status == 'completed' else 'text-gray-500' if status == 'cancelled' else 'text-red-600'}'></span>"
    
    def GenderIcon(appointment):
      """Returns a styled gender icon based on client's gender"""

      genders = {"male":"mars","female":"venus"}
      colors = {"male":"sky-600","female":"pink-600"}
      return f"<span class='fa-solid fa-{genders[appointment['client_gender'].lower()]} text-{colors[appointment['client_gender'].lower()]}'></span>"
    
    #UI
    #Large screen
    ui.aggrid(
      {
        "columnDefs":[
          {"headerName":"S/N","field":"sno","width":100},
          {"headerName":"CLIENT ID","field":"client_id","filter":"agTextColumnFilter"},
          {"headerName":"NAME","field":"name","filter":"agTextColumnFilter"},
          {"headerName":"AGE","field":"age"},
          {"headerName":"GENDER","field":"gender"},
          {"headerName":"ADDRESS","field":"address"},
          {"headerName":"APPOINTMENT DATE","field":"appt_date"},
          {"headerName":"STATUS","field":"status","cellClassRules":{
            "text-green-600 text-bold":"x == 'Active'",
            "text-yellow-600 text-bold":"x == 'Completed'",              "text-red-600 text-bold":"x == 'Cancelled'"
          }}
        ] ,
        "rowData":[{
          "sno":appointments.index(appointment) + 1,
          "client_id":appointment["client_id"],
          "name":appointment["client_name"].title(),
          "age":format_age(appointment["client_birthdate"]),
          "gender":appointment["client_gender"].capitalize(),
          "address":appointment["client_address"].capitalize(),
          "appt_date":appointment["appointment_time"].strftime("%d %b %Y"),
          "status":"Active" if appointment["made"] and not (appointment["done"] or appointment["cancelled"]) else "Completed" if appointment["done"] else "Cancelled" if appointment["cancelled"] else "---",
        } for appointment in appointments]
      },theme="quartz").classes(add="lg-show w-full h-full animate__animated animate__fadeIn animate_delay-2s animate__slow").on("cellClicked",lambda e:self.AppointmentDialog(appointment=[appointment for appointment in appointments if appointment["client_id"] == e.args["data"]["client_id"]][0]))
    
    #Small Screens
    ui.aggrid(
          {
            "columnDefs":[
              {"headerName":"","field":"status","width":75},
              {"headerName":"CLIENT ID","field":"client_id","filter":"agTextColumnFilter","floatingFilter":True,"width":160},
              {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","floatingFilter":True,"width":300},
              {"headerName":"","field":"gender","align":"left","width":75},
              {"headerName":"AGE","field":"age","width":150}
            ],
            "rowData":[
              {
                "status":StatusDot(appointment),
                "client_id":appointment["client_id"],
                "name":appointment["client_name"].title(),
                "age":f"{format_age(appointment['client_birthdate']).split(' ')[0]} {format_age(appointment['client_birthdate']).split(' ')[1]}",
                "gender":GenderIcon(appointment)
              } for appointment in appointments
            ],
          },
          html_columns=[0,3],
          theme="quartz"
        ).classes(add="lg:hidden w-full h-full animate__animated animate__fadeIn animate__slow").on("cellClicked",lambda e:self.AppointmentDialog(appointment=[appointment for appointment in appointments if appointment["client_id"] == e.args["data"]["client_id"]][0]))
    
  def AppointmentDialog(self,appointment:dict):
    """"""
    #DATA
    if "receptionist" not in self.user.roles:
      return
    
    details = {
      "name":appointment["client_name"],
      "short_name":f"{appointment['client_name'].split(' ')[0]} {appointment['client_name'].split(' ')[1] if len(appointment['client_name'].split(' ')) > 2 else ''} {appointment['client_name'].split(' ')[2]}".title(),
      "age":format_age(appointment["client_birthdate"]),
      "gender":appointment["client_gender"],
      "address":appointment["client_address"]
    }
    #FXS
    def close_dialog():
      self.AppointmentsCarousel()

    #UI
    with ui.dialog() as self.appointment_dialog,html.div().style(add="min-height:50%;").classes(add="w-fit p-0.5 bg-sky-50 flex flex-col"):
      #Header
      with html.div().classes(add="w-full grid grid-cols-11 bg-[#07004d]"):
        with html.div().classes(add="col-span-10 bg-inherit"):
          ClientCard(details=details)
        ui.button(icon="fas fa-circle-xmark",color="",on_click=close_dialog).classes(add="col-span-1 bg-inherit text-red-600 text-bold text-base")
      #Appointment
      with html.div().classes(add="grow w-full"):
        pass
      
      #Button
      with html.div().classes(add="w-full p-2 flex flex-row justify-center gap-5") as self.reschedule_panel:
        #Initiate visit button
        #ui.button(text="initiate visit",color="gray-900",on_click=lambda e:self.NewVisitPanel(client=[client for client in get_clients() if client.client_id == appointment['client_id']][0],appointment_id=appointment["appointment_id"])).props(add="bordered dense glossy").classes(add="rounded shadow-md shadow-[#07004d] text-sky-300 text-xl text-bold")
        #Reschedule button
        ui.button(text="reschedule",color="",on_click=lambda e:self.ReschedulePanel(appointment["appointment_id"])).props(add="bordered dense glossy").classes(add="rounded bg-harmony shadow-md shadow-[#07004d] text-yellow-500 text-xl text-bold")
        #Cancel button
        ui.button(text="cancel",color="",on_click=lambda e:self.cancel_appointment(appointment)).props(add="bordered dense glossy").classes(add="rounded bg-harmony shadow-md shadow-[#07004d] text-red-600 text-xl text-bold")
    
    if appointment["cancelled"] or appointment["done"]:
      return
    else:
      self.appointment_dialog.open()

  def NewVisitPanel(self,client:dict,appointment_id:str|None=None):
    """Shows a dialog for initiating or ending visit"""
    #DATA
    def format_visit_id():
      if client.visits:
        return f"{client.client_id}v{int(self.last_visit(client).visit_id.split('v')[1]) + 1}"
      else:
        return f"{client.client_id}v1"

    details = {
      "name":f"{client.first_name} {client.middle_name if client.middle_name else ''} {client.last_name}",
      "short_name":f"{client.first_name} {client.middle_name[0] if client.middle_name else ''} {client.last_name}",
      "age":format_age(client.birthdate,short=True),
      "gender":client.gender,
      "address":client.address,
      "last_visit":format_age(self.last_visit(client).start_time) if client.visits else "---"
    }

    visit_data = {
      "client_id":client.client_id,
      "visit_id":format_visit_id(),
      "appointment_id":appointment_id,
      "payment_mode":"",
      "package":"",
      "service":"",
      "service_option":"",
      "attending_clinician":"",
      "card_no":"",
      "authorization_no":"",
      "auth_button_clicked":False
      }

    payment_options = ["cash"] if client.payment_mode.lower() == "cash" else [client.payment_mode.upper(),"cash"]
    payment_packages = json.loads(self.basics.payment_packages)
    
    #MODS
    def get_authorization_number():
      """Retrives authorization number for insured clients and inserts it into visit_data"""

      auth = clients_processor.authorize_visit({"scheme":visit_data["payment_mode"],"card_no":visit_data["card_no"]})

      ui.notify(message=auth["message"],position="center" if auth["type"] == "negative" else "top",type=auth["type"])
      with self.auth_number.add_slot("append"):
        if auth["type"] == "positive":
          ui.icon(name="fas fa-user-check",color="green-600").classes(add="mx-3")
        else:
          ui.icon(name="fas fa-user-xmark",color="red-600").classes(add="mx-3")
    
      #Binding data
      visit_data["authorization_no"] = auth["auth_no"]
    
    def ServiceOptions(service_category:str):
      """Dynamically loads a selection element for service options based on the service_categgory value"""
      service = service_category
      options = [_service.title() for _service in self.services[service][1]]
      value = self.services[service][1][0].title()
      label = self.services[service][0].upper()

      self.service_options_pad.clear()
      with self.service_options_pad:
        ui.select(options=options,value=value,label=label).classes(add="w-full shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value_to(visit_data,"service_option")

    #UI
    self.client_details_panel.clear()
    with self.client_details_panel:
      #Visit details
      with html.div().classes(add="grow w-full flex flex-col justify-between gap-3 p-1 bg-sky-100"):
        #Services
        with html.div().classes(add="w-full p-1 grid grid-cols-2 gap-3 animate__animated animate__fadeIn"):
          #Service
          with html.div().classes(add="col-span-2 w-full grid grid-cols-2 gap-3"):
            #Service type
            self.service_category = ui.select(options=list(self.services),label="SERVICE",value="Consultation",on_change=lambda e:ServiceOptions(e.value)).classes(add="shadow-md shadow-[#07004d] bg-sky-50 rounded-sm px-2 text-lg").bind_value_to(visit_data,"service")
            #Service Options
            with html.div().classes(add="") as self.service_options_pad:
              ui.select(options=[_service.title() for _service in self.services["Consultation"][1]],value=self.services["Consultation"][1][0].title(),label="CONSULTANT").classes(add="shadow-md shadow-[#07004d] bg-sky-50 rounded-sm px-2 text-lg").bind_value_to(visit_data,"service_option")
            
          #Payment
          with html.div().classes(add="col-span-2 w-full grid grid-cols-2 gap-3"):
            ui.select(options=payment_options,value=payment_options[0],label="PAYMENT MODE").props(add="bordered popup-content-class='uppercase'").classes(add="shadow-md shadow-[#07004d] bg-sky-50 rounded px-2 text-lg uppercase").bind_value_to(visit_data,"payment_mode")   #payment mode
            ui.select(options=payment_packages,value=payment_packages[0],label="PACKAGE").props(add="bordered popup-content-class='uppercase'").classes(add="shadow-md shadow-[#07004d] bg-sky-50 rounded px-2 text-lg uppercase").bind_value_to(visit_data,"package")
            ui.input(label="CARD/NIDA NO",value=client.card_no).props(add="type='text' bordered readonly").bind_visibility_from(visit_data,"payment_mode",lambda v:v != "cash").classes(add="bg-white shadow-md shadow-[#07004d] rounded-sm px-2 text-lg").bind_value_to(visit_data,"card_no")     #Card No
            ui.button(text="authorize",color="#07004d",on_click=get_authorization_number).props(add="bordered glossy").bind_visibility_from(visit_data,"payment_mode",lambda v:v != "cash").classes(add="rounded shadow-md shadow-[#07004d] text-sky-300 text-lg lg:text-xl text-bold")   #Authorize button
            self.auth_number = ui.input(label="AUTHORIZATION NO").props(add="bordered glossy readonly").bind_visibility_from(visit_data,"payment_mode",lambda v:v != "cash").classes(add="col-span-2 w-3/4 justify-self-center bg-white shadow-md shadow-[#07004d] rounded-sm px-2 text-xl text-green-700").bind_value(visit_data,"authorization_no")          #Authorization Number
          
        #Action buttons
        with html.div().classes(add="w-full p-1 flex flex-row justify-center"):
          #Initiate visit
          ui.button(text="start visit",color="#07004d",on_click=lambda e:self.initiate_visit(visit_data=visit_data)).props(add="bordered dense glossy").classes(add="w-auto shadow-md shadow-[#07004d] text-sky-300 text-xl lg:text-2xl text-bold")

#NURSING
class TriageManager():
  """A class to display UI for triage management"""

  def __init__(self,user,mini:bool=False):
    #DATA
    self.user = user
    self.initial_data()
    
    #UI
    with html.div().classes(add=f"w-full h-full flex flex-col {'' if self.triage_visits else 'justify-center content-center bg-white rounded-b'}"):
      if self.triage_visits:
        ui.separator().classes(add="w-full bg-[#09026f]")
        with html.div().classes(add="w-full p-2 bg-harmony flex flex-row"):
          ui.label("TODAY VISITS").classes(add="").classes(add="bg-inherit grow text-3xl text-yellow-500 text-bold")
          with html.div().classes(add="bg-inherit") as self.stats_panel:
            self.TriageStats()
        #Displays
        with html.div().classes(add="w-full grow bg-white rounded-b") as self.display_panel:
          if mini:
            self.TriagesMiniDisplay()
          else:
            self.TriagesDisplay()
      else:
        with html.div().classes(add="bg-inherit flex flex-col gap-2 p-3 text-bold"):
          ui.label("No clients for now").classes(add="text-3xl text-rose-500")
          ui.label("Just relax and have fun!").classes(add="italic text-center text-2xl text-pink-300")

  #FUNCTIONALITIES
  def initial_data(self):
    self._triage_visits = [visit for visit in get_active_visits() if visit.vital_signs or visit.anthropometrics]
    self.triage_visits = [visit._asdict() for visit in self._triage_visits]
    self.done_triages = [visit for visit in self.triage_visits if self.triage_status(visit) == "done"]
    self.not_done_triages = [visit for visit in self.triage_visits if self.triage_status(visit) == "not done"]
    self.incomplete_triages = [visit for visit in self.triage_visits if self.triage_status(visit) == "incomplete"]
  
  def payment_status(self,visit:dict):
    """Returns a string representing payment status of imagings"""

    statuses = set()

    triages = visit["vital_signs"] + visit["anthropometrics"]
    
    for triage in triages:
      if triage.payment.paid and not triage.payment.billed:
        statuses.add("paid")
      if triage.payment.billed and not triage.payment.paid:
        statuses.add("billed")
      if not triage.payment.billed and not triage.payment.paid:
        statuses.add("not paid")
    
    if len(statuses) == 1:
      for status in statuses:
        return status
    else:
      return "partial"
    
  def triage_status(self,visit:dict):
    """Returns a string representing payment status of triage services"""

    statuses = set()

    vital = visit["vital_signs"][-1] if visit["vital_signs"] else None
    #Vitals
    if vital:
      if vital.done:
        if (vital.temperature and vital.pulse_rate and vital.resp_rate and vital.o2sat) or (vital.sbp and vital.dbp):
          statuses.add("done")
        elif (vital.temperature or vital.sbp or vital.dbp or vital.pulse_rate or vital.resp_rate or vital.o2sat):
          statuses.add("incomplete")
      else:
        statuses.add("not done")
    else:
      statuses.add("not done")
    
    #Anthropometrics
    if visit["anthropometrics"]:
      if get_duration(visit["client_birthdate"])["years"] > 2:
        _anthrops_all = [_anthrop for _anthrop in visit["anthropometrics"] if _anthrop.weight and _anthrop.height]
        _anthrops_some = [_anthrop for _anthrop in visit["anthropometrics"] if _anthrop.weight or _anthrop.height]
      else:
        _anthrops_all = [_anthrop for _anthrop in visit["anthropometrics"] if _anthrop.weight and _anthrop.height and _anthrop.muac and _anthrop.head_circum]
        _anthrops_some = [_anthrop for _anthrop in visit["anthropometrics"] if _anthrop.weight or _anthrop.height or _anthrop.muac or _anthrop.head_circum]
      
      if _anthrops_all:
        statuses.add("done")
      elif _anthrops_some:
        statuses.add("incomplete")
      else:
        statuses.add("not done")
    else:
      statuses.add("not done")
    
    if len(statuses) == 1:
      return statuses.pop()
    else:
      return "incomplete"
    
  def relay_dialogs(self,visit:dict):
    """Decides which dialog to display"""

    status = self.triage_status(visit)

    if status == "Done" or status == "Incomplete":
      self.TriagesDialog(visit)
    else:
      self.NewTriageDialog(visit)

  def save_triage(self,triage:dict,mini:bool=False):
    """register data to database"""

    status = clients_db.update_triage(triage)
  
    #Notify
    ui.notify(message=status["message"],type=status["type"],position=status["position"])
    
    #Page refresh
    self.initial_data()
    self.TriageStats()
    if mini:
      self.TriagesMiniDisplay()
    else:
      self.TriagesDisplay()

  def client_mini(self,visit):
    """Returns a string of html elements for display in small screens"""

    def GenderIcon(visit):
      """Returns a styled gender icon based on client's gender"""

      genders = {"male":"mars","female":"venus"}
      colors = {"male":"sky-600","female":"pink-600"}

      return f"<span class='fa-solid fa-{genders[visit['client_gender'].lower()]} text-{colors[visit['client_gender'].lower()]}'></span>"
    
    age = f"<span class='ml-1'>{format_age(visit['client_birthdate']).split(' ')[0]} {format_age(visit['client_birthdate']).split(' ')[1][0].upper()}</span>"
    gender = GenderIcon(visit)
    payment_mode = f"<span class=''>{visit['payment_mode'].upper()}</span>"

    return f"<span class='h-full'>{gender}{age}</span>"


  #UI
  def TriageStats(self):
    """"""
    self.stats_panel.clear()
    with self.stats_panel:
      with html.span().classes(add="flex flex-row"):
        #Visits
        with ui.label("VISITS").classes(add="rounded-full p-2 text-sky-500"):
          ui.label(str(len(self.triage_visits))).classes(add="ml-1 inline text-bold text-white")
        #Done
        with ui.chip(icon="fa-regular fa-circle-check",text_color="green",color="").classes(add=f"{'' if self.done_triages else 'hidden'} p-2 bg-inherit").tooltip("Completed Triages"):
          ui.label(str(len(self.done_triages))).classes(add="inline text-bold text-white")
        #Pending
        with ui.chip(icon="fas fa-spinner",text_color="yellow",color="").classes(add=f"{'' if self.incomplete_triages else 'hidden'} p-2 bg-inherit").tooltip("Incomplete Triages"):
          ui.label(str(len(self.incomplete_triages))).classes(add="inline text-bold text-white")
        #Not Done
        with ui.chip(icon="fa-regular fa-circle-xmark",text_color="red",color="").classes(add=f"{'' if self.not_done_triages else 'hidden'} p-2 bg-inherit"):
          ui.label(str(len(self.not_done_triages))).classes(add="inline text-bold text-white")

  def TriagesDisplay(self):
    """"""
    #UI
    self.display_panel.clear()
    with self.display_panel:
      self.visit_aggrid = ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/N","field":"sno","width":50},
            {"headerName":"CLIENT ID","field":"client_id","filter":"agTextColumnFilter","floatingFilter":True,"width":100},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","floatingFilter":True},
            {"headerName":"AGE","field":"age","width":80},
            {"headerName":"GENDER","field":"gender","width":80},
            {"headerName":"VISIT TIME","field":"duration","width":120},
            {"headerName":"STATUS","field":"status","width":100,"cellClassRules":{
              "text-green-600 text-bold":"x == 'Done'",
              "text-red-600 text-bold":"x == 'Not Done'",
              "text-yellow-500 text-bold":"x == 'Incomplete'"
              }
            }
          ] ,
          "rowData":[
            {
              "sno":self.triage_visits.index(visit) + 1,
              "client_id":visit["client_id"],
              "visit_id":visit["visit_id"].upper(),
              "name":visit["client_name"].title(),
              "age":f"{format_age(visit['client_birthdate']).split(' ')[0]} {format_age(visit['client_birthdate']).split(' ')[1]}",
              "gender":visit["client_gender"].capitalize(),
              "duration":f"{format_age(visit['start_time'])}",
              "payment":visit["payment_mode"].upper(),
              "status":self.triage_status(visit).title()
            } for visit in self.triage_visits
          ]
        },theme="quartz"
        ).classes(add="w-full h-full animate__animated animate__fadeIn").on("cellClicked",lambda e:self.TriagesDialog(visit=[visit for visit in self.triage_visits if visit['visit_id'] == e.args["data"]["visit_id"].lower()][0]))
  
  def TriagesMiniDisplay(self):
    """Displays the details of clients for small screens"""
    #MODS
    def StatusDot(visit):
      """A function to return a styled icon based on status of client's last visit"""

      status = self.triage_status(visit)
      return f"<span class='fa-solid fa-circle { 'text-green-600' if status == 'done' else 'text-red-600' if status == 'not done' else 'text-yellow-500'}'></span>"
    
    def GenderIcon(visit):
      """Returns a styled gender icon based on client's gender"""

      genders = {"male":"mars","female":"venus"}
      colors = {"male":"sky-600","female":"pink-600"}
      return f"<span class='fa-solid fa-{genders[visit['client_gender'].lower()]} text-{colors[visit['client_gender'].lower()]}'></span>"

    #UI
    self.display_panel.clear()
    with self.display_panel:
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"","field":"status","width":75},
            {"headerName":"CLIENT ID","field":"client_id","filter":"agTextColumnFilter","floatingFilter":True,"width":160},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","floatingFilter":True,"width":300},
            {"headerName":"","field":"details","align":"left","width":150},
          ],
          "rowData":[
            {
              "status":StatusDot(visit),
              "client_id":visit["client_id"],
              "name":f"{visit['client_name'].split(' ')[0]} {visit['client_name'].split(' ')[1][0]}. {visit['client_name'].split(' ')[2]}".title(),
              "details":self.client_mini(visit),
            } for visit in self.triage_visits
          ],
        },
        html_columns=[0,3],
        theme="quartz"
      ).classes(add="w-full h-full animate__animated animate__fadeIn animate__slow").on("cellClicked",lambda e:self.TriagesDialog(visit=[visit for visit in self.triage_visits if visit['client_id'] == e.args["data"]["client_id"]][0],mini=True))

  def NewTriagePanel(self,visit:dict,repeat:bool=False,mini:bool=False):
    """"""
    #DATA
    anthropometrics_1,vitals_1 = visit["anthropometrics"][0],visit["vital_signs"][0]
    
    if repeat:
      vitals = {
        "visit_id":visit["visit_id"],
        "vitals_id":f"{visit['visit_id']}vs{len(visit['vital_signs']) + 1}",
        "attendee_id":self.user.username,
        "temp":None,"sbp":None,"dbp":None,"pr":None,"rr":None,"osat":None,
        "payment":{
          "visit_id":visit["visit_id"],
          "vitals_id":f"{visit['visit_id']}vs{len(visit['vital_signs']) + 1}",
          "payment_id":f"{visit['visit_id']}vs{len(visit['vital_signs']) + 1}pay{len(visit['payments']) + 1}",
          "cost":0,
          "payment_mode":visit["payment_mode"],
          "authorization_no":visit["consultations"][0].payment.authorization_no if visit["consultations"] else None,
          "billed":True,
          "paid":True
        }
      }
      anthrops = {
        "visit_id":visit["visit_id"],
        "anthropometrics_id":f"{visit['visit_id']}anp{len(visit['anthropometrics']) + 1}",
        "attendee_id":self.user.username,
        "weight":None,
        "height":None,
        "muac":None,
        "hc":None,
        "payment":{
          "visit_id":visit["visit_id"],
          "anthropometrics_id":f"{visit['visit_id']}anp{len(visit['anthropometrics']) + 1}",
          "payment_id":f"{visit['visit_id']}anp{len(visit['anthropometrics']) + 1}pay{len(visit['payments']) + 1}",
          "cost":0,
          "payment_mode":visit["payment_mode"],
          "authorization_no":visit["consultations"][0].payment.authorization_no if visit["consultations"] else None,
          "billed":True,
          "paid":True
        }
      }
      
      triage_data = {"vitals":vitals,"anthropometrics":anthrops}
      clients_db.register_triage(triage_data)

    else:
      if self.payment_status(visit) == "paid" or self.payment_status(visit) == "billed":
        vitals = {"attendee_id":self.user.username,"vitals_id":vitals_1.vitals_id,"temp":None,"sbp":None,"dbp":None,"pr":None,"rr":None,"osat":None}
        anthrops = {"attendee_id":self.user.username,"anthropometrics_id":anthropometrics_1.anthropometrics_id,"weight":None,"height":None,"muac":None,"hc":None}
        triage_data = {"vitals":vitals,"anthropometrics":anthrops}
      elif self.payment_status(visit) == "partial":
        triage_data = {}
        if vitals_1.payment.paid or vitals_1.payment.billed:
          vitals = {"attendee_id":self.user.username,"vitals_id":vitals_1.vitals_id,"temp":None,"sbp":None,"dbp":None,"pr":None,"rr":None,"osat":None}
          triage_data["vitals"] = vitals
        if anthropometrics_1["payment"]["paid"] or anthropometrics_1.payment.billed:
          anthrops = {"attendee_id":self.user.username,"anthropometrics_id":anthropometrics_1.anthropometrics_id,"temp":None,"sbp":None,"dbp":None,"pr":None,"rr":None,"osat":None}
          triage_data["anthropometrics"] = anthrops
      else:
        ui.notify(message="Unpaid Service!",type="warning",position="center")
        return
  
    #UI
    self.triages_dialog_panel.clear()
    with self.triages_dialog_panel:
      with html.div().classes(add="grow w-full p-0.5 rounded-b ring-1 ring-blue-400 shadow-md shadow-blue-400 flex flex-col animate__animated animate__fadeIn animate__slow"):
        #TRIAGE
        with html.form().classes(add="grow w-full flex flex-row"):
          #Vital signs
          if "vitals" in triage_data:
            with html.div().classes(add="w-full"):
              ui.label("VITAL SIGNS").classes(add="w-full bg-harmony text-sky-300 text-bold text-center text-3xl")
              with html.div().classes(add="w-full p-3 flex flex-row justify-around gap-5"):
                if get_duration(visit["client_birthdate"])["years"] >= 12:
                  self.sbp_input = ui.number(label="SBP (mmHg)",min=0,max=370).bind_value(vitals,"sbp").classes(add="w-32 bg-white rounded shadow-md shadow-sky-600 px-5 text-lg")
                  self.dbp_input = ui.number(label="DBP (mmHg)",min=0,max=360).bind_value(vitals,"dbp").classes(add="w-32 bg-white rounded shadow-md shadow-sky-600 px-5 text-lg")
                self.pr_input = ui.number(label="PR (bpm)",min=0,max=500).bind_value(vitals,"pr").classes(add="w-32 bg-white rounded shadow-md shadow-sky-600 px-5 text-lg")
                self.temp_input = ui.number(label="TEMP (℃)",min=11.8,max=46.3).props(add="required").bind_value(vitals,"temp").classes(add="w-32 bg-white rounded shadow-md shadow-sky-600 px-5 text-lg")
                self.rr_input = ui.number(label="RR (cpm)",min=0,max=200).bind_value(vitals,"rr").classes(add="w-32 bg-white rounded shadow-md shadow-sky-600 px-5 text-base")
                self.o2sat_input = ui.number(label="O₂ SAT (%)",min=0,max=100).bind_value(vitals,"osat").classes(add="w-32 bg-white rounded shadow-md shadow-sky-600 px-5 text-base")
          
          #Anthropometrics
          if "anthropometrics" in triage_data:
            with html.div().classes(add="w-full"):
              ui.label("ANTHROPOMETRICS").classes(add="w-full bg-harmony text-sky-300 text-bold text-center text-3xl")
              with html.div().classes(add="w-full p-2 flex flex-row justify-around lg:justify-center gap-5"):
                self.weight_input = ui.number(label="WEIGHT (kg)",min=0,max=370).bind_value(anthrops,"weight").classes(add="w-32 bg-white rounded shadow-md shadow-sky-600 px-5 text-lg")
                self.height_input = ui.number(label=f"{'LENGTH' if get_duration(visit['client_birthdate'])['years'] < 2 else 'HEIGHT'} (cm)",min=0,max=360).bind_value(anthrops,"height").classes(add="w-32 bg-white rounded shadow-md shadow-sky-600 px-5 text-lg")
                if get_duration(visit["client_birthdate"])["years"] < 2:
                  self.hc_input = ui.number(label="HC (cm)").bind_value(anthrops,"hc").classes(add="w-32 bg-white rounded shadow-md shadow-harmony px-5 text-lg")
                  self.muac_input = ui.number(label="MUAC (cm))").bind_value(anthrops,"muac").classes(add="w-36 bg-white rounded shadow-md shadow-harmony px-5 text-lg")
        
        #BUTTONS
        with html.div().classes(add="w-full p-1 flex flex-row justify-center"):
          ui.button(text="SAVE",icon="fa-regular fa-floppy-disk fa-sm",color="",on_click=lambda e:self.save_triage(triage=triage_data,mini=mini)).props(add="").classes(add="ring-1 ring-sky-500 bg-harmony shadow-md shadow-harmony text-sky-300 text-xl text-bold")

  def TriagesDialog(self,visit:dict,mini:bool=False):
    """A method to display dialog for triage details pulled from database"""

    #DATA
    details = {
      "name":visit["client_name"],
      "short_name":f"{visit["client_name"].split(" ")[0]} {visit["client_name"].split(" ")[1][0]}. {visit["client_name"].split(" ")[2]}".title(),
      "age":format_age(visit["client_birthdate"]),
      "gender":visit["client_gender"],
      "address":visit["client_address"],
      "last_visit":format_age(visit["start_time"])
    }
    
    vitals = [vital._asdict() for vital in visit["vital_signs"] if vital.done]
    anthrop = visit["anthropometrics"][0]
    #FXS
    def close_dialog():
      self.initial_data()
      self.TriageStats()
      self.TriagesDisplay()
      self.triages_dialog.close()

    #UI
    with ui.dialog().props(add="transition-show='scale' transition-hide='scale' transition-duration='500'") as self.triages_dialog,html.div().style(add="min-width:90%;min-height:60%;").classes(add="bg-sky-100 flex flex-col"):
      #HEADER
      with html.div().classes(add="w-full rounded-t p-1 flex flex-row bg-harmony"):
        with html.div().classes(add="grow"):
          ClientCard(details=details)
        ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=close_dialog).classes(add="bg-inherit text-red-600 text-bold text-base")
      
      #TRIAGES
      with html.div().classes(add="grow w-full flex flex-col justify-between animate___animated animate__fadeIn animate__slow") as self.triages_dialog_panel:
        if len(visit["vital_signs"]) > 1:
          self.TriagesAggrid(visit=visit,mini=mini)
        else:
          if visit["vital_signs"][0].done:
            self.TriagesAggrid(visit=visit,mini=mini)
          else:
            self.NewTriagePanel(visit=visit,mini=mini)

    self.triages_dialog.open()

  def TriagesAggrid(self,visit,mini:bool=False):
    #DATA
    vitals = sorted([vital._asdict() for vital in visit["vital_signs"] if vital.done],key=lambda e:e["vitals_time"],reverse=True)
    if visit["anthropometrics"]:
      _anthrops = [_anthrop._asdict() for _anthrop in visit["anthropometrics"] if _anthrop.weight]
      if _anthrops:
        anthrop = _anthrops[-1]
      else:
        anthrop = {"weight":None,"height":None,"muac":None,"head_circum":None}
    else:
      anthrop = {"weight":None,"height":None,"muac":None,"head_circum":None}

    #UI
    self.triages_dialog_panel.clear()
    with self.triages_dialog_panel.classes(add=""):
      #Separator
      for i in range(2):
        ui.separator().classes(add="w-full bg-[#09026f]")
      #Anthropometrics
      with html.section().classes(add="bg-harmony w-full p-2 flex flex-row gap-5 text-bold text-lg"):
        #Weight
        with ui.label(""):
          ui.label("").classes(add="fa-solid fa-weight-scale text-yellow-500")
          ui.label(f"{str(anthrop['weight'])+'kg' if anthrop['weight'] else '---'}").classes(add="inline ml-0.5 text-sky-300")
        #Height/Length
        with ui.label(""):
          ui.label("").classes(add="fa-solid fa-ruler-vertical text-yellow-500").tooltip(f"")
          ui.label(f"{str(anthrop['height'])+'cm' if anthrop['height'] else '---'}").classes(add="inline ml-0.5 text-sky-300")
        #MUAC
        with ui.label("").classes(add=f"{'' if anthrop['muac'] else 'hidden'}"):
          ui.label("").classes(add="fa-solid fa-child text-yellow-500")
          ui.label(f"{anthrop['muac']} cm").classes(add="inline ml-0.5 text-sky-300")
        #Head Circumference
        with ui.label("").classes(add=f"{'' if anthrop['head_circum'] else 'hidden'}"):
          ui.label("").classes(add="fa-solid fa-child text-yellow-500")
          ui.label(f"{anthrop['head_circum']} cm").classes(add="inline ml-0.5 text-sky-300")
        
      #Vitals
      with html.section().classes(add="grow flex flex-col"):
        #Large screen
        ui.table(
          columns=[
            {"name":"date","label":"DATE","field":"date","align":"left"},
            {"name":"time","label":"TIME","field":"time","align":"left"},
            {"name":"temp","label":"TEMPERATURE (℃)","field":"temp","align":"left"},
            {"name":"sbp","label":"SYSTOLIC BP (mmHg)","field":"sbp","align":"left"},
            {"name":"dbp","label":"DIASTOLIC BP (mmHg)","field":"dbp","align":"left"},
            {"name":"pr","label":"PULSE RATE (bpm)","field":"pr","align":"left"},
            {"name":"rr","label":"RESPIRATORY RATE (cpm)","field":"rr","align":"left"},
            {"name":"osat","label":"O₂ SATURATION (%)","field":"osat","align":"left"}
          ],
          rows=[
            {
              "date":str(int(vital["vitals_time"].strftime("%d")))+ vital["vitals_time"].strftime(" %b %Y"),
              "time":vital["vitals_time"].strftime("%H:%M"),
              "temp":vital["temperature"],
              "sbp":vital["sbp"],
              "dbp":vital["dbp"],
              "pr":vital["pulse_rate"],
              "rr":vital["resp_rate"],
              "osat":vital["o2sat"]
            } for vital in vitals
          ],title="VITAL SIGNS CHART",pagination={"rowsPerPage":5}
        ).classes(add="hidden w-full grow bg-sky-50")

        #Small screen
        with ui.scroll_area().classes(add="grow lghidden"):
          for vital in vitals:
            with html.div().classes(add="rounded shadow-sm shadow-sky-700"):
              with html.div().classes(add="p-1 flex flex-row gap-5 bg-harmony rounded-t text-sky-200 font-semibold"):
                ui.label(f"{vital["vitals_time"].strftime('%d %b %Y')}").classes(add="")
                ui.label(vital["vitals_time"].strftime("%H:%M"))

              with html.div().classes(add="flex flex-row gap-0"):
                #Temp
                ui.chip(text=f"{vital['temperature']}°C" if vital["temperature"] else "---",icon="fa-solid fa-temperature-quarter fa-sm",color="",text_color="sky-900").props(add="").classes(add="bg-inherit px-1 shadow-sm shadow-sky-700 rounded font-semibold")
                #PR/HR
                ui.chip(text=f"{vital['pulse_rate']} bpm" if vital["pulse_rate"] else "---",icon="fa-solid fa-heart-pulse fa-sm",color="",text_color="sky-900").props(add="").classes(add="bg-inherit px-2 shadow-sm shadow-sky-700 rounded font-semibold")
                #RR
                ui.chip(text=f"{vital['resp_rate']} cpm" if vital["resp_rate"] else "---",icon="fa-solid fa-lungs fa-sm",color="",text_color="sky-900").props(add="").classes(add="bg-inherit px-2 shadow-sm shadow-sky-700 rounded font-semibold")
                #SPO2
                with ui.chip(text="O₂ :",color="",text_color="sky-900").props(add="").classes(add="bg-inherit px-2 shadow-sm shadow-sky-700 rounded font-semibold text-md"):
                  ui.label(f"{vital['o2sat']} %" if vital["o2sat"] else "---").classes(add="inline ml-0.5")
                #BP
                with ui.chip(icon="fa-solid fa-stethoscope fa-sm",color="",text_color="sky-900").classes(add="bg-inherit px-2 rounded shadow-sm shadow-sky-700 font-semibold"):
                  ui.label(f"{vital['sbp']}" if vital["sbp"] else "---")
                  ui.label("/").classes(add="inline m-0 p-0")
                  ui.label(f"{vital['dbp']}" if vital["dbp"] else "---").classes(add="inline m-0 p-0")
                  html.span("mmHg").classes(add="bg-inherit ml-0.5")

      #Button
      with html.section().classes(add="w-full p-1 flex flex-row justify-center"):
        ui.button(text="TRIAGE",icon="fa-solid fa-circle-plus fa-sm",color="",on_click=lambda e:self.NewTriagePanel(visit=visit,repeat=True,mini=mini)).classes(add="rounded bg-harmony text-sky-300 text-xl text-bold")

class DispensingManager():
  """A class to display UI for managing studies"""

  def __init__(self,user):
    #DATA
    self.user = user
    self.initial_data()
    
    #UI
    with html.div().classes(add=f"w-full h-full flex flex-col {'' if self.visits else 'justify-center content-center bg-white rounded-b'}"):
      if self.visits:
        #Header
        ui.separator().classes(add="w-full bg-[#09026f]")
        with html.div().classes(add="w-full rounded-t px-2 py-1 bg-harmony flex flex-row"):
          ui.label("TODAY VISITS").classes(add="").classes(add="bg-inherit grow text-2xl lg:text-3xl text-yellow-500 text-bold")
          with html.div().classes(add="bg-inherit") as self.stats_panel:
            self.DispensingStats()
        #Displays
        with html.div().classes(add="w-full grow bg-white rounded-b flex flex-col") as self.display_panel:
          self.PharmacyVisitsDisplay()
      
      else:
        with html.div().classes(add="bg-inherit flex flex-col gap-2 p-3 rounded text-bold fa-fade"):
          ui.label("No clients for now").classes(add="text-xl lg:text-3xl text-center text-rose-500")
          ui.label("Just relax and have fun!").classes(add="italic text-center text-lg lg:text-2xl text-pink-400")

  #FUNCTIONALITIES
  def initial_data(self):
    self.formulary_medicines = [self.format_formulary_medicine(formulary_medicine) for formulary_medicine in admin_processor.get_formulary()]
    _pharmacy_visits = [self.format_pharmacy_visit(visit) for visit in clients_processor.get_pharmacy_visits()]
    self.dispensed_visits = [visit for visit in _pharmacy_visits if self.dispense_status(visit) == "dispensed"]
    self.not_dispensed_visits = [visit for visit in _pharmacy_visits if self.dispense_status(visit) == "not dispensed"]
    self.incomplete_visits = [visit for visit in _pharmacy_visits if self.dispense_status(visit) == "incomplete"]
    self.visits = self.not_dispensed_visits + self.incomplete_visits + self.dispensed_visits
  
  def format_pharmacy_visit(self,visit):

    _formmated_medications_visit = visit._replace(medications=[medication._asdict() for medication in visit.medications])

    _formatted_medical_items_visit = _formmated_medications_visit._replace(medical_items=[medical_item._asdict() for medical_item in visit.medical_items])

    new_visit = _formatted_medical_items_visit._asdict()

    #Prescription mode
    if new_visit["consultations"]:
      new_visit["prescription_mode"] = "consulted"
    else:
      new_visit["prescription_mode"] = "direct"
    
    return new_visit
  
  def format_formulary_medicine(self,formulary_medicine):
    _new_medicine = formulary_medicine._replace(requisitions=[requisition._asdict() for requisition in formulary_medicine.requisitions])
    _new_medicine = _new_medicine._asdict()
    _new_medicine.pop('schemes')

    return _new_medicine

  def dispense_status(self,visit:dict):
    """Returns a string representing payment status of imagings"""

    statuses = set()

    medicines = visit["medications"] + visit["medical_items"]
    
    for medicine in medicines:
      if medicine["dispensed"]:
        statuses.add("dispensed")
      else:
        statuses.add("not dispensed")
    
    if len(statuses) == 1:
      return statuses.pop()
    else:
      return "incomplete"
  
  def format_medicines(self,visit:dict=None):

    def dispensing_balance(inventory):
      dispensing_inventory = sorted([inv for inv in inventory if inv.receiver == "dispensing" or inv.issuer == "dispensing"],key=lambda inv:inv.date,reverse=True)

      if dispensing_inventory:
        latest_inventory = dispensing_inventory[0]
        return latest_inventory.issuer_current_amount if latest_inventory.issuer == "dispensing" else latest_inventory.receiver_current_amount

      else:
        return 0
    
    def client_balance(inventory):
      client_inventory = sorted([inv for inv in inventory if inv.receiver == str(visit["client_id"]) or inv.issuer == str(visit["client_id"])],key=lambda inv:inv.date,reverse=True)

      if client_inventory:
        latest_inventory = client_inventory[0]
        return latest_inventory.issuer_current_amount if latest_inventory.issuer == str(visit["client_id"]) else latest_inventory.receiver_current_amount

      else:
        return 0

    medicines = []

    for visit_medicine in visit["medications"] + visit["medical_items"]:
      medicine = {}
      for formulary_medicine in self.formulary_medicines:
        if visit_medicine["name"].lower() == formulary_medicine["name"].lower():
          medicine["visit_id"] = visit_medicine["visit_id"]
          medicine["name"] = formulary_medicine["name"].lower()
          medicine["type"] = 'tablet' if visit_medicine['name'].lower().split()[-1].startswith("tab") else "capsule" if visit_medicine['name'].lower().split()[-1].startswith('cap') else 'bottle' if (visit_medicine['name'].lower().split()[-1].startswith('syrup') or visit_medicine['name'].lower().split()[-1].startswith('susp')) else 'vial' if visit_medicine['name'].lower().split()[-1].startswith('vial') else 'ampoule' if visit_medicine['name'].lower().split()[-1].startswith('ampoule') else 'item'
          medicine["medication_id"] = visit_medicine["medication_id"] if "medication_id" in visit_medicine else None
          medicine["medical_item_id"] = visit_medicine["medical_item_id"] if "medical_item_id" in visit_medicine else None
          medicine["dosage"] = visit_medicine["dosage"] if "dosage" in visit_medicine else None
          medicine["prescribed_items_no"] = visit_medicine["prescribed_items_no"]
          medicine["dispensed_items_no"] = visit_medicine["prescribed_items_no"]
          medicine["prescribed_on"] = visit_medicine["prescribed_on"]
          medicine["prescriber_id"] = visit_medicine["prescriber_id"]
          medicine["dispensed"] = visit_medicine["dispensed"]
          medicine["dispensing_time"] = visit_medicine["dispensing_time"]
          medicine["dispenser_id"] = self.user.username
          medicine["cancelled"] = visit_medicine["cancelled"]
          medicine["cancelled_on"] = visit_medicine["cancelled_on"]
          medicine["cancelled_by"] = visit_medicine["cancelled_by"]
          medicine["prescription_no"] = visit["prescription_no"]
          medicine["dispensing_balance"] = dispensing_balance(formulary_medicine["inventory"])
          medicine["client_balance"] = client_balance(formulary_medicine["inventory"])
          medicine["requisitions"] = [requisition for requisition in formulary_medicine["requisitions"] if requisition["active"]]
          medicine["payment"] = visit_medicine["payment"]
          #Inventory
          medicine["medicine_id"] = formulary_medicine["medicine_id"].lower()
          medicine["invoice"] = visit["prescription_no"]
          medicine["logger"] = self.user.username
          medicine["issuer"] = "dispensing"
          medicine["receiver"] = visit["visit_id"].split("v")[0]
          medicine["amount"] = visit_medicine["prescribed_items_no"]

          if formulary_medicine["requisitions"]:
            medicine["dispensable"] = True if sum([requisition["balance"] for requisition in formulary_medicine["requisitions"] if requisition["active"]]) else False
          else:
            medicine["dispensable"] = False

          medicines.append(medicine)
    
    return medicines

  def _medicines(self,visit):
    """Returns a string representing payment status of imagings"""

    medicines = visit["medications"] + visit["medical_items"]
    _dispensed = [medicine for medicine in medicines if medicine["dispensed"]]
    _pending = [medicine for medicine in medicines if (medicine["payment"].paid or medicine["payment"].billed) and not (medicine["dispensed"] or medicine["cancelled"])]
    _not_dispensed = [medicine for medicine in medicines if not (medicine["payment"].paid or medicine["payment"].billed) and not (medicine["dispensed"] or medicine["cancelled"])]
    _cancelled = [medicine for medicine in medicines if medicine["cancelled"]]

    return f"<span><span class='{'' if _dispensed else 'hidden'} mr-2'><i class='fas fa-check text-green-500'></i><i class='ml-0.5 '>{len(_dispensed)}</i></span><span class='{'' if _pending else 'hidden'} mr-2'><i class='fas fa-spinner text-yellow-500 fa-spin'></i><i class='ml-0.5 '>{len(_pending)}</i></span><span class='{'' if _not_dispensed else 'hidden'} mr-2'><i class='fas fa-xmark text-red-500'></i><i class='ml-0.5'>{len(_not_dispensed)}</i></span><span class='{'' if _cancelled else 'hidden'} mr-2'><i class='fas fa-ban text-gray-500'></i><i class='ml-0.5 '>{len(_cancelled)}</i></span></span>"
    
  def dispense_medicines(self,medicines):
    """Saves the findings in the database"""

    #
    #Update database
    for medicine in medicines:
      #Modifying requisitions
      dispensable_medicines = medicine["dispensed_items_no"]
      for requisition in medicine["requisitions"]:
        if dispensable_medicines:
          if dispensable_medicines < requisition["balance"]:
            requisition["balance"] -= dispensable_medicines
            dispensable_medicines = 0
          else:
            requisition["balance"] = 0
            requisition["active"] = False
            dispensable_medicines -= requisition["balance"]
    
      status = clients_db.update_medicine(medicine)
      register_inventory(inventory=medicine,dispensed=True)
      for requisition in medicine["requisitions"]:
        admin_db.update_requisition(requisition=requisition,dispense=True)
    
    #Failure notification
    ui.notify(message=status["message"],type=status["type"],position=status["position"])

    #UI Update
    self.initial_data()
    self.DispensingStats()
    self.MedicinesPanel(visit=[visit for visit in self.visits if visit["visit_id"] == medicines[0]["visit_id"]][0])
  
  def client_mini(self,visit):
    """Returns a string of html elements for display in small screens"""

    def GenderIcon(visit):
      """Returns a styled gender icon based on client's gender"""

      genders = {"male":"mars","female":"venus"}
      colors = {"male":"sky-600","female":"pink-600"}

      return f"<span class='fa-solid fa-{genders[visit['client_gender'].lower()]} text-{colors[visit['client_gender'].lower()]}'></span>"
    
    age = f"<span class='ml-1'>{format_age(visit['client_birthdate']).split(' ')[0]} {format_age(visit['client_birthdate']).split(' ')[1][0].upper()}</span>"
    gender = GenderIcon(visit)
    payment_mode = f"<span class=''>{visit['payment_mode'].upper()}</span>"

    return f"<span class='h-full'>{gender}{age}</span>"

  def medicines_mini(self,visit):
    """Returns a string of html elements for display of services in small screens"""
    medicines = visit["medications"] + visit["medical_items"]
    _dispensed = len([medicine for medicine in medicines if medicine["dispensed"]])
    _cancelled = len([medicine for medicine in medicines if medicine["cancelled"]])
    _pending = len([medicine for medicine in medicines if not (medicine["cancelled"] or medicine["dispensed"])])

    dispensed = pending = cancelled = ""

    if _dispensed:
      dispensed = f"<span class='text-green-600'><span class='fas fa-check-double'></span><sup class='ml-0.5 text-bold'>{_dispensed}</sup></span>"

    if _pending:
      pending = f"<span class='text-yellow-600'><span class='fa-solid fa-spinner fa-spin'></span><sup class='ml-0.5 text-bold'>{_pending}</sup></span>"

    if _cancelled:
      cancelled = f"<span class='text-gray-600'><span class='fa-solid fa-ban'></span><sup class='ml-0.5 text-bold'>{_cancelled}</sup></span>"
    
    #Returns
    if _dispensed + _pending + _cancelled:
      return f"<span class='flex flex-row justify-between items-center'>{dispensed}{pending}{cancelled}</span>"
    else:
      return "---"

  #DISPLAYS
  def DispensingStats(self):
    """"""
    self.stats_panel.clear()
    with self.stats_panel:
      with html.span().classes(add="flex flex-row"):
        #Visits
        with ui.label("VISITS").classes(add="rounded-full p-2 text-sky-500"):
          ui.label(str(len(self.visits))).classes(add="ml-1 inline text-bold text-white")
        #Done
        with ui.chip(icon="fa-regular fa-circle-check",text_color="green",color="").classes(add=f"{'' if self.dispensed_visits else 'hidden'} p-2 bg-inherit").tooltip("Completed Triages"):
          ui.label(str(len(self.dispensed_visits))).classes(add="inline text-bold text-white")
        #Pending
        with ui.chip(icon="fas fa-spinner",text_color="yellow",color="").classes(add=f"{'' if self.incomplete_visits+self.not_dispensed_visits else 'hidden'} p-2 bg-inherit").tooltip("Incomplete Triages"):
          ui.label(str(len(self.incomplete_visits + self.not_dispensed_visits))).classes(add="inline text-bold text-white")

  def PharmacyVisitsDisplay(self):
    """"""
    #UI
    self.display_panel.clear()
    with self.display_panel:
      #Large Screen
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/N","field":"sno","width":80},
            {"headerName":"CLIENT ID","field":"client_id","filter":"agTextColumnFilter","width":150},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":350},
            {"headerName":"AGE","field":"age"},
            {"headerName":"GENDER","field":"gender","width":100},
            {"headerName":"PRESCRIPTION MODE","field":"prescription_mode"},
            {"headerName":"PAYMENT","field":"payment_mode","width":100},
            {"headerName":"MEDICINES","field":"medicines"}
          ],
          "rowData":[
            {
              "sno":self.visits.index(visit) + 1,
              "client_id":visit["client_id"],
              "name":visit["client_name"].title(),
              "age":format_age(birthdate=visit["client_birthdate"]),
              "gender":visit["client_gender"].capitalize(),
              "prescription_mode":visit["prescription_mode"].capitalize(),
              "payment_mode":" ".join({mode.upper() for mode in [medicine["payment"].payment_mode for medicine in visit["medications"] + visit["medical_items"]]}),
              "medicines":self._medicines(visit)
            }
          for visit in self.visits
          ]
        },
        theme="quartz",
        html_columns = [7]
      ).classes(add="lg-show grow w-full animate__animated animate__fadeIn animate__slow").on("cellClicked",lambda e:self.DispensingDialog(visit=[visit for visit in self.visits if visit["client_id"] == e.args["data"]["client_id"]][0]))

      #Small Screen
      #Small Screen
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"","field":"client_id","filter":"agTextColumnFilter","width":200},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","floatingFilter":True,"width":300},
            {"headerName":"","field":"specs"},
            {"headerName":"","field":"services"}
          ],
          "rowData":[
            {
              "client_id":visit["client_id"],
              "name":f"{visit['client_name'].split(' ')[0]} {visit['client_name'].split(' ')[1][0]}. {visit['client_name'].split(' ')[2]}".title(),
              "specs":self.client_mini(visit),
              "services":self.medicines_mini(visit)
            } for visit in self.visits
          ]
        },
        theme="quartz",
        html_columns=[2,3]
      ).props(add="").classes(add="lg:hidden grow w-full animate__animated animate__fadeIn").on("cellClicked",lambda e:self.DispensingDialog(visit=[visit for visit in self.visits if visit["client_id"] == e.args["data"]["client_id"]][0]))

  def DispensingDialog(self,visit:dict):

    #DATA
    details = {
      "name":visit["client_name"],
      "short_name":f"{visit['client_name'].split(' ')[0]} {visit['client_name'].split(' ')[-1]}".title(),
      "age":format_age(visit["client_birthdate"]),
      "gender":visit["client_gender"],
      "address":visit["client_address"]}
    
    #FXS
    def close_dialog():
      self.PharmacyVisitsDisplay()
      self.dispensing_dialog.close()

    #UI
    with ui.dialog().props(add="transition-show='scale' transition-hide='scale' transition-duration='500'") as self.dispensing_dialog,html.div().style(add="min-width:100%;min-height:50%;").classes(add="bg-sky-50 ring-1 ring-blue-400 shadow-md shadow-blue-400 overflow-y-hidden"):
      #Dialog Header
      with html.div().classes(add="w-full pr-2 flex flex-row justify-between items-center bg-harmony"):
        with html.div().classes(add="grow"):
          ClientCard(details=details)
        ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=close_dialog).classes(add="bg-inherit shadow-md text-red-500 text-bold")
      
      #Dialog Body
      with html.div().classes(add="w-full") as self.medicines_dialog_panel:
        self.MedicinesPanel(visit=visit)
      
    self.dispensing_dialog.open()

  def MedicinesPanel(self,visit:dict):
    """"""
    #DATA
    medicines = self.format_medicines(visit=visit)
    dispensed_medicines = [medicine for medicine in medicines if medicine["dispensed"]]
    dispensable_medicines = [medicine for medicine in medicines if not (medicine["dispensed"] or medicine["cancelled"])]
    ticked_medicines = []

    #FXS
    def attendee(username):
      attendee = admin_processor.get_staff(username)
      return f"{attendee.first_name} {attendee.last_name}"
      
    def pick_ticked_medicine(ticked_medicine:str,ticked_medicine_count:int,ticked:bool):
      """Returns a list of ticked medicines"""
      if ticked:
        for medicine in dispensable_medicines:
          if medicine["medicine_id"] == ticked_medicine:
            medicine["dispensed_items_no"] = ticked_medicine_count
            ticked_medicines.append(medicine)
      else:
        for medicine in ticked_medicines:
          if medicine["medicine_id"] == ticked_medicine:
            ticked_medicines.remove(medicine)

    def dispense_all(medicines:list):
      """Dispenses all medicines in the ticked_medicines list"""
      
      if medicines:
        self.dispense_medicines(medicines=medicines)
          
      else:
        ui.notify(message="No medicine selected",type="warning",position="center")
      
    #UI
    self.medicines_dialog_panel.clear()
    with self.medicines_dialog_panel.classes(add="p-2"):
      with ui.scroll_area().classes(add="w-full h-[400px] pb-2 bg-white rounded shadow-md shadow-[307004d] animate__animated animate__fadeIn animate__slow"):
        for medicine in medicines:
          with html.div().classes(add="w-full p-1 rounded bg-sky-50 grid grid-cols-3 gap-1 content-center shadow-md shadow-[#07004d]"):
            #Medicine name
            with html.div().classes(add="col-span-3 lg:col-span-1 flex flex-row"):
              #Checkbox
              ui.checkbox(on_change=lambda e:pick_ticked_medicine(
                ticked_medicine=e.sender.parent_slot.parent.slots["default"].children[1].slots["default"].children[0].props["id"],
                ticked_medicine_count=e.sender.parent_slot.parent.parent_slot.parent.slots["default"].children[1].slots["default"].children[6].props["model-value"]["label"],
                ticked=e.value
              )).props(add=f"{'' if medicine['payment'].paid or medicine['payment'].billed else 'disable'}").classes(add=f"{'hidden' if medicine['dispensed'] or medicine['cancelled'] else ''} bg-white tiki")
              #Name
              with html.div().classes(add="grow flex flex-col justify-center"):
                html.div(f"{medicines.index(medicine) + 1}. {medicine['name'].upper()}").props(add=f"id={medicine['medicine_id']}").classes(add="w-full rounded-sm m-0 p-0 bg-inherit text-sky-700 text-lg text-bold")
                html.div(medicine["dosage"] if medicine["dosage"] else "---").classes(add="w-full bg-inherit text-base font-medium italic")
            
            #Details
            with html.div().classes(add=f"col-span-3 lg:col-span-2 grid {'grid-cols-12' if medicine['payment'].paid or medicine['payment'].billed else 'grid-cols-13'} gap-1 content-center"):
              #Timeframe
              ui.chip(text=f"{format_age(datetime.fromisoformat(medicine['prescribed_on'])) if isinstance(medicine['prescribed_on'],str) else format_age(medicine['prescribed_on']) } ago",icon="fa-regular fa-clock fa-lg",text_color="sky-900",color="").classes(add="col-span-4 lg:col-span-2 rounded-sm ml-5 px-0 bg-inherit text-base font-semibold")
              #Odered by
              ui.chip(text=attendee(medicine["prescriber_id"]),icon="fa-solid fa-user-doctor fa-lg",text_color="sky-900",color="").classes(add="col-span-5 lg:col-span-2 rounded-sm mx-0 px-0 bg-inherit text-base text-bold")
              #Payment status
              ui.chip(text="Paid" if medicine["payment"].paid else "Billed" if medicine["payment"].billed else "Not Paid",icon=f"{'fa-regular fa-circle-check' if medicine['payment'].paid else 'fa-solid fa-file-invoice' if medicine['payment'].billed else 'fa-regular fa-circle-xmark'} fa-lg",text_color="green" if medicine["payment"].paid else "purple" if medicine["payment"].billed else "red",color="").classes(add=f"col-span-3 {'lg:col-span-1' if medicine['payment'].paid or medicine['payment'].billed else 'lg:col-span-2'} rounded-sm mx-0 px-0 bg-inherit text-base text-bold")
              #Dispensing status
              ui.chip(
                text="Cancelled" if medicine["cancelled"] else "Dispensed" if ((medicine["payment"].paid or medicine["payment"].billed) and medicine["dispensed"]) else "Pending" if ((medicine["payment"].billed or medicine["payment"].paid) and not medicine["dispensed"]) else "Not dispensed",
                icon=f"{'fas fa-ban' if medicine['cancelled'] else 'fa-regular fa-circle-check' if ((medicine['payment'].paid or medicine['payment'].billed) and medicine['dispensed']) else 'fa-solid fa-spinner fa-spin' if ((medicine['payment'].billed or medicine['payment'].paid) and not medicine['dispensed']) else 'fa-regular fa-circle-xmark fa-flip'} fa-lg",
                text_color="gray" if medicine["cancelled"] else "green" if ((medicine["payment"].paid or medicine["payment"].billed) and medicine["dispensed"]) else "orange" if ((medicine["payment"].billed or medicine["payment"].paid) and not medicine["dispensed"]) else "red",
                color=""
              ).classes(add=f"col-span-4 justify-self-center lg:col-span-2 lg:justify-self-start rounded-sm mx-0 p-0 bg-inherit text-base text-bold text-wrap")
              #Store status
              ui.chip(text=f"{medicine['dispensing_balance']:,.0f}",icon="fas fa-house-medical fa-lg",text_color="sky-600",color="").classes(add=f"{'hidden' if medicine['dispensed'] or medicine['cancelled'] else ''} col-span-2 mx-1 px-0 bg-inherit text-lg text-bold")
              #Prescribed no
              ui.chip(text=f"{medicine['dispensed_items_no'] if medicine['dispensed_items_no'] else medicine['prescribed_items_no']}",icon=f"fas fa-{'tablets' if medicine['type'] == 'tablet' else 'capsules' if medicine['type'] == 'capsule' else 'prescription-bottle' if medicine['type'] == 'bottle' else 'vial' if medicine['type'] == 'vial' or medicine['type'] == 'ampoule' else 'thermometer'} fa-lg",color="",text_color=f"{'green-600' if medicine['dispensed'] else 'sky-600'}").classes(add=f"{'hidden' if medicine['cancelled'] or not medicine["dispensed"] else ''} col-span-2 lg:col-span-1 mx-0 px-0 bg-inherit text-lg text-bold")
              #Dispensed no
              ui.select(options=[i for i in range(1,medicine["prescribed_items_no"]+1)],value=medicine["prescribed_items_no"],with_input=True).props(add=f"type='number' dense min=1 max={medicine['prescribed_items_no']} {'' if medicine['payment'].paid or medicine['payment'].billed else 'readonly'}").classes(add=f"{'hidden' if medicine['dispensed'] or medicine['cancelled'] else ''} col-span-2 lg:col-span-1 w-[100%] my-2 px-2 bg-white shadow-md shadow-[#07004d] rounded text-lg")
              #Medication_id holder
              html.small(medicine["medicine_id"]).classes("hidden") #Medication_id not for purpose of display
              #Dispense button
              ui.button(text="Dispense",color="",on_click=lambda e:self.dispense_medicines(medicines=[medicine for medicine in medicines if medicine["medicine_id"].lower() == e.sender.parent_slot.parent.slots["default"].children[7]._text.lower()])).classes(add=f"{'hidden' if medicine['dispensed'] or medicine['cancelled'] else ''} col-span-4 lg:col-span-2 px-2 bg-harmony text-yellow-500 text-lg text-bold")
              #Dispensing information
              if medicine["dispensed"]:
                #Dispenser
                ui.chip(text=attendee(medicine["dispenser_id"]),icon="fa-solid fa-hospital-user fa-lg",text_color="green-600",color="").classes(add="col-span-2 justify-self-end rounded mx-0 px-2 bg-inherit capitalize text-base text-bold")
                #Timeframe
                ui.chip(text=f"{format_age(datetime.fromisoformat(medicine['dispensing_time'])) if isinstance(medicine['dispensing_time'],str) else format_age(medicine['dispensing_time'])} ago",icon="fa-regular fa-clock",text_color="green-600",color="").classes(add="col-span-2 justify-self-end rounded-sm mx-0  bg-inherit text-base text-bold")
                
      #Buttons
      with html.div().classes(add="w-full p-3 flex flex-col lg:flex-row justify-center items-center gap-3"):
        ui.label(f"{len(medicines)} MEDICINE{'S' if len(medicines)>1 else ''}").classes(add="w-full text-center lg:text-start lg:w-auto lg:grow px-3 font-semibold text-gray-500 text-base italic self-end")
        with html.div().classes(add="grow flex flex-row justify-end gap-10"):
          #Dispense all button
          if dispensable_medicines:
            ui.button(text="DISPENSE TICKED MEDICINES",color="",on_click=lambda e:dispense_all(medicines=ticked_medicines)).classes(add="rounded bg-harmony shadow-md shadow-[#07004d] text-yellow-500 text-lg text-bold")
          #Prin Button
          if dispensed_medicines:
            ui.button(text="PRINT RECEIPT",icon="fas fa-receipt",color="",on_click=lambda e:self.print_receipt(medicines=medicines)).classes(add="hidden rounded bg-harmony shadow-md shadow-[#07004d] text-yellow-300 text-lg text-bold")

  def print_receipt(self,medicines):
    ui.notify(medicines)
    ###Under maintanace


#CLINICIAN
class ConsultationsManager():
  """"""
  def __init__(self,user):
    #DATA
    self.user = user
    self.initial_data()

    #UI
    with html.div().classes(add="grow w-full flex flex-col"):
      #Separator
      for i in range(2):
        ui.separator().classes(add="w-full bg-[#09026f]")
      
      #Header
      with html.section().classes(add="w-full p-1 bg-harmony flex flex-row justify-between items-center"):
        ui.label("CONSULTATIONS").classes(add="grow rounded-t text-2xl lg:text-3xl text-yellow-500 font-semibold")
        with html.span().classes(add="") as clocker:
          label = ui.label().classes(add="inline text-yellow-500 font-bold")
          ui.timer(1.0, lambda: label.set_text(f'{datetime.now().strftime("%a %d %b %Y")}    {datetime.now():%X}'))


      #Body
      with html.div().classes(add="grow w-full p-0 flex flex-col justify-center content-center") as self.consultations_panel:
        if self.consulted_visits:
          self.ConsultationsAggrid(visits=self.consulted_visits)
        else:
          ui.label("No clients for consultation now!").classes(add="m-5 text-red-600 text-xl lg:text-2xl italic font-semibold fa-fade")
  
  #FUNCTIONALITIES
  def initial_data(self):
    #Consultations
    self.active_clients = sorted([client for client in get_clients() if client.client_id in [visit.client_id for visit in get_active_visits()]],key=lambda e:e.visits[-1].start_time,reverse=True)
    self.raw_consultations = [visit for visit in [client.visits[-1] for client in self.active_clients] if visit.consultations and (visit.consultations[0].payment.paid or visit.consultations[0].payment.billed)]
    self.new_consultations = [visit for visit in self.raw_consultations if not visit.consultations[0].initiated]
    self.cont_consultations = [visit for visit in self.raw_consultations if visit.consultations[0].initiated]
    self.consulted_clients = [client for client in self.active_clients if client.client_id in [consult.client_id for consult in self.new_consultations + self.cont_consultations]]
    self.consulted_visits = self.consultations = self.new_consultations + self.cont_consultations
    self.lab_consultations = []
    self.imaging_consultations = []
    self.procedure_consultations = []
    self.pharmacy_consultations = []

    self.diagnoses = get_diagnoses()
    self.active_consultation = None

  def format_active_consultation(self,consult):

    consultation = consult._asdict()
    consultation["clinical_history"] = consult.clinical_history._asdict()
    consultation["general_exam"] = consult.general_exam._asdict()
    consultation["orodental_exam"] = consult.orodental_exam._asdict()

    return consultation

  def client_mini(self,visit):
    """Returns a string of html elements for display in small screens"""

    def GenderIcon(visit):
      """Returns a styled gender icon based on client's gender"""

      genders = {"male":"mars","female":"venus"}
      colors = {"male":"sky-600","female":"pink-600"}

      return f"<span class='fa-solid fa-{genders[visit.client_gender.lower()]} text-{colors[visit.client_gender.lower()]}'></span>"
    
    age = f"<span class='ml-1'>{format_age(visit.client_birthdate).split(' ')[0]} {format_age(visit.client_birthdate).split(' ')[1][0].upper()}</span>"
    gender = GenderIcon(visit)
    payment_mode = f"<span class=''>{visit.payment_mode.upper()}</span>"

    return f"<span class='h-full'>{gender}{age}</span>"
  
  def services(self,imagings=None,medicines=None,procedures=None):

    if procedures:
      _done = [procedure for procedure in procedures if procedure.done]
      _pending = [procedure for procedure in procedures if (procedure.payment.paid or procedure.payment.billed) and not (procedure.done or procedure.cancelled)]
      _not_done = [procedure for procedure in procedures if not (procedure.payment.paid or procedure.payment.billed) and not (procedure.done or procedure.cancelled)]
      _cancelled = [procedure for procedure in procedures if procedure.cancelled]

      return f"<span><span class='{'' if _done else 'hidden'} mx-0.5'><i class='fas fa-check text-green-500'></i><i class='ml-0.5 '>{len(_done)}</i></span><span class='{'' if _pending else 'hidden'} mx-0.5'><i class='fas fa-spinner text-yellow-500 fa-spin'></i><i class='ml-0.5 '>{len(_pending)}</i></span><span class='{'' if _not_done else 'hidden'} mx-0.5'><i class='fas fa-xmark text-red-500 '></i><i class='ml-0.5'>{len(_not_done)}</i></span><span class='{'' if _cancelled else 'hidden'} mx-0.5'><i class='fas fa-ban text-gray-500'></i><i class='ml-0.5'>{len(_cancelled)}</i></span></span>"
    
    elif imagings:
      _processed = [imaging for imaging in imagings if imaging.processed]
      _pending = [imaging for imaging in imagings if (imaging.payment.paid or imaging.payment.billed) and not (imaging.processed or imaging.cancelled)]
      _not_processed = [imaging for imaging in imagings if not (imaging.payment.paid or imaging.payment.billed) and not (imaging.processed or imaging.cancelled)]
      _cancelled = [imaging for imaging in imagings if imaging.cancelled]

      return f"<span><span class='{'' if _processed else 'hidden'} mx-0.5'><i class='fas fa-check text-green-500'></i><i class='ml-0.5 '>{len(_processed)}</i></span><span class='{'' if _pending else 'hidden'} mx-0.5'><i class='fas fa-spinner text-yellow-500 fa-spin'></i><i class='ml-0.5 '>{len(_pending)}</i></span><span class='{'' if _not_processed else 'hidden'} mx-0.5'><i class='fas fa-xmark text-red-500'></i><i class='ml-0.5'>{len(_not_processed)}</i></span><span class='{'' if _cancelled else 'hidden'} mx-0.5'><i class='fas fa-ban text-gray-500'></i><i class='ml-0.5 '>{len(_cancelled)}</i></span></span>"
     
    elif medicines:
      _dispensed = [medicine for medicine in medicines if medicine.dispensed]
      _pending = [medicine for medicine in medicines if (medicine.payment.paid or medicine.payment.billed) and not (medicine.dispensed or medicine.cancelled)]
      _not_dispensed = [medicine for medicine in medicines if not (medicine.payment.paid or medicine.payment.billed) and not (medicine.dispensed or medicine.cancelled)]
      _cancelled = [medicine for medicine in medicines if medicine.cancelled]

      return f"<span><span class='{'' if _dispensed else 'hidden'} mx-0.5'><i class='fas fa-check text-green-500'></i><i class='ml-0.5 '>{len(_dispensed)}</i></span><span class='{'' if _pending else 'hidden'} mx-0.5'><i class='fas fa-spinner text-yellow-500 fa-spin'></i><i class='ml-0.5 '>{len(_pending)}</i></span><span class='{'' if _not_dispensed else 'hidden'} mx-0.5'><i class='fas fa-xmark text-red-500'></i><i class='ml-0.5'>{len(_not_dispensed)}</i></span><span class='{'' if _cancelled else 'hidden'} mx-0.5'><i class='fas fa-ban text-gray-500'></i><i class='ml-0.5 '>{len(_cancelled)}</i></span></span>"
    
    else:
      return "---"

  def services_mini(self,visit):
    """Returns a string of html elements for display of services in small screens"""

    imgs = procs = meds = ""

    if visit.imagings:
      imgs = f"<span class=''><span class='fas fa-x-ray'></span><sup class=''>{len(visit.imagings)}</sup></span>"

    if visit.procedures:
      procs = f"<span class=''><span class='fa-solid fa-head-side-mask'></span><sup class=''>{len(visit.procedures)}</sup></span>"

    if visit.medications + visit.medical_items:
      meds = f"<span class=''><span class='fa-solid fa-pills'></span><sup class=''>{len(visit.medications + visit.medical_items)}</sup></span>"
    
    #Returns
    if imgs + procs + meds:
      return f"<span class='flex flex-row justify-between items-center'>{imgs}{procs}{meds}</span>"
    else:
      return "---"

  def vitals(self,visit:dict):
    """Returns status of vital signs measurement and their interpretation"""

    if visit.vital_signs:
      vitals = visit.vital_signs[-1]
      temp,sbp,dbp,pr,rr,osat = vitals.temperature,vitals.sbp,vitals.dbp,vitals.pulse_rate,vitals.resp_rate,vitals.o2sat

      if temp or sbp or dbp or rr or osat:
        return f"<span><span class='{'' if temp else 'hidden'} mr-1'><i class='mr-0.5 '>T</i><i class='fas {'fa-check text-green-600' if self.normal(t=temp) else 'fa-exclamation fa-fade text-red-600'}'></i></span><span class='{'' if sbp else 'hidden'} mr-1'><i class='mr-0.5 '>BP</i><i class='fas {'fa-check text-green-600' if self.normal(sbp=sbp,dbp=dbp) else 'fa-exclamation fa-fade text-red-600'}'></i></span><span class='{'' if pr else 'hidden'} mr-1'><i class='mr-0.5'>PR</i><i class='fas {'fa-check text-green-600' if self.normal(pr=pr) else 'fa-exclamation fa-fade text-red-600'}'></i></span><span class='{'' if rr else 'hidden'} mr-1'><i class='mr-0.5'>RR</i><i class='fas {'fa-check text-green-600' if self.normal(rr=rr) else 'fa-exclamation fa-fade text-red-600'}'></i></span><span class='{'' if osat else 'hidden'}'><i class='mr-0.5'>O₂</i><i class='fas {'fa-check text-green-600' if self.normal(osat=osat) else 'fa-exclamation fa-fade text-red-600'}'></i></span></span>"
      else:
        return "-----"
    else:
      return "-----"

  def normal(self,sbp:int|None=None,dbp:int|None=None,pr:int|None=None,rr:int|None=None,t:float|None=None,osat:int|None=None):
    """Returns True if vital is within normal range"""
    
    #Temperature
    if t:
      if t <= 37.5 and t >= 36.5:
        return True
      else:
        return False
      
    #Blood Pressure
    if sbp and dbp:
      if (sbp < 140 and sbp >= 100): #and (dbp < 90 and dbp >= 60):
        return True
      else:
        return False

    #Pulse Rate
    if pr:
      if pr <= 100 and pr >= 60:
        return True
      else:
        return False

    #Respiratory Rate
    if rr:
      if rr <= 20 and rr >= 12:
        return True
      else:
        return False

    #Oxygen Saturation
    if osat:
      if osat >= 95:
        return True
      else:
        return False

  def last_visit(self,client):
    """Returns the last visit of client as a namedtuple object"""

    return sorted(client.visits,key=lambda visit:visit.start_time,reverse=True)[0]
  
  def register_appointment(self,appointment:dict):
    """Register a new appointment and store data to database"""
    
    appointment["attendee_id"] = get_staff_username(first_name=appointment["consultant"].split(" ")[0].lower(),last_name=appointment["consultant"].split(" ")[0].lower(),role="doctor")

    status = clients_db.register_appointment(appointment)

    #Notification
    ui.notify(message=status["message"],type=status["type"],position="center")
    
  #DISPLAYS
  def ConsultationsAggrid(self,visits:list[dict]):
    """"""
    #UI
    self.consultations_panel.clear()
    with self.consultations_panel:
      #Large screen
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/N","field":"sno","width":70},
            {"headerName":"CLIENT ID","field":"client_id","filter":"agTextColumnFilter","floatingFilter":True,"width":130},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","floatingFilter":True},
            {"headerName":"AGE","field":"age","width":100},
            {"headerName":"GENDER","field":"gender","width":100},
            {"headerName":"PAYMENT","field":"payment","width":110},
            {"headerName":"VITAL SIGNS","field":"vitals","width":220},
            {"headerName":"IMAGINGS","field":"imagings"},
            {"headerName":"PROCEDURES","field":"procedures"},
            {"headerName":"MEDICATIONS","field":"medications"}
          ],
          "rowData":[
            {
              "sno":visits.index(visit) + 1,
              "client_id":visit.client_id,
              "name":visit.client_name.title(),
              "age":f"{format_age(visit.client_birthdate).split(' ')[0]} {format_age(visit.client_birthdate).split(' ')[1]}",
              "gender":visit.client_gender.capitalize(),
              "payment":visit.payment_mode.upper(),
              "vitals":self.vitals(visit),
              "imagings":self.services(imagings=visit.imagings),
              "procedures":self.services(procedures=visit.procedures),
              "medications":self.services(medicines=visit.medications+visit.medical_items),
            } for visit in visits
          ]
        },
        theme="quartz",
        html_columns=[6,7,8,9]
      ).props(add="").classes(add="lg-show grow w-full animate__animated animate__fadeIn").on("cellClicked",lambda e:self.ConsultationsDialog(client=[client for client in self.consulted_clients if client.client_id == e.args["data"]["client_id"]][0]))

      #Small screen
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"","field":"client_id","filter":"agTextColumnFilter","width":200},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","floatingFilter":True,"width":300},
            {"headerName":"","field":"specs"},
            {"headerName":"","field":"services"}
          ],
          "rowData":[
            {
              "client_id":visit.client_id,
              "name":f"{visit.client_name.split(' ')[0]} {visit.client_name.split(' ')[-1]}".title(),
              "specs":self.client_mini(visit),
              "services":self.services_mini(visit)
            } for visit in visits
          ]
        },
        theme="quartz",
        html_columns=[2,3]
      ).props(add="").classes(add="lg:hidden grow w-full animate__animated animate__fadeIn").on("cellClicked",lambda e:self.ConsultationsDialog(client=[client for client in self.consulted_clients if client.client_id == e.args["data"]["client_id"]][0]))

  async def ConsultationsDialog(self, client):
    """Displays from consultations in the previous visits - OPTIMIZED"""
    #DATA
    details = {
      "name": f"{client.first_name} {client.middle_name if client.middle_name else ''} {client.last_name}".title(),
      "short_name":f"{client.first_name} {client.middle_name[0] if client.middle_name else ''} {client.last_name}".title(),
      "age": format_age(birthdate=client.birthdate, short=True),
      "gender":client.gender,
      "address":client.address,
      "last_visit": f"{format_age(client.visits[-2].start_time)} ago" if len(client.visits) > 1 else "---"
    }
    
    visits = sorted(client.visits, key=lambda e: e.start_time, reverse=True)
    
    #FXS
    @ui.refreshable
    async def dialog_content():
      with html.div().style(add="min-width:100%;min-height:90%;").classes(add="bg-sky-50 p-0.5 flex flex-col gap-0"):
        #Dialog Header
        with html.div().classes(add="w-full pr-2 rounded-t flex flex-row justify-between items-center bg-harmony"):
          with html.div().classes(add="grow"):
            ClientCard(details,short=True)
          ui.button(icon="fa-regular fa-circle-xmark", color="",on_click=self.consultations_dialog.close).classes(add="bg-inherit size-8 rounded-full text-red-500")
      
        #Dialog Body
        with html.div().classes(add="grow w-full flex flex-col") as self.visit_panel:
          #Separator
          for i in range(2):
            ui.separator().classes(add="w-full bg-[#09026f]")
          
          #Tabs
          with html.div().classes(add="lghidden w-full flex flex-col"):
            with html.div().classes(add="w-full pl-1 bg-harmony shadow-sm shadow-[#07004d] flex flex-row gap-0.5 items-center"):
              ui.label(len(visits)).classes(add="m-0 size-8 rounded-full flex flex-row justify-center items-center bg-harmony ring-1 ring-offset-1 ring-[#07004d] text-bold text-lg lg:text-xl text-yellow-500")
              with ui.tabs(value=visits[0].visit_id).props(add="inline-label mobile-arrows outside-arrows active-class='text-sky-700 font-bold' align='left'").classes(add="grow m-0 pl-1 bg-sky-50") as visits_mini_tabs:
                for i, visit in enumerate(visits):
                  ui.tab(name=visit.visit_id,label=f"{i + 1}. {visit.start_time.strftime('%d %b %Y')}")

          #Tab Panels
          with html.div().classes(add="lghidden w-full grow flex flex-col"):
            with ui.tab_panels(tabs=visits_mini_tabs,value=visits[0].visit_id).props(add="animated infinite transition-prev='jump-right' transition-next='jump-left' transition-duration='700'").classes(add="bg-inherit grow w-full rounded-b grid grid-cols-1 shadow-sm shadow-black") as xxx:
              with ui.tab_panel(name=visit.visit_id).classes(add="p-0 flex flex-col gap-0") as self.visit_tab:
                for visit in visits:
                  if visit.active:
                    await self.ActiveConsultationPanel(visit)
                  else:
                    await self.PreviousVisitPanel(visit)

    # UI
    self.consultations_dialog = ui.dialog().props(add="transition-show='jump-up' transition-hide='jump-down' transition-duration='500'")
    
    with self.consultations_dialog:
      await dialog_content()
    
    self.consultations_dialog.open()
  
  async def PreviousVisitPanel(self, visit: dict):
    """Optimized previous visit display"""
    # Load data only when needed
    if not hasattr(self, '_cached_visits'):
      self._cached_visits = {}
    
    visit_id = visit.get('visit_id')
    
    # Check cache first
    if visit_id in self._cached_visits:
      self.visit_tab.clear()
      self.visit_tab.add(self._cached_visits[visit_id])
      return
    
    # Otherwise render fresh (with loading indicator)
    self.visit_tab.clear()
    with self.visit_tab:
      loading = ui.spinner(size='lg', color='primary')
        
      # Use async to prevent blocking
      async def render_content():
        try:
          content = await self._render_visit_content(visit)
          self._cached_visits[visit_id] = content
          loading.delete()
          self.visit_tab.add(content)
        except Exception as e:
          loading.delete()
          ui.notify(f"Error loading visit: {e}", type='negative')
      
      ui.timer(0.1, render_content, once=True)

  async def ActiveConsultationPanel(self,visit):
    """Optimized active consultation panel"""
    self.active_visit = visit
    self.active_consultation = visit.consultations[0]

    #Load triage data
    async def load_data():
      _anthrops = sorted([a for a in visit.anthropometrics if a.done and a.weight],key=lambda a: a.anthropometrics_time, reverse=True)
      anthrops = _anthrops[0] if _anthrops else visit.anthropometrics[-1] if visit.anthropometrics else None
      
      _vitals = sorted([v for v in visit.vital_signs if v.done],key=lambda v: v.vitals_time, reverse=True)
      vitals = _vitals[0] if _vitals else visit.vital_signs[-1] if visit.vital_signs else None
      
      return anthrops, vitals
    
    # Show loading while fetching
    self.visit_tab.clear()
    with self.visit_tab.classes(add="justify-center items-center"):
      loading = ui.spinner(size='lg',type="puff")
      
      async def render():
        anthrops, vitals = await load_data()
        loading.delete()
        await self._render_active_consultation(visit, anthrops, vitals)
      
      ui.timer(0.1, render, once=True)

  async def _render_active_consultation(self,visit,anthrops,vitals):
    """Render active consultation content"""
    #DATA
    self.active_consultation = self.format_active_consultation(visit.consultations[0])
    self.active_diagnoses = [diagnosis._asdict() for diagnosis in self.active_consultation["diagnoses"]]

    def default_display(consultation=None,visit=None,attendee_id=None,parent=None):
      pass

    clerkship_sections = {
      "present history":(self.PresentingIllness,self.PresentingIllness),
      "medical & surgical history":(default_display,self.PastMedicalSurgicalHistory),
      "family & social history":(default_display,self.FamilySocialHistory),
      "physical examination":(default_display,self.PhysicalExamination),
      "provisional diagnoses":(default_display,self.ProvisionalDiagnoses),
      "workup":(default_display,ImagingsForm),
      "definitive diagnoses":(default_display,self.DefinitiveDiagnoses),
      "management":(default_display,ManagementPlanForm)
    }
    clerkship_sections_titles = list(clerkship_sections.keys())

    async def render_display(e):
      for tab in e.sender.slots['default'].children:
        if tab.props['name'] == e.value:
          tab.clear()
          with tab:
            with html.div().classes(add="grow w-full p-1 flex flex-col justify-between gap-2"):
              clerkship_sections[e.value][1](parent=self,visit=visit,consultation=self.active_consultation,attendee_id=self.user.username)

    #UI
    self.visit_tab.clear()
    with self.visit_tab.classes(remove="justify-center items-center"):
      with html.section().classes(add="bg-harmony w-full flex flex-col lg:flex-row"):
        #Anthropometrics
        with html.div().classes(add=f"bg-inherit flex flex-row justify-center items-center lg:justify-around gap-3"):
          #BWt
          with ui.chip(icon="fa-solid fa-weight-scale",color="",text_color="yellow-8").props(add="dense").classes(add="bg-inherit m-0 rounded text-base lg:text-lg text-yellow-500"):
            ui.badge(text=f"{anthrops.weight if anthrops.weight else '---'} {'kg' if anthrops.weight else ''}",color="").classes(add=f"bg-inherit ml-0.5 text-base text-bold text-sky-300")
          #height/Length
          with ui.chip(icon="fa-solid fa-ruler-vertical",color="",text_color="yellow-8").props(add="dense").classes(add="bg-inherit m-0 rounded text-base lg:text-lg text-yellow-500"):
            ui.badge(text=f"{anthrops.height if anthrops.height else '---'} {'cm' if anthrops.height else ''}",color="").classes(add=f"bg-inherit ml-0.5 text-base text-bold text-sky-300")
          
          if get_duration(visit.client_birthdate)["years"] < 2:
            #MUAC
            with ui.chip(text="MUAC",color="").classes(add="hidden m-0 p-0 bg-inherit rounded text-md text-bold text-yellow-500"):
              ui.badge(text=f"{anthrops.muac if anthrops.muac else '---'} {'cm' if anthrops.muac else ''}",color="").props(add="dense").classes(add=f"bg-inherit ml-0.5 text-lg text-bold text-sky-300")
            #Head Circumference
            with ui.chip(text="HC",color="").classes(add="hidden m-0 p-0 bg-inherit rounded text-md text-bold text-yellow-500"):
              ui.badge(text=f"{anthrops.head_circum if anthrops.head_circum else '---'} {'cm' if anthrops.head_circum else ''}",color="").classes(add=f"bg-inherit ml-0.5 text-lg text-bold text-sky-300")

        #Vitals
        with html.div().classes(add="grow bg-inherit p-1 flex flex-row justify-around items-center text-bold"):
          #T
          with ui.chip(icon="fa-solid fa-temperature-high",text_color="yellow-8",color="").classes(add="bg-inherit m-0 px-0.5 py-0 rounded text-md text-yellow-500"):
            ui.badge(text=f"{vitals.temperature if vitals.temperature else '---'} {'℃' if vitals.temperature else ''}",color="").classes(add=f"bg-inherit m-0 p-0 text-base text-bold text-{'sky-300' if (not vitals.temperature) else 'green-400' if self.normal(t=vitals.temperature) else 'red-600'}")
          #BP
          with ui.chip(icon="fa-solid fa-pump-medical",text_color="yellow-8",color="").classes(add=f"{'hidden' if get_duration(visit.client_birthdate)['years'] < 12 else ''} bg-inherit m-0 p-0 rounded text-base text-bold"):
            ui.badge(text=f"{vitals.sbp if vitals.sbp else '---'}/{vitals.dbp if vitals.dbp else '---'} {'mmHg' if vitals.sbp or vitals.dbp else ''}",color="").classes(add=f"bg-inherit m-0 p-0 text-base text-bold text-{'sky-300' if ((not vitals.sbp) and (not vitals.dbp)) else 'green-400' if (self.normal(sbp=vitals.sbp) or self.normal(dbp=vitals.dbp)) else 'red-600'}")
          #PR
          with ui.chip(icon="fa-solid fa-heart-pulse",text_color="yellow-8",color="").classes(add="bg-inherit m-0 px-0.5 py-0 rounded text-md text-yellow-500"):
            ui.badge(text=f"{vitals.pulse_rate if vitals.pulse_rate else '---'} {'bpm' if vitals.pulse_rate else ''}",color="").classes(add=f"bg-inherit m-0 p-0 text-base text-bold text-{'sky-300' if (not vitals.pulse_rate) else 'green-400' if self.normal(t=vitals.pulse_rate) else 'red-600'}")
          #RR
          with ui.chip(icon="fa-solid fa-lungs",text_color="yellow-8",color="").classes(add="bg-inherit m-0 px-0.5 py-0 rounded text-md text-yellow-500"):
            ui.badge(text=f"{vitals.resp_rate if vitals.resp_rate else '---'} {'cpm' if vitals.resp_rate else ''}",color="").classes(add=f"bg-inherit m-0 p-0 text-base text-bold text-{'sky-300' if (not vitals.resp_rate) else 'green-400' if self.normal(t=vitals.resp_rate) else 'red-600'}")
          #O2SAT
          with ui.chip(text="O₂",text_color="yellow-8",color="").classes(add="bg-inherit m-0 p-0 rounded text-base text-bold"):
            ui.badge(text=f"{vitals.o2sat if vitals.o2sat else '---'} {'%' if vitals.o2sat else ''}",color="").classes(add=f"bg-inherit m-0 ml-0.5 p-0 text-base text-bold text-{'sky-300' if (not vitals.o2sat) else 'green-400' if self.normal(osat=vitals.o2sat) else 'red-600'}")

      with html.section().classes(add="grow w-full flex flex-col"):
        # Use lazy tabs
        with html.div().classes(add="order-last w-full p-0 rounded-b shadow-sm shadow-[#07004d]"):
          with ui.tabs(value=clerkship_sections_titles[0]).props(add='''dense inline-label mobile-arrows outside-arrows :vertical="$q.screen.gt.sm" active-class="text-sky-500"''').classes(add="w-full rounded-b bg-harmony py-1 text-yellow-500 font-bold") as clerkship_tabs:
            for section_title in clerkship_sections_titles:
              ui.tab(section_title)
        
        with ui.tab_panels(clerkship_tabs,value=clerkship_sections_titles[0],on_change=lambda e:render_display(e)).props(add="animated infinite transition-prev='jump-right' transition-next='jump-left' transition-duration='700'").classes(add="bg-inherit grow w-full grid grid-cols-1 animate__animated aimate__fadeIn") as xtabs:
          for section_title,section_func in clerkship_sections.items():
            with ui.tab_panel(section_title).props(add="keep-alive").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col"):
              with html.div().classes(add="grow w-full flex flex-col justify-center items-center"):
                section_func[0](consultation=visit.consultations[0],visit=visit,attendee_id=self.user.username,parent=self)
                
  def xxxPreviousVisitPanel(self,visit:dict):
    """A display for previous visits"""
    #DATA
    consultation = visit["consultations"][0] if visit["consultations"] else None
    clinical_history = visit["consultations"][0]["clinical_history"] if visit["consultations"] else None
    
    #FXS
    def hpis(clinical_history):
      complaints,hpis = clinical_history["chief_complaints"],[clinical_history["hpi1"],clinical_history["hpi2"],clinical_history["hpi3"]]
      hpis = zip(complaints,hpis)
      return list(hpis)

    #UI
    self.visit_tab.clear()
    with self.visit_tab.classes(add="bg-sky-100"):
      with ui.scroll_area().classes(add="h-[600px] lg:h-[500px]"):
        with ui.timeline(side="right",layout="dense").classes(add=""):
          #Consultation
          if visit["consultations"]:
            #HPI
            with ui.timeline_entry(icon="fas fa-notes-medical").props(add="color='green-6'") as hpi_entry:
              #Subtitle
              with hpi_entry.add_slot("subtitle"):
                if clinical_history["history_time"]:
                  with ui.label(clinical_history["history_time"].strftime("%a %-d %b %Y")).classes(add="text-base text-bold text-blue-700"):
                    ui.label(clinical_history["history_time"].strftime("%H:%M")).classes(add="inline ml-5 text-base text-bold text-green-700")
              #Title
              with hpi_entry.add_slot("title"):
                ui.label('HISTORY OF PRESENTING ILLNESS').classes(add="w-full text-sky-600 text-bold text-3xl italic")
              #Body
              with hpi_entry.add_slot("default"):
                if clinical_history["chief_complaints"]:
                  with html.form().classes(add="w-full grid grid-cols-1 lg:grid-cols-2 gap-2"):                
                    for hpi in hpis(clinical_history):
                      if hpi[0]:
                        with ui.label(text=f"{hpis(clinical_history).index(hpi) + 1}. {hpi[0].capitalize()}").classes(add="my-2 text-bold text-xl"):
                          if hpi[1]:
                            html.p(hpi[1].capitalize()).classes(add="block text-md font-light italic")
                          else:
                            html.p("No notes available!").classes(add="block text-red-400 font-normal text-md italic")
                else:
                  html.p("No notes available!").classes(add="block text-red-400 font-normal text-lg italic")
            
            #PMH & FSH
            with ui.timeline_entry(icon="fas fa-notes-medical").props(add="color='green-6'") as past_hx_entry:
              #Subtitle
              with past_hx_entry.add_slot("subtitle"):
                if clinical_history["history_time"]:
                  with ui.label(clinical_history["history_time"].strftime("%a %-d %b %Y")).classes(add="text-base text-bold text-blue-700"):
                    ui.label(clinical_history["history_time"].strftime("%H:%M")).classes(add="inline ml-5 text-base text-bold text-green-700")
              #Title
              with past_hx_entry.add_slot("title"):
                ui.label('PAST CLINICAL AND SOCIAL HISTORY').classes(add="w-full text-sky-600 text-bold text-3xl italic")
              #Body
              with past_hx_entry.add_slot("default"):
                with html.div().classes(add="w-full grid grid-cols-1 lg:grid-cols-2 gap-2"):
                  #Medical/Surgical
                  with html.div().classes(add="w-full text-lg"):
                    ui.label("PAST MEDICAL & SURGICAL HISTORY").classes(add="text-bold text-xl")
                    if clinical_history["medical_history"] or clinical_history["surgical_history"]:
                      if clinical_history["medical_history"]:
                        ui.markdown(content=clinical_history["medical_history"].capitalize()).classes(add="text-md font-light italic")
                      if clinical_history["surgical_history"]:
                        ui.markdown(content=clinical_history["surgical_history"].capitalize()).classes(add="text-md font-light italic")
                    else:
                      html.p("No notes available!").classes(add="block text-red-400 font-normal text-lg italic")

                  #Family/Social
                  with html.div().classes(add="w-full text-lg"):
                    html.label("FAMILY & SOCIAL HISTORY").classes(add="text-bold text-xl")
                    if clinical_history["family_history"] or clinical_history["social_history"]:
                      if clinical_history["family_history"]:
                        html.p(clinical_history["family_history"].capitalize()).classes(add="text-base font-light italic")
                      if clinical_history["social_history"]:
                        html.p(clinical_history["social_history"].capitalize()).classes(add="text-base font-light italic")
                    else:
                      html.p("No notes available!").classes(add="block text-red-400 font-normal text-lg italic")
            
            #PHYSICAL EXAM
            with ui.timeline_entry(icon="fas fa-stethoscope").props(add="color='green-6'") as pe_entry:
              #Subtitle
              with pe_entry.add_slot("subtitle"):
                if consultation["general_exam"]["ge_exam_time"]:
                  with ui.label(consultation["general_exam"]["ge_exam_time"].strftime("%a %-d %b %Y")).classes(add="text-base text-bold text-blue-700"):
                    ui.label(consultation["general_exam"]["ge_exam_time"].strftime("%H:%M")).classes(add="inline ml-5 text-base text-bold text-green-700")
              #Title
              with pe_entry.add_slot("title"):
                ui.label('PHYSICAL EXAMINATION').classes(add="w-full text-sky-600 text-bold text-3xl italic")
              #Body
              with pe_entry.add_slot("default"):
                with html.div().classes(add="w-full grid grid-cols-1 lg:grid-cols-2 gap-2"):
                  #General exam
                  with html.div().classes(add="w-full text-lg"):
                    ui.label("GENERAL EXAMINATION").classes(add="text-bold text-xl")
                    if consultation["general_exam"]["notes"]:
                      ui.markdown(content=consultation["general_exam"]["notes"].capitalize()).classes(add="text-md font-light italic")
                    else:
                      html.p("No notes available!").classes(add="block text-red-400 font-normal text-lg italic")

                  #Orodental exam
                  with html.div().classes(add="w-full text-lg"):
                    html.label("ORODENTAL EXAMINATION").classes(add="text-bold text-xl")
                    if consultation["orodental_exam"]["intraoral"] or consultation["orodental_exam"]["extraoral"]:
                      if consultation["orodental_exam"]["intraoral"]:
                        html.p(consultation["orodental_exam"]["intraoral"].capitalize()).classes(add="text-base font-light italic")
                      if consultation["orodental_exam"]["extraoral"]:
                        html.p(consultation["orodental_exam"]["extraoral"].capitalize()).classes(add="text-base font-light italic")
                    else:
                      html.p("No notes available!").classes(add="block text-red-400 font-normal text-lg italic")
          
          #Imagings
          if visit["imagings"]:
            imagings = visit["imagings"]
            first_imaging = imagings[0]
            with ui.timeline_entry(icon="fas fa-x-ray").props(add="color='green-6'") as img_entry:
              #Subtitle
              with img_entry.add_slot("subtitle"):
                with ui.label(first_imaging["request_time"].strftime("%a %-d %b %Y")).classes(add="text-base text-bold text-blue-700"):
                  ui.label(first_imaging["request_time"].strftime("%H:%M")).classes(add="inline ml-5 text-base text-bold text-green-700")
              #Title
              with img_entry.add_slot("title"):
                ui.label('IMAGINGS').classes(add="w-full text-sky-600 text-bold text-3xl italic")
              #Body
              with img_entry.add_slot("default"):
                with html.div().classes(add="w-full"):
                  ImagingResultsForm(visit=visit)

          #Procedures
          if visit["procedures"]:
            procedures = visit["procedures"]
            first_procedure = procedures[0]
            with ui.timeline_entry(icon="fas fa-tooth").props(add="color='green-6'") as proc_entry:
              #Subtitle
              with proc_entry.add_slot("subtitle"):
                with ui.label(first_procedure["ordered_on"].strftime("%a %-d %b %Y")).classes(add="text-base text-bold text-blue-700"):
                  ui.label(first_procedure["ordered_on"].strftime("%H:%M")).classes(add="inline ml-5 text-base text-bold text-green-700")
              #Title
              with proc_entry.add_slot("title"):
                ui.label('PROCEDURES').classes(add="w-full text-sky-600 text-bold text-3xl italic")
              #Body
              with proc_entry.add_slot("default"):
                if procedures:
                    ui.table(
                      columns=[
                        {"name":"sno","label":"S/No","field":"sno","width":50},
                        {"name":"name","label":"NAME","field":"name"},
                        {"name":"status","label":"STATUS","field":"status"}
                      ],
                      rows=[
                        {
                          "sno":procedures.index(procedure) + 1,
                          "name":procedure["name"],
                          "status":"done" if procedure["done"] else "not done"
                        } for procedure in procedures
                      ],
                      column_defaults={
                        "align":"left"
                      },
                      pagination=5,title="PROCEDURES"
                    ).props(add="dense rows-per-page-label='procedures per page'").classes(add="w-1/2 uppercase")

          #Medicines
          if visit["medications"] or visit["medical_items"]:
            medications,medical_items = visit["medications"],visit["medical_items"]
            first_item = medications[0] if medications else medical_items[0]
            with ui.timeline_entry(icon="fas fa-file-prescription").props(add="color='green-6'") as med_entry:
              #Subtitle
              with med_entry.add_slot("subtitle"):
                with ui.label(first_item["prescribed_on"].strftime("%a %-d %b %Y")).classes(add="text-base text-bold text-blue-700"):
                  ui.label(first_item["prescribed_on"].strftime("%H:%M")).classes(add="inline ml-5 text-base text-bold text-green-700")
              #Title
              with med_entry.add_slot("title"):
                ui.label('MEDICATIONS & MEDICAL ITEMS').classes(add="w-full text-sky-600 text-bold text-3xl italic")
              #Body
              with med_entry.add_slot("default"):
                with html.div().classes(add="w-full p-0.5"):
                  #Medications
                  if medications:
                    ui.table(
                      columns=[
                        {"name":"sno","label":"S/No","field":"sno","width":50},
                        {"name":"name","label":"NAME","field":"name"},
                        {"name":"dosage","label":"DOSAGE","field":"dosage"},
                        {"name":"prescribed_items","label":"PRESCRIBED ITEMS","field":"prescribed_items","width":50},
                        {"name":"status","label":"STATUS","field":"status"}
                      ],
                      rows=[
                        {
                          "sno":medications.index(medication) + 1,
                          "name":medication["name"],
                          "dosage":medication["dosage"],
                          "prescribed_items":medication["prescribed_items_no"],
                          "status":"dispensed" if medication["dispensed"] else "not dispensed"
                        } for medication in medications
                      ],
                      column_defaults={
                        "align":"left"
                      },
                      pagination=5,title="MEDICATIONS"
                    ).props(add="dense rows-per-page-label='medications per page' ").classes(add="uppercase")

                  #Medical items
                  if medical_items:
                    ui.table(
                      columns=[
                        {"name":"sno","label":"S/No","field":"sno","width":50},
                        {"name":"name","label":"NAME","field":"name"},
                        {"name":"prescribed_items","label":"PRESCRIBED ITEMS","field":"prescribed_items","width":50},
                        {"name":"status","label":"STATUS","field":"status"}
                      ],
                      rows=[
                        {
                          "sno":medications.index(medication) + 1,
                          "name":medication["name"],
                          "prescribed_items":medication["prescribed_items_no"],
                          "status":"dispensed" if medication["dispensed"] else "not dispensed"
                        } for medication in medical_items
                      ],
                      column_defaults={
                        "align":"left"
                      },
                      pagination=5,title="MEDICAL ITEMS"
                    ).classes(add="uppercase")
       
  def PresentingIllness(self,consultation:dict,parent=None,visit=None,attendee_id=None):
    """"""
    #DATA
    history = self.active_consultation["clinical_history"]
    complaints = {
      "count":len(history["chief_complaints"]),
      "complaint1":history["chief_complaints"][0] if len(history["chief_complaints"]) > 0 else None,
      "complaint2":history["chief_complaints"][1] if len(history["chief_complaints"]) > 1 else None,
      "complaint3":history["chief_complaints"][2] if len(history["chief_complaints"]) > 2 else None
    }
    hpis = {
      "hpi1":history["hpi1"] if history["hpi1"] else None,
      "hpi2":history["hpi2"] if history["hpi2"] else None,
      "hpi3":history["hpi3"] if history["hpi3"] else None
    }
    
    #FXS
    def HPI():
      hpi_pad.clear()
      with hpi_pad.classes(add=""):
        if complaints["count"]:
          with html.div().classes(add="grow w-full py-0.5 flex flex-col lg:flex-row lg:items-center lg:content-center gap-1 lg:gap-5"):
          #HPI1
            if complaints["complaint1"]:
              ui.textarea(label=complaints["complaint1"].upper(),placeholder="Probe more...").props(add="hide-bottom-space stack-label input-class='h-[100px] lg:h-[250px]' label-color='#07004d'").classes(add="w-full lg:w-[30%] lg:h-full rounded bg-white shadow-md shadow-[#07004d] px-3 text-lg").bind_value(hpis,"hpi1")
            #HPI2
            if complaints["complaint2"]:
              ui.textarea(label=complaints["complaint2"].upper(),placeholder="Probe more...").props(add="hide-bottom-space stack-label input-class='h-[100px] lg:h-[250px]' label-color='#07004d'").classes(add="w-full lg:w-[30%] lg:h-full rounded bg-white shadow-md shadow-[#07004d] px-3 text-lg").bind_value(hpis,"hpi2")
            #HPI3
            if complaints["complaint3"]:
              ui.textarea(label=complaints["complaint3"].upper(),placeholder="Probe more...").props(add="hide-bottom-space stack-label input-class='h-[100px] lg:h-[250px]' label-color='#07004d'").classes(add="w-full lg:w-[30%] lg:h-full rounded bg-white shadow-md shadow-[#07004d] px-3 text-lg").bind_value(hpis,"hpi3")
            
            #BUTTONS
          ui.button(text="SAVE HPI",icon="fa-regular fa-floppy-disk",color="",on_click=save_hpi).classes(add="bg-harmony lg:my-3 w-fit self-center rounded shadow-md shadow-[#07004d] text-xl text-yellow-500 text-bold")
        
        else:
          with html.div().classes(add="grow w-full p-1 rounded flex flex-col justify-center items-center content-center"):
            ui.label("No client's complaint saved!").classes(add="text-red-500 text-xl italic font-bold fa-fade")

    def amplify_complaints():
      #Save complaints
      comps = [comp for key,comp in complaints.items() if key != "count" and comp]
      status = clients_db.register_chief_complaints({"consultant_id":self.user.username,"hx_id":history["hx_id"],"complaints":json.dumps(comps) if comps else None})
      ui.notify(message=status["message"],type=status["type"],position=status["position"])
      self.active_consultation["clinical_history"]["chief_complaints"] = comps
      
      #Updating complaints
      #Complaint1
      complaints["count"] = len(comps)
      if not complaints["complaint1"]:
        hpis["hpi1"] = None
        if complaints["complaint2"]:
          complaints["complaint1"],hpis["hpi1"] = complaints["complaint2"],hpis["hpi2"]
          complaints["complaint2"],hpis["hpi2"] = None,None
        else:
          if complaints["complaint3"]:
            complaints["complaint1"],hpis["hpi1"] = complaints["complaint3"],hpis["hpi3"]
            complaints["complaint3"],hpis["hpi3"] = None,None
      #Complaint2
      if not complaints["complaint2"]:
        hpis["hpi2"] = None
        if complaints["complaint3"]:
          complaints["complaint2"],hpis["hpi2"] = complaints["complaint3"],hpis["hpi3"]
          complaints["complaint3"],hpis["hpi3"] = None,None
      #Complaint3
      if not complaints["complaint3"]:
        hpis["hpi3"] = None
      
      #Display HPI boxes
      HPI()
     
    def save_hpi():
      #DB SAVING
      status = clients_db.register_hpi({"hx_id":history["hx_id"],"editor_id":self.user.username,"hpi1":hpis["hpi1"],"hpi2":hpis["hpi2"],"hpi3":hpis["hpi3"]})
      
      #UPDATE ACTIVE CONSULTATION
      self.active_consultation["clinical_history"]["hpi1"] = hpis["hpi1"]
      self.active_consultation["clinical_history"]["hpi2"] = hpis["hpi2"]
      self.active_consultation["clinical_history"]["hpi3"] = hpis["hpi3"]

      #NOTIFY
      ui.notify(message=status["message"],type=status["type"],position=status["position"])
    
    #UI
    #Complaints
    with html.section().classes(add="w-full grid grid-cols-2 lg:grid-cols-4 gap-1 lg:items-center lg:justify-center lg:gap-3"):
      #Complaint1
      ui.input(label="1ST COMPLAINT").props(add=f"clearable").classes(add="bg-white shadow-md shadow-[#07004d] rounded px-5 text-base").bind_value(complaints,"complaint1")
      #Complaint2
      ui.input(label="2ND COMPLAINT").props(add="clearable").classes(add="bg-white shadow-md shadow-[#07004d] rounded px-5 text-base").bind_value(complaints,"complaint2")
      #Complaint3
      ui.input(label="3RD COMPLAINT").props(add="clearable").classes(add="bg-white shadow-md shadow-[#07004d] rounded px-5 text-base").bind_value(complaints,"complaint3")
    
      #Buttons
      ui.button(text="AMPLIFY",color="",on_click=amplify_complaints).classes(add="lg:col-span 2 w-full lg:w-1/2 place-self-center rounded bg-harmony shadow-md shadow-[#07004d] text-yellow-500 text-bold text-xl")
  
    #HPI
    with html.section().classes(add="w-full grow flex flex-col lg:justify-around gap-y-0.5") as hpi_pad:
      HPI()

  def PastMedicalSurgicalHistory(self,consultation:dict,parent=None,visit=None,attendee_id=None):
    """"""
    #DATA
    history = self.active_consultation["clinical_history"]
    pmh = {
      "hx_id":history["hx_id"],
      "mhx":history["medical_history"],
      "shx":history["surgical_history"],
      "editor_id":self.user.username
    }

    #FXS
    def save_medical_surgical_history():
      #DATABASE SAVING
      status = clients_db.register_pmh(pmh)

      #UPDATE ACTIVE CONSULTATION
      self.active_consultation["clinical_history"]["medical_history"] = pmh["mhx"]
      self.active_consultation["clinical_history"]["surgical_history"] = pmh["shx"]

      #NOTIFY
      ui.notify(message=status["message"],type=status["type"],position=status["position"])

    #UI
    with html.div().classes(add="w-full flex flex-col lg:flex-row gap-3"):
      #Medical Hx
      ui.textarea(label="MEDICAL HISTORY",placeholder="...").props(add="clearable stack-label input-class='lg:h-[250px]' label-color='#07004d'").classes(add="grow shadow-md shadow-[#07004d] bg-white rounded px-3 text-lg").bind_value(pmh,"mhx")
      #Surgical Hx
      ui.textarea(label="SURGICAL HISTORY",placeholder="...").props(add="clearable stack-label input-class='lg:h-[250px]' label-color='#07004d'").classes(add="grow shadow-md shadow-[#07004d] bg-white rounded px-3 text-lg").bind_value(pmh,"shx")
  
    #BUTTONS
    with html.div().classes(add="w-full flex flex-row justify-center"):
      ui.button(text="SAVE",icon="fa-regular fa-floppy-disk",color="",on_click=save_medical_surgical_history).classes(add="bg-harmony rounded shadow-md shadow-[#07004d] text-lg lg:text-xl text-yellow-500 text-bold")

  def FamilySocialHistory(self,consultation:dict,parent=None,visit=None,attendee_id=None):
    """"""
    #DATA
    history = self.active_consultation["clinical_history"]
    fsh = {
      "hx_id":history["hx_id"],
      "fhx":history["family_history"],
      "shx":history["social_history"],
      "editor_id":self.user.username
    }

    #FXS
    def save_family_social_history():
      #DATABASE SAVING
      status = clients_db.register_fsh(fsh)

      #UPDATE ACTIVE CONSULTATION
      self.active_consultation["clinical_history"]["family_history"] = fsh["fhx"]
      self.active_consultation["clinical_history"]["social_history"] = fsh["shx"]

      #NOTIFY
      ui.notify(message=status["message"],type=status["type"],position=status["position"])

    #UI
    with html.div().classes(add="w-full flex flex-col lg:flex-row gap-3"):
      #Family Hx
      ui.textarea(label="FAMILY HISTORY").props(add="clearable stack-label input-class='lg:h-[250px]' label-color='#07004d'").classes(add="grow shadow-md shadow-[#07004d] bg-white rounded px-3 text-lg").bind_value(fsh,"fhx")
      #Social Hx
      ui.textarea(label="SOCIAL HISTORY").props(add="clearable stack-label input-class='lg:h-[250px]' label-color='#07004d'").classes(add="grow shadow-md shadow-[#07004d] bg-white rounded px-3 text-lg").bind_value(fsh,"shx")
  
    #BUTTONS
    with html.div().classes(add="w-full flex flex-row justify-center"):
      ui.button(text="SAVE",icon="fa-regular fa-floppy-disk",color="",on_click=save_family_social_history).props(add="glossy").classes(add="bg-harmony rounded shadow-md shadow-[#07004d] text-lg lg:text-xl text-yellow-500 text-bold")

  def PhysicalExamination(self,consultation:dict,parent=None,visit=None,attendee_id=None):
    """"""
    general_exam = self.active_consultation["general_exam"]
    orodental_exam = self.active_consultation["orodental_exam"]
    #DATA
    ge = {
      "ge_id":general_exam["ge_id"],
      "editor_id":self.user.username,
      "notes":general_exam["notes"]
    }
    orodental = {
      "orodental_exam_id":orodental_exam["orodental_exam_id"],
      "editor_id":self.user.username,
      "intraoral":orodental_exam["intraoral"],
      "extraoral":orodental_exam["extraoral"]
    }

    #FXS
    def save_examination():
      #DATABASE SAVING
      ge_status = clients_db.register_general_exam(ge)
      orodental_status = clients_db.register_orodental_exam(orodental)

      #UPDATE ACTIVE CONSULTATION
      self.active_consultation["general_exam"]["notes"] = general_exam["notes"]
      self.active_consultation["orodental_exam"]["intraoral"] = orodental_exam["intraoral"]
      self.active_consultation["orodental_exam"]["extraoral"] = orodental_exam["extraoral"]

      #NOTIFY
      status = set()
      status.add(orodental_status["type"])
      status.add(ge_status["type"])
      if len(status) == 1:
        ui.notify(message="Physical Examination saved successfully!",type="positive",position="top")
      else:
        u.notify(message="Physical Examination not saved!",type="negative",position="center")
        return

    #UI
    with html.div().classes(add="grow w-full p-1 flex flex-col justify-between lg:flex-row gap-1"):
      #GE
      ui.textarea(label="GENERAL EXAMINATION").props(add="clearable stack-label input-class='lg:h-[250px]' label-color='#07004d'").classes(add="lg:w-[30%] shadow-sm shadow-[#07004d] bg-white rounded px-3 text-lg").bind_value(ge,"notes")
      #ODE
      ui.textarea(label="EXTRAORAL EXAMINATION").props(add="clearable stack-label input-class='lg:h-[250px]' label-color='#07004d'").classes(add="lg:w-[30%] shadow-sm shadow-[#07004d] bg-white rounded px-3 text-lg").bind_value(orodental,"extraoral")
      ui.textarea(label="INTRAORAL EXAMINATION").props(add="clearable stack-label input-class='lg:h-[250px]' label-color='#07004d'").classes(add="lg:w-[30%] shadow-sm shadow-[#07004d] bg-white rounded px-3 text-lg").bind_value(orodental,"intraoral")
      
    #BUTTONS
    with html.div().classes(add="w-full py-1 flex flex-row justify-center"):
      ui.button(text="SAVE",icon="fa-regular fa-floppy-disk",color="",on_click=save_examination).props(add="glossy").classes(add="rounded bg-harmony shadow-md shadow-[#07004d] text-lg lg:text-xl text-yellow-500 text-bold")

  def ProvisionalDiagnoses(self,consultation:dict,parent=None,visit=None,attendee_id=None):

    #FXS
    async def load_provisional_diagnoses():
      diagnoses_select.options = self.diagnoses
      diagnoses_select.update()
    
    def DifferentialDiagnosesDialog(pdx):
      """"""
      #DATA & CONTROLS
      if not pdx:
        return
      
      ddxs = set()

      #FXS
      async def load_differential_diagnoses():
        differentials = self.diagnoses
        differentials.remove(pdx)

        differentials_select.options = differentials
        differentials_select.update()
      
      def display_differentials(new_ddx=None):
        """Displays differentials selected"""
        
        if new_ddx:
          ddxs.add(new_ddx)

        ddx_display.clear()
        if ddxs:
          with ddx_display.classes(add="animate__animated animate__fadeIn animate__slow gap-y-2 justify-start items-start",remove="items-center justify-center"):
            for ddx in ddxs:
              ui.chip(text=ddx,text_color="#07004d",color="",removable=True,on_value_change=lambda e:clear_differential(e.sender._text)).props(add="icon-remove='delete'").classes(add="bg-inherit rounded-sm shadow-sm shadow-[#07004d]")
        else:
          with ddx_display.classes(add="animate__animated animate__fadeIn animate__slow justify-center items-center",remove="justify-start items-start"):
            ui.label("No Differential Diagnosis!").classes(add="text-bold italic text-red-400 fa-fade")
      
      def clear_differential(saved_ddx):
        if not saved_ddx:
          return

        ddxs.remove(saved_ddx)

      def save_diagnosis():
        diagnosis = {
          "consultation_id":self.active_consultation.consultation_id,
          "provisional":pdx,
          "differentials":list(ddxs)
        }

        self.active_diagnoses.append(diagnosis)

        status = clients_db.register_diagnosis(diagnosis=diagnosis)

        ui.notify(message=status["message"],position=status["position"],type=status["type"])

        ddx_dialog.close()

        #DISPLAY
        provisional_diagnoses_panel.clear()
        with provisional_diagnoses_panel:
          self.DiagnosesDisplay()
      
      #UI
      with ui.dialog().props(add="transition-show='scale' transition-hide='scale' transition-duration='500' ") as ddx_dialog,html.div().style(add="min-width:50%;min-height:60%;").classes(add="bg-sky-100 p-0.5 flex flex-col items-center gap-y-3"):
        #Diagnosis Label
        with html.div().classes(add="w-full bg-harmony flex flex-row items-center"):
          ui.label(text=pdx).classes(add="grow px-1 bg-inherit text-center text-yellow-500 text-2xl text-bold")
          ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=ddx_dialog.close).classes(add="bg-inherit text-red-500 text-lg text-bold")
        
        #DDx Select
        with html.div().classes(add="w-full py-3 flex flex-row justify-center"):
          differentials_select = ui.select(options=[],label="DIFFERENTIAL DIAGNOSIS",with_input=True,on_change=lambda e:display_differentials(e.value)).props(add="clearable").classes(add="lg:w-3/5 mx-5 px-5 rounded shadow-md shadow-[#07004d] bg-white text-lg")
        
        ui.separator().classes(add="w-full")

        with html.div().classes(add="grow bw-full flex flex-col") as ddx_display:
          display_differentials()
        
        ui.separator().classes(add="w-full")

        #ui.space()
        with html.div().classes(add=f"w-full p-3 justify-self-end flex flex-row justify-center gap-5"):
          ui.button(text="save diagnosis",color="",on_click=save_diagnosis).classes(add="bg-harmony text-yellow-500 text-lg lg:text-xl")
          #ui.button(text="delete diagnosis",color="",on_click=lambda e:delete_pdx(pdx=raw_pdx)).classes(add="hidden bg-harmony text-red-500 text-lg lg:text-xl")
  
      ddx_dialog.open()
    
      #BACKGROUND LOADS
      ui.timer(0.1,lambda:load_differential_diagnoses(),once=True)

    #UI
    with html.section().classes(add="grow w-full flex flex-col lg:grid grid-cols-3 items-center gap-3 lg:gap-0"):
      #Selecteor
      with html.div().classes(add="w-full lg:h-full py-3 flex flex-row justify-center items-start"):
        diagnoses_select = ui.select(options=[],label="PROVISIONAL DIAGNOSIS",with_input=True,on_change=lambda e:DifferentialDiagnosesDialog(pdx=e.value)).props(add=f"clearable").classes(add="lg:w-3/5 px-5 rounded shadow-md shadow-[#07004d] bg-white text-lg")

      #Diagnoses Display
      with html.div().classes(add="grow lg:col-span-2 w-full lg:h-full flex flex-col shadow-sm shadow-[#07004d]") as provisional_diagnoses_panel:
        self.DiagnosesDisplay()
        
    #Background loads
    ui.timer(0.1,lambda: asyncio.create_task(load_provisional_diagnoses()),once=True)

  def DefinitiveDiagnoses(self,consultation:dict,parent=None,visit=None,attendee_id=None):
    #DATA
    _selectable_diagnoses = set()
    _selectable_diagnoses.update([f"{provisional['provisional_icd'].upper()}:{provisional['provisional']}" for provisional in self.active_diagnoses])
    for diagnosis in self.active_diagnoses:
      _selectable_diagnoses.update(diagnosis["differentials"])
    
    selectable_diagnoses = list(_selectable_diagnoses)
    
    #FXS
    def update_diagnosis(dx:str):
      if not dx:
        return
      
      definitive = dx.split(":")[1]
      definitive_icd = dx.split(":")[0]
      definitive_generic = definitive_icd.split(".")[0] if "." in definitive_icd else definitive_icd
      
      for active_dx in self.active_diagnoses:
        if (active_dx["provisional_icd"].lower() == definitive_icd.lower() or ("differentials" in active_dx and dx.lower() in [i.lower() for i in active_dx["differentials"]])):
          active_dx["definitive"] = definitive
          active_dx["definitive_icd"] = definitive_icd
          active_dx["definitive_generic"] = definitive_generic

          break
      
      #Update
      status = clients_db.update_diagnosis(active_dx)

      ui.notify(message=status["message"],position=status["position"],type=status["type"])
      
      #Displaying output
      if status["status"]:
        definitive_diagnoses_panel.clear()
        with definitive_diagnoses_panel:
          self.DiagnosesDisplay(definitive=True)
      
    #UI
    with html.section().classes(add="grow w-full flex flex-col lg:grid grid-cols-3 items-center gap-3 lg:gap-0"):
      #Selecteor
      with html.div().classes(add="w-full lg:h-full py-3 flex flex-row justify-center items-start"):
        ui.select(options=selectable_diagnoses,label="DEFINITIVE DIAGNOSIS",with_input=True,on_change=lambda e:update_diagnosis(dx=e.value)).props(add=f"clearable").classes(add="lg:w-3/5 px-5 rounded shadow-md shadow-[#07004d] bg-white text-lg")

      #Diagnoses Display
      with html.div().classes(add="grow lg:col-span-2 w-full lg:h-full py-2 flex flex-col shadow-sm shadow-[#07004d]") as definitive_diagnoses_panel:
        self.DiagnosesDisplay(definitive=True)
    
  def DiagnosesDisplay(self,definitive:bool=False):
    """Displays list of diagnoses for client"""
    
    if definitive:
      if self.active_diagnoses:
        with html.ol().classes(add="grow bg-inherit w-full list-inside list-decimal"):
          for active_diagnosis in self.active_diagnoses:
            if "definitive" in active_diagnosis and active_diagnosis["definitive"]:
              html.li(active_diagnosis["definitive"]).classes(add="my-1 text-xl font-bold")
      
      else:
        with html.div().classes(add="grow w-full flex flex-col justify-center items-center"):
          ui.label("No diagnosis saved!").classes(add="text-red-400 text-bold text-base italic fa-fade")

    else:
      if self.active_diagnoses:
        #Provisional diagnosis
        with html.ol().classes(add="grow bg-inherit w-full list-inside list-decimal"):
          for active_diagnosis in self.active_diagnoses:
            with html.li(active_diagnosis["provisional"]).classes(add="my-1 px-2 text-xl text-harmony font-bold"):
              if "differentials" in active_diagnosis and active_diagnosis["differentials"]:
                with html.ul().classes(add="list-inside list-discd text-lg text-gray-500"):
                  for differentials in active_diagnosis["differentials"]:
                    html.li(differentials)

      else:
        with html.div().classes(add="grow w-full flex flex-col justify-center items-center"):
          ui.label("No diagnosis saved!").classes(add="text-red-400 text-bold text-base italic fa-fade")

class ImagingsForm():
  """A class to display form inputs fo requesting imagings"""

  def __init__(self,parent,visit:dict,attendee_id:str,consultation=None):
    #DATA
    self.parent,self.visit,self.attendee_id = parent,visit,attendee_id
    self.initial_data()
    
    #UI
    with html.div().classes(add="grow w-full flex flex-col lg:grid lg:grid-cols-3"):
      #Imaging select
      with html.div().classes(add="w-full lg:h-full flex flex-col"):
        with html.section().classes(add="w-full p-5 flex flex-row justify-center"):
          ui.select(options=self.selectable_imagings,label="IMAGINGS",on_change=lambda e:self.ImagingDialog(imaging_input=e.value)).props(add="clearable stacked-label").classes(add="w-52 px-5 rounded shadow-md shadow-[#07004d] bg-white text-lg uppercase")
        
        #Commentary
        with html.section().classes(add="grow lg-show w-full"):
          pass
      
      #Imaging display
      with html.div().classes(add="grow w-full lg:col-span-2 lg:h-full p-2  flex flex-col gap-3") as self.imaging_details_display:
        self.ImagingsDisplay()

  #FUNCTIONALITIES
  def initial_data(self):
    self.insurance_authorization_no = self.visit.consultations[0].payment.authorization_no
    self.imagings = [self.format_imaging(service) for service in get_services() if service.type == "imaging"]
    self.visit_imagings = [img._asdict() for img in self.visit.imagings]
    self.selectable_imagings = [imaging["name"].upper() for imaging in self.imagings]
    
  def save_imaging(self,imaging:dict):
    """A method to save the imaging(s) in the database"""

    self.visit_imagings.append(imaging)

    status = clients_db.register_imaging(imaging)
    ui.notify(message=status["message"],type=status["type"],position=status["position"])
      
    self.ImagingsDisplay()
    self.imaging_dialog.close()
 
  def cancel_imaging(self,imaging_id:str):
    """Cancel imaging request"""

    clients_db.update_imaging(imaging_data={"imaging_id":imaging_id},delete=True)
  
  def format_imaging(self,imaging):
    """"""
    imaging = imaging._asdict()
    if self.visit.payment_mode != "cash":
      imaging_payment_schemes = [scheme._asdict() for scheme in imaging["schemes"] if scheme.scheme_name == self.visit.payment_mode.lower() and scheme.active]
      if imaging_payment_schemes:
        imaging_payment_scheme = imaging_payment_schemes[0]
        payment_mode = self.visit.payment_mode
      else:
        imaging_payment_scheme = [scheme._asdict() for scheme in imaging_payment_schemes if scheme.scheme_name == "cash"][0]
        payment_mode = "cash"
    else:
      imaging_payment_scheme = [scheme._asdict() for scheme in imaging["schemes"] if scheme.scheme_name == "cash" and scheme.active][0]
      payment_mode = "cash"
    
    visit_id = self.visit.visit_id
    imaging_id = f"{visit_id}img{uuid.uuid4()}"
    imaging_price = [price._asdict() for price in imaging_payment_scheme["prices"] if price.active][0]

    displayable_price = f"{imaging_price["min"]:,.2f} - {imaging_price["max"]:,.2f} TZS" if imaging_price["price_range"] else f"{imaging_price[self.visit.package]:,.2f} TZS"
    db_price = None if imaging_price["price_range"] else imaging_price[f"{self.visit.package}"]

    imaging.update({
      "visit_id":visit_id,
      "imaging_id":imaging_id,
      "attendee_id":self.attendee_id,
      "request_time":datetime.now(),
      "displayable_price":displayable_price,
      "study":imaging["name"],
      "notes":None,
      "cancelled":False,
      "processed":False,
      "payment":{
        "visit_id":visit_id,
        "payment_id":f"{imaging_id}pay{uuid.uuid4()}",
        "authorization_no":self.insurance_authorization_no,
        "payment_mode":payment_mode,
        "cost":db_price,
        "billed":True,
        "paid":False
      }
    })

    return imaging


  #DISPLAYS
  def ImagingsDisplay(self):
    """A method to display diagnoses from db"""
    #FXS
    def ImagingStatus(imaging,lg:bool=False):
      """A function to return a styled icon based on status of imaging"""
      if lg:
        return f"<span class=' text-bold text-{"gray-600" if imaging["cancelled"] else "green-600" if imaging["processed"] else"yellow-600"}'><span class='{"fa-regular fa-circle-xmark" if imaging["cancelled"] else "fa-solid fa-check-double" if imaging["processed"] else "fa-solid fa-spinner fa-spin"}'></span><span class='ml-1'>{"Cancelled" if imaging["cancelled"] else "Done" if imaging["processed"] else "Awaiting"}</span></span>"
      else:
        return f"<span class=' text-bold text-{"gray-600" if imaging["cancelled"] else "green-600" if imaging["processed"] else"yellow-600"}'><span class='{"fa-regular fa-circle-xmark" if imaging["cancelled"] else "fa-solid fa-check-double" if imaging["processed"] else "fa-solid fa-spinner fa-spin"}'></span></span></span>"
    
    def ImagingPlanner(imaging):
      planner = get_staff(username=imaging["attendee_id"])

      return f"{planner.title} {planner.last_name} {planner.first_name[0]}.".title()
    
    #UI
    self.imaging_details_display.clear()
    if self.visit_imagings:
      with self.imaging_details_display.classes(remove="items-center justify-center"):
        #Small Screen
        ui.aggrid(
          {
            "columnDefs":[
              {"headerName":"","field":"sno","width":50},
              {"headerName":"STUDY","field":"name"},
              {"headerName":"STATUS","field":"status","width":100}
            ],
            "rowData":[
              {
                "sno":self.visit_imagings.index(imaging) + 1,
                "name":imaging["study"].upper(),
                "status":ImagingStatus(imaging),
              } for imaging in self.visit_imagings
            ]
          },
          theme="quartz",
          html_columns=[2]
        ).props(add="").classes(add="lg:hidden grow w-full animate__animated animate__fadeIn")
        
        #Large Screen
        ui.aggrid(
          {
            "columnDefs":[
              {"headerName":"","field":"sno","width":50},
              {"headerName":"STUDY","field":"name"},
              {"headerName":"PLANNED BY","field":"planner","width":100},
              {"headerName":"DURATION","field":"duration","width":100},
              {"headerName":"STATUS","field":"status","width":110}
            ],
            "rowData":[
              {
                "sno":self.visit_imagings.index(imaging) + 1,
                "name":imaging["study"].upper(),
                "planner":ImagingPlanner(imaging),
                "duration":format_age(imaging["request_time"]),
                "status":ImagingStatus(imaging=imaging,lg=True),
              } for imaging in self.visit_imagings
            ]
          },
          theme="quartz",
          html_columns=[4]
        ).props(add="").classes(add="lg-show grow w-full animate__animated animate__fadeIn")

    else:
      with self.imaging_details_display.classes(add="justify-center items-center"):
        ui.label("No imaging requested!").classes(add="text-bold italic text-red-500 text-xl fa-fade")

  def ImagingDialog(self,imaging_input):
    """A method to display a dialog for differential diagnoses"""
    #DATA & CONTROLS
    if not imaging_input:
      return
    
    imaging = [_imaging for _imaging in self.imagings if _imaging["study"].lower() == imaging_input.lower()][0]

    requested = False

    if [img for img in self.visit_imagings if img["study"] == imaging_input.lower()]:
      requested = True

    #UI
    with ui.dialog().props(add="transition-show='jump-up' transition-hide='jump-down' transition-duration='500' ") as self.imaging_dialog,html.div().style(add="min-width:50%;").classes(add="bg-sky-50 p-0.5 flex flex-col"):
      #Header
      with html.div().classes(add="w-full bg-harmony px-1 flex flex-row items-center"):
        ui.label(text=imaging["study"]).classes(add="grow px-3 text-yellow-500 text-2xl text-bold uppercase")
        ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=self.imaging_dialog.close).classes(add="rounded bg-harmony shadow-md shadow-[#07004d] text-red-500 text-lg text-bold")
      
      #Details
      with html.div().classes(add="w-full px-1 bg-harmony grid grid-cols-3"):
        #Payment Mode
        ui.html(f"<span class='fa-solid fa-wallet text-sky-500'></span><span class='ml-2 text-yellow-400'>{imaging['payment']['payment_mode']}</span>",sanitize=False).classes(add="bg-inherit text-base uppercase font-bold")
        #Price
        ui.html(f"<span class='fa-solid fa-coins text-sky-500'></span><span class='ml-2 text-yellow-400'>{imaging['payment']['cost']:,.2f} TZS</span>",sanitize=False).classes(add="col-span-2 bg-inherit text-base uppercase font-bold")
      
      #Hint if there are concerns
      with html.div().classes(add="w-full flex flex flex-col items-center justify-center"):
        if requested:
          ui.html(f"<span class='fa-solid fa-house-medical-circle-exclamation'></span><span class='ml-2 italic'>It's already requested!</span>",sanitize=False).classes(add="bg-inherit text-lg text-red-400 font-bold fa-fade")
      
      #Imaging notes
      with html.div().classes(add="grow w-full flex flex-row justify-center p-3"):
        ui.textarea(label="ADDITIONAL NOTES",placeholder="Write any additional details to help radiologist/radiographer").props(add="clearable stack-label input-class='").classes(add="w-4/5 px-5 rounded shadow-md shadow-[#07004d] bg-white text-lg").bind_value(imaging,"notes")
      
      #Buttons
      with html.div().classes(add="w-full p-2 flex flex-row justify-around gap-x-2"):
        ui.button(text="REQUEST IMAGING",color="",on_click=lambda e:self.save_imaging(imaging=imaging)).classes(add="rounded bg-harmony shadow-md shadow-[#07004d] text-yellow-500 text-lg text-bold")
        #ui.button(text="CANCEL",icon="fa-regular fa-circle-xmark",color="",on_click=self.cancel_imaging).classes(add="rounded bg-harmony shadow-md shadow-[#07004d] text-red-500 text-lg text-bold")
    
    self.imaging_dialog.open()
  
  def ImagingsDisplayDialog(self,imaging:dict):

    #DATA
    if imaging["processed"]:
      ui.notify(message="Imaging results not yet processed!",type="warning",position="center")
      return
    else:
      imaging_path = Path(f"services/provider/media/imagings/{imaging['visit_id'].upper()}/{'uss' if 'uss' in imaging['study'] else 'xrays'}/{imaging['study'].split(' ')[0]}")
      
      if imaging_path.exists():
        image_paths =list(imaging_path.iterdir())
      else:
        return
      
    #UI
    with ui.dialog().props(add="transition-show='scale' transition-hide='scale' transition-duration='500'") as self.images_display_dialog,html.div().style(add="min-width:100%;min-height:50%;").classes(add="mrelative bg-sky-50 ring-1 ring-sky-500"):
      #Imaging details
      with html.div().classes(add="w-full flex flex-row gap-x-5 bg-gray-900 p-2 rounded-t"):
        #Name
        ui.label(text=imaging["study"].upper()).classes(add="grow p-1 text-center text-yellow-500 text-3xl text-bold")
        #Download Button
        ui.button(icon="fas fa-download fa-lg",color="",on_click=lambda e:self.download_attachments(attachments=image_paths)).classes(add="bg-inherit size-8 rounded-full ring-1 ring-sky-300 shadow-md shadow-sky-500 text-sky-500 text-bold").tooltip("Download Radiographs")
        #Close Button
        ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=self.images_display_dialog.close).classes(add="bg-inherit size-12 text-red-500 text-bold")

      #Images
      with html.div().classes(add="w-full h-[520px] flex flex-row justify-center bg-red-200"):
        with ui.carousel().props(add="animated infinite navigation swipeable thumbnails transition-prev='fade' transition-next='fade' transition-duration='300' navigation-position='bottom' navigation-icon='fas fa-circle-dot' navigation-active-icon='fas fa-eye' control-type='outline' control-text-color='light-blue-5'").classes(add="w-full h-full"):
          for image_path in image_paths:
            with ui.carousel_slide().classes(add="h-full w-full flex flex-col p-0.5"):
              ui.image(source=image_path).props(add="fit='fill'").classes(add="grow w-full")

    self.images_display_dialog.open()

class ImagingResultsForm():

  def __init__(self,visit:dict):
    #DATA
    self.visit = visit
    self.imagings = self.visit["imagings"]
    #UI
    with html.div().classes(add="w-full"):
      with html.div().classes(add="w-full grid grid-rows-3 gap-3"):
        for imaging in self.imagings:
          with ui.button(icon=f"fa-regular fa-{'circle-check' if imaging['processed'] else 'circle-xmark' }",color="gray-800",on_click=lambda e:self.ImageDialog(imaging=[imaging for imaging in self.imagings if imaging["study"] == e.sender.slots["default"].children[0]._text.lower()][0])).classes(add=f"block rounded-full w-fit text-left text-xl text-{'green-600' if imaging['processed'] else 'red-500'} ring-1 ring-blue-500 ring-offset-2 shadow-md shadow-blue-400 text-bold"):
            ui.label(imaging['study']).classes(add="ml-3 text-sky-400")
  
  #FUNCTIONALITIES
  def download_attachments(self,attachments:list[Path]):
    """A method to download attaachments to a local machine"""

    for attachment in attachments:
      ui.download(src=attachment,filename=f"{self.visit['client_name'].split(' ')[0].upper()}_{self.visit['client_name'].split(' ')[-1].upper()}_{self.visit['start_time'].strftime('%Y%m%d')}_{attachments.index(attachment) + 1}")

  #DISPLAYS
  def ImageDialog(self,imaging:dict):

    #DATA
    if not imaging["processed"]:
      ui.notify(message="Imaging results not yet processed!",type="warning",position="center")
      return
    else:
      imaging_path = Path(f"media/imagings/{imaging['visit_id']}/{'uss' if 'uss' in imaging['study'] else 'xrays'}/{imaging['study'].split(' ')[0]}")

      if imaging_path.exists():
        image_paths =list(imaging_path.iterdir())
      else:
        return
      
    #UI
    with ui.dialog().props(add="transition-show='scale' transition-hide='scale' transition-duration='500'") as self.images_dialog,html.div().style(add="min-width:100%;min-height:100%").classes(add="relative bg-sky-50 ring-1 ring-sky-500"):
      #Imaging details
      with html.div().classes(add="w-full flex flex-row gap-x-5 bg-gray-900 p-2 rounded-t"):
        #Name
        ui.label(text=imaging["study"].upper()).classes(add="grow p-1 text-center text-yellow-500 text-3xl text-bold")
        #Download Button
        ui.button(icon="fas fa-download fa-lg",color="",on_click=lambda e:self.download_attachments(attachments=image_paths)).classes(add="bg-inherit size-12 rounded-full ring-1 ring-sky-300 shadow-md shadow-sky-500 text-sky-500 text-bold").tooltip("Download Radiographs")
        #Close Button
        ui.button(icon="fas fa-circle-xmark",color="",on_click=self.images_dialog.close).classes(add="bg-inherit size-12 rounded-full ring-1 ring-red-500 shadow-md shadow-red-500 text-red-500 text-bold")

      #Images
      with html.div().classes(add="w-full h-[520px] flex flex-row justify-center bg-red-200"):
        with ui.carousel().props(add="animated infinite navigation swipeable thumbnails transition-prev='fade' transition-next='fade' transition-duration='300' navigation-position='bottom' navigation-icon='fas fa-circle-dot' navigation-active-icon='fas fa-eye' control-type='outline' control-text-color='light-blue-5'").classes(add="w-full h-full"):
          for image_path in image_paths:
            with ui.carousel_slide().classes(add="h-full w-full p-0.5"):
              ui.image(source=image_path).props(add="fill='cover'")

    self.images_dialog.open()

class ManagementPlanForm():
  """A class to display form inputs fo requesting imagings"""

  def __init__(self,parent,visit:dict,attendee_id:str,consultation=None):
    #DATA
    self.visit,self.parent,self.attendee_id = visit,parent,attendee_id
    self.initial_data()

    #UI
    with html.div().classes(add="w-full grow flex flex-col gap-1"):
      #Management selections
      with html.section().classes(add="w-full p-2 flex flex-row justify-center gap-3"):
        ui.select(options=self.selectable_medicines,label="MEDICINES",with_input=True,on_change=lambda e:self.MedicineDialog(medicine_input=e.value)).props(add="clearable").classes(add="px-5 rounded shadow-sm shadow-[#07004d] bg-white text-lg")
        ui.select(options=self.selectable_procedures,label="PROCEDURES",with_input=True,on_change=lambda e:self.ProcedureDialog(procedure_input=e.value)).props(add="clearable").classes(add="px-5 rounded shadow-sm shadow-[#07004d] bg-white text-lg")
      
      ui.separator().classes(add="w-full")
      
      #Management display
      with html.section().classes(add="grow p-0 w-full flex flex-col"):
        #Tabs
        with html.div().classes(add="w-full px-1 grid grid-cols-10 items-center gap-1"):
          with ui.tabs(value="procedures" if self.visit_procedures and not self.visit_medicines else "medicines").props(add="inline-label active-class='text-sky-700 font-bold'").classes(add="col-span-9 py-1") as management_tabs:
            ui.tab(name="medicines",label=f"MEDICINES",icon="fa-solid fa-pills").props(add="dense")
            ui.tab(name="procedures",label=f"PROCEDURES",icon="fas fa-hospital").props(add="dense")
        
        #Panels
        with html.div().classes(add="grow w-full rounded-br flex flex-col"):
          with ui.tab_panels(tabs=management_tabs,value="procedures" if self.visit_procedures and not self.visit_medicines else "medicines").props(add="animated infinite transition-prev='jump-right' transition-next='jump-left' transition-duration='700'").classes(add="bg-inherit grow w-full grid grid-cols-1"):
            #Medicines
            with ui.tab_panel(name="medicines").classes(add="w-full h-full p-0 rounded-0 flex flex-col"):
              with html.div().classes(add="grow w-full h-full flex flex-col") as self.medicines_display:
                self.MedicinesDisplay(medicines=self.visit_medicines)
            
            #Procedures
            with ui.tab_panel(name="procedures").classes(add="w-full h-full p-0 rounded-0 flex flex-col"):
              with html.div().classes(add="grow w-full h-full flex flex-col") as self.procedures_display:
                self.ProceduresDisplay(procedures=self.visit_procedures)
          
  #FUNCTIONALITIES
  def initial_data(self):
    self.insurance_authorization_no = self.visit.consultations[0].payment.authorization_no
    self.procedures = [self.format_procedure(service) for service in get_services() if service.type == "procedure"]
    self.formulary_medicines = get_formulary()
    self.medicines = [self.format_medicine(medicine) for medicine in self.formulary_medicines]
    
    self.selectable_medicines = [medicine["name"].upper() for medicine in self.medicines]
    self.selectable_procedures = [procedure["name"].upper() for procedure in self.procedures]

    _visit_medicines,self.visit_procedures = self.visit.medications + self.visit.medical_items,[procedure._asdict() for procedure in self.visit.procedures]
    self.visit_medicines = [medicine._asdict() for medicine in _visit_medicines]
    for medicine in self.visit_medicines:
      medicine["id"] = medicine["medication_id"] if "medication_id" in medicine else medicine["medical_item_id"]
  
  def format_medicine(self,medicine):
    """Format medicine from formulary to include details from requisition medicines"""
    #
    medicine = medicine._asdict()
    #Formatting payment details
    if self.visit.payment_mode != "cash":
      medicine_payment_schemes = [scheme._asdict() for scheme in medicine["schemes"] if scheme.scheme_name == self.visit.payment_mode.lower() and scheme.active]
      if medicine_payment_schemes:
        medicine_payment_scheme = medicine_payment_schemes[0]
        payment_mode = self.visit.payment_mode
      else:
        medicine_payment_scheme = [scheme._asdict() for scheme in medicine["schemes"] if scheme.scheme_name == "cash"][0]
        payment_mode = "cash"
    else:
      medicine_payment_scheme = [scheme._asdict() for scheme in medicine["schemes"] if scheme.scheme_name == "cash" and scheme.active][0]
      payment_mode = "cash"

    visit_id = self.visit.visit_id
    medication_id = f"{visit_id}med{uuid.uuid4()}"
    medicine_price = [price._asdict() for price in medicine_payment_scheme["prices"] if price.active][0]

    #Formatting inventory details
    if medicine["inventory"]:
      dispensing_inventory = sorted([inventory for inventory in medicine["inventory"] if inventory.issuer == "dispensing store" or inventory.receiver == "dispensing store"],key=lambda inv:inv.date,reverse=True)
      if dispensing_inventory:
        balance = _inventory.issuer_current_amount if _inventory.issuer == "dispensing store" else _inventory.receiver_current_amount
      else:
        balance = 0
    else:
      balance = 0
    
    #Finall
    medicine.update(
      {
      "id":medication_id,
      "visit_id":visit_id,
      "medication_id":medication_id if medicine["category"] == "medicine" else None,
      "medical_item_id":medication_id if medicine["category"] == "medical supply" else None,
      "prescriber_id":self.attendee_id,
      "prescription_no":self.visit.prescription_no,
      "dosage":"---",
      "prescribed_items_no":0,
      "dispensed_items_no":0,
      "balance":balance,
      "prescribed_on":datetime.now(),
      "dispensed":False,
      "dispensing_time":None,
      "dispenser_id":None,
      "cancelled":False,
      "cancelled_on":None,
      "cancelled_by":None,
      "payment":{
        "visit_id":visit_id,
        "payment_id":f"{medication_id}pay{str(uuid.uuid4()).split('-')[1]}",
        "medication_id":medication_id if medicine["category"] == "medicine" else None,
        "medical_item_id":medication_id if medicine["category"] == "medical supply" else None,
        "authorization_no":self.insurance_authorization_no,
        "payment_mode":payment_mode,
        "unit_price":medicine_price[self.visit.package.lower()],
        "cost":0,
        "billed":True
      }
    }
    )

    return medicine

  def format_procedure(self,procedure):
    #
    procedure = procedure._asdict()
    
    if self.visit.payment_mode != "cash":
      procedure_payment_schemes = [scheme for scheme in procedure["schemes"] if scheme.scheme_name == self.visit.payment_mode.lower() and scheme.active]
      if procedure_payment_schemes:
        procedure_payment_scheme = procedure_payment_schemes[0]
        payment_mode = self.visit.payment_mode
      else:
        procedure_payment_scheme = [scheme for scheme in procedure["schemes"] if scheme.scheme_name == "cash"][0]
        payment_mode = "cash"
    else:
      procedure_payment_scheme = [scheme for scheme in procedure["schemes"] if scheme.scheme_name == "cash" and scheme.active][0]
      payment_mode = "cash"
    
    visit_id = self.visit.visit_id
    procedure_id = f"{visit_id}proc{str(uuid.uuid4()).split('-')[1]}"
    procedure_price = [price._asdict() for price in procedure_payment_scheme.prices if price.active][0]
    displayable_price = f"{procedure_price['min']:,.2f} - {procedure_price['max']:,.2f} TZS" if procedure_price["price_range"] else f"{procedure_price[self.visit.package]:,.2f} TZS"
    db_price = None if procedure_price["price_range"] else procedure_price[self.visit.package]

    procedure.update({
      "id":procedure_id,
      "visit_id":visit_id,
      "procedure_id":procedure_id,
      "attendee_id":self.attendee_id,
      "ordered_on":datetime.now(),
      "displayable_price":displayable_price,
      "cancelled":False,
      "done":False,
      "count":1,
      "payment":{
        "visit_id":visit_id,
        "payment_id":f"{procedure_id}pay{str(uuid.uuid4()).split('-')[1]}",
        "authorization_no":self.insurance_authorization_no,
        "payment_mode":payment_mode,
        "unit_cost":db_price,
        "cost":db_price,
        "billed":True,
        "paid":False
      }
    })

    return procedure

  def save_medication(self,medicine:dict,prescription:dict):
    """Saving medication details in class state"""

    #Update state
    if medicine["category"] == "medicine":
      medicine["dosage"] = prescription["dosage"]
      medicine["prescribed_items_no"] = prescription["prescribed_items_no"]
      medicine["payment"]["cost"] = prescription["cost"]

      self.visit_medicines.append(medicine)
      
      status = clients_db.register_medication(medication_data=medicine)

    if medicine["category"] == "medical supply":
      medicine["prescribed_items_no"] = prescription["prescribed_items_no_items"]
      medicine["payment"]["cost"] = prescription["cost"]

      self.visit_medicines.append(medicine)

      status = clients_db.register_medical_item(medical_item=medicine)

    #NOTIFY
    ui.notify(message=status["message"],type=status["type"],position=status["position"])

    #UI display
    self.medicine_dialog.close()
    self.MedicinesDisplay(medicines=self.visit_medicines)

  def save_procedure(self,procedure:dict):
    """A method to save the procedure(s) in the database"""
    
    self.visit_procedures.append(procedure)
    
    status = clients_db.register_procedure(procedure)

    ui.notify(message=status["message"],type=status["type"],position=status["position"])

    self.ProceduresDisplay(procedures=self.visit_procedures)

    self.procedure_dialog.close()
  
  #DISPLAYS
  def MedicineDialog(self,medicine_input):
    """Displays dialog for prescription"""
    #DATA & CONTROLS
    if not medicine_input:
      return
    medicine = [_medicine for _medicine in self.medicines if _medicine['name'] == medicine_input.lower()][0]
    prescription = {
      "dispensing_balance":medicine["balance"],
      "dosage":None,
      "prescribed_items_no":0,
      "prescribed_items_no_items":0,
      "cost":0
    }

    prescribed,os = False,True

    if medicine["balance"]:
      os = False

    if [med for med in self.visit_medicines if med["name"] == medicine_input.lower()]:
      prescribed = True
      

    #FXS
    def units(medicine:dict,verbose:bool=False,plural:bool=False):
      unit = ""

      if plural:
        if verbose:
          unit = 'TABLETS' if medicine['name'].lower().split()[-1].startswith('tab') else 'CAPSULES' if medicine['name'].lower().split()[-1].startswith('cap') else 'BOTTLES' if (medicine['name'].lower().split()[-1].startswith('syrup') or medicine['name'].lower().split()[-1].startswith('susp')) else 'VIALS' if medicine['name'].lower().split()[-1].startswith('vial') else 'AMPOULES' if medicine['name'].lower().split()[-1].startswith('ampoule') else 'ITEMS'
        else:
          unit = 'TABS' if medicine['name'].lower().split()[-1].startswith('tab') else 'CAPS' if medicine['name'].lower().split()[-1].startswith('cap') else 'BTS' if (medicine['name'].lower().split()[-1].startswith('syrup') or medicine['name'].lower().split()[-1].startswith('susp')) else 'VLS' if medicine['name'].lower().split()[-1].startswith('vial') else 'AMPS' if medicine['name'].lower().split()[-1].startswith('ampoule') else 'ITEMS'
      else:
        if verbose:
          unit = 'TABLET' if medicine['name'].lower().split()[-1].startswith('tab') else 'CAPSULE' if medicine['name'].lower().split()[-1].startswith('cap') else 'BOTTLE' if (medicine['name'].lower().split()[-1].startswith('syrup') or medicine['name'].lower().split()[-1].startswith('susp')) else 'VIAL' if medicine['name'].lower().split()[-1].startswith('vial') else 'AMPOULE' if medicine['name'].lower().split()[-1].startswith('ampoule') else 'ITEM'
        else:
          unit = unit = 'TAB' if medicine['name'].lower().split()[-1].startswith('tab') else 'CAP' if medicine['name'].lower().split()[-1].startswith('cap') else 'BT' if (medicine['name'].lower().split()[-1].startswith('syrup') or medicine['name'].lower().split()[-1].startswith('susp')) else 'VLS' if medicine['name'].lower().split()[-1].startswith('vial') else 'AMP' if medicine['name'].lower().split()[-1].startswith('ampoule') else 'ITEM'
      
      return unit
    
    def icon(medicine:dict):
      return f"fas fa-{'tablets' if medicine['name'].lower().split()[-1].startswith('tab') else 'capsules' if medicine['name'].lower().split()[-1].startswith('cap') else 'prescription-bottle-medical' if (medicine['name'].lower().split()[-1].startswith('syrup') or medicine['name'].lower().split()[-1].startswith('susp')) else 'vials' if medicine['name'].lower().split()[-1].startswith('vial') or medicine['name'].lower().split()[-1].startswith('ampoule') else 'file-prescription'}"
    
    #UI
    with ui.dialog().props(add="transition-show='scale' transition-hide='scale' transition-duration='500'") as self.medicine_dialog,html.div().style(add="min-width:50%;").classes(add="bg-sky-100 p-0.5 flex flex-col gap-3"):
      #Header
      with html.div().classes(add="w-full bg-harmony px-1 rounded-t"):
        with html.div().classes(add="w-full flex flex-row justify-between items-center"):
          ui.label(text=medicine["name"]).classes(add="grow p-3 text-center text-yellow-400 text-lg lg:text-3xl text-bold uppercase")
          ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=self.medicine_dialog.close).classes(add="text-red-500 text-lg")

        #Separator
        for i in range(2):
          ui.separator().classes(add="w-full bg-[#09026f]")

        #Medication details
        with html.div().classes(add="w-full grid grid-cols-5 gap-2 small-caps"):
          #Payment mode
          ui.html(f"<span class='fa-solid fa-wallet text-sky-500'></span><span class='ml-2 text-yellow-400'>{medicine['payment']['payment_mode']}</span>",sanitize=False).classes(add="bg-inherit text-base uppercase font-bold")
          #Unit cost
          ui.html(f"<span class='fa-solid fa-coins text-sky-500'></span><span class='ml-2 text-yellow-400'>{medicine['payment']['unit_price']:,.2f} TZS/{units(medicine)}</span>",sanitize=False).classes(add="col-span-2 bg-inherit text-base uppercase font-bold")
          #Store balance
          ui.html(f"<span class='fa-solid fa-store text-sky-500'></span><span class='ml-2 text-yellow-400'>{medicine['balance']:,.0f} {units(medicine,plural=True)}</span>",sanitize=False).classes(add="col-span-2 bg-inherit text-base uppercase font-bold")
          #Total cost
          with html.span().classes(add="col-span-5 lg:col-span-2 bg-inherit text-base"):
            html.span().classes(add="fa-solid fa-tags text-sky-500")
            ui.label().classes(add="inline ml-1 font-bold text-yellow-400").bind_text_from(prescription,"cost",backward=lambda cost:f"{cost:,.2f} TZS")
      
      #Hint if there are concerns
      with html.div().classes(add="w-full flex flex flex-col items-center justify-center"):
        if prescribed:
          ui.html(f"<span class='fa-solid fa-file-circle-check'></span><span class='ml-2 italic'>It's already prescribed</span>",sanitize=False).classes(add="bg-inherit text-lg text-red-400 font-bold fa-fade")
        
        if os:
          ui.html(f"<span class='fa-solid fa-house-medical-circle-exclamation'></span><span class='ml-2 italic'>It's out of stock (O/S)</span>",sanitize=False).classes(add="bg-inherit text-lg text-red-400 font-bold fa-fade")
      
      #Medicine
      if medicine["category"] == "medicine":
        with html.form().classes(add="grow w-full p-3 flex flex-row gap-3"):
          #Details
          with html.div().classes(add="grow flex flex-row justify-around"):
            #Dosage
            ui.input(label="DOSAGE",placeholder="e.g. 500mg tds for 5 days").props(add=f"required stack-label").classes(add="w-48 lg:w-auto rounded shadow-md shadow-[#07004d] px-3 bg-white text-lg").bind_value(prescription,"dosage")
            #Quantity
            ui.number(label=f"No of {units(medicine=medicine,verbose=True,plural=True)}",value=1,min=1).props(add=f"stack-label").classes(add="w-48 lg:w-auto rounded shadow-md shadow-[#07004d] px-3 bg-white text-lg").bind_value(prescription,"prescribed_items_no").bind_value_to(prescription,"cost",forward=lambda items:items*medicine["payment"]["unit_price"])
          #Buttons
          with html.div().classes(add="w-full flex flex-row justify-center gap-2"):
            ui.button(text="SAVE MEDICATION",color="",on_click=lambda e:self.save_medication(medicine=medicine,prescription=prescription)).props(add=f"").classes(add="rounded bg-harmony shadow-md shadow-[#07004d] text-yellow-500 text-xl text-bold")
          
      if medicine["category"] == "medical supply":
        with html.div().classes(add="grow w-full p-3 flex flex-row justify-center gap-5"):
          ui.number(label=f"No of {units(medicine=medicine,verbose=True,plural=True)}",value=1,placeholder="e.g. 2").props(add=f"stack-label").classes(add="w-48 lg:w-auto rounded shadow-md shadow-[#07004d] px-3 bg-white text-lg").bind_value(prescription,"prescribed_items_no_items").bind_value_to(prescription,"cost",forward=lambda items:items*medicine["payment"]["unit_price"])
          ui.button(text="SAVE ITEM",color="",on_click=lambda e:self.save_medication(medicine=medicine,prescription=prescription)).props(add=f"").classes(add="rounded bg-harmony shadow-md shadow-[#07004d] text-yellow-500 text-xl text-bold")
          
    self.medicine_dialog.open()

  def ProcedureDialog(self,procedure_input):
    """"""
    #DATA & CONTROLS
    if not procedure_input:
      return
    
    planned = False

    procedure = [_procedure for _procedure in self.procedures if _procedure["name"].lower() == procedure_input.lower()][0]

    if [proc for proc in self.visit_procedures if proc['name'] == procedure_input.lower()]:
      planned = True
    
    #FXS
    def total_cost(count):
      if not count:
        count = 0
      return count * procedure["payment"]["unit_cost"]

    #UI
    with ui.dialog().props(add="transition-show='scale' transition-hide='scale' transition-duration='500'") as self.procedure_dialog,html.div().style(add="min-width:50%;").classes(add="bg-sky-100 p-0.5 flex flex-col gap-3"):
      #Header
      with html.section().classes(add="w-full bg-harmony px-1 rounded-t"):
        with html.div().classes(add="w-full flex flex-row justify-between"):
          ui.label(text=procedure["name"]).classes(add="grow p-3 text-center text-yellow-400 text-lg lg:text-3xl text-bold uppercase")
          ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=self.procedure_dialog.close).classes(add="text-red-500 text-lg")

        #Separator
        for i in range(2):
          ui.separator().classes(add="w-full bg-[#09026f]")

        #Procedure details
        with html.div().classes(add="w-full grid grid-cols-5 gap-1 small-caps"):
          #Payment mode
          ui.html(f"<span class='fa-solid fa-wallet text-sky-500'></span><span class='ml-2 text-yellow-500'>{procedure['payment']['payment_mode']}</span>",sanitize=False).classes(add="bg-inherit text-base uppercase font-bold")
        
          #Price
          ui.html(f"<span class='fa-solid fa-coins text-sky-500'></span><span class='ml-2 text-yellow-500'>{procedure['displayable_price']}</span>",sanitize=False).classes(add="col-span-2 bg-inherit text-base uppercase font-bold")

          #Total cost
          with html.span().classes(add="col-span-2 bg-inherit text-base"):
            html.span().classes(add="fa-solid fa-tags text-sky-500")
            ui.label().classes(add="inline ml-1 font-bold text-yellow-400").bind_text_from(procedure["payment"],"cost",backward=lambda cost:f"{cost:,.2f} TZS")
      
      
      #Hints if something is off
      with html.div().classes(add="w-full flex flex flex-col items-center justify-center"):
        if planned:
          ui.html(f"<span class='fa-solid fa-file-circle-check'></span><span class='ml-2 italic'>It's already planned!</span>",sanitize=False).classes(add="bg-inherit text-lg text-red-400 font-bold fa-fade")
        
      #Body
      with html.section().classes(add="w-full p-5 flex flex-row justify-around lg:justify-center gap-3"):
        ui.number(label=f"HOW MANY...?",min=1).props(add="stack-label").classes(add="w-28 rounded shadow-md shadow-[#07004d] px-3 bg-white text-lg").bind_value(procedure,"count").bind_value_to(procedure["payment"],"cost",forward=lambda count:total_cost(count))
        ui.button(text="PLAN A PROCEDURE",color="",on_click=lambda e:self.save_procedure(procedure=procedure)).classes(add="rounded bg-harmony shadow-md shadow-[#07004d] text-yellow-500 text-xl text-bold")
    
    self.procedure_dialog.open()
  
  def MedicinesDisplay(self,medicines:list):
    #DATA
    medicines = medicines

    #FXS
    def MedicineStatus(medicine,lg:bool=False):
      """A function to return a styled icon based on status of client's last visit"""
      if lg:
        return f"<span class=' text-bold text-{"gray-600" if medicine["cancelled"] else "green-600" if medicine["dispensed"] else"yellow-600"}'><span class='{"fa-regular fa-circle-xmark" if medicine["cancelled"] else "fa-solid fa-check-double" if medicine["dispensed"] else "fa-solid fa-spinner fa-spin"}'></span><span class='ml-1'>{"Cancelled" if medicine["cancelled"] else "Dispensed" if medicine["dispensed"] else "Awaiting"}</span></span>"
      else:
        return f"<span class=' text-bold text-{"gray-600" if medicine["cancelled"] else "green-600" if medicine["dispensed"] else"yellow-600"}'><span class='{"fa-regular fa-circle-xmark" if medicine["cancelled"] else "fa-solid fa-check-double" if medicine["dispensed"] else "fa-solid fa-spinner fa-spin"}'></span></span>"
    
    def Prescriber(medicine):
      planner = get_staff(username=medicine["prescriber_id"])

      return f"{planner.title} {planner.last_name} {planner.first_name[0]}.".title()

    def Dosage(medicine):
      if "dosage" in medicine:
        if medicine["dosage"]:
          return medicine["dosage"].upper()
        else:
          return "---"
      else:
        return "---"

    #UI
    self.medicines_display.clear()
    if medicines:
      with self.medicines_display.classes(remove="justify-center items-center"):
        #Small Screen
        ui.aggrid(
          {
            "columnDefs":[
              {"headerName":"","field":"sno","width":75},
              {"headerName":"","field":"name","width":300},
              {"headerName":"ITEMS","field":"items_no","width":100},
              {"headerName":"","field":"status","width":50}
            ],
            "rowData":[
              {
                "sno":medicines.index(medicine) + 1,
                "name":medicine["name"].upper(),
                "items_no":f"{medicine["prescribed_items_no"]:,.0f}",
                "status":MedicineStatus(medicine),
                "id":medicine["id"]
              } for medicine in medicines
            ]
          },
          theme="quartz",
          html_columns=[3]
        ).props(add="").classes(add="lg:hidden grow w-full animate__animated animate__fadeIn")
        
        #Large Screen
        ui.aggrid(
          {
            "columnDefs":[
              {"headerName":"","field":"sno","width":50},
              {"headerName":"NAME","field":"name"},
              {"headerName":"DOSAGE","field":"dosage"},
              {"headerName":"DURATION","field":"duration","width":100},
              {"headerName":"PRESCRIBER","field":"prescriber","width":100},
              {"headerName":"STATUS","field":"status","width":100}
            ],
            "rowData":[
              {
                "sno":medicines.index(medicine) + 1,
                "name":medicine["name"].upper(),
                "prescriber":Prescriber(medicine),
                "duration":format_age(medicine["prescribed_on"]),
                "dosage":Dosage(medicine),
                "status":MedicineStatus(medicine=medicine,lg=True),
                "id":medicine["id"]
              } for medicine in medicines
            ]
          },
          theme="quartz",
          html_columns=[5]
        ).props(add="").classes(add="lg-show grow w-full animate__animated animate__fadeIn")
        

    else:
      with self.medicines_display.classes(add="justify-center items-center"):
        ui.label("No medication/medical item prescribed!").classes(add="text-bold italic text-red-500 text-xl fa-fade")

  def ProceduresDisplay(self,procedures:list):

    #FXS
    def ProcedureStatus(procedure,lg:bool=False):
      """A function to return a styled icon based on status of client's last visit"""
      if lg:
        return f"<span class=' text-bold text-{"gray-600" if procedure["cancelled"] else "green-600" if procedure["done"] else"yellow-600"}'><span class='{"fa-regular fa-circle-xmark" if procedure["cancelled"] else "fa-solid fa-check-double" if procedure["done"] else "fa-solid fa-spinner fa-spin"}'></span><span class='ml-1'>{"Cancelled" if procedure["cancelled"] else "Done" if procedure["done"] else "Awaiting"}</span></span>"
      else:
        return f"<span class=' text-bold text-{"gray-600" if procedure["cancelled"] else "green-600" if procedure["done"] else"yellow-600"}'><span class='{"fa-regular fa-circle-xmark" if procedure["cancelled"] else "fa-solid fa-check-double" if procedure["done"] else "fa-solid fa-spinner fa-spin"}'></span></span></span>"
    
    def ProcedurePlanner(procedure):
      planner = get_staff(username=procedure["attendee_id"])

      return f"{planner.title} {planner.last_name} {planner.first_name[0]}.".title()
    
    def removable(procedure):
      return False if procedure["cancelled"] or procedure["done"] or procedure["payment"]["paid"] else True

    #UI
    self.procedures_display.clear()
    if procedures:
      with self.procedures_display.classes(remove="justify-center items-center"):
        #Small Screen
        ui.aggrid(
          {
            "columnDefs":[
              {"headerName":"","field":"sno","width":50},
              {"headerName":"","field":"name","width":200},
              {"headerName":"COUNT","field":"count","width":100},
              {"headerName":"","field":"status","width":50}
            ],
            "rowData":[
              {
                "sno":procedures.index(procedure) + 1,
                "name":procedure["name"].upper(),
                "count":procedure["count"],
                "status":ProcedureStatus(procedure),
              } for procedure in procedures
            ]
          },
          theme="quartz",
          html_columns=[3]
        ).props(add="").classes(add="lg:hidden grow w-full animate__animated animate__fadeIn")
        
        #Large Screen
        ui.aggrid(
          {
            "columnDefs":[
              {"headerName":"","field":"sno","width":50},
              {"headerName":"NAME","field":"name"},
              {"headerName":"PROCEDURES","field":"count","width":75},
              {"headerName":"PLANNED BY","field":"planner","width":100},
              {"headerName":"DURATION","field":"duration","width":100},
              {"headerName":"STATUS","field":"status","width":110}
            ],
            "rowData":[
              {
                "sno":procedures.index(procedure) + 1,
                "name":procedure["name"].upper(),
                "count":procedure["count"],
                "planner":ProcedurePlanner(procedure),
                "duration":format_age(procedure["ordered_on"]),
                "status":ProcedureStatus(procedure=procedure,lg=True),
              } for procedure in procedures
            ]
          },
          theme="quartz",
          html_columns=[5]
        ).props(add="").classes(add="lg-show grow w-full animate__animated animate__fadeIn")
        
    else:
      with self.procedures_display.classes(add="justify-center items-center"):
        ui.label("No procedure planned!").classes(add="text-bold italic text-red-500 text-xl fa-fade")

class ProceduresManager():
  """A class of UI for managing consultations"""
  
  def __init__(self,user):
    self.user = user
    self.initial_data()

    #UI
    with html.div().classes(add="grow w-full bg-inherit flex flex-col") as self.main_panel:
      #Header
      #Separator
      for i in range(2):
        ui.separator().classes(add="w-full bg-[#09026f]")

      ui.label("PROCEDURES").classes(add="w-full rounded-none bg-harmony text-bold text-xl lg:text-3xl text-yellow-500 p-2")
      with html.div().classes(add="grow w-full rounded-b flex flex-col") as self.procedures_panel:
        self.ProceduresDisplay(visits=self.procedure_visits)

  #FUNCTIONALITIES
  def initial_data(self):
    _procedure_visits = clients_processor.get_active_visits_with_procedures()
    done_procedure_visits = sorted([self.format_procedure_visit(procedure_visit) for procedure_visit in _procedure_visits if self.procedure_visit_status(procedure_visit) == "done"],key=lambda e:e.procedures[-1].done_on,reverse=True)
    pending_procedure_visits = [self.format_procedure_visit(procedure_visit) for procedure_visit in _procedure_visits if self.procedure_visit_status(procedure_visit) == "pending" or self.procedure_visit_status(procedure_visit) == "partial"]
    undone_procedure_visits = sorted([self.format_procedure_visit(procedure_visit) for procedure_visit in _procedure_visits if self.procedure_visit_status(procedure_visit) == "not done"],key=lambda e:e.procedures[-1].ordered_on)
    self.procedure_visits = pending_procedure_visits + undone_procedure_visits + done_procedure_visits
    
    #Activee Procedures
    self.active_procedures = []
    for visit in _procedure_visits:
      for procedure in visit.procedures:
        if not (procedure.done or procedure.cancelled):
          self.active_procedures.append(procedure._asdict())
    
    self.staffs = [staff.name.title() for staff in admin_processor.get_staffs(short=True)]

  def is_in_range(self,start_date:str,end_date:str,target_date:str):
    """Returns True if 'target_date' is between 'start_date' and 'end_date'"""
    
    start_date,end_date,target_date = datetime.fromisoformat(start_date).date(),datetime.fromisoformat(end_date),datetime.fromisoformat(target_date)
  
  def format_procedure_visit(self,visit):

    return visit._replace(procedures=[procedure._asdict() for procedure in visit.procedures])

  def procedure_visit_status(self,visit):
    """Returns value depending on whether the procedure has been done"""
    
    procedures = visit.procedures
    statuses = set()

    for procedure in procedures:
      if (procedure.payment.paid or procedure.payment.billed) and not procedure.done:
        statuses.add("pending")
      if (procedure.payment.paid or procedure.payment.billed) and procedure.done:
        statuses.add("done")
      if not (procedure.payment.paid or procedure.payment.billed) and not procedure.done:
        statuses.add("not done")
    
    if len(statuses) == 1:
      for status in statuses:
        return status
    else:
      return "partial"
  
  def procedures(self,procedures:list[dict]):
    """Returns a list of procedures"""
    _done = len([procedure for procedure in procedures if procedure["done"]])
    _cancelled = len([procedure for procedure in procedures if procedure["cancelled"]])
    _pending = len([procedure for procedure in procedures if (procedure["payment"].paid or procedure["payment"].billed) and not procedure["done"]])
    
    _done_str = f"<span class='mx-2 text-green-600' ><i class='fa-solid fa-circle-check'></i><i class='ml-1'>{_done}</i></span>" if _done else ""
    _pending_str = f"<span class='mx-2 text-yellow-600' ><i class='fa-solid fa-spinner fa-spin'></i><i class='ml-1'>{_pending}</i></span>" if _pending else ""
    _cancelled_str = f"<span class='mx-2 text-gray-600' ><i class='fa-solid fa-ban'></i><i class='ml-1'>{_cancelled}</i></span>" if _cancelled else ""
    
    return f"{_done_str} {_pending_str} {_cancelled_str}"

  def save_procedure(self,procedure:dict):
    """Saves the findings in the database"""
    visit_id = procedure["visit_id"]

    status = clients_db.update_procedure(procedure=procedure)
    ui.notify(message=status["message"],type=status["type"],position=status["position"])
    
    self.initial_data()
    self.ProceduresPanel(visit=[visit for visit in self.procedure_visits if visit.visit_id == visit_id][0])

  def client_mini(self,visit):
    """Returns a string of html elements for display in small screens"""

    def GenderIcon(visit):
      """Returns a styled gender icon based on client's gender"""

      genders = {"male":"mars","female":"venus"}
      colors = {"male":"sky-600","female":"pink-600"}

      return f"<span class='fa-solid fa-{genders[visit.client_gender.lower()]} text-{colors[visit.client_gender.lower()]}'></span>"
    
    age = f"<span class='ml-1'>{format_age(visit.client_birthdate).split(' ')[0]} {format_age(visit.client_birthdate).split(' ')[1][0].upper()}</span>"
    gender = GenderIcon(visit)
    payment_mode = f"<span class=''>{visit.payment_mode.upper()}</span>"

    return f"<span class='h-full'>{gender}{age}</span>"

  def procedures_mini(self,visit):
    """Returns a string of html elements for display of services in small screens"""
    procedures = visit.procedures
    _done = len([procedure for procedure in procedures if procedure["done"]])
    _cancelled = len([procedure for procedure in procedures if procedure["cancelled"]])
    _pending = len([procedure for procedure in procedures if not (procedure["cancelled"] or procedure["done"])])

    done = pending = cancelled = ""

    if _done:
      done = f"<span class='text-green-600'><span class='fas fa-check-double'></span><sup class='ml-0.5 text-bold'>{_done}</sup></span>"

    if _pending:
      pending = f"<span class='text-yellow-600'><span class='fa-solid fa-spinner fa-spin'></span><sup class='ml-0.5 text-bold'>{_pending}</sup></span>"

    if _cancelled:
      cancelled = f"<span class='text-gray-600'><span class='fa-solid fa-ban'></span><sup class='ml-0.5 text-bold'>{_cancelled}</sup></span>"
    
    #Returns
    if _done + _pending + _cancelled:
      return f"<span class='flex flex-row justify-between items-center'>{done}{pending}{cancelled}</span>"
    else:
      return "---"

  #UI
  def ProceduresDisplay(self,visits:dict):
    """A default panel to display procedures"""
    
    self.procedures_panel.clear()
    if visits:
      with self.procedures_panel.classes(remove="items-center justify-center"):
        #Large Screen
        ui.aggrid(
          {
            "columnDefs":[
              {"headerName":"S/N","field":"sno","width":50},
              {"headerName":"CLIENT ID","field":"client_id","filter":"agTextColumnFilter","width":100},
              {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":300},
              {"headerName":"AGE","field":"age","width":150},
              {"headerName":"GENDER","field":"gender","width":100},
              {"headerName":"ADDRESS","field":"address","width":120},
              {"headerName":"PROCEDURES","field":"procedures","filter":"agTextColumnFilter","floatingFilter":True,"width":200}
            ],
            "rowData":[
              {
                "sno":visits.index(visit) + 1,
                "client_id":visit.client_id,
                "name":visit.client_name.title(),
                "age":format_age(visit.client_birthdate),
                "gender":visit.client_gender.capitalize(),
                "address":visit.client_address.title(),
                "procedures":self.procedures(visit.procedures),
              } for visit in visits
            ]
          },
          theme="quartz",
          html_columns=[6]
        ).style(add="overflow-x:hidden;").classes(add="lg-show grow w-full animate__animated animate__fadeIn").on("cellClicked",lambda e:self.ProceduresDialog(visit=[visit for visit in self.procedure_visits if visit.client_id == e.args["data"]["client_id"]][0]))

        #Small Screen
        ui.aggrid(
          {
            "columnDefs":[
              {"headerName":"","field":"client_id","filter":"agTextColumnFilter","width":200},
              {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","floatingFilter":True,"width":300},
              {"headerName":"","field":"specs"},
              {"headerName":"","field":"services"}
            ],
            "rowData":[
              {
                "client_id":visit.client_id,
                "name":f"{visit.client_name.split(' ')[0]} {visit.client_name.split(' ')[-1]}".title(),
                "specs":self.client_mini(visit),
                "services":self.procedures_mini(visit)
              } for visit in visits
            ]
          },
          theme="quartz",
          html_columns=[2,3]
        ).props(add="").classes(add="lg:hidden grow w-full animate__animated animate__fadeIn").on("cellClicked",lambda e:self.ProceduresDialog(visit=[visit for visit in self.procedure_visits if visit.client_id == e.args["data"]["client_id"]][0]))

    else:
      with self.procedures_panel.classes(add="justify-center items-center"):
        ui.label("No procedure(s) planned currently").classes(add="text-red-500 font-bold italic text-xl fa-fade")
    
  def ProceduresDialog(self,visit:dict):
    """A dialog to display details of a procedure visit"""
    
    #DATA
    self.details = {
      "name":visit.client_name,
      "short_name":f"{visit.client_name.split(' ')[0]} {visit.client_name.split(' ')[-1]}".title(),
      "age":format_age(visit.client_birthdate,short=True),
      "gender":visit.client_gender,
      "address":visit.client_address
    }
    #FXS
    def close_dialog():
      self.initial_data()
      self.procedures_dialog.close()

    #UI
    with ui.dialog().props(add=f"transition-show='jump-up' transition-hide='jump-down' transition-duration='300'") as self.procedures_dialog,html.div().style(add="min-width:100%;min-height:100%;").classes(add="bg-sky-50 flex flex-col"):
      #Dialog Header
      with html.div().classes(add="bg-harmony w-full p-1 rounded-t flex flex-row items-center"):
        with html.div().classes(add="grow"):
          ClientCard(details=self.details)
        ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=close_dialog).classes(add="size-12 bg-inherit text-rose-600 text-bold text-lg")
      
      #Procedures
      with html.div().classes(add="grow w-full flex flex-col") as self.procedures_dialog_panel:
        self.ProceduresPanel(visit=visit)
    
    self.procedures_dialog.open()

  def ProceduresPanel(self,visit):
    """Panel for procedures listing and processing"""
    #DATA
    _procedures = [procedure for procedure in visit.procedures]
    cancelled_procedures = [procedure for procedure in _procedures if procedure["cancelled"]]
    done_procedures = [procedure for procedure in _procedures if procedure["done"]]
    not_done_procedures = [procedure for procedure in _procedures if not (procedure["cancelled"] or procedure["done"])]
    procedures = not_done_procedures + done_procedures + cancelled_procedures
    #UI
    self.procedures_dialog_panel.clear()
    with self.procedures_dialog_panel:
      with ui.scroll_area().classes(add="grow w-full animate__animated animate__fadeIn"):
        for procedure in procedures:
          #Data
          procedure_data = {
            "procedure_id":procedure["procedure_id"],
            "procedure_notes":procedure["procedure_notes"] if procedure["procedure_notes"] else None,
            "performer":f"{get_staff(procedure['performer']).first_name} {get_staff(procedure['performer']).last_name}".title() if procedure['performer'] else f"{self.user.first_name} {self.user.last_name}".title(),
            "assistant":f"{get_staff(procedure['assistant']).first_name} {get_staff(procedure['assistant']).last_name}".title() if procedure["assistant"] else None,
          }
          #miniUI
          with ui.expansion(value=True if procedures.index(procedure) == 0 and not (procedure["done"] or procedure["cancelled"]) else False,group="procedures_group").props(add=f"{'disable' if procedure['cancelled'] else ''} duration=500 expand-icon='fas fa-angles-down fa-lg' expand-icon-class='text-harmony text-bold' header-class='q-pa-none {'bg-gray-300' if procedure['cancelled'] else 'bg-sky-100'}'").classes(add="w-full rounded bg-sky-50 shadow-md shadow-[#07004d]") as expansion:
            with expansion.add_slot("header"):
              with html.div().classes(add="w-full grid grid-cols-6"):
                #Study
                ui.chip(text=procedure["name"].title(),text_color="sky-900",color="").classes(add="col-span-6 lg:col-span-2 rounded-sm m-0 px-2 bg-inherit text-xl text-bold")
                #Timeframe
                ui.chip(text=f"{format_age(procedure['ordered_on'])} ago",icon="fa-regular fa-clock fa-lg",text_color="sky-900",color="").classes(add="col-span-2 lg:col-span-1 rounded-sm px-2 bg-inherit text-base text-bold")
                #Payment status
                ui.chip(text="Paid" if procedure["payment"].paid else "Billed" if procedure["payment"].billed else "Not Paid",icon=f"{'fa-regular fa-circle-check' if procedure['payment'].paid else 'fa-solid fa-file-invoice' if procedure['payment'].billed else 'fa-regular fa-circle-xmark'} fa-lg",text_color="teal" if procedure["payment"].paid else "purple" if procedure["payment"].billed else "red",color="").classes(add="col-span-2 lg:col-span-1 rounded-sm px-2 bg-inherit text-base text-bold")
                #Imaging status
                ui.chip(
                  text="Done" if ((procedure["payment"].paid or procedure["payment"].billed) and procedure["done"]) else "Pending" if ((procedure["payment"].billed or procedure["payment"].paid) and not procedure["done"]) else "Not done",
                  icon=f"{'fa-regular fa-circle-check' if ((procedure['payment'].paid or procedure['payment'].billed) and procedure['done']) else 'fa-solid fa-spinner fa-spin' if ((procedure['payment'].billed or procedure['payment'].paid) and not procedure['done']) else 'fa-regular fa-circle-xmark fa-flip'} fa-lg",
                  text_color="teal" if ((procedure["payment"].paid or procedure["payment"].billed) and procedure["done"]) else "orange" if ((procedure["payment"].billed or procedure["payment"].paid) and not procedure["done"]) else "red",
                  color=""
                  ).classes(add="col-span-2 lg:col-span-1 lg:justify-self-end rounded-sm px-2 bg-inherit text-base text-bold")
            
            if not procedure["cancelled"]:
              with expansion.add_slot("default"):
                with html.div().classes(add="w-full p-1 flex flex-col gap-5"):
                  with html.div().classes(add="w-full grid grid-cols-3 gap-3"):
                    with html.div().classes(add="col-span-3 lg:col-span-1 w-full p-1 flex flex-col gap-2 justify-around"):
                      performer = ui.select(options=self.staffs,value=procedure_data['performer'],label="PERFORMED BY").props(add=f"{'' if procedure['payment'].paid or procedure['payment'].billed else 'readonly'} stack-label label-color='#07004d'").classes(add="w-full rounded bg-white shadow-md shadow-[#07004d] px-2 text-lg").bind_value(procedure_data,"performer")
                      assistant = ui.select(options=self.staffs,label="ASSISTED BY").props(add=f"{'' if procedure['payment'].paid or procedure['payment'].billed else 'readonly'} stack-label label-color='#07004d'").classes(add="w-full rounded bg-white shadow-md shadow-[#07004d] px-2 text-lg").bind_value(procedure_data,"assistant")
                    #Findings
                    notes = ui.textarea(label="PROCEDURE NOTES",placeholder="Write your observations and interventions done...").props(add="" if (procedure["payment"].paid or procedure["payment"].billed) else "readonly").props(add="autogrow clearable stack-label input-style='min-height:200px;' label-color='#07004d' bg-color='white' clear-icon='fa-regular fa-circle-xmark'").classes(add="col-span-3 lg:col-span-2 w-full bg-white shadow-md shadow-[#07004d] px-3 text-lg").bind_value(procedure_data,"procedure_notes")
                  
                  with html.div().classes(add="w-full flex flex-row justify-center"):
                    ider = ui.label(procedure['procedure_id']).classes(add="hidden") 
                    ui.button(text="submit results",color="",on_click=lambda e:self.save_procedure({
                      "procedure_id":e.sender.parent_slot.parent.slots["default"].children[0]._text,
                      "visit_id":visit.visit_id,
                      "procedure_notes":notes.value,
                      "performer":get_staff_username(name=performer.value),"assistant":get_staff_username(name=assistant.value)
                      })).props(add="" if (procedure["payment"].paid or procedure["payment"].billed) else "disabled").classes(add="rounded bg-harmony text-lg text-bold text-yellow-500")
  

#Store
class Requisitions():
  """A class to display and process requisitions"""

  def __init__(self,user):
    #DATA
    self.user = user
    self.initial_data()

    #UI
    with html.div().classes(add="grow w-full flex flex-col"):
      #Separator
      for i in range(2):
        ui.separator().classes(add="w-full bg-[#09026f]")
      #Header
      with html.section().classes(add="w-full p-1 flex flex-row bg-harmony text-yellow-500"):
        with html.div().classes(add="lg:order-2 grow bg-inherit flex flex-row content-center"):
          ui.label("REQUISITIONS").classes(add="w-full rounded-t text-3xl text-bold")
        ui.button(icon="fas fa-circle-plus",color="",on_click=self.RequisitionDialog).classes(add="lg:order-1 size-8 bg-inherit")
      #Body
      with html.section().classes(add="grow w-full p-0.5 flex flex-col rounded") as self.requisitions_panel:
        if self.requisitions:
          self.RequisitionsPanel()
        else:
          with html.div().classes(add="w-full h-full content-center justify-center bg-sky-100 p-5"):
            ui.label("No requisitions found").classes(add="text-center text-2xl text-red-400 font-semibold fa-fade")
            ui.label("Click the right upper '+' button to initiate new requisition").classes(add="text-center text-lg italic text-gray-500")

  #Functionalities
  def initial_data(self):
    base_requisitions = admin_processor.get_requisitions()
    self.requisitions = base_requisitions[:-1] if len(base_requisitions) > 1 else base_requisitions

    ###
    self.physical_count_id = str(uuid.uuid4()).split("-")[1]

  def mos(self,medicine=None,balance=0,amc=0):
    """A method that returns value of mos based on the input values"""
    mos = 0
    if medicine:
      balance = self.closing_balance(medicine)
      amc = self.amc(medicine)
    
    if amc > 0:
      mos = round(balance/amc,1)
    else:
      mos = 2 if balance > 0 else 0
    
    return math.floor(mos)
  
  def dos(self,balance,adc):
    dos = 0

    if adc > 0:
      dos = round(balance/amc,1)
    else:
      dos = 60 if balance > 0 else 0
    
    return math.floor(dos)
  
  def update_inventory(self,data,transfer:bool=False,count:bool=False,receive:bool=False):
    inventories = []
    
    if transfer:
      if not (data["main_balance"] > 0 and data["main_balance"] >= data["transfer_balance"]):
        ui.notify(message="Insufficient Main Store balance!",position="top",type="warning")
        return

      inventory = {
        "medicine_name":data["medicine_name"],
        "medicine_id":data["medicine_id"],
        "logger":self.user.username,
        "invoice":data["invoice"],
        "issuer":"main store",
        "receiver":"dispensing",
        "amount":data["transfer_balance"]
      }
      inventories.append(inventory)
    
    if count:
      main_inventory = {
        "medicine_name":data["medicine_name"],
        "medicine_id":data["medicine_id"],
        "logger":self.user.username,
        "invoice":data["invoice"],
        "issuer":"main store",
        "issuer_amount":data["main_count"],
        "receiver":"main store",
        "receiver_amount":data["main_count"],
        "amount":data["transfer_balance"]
      }
      disp_inventory = {
        "medicine_name":data["medicine_name"],
        "medicine_id":data["medicine_id"],
        "logger":self.user.username,
        "invoice":data["invoice"],
        "issuer":"dispensing",
        "issuer_amount":data["dispensing_count"],
        "receiver":"dispensing",
        "receiver_amount":data["dispensing_count"],
        "amount":data["transfer_balance"]
      }
      
      inventories += [main_inventory,disp_inventory]
    
    if receive:
      inventory = {
        "medicine_name":data["medicine_name"],
        "medicine_id":data["medicine_id"],
        "logger":self.user.username,
        "invoice":None,
        "issuer":"vendor",
        "receiver":"main store",
        "amount":data["received_amount"]
      }
      inventories.append(inventory)

    #DATABASE UPDATE
    status = [admin_db.register_inventory(inventory,transfer=transfer,count=count,received=receive) for inventory in inventories][0]

    #NOTIFICATION
    if not receive:
      ui.notify(message=status["message"],type=status["type"],position="top")

      self.ReceivedMedicinesDisplay(self.current_medicines)
  
  def receive_medicine(self,data):
    """Processes involve:update requisition rows,update inventory rows"""

    #Requisition
    data["expire_date"] = datetime.fromisoformat(data["expire_date"])
    data["received_by"] = self.user.username if data["received_amount"] else None
    data["rejected"] = True if data["rejected_amount"] else False
    data["rejected_amount"] = data["rejected_amount"] if data["rejected_amount"] else 0
    data["rejected_price"] = data["rejected_price"] if data["rejected_price"] else 0

    status = admin_db.update_requisition(data,receive=True)

    #Inventory
    self.update_inventory(data,receive=True)
    
    ui.notify(message=status["message"],type=status["type"],position="top")

    #Update display
    for curr_medicine in self.current_medicines:
      if curr_medicine["medicine_id"].lower() == data["medicine_id"].lower():
        index = self.current_medicines.index(curr_medicine)
        self.current_medicines.pop(index)
        self.current_medicines.insert(index,data)
    self.MedicinesReceivingDisplay(self.current_medicines)

  def initiate_requisition(self):
    available_requisitions = admin_processor.get_requisitions(skim=True)

    if available_requisitions["initiated"]:
      ui.notify(message="There is pending order",caption="Complete processing that order first",type="warning",position="top")
      return

    for medicine in self.current_medicines:
      status = admin_db.register_requisition(medicine)
      
    ui.notify(message=status['message'],type=status["type"],position="top")

    self.MedicinesOrderingDisplay(self.current_medicines)

  def confirm_requisition_order(self):
    for medicine in self.current_medicines:
      status = admin_db.update_requisition(medicine,confirm_order=True)
      
    ui.notify(message=status['message'],type=status["type"],position="top")

    self.initial_data()
    self.RequisitionsPanel()

  def confirm_requisition_received(self):
    for medicine in self.current_medicines:
      status = admin_db.update_requisition(medicine,confirm_received=True)
      
    ui.notify(message=status['message'],type=status["type"],position="top")

    self.initial_data()
    self.RequisitionsPanel()

  def order_medicine(self,data):
    """"""
    status = admin_db.update_requisition(data,order=True)

    ui.notify(message=status["message"],type=status["type"],position="top")

    #Update display
    for curr_medicine in self.current_medicines:
      if curr_medicine["medicine_id"].lower() == data["medicine_id"].lower():
        index = self.current_medicines.index(curr_medicine)
        self.current_medicines.pop(index)
        self.current_medicines.insert(index,data)
    self.MedicinesOrderingDisplay(self.current_medicines)

  #FORMATTING FETCHED DATA
  async def fetch_medicine_data(self,medicine,index:int,new:bool=False,received:bool=False):
    fetched_data = admin_processor.get_consumption_data(medicine["medicine_id"])
    physical_count = admin_processor.get_physical_count(medicine_id=medicine["medicine_id"],time=datetime.now())
    
    formatted_data = {
      "sno":index + 1,
      "main_balance":fetched_data['balance'].main,
      "dispensing_balance":fetched_data['balance'].dispensing,
      "current_balance":fetched_data['balance'].total,
      "amc":fetched_data['averages'].monthly,
      "adc":fetched_data['averages'].daily,
      "mos":self.mos(balance=fetched_data['balance'].total,amc=fetched_data['averages'].monthly),
      "dos":self.dos(fetched_data['balance'].total,fetched_data['averages'].daily),
      "last_count":physical_count.date.strftime("%d %b %Y") if physical_count else "---",
      "medicine_id":medicine["medicine_id"]
    }
    
    if new:
      
      formatted_data.update({
        "name":medicine["name"],
        "medicine_name":medicine["name"],
        "requisition_id":medicine["requisition_id"],
        "type":medicine["type"] if "type" in medicine else None,
        "ordered":medicine["ordered"] if "ordered" in medicine else False,
        "order_unit":medicine["order_unit"] if "order_unit" in medicine else "",
        "order_unit_size":medicine["order_unit_size"] if "order_unit_size" in medicine else 1,
        "ordered_amount":medicine["ordered_amount"] if "ordered_amount" in medicine else 0,
        "ordered_units":0,
        "unit_price":medicine["unit_price"] if "unit_price" in medicine else 0,
        "ordered_price":medicine["ordered_price"] if "ordered_price" in medicine else 0,
        "ordered_by":self.user.username
      })

    elif received:
      formatted_data.update({
        "name":medicine["medicine_name"],
        "expiry_date":medicine["expire_date"].strftime("%b %Y") if medicine["expire_date"] else "---",
        "ordered":medicine["ordered"],
        "received":medicine["received"],
        "expiry_date":medicine["expire_date"].strftime("%b %Y") if medicine["expire_date"] else "---"
      })
    
    return formatted_data

  async def fetch_inventory_data(self,medicine_id):
    fetched_data = await admin_processor.get_inventory_data(medicine_id)
    return {
      "medicine_id":medicine_id,
      "invoice":self.physical_count_id,
      "issuer":None,
      "receiver":None,
      "previous_dispensing_balance":fetched_data["balance"].dispensing,
      "previous_main_balance":fetched_data["balance"].main,
      "main_balance":fetched_data["balance"].main,
      "dispensing_balance":fetched_data["balance"].dispensing,
      "last_count":fetched_data["last_count"].date,
      "transferable":True if fetched_data["balance"].main else False
    }

  #DISPLAYS
  def RequisitionsPanel(self):
    """A method to display list of requisitions"""
    
    #UI
    self.requisitions_panel.clear()
    with self.requisitions_panel:
      #Small screen
      with ui.scroll_area().classes(add="lg:hidden bg-white rounded-none grow w-full"):
        for requisition in self.requisitions:
          with ui.button(color="",on_click=lambda e:self.RequisitionDialog(requisition=[requisition for requisition in self.requisitions if requisition.name.lower() == e.sender.props["id"].lower()][0])).props(add=f"glossy id='{requisition.name}'").classes(add="w-full bg-harmony"):
            #Header
            with html.div().classes(add="w-full flex flex-row justify-between"):
              ui.label(requisition.name.upper()).classes(add="text-xl text-sky-500")
              ui.icon(name="fa-solid fa-check-double" if requisition.requisition_received else "fa-solid fa-spinner fa-spin" if requisition.requisition_ordered else "fa-solid fa-dots",color="green" if requisition.requisition_received else "yellow" if requisition.requisition_ordered else "gray")
            
            #Separator
            ui.separator().classes(add="w-full bg-sky-200")

            #Details
            with html.div().classes(add="w-full flex flex-col"):
              #Ordered
              with html.div().classes(add="w-full grid grid-cols-6 text-sky-100"):
                #Label
                ui.label("ORDERED").style(add="text-shadow:1px 1px #baebaebae;").classes(add="text-sky-300 justify-self-start")
                #Date
                ui.label(requisition.ordered_on.strftime("%d %b %Y") if requisition.requisition_ordered else "---").classes(add="col-span-2")
                #Amount
                ui.label(f"{requisition.ordered:,.0f} ITEM{'' if requisition.ordered == 1 else 'S'}" if requisition.requisition_ordered else "---").classes(add="justify-self-end")
                #Price
                ui.label(f"{requisition.ordered_price:,.2f} TZS" if requisition.requisition_ordered else "---").classes(add="col-span-2 justify-self-end")

              #Received
              with html.div().classes(add="w-full grid grid-cols-6 text-sky-100"):
                #Label
                ui.label("RECEIVED").style(add="text-shadow:1px 1px #baebaebae;").classes(add="text-sky-300 justify-self-start")
                #Date
                ui.label(requisition.received_on.strftime("%d %b %Y") if requisition.requisition_received else "---").classes(add="col-span-2")
                #Amount
                ui.label(f"{requisition.received:,.0f} ITEM{'' if requisition.received == 1 else 'S'}" if requisition.requisition_received else "---").classes(add="justify-self-end")
                #Price
                ui.label(f"{requisition.received_price:,.2f} TZS" if requisition.requisition_received else "---").classes(add="col-span-2 justify-self-end")

              #Rejected
              if requisition.rejected:
                with html.div().classes(add="w-full grid grid-cols-6 text-sky-100"):
                  #Label
                  ui.label("REJECTED").style(add="text-shadow:1px 1px #baebaebae;").classes(add="text-sky-300 justify-self-start")
                  #Date
                  ui.label().classes(add="col-span-2")
                  #Amount
                  ui.label(f"{requisition.rejected:,.0f} ITEM{'' if requisition.rejected == 1 else 'S'}" if requisition.rejected else "---").classes(add="justify-self-end")
                  #Price
                  ui.label(f"{requisition.rejected_price:,.2f} TZS" if requisition.rejected else "---").classes(add="col-span-2 justify-self-end")
            
            #Other Details
            with html.div().classes(add="w-full"):
              pass


      #Large Screen
      ui.aggrid(
        options={
          "columnDefs":[
            {"headerName":"","field":"sno","width":75},
            {"headerName":"NAME","field":"name","sortable":True},
            {"headerName":"ORDERED","field":"ordered","type":"rightAligned"},
            {"headerName":"ORDER PRICE","field":"order_cost","type":"rightAligned"},
            {"headerName":"ORDER DATE","field":"order_date","type":"rightAligned"},
            {"headerName":"RECEIVED","field":"received","type":"rightAligned"},
            {"headerName":"RECEIVE PRICE","field":"receive_cost","type":"rightAligned"},
            {"headerName":"RECEIVE DATE","field":"receive_date","type":"rightAligned"},
            {"headerName":"REJECTED","field":"rejected","type":"rightAligned"},
            {"headerName":"REJECTED PRICE","field":"rejected_cost","type":"rightAligned"},
          ],
          "rowData":[
            {
              "sno":self.requisitions.index(requisition) + 1,
              "name":requisition.name.upper(),
              "ordered":f"{requisition.ordered:,.0f}" if requisition.requisition_ordered else "---",
              "order_cost":f"{requisition.ordered_price:,.2f}" if requisition.requisition_ordered else "---",
              "order_date":requisition.ordered_on.strftime("%d %b %Y") if requisition.requisition_ordered else "---",
              "received":f"{requisition.received:,.0f}" if requisition.requisition_received else "---",
              "receive_cost":f"{requisition.received_price:,.2f}" if requisition.requisition_received else "---",
              "receive_date":requisition.received_on.strftime("%d %b %Y") if requisition.requisition_received else "---",
              "rejected":f"{requisition.rejected:,.0f}" if requisition.rejected else "---",
              "rejected_cost":f"{requisition.rejected_price:,.2f}" if requisition.rejected else "---"
            } for requisition in self.requisitions
          ],
          "pagination":True,
          "paginationPageSize":10
        },
        theme="quartz",
        html_columns=[4,5,6]
      ).classes(add="lg-show grow w-full bg-inherit text-sm animate__animated animate__fadeIn").on("cellClicked",lambda e:self.RequisitionDialog(requisition=[requisition for requisition in self.requisitions if requisition.name.lower() == e.args["data"]["name"].lower()][0]))

  def RequisitionDialog(self,requisition=None):
    """A method for displaying requisistion form"""

    #DATA
    if requisition:
      requisition = requisition._asdict()
      requisition["medicines"]=[medicine._asdict() for medicine in requisition["medicines"]]
      medicines = requisition["medicines"]

    else:
      #new requisition
      requisition = {
        "name":f"req{str(uuid.uuid4()).split('-')[1]}".upper(),
        "requisition_initiated":False,
        "requisition_ordered":False,
        "requisition_received":False
      }
      medicines = admin_processor.get_formulary()
      medicines = [medicine._asdict() for medicine in medicines]

    
    #FXS
    def close_dialog():
      self.requisition_dialog.close()

    #UI
    with ui.dialog().props(add="transition-show='jump-up' transition-hide='jump-down' transition-duration='500'") as self.requisition_dialog,html.div().style(add="min-width:100%;min-height:100%;").classes(add="bg-sky-100 p-0.5 flex flex-col"):
      #Header
      with html.header().classes(add="w-full rounded-t bg-harmony grid grid-cols-11 items-center"):
        #Details
        with html.div().classes(add="col-span-10 w-full p-1 flex flex-col"):
          #Requisition ID
          ui.label(requisition["name"].upper()).classes(add="w-full text-bold text-sky-500 text-xl")
          
          #Requisition Summary
          with html.div().classes(add=f"w-fit grid {'grid-cols-2 lg:grid-cols-5' if requisition['requisition_received'] else 'grid-rows-3 grid-cols-1 lg:grid-cols-3 lg:grid-rows-1'} gap-1 text-bold text-sky-300"):
            if requisition["requisition_received"]:
              #Invoice
              with html.div().classes(add="grid grid-cols-3 gap-1"):
                html.span("INVOICE").classes(add="text-sky-300")
                html.span(requisition["invoice"] if requisition["invoice"] else "---").classes(add="text-white col-span-2 justify-self-start")
              
              #Items
              with html.div().classes(add="grid grid-cols-3 gap-1"):
                html.span("ITEMS").classes(add="text-sky-300")
                html.span(f"{requisition['received']:,.0f}").classes(add="text-white col-span-2 justify-self-start")
              
              #Delivery Note
              with html.div().classes(add="lg:col-span-2 grid grid-cols-3 gap-1"):
                html.span("DELIVERY NOTE").classes(add="text-sky-300")
                html.span(requisition["delivery_note"] if requisition["delivery_note"] else "---").classes(add="text-white col-span-2 justify-self-start")
              
              #Price
              with html.div().classes(add="grid grid-cols-3 gap-1"):
                html.span("COST").classes(add="text-sky-300")
                html.span(f"{requisition['received_price']:,.2f} TZS").classes(add="text-white col-span-2 justify-self-start")
              
            elif requisition["requisition_ordered"]:
              #Ordered items
              with html.div().classes(add="grid grid-cols-3"):
                html.span("ORDERED ITEMS").classes(add="col-span-2 text-sky-300")
                html.span(f"{requisition['ordered']:,.0f}").classes(add="text-white")
              
              #Ordered Price
              with html.div().classes(add="grid grid-cols-3"):
                html.span("ORDERED PRICE").classes(add="col-span-2 text-sky-300")
                html.span(f"{requisition['ordered_price']:,.2f}").classes(add="text-white")
              
              #Order DAte
              with html.div().classes(add="grid grid-cols-3"):
                html.span("ORDER DATE").classes(add="col-span-2 text-sky-300")
                html.span(requisition['ordered_on'].strftime("%d %b %Y")).classes(add="text-white")
              
        #Button
        ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=close_dialog).classes(add="bg-inherit text-red-600 text-xl justify-self-end")
      
      #Body
      with html.div().classes(add="grow w-full flex flex-col") as self.requisition_display_panel:
        if requisition["requisition_received"]:
          self.ReceivedMedicinesDisplay(medicines)
        elif requisition["requisition_ordered"]:
          self.MedicinesReceivingDisplay(medicines)
        else:
          self.MedicinesOrderingDisplay(medicines=medicines,requisition=requisition)
      
      #Buttons
      with html.div().classes(add="p-1 flex flex-row justify-center gap-3"):
        if requisition["requisition_received"]:
          pass
        elif requisition["requisition_ordered"]:
          ui.button(text="RECEIVE ORDER",color="",on_click=self.confirm_requisition_received).classes(add="bg-harmony text-green-600 text-bold text-lg")
          #ui.button(text="CANCEL ORDER",color="",on_click=lambda e:ui.notify('confirm')).classes(add="bg-harmony text-red-600 text-bold text-lg")
        elif requisition["requisition_initiated"]:
          ui.button(text="CONFIRM ORDER",color="",on_click=self.confirm_requisition_order).props(add="glossy").classes(add="bg-harmony text-teal-500 text-bold text-lg")
        else:
          ui.button(text="INITIATE ORDER",color="",on_click=self.initiate_requisition).props(add="glossy").classes(add="bg-harmony text-sky-300 text-bold text-lg").bind_visibility_from(requisition,"requisition_initiated",backward=lambda val:not val)

        
    self.requisition_dialog.open()
    
  def MedicinesOrderingDisplay(self,medicines,requisition=None):
    """"""
    #DATA
    for medicine in medicines:
      if requisition:
        medicine["requisition_id"] = requisition["name"].lower()
      if "medicine_name" in medicine:
        medicine["name"] = medicine["medicine_name"]
    self.current_medicines = medicines   #This is for refreshing the medicines panel after editing a given medicines

    #FXS
    async def show_main_display():
      medicines = [await self.fetch_medicine_data(medicine=medicine,index=self.current_medicines.index(medicine),new=True) for medicine in self.current_medicines]
      self.current_medicines = medicines

      #Large screen
      main_grid.options["rowData"] = medicines
      main_grid.update()

      #Small Screen
      with scroll_panel:
        for medicine in medicines:
          self.SmallScreenMedicineDisplay(medicine,new=True)

      spinner_display.visible = False
      main_display.visible = True

    #UI
    self.requisition_display_panel.clear()
    with self.requisition_display_panel:
      #Loading spinner
      with html.div().classes(add="grow w-full flex flex-col justify-center items-center") as spinner_display:
        PageLoading()
      
      #Main display
      main_display = html.div().classes(add="grow w-full py-2 lg:p-0 flex flex-col bg-sky-50")
      main_display.visible = False
      
      with main_display:
        #Large screen
        main_grid = ui.aggrid(
          options={
            "columnDefs":[
              {"headerName":"","field":"sno","width":100},
              {"headerName":"NAME","field":"name","sortable":True,"filter":True,"floatingFilter":True,"width":500},
              {"headerName":"LAST COUNT","field":"last_count","type":"rightAligned"},
              {"headerName":"CLOSING BALANCE","field":"current_balance","type":"rightAligned","width":300},
              {"headerName":"AMC","field":"amc","type":"rightAligned"},
              {"headerName":"MOS","field":"mos","type":"rightAligned"},
              {"headerName":"ORDER QTY","field":"ordered_amount","type":"rightAligned"},
              {"headerName":"ORDER PRICE","field":"ordered_price","type":"rightAligned"}
            ],
            "rowData":[],
            "defaultColDef":{
              "headerClass":"text-bold text-harmony",
              "cellClass":"uppercase"
            }
          },
          theme="quartz"
        ).classes(add="lg-show grow w-full animate__animated animate__fadeIn").on("cellClicked",lambda e:self.MedicineDialog(e.args["data"],new=True))
        
        #Small screen
        scroll_panel = ui.scroll_area().props(add="").classes(add="lg:hidden grow w-full")
    
    #Cosmetics
    main_display.visible = False

    #Timer
    ui.timer(0.1,show_main_display,once=True)
  
  def MedicinesReceivingDisplay(self,medicines):
    """"""
    #DATA
    for medicine in medicines:
      medicine["sno"] = medicines.index(medicine) + 1
    self.current_medicines = medicines   #This is for refreshing the medicines panel after editing a given medicines

    #UI
    self.requisition_display_panel.clear()
    with self.requisition_display_panel:
      #Main display
      with html.div().classes(add="grow w-full py-2 lg:p-0 flex flex-col bg-sky-50"):
        #Large screen
        ui.aggrid(
          options={
            "columnDefs":[
              {"headerName":"","field":"sno","width":100},
              {"headerName":"NAME","field":"name","sortable":True,"filter":True,"floatingFilter":True,"width":500},
              {"headerName":"EXPIRY DATE","field":"expiry_date","type":"rightAligned"},
              {"headerName":"ORDERED QTY","field":"ordered_amount","type":"rightAligned"},
              {"headerName":"ORDERED PRICE","field":"ordered_price","type":"rightAligned","width":200},
              {"headerName":"RECEIVED QTY","field":"received_amount","type":"rightAligned"},
              {"headerName":"RECEIVED PRICE","field":"received_price","type":"rightAligned"},
              {"headerName":"REJECTED QTY","field":"rejected_amount","type":"rightAligned"},
            ],
            "rowData":[{
              "sno":medicines.index(medicine) + 1,
              "name":medicine["medicine_name"],
              "expiry_date":medicine["expire_date"].strftime("%b %Y") if medicine["expire_date"] else "---",
              "ordered_amount":f"{medicine['ordered_amount']:,.0f}",
              "ordered_price":f"{medicine["ordered_price"]:,.2f}",
              "received_amount":f"{medicine['received_amount']:,.0f}",
              "received_price":f"{medicine["received_price"]:,.2f}",
              "rejected_amount":f"{medicine['rejected']:,.0f}",
              "rejected_price":f"{medicine["rejected_price"]:,.2f}",
              "medicine_id":medicine["medicine_id"]
            } for medicine in medicines],
            "defaultColDef":{
              "headerClass":"text-bold text-harmony",
              "cellClass":"uppercase"
            }
          },
          theme="quartz"
        ).classes(add="lg-show grow w-full animate__animated animate__fadeIn").on("cellClicked",lambda e:self.MedicineDialog(data=[medicine for medicine in medicines if medicine["medicine_id"] == e.args["data"]["medicine_id"]][0],ordered=True))
        
        #Small screen
        with ui.scroll_area().props(add="").classes(add="lg:hidden grow w-full"):
          for medicine in medicines:
            self.SmallScreenMedicineDisplay(medicine,ordered=True)
    
  def ReceivedMedicinesDisplay(self,medicines):
    """"""
    #DATA
    self.current_medicines = medicines   #This is for refreshing the medicines panel after editing a given medicines

    #FXS
    async def show_main_display():
      medicines = [await self.fetch_medicine_data(medicine=medicine,index=self.current_medicines.index(medicine),received=True) for medicine in self.current_medicines]

      #Large screen
      main_grid.options["rowData"] = medicines
      main_grid.update()

      #Small Screen
      with scroll_panel:
        for medicine in medicines:
          self.SmallScreenMedicineDisplay(medicine,received=True)

      spinner_display.visible = False
      main_display.visible = True

    #UI
    self.requisition_display_panel.clear()
    with self.requisition_display_panel:
      #Loading spinner
      with html.div().classes(add="grow w-full flex flex-col justify-center items-center") as spinner_display:
        PageLoading()
      
      #Main display
      main_display = html.div().classes(add="grow w-full py-2 lg:p-0 flex flex-col bg-sky-50")
      main_display.visible = False
      
      with main_display:
        #Large screen
        main_grid = ui.aggrid(
          options={
            "columnDefs":[
              {"headerName":"","field":"sno","width":100},
              {"headerName":"NAME","field":"name","sortable":True,"filter":True,"floatingFilter":True,"width":500},
              {"headerName":"EXPIRY DATE","field":"expiry_date","type":"rightAligned"},
              {"headerName":"MAIN STORE","field":"main_balance","type":"rightAligned"},
              {"headerName":"DISPENSING","field":"dispensing_balance","type":"rightAligned"},
              {"headerName":"AMC","field":"amc","type":"rightAligned"},
              {"headerName":"ADC","field":"adc","type":"rightAligned"},
              {"headerName":"MOS","field":"mos","type":"rightAligned"},
              {"headerName":"DOS","field":"dos","type":"rightAligned","headerTooltip":"Days of consumption"},
              {"headerName":"LAST COUNT","field":"last_count","type":"rightAligned"}
            ],
            "rowData":[],
            "defaultColDef":{
              "headerClass":"text-bold text-harmony",
              "cellClass":"uppercase"
            }
          },
          theme="quartz"
        ).classes(add="lg-show grow w-full animate__animated animate__fadeIn").on("cellClicked",lambda e:self.MedicineDialog(e.args["data"],received=True))
        
        #Small screen
        scroll_panel = ui.scroll_area().props(add="").classes(add="lg:hidden grow w-full")
    
    #Cosmetics
    main_display.visible = False

    #Timer
    ui.timer(0.1,show_main_display,once=True)
  
  def SmallScreenMedicineDisplay(self,medicine,new:bool=False,ordered:bool=False,received:bool=False):
    """Displays a button widget for one medicine in medicines display panels above"""
    #DATA
    medicine["name"] = medicine["medicine_name"] if "medicine_name" in medicine else medicine["name"]
    
    #UI
    with ui.button(color="",on_click=lambda e:self.MedicineDialog(medicine,new=new,ordered=ordered,received=received)).props(add="dense").classes(add="w-full p-1 pr-3 bg-sky-100 shadow-md shadow-[#07004d]"):
      if received:
        #Header
        with html.div().classes(add="w-full grid grid-cols-11"):
          with ui.label(f"{medicine['sno']}. ").classes(add="col-span-10 justify-self-start text-start text-sky-600 text-lg"):
            ui.label(medicine["name"].upper()).classes(add="inline ml-1 text-harmony")
          ui.icon(name=f"fa-solid {'fa-circle-check'if medicine["received"] else 'fa-circle-xmark'}",color="green" if medicine["received"] else "red").classes(add="justify-self-end")
        
        #Separator
        ui.separator().classes(add="w-full bg-harmony")

        #Details
        if medicine["received"]:
          with html.div().classes(add="w-full grid grid-cols-3"):
            #Expiry Date
            ui.chip(text=medicine["expiry_date"],icon="fa-solid fa-hourglass-half fa-sm",color="",text_color="").props(add="dense").classes(add="bg-inherit text-sky-700 text-bold")
        
        #Stats
        with html.div().classes(add="w-full grid grid-cols-5"):
          #Balances
          with html.div().classes(add="col-span-3 grid grid-cols-2"):
            ui.label("MAIN STORE").classes(add="text-start font-bold")
            ui.label(medicine["main_balance"]).classes(add="justify-self-start font-medium text-sky-700")
            ui.label("DISPENSING").classes(add="text-start font-bold")
            ui.label(medicine["dispensing_balance"]).classes(add="justify-self-start font-medium text-sky-700")
          
          #Daily Stats
          with html.div().classes(add="flex grid grid-cols-3"):
            ui.label("ADC").classes(add="text-start font-bold")
            ui.label(medicine["adc"]).classes(add="col-span-2 font-medium text-sky-700")
            ui.label("DOS").classes(add="text-start font-bold")
            ui.label(medicine["dos"]).classes(add="col-span-2 font-medium text-sky-700")
          
          #Monthly stats
          with html.div().classes(add="flex grid grid-cols-3"):
            ui.label("AMC").classes(add="text-start font-bold")
            ui.label(medicine["amc"]).classes(add="col-span-2 font-medium text-sky-700")
            ui.label("MOS").classes(add="text-start font-bold")
            ui.label(medicine["mos"]).classes(add="col-span-2 font-medium text-sky-700")
                
      elif ordered:
        #Header
        with html.div().classes(add="w-full grid grid-cols-11"):
          with ui.label(f"{medicine['sno']}. ").classes(add="col-span-10 justify-self-start text-start text-sky-700 text-lg"):
            ui.label(medicine["name"].upper()).classes(add="inline ml-1 text-harmony")
          ui.icon(name=f"fa-solid {'fa-circle-check'if medicine["received"] else 'fa-circle-xmark'}",color="green" if medicine["received"] else "red").classes(add="justify-self-end")
        
        #Separator
        ui.separator().classes(add="w-full bg-harmony")

        #Details
        if medicine["received"]:
          with html.div().classes(add="w-full grid grid-cols-3"):
            #Expiry Date
            ui.chip(text=medicine["expire_date"],icon="fa-solid fa-hourglass-half fa-sm",color="",text_color="").props(add="dense").classes(add="bg-inherit text-sky-700 text-bold")
        
        #Stats
        with html.div().classes(add="w-full p-1 grid grid-cols-2 gap-2"):
          with html.span().classes(add="w-full flex flex-col gap-0 rounded shadow-sm shadow-[#07004d]"):
            ui.label("ORDERED QTY").classes(add="rounded-t bg-harmony text-sky-300 text-center font-bold")
            ui.label(medicine["ordered_amount"]).classes(add="rounded-b font-medium text-sky-700")
          
          with html.span().classes(add="w-full flex flex-col gap-0 rounded shadow-sm shadow-[#07004d]"):
            ui.label("ORDERED PRICE").classes(add="rounded-t bg-harmony text-sky-300 text-center font-bold")
            ui.label(medicine["ordered_price"]).classes(add="rounded-b font-medium text-sky-700")

          with html.span().classes(add="w-full flex flex-col gap-0 rounded shadow-sm shadow-[#07004d]"):
            ui.label("RECEIVED QTY").classes(add="rounded-t bg-harmony text-sky-300 text-center font-bold")
            ui.label(medicine["received_amount"]).classes(add="rounded-b font-medium text-sky-700")
          
          with html.span().classes(add="w-full flex flex-col gap-0 rounded shadow-sm shadow-[#07004d]"):
            ui.label("RECEIVED PRICE").classes(add="rounded-t bg-harmony text-sky-300 text-center font-bold")
            ui.label(medicine["received_price"]).classes(add="rounded-b font-medium text-sky-700")

          with html.span().classes(add="w-full flex flex-col gap-0 rounded shadow-sm shadow-[#07004d]"):
            ui.label("REJECTED QTY").classes(add="rounded-t bg-harmony text-sky-300 center font-bold")
            ui.label(medicine["rejected_amount"]).classes(add="rounded-b font-medium text-sky-700")

          with html.span().classes(add="w-full flex flex-col gap-0 rounded shadow-sm shadow-[#07004d]"):
            ui.label("REJECTED PRICE").classes(add="rounded-t bg-harmony text-sky-300 text-center font-bold")
            ui.label(medicine["rejected_price"]).classes(add="rounded-b font-medium text-sky-700")
        
      elif new:
        #Header
        with html.div().classes(add="w-full grid grid-cols-11"):
          with ui.label(f"{medicine['sno']}. ").classes(add="col-span-10 justify-self-start text-start text-sky-700 text-lg"):
            ui.label(medicine["name"].upper()).classes(add="inline ml-1 text-harmony")
          ui.icon(name=f"fa-solid {'fa-circle-check'if medicine["ordered"] else 'fa-circle-xmark'}",color="green" if medicine["ordered"] else "red").classes(add="justify-self-end")
        
        #Separator
        ui.separator().classes(add="w-full bg-harmony")

        #Stats
        with html.div().classes(add="w-full grid grid-cols-4"):
          #Balances
          with html.div().classes(add="col-span-3 grid grid-cols-2"):
            ui.label("CLOSING BAL").classes(add="text-start font-bold")
            ui.label(f"{medicine['current_balance']:,.0f}").classes(add="justify-self-start font-medium text-sky-700")
            ui.label("ORDERED QTY").classes(add="text-start font-bold")
            ui.label(f"{medicine['ordered_amount']:,.0f}").classes(add="justify-self-start font-medium text-sky-700")
          
          #Daily Stats
          with html.div().classes(add="flex grid grid-cols-3"):
            ui.label("AMC").classes(add="text-start font-bold")
            ui.label(f"{medicine['amc']:,.0f}").classes(add="col-span-2 self-justify-end font-medium text-sky-700")
            ui.label("MOS").classes(add="text-start font-bold")
            ui.label(f"{medicine['mos']:,.0f}").classes(add="col-span-2 self-justify-end font-medium text-sky-700")

  def MedicineDialog(self,data,new:bool=False,ordered:bool=False,received:bool=False):
    """A method to display medicine dialog"""
    #DATA
    if received:
      medicine_id,name = data["medicine_id"],data["name"]
      inventory_data = {
        "medicine_name":name,
        "main_balance":0,
        "dispensing_balance":0,
        "transfer_balance":0,
        "last_count":None,
        "transferable":False,
        "main_count":0,
        "dispensing_coung":0
      }
    elif ordered:
      medicine = data
    elif new:
      medicine = data

    #FXS
    async def update_inventory_data():
      inventory_data.update(await self.fetch_inventory_data(medicine_id))

      transfer_input.update()

      for spinner in [spinner_1,spinner_2,spinner_3,spinner_4,spinner_5]:
        spinner.visible = False
      
      for label in [main_balance_label,main_balance_label_2,disp_balance_label,disp_balance_label_2,last_count_label]:
        label.visible = True
    
    def calculate_units(value):
      return math.ceil(value/medicine["order_unit_size"])
    
    def calculate_price(unit_price):
      if unit_price:
        return unit_price * (medicine["ordered_amount"]/medicine["order_unit_size"])
      else:
        return 0

    #UI
    with ui.dialog() as self.medicine_dialog,html.div().style(add=f"min-width:30%;min-height:50%;").classes(add="bg-sky-100 p-0.5 flex flex-col gap-0"):
      #For received medicine
      if received:
        #Header
        with html.header().classes(add="bg-harmony w-full grid grid-cols-11 items-center"):
          #Title
          ui.label(name).classes(add="col-span-10 w-full p-1 rounded-t text-2xl lg:text-3xl text-bold text-center text-sky-300 uppercase")
          ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=self.medicine_dialog.close).classes(add="bg-inherit text-red-600 text-xl justify-self-end")
        
        #Body
        with html.div().classes(add="grow w-full p-2 flex flex-col gap-5"): 
          #Updating received medicine
          if received:
            #Transfer to dispensing store
            with html.div().classes(add="w-full rounded bg-sky-100 shadow-sm shadow-[#07004d] flex flex-col gap-1"):
              #Header
              with html.div().classes(add="w-full flex flex-col"):
                ui.label("TRANSFER TO DISPENSING STORE").classes(add="w-full p-1 rounded-t bg-harmony text-sky-300 text-bold text-xl text-start")
              
              with html.div().classes(add="w-full p-1 grid grid-cols-2 gap-3"):
                #Main Store balance
                with ui.label("MAIN STORE:").classes(add="bg-inherit text-center text-harmony text-bold text-xl"):
                  spinner_1 = ui.spinner(type="dots",size="md").classes(add="inline ml-1")
                  main_balance_label = ui.label().classes(add="inline ml-1 bg-inherit text-sky-600 text-bold text-xl").bind_text_from(inventory_data,"main_balance",backward=lambda balance:f"{balance:,.0f}")
              
                #Dispensing Store balance
                with ui.label("DISPENSING:").classes(add="bg-inherit text-center text-harmony text-bold text-xl"):
                  spinner_2 = ui.spinner(type="dots",size="md").classes(add="inline ml-1")
                  disp_balance_label = ui.label().classes(add="inline ml-1 bg-inherit text-sky-600 text-bold text-xl").bind_text_from(inventory_data,"dispensing_balance",backward=lambda balance:f"{balance:,.0f}")
              
              #Inputs & Buttons
              with html.div().classes(add="w-full p-2 flex flex-row justify-center gap-5 p-0.5").bind_visibility_from(inventory_data,"transferable"):
                transfer_input = ui.number(label=f"No of {uom(name)}s".upper(),min=inventory_data["main_balance"]).props(add="stack-label").classes(add="w-40 rounded shadow-md shadow-[#07004d] px-5 bg-sky-50 text-lg").bind_value(inventory_data,"transfer_balance")
                ui.button(text="TRANSFER",color="",on_click=lambda e:self.update_inventory(data=inventory_data,transfer=True)).props(add="glossy").classes(add="bg-harmony text-yellow-500 text-bold text-xl")
            
            #Physical count
            with html.div().classes(add="w-full rounded bg-sky-100 shadow-sm shadow-[#07004d] flex flex-col gap-1"):
              #Header
              with html.div().classes(add="w-full rounded-t flex flex-col bg-harmony"):
                ui.label("PHYSICAL COUNT").classes(add="w-full p-0 px-1 rounded-t bg-inherit text-sky-300 text-bold text-xl text-start")
                with ui.label("Last Count:").classes(add="p-0 px-1 rounded-t bg-inherit text-sky-100 text-bold text-md text-start"):
                  spinner_3 = ui.spinner(type="dots",size="md").classes(add="inline ml-1")
                  last_count_label = ui.label().classes(add="inline ml-1 px-1 text-white text-md").bind_text_from(inventory_data,"last_count",backward=lambda count_date:count_date.strftime("%d %b %Y") if count_date else "---")
                
              with html.div().classes(add="w-full p-1 grid grid-cols-2 gap-3"):
                #Main Store balance
                with ui.label("MAIN STORE:").classes(add="bg-inherit text-center text-harmony text-bold text-xl"):
                  spinner_4 = ui.spinner(type="dots",size="md").classes(add="inline ml-1")
                  main_balance_label_2 = ui.label().classes(add="inline ml-1 bg-inherit text-sky-600 text-bold text-xl").bind_text_from(inventory_data,"main_balance",backward=lambda balance:f"{balance:,.0f}")
              
                #Dispensing Store balance
                with ui.label("DISPENSING:").classes(add="bg-inherit text-center text-harmony text-bold text-xl"):
                  spinner_5 = ui.spinner(type="dots",size="md").classes(add="inline ml-1")
                  disp_balance_label_2 = ui.label().classes(add="inline ml-1 bg-inherit text-sky-600 text-bold text-xl").bind_text_from(inventory_data,"dispensing_balance",backward=lambda balance:f"{balance:,.0f}")
              
              #Inputs
              with html.div().classes(add="w-full p-2 flex flex-row justify-center gap-3 p-0.5"):
                ui.number(label="MAIN STORE").props(add="stack-label").classes(add="w-40 rounded shadow-md shadow-[#07004d] px-5 bg-sky-50 text-lg").bind_value(inventory_data,"main_count")
                ui.number(label="DISPENSING STORE").props(add="stack-label").classes(add="w-40 rounded shadow-md shadow-[#07004d] px-5 bg-sky-50 text-lg").bind_value(inventory_data,"dispensing_count")
                ui.button(text="update count",color="",on_click=lambda e:self.update_inventory(inventory_data,count=True)).props(add="glossy").classes(add="bg-harmony text-yellow-500 text-bold text-xl")

        #Cosmetics
        for label in [main_balance_label,disp_balance_label,last_count_label,main_balance_label_2,disp_balance_label_2]:
          label.visible = False
      
        ui.timer(5,update_inventory_data,once=True)
      
      #For ordered medicine
      elif ordered:
        #Header
        with html.header().classes(add="bg-harmony w-full grid grid-cols-11 items-center"):
          #Title
          ui.label(medicine["name"]).classes(add="col-span-10 w-full p-1 rounded-t text-2xl lg:text-3xl text-bold text-center text-sky-300 uppercase")
          ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=self.medicine_dialog.close).classes(add="bg-inherit text-red-600 text-xl justify-self-end")
        
        #Body
        with html.div().classes(add="grow w-full p-2 flex flex-col gap-5"):
          #Dates
          with ui.input(label="EXPIRY DATE").props(add="id='readonly").classes(add="w-full rounded shadow-md shadow-[#07004d] px-3 bg-white text-lg lg:text-xl") as exp_date_display:
            with ui.dialog() as calendar:
              ui.date(mask='YYYY-MM-DD',on_change=calendar.close).props(add=f"bordered square today-btn color='harmony' event-color='orange' first-day-of-week='1' navigation-min-year-month='{datetime.now().strftime("%Y/%m")}'").bind_value(exp_date_display).bind_value(medicine,"expire_date")
              with exp_date_display.add_slot("prepend"):
                ui.icon("fas fa-cake-candles",color="").classes(add="text-harmony").on("click",calendar.open)
                
          #Quantity
          with html.section().classes(add="w-full p-2 grid grid-cols-2  gap-3"):
            ui.number(label="RECEIVED QTY",placeholder=f"Ordered: {medicine['ordered_amount']:,.0f}").bind_value(medicine,"received_amount").classes(add="w-full shadow-md shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl")
            ui.number(label="RECEIVED COST",placeholder=f"Ordered: {medicine['ordered_price']:,.0f}").bind_value(medicine,"received_price").classes(add="w-full shadow-md shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl")
            ui.number(label="REJECTED QTY",placeholder=f"Ordered: {medicine['ordered_amount']:,.0f}").bind_value(medicine,"rejected_amount").classes(add="w-full shadow-md shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl")
            ui.number(label="REJECTED COST",placeholder=f"Ordered: {medicine['ordered_price']:,.0f}").bind_value(medicine,"rejected_price").classes(add="w-full shadow-md shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl")
          
          #Space
          ui.space()

          #Button
          with html.div().classes(add="w-full py-2 flex flex-row justify-center"):
            ui.button(text="PROCESS MEDICINE",color="",on_click=lambda e:self.receive_medicine(data=medicine)).classes(add="bg-harmony text-sky-300 text-bold text-lg")
      
      #For new order
      elif new:
        #Header
        with html.header().classes(add="bg-harmony w-full grid grid-cols-11 items-center"):
          #Title
          ui.label(medicine["name"]).classes(add="col-span-10 w-full p-1 rounded-t text-2xl lg:text-3xl text-bold text-center text-sky-300 uppercase")
          ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=self.medicine_dialog.close).classes(add="bg-inherit text-red-600 text-xl justify-self-end")
        
        #Seprator
        ui.separator().classes(add="w-full bg-[#09026f]")

        #Displays
        with html.div().classes(add="w-full py-2 bg-harmony grid grid-cols-6 text-bold"):
          #UOM
          with ui.label("UOM: ").classes(add="w-full text-sky-400 text-center"):
            ui.label().classes(add="inline ml-1 text-sky-50 uppercase").bind_text_from(medicine,"order_unit_size",backward=lambda val:f"{int(val)}{uom(medicine_name=medicine['name'],compact=True)}" if val else None).bind_text(medicine,"order_unit")
          
          #Units display
          with ui.label("UNITS: ").classes(add="col-span-2 w-full text-sky-400 text-center"):
            ui.label().classes(add="inline ml-1 text-sky-50").bind_text_from(medicine,"ordered_amount",backward=lambda val:f"{calculate_units(val):,.0f}")
          
          #Total price
          with ui.label("PRICE: ").classes(add="col-span-3 w-full text-sky-400 text-center"):
            ui.label().classes(add="inline ml-1 text-sky-50 uppercase").bind_text_from(medicine,"unit_price",backward=lambda val:f"{calculate_price(val):,.2f} TZS")

        #Body
        with html.div().classes(add="w-full p-2 pt-3 grid grid-cols-3 gap-5"):
          #Order unit size
          ui.number(label=f"{uom(medicine['name'])}s/UNIT".upper(),min=1).props(add="stack-label").classes(add="w-36 rounded shadow-md shadow-[#07004d] px-3 bg-sky-50 text-lg lg:text-xl uppercase").bind_value(medicine,"order_unit_size")
          
          #Order amount
          ui.number(label=f"{uom(medicine['name'])}s to order".upper(),min=1).props(add="stack-label").classes(add="w-36 rounded shadow-md shadow-[#07004d] px-3 bg-sky-50 text-lg lg:text-xl uppercase").bind_value(medicine,"ordered_amount")
          
          #Unit cost
          ui.number(label="UNIT PRICE(TZS)",min=0,on_change=lambda e:self.medicine_dialog.update()).props(add="stack-label").bind_value(medicine,"unit_price").bind_value_to(medicine,"ordered_price",forward=lambda val:calculate_price(val)).classes(add="w-32 rounded shadow-md shadow-[#07004d] px-3 bg-sky-50 text-lg lg:text-xl uppercase")
          
          #Space
          with html.div().classes(add="w-full col-span-3"):
            ui.space()

          #Buttons
          ui.button(text="order medicine",color="",on_click=lambda e:self.order_medicine(medicine)).props(add="glossy").classes(add="col-span-3 justify-self-center bg-harmony text-sky-300 text-bold text-lg")



      
    self.medicine_dialog.open()
  
          

class StockAnalysisDisplay():
  """A class for UI and functionalities of stock analysis"""

  def __init__(self,requisitions=None):
    self.requisitions = requisitions

    #UI
    with html.div().classes(add="grow w-full flex flex-col"):
      #Separator
      for i in range(2):
        ui.separator().classes(add="w-full bg-[#09026f]")
      #Header
      with html.section().classes(add="w-full p-1 flex flex-row bg-harmony text-yellow-500"):
        with html.div().classes(add="rounded-t-md grow bg-inherit flex flex-row content-center"):
          ui.label("STOCK STATUS").classes(add="w-full rounded-t text-3xl text-bold")
      
      with html.div().classes(add="grow w-full p-1 flex flex-col justify-center content-center") as self.stocks_panel:
        if self.requisitions:
          self.StocksPanel()
        else:
          ui.label("No received requisition!").classes(add="m-5 text-rose-500 text-2xl lg:text-3xl italic font-semibold fa-fade")
  
  #FUNCTIONALITES
  def amc(self,medicine:dict):
    """A method that calculates average monthly consumption of medicine"""

    initial_amount,final_amount = medicine["initial_store_balance"],medicine["store_balance"] + medicine["dispensing_balance"]
    duration = (datetime.now().date() - medicine["received_on"].date()).days/30
    
    return math.ceil((initial_amount-final_amount)/duration) if duration else 0
  
  def dos(self,medicine:dict):
    "A method to that returns a calculated number of days of stock based on data from medicine input"

    final_amount = medicine["store_balance"] + medicine["dispensing_balance"]
    amc = self.amc(medicine)
    
    if medicine["initial_store_balance"]:
      if amc:
        return round((final_amount/amc)*30)
      else:
        return 150
    else:
      return 0

  def mos(self,medicine:dict):
    """A method that returns value of mos based on the input values"""
    final_amount = medicine["store_balance"] + medicine["dispensing_balance"]
    amc = self.amc(medicine)
    
    if medicine["initial_store_balance"]:
      if amc:
        return round(final_amount/amc)
      else:
        return 2
    else:
      return 0
  
  def stock(self):
    """A method that returns a dictionary with stock details"""
    medicines = self.requisition["medicines"]
    
    no_demand,overstocks,understocks,stockouts,stocked = [],[],[],[],[]

    for medicine in medicines:
      amc = self.amc(medicine=medicine)
      mos = self.mos(medicine=medicine)
      dos = self.dos(medicine=medicine)

      if amc > 0:
        overstocks.append(medicine) if mos > 4 else understocks.append(medicine) if ((mos > 0 and mos < 2) or (mos == 0 and dos > 0)) else stockouts.append(medicine) if mos == 0 else stocked.append(medicine)
      else:
        no_demand.append(medicine)
      
    return {"no_demand":no_demand,"overstocks":overstocks,"stocked":stocked,"understocks":understocks,"stockouts":stockouts}

  #DISPLAYS
  def StocksPanel(self):
    """A Main display"""
    #DATA
    stocks = self.stock()
    stockouts,understocks,stocked,overstocks,no_demand = stocks["stockouts"],stocks["understocks"],stocks["stocked"],stocks["overstocks"],stocks["no_demand"]
    #UI
    self.stocks_panel.clear()
    with self.stocks_panel:
      with html.div().classes(add="grow w-full lg:p-1 flex flex-row lg:flex-col justify-between gap-1 lg:gap-3"):
        #Adequate
        with ui.button(color="green-600",on_click=lambda e:self.StocksDialog(stocked=stocked)).props(add="dense glossy padding='2px 2px'").classes(add="w-full lg:w-auto rounded") as stocked_button:
          with stocked_button.add_slot("default"):
            with html.span().classes(add="w-full flex flex-row justify-between gap-5 bg-gray-900 rounded p-2"):
              ui.label("ADEQUATE STOCKS").classes(add="bg-inherit text-green-600 font-medium text-xl lg:text-2xl")
              ui.badge(text=str(len(stocked)),color="").classes(add="bg-inherit flex flex-col justify-center size-8 rounded-full ring-1 ring-green-600 shadow-md shadow-green-600 text-green-600 text-2xl text-bold")
        #Stockouts
        with ui.button(color="red-500",on_click=lambda e:self.StocksDialog(stockouts=stockouts)).props(add="dense glossy padding='2px 2px'").classes(add="w-[49%] lg:w-auto inline rounded") as stockouts_button:
          with stockouts_button.add_slot("default"):
            with html.span().classes(add="w-full flex flex-row justify-between gap-5 bg-gray-900 rounded p-2"):
              ui.label("STOCKOUTS").classes(add="bg-inherit text-red-500 font-medium text-xl lg:text-2xl")
              ui.badge(text=str(len(stockouts)),color="").classes(add=f"bg-inherit flex flex-col justify-center size-8 rounded-full ring-1 ring-red-500 shadow-md shadow-red-500 text-red-500 text-xl lg:text-2xl text-bold {'fa-beat-fade' if stockouts else ''}")
        #Understocks
        with ui.button(color="yellow-400",on_click=lambda e:self.StocksDialog(understocks=understocks)).props(add="dense glossy padding='2px 2px'").classes(add="w-[49%] lg:w-auto inline rounded") as understocks_button:
          with understocks_button.add_slot("default"):
            with html.span().classes(add="w-full flex flex-row justify-between gap-5 bg-gray-900 rounded p-2"):
              ui.label("UNDERSTOCKS").classes(add="bg-inherit text-yellow-400 font-medium text-xl lg:text-2xl")
              ui.badge(text=str(len(understocks)),color="").classes(add=f"bg-inherit flex flex-col justify-center size-8 rounded-full ring-1 ring-yellow-400 shadow-md shadow-yellow-400 text-yellow-400 text-xl lg:text-2xl text-bold {'fa-beat-fade' if understocks else ''}")
        #Overstocks
        with ui.button(color="purple-500",on_click=lambda e:self.StocksDialog(overstocks=overstocks)).props(add="dense glossy padding='2px 2px'").classes(add="w-[49%] lg:w-auto rounded") as overstocks_button:
          with overstocks_button.add_slot("default"):
            with html.span().classes(add="w-full flex flex-row justify-between gap-5 bg-gray-900 rounded p-2"):
              ui.label("OVERSTOCKS").classes(add="bg-inherit text-purple-500 font-medium text-xl lg:text-2xl")
              ui.badge(text=str(len(overstocks)),color="").classes(add=f"bg-inherit flex flex-col justify-center size-8 rounded-full ring-1 ring-purple-500 shadow-md shadow-purple-500 text-purple-500 text-xl text-bold {'fa-beat-fade' if overstocks else ''}")
        #No Demand
        with ui.button(color="gray-400",on_click=lambda e:self.StocksDialog(no_demand=no_demand)).props(add="dense glossy padding='2px 2px'").classes(add="w-[49%] lg:w-auto rounded") as no_demand_button:
          with no_demand_button.add_slot("default"):
            with html.span().classes(add="w-full flex flex-row justify-between gap-5 bg-gray-900 rounded p-2"):
              ui.label("NO DEMAND").classes(add="bg-inherit text-gray-400 font-medium text-xl lg:text-2xl")
              ui.badge(text=str(len(no_demand)),color="").classes(add=f"bg-inherit flex flex-col justify-center size-8 rounded-full ring-1 ring-gray-500 shadow-md shadow-gray-500 text-gray-400 text-xl text-bold {'fa-beat-fade' if no_demand else ''}")
           
  def StocksDialog(self,no_demand=None,overstocks=None,stocked=None,understocks=None,stockouts=None):
    #DATA
    if no_demand or overstocks or stocked or understocks or stockouts:
      requisition = self.requisition
      medicines = no_demand if no_demand else stockouts if stockouts else understocks if understocks else stocked if stocked else overstocks if overstocks else []
    else:
      ui.notify(message=f"No {'undemanded items' if type(no_demand) is list else 'stockouts' if type(stockouts) is list else 'understocks' if type(understocks) is list else 'adequately stocked items' if type(stocked) is list else 'overstocks' if type(overstocks) is list else ''}!",type="info",position="top",color=f"{'red-600' if type(stockouts) is list else 'yellow-500' if type(understocks) is list else 'green-500' if type(stocked) is list else 'violet-500' if type(overstocks) is list else ''}")
      return
    
    #UI
    with ui.dialog().props(add="transition-show='jump-up' transition-hide='jump-down' transition-duration='500'") as self.stocks_dialog,html.div().style(add="min-width:100%;max-height:95%;").classes(add="bg-sky-100 p-0.5 flex flex-col"):
      #Dialog Header
      with html.div().classes(add="w-full flex flex-row place-center bg-harmony"):
        #Details
        with html.div().classes(add="grow bg-inherit flex-col flex lg:flex-row justify-between content-center lg:items-center pl-3"):
          #Title
          ui.label("NO DEMAND" if type(no_demand) is list else "OVERSTOCKS" if type(overstocks) is list else "ADEQUATELY STOCKED" if type(stocked) is list else "UNDERSTOCKS" if type(understocks) is list else "STOCKOUTS" if type(stockouts) is list else "").classes(add=f"text-{'red-600' if type(stockouts) == list else 'yellow-400' if type(understocks) is list else 'green-500' if type(stocked) == list else 'purple-600' if type(overstocks) == list else 'gray-300' if type(no_demand) == list else ''} text-2xl lg:text-3xl text-bold")
          #Requisition ID
          with ui.label("REQUISITION ID:").classes(add="w-full lg:w-auto font-medium text-sky-300 text-lg"):
            ui.label(requisition["requisition_id"]).classes(add="inline ml-0.5 text-yellow-500 text-bold uppercase")
          #Stock count
          with ui.label(f"ITEMS").classes(add="w-full lg:w-auto text-bold text-sky-300 text-lg"):
            ui.label(str(len(medicines))).classes(add="inline ml-1 text-yellow-500 uppercase")
        #Close button
        with html.div().classes(add="flex flex-col justify-center"):
          ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=self.stocks_dialog.close).classes(add="size-12 bg-inherit rounded-full text-red-600 text-bold text-base hover:scale-[1.1]")
      
      #Stocks Display
      with html.div().classes(add="grow w-full animate__animated animate__fadeIn animate__slow"):
        with html.div().classes(add="grow lg:hidden flex flex-col"):
          self.StockMedicinesMiniDisplay(no_demand=no_demand,overstocks=overstocks,stocked=stocked,understocks=understocks,stockouts=stockouts)
        with html.div().classes(add="grow lg-flex flex-col"):
          self.StocksAggrid(no_demand=no_demand,overstocks=overstocks,stocked=stocked,understocks=understocks,stockouts=stockouts)
    
    self.stocks_dialog.open()
  
  def StocksAggrid(self,stockouts=None,understocks=None,stocked=None,overstocks=None,no_demand=None):
    """"""
    #DATA
    medicines = stockouts if stockouts else understocks if understocks else stocked if stocked else overstocks if overstocks else no_demand if no_demand else []
    
    #UI
    if stockouts:
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/No","field":"sno","width":70},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
            {"headerName":"TYPE","field":"type","width":150},
            {"headerName":"UNIT","field":"unit","width":150},
            {"headerName":"BRAND NAME","field":"brand_name"},
            {"headerName":"MANUFACTURER","field":"manufacturer"},
            {"headerName":"AMC","field":"amc","width":150},
          ],
          "rowData":[
            {
              "sno":medicines.index(medicine) + 1,
              "name":medicine["name"],
              "type":medicine["type"],
              "unit":medicine["order_unit"],
              "brand_name":medicine["brand_name"] if medicine["brand_name"] else "---",
              "manufacturer":medicine["manufacturer"] if medicine["manufacturer"] else "---",
              "amc":f"{self.amc(medicine):,.0f}",
            }
            for medicine in medicines
          ]
        },theme="quartz"
        ).classes(add="w-full grow bg-sky-300 text-sm uppercase")
    
    elif understocks:
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/No","field":"sno","width":100},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
            {"headerName":"TYPE","field":"type","width":150},
            {"headerName":"UNIT","field":"unit","width":150},
            {"headerName":"BRAND NAME","field":"brand_name"},
            {"headerName":"MANUFACTURER","field":"manufacturer"},
            {"headerName":"BATCH NO","field":"batch_no"},
            {"headerName":"EXPIRY DATE","field":"expire_date","width":200},
            {"headerName":"AMC","field":"amc"},
            {"headerName":"MOS","field":"mos"},
            {"headerName":"STOCK DAYS","field":"dos"}
          ],
          "rowData":[
            {
              "sno":medicines.index(medicine) + 1,
              "name":medicine["name"],
              "type":medicine["type"],
              "unit":medicine["order_unit"],
              "brand_name":medicine["brand_name"] if medicine["brand_name"] else "---",
              "manufacturer":medicine["manufacturer"] if medicine["manufacturer"] else "---",
              "batch_no":medicine["batch_no"] if medicine["batch_no"] else "---",
              "expire_date":medicine["expire_date"].strftime("%b %Y") if medicine["expire_date"] else "---",
              "amc":f"{self.amc(medicine):,.0f}",
              "mos":f"{self.mos(medicine):,.0f}",
              "dos":self.dos(medicine)
            }
            for medicine in medicines
          ]
        },theme="quartz"
        ).style(add="height:350px").classes(add="grow w-full bg-sky-300 text-sm uppercase")
      
    elif stocked:
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/N","field":"sno","width":80},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
            {"headerName":"TYPE","field":"type","width":150},
            {"headerName":"UNIT","field":"unit","width":150},
            {"headerName":"BRAND NAME","field":"brand_name"},
            {"headerName":"MANUFACTURER","field":"manufacturer"},
            {"headerName":"BATCH NO","field":"batch_no"},
            {"headerName":"EXPIRY DATE","field":"expire_date","width":200},
            {"headerName":"AMC","field":"amc"},
            {"headerName":"MOS","field":"mos"},
            {"headerName":"STOCK DAYS","field":"dos"}
          ],
          "rowData":[
            {
              "sno":medicines.index(medicine) + 1,
              "name":medicine["name"],
              "type":medicine["type"],
              "unit":medicine["order_unit"],
              "brand_name":medicine["brand_name"] if medicine["brand_name"] else "---",
              "manufacturer":medicine["manufacturer"] if medicine["manufacturer"] else "---",
              "batch_no":medicine["batch_no"] if medicine["batch_no"] else "---",
              "expire_date":medicine["expire_date"].strftime("%b %Y") if medicine["expire_date"] else "---",
              "amc":f"{self.amc(medicine):,.0f}",
              "mos":f"{self.mos(medicine):,.0f}",
              "dos":f"{self.dos(medicine):,.0f}"
            }
            for medicine in medicines
          ]
        },theme="quartz"
        ).style(add="height:350px").classes(add="grow w-full bg-sky-300 text-sm uppercase")

    elif overstocks:
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/No","field":"sno","width":100},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
            {"headerName":"TYPE","field":"type","width":150},
            {"headerName":"UNIT","field":"unit","width":150},
            {"headerName":"BRAND NAME","field":"brand_name"},
            {"headerName":"MANUFACTURER","field":"manufacturer"},
            {"headerName":"BATCH NO","field":"batch_no"},
            {"headerName":"EXPIRY DATE","field":"expire_date","width":200},
            {"headerName":"AMC","field":"amc"},
            {"headerName":"MOS","field":"mos"}
          ],
          "rowData":[
            {
              "sno":medicines.index(medicine) + 1,
              "name":medicine["name"],
              "type":medicine["type"],
              "unit":medicine["order_unit"],
              "brand_name":medicine["brand_name"] if medicine["brand_name"] else "---",
              "manufacturer":medicine["manufacturer"] if medicine["manufacturer"] else "---",
              "batch_no":medicine["batch_no"] if medicine["batch_no"] else "---",
              "expire_date":medicine["expire_date"].strftime("%b %Y") if medicine["expire_date"] else "---",
              "amc":f"{self.amc(medicine):,.0f}",
              "mos":f"{self.mos(medicine):,.0f}"
            }
            for medicine in medicines
          ]
        },theme="quartz"
        ).style(add="height:350px").classes(add="grow w-full bg-sky-300 text-sm uppercase")
    
    elif no_demand:
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/No","field":"sno","width":100},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
            {"headerName":"TYPE","field":"type","width":150},
            {"headerName":"UNIT","field":"unit","width":150},
            {"headerName":"BRAND NAME","field":"brand_name"},
            {"headerName":"MANUFACTURER","field":"manufacturer"},
            {"headerName":"BATCH NO","field":"batch_no"},
            {"headerName":"EXPIRY DATE","field":"expire_date","width":200},
            {"headerName":"MOS","field":"mos"}
          ],
          "rowData":[
            {
              "sno":medicines.index(medicine) + 1,
              "name":medicine["name"],
              "type":medicine["type"],
              "unit":medicine["order_unit"],
              "brand_name":medicine["brand_name"] if medicine["brand_name"] else "---",
              "manufacturer":medicine["manufacturer"] if medicine["manufacturer"] else "---",
              "batch_no":medicine["batch_no"] if medicine["batch_no"] else "---",
              "expire_date":medicine["expire_date"].strftime("%b %Y") if medicine["expire_date"] else "---",
              "mos":f"{self.mos(medicine):,.0f}"
            }
            for medicine in medicines
          ]
        },theme="quartz"
        ).style(add="height:350px").classes(add="grow w-full bg-sky-300 text-sm uppercase")

  def StockMedicinesMiniDisplay(self,no_demand=None,overstocks=None,stocked=None,understocks=None,stockouts=None):

    #DATA
    medicines = stockouts if stockouts else understocks if understocks else stocked if stocked else overstocks if overstocks else no_demand if no_demand else []

    #UI
    with ui.scroll_area().classes(add="lg:hidden grow w-full rounded shadow-md shadow-[#07004d] py-3"):
      if no_demand:
        for medicine in medicines:
          with ui.button(color="").props(add=f"elevated id={medicine['requisition_medicine_id']}").classes(add=f"w-full h-fit p-1 bg-sky-100 shadow-md shadow-[#07004d] flex flex-row"):
            #Index
            ui.label(str(medicines.index(medicine) + 1)).classes(add="size-8 rounded-full ring-1 ring-offset-1 ring-[#07004d] bg-harmony flex flex-col justify-center text-sky-300 text-lg font-semibold")
            #Details
            with html.div().classes(add="grow ml-1 h-full flex flex-col gap-1"):
              #Identity
              with html.section().classes(add="w-full px-1 flex flex-col md:flex-row justify-between font-semibold"):
                ui.label(medicine['name']).classes(add="text-start text-lg")
              
              #Stock details
              with html.section().classes(add="w-full px-1 flex flex-row justify-between gap-3 font-semibold"):
                ui.label(medicine['type']).classes(add="text-start md:text-end italic text-gray-700")
                with ui.label("MOS").classes(add="text-gray-700"):
                  ui.label(f"{self.mos(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")

              #Stats
              with html.div().classes(add="w-full px-1 flex flex-row justify-between font-semibold"):
                with ui.label("MAIN STORE").classes(add="text-gray-700"):
                  ui.label(f"{medicine['store_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("DISPENSING STORE").classes(add="text-gray-700"):
                  ui.label(f"{medicine['dispensing_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")

      if overstocks:
        for medicine in medicines:
          with ui.button(color="").props(add=f"elevated id={medicine['requisition_medicine_id']}").classes(add=f"w-full h-fit p-1 bg-sky-100 shadow-md shadow-[#07004d] flex flex-row"):
            #Index
            ui.label(str(medicines.index(medicine) + 1)).classes(add="size-8 rounded-full ring-1 ring-offset-1 ring-[#07004d] bg-harmony flex flex-col justify-center text-sky-300 text-lg font-semibold")
            #Details
            with html.div().classes(add="grow ml-1 h-full flex flex-col gap-1"):
              #Identity
              with html.section().classes(add="w-full px-1 flex flex-col md:flex-row justify-between font-semibold"):
                ui.label(medicine['name']).classes(add="text-start text-lg")
              
              #Stock details
              with html.section().classes(add="w-full px-1 flex flex-row justify-between gap-3 font-semibold"):
                ui.label(medicine['type']).classes(add="text-start md:text-end italic text-gray-700")
                with ui.label("AMC").classes(add="text-gray-700"):
                  ui.label(f"{self.amc(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("MOS").classes(add="text-gray-700"):
                  ui.label(f"{self.mos(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")

              #Stats
              with html.div().classes(add="w-full px-1 flex flex-row justify-between font-semibold"):
                with ui.label("MAIN STORE").classes(add="text-gray-700"):
                  ui.label(f"{medicine['store_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("DISPENSING STORE").classes(add="text-gray-700"):
                  ui.label(f"{medicine['dispensing_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")

      if stocked:
        for medicine in medicines:
          with ui.button(color="").props(add=f"elevated id={medicine['requisition_medicine_id']}").classes(add=f"w-full h-fit p-1 bg-sky-100 shadow-md shadow-[#07004d] flex flex-row"):
            #Index
            ui.label(str(medicines.index(medicine) + 1)).classes(add="size-8 rounded-full ring-1 ring-offset-1 ring-[#07004d] bg-harmony flex flex-col justify-center text-sky-300 text-lg font-semibold")
            #Details
            with html.div().classes(add="grow ml-1 h-full flex flex-col gap-1"):
              #Identity
              with html.section().classes(add="w-full px-1 flex flex-col md:flex-row justify-between font-semibold"):
                ui.label(medicine['name']).classes(add="text-start text-lg")
              
              #Stock details
              with html.section().classes(add="w-full px-1 flex flex-row justify-between gap-3 font-semibold"):
                ui.label(medicine['type']).classes(add="text-start md:text-end italic text-gray-700")
                with ui.label("AMC").classes(add="text-gray-700"):
                  ui.label(f"{self.amc(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("MOS").classes(add="text-gray-700"):
                  ui.label(f"{self.mos(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")

              #Stats
              with html.div().classes(add="w-full px-1 flex flex-row justify-between font-semibold"):
                with ui.label("MAIN STORE").classes(add="text-gray-700"):
                  ui.label(f"{medicine['store_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("DISPENSING STORE").classes(add="text-gray-700"):
                  ui.label(f"{medicine['dispensing_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")

      if understocks:
        for medicine in medicines:
          with ui.button(color="").props(add=f"elevated id={medicine['requisition_medicine_id']}").classes(add=f"w-full h-fit p-1 bg-sky-100 shadow-md shadow-[#07004d] flex flex-row"):
            #Index
            ui.label(str(medicines.index(medicine) + 1)).classes(add="size-8 rounded-full ring-1 ring-offset-1 ring-[#07004d] bg-harmony flex flex-col justify-center text-sky-300 text-lg font-semibold")
            #Details
            with html.div().classes(add="grow ml-1 h-full flex flex-col gap-1"):
              #Identity
              with html.section().classes(add="w-full px-1 flex flex-col md:flex-row justify-between font-semibold"):
                ui.label(medicine['name']).classes(add="text-start text-lg")
              
              #Stock details
              with html.section().classes(add="w-full px-1 flex flex-row justify-between gap-3 font-semibold"):
                ui.label(medicine['type']).classes(add="text-start md:text-end italic text-gray-700")
                with ui.label("AMC").classes(add="text-gray-700"):
                  ui.label(f"{self.amc(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("MOS").classes(add="text-gray-700"):
                  ui.label(f"{self.mos(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("DOS").classes(add="text-gray-700"):
                  ui.label(f"{self.dos(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")

              #Stats
              with html.div().classes(add="w-full px-1 flex flex-row justify-between font-semibold"):
                with ui.label("MAIN STORE").classes(add="text-gray-700"):
                  ui.label(f"{medicine['store_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("DISPENSING STORE").classes(add="text-gray-700"):
                  ui.label(f"{medicine['dispensing_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")

      if stockouts:
        for medicine in medicines:
          with ui.button(color="").props(add=f"elevated id={medicine['requisition_medicine_id']}").classes(add=f"w-full h-fit p-1 bg-sky-100 shadow-md shadow-[#07004d] flex flex-row"):
            #Index
            ui.label(str(medicines.index(medicine) + 1)).classes(add="size-8 rounded-full ring-1 ring-offset-1 ring-[#07004d] bg-harmony flex flex-col justify-center text-sky-300 text-lg font-semibold")
            #Details
            with html.div().classes(add="grow ml-1 h-full flex flex-col gap-1"):
              #Identity
              with html.section().classes(add="w-full px-1 flex flex-col md:flex-row justify-between font-semibold"):
                ui.label(medicine['name']).classes(add="text-start text-lg")
              
              #Stock details
              with html.section().classes(add="w-full px-1 flex flex-row justify-between gap-3 font-semibold"):
                ui.label(medicine['type']).classes(add="text-start md:text-end italic text-gray-700")
                with ui.label("AMC").classes(add="text-gray-700"):
                  ui.label(f"{self.amc(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("MOS").classes(add="text-gray-700"):
                  ui.label(f"{self.mos(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("DOS").classes(add="text-gray-700"):
                  ui.label(f"{self.dos(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")

              #Stats
              with html.div().classes(add="w-full px-1 flex flex-row justify-between font-semibold"):
                with ui.label("MAIN STORE").classes(add="text-gray-700"):
                  ui.label(f"{medicine['store_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("DISPENSING STORE").classes(add="text-gray-700"):
                  ui.label(f"{medicine['dispensing_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")

class FacilityFormulary():
  def __init__(self,user):
    #DATA
    self.user = user
    self.initial_data()

    #UI
    with html.div().classes(add="grow w-full flex flex-col"):
      #Separator
      for i in range(2):
        ui.separator().classes(add="lg-show w-full bg-[#09026f]")
      #Header
      with html.section().classes(add="w-full p-1 lg:rounded-0 flex flex-row bg-harmony text-yellow-500"):
        with html.div().classes(add="rounded-t-md grow bg-inherit flex flex-row content-center gap-5 lg:gap-1"):
          ui.label("FORMULARY").classes(add="lg:order-2 grow rounded-t text-2xl lg:text-3xl text-bold")
          ui.button(icon="fa-solid fa-circle-plus",color="",on_click=self.MedicineDialog).classes(add="lg:order-1 size-8 rounded-[50%] bg-inherit text-yellow-500")

      #Body
      with html.div().classes(add="grow w-full flex flex-col justify-center content-center") as self.formulary_panel:
        if self.medicines:
          self.FormularyAggrid()
          
        else:
          with html.div().classes(add=""):
            ui.label("There is no hospital formulary!").classes(add="m-5 text-rose-500 text-center text-2xl lg:text-3xl italic font-semibold fa-fade")
            ui.label("Create a formulary by clicking a + button").classes(add="text-center text-rose-400 text-xl lg:text-2xl")

  #FUNCTIONALITIES
  def initial_data(self):
    self.medicines = [self.format_formulary_medicine(medicine) for medicine in get_formulary()]
    self.template_medicines = get_formulary_medicines()

    self.medicine = {}

  def format_formulary_medicine(self,formulary_medicine):
    _new_medicine = formulary_medicine._asdict()
    _new_medicine["schemes"] = [scheme._asdict() for scheme in _new_medicine["schemes"]]
    for scheme in _new_medicine["schemes"]:
      scheme["prices"] = [pricing._asdict() for pricing in scheme["prices"]]
    
    return _new_medicine

  def retrieve_medicine(self,medicine:str):
    """A method that retrieves service details and populate details in ServiceDetailsForm"""
    if not medicine:
      return
    
    medicine = get_formulary_medicine(medicine.lower())

    if medicine["medicine_id"] in [medicine["medicine_id"] for medicine in self.medicines]:
      ui.notify(message="Medicine already in the formulary!",position="top",type="warning")
      return
    
    #Formatting medicine
    medicine["active"] = True
    
    self.new_medicine_panel.clear()
    with self.new_medicine_panel.classes(remove="justify-center items-center gap-5",add="gap-1"):
      self.MedicineDetailsForm(medicine=medicine,new=True)

  async def retrieve_payment_scheme(self,scheme:str,medicine):
    if not scheme:
      return
    
    scheme = await admin_processor.retrieve_payment_scheme(name=scheme.lower(),medicine=medicine)

    if not scheme:
      ui.notify(message=f"No details found for {scheme.upper()}",position="top",type="warning")
    else:
      self.NewPaymentSchemePanel(medicine=medicine,scheme=scheme)
  
  def register_payment_scheme_and_pricing(self,scheme,medicine):
    scheme["prices"] = [scheme["prices"]]

    status = admin_db.register_scheme(scheme=scheme,default=True)

    ui.notify(message=status["message"],type=status["type"],position=status["position"])

    if "schemes" in medicine:
      medicine["schemes"].append(scheme)
    else:
      medicine["schemes"] = [scheme]
    
    self.initial_data()
    self.PaymentSchemes(medicine["schemes"])

  def update_pricing(self,pricing):
    """updates the database if they arent similar"""
    
    #Scheme
    scheme = {"scheme_id":pricing["scheme_id"],"active":pricing["active"],"restricted":pricing["restricted"]}

    #Pricing
    pricing.pop("active")
    pricing.pop("restricted")

    if not pricing["price_range"]:
      pricing["min"],pricing["max"] = 0.0,0.0

    if not pricing["copayment"]:
      pricing["topup"] = 0.0
    
    #Updating database
    pricing_status = admin_db.register_pricing(pricing)
    scheme_status = admin_db.update_scheme(scheme)

    if pricing_status["status"]:
      ui.notify(message=pricing_status["message"],position=pricing_status["position"],type=pricing_status["type"])
    else:
      ui.notify(message=scheme_status["message"],position=scheme_status["position"],type=scheme_status["type"])

  async def update_formulary(self,raw_data,edit:bool=False,delete:bool=False):
    """"""

    data = {key:value.lower() for key,value in raw_data.items() if type(value) == str}
    data["active"] = raw_data["active"]

    if edit:
      status = update_formulary(medicine=data)
    elif delete:
      status = update_formulary(medicine=data,delete=True)
    else:
      status = register_formulary([data])
      await self.retrieve_payment_scheme(scheme="cash",medicine=data)
      

    ui.notify(message=status["message"],type=status["type"],position=status["position"])
    
    self.initial_data()
    
    if edit or delete:
      self.FormularyAggrid()
      self.medicine_dialog.close()
    else:
      pass
    
  #DISPLAYS
  def FormularyAggrid(self):
    """"""
    #FXS
    def Status(medicine,lg:bool=False):
      _status = medicine["active"]
      status = ""
      if lg:
        if _status:
          status = "<span class='text-green-600 text-bold' >Active</span>"
        else:
          status = "<span class='text-red-600 text-bold' >Inactive</span>"
      else:
        if _status:
          status = "<span class='fa-solid fa-circle-dot text-green-600 text-bold' ></span>"
        else:
          status = "<span class='fa-solid fa-circle-dot text-red-600 text-bold' ></span>"
      
      return status
    
    def CashPrice(medicine):
      scheme = [scheme for scheme in medicine["schemes"] if scheme["scheme_name"] == "cash"][0]
      price = [price for price in scheme["prices"] if price["active"]][0]["standard"]

      return price
  
    def InsuranceSchemes(medicine):
      schemes = [scheme["scheme_name"] for scheme in medicine["schemes"] if scheme["active"] and scheme["scheme_name"] != "cash"]
      nhif = "<span class='text-yellow-800 text-lg'>NHIF</span>" if "nhif" in schemes else ""
      assemble = "<span class='text-teal-800'>Assemble</span>" if "assemble" in schemes else ""
      jubilee = "<span class='text-red-800 text-lg'>Jubilee</span>" if "jubilee" in schemes else ""
      strategis = "<span class='text-green-700 text-lg'>Strategis</span>" if "strategis" in schemes else ""
      britam = "<span class='text-sky-700 text-lg'>Britam</span>" if "britam" in schemes else ""

      return f"<span class='text-bold' >{nhif} {assemble} {jubilee} {strategis} {britam}</span>"

    #UI
    self.formulary_panel.clear()
    with self.formulary_panel.classes(add=""):
      #Small Screen
      ui.aggrid(
        options={
          "columnDefs":[
            {"headerName":"","field":"status","width":100},
            {"headerName":"NAME","field":"name","sortable":True,"filter":True,"floatingFilter":True,"width":500},
            {"headerName":"TYPE","field":"type","width":200},
            {"headerName":"CASH","field":"cash_price","width":200,"type":"rightAligned"}
          ],
          "rowData":[
            {
              "name":medicine["name"].upper(),
              "status":Status(medicine),
              "type":medicine["type"].title(),
              "cash_price":f"{CashPrice(medicine):,.2f}" if "schemes" in medicine else "---",
              "medicine_id":medicine["medicine_id"]
            } for medicine in self.medicines
          ]
        },
        theme="quartz",
        html_columns=[0,3]
      ).classes(add="lg:hidden grow w-full bg-inherit text-sm animate__animated animate__fadeIn").on("cellClicked",lambda e:self.MedicineDialog(medicine=[medicine for medicine in self.medicines if medicine['medicine_id'] == e.args['data']['medicine_id'].lower()][0]))

      #Large Screen
      ui.aggrid(
        options={
          "columnDefs":[
            {"headerName":"","field":"sno","width":75},
            {"headerName":"NAME","field":"name","sortable":True,"filter":True,"floatingFilter":True,"width":500},
            {"headerName":"TYPE","field":"type","width":150},
            {"headerName":"LEVEL","field":"prescription_level","width":100},
            {"headerName":"STATUS","field":"status","width":100},
            {"headerName":"CASH (TZS)","field":"cash_prices","width":150},
            {"headerName":"INSURANCE SCHEMES","field":"insurances","width":500}
          ],
          "rowData":[
            {
              "sno":self.medicines.index(medicine) + 1,
              "name":medicine["name"].upper(),
              "status":Status(medicine=medicine,lg=True),
              "type":medicine["type"].upper(),
              "prescription_level":medicine["prescription_level"].upper() if medicine["prescription_level"] else "-",
              "cash_price":f"{CashPrice(medicine):,.2f}" if "schemes" in medicine else "---",
              "insurances":InsuranceSchemes(medicine) if "schemes" in medicine else "---",
              "medicine_id":medicine["medicine_id"]
            } for medicine in self.medicines
          ]
        },
        theme="quartz",
        html_columns=[4,5,6]
      ).classes(add="lg-show grow w-full bg-inherit text-sm animate__animated animate__fadeIn").on("cellClicked",lambda e:self.MedicineDialog(medicine=[medicine for medicine in self.medicines if medicine['medicine_id'] == e.args['data']['medicine_id'].lower()][0]))

  def MedicineDialog(self,medicine:dict|None=None):
    """A method to display dialog for medicine editing"""
    #DATA
    self.medicine = medicine

    #FXS
    def close_dialog():
      self.medicine_dialog.close()
      self.FormularyAggrid()

    # UI
    with ui.dialog().props(add="transition-show='jump-up' transition-hide='jump-down' transition-duration='500'") as self.medicine_dialog,html.div().style(add="min-width:50%;min-height:80%;").classes(add="p-0.5 rounded bg-sky-100 flex flex-col"):
      #Header
      with html.div().classes(add="bg-harmony rounded-t p-1 grid grid-cols-11 items-center"):
        ui.label(medicine["name"] if medicine else "MEDICINE DETAILS").classes(add="col-span-10 bg-inherit grow text-sky-300 text-2xl lg:text-3xl text-bold uppercase")
        ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=self.medicine_dialog.close).classes(add="justify-self-end size-8 bg-inherit text-rose-500")
      
      #Body
      with html.div().classes(add="grow py-2 flex flex-col gap-5 items-center"):
        if medicine:
          self.MedicineDetailsForm(medicine=medicine,edit=True)
        else:
          ui.select(label="MEDICINE NAME",options=self.template_medicines,with_input=True,on_change=lambda e:self.retrieve_medicine(medicine=e.value)).props(add=f"input-class='px-2' popup-content-class='uppercase'").classes(add="px-1 bg-white shadow-md shadow-[#07004d] rounded text-lg")
          ui.separator().classes(add="w-full")
          with html.div().classes(add="w-full grow flex flex-row justify-center items-center") as self.new_medicine_panel:
            with html.div().classes(add="flex flex-col items-center gap-3 bg-red"):
              pass

    self.medicine_dialog.open()
  
  def MedicineDetailsForm(self,medicine:dict|None=None,new:bool=False,edit:bool=False):
    #DATA
    tab_sections = ["general","pricing"]
     
    if edit:
      data = medicine
      for key,value in data.items():
        if type(value) == str:
          data[key] = value.title()
    
    else:
      if medicine:
        data = medicine
      else:
        data = {
          "medicine_id":None,"name":None,"type":None,"drug_class":None,"active":True,
          "fda_pregnancy_category_1":None,"pregnancy_category_2":None,"fda_pregnancy_category_3":None,"prescription_level":None,
        }
    
    #FXS
    async def template_payment_schemes():
      scheme_names = await admin_processor.get_template_payment_schemes()
      if "schemes" in medicine:
        scheme_names = [name for name in scheme_names if name not in [i["scheme_name"] for i in medicine["schemes"]]]
      add_scheme_select.options = [name.upper() for name in scheme_names]
      add_scheme_select.update()

    #UI
    with html.form().classes(add="grow w-full flex flex-col gap-3"):
      #General Details
      ui.input(label="NAME").props(add="type='text'").props(add="readonly").classes(add=f"{ 'hidden' if medicine else '' } w-[90%] px-2 rounded bg-white shadow-sm shadow-[#07004d] text-lg uppercase").bind_value(data,"name")
      
      #Tabs
      with html.div().classes(add="w-full rounded-b shadow-sm shadow-[#07004d]"):
        #Separator
        for i in range(2):
          ui.separator().classes(add="w-full bg-[#09026f]")
        #Tabs
        with ui.tabs(value=tab_sections[0]).props(add="inline-label mobile-arrows outside-arrows spread active-class='text-sky-500'").classes(add="w-full rounded-b bg-harmony py-1 text-sky-200 font-bold") as medicine_tabs:
          for section in tab_sections:
            ui.tab(name=section).props(add="")
      
      #Panels
      with html.div().classes(add="grow w-full rounded-br flex flex-col"):
        with ui.tab_panels(tabs=medicine_tabs,value=tab_sections[0]).props(add="animated infinite transition-prev='jump-right' transition-next='jump-left' transition-duration='700'").classes(add="bg-inherit grow w-full grid grid-cols-1"):
          #Details
          with ui.tab_panel(name="general").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col justify-between gap-0.5"):
            #General
            with html.section().classes(add="w-full grid grid-cols-2 gap-3"):
              ui.input(label="TYPE").props(add="type='text'").props(add="readonly").classes(add="w-full px-2 rounded bg-white shadow-sm shadow-[#07004d] text-lg").bind_value(data,"type",backward=lambda val:val.title())
              ui.toggle(options={True:"active",False:"inactive"}).props(add="glossy spread size='lg' toggle-color='bg-inherit' toggle-text-color='sky-500' text-color='yellow-500'").classes(add="w-full bg-harmony font-semibold").bind_value(data,"active")
            
            #Other details
            with html.section().classes(add="grow w-full p-1 flex lg:grid grid-cols-2 flex-col justify-between gap-3"):
              #Pregnancy Category (1st Trimester)
              with html.div().classes(add="p-1 rounded bg-sky-50 shadow-sm shadow-[#07004d]"):
                ui.label("PREGNANCY CATEGORY (1ST TIMESTER))").props(add="inline").classes(add="font-medium")
                ui.radio(options=[None,"A","B","C","D","X"]).props(add="inline left-label").classes(add="").bind_value(data,"fda_pregnancy_category_1")

              #Pregnancy Category (2nd Trimester)
              with html.div().classes(add="p-1 rounded bg-sky-50 shadow-sm shadow-[#07004d]"):
                ui.label("PREGNANCY CATEGORY (2ND TRIMESTER)").classes(add="font-medium")
                ui.radio(options=[None,"A","B","C","D","X"]).props(add="inline left-label").classes(add="").bind_value(data,"fda_pregnancy_category_2")
              
              #Pregnancy Category (3rd Trimester)
              with html.div().classes(add="p-1 rounded bg-sky-50 shadow-sm shadow-[#07004d]"):
                ui.label("PREGNANCY CATEGORY (3RD TRIMESTER)").classes(add="font-medium")
                ui.radio(options=[None,"A","B","C","D","X"]).props(add="inline left-label").classes(add="").bind_value(data,"fda_pregnancy_category_3")
              
              #Prescription Level
              with html.div().classes(add="p-1 rounded bg-sky-50 shadow-sm shadow-[#07004d]"):
                ui.label("PRESCRIPTION LEVEL").classes(add="font-medium")
                ui.radio(options=[None,"A","B","C","D","S"]).props(add="inline left-label").classes(add="").bind_value(data,"prescription_level")

            #Buttons
            with html.div().classes(add=f"w-full py-2 flex flex-row justify-center items-center gap-5"):
              ui.button(text="SAVE",color="",on_click=lambda e:self.update_formulary(raw_data=data,edit=edit)).props(add="glossy").classes(add=" bg-harmony text-yellow-500 text-bold text-xl")
              ui.button(text="DELETE",color="",on_click=lambda e:self.update_formulary(raw_data=data,delete=True)).props(add="glossy").classes(add=f"{'hidden' if new else ''} bg-harmony text-red-600 text-bold text-xl")
          
          #Payment Schemes
          with ui.tab_panel(name="pricing").classes(add="w-full h-full q-pa-none p-0 rounded-0 flex flex-col gap-2"):
            #Add new button
            with html.div().classes(add="w-full px-3 py-1 flex flex-row justify-center"):
              with ui.select(label="SELECT SCHEME",options=[],on_change=lambda e:self.retrieve_payment_scheme(scheme=e.value,medicine=self.medicine)).props(add=f"input-class='px-2' popup-content-class='uppercase'").classes(add="w-60 p-0 px-1 bg-white shadow-md shadow-[#07004d] rounded text-lg") as add_scheme_select:
                with add_scheme_select.add_slot("prepend"):
                  html.span().classes(add="fa-solid fa-circle-plus text-harmony")
                  
            #Payment scheme
            with html.div().classes(add="grow w-full bg-white flex flex-col") as self.payment_schemes_panel:
              self.PaymentSchemes(data["schemes"] if "schemes" in data else None)
  
    #ASYNCS
    ui.timer(0.1,lambda:template_payment_schemes(),once=True)
  
  def NewPaymentSchemePanel(self,scheme,medicine):
    """"""
    #DATA
    medicine = medicine
    scheme = scheme
    scheme["prices"]["logger"] = self.user.username

    #UI
    self.payment_schemes_panel.clear()
    with self.payment_schemes_panel:
      with html.div().classes(add="grow w-full flex flex-col gap-1 bg-sky-100 rounded shadow-sm shadow-[#07004d]"):
        #Header
        with html.section().classes(add="w-full p-1 rounded-t bg-harmony grid grid-cols-3 lg:grid-cols-2"):
          ui.label(scheme["scheme_name"].upper()).classes(add=" px-1 text-xl text-sky-300 text-bold")
          with html.div().classes(add="col-span-2 lg:col-span-1 flex flex-row justify-between items-center gap-1"):
            ui.switch(text="ACTIVE",value=scheme["active"]).props(add="dense left-label color='green' icon='fa-solid fa-power-off' size='lg'").classes(add="bg-inherit text-bold text-lg text-sky-200").bind_value(scheme,"active")
            ui.switch(text="RESTRICTED",value=scheme["restricted"]).props(add="dense left-label color='green' icon='fa-solid fa-power-off' size='lg'").classes(add="bg-inherit text-bold text-lg text-sky-200").bind_value(scheme,"restricted")
        #Prices
        with html.section().classes(add="w-full p-1 flex flex-col lg:grid grid-cols-6  gap-3"):
          #Cash pricing
          if scheme["scheme_name"].lower() == "cash":
            #Price Range Switch
            price_range_switch = ui.switch(text="PRICE RANGE").props(add="color='green' icon='fa-solid fa-power-off' size='lg'").classes(add="col-span-6 lg:col-span-2 w-full bg-sky-50 shadow-sm shadow-[#07004d] text-bold text-lg text-harmony").bind_value(scheme["prices"],"price_range")
            #Min
            ui.number(label="MIN").props(add="bordered stack-label label-color='#07004d'").classes(add="col-span-6 lg:col-span-2 w-full shadow-sm shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl").bind_visibility_from(price_range_switch,"value").bind_value(scheme["prices"],"min",backward=lambda val:float(val))
            #Max
            ui.number(label="MAX").props(add="bordered stack-label label-color='#07004d'").classes(add="col-span-6 lg:col-span-2 w-full shadow-sm shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl").bind_visibility_from(price_range_switch,"value").bind_value(scheme["prices"],"max",backward=lambda val:float(val))
            #Standard
            ui.number(label="STANDARD").props(add="bordered stack-label label-color='#07004d'").classes(add="col-span-6 lg:col-span-2 w-full shadow-sm shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl").bind_visibility_from(price_range_switch,"value",backward=lambda e:not e).bind_value(scheme["prices"],"standard",backward=lambda val:float(val))
            #Priority
            ui.number(label="PRIORITY").props(add="bordered stack-label label-color='#07004d'").classes(add="col-span-6 lg:col-span-2 w-full shadow-sm shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl").bind_visibility_from(price_range_switch,"value",backward=lambda e:not e).bind_value(scheme["prices"],"priority",backward=lambda val:float(val))
            
          #Insurance pricing(s)
          else:
            with html.div().classes(add="col-span-6 grid grid-cols-2 gap-3"):
              #Copayment switch
              copayment_switch = ui.switch(text="COPAYMENT").props(add="color='green' icon='fa-solid fa-power-off' size='lg'").classes(add="col-span-2 lg:col-span-1 bg-sky-50 shadow-sm shadow-[#07004d] text-bold text-lg text-harmony").bind_value(scheme["prices"],"copayment")
              #Topup
              ui.number(label="TOPUP").props(add="bordered stack-label label-color='#07004d'").classes(add="col-span-2 lg:col-span-1 shadow-sm shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl").bind_visibility_from(copayment_switch,"value").bind_value(scheme["prices"],"topup",backward=lambda val:float(val))
            
            with html.div().classes(add="col-span-6 grid grid-cols-2 gap-3"):
              #Standard
              ui.number(label="STANDARD").props(add="bordered stack-label label-color='#07004d'").classes(add="col-span-2 lg:col-span-1 shadow-sm shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl").bind_value(scheme["prices"],"standard",backward=lambda val:float(val))
              #Priority
              ui.number(label="PRIORITY").props(add="bordered stack-label label-color='#07004d'").classes(add="col-span-2 lg:col-span-1 h-auto shadow-sm shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl").bind_value(scheme["prices"],"priority",backward=lambda val:float(val))
        
        #Amna kitu kabisa
        with html.div().classes(add="grow w-full "):
          ui.space()

        #Save button
        with html.div().classes(add="w-full flex flex-row justify-center items-center gap-5"):
          if scheme["scheme_name"] != "cash":
            ui.button(text="GET PRICES",color="").props(add=f"glossy").classes(add="hidden bg-harmony text-sky-300 text-bold text-xl")
          ui.button(text="SAVE CHANGES",color="",on_click=lambda e:self.register_payment_scheme_and_pricing(scheme=scheme,medicine=medicine)).props(add=f"glossy").classes(add="bg-harmony text-sky-300 text-bold text-xl")

  def PaymentSchemes(self,schemes=None):
    """Displays for editing payment schemes for medicines"""
    #DATA
    if schemes:
      for scheme in schemes:
        scheme["current_pricing"] = [pricing for pricing in scheme["prices"] if pricing["active"]][0]

    #UI
    self.payment_schemes_panel.clear()
    with self.payment_schemes_panel:
      #Schemes
      with html.div().classes(add="grow w-full flex flex-col gap-1"):
        #Scheme zenyewe
        with ui.scroll_area().classes(add="w-full grow p-0 q-pa-none bg-white rounded-none shadow-md shadow-[307004d] animate__animated animate__fadeIn animate__slow"):
          if schemes:
            for scheme in schemes:
              pricing = scheme["current_pricing"]
              #Scheme Proper
              with html.div().props(add=f"scheme_id='{scheme["scheme_id"]}'").classes(add="w-full flex flex-col gap-1 bg-sky-100 rounded shadow-sm shadow-[#07004d]"):
                #Header
                with html.section().classes(add="w-full p-0.5 rounded-t bg-harmony grid grid-cols-3 lg:grid-cols-2"):
                  ui.label(scheme["scheme_name"].upper()).classes(add=" px-1 text-xl text-sky-300 text-bold")
                  with html.div().classes(add="col-span-2 lg:col-span-1 flex flex-row justify-between items-center"):
                    ui.switch(text="ACTIVE",value=scheme["active"]).props(add="dense left-label color='green' icon='fa-solid fa-power-off'").classes(add="bg-inherit text-bold text-sky-200")
                    ui.switch(text="RESTRICTED",value=scheme["restricted"]).props(add="dense left-label color='green' icon='fa-solid fa-power-off'").classes(add="bg-inherit text-bold text-sky-200")
                #Prices
                with html.section().classes(add="grow w-full p-1 grid grid-cols-6 gap-2"):
                  #Cash pricing
                  if scheme["scheme_name"].lower() == "cash":
                    #Price Range Switch
                    price_range_switch = ui.switch(text="PRICE RANGE",value=pricing["price_range"]).props(add="color='green' icon='fa-solid fa-power-off' size='lg'").classes(add="col-span-6 lg:col-span-2 w-full bg-sky-50 shadow-sm shadow-[#07004d] text-bold text-lg text-harmony")
                    #Min
                    min_cash_price = ui.number(label="MIN",value=pricing["min"]).props(add="bordered stack-label label-color='#07004d'").classes(add="col-span-6 lg:col-span-2 w-full shadow-sm shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl").bind_visibility_from(price_range_switch,"value")
                    #Max
                    max_cash_price = ui.number(label="MAX",value=pricing["max"]).props(add="bordered stack-label label-color='#07004d'").classes(add="col-span-6 lg:col-span-2 w-full shadow-sm shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl").bind_visibility_from(price_range_switch,"value")
                    #Standard
                    standard_cash_price = ui.number(label="STANDARD",value=pricing["standard"]).props(add="bordered stack-label label-color='#07004d'").classes(add="col-span-6 lg:col-span-2 w-full shadow-sm shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl").bind_visibility_from(price_range_switch,"value",backward=lambda e:not e)
                    #Priority
                    priority_cash_price = ui.number(label="PRIORITY",value=pricing["priority"]).props(add="bordered stack-label label-color='#07004d'").classes(add="col-span-6 lg:col-span-2 w-full shadow-sm shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl").bind_visibility_from(price_range_switch,"value",backward=lambda e:not e)
                    
                  #Insurance pricing(s)
                  else:
                    #Copayment
                    with html.div().classes(add="col-span-6 lg:col-span-3 w-full grid grid-cols-1 gap-2"):
                      #Copayment switch
                      copayment_switch = ui.switch(text="COPAYMENT",value=pricing["copayment"]).props(add="color='green' icon='fa-solid fa-power-off' size='lg'").classes(add="w-full bg-sky-50 shadow-sm shadow-[#07004d] text-bold text-lg text-harmony")
                      #Topup
                      ui.number(label="TOPUP",value=pricing["topup"]).props(add="bordered stack-label label-color='#07004d'").classes(add="w-full shadow-sm shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl").bind_visibility_from(copayment_switch,"value")
                    #Prices Inputs
                    with html.div().classes(add="col-span-6 lg:col-span-3 grid grid-cols-1 gap-2"):
                      #Standard
                      ui.number(label="STANDARD",value=pricing["standard"]).props(add="bordered stack-label label-color='#07004d'").classes(add="w-full shadow-sm shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl")
                      #Priority
                      ui.number(label="PRIORITY",value=pricing["priority"]).props(add="bordered stack-label label-color='#07004d'").classes(add="w-full shadow-sm shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl")
                      
                  #Save button
                  ui.button(text="SAVE CHANGES",color="",on_click=lambda e:self.update_pricing({
                    "scheme_id":e.sender.parent_slot.parent.parent_slot.parent.props["scheme_id"],
                    "active":e.sender.parent_slot.parent.parent_slot.parent.slots["default"].children[0].slots["default"].children[1].slots["default"].children[0].props["model-value"],
                    "restricted":e.sender.parent_slot.parent.parent_slot.parent.slots["default"].children[0].slots["default"].children[1].slots["default"].children[1].props["model-value"],
                    "copayment":e.sender.parent_slot.parent.slots["default"].children[0].slots["default"].children[0].props["model-value"] if e.sender.props["scheme"].lower() != "cash" else False,
                    "topup":float(e.sender.parent_slot.parent.slots["default"].children[0].slots["default"].children[1].props["model-value"]) if e.sender.props["scheme"].lower() != "cash" else 0.0,
                    "price_range":e.sender.parent_slot.parent.slots["default"].children[0].props["model-value"] if e.sender.props["scheme"].lower() == "cash" else False,
                    "min":float(e.sender.parent_slot.parent.slots["default"].children[1].props["model-value"]) if e.sender.props["scheme"].lower() == "cash" else 0.0,
                    "max":float(e.sender.parent_slot.parent.slots["default"].children[2].props["model-value"]) if e.sender.props["scheme"].lower() == "cash" else 0.0,
                    "standard":float(e.sender.parent_slot.parent.slots["default"].children[3].props["model-value"]) if e.sender.props["scheme"].lower() == "cash" else float(e.sender.parent_slot.parent.slots["default"].children[1].slots["default"].children[0].props["model-value"]),
                    "priority":float(e.sender.parent_slot.parent.slots["default"].children[4].props["model-value"]) if e.sender.props["scheme"].lower() == "cash" else float(e.sender.parent_slot.parent.slots["default"].children[1].slots["default"].children[1].props["model-value"]),
                    "logger":self.user.username
                  })).props(add=f"glossy scheme='{scheme["scheme_name"]}'").classes(add="col-span-6 justify-self-center bg-harmony text-sky-300 text-bold text-xl")





class DispensingStoreManagement():
  """A class for UI and functionalities of dispensing store management"""

  def __init__(self,requisition):
    self.requisition = requisition
    self.visits = len(get_active_visits())

    #UI
    with html.div().classes(add="w-full h-full rounded-t"):
      ui.label("DISPENSING STORE").classes(add="w-full py-1 rounded-t bg-gray-900 px-0 py-3 text-sky-300 text-center text-3xl text-bold")
      with html.div().classes(add="grow w-full p-3 rounded") as self.stocks_panel:
        self.StocksPanel()
  
  #FUNCTIONALITES
  def adc(self,medicine:dict):
    """A method that calculates average daily consumption of medicine"""
    
    pharmacy_visits = (self.visits * 0.75)
    #Capsules or tableets
    if medicine["order_unit"] == "capsule" or medicine["order_unit"] == "tablet":
      return math.ceil(pharmacy_visits * 20)  #Min=10 Max=30 Avg=20
    elif medicine["order_unit"] == "tube" or medicine["order_unit"] == "bottle" or medicine["order_unit"] == "pack":
      return math.ceil(pharmacy_visits)
    else:
      return math.ceil(pharmacy_visits * 0.3)
  
  def dos(self,medicine:dict):
    "A method to that returns a calculated number of days of stock based on data from medicine input"

    available_amount = medicine["dispensing_balance"]
    adc = self.adc(medicine)
    
    if medicine["dispensing_balance"]:
      if adc:
        return round((available_amount/adc))
      else:
        return 1
    else:
      return 0
    
  def stock(self):
    """A method that returns a dictionary with stock details"""
    medicines = self.requisition["medicines"]
    
    overstocks,understocks,stockouts,stocked = [],[],[],[]

    for medicine in medicines:
      dos = self.dos(medicine=medicine)
      stockouts.append(medicine) if dos == 0 else understocks.append(medicine) if dos < 7 else overstocks.append(medicine) if dos >= 14 else stocked.append(medicine)
      
    return {"overstocks":overstocks,"stocked":stocked,"understocks":understocks,"stockouts":stockouts}

  #DISPLAYS
  def StocksPanel(self):
    """A Main display"""
    #DATA
    stocks = self.stock()
    stockouts,understocks,stocked,overstocks = stocks["stockouts"],stocks["understocks"],stocks["stocked"],stocks["overstocks"]
    #UI
    self.stocks_panel.clear()
    with self.stocks_panel:
      with html.div().classes(add="w-full flex flex-col gap-5"):
        #Adequate
        with ui.button(color="green-600",on_click=lambda e:self.StocksDialog(stocked=stocked)).props(add="dense glossy padding='2px 2px'").classes(add="w-full rounded ring-1 ring-green-600 shadow-md shadow-green-600 hover:shadow-green-500") as stocked_button:
          with stocked_button.add_slot("default"):
            with html.span().classes(add="w-full flex flex-row justify-between bg-gray-900 rounded p-2"):
              ui.label("ADEQUATE STOCKS").classes(add="bg-inherit text-green-600 font-medium text-2xl")
              ui.badge(text=str(len(stocked)),color="").classes(add=f"{'px-2 text-2xl' if len(stocked) < 10 else 'pl-1 text-xl'}  bg-inherit size-8 rounded-full ring-1 ring-green-600 shadow-md shadow-green-600 text-green-600 text-bold")
        #Stockouts
        with ui.button(color="red-500",on_click=lambda e:self.StocksDialog(stockouts=stockouts)).props(add="dense glossy padding='2px 2px'").classes(add="w-full rounded ring-1 ring-red-500 shadow-md shadow-red-500 hover:shadow-red-400") as stockouts_button:
          with stockouts_button.add_slot("default"):
            with html.span().classes(add="w-full flex flex-row justify-between bg-gray-900 rounded p-2"):
              ui.label("STOCKOUTS").classes(add="bg-inherit text-red-500 font-medium text-2xl")
              ui.badge(text=str(len(stockouts)),color="").classes(add=f"{'px-2 text-2xl' if len(stockouts) < 10 else 'pl-1 text-xl'} bg-inherit size-8 rounded-full ring-1 ring-red-500 shadow-md shadow-red-500 text-red-500 text-bold {'fa-beat-fade' if stockouts else ''}")
        #Understocks
        with ui.button(color="yellow-400",on_click=lambda e:self.StocksDialog(understocks=understocks)).props(add="dense glossy padding='2px 2px'").classes(add="w-full rounded ring-1 ring-yellow-400 shadow-md shadow-yellow-400 hover:shadow-yellow-300") as understocks_button:
          with understocks_button.add_slot("default"):
            with html.span().classes(add="w-full flex flex-row justify-between bg-gray-900 rounded p-2"):
              ui.label("UNDERSTOCKS").classes(add="bg-inherit text-yellow-400 font-medium text-2xl")
              ui.badge(text=str(len(understocks)),color="").classes(add=f"{'px-2 text-2xl' if len(understocks) < 10 else 'pl-1 text-xl'} bg-inherit size-8 rounded-full ring-1 ring-yellow-400 shadow-md shadow-yellow-400 text-yellow-400 text-bold {'fa-beat-fade' if understocks else ''}")
        #Overstocks
        with ui.button(color="purple-500",on_click=lambda e:self.StocksDialog(overstocks)).props(add="dense glossy padding='2px 2px'").classes(add="w-full rounded ring-1 ring-purple-500 shadow-md shadow-purple-500 hover:shadow-purple-400") as overstocks_button:
          with overstocks_button.add_slot("default"):
            with html.span().classes(add="w-full flex flex-row justify-between bg-gray-900 rounded p-2"):
              ui.label("OVERSTOCKS").classes(add="bg-inherit text-purple-500 font-medium text-2xl")
              ui.badge(text=str(len(overstocks)),color="").classes(add=f"{'px-2 text-2xl' if len(overstocks) < 10 else 'pl-1 text-xl'} bg-inherit size-8 rounded-full ring-1 ring-purple-500 shadow-md shadow-purple-500 text-purple-500 text-bold {'fa-beat-fade' if overstocks else ''}")
        
  def StocksDialog(self,overstocks=None,stocked=None,understocks=None,stockouts=None):
    #DATA
    if overstocks or stocked or understocks or stockouts:
      requisition = self.requisition
      medicines = stockouts if type(stockouts) == list else understocks if type(understocks) == list else stocked if type(stocked) == list else overstocks if type(overstocks) == list else []
    else:
      ui.notify(message=f"No {'stockouts' if type(stockouts) is list else 'understocks' if type(understocks) is list else 'adequately stocked items' if type(stocked) is list else 'overstocks' if type(overstocks) is list else ''}!",type="info",position="top",color=f"{'red-600' if type(stockouts) is list else 'yellow-500' if type(understocks) is list else 'green-500' if type(stocked) is list else 'violet-500' if type(overstocks) is list else ''}")
      return
    
    #UI
    with ui.dialog().props(add="transition-show='scale' transition-hide='scale' transition-duration='500'") as self.stocks_dialog,html.div().style(add="min-width:100%;max-height:95%;").classes(add="bg-white ring-1 ring-blue-400 shadow-md shadow-blue-400"):
      #Dialog Header
      with html.div().classes(add="w-full py-1 pr-2 flex flex-row gap-5 place-center bg-gray-900"):
        #Details
        with html.div().classes(add="grow bg-inherit flex flex-row justify-between content-center pl-3"):
          #Title
          ui.label("STOCKOUTS" if type(stockouts) is list else "UNDERSTOCKS" if type(understocks) is list else "ADEQUATE STOCKS" if type(stocked) is list else "OVERSTOCKS" if type(overstocks) is list else "").classes(add=f"text-{'red-600' if type(stockouts) is list else 'yellow-400' if type(understocks) is list else 'green-600' if type(stocked) is list else 'purple-600' if type(overstocks) is list else ''} text-3xl text-bold")
          #Requisition ID
          with ui.label("REQUISITION ID:").classes(add="h-fit rounded-t font-medium text-sky-50 text-lg"):
            ui.label(requisition["requisition_id"]).classes(add="inline ml-0.5 text-yellow-500 text-bold uppercase")
          #Stock count
          with ui.label(str(len(medicines))).classes(add="h-fit rounded-t text-bold text-yellow-500 text-lg"):
            ui.label(f"ITEM{'' if len(medicines) == 1 else 'S'}").classes(add="inline ml-1 text-sky-50 uppercase")
        #Close button
        ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=self.stocks_dialog.close).classes(add="my-2 size-12 bg-inherit rounded-full text-red-600 text-bold text-base hover:scale-[1.1]")
      #Stocks Aggrid
      with html.div().classes(add="w-full animate__animated animate__fadeIn animate__slow"):
        self.StocksAggrid(overstocks=overstocks,stocked=stocked,understocks=understocks,stockouts=stockouts)
    
    self.stocks_dialog.open()
  
  def StocksAggrid(self,stockouts=None,understocks=None,stocked=None,overstocks=None):
    """"""
    #DATA
    medicines = stockouts if stockouts else understocks if understocks else stocked if stocked else overstocks if overstocks else []
    
    #UI
    if stockouts:
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/No","field":"sno","width":70},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
            {"headerName":"TYPE","field":"type","width":150},
            {"headerName":"UNIT","field":"unit","width":150},
            {"headerName":"BRAND NAME","field":"brand_name"},
            {"headerName":"MANUFACTURER","field":"manufacturer"},
            {"headerName":"DAILY CONSUMPTION","field":"adc","width":150},
          ],
          "rowData":[
            {
              "sno":medicines.index(medicine) + 1,
              "name":medicine["name"],
              "type":medicine["type"],
              "unit":medicine["order_unit"],
              "brand_name":medicine["brand_name"] if medicine["brand_name"] else "---",
              "manufacturer":medicine["manufacturer"] if medicine["manufacturer"] else "---",
              "adc":f"{self.adc(medicine):,.0f}",
            }
            for medicine in medicines
          ]
        },theme="quartz"
        ).classes(add="w-full h-[350px] bg-sky-300 text-sm uppercase")
    
    elif understocks:
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/No","field":"sno","width":100},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
            {"headerName":"TYPE","field":"type","width":150},
            {"headerName":"UNIT","field":"unit","width":150},
            {"headerName":"BRAND NAME","field":"brand_name"},
            {"headerName":"EXPIRY DATE","field":"expire_date","width":200},
            {"headerName":"BALANCE","field":"balance"},
            {"headerName":"DAILY CONSUMPTION","field":"adc"},
            {"headerName":"STOCK DAYS","field":"dos"}
          ],
          "rowData":[
            {
              "sno":medicines.index(medicine) + 1,
              "name":medicine["name"],
              "type":medicine["type"],
              "unit":medicine["order_unit"],
              "brand_name":medicine["brand_name"] if medicine["brand_name"] else "---",
              "expire_date":medicine["expire_date"].strftime("%b %Y") if medicine["expire_date"] else "---",
              "balance":f"{medicine['dispensing_balance']:,.0f}",
              "adc":f"{self.adc(medicine):,.0f}",
              "dos":self.dos(medicine)
            }
            for medicine in medicines
          ]
        },theme="quartz"
        ).style(add="height:350px").classes(add="w-full bg-sky-300 text-sm uppercase")
      
    elif stocked:
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/N","field":"sno","width":80},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
            {"headerName":"TYPE","field":"type","width":150},
            {"headerName":"UNIT","field":"unit","width":150},
            {"headerName":"BRAND NAME","field":"brand_name"},
            {"headerName":"EXPIRY DATE","field":"expire_date","width":200},
            {"headerName":"BALANCE","field":"balance"},
            {"headerName":"DAILY CONSUMPTION","field":"adc"},
            {"headerName":"STOCK DAYS","field":"dos"}
          ],
          "rowData":[
            {
              "sno":medicines.index(medicine) + 1,
              "name":medicine["name"],
              "type":medicine["type"],
              "unit":medicine["order_unit"],
              "brand_name":medicine["brand_name"] if medicine["brand_name"] else "---",
              "expire_date":medicine["expire_date"].strftime("%b %Y") if medicine["expire_date"] else "---",
              "balance":f"{medicine['dispensing_balance']:,.0f}",
              "adc":f"{self.adc(medicine):,.0f}",
              "dos":self.dos(medicine)
            }
            for medicine in medicines
          ]
        },theme="quartz"
        ).style(add="height:350px").classes(add="w-full bg-sky-300 text-sm uppercase")

    elif overstocks:
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/No","field":"sno","width":100},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
            {"headerName":"TYPE","field":"type","width":150},
            {"headerName":"UNIT","field":"unit","width":150},
            {"headerName":"BRAND NAME","field":"brand_name"},
            {"headerName":"EXPIRY DATE","field":"expire_date","width":200},
            {"headerName":"DISPENSING BALANCE","field":"balance"},
            {"headerName":"DAILY CONSUMPTION","field":"adc"},
            {"headerName":"STOCK DAYS","field":"dos"}
          ],
          "rowData":[
            {
              "sno":medicines.index(medicine) + 1,
              "name":medicine["name"],
              "type":medicine["type"],
              "unit":medicine["order_unit"],
              "brand_name":medicine["brand_name"] if medicine["brand_name"] else "---",
              "expire_date":medicine["expire_date"].strftime("%b %Y") if medicine["expire_date"] else "---",
              "balance":f"{medicine['dispensing_balance']:,.0f}",
              "adc":f"{self.adc(medicine):,.0f}",
              "dos":self.dos(medicine)
            }
            for medicine in medicines
          ]
        },theme="quartz"
        ).style(add="height:350px").classes(add="w-full bg-sky-300 text-sm uppercase")


#Management
class StaffManager():
  """This class constructs UI for Staff management interface"""

  def __init__(self,user):
    #DATA
    self.user = user
    self.staffs = [staff for staff in get_staffs() if not staff["is_super"]]

    #UI
    with html.main().classes(add="grow w-full flex flex-col"):
      #Separator
      for i in range(1):
        ui.separator().classes(add="w-full bg-[#09026f]")
      
      #Header
      with html.div().classes(add="w-full flex flex-row items-center bg-harmony"):
        ui.label("STAFF MANAGEMENT PANEL").classes(add="grow bg-inherit text-yellow-500 text-center text-xl uppercase text-bold")
        ui.button(icon="fas fa-circle-plus",color="",on_click=self.StaffDialog).classes(add="lg:hidden size-16 bg-inherit text-yellow-500")
        ui.button(icon="fas fa-circle-plus",color="",on_click=lambda e:self.StaffPanel(lg=True)).classes(add="lg-show size-16 bg-inherit text-yellow-500")
      
      #Body
      with html.section().classes(add="grow w-full p-0.5 grid grid-cols-1 lg:grid-cols-2 gap-x-0.5"):
        #Table of staff
        with html.section().classes(add="w-full h-full flex flex-col") as self.staffs_panel:
          self.StaffsDisplay(staffs=self.staffs)
        
        #Staff Details Interface(for Large screens only)
        with html.section().classes(add="lg-flex w-full h-full flex-col") as self.staff_panel_lg:
          pass
  
  #FUNCTIONALITIES
  def save_staff(self,staff_data:dict,lg:bool=False):
    """"""
    #CONTROLS
    if not (staff_data["first_name"] and staff_data["last_name"] and staff_data["title"] and staff_data["gender"] and staff_data["birthdate"] and staff_data["qualification"] and staff_data["designation"] and staff_data["primary_role"]):
      ui.notify(message="Please fill all required fields",type="negative",position="center")
      return
    #Format data
    data = {
      "first_name":staff_data["first_name"].lower() if staff_data["first_name"] else None,
      "middle_name":staff_data["middle_name"].lower() if staff_data["middle_name"] else None,
      "last_name":staff_data["last_name"].lower() if staff_data["last_name"] else None,
      "username":f"{staff_data['last_name'].lower()}{staff_data['first_name'].lower()[0]}{staff_data['middle_name'].lower()[0] if staff_data['middle_name'] else ''}",
      "title":staff_data["title"].lower() if staff_data["title"] else None,
      "gender":staff_data["gender"].lower() if staff_data["gender"] else None,
      "birthdate":staff_data['birthdate'],
      "qualification":staff_data["qualification"].lower() if staff_data["qualification"] else None,
      "designation":staff_data["designation"].lower() if staff_data["designation"] else None,
      "roles":[staff_data["primary_role"].lower()],
      "primary_role":staff_data["primary_role"],
      "secondary_role":staff_data["secondary_role"],
      "active":True,
      "suspended":False,
      "logins":staff_data["logins"]
    }
    
    if staff_data["secondary_role"]:
      data["roles"].append(staff_data["secondary_role"].lower())
    
    #Save to database
    status = register_staff(data)

    #Notification
    ui.notify(message=status["message"],type=status["type"],position=status["position"])
    
    #UI
    if status["success"]:
      #UI update
      self.staffs = [staff for staff in get_staffs() if not staff["is_super"]]
      if lg:
        self.StaffsDisplay(self.staffs)
        self.StaffPanel(staff=data,lg=True)
      else:
        self.StaffPanel(staff=data)
    
  def update_staff(self,staff_data,suspend:bool=False,activate:bool=False,edit:bool=False,lg:bool=False):
    """"""
    if activate:
      staff_data["username"] = staff_data["username"].lower()
      staff_data["active"],staff_data["suspended"] = True,False
      status = update_staff(staff=staff_data,activate=True)

      #UI update
      self.staffs = [staff for staff in get_staffs() if not staff["is_super"]]
      if lg:
        self.StaffsDisplay(self.staffs)
        self.StaffPanel(staff=staff_data,lg=lg)
      else:
        self.StaffPanel(staff=staff_data)

    if edit:
      data = {
        "first_name":staff_data["first_name"].lower(),
        "middle_name":staff_data["middle_name"].lower(),
        "last_name":staff_data["last_name"].lower(),
        "username":staff_data["username"].lower(),
        "title":staff_data["title"].lower(),
        "gender":staff_data["gender"].lower(),
        "birthdate":staff_data["birthdate"],
        "email":staff_data["email"],
        "mobile":staff_data["mobile"],
        "qualification":staff_data["qualification"].lower(),
        "designation":staff_data["designation"].lower(),
        "roles":[staff_data["primary_role"].lower()],
        "primary":staff_data["primary_role"],
        "secondary_role":staff_data["secondary_role"],
        "active":True,
        "suspended":False
      }

      if staff_data["secondary_role"]:
        data["roles"].append(staff_data["secondary_role"].lower())

      status = update_staff(staff=data,edit=True)

      #UI update
      self.staffs = [staff for staff in get_staffs() if not staff["is_super"]]
      if lg:
        self.StaffsDisplay(self.staffs)
        self.StaffPanel(staff=data,lg=lg)
      else:
        self.StaffPanel(staff=staff_data)
    
    if suspend:
      staff_data["username"] = staff_data["username"].lower()
      staff_data["active"],staff_data["suspended"] = False,True
      status = update_staff(staff=staff_data,suspend=True)

      #UI update
      self.staffs = [staff for staff in get_staffs() if not staff["is_super"]]
      if lg:
        self.StaffsDisplay(self.staffs)
        self.StaffPanel(staff=staff_data,lg=lg)
      else:
        self.StaffPanel(staff=staff_data)
    
    #Notify
    ui.notify(message=status["message"],type=status["type"],position=status["position"])

  #DISPLAYS
  def StaffsDisplay(self,staffs:list) -> None:
    """"""

    self.staffs_panel.clear()
    with self.staffs_panel:
      #Small Screen
      ui.aggrid(
        options={
          "columnDefs":[
            {"headerName":"","field":"status","width":60},
            {"headerName":"NAME","field":"name","sortable":True,"filter":True,"floatingFilter":True},
            {"headerName":"1°  ROLE","field":"primary_role","sortable":True,"filter":True,"width":150},
            {"headerName":"2° ROLE","field":"extra_roles","sortable":True,"filter":True,"width":150}
          ],
          "rowData":[
            {
              "status":StatusDot(active=staff["active"]),
              "name":f"{staff['first_name']} {staff['middle_name'][0].upper() if staff['middle_name'] else ''}. {staff['last_name']}".title(),
              "primary_role":staff['roles'][0].capitalize() if staff["roles"] else "---",
              "extra_roles":" : ".join(staff["roles"][1:]).title() if len(staff["roles"]) > 1 else "---",
              "username":staff["username"]
            } for staff in staffs
          ]
        },
        theme="quartz",
        html_columns=[0]
      ).classes(add="lg:hidden w-full h-full bg-inherit rounded-none text-sm animate__animated animate__fadeIn animate__slow").on("cellClicked",lambda e:self.StaffDialog(staff=[staff for staff in self.staffs if staff['username'] == e.args['data']['username']][0]))


      #Large Screen
      ui.aggrid(
        options={
          "columnDefs":[
            {"headerName":"","field":"status","width":65},
            {"headerName":"NAME","field":"name","sortable":True,"filter":True,"floatingFilter":True},
            {"headerName":"DESIGNATION","field":"designation","width":150},
            {"headerName":"PRIMARY ROLE","field":"primary_role","sortable":True,"filter":True,"width":200},
            {"headerName":"EXTRA ROLE","field":"extra_roles","sortable":True,"filter":True,"width":150}
          ],
          "rowData":[
            {
              "status":StatusDot(active=staff["active"]),
              "name":f"{staff['first_name']} {staff['middle_name'][0].upper() if staff['middle_name'] else ''}. {staff['last_name']}".title(),
              "designation":staff["designation"].title() if staff["designation"] else "---",
              "primary_role":staff['roles'][0].capitalize() if staff["roles"] else "---",
              "extra_roles":" : ".join(staff["roles"][1:]).title() if len(staff["roles"]) > 1 else "---",
              "username":staff["username"]
            } for staff in staffs
          ]
        },
        theme="quartz",
        html_columns=[0]
      ).classes(add="lg-show w-full h-full bg-inherit rounded-b-md text-sm animate__animated animate__fadeIn").on("cellClicked",lambda e:self.StaffPanel(staff=[staff for staff in self.staffs if staff['username'].lower() == e.args['data']['username'].lower()][0],lg=True))

  def StaffDialog(self,staff:dict|None=None):
    """A method to display dialog for staff registration"""
    #FXS
    def close_dialog():
      self.StaffsDisplay(staffs=self.staffs)
      self.staff_dialog.close()
    
    # UI
    with ui.dialog().props(add=f"transition-show='jump-up' transition-hide='jump-down' transition-duration='500'") as self.staff_dialog,html.div().style(add="min-width:75%;min-height:75%;").classes(add="p-0.5 bg-sky-100 flex flex-col"):
      #Header
      with html.section().classes(add="bg-harmony rounded-t flex flex-row justify-between"):
        ui.label(f"{staff['first_name']} {staff['middle_name'] if staff['middle_name'] else ''} {staff['last_name']}".upper() if staff else "NEW STAFF REGISTRATION").classes(add="bg-inherit p-2 grow text-yellow-500 text-2xl text-bold text-center")
        ui.button(icon="fa-regular fa-circle-xmark fa-lg",color="",on_click=close_dialog).classes(add="bg-inherit text-red-500 text-bold text-lg")
      
      #Body
      with html.section().classes(add="grow w-full flex flex-col") as self.staff_panel:
        self.StaffPanel(staff=staff)
  
    self.staff_dialog.open()
  
  def StaffPanel(self,staff:dict|None=None,lg:bool=False):
    """"""
    sections = ["profile","logs"]
    
    if lg:
      self.staff_panel_lg.clear()
      with self.staff_panel_lg:
        if staff:
          #Separator
          for i in range(2):
            ui.separator().classes(add="w-full bg-[#09026f]")

          #Tabs
          with html.div().classes(add="w-full p-0 rounded-b shadow-sm shadow-[#07004d]"):
            with ui.tabs(value=sections[0]).props(add="inline-label mobile-arrows outside-arrows active-class='text-sky-500'").classes(add="w-full rounded-b bg-harmony py-1 text-yellow-500 font-bold") as profile_tabs:
              for section in sections:
                ui.tab(name=section).props(add="dense")
          
          #Panels
          with html.div().classes(add="grow w-full rounded-br flex flex-col"):
            with ui.tab_panels(tabs=profile_tabs,value=sections[0]).props(add="animated infinite transition-prev='jump-right' transition-next='jump-left' transition-duration='700'").classes(add="bg-inherit grow w-full grid grid-cols-1"):
              #Profile
              with ui.tab_panel(name="profile").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col gap-0.5"):
                self.StaffDetailsForm(staff=staff)
              
              #Logs
              with ui.tab_panel(name="logs").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col gap-0.5"):
                self.StaffLogs(staff=staff)

        else:
          self.StaffDetailsForm()
    
    else:
      self.staff_panel.clear()
      with self.staff_panel:
        if staff:
          #Separator
          for i in range(2):
            ui.separator().classes(add="w-full bg-[#09026f]")

          #Tabs
          with html.div().classes(add="w-full p-0 rounded-b shadow-sm shadow-[#07004d]"):
            with ui.tabs(value=sections[0]).props(add="inline-label mobile-arrows outside-arrows active-class='text-sky-500'").classes(add="w-full rounded-b bg-harmony py-1 text-yellow-500 font-bold") as profile_tabs:
              for section in sections:
                ui.tab(name=section).props(add="dense")
          
          #Panels
          with html.div().classes(add="grow w-full rounded-br flex flex-col"):
            with ui.tab_panels(tabs=profile_tabs,value=sections[0]).props(add="animated infinite transition-prev='jump-right' transition-next='jump-left' transition-duration='700'").classes(add="bg-inherit grow w-full grid grid-cols-1"):
              #Profile
              with ui.tab_panel(name="profile").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col gap-0.5"):
                self.StaffDetailsForm(staff=staff)
              
              #Logs
              with ui.tab_panel(name="logs").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col gap-0.5"):
                self.StaffLogs(staff=staff)

        
        else:
          self.StaffDetailsForm()

  def StaffDetailsForm(self,staff:dict|None=None):
    """A structure of form for staff details"""
    #DATA
    edit = bool(staff)
    if staff:
      for key,value in staff.items():
        if type(value) is str:
          staff[key] = value.title()
      staff["title"] = [title for title in TITLES if title.lower() == staff["title"].lower()][0]
      staff["qualification"] = [qualification for qualification in CERTIFICATIONS if qualification.lower() == staff["qualification"].lower()][0]
      staff["designation"] = [designation for designation in DESIGNATIONS if designation.lower() == staff["designation"].lower()][0]
      staff["primary_role"] = [role for role in PRIMARY_ROLES if role.lower() == staff["roles"][0].lower()][0]
      if len(staff["roles"]) > 1:
        staff["secondary_role"] = [role for role in SECONDARY_ROLES if role and role.lower() == staff["roles"][1].lower()][0]
      else:
        staff["secondary_role"] = None

    staff = staff if staff else {"title":"","first_name":"","middle_name":"","last_name": "","birthdate":datetime.fromisoformat("1995-10-06") ,"gender": "","qualification":CERTIFICATIONS[-1],"designation": "","primary_role": "","secondary_role": "","suspended":False,"active":True,"logins":[]}
    
    #UI
    with html.form().classes(add="grow w-full p-2 flex lg:grid grid-cols-2 flex-col justify-between lg:justify-start gap-2 animate__animated animate__fadeIn animate__slow"):
      #Name
      with html.div().classes(add="grid grid-cols-8 gap-2"):
        ui.select(label="TITLE",options=TITLES).props(add=f"{'readonly' if staff['suspended'] else ''} required stack-label type='text'").classes(add="col-span-2 px-2 shadow-md shadow-[#07004d] bg-white rounded text-lg capitalize").bind_value(staff,"title")
        ui.input(label="FIRST NAME").props(add=f"{'readonly' if staff['suspended'] else ''} required stack-label type='text'").classes(add="col-span-3 shadow-md shadow-[#07004d] px-2 bg-white rounded-sm text-lg").bind_value(staff,"first_name")
        ui.input(label="MIDDLE NAME").props(add=f"{'readonly' if staff['suspended'] else ''} stack-label type='text'").classes(add="col-span-3 shadow-md shadow-[#07004d] px-2 bg-white rounded-sm text-lg").bind_value(staff,"middle_name")
        ui.input(label="LAST NAME").props(add=f"{'readonly' if staff['suspended'] else ''} required stack-label type='text'").classes(add="col-span-4 shadow-md shadow-[#07004d] px-2 bg-white rounded-sm text-lg").bind_value(staff,"last_name")
        ui.select(label="GENDER",options=["Male","Female"]).props(add=f"{'readonly' if staff['suspended'] else ''} required type='text'").classes(add="col-span-4 shadow-md shadow-[#07004d] px-2 bg-white rounded-sm text-lg").bind_value(staff,"gender")

      #Details
      with html.section().classes(add="grid grid-cols-2 lg:grid-cols-1  gap-2"):
        #Birthdate
        with ui.input(label="BIRTHDATE").props(add="bordered readonly").classes(add="w-full px-2 shadow-md shadow-[#07004d] bg-white rounded text-lg").bind_value_from(staff,"birthdate",backward=lambda e:e.strftime("%d %b %Y")) as bdate_display:
          with ui.dialog() as calendar:
            ui.date(mask="YYYY-MM-DD",on_change=lambda e:calendar.close()).props(add=f"{'readonly' if staff['suspended'] else ''} bordered square today-btn color='harmony' event-color='orange' first-day-of-week='1' navigation-max-year-month='{datetime.now().strftime("%Y/%m")}'").bind_value(target_object=staff,target_name="birthdate",forward=lambda e:datetime.fromisoformat(str(e)[:10]))
            with bdate_display.add_slot("append"):
              ui.icon("fas fa-cake-candles",color="pink-500").on("click",calendar.open)
        #Age
        ui.input(label="AGE").props(add="readonly stack-label").bind_value_from(target_object=staff,target_name="birthdate",backward=lambda e:format_age(e)).classes(add="w-full shadow-md shadow-[#07004d] bg-sky-50 rounded px-2 text-lg text-bold text-sky-600")
      
      ui.separator().classes(add="lg:hidden my-1 w-full")

      #Academic Details
      with html.div().classes(add="col-span-2 grid grid-cols-2 gap-2 p-1"):
        ui.select(label="QUALIFICATION",options=CERTIFICATIONS).props(add=f"{'readonly' if staff['suspended'] else ''} stack-label type='text'").classes(add="shadow-md shadow-[#07004d] px-2 bg-white rounded text-lg").bind_value(staff,"qualification")
        #Designation
        ui.select(label="DESIGNATION",options=DESIGNATIONS).props(add=f"{'readonly' if staff['suspended'] else ''} required stack-label type='text'").classes(add="shadow-md shadow-[#07004d] px-2 bg-white rounded text-lg").bind_value(staff,"designation")
        #Uploads
        with ui.label().classes(add="hidden col-span-2 rounded flex flex-row justify-center"):
          with ui.dialog().style(add="min-width:50%;") as upload_dialog:
            ui.upload(label="CERTIFICATE UPLOAD",multiple=True,max_file_size=500000,auto_upload=True).props(add="accept='.pdf'").style(add="").classes(add="m-1 w-full bg-sky-50 text-yellow-800")
          ui.button('upload certificates',color="gray-800",on_click=upload_dialog.open).classes(add="justify-self-center text-yellow-500 text-xl text-bold")
        
      ui.separator().classes(add="lg:hidden my-1 w-full")
      
      #Roles
      with html.div().classes(add="col-span-2 w-full grid grid-cols-1 lg:grid-cols-2 gap-2"):
        #Primary roles
        with html.div().classes(add="w-full p-0.5 rounded bg-sky-50 shadow-md shadow-[#07004d]"):
          ui.label('primary roles').classes(add="rounded small-caps text-bold text-xl text-harmony")
          ui.radio(options=PRIMARY_ROLES).props(add=f"{'disable' if staff['suspended'] else ''} inline required").bind_value(staff,"primary_role")
        #Secondary roles
        with html.div().classes(add="w-full p-0.5 rounded bg-sky-50 shadow-md shadow-[#07004d]"):
          ui.label('secondary roles').classes(add="rounded small-caps text-bold text-xl text-harmony")
          ui.radio(options=SECONDARY_ROLES).props(add=f"{'disable' if staff['suspended'] else ''} inline").classes(add="lg:self-start").bind_value(staff,"secondary_role")
        
          #Lg buttons
          with html.div().classes(add=f"lg-flex col-start-2 col-span-1 self-end w-full flex-row justify-center gap-5"):
            if staff["suspended"]:
              ui.button(text="ACTIVATE",color="",on_click=lambda e:self.update_staff(staff_data=staff,activate=True,lg=True)).classes(add="bg-harmony text-yellow-500 text-bold text-xl")
            else:
              if edit:
                ui.button(text="SAVE",color="",on_click=lambda e:self.update_staff(staff_data=staff,edit=True,lg=True)).classes(add="bg-harmony text-yellow-500 text-bold text-xl")
                ui.button(text="SUSPEND",color="",on_click=lambda e:self.update_staff(staff_data=staff,suspend=True)).classes(add="bg-harmony text-yellow-500 text-bold text-xl")
                
              else:
                ui.button(text="SAVE",color="",on_click=lambda e:self.save_staff(staff_data=staff,lg=True)).classes(add="bg-harmony text-yellow-500 text-bold text-xl")


      #Buttons
      with html.div().classes(add=f"lg:hidden w-full flex flex-row justify-center gap-5"):
        if staff["suspended"]:
          ui.button(text="ACTIVATE",color="",on_click=lambda e:self.update_staff(staff_data=staff,activate=True)).classes(add="bg-harmony text-yellow-500 text-bold text-xl")
        else:
          if edit:
            ui.button(text="SAVE",color="",on_click=lambda e:self.update_staff(staff_data=staff,edit=True)).classes(add="bg-harmony text-yellow-500 text-bold text-xl")
            ui.button(text="SUSPEND",color="",on_click=lambda e:self.update_staff(staff_data=staff,suspend=True)).classes(add="bg-harmony text-yellow-500 text-bold text-xl")
            
          else:
            ui.button(text="SAVE",color="",on_click=lambda e:self.save_staff(staff)).classes(add="bg-harmony text-yellow-500 text-bold text-xl")

  def StaffLogs(self,staff:dict):
    """Displays details of logins of staff"""
    #DATA
    logs = sorted(staff["logins"],key=lambda log:log["login_time"],reverse=True)

    #UI
    with html.div().classes(add="grow w-full flex flex-col") as logs_container:
      if logs:
        with ui.scroll_area().classes(add="grow w-full") as logs_container:
          for log in logs:
            with ui.button(color="").props(add="glossy").classes(add=f"w-full m-0 p-0 bg-sky-50 rounded shadow-sm shadow-[#07004d] {'ring-2 ring-green-600 ring-offset-1' if log['logged'] else ''}"):
              #Login
              with html.span().classes(add="w-full p-1 grid grid-cols-2"):
                ui.label("LOGIN").classes(add="w-full font-semibold text-sky-600 text-lg text-start")
                ui.label(log["login_time"].strftime("%d %b %Y %H:%M") if log["login_time"] else "---").classes(add="w-full font-medium text-harmony text-lg")
              
              #Separator
              ui.separator().classes(add="w-full")

              #Logout
              with html.span().classes(add="p-1 w-full grid grid-cols-2"):
                ui.label("LOGOUT").classes(add="w-full font-semibold text-sky-600 text-lg text-start")
                ui.label(log["logout_time"].strftime("%d %b %Y %H:%M") if log["logout_time"] else "---").classes(add="w-full font-medium text-harmony text-lg")

      else:
        with logs_container.classes(add="justify-center items-center"):
          ui.label("This staff has no logs!").classes(add="italic font-semibold text-red-600 text-xl fa-fade")

class ServicesManager():

  def __init__(self,user):
    #DATA
    self.user = user
    self.initial_data()

    #UI
    with html.main().classes(add="grow w-full flex flex-col"):
      #Separator
      for i in range(1):
        ui.separator().classes(add="w-full bg-[#09026f]")
      
      #Header
      with html.div().classes(add="w-full flex flex-row items-center bg-harmony"):
        ui.label("SERVICES MANAGEMENT PANEL").classes(add="grow bg-inherit text-yellow-500 text-center text-xl lg:text-2xl uppercase text-bold")
        ui.button(icon="fas fa-circle-plus",color="",on_click=self.ServiceDialog).classes(add="size-16 bg-inherit text-yellow-500")
      
      #Body
      with html.section().classes(add="grow w-full p-0.5 flex flex-col") as self.services_panel:
        self.ServicesDisplay(self.services)
        
  #FUNCTIONALITIES
  def initial_data(self):
    self.services = get_services()
    self.template_services = get_template_services()

  def retrieve_service(self,service:str):
    """A method that retrieves service details and populate details in ServiceDetailsForm"""
    if not service:
      return
    
    service = get_template_service(service.lower())
    service["payment"] = self.pricings(service)
    
    self.ServiceDetailsForm(service)

  def save_service(self,service:dict,update:bool=False):
    """"""

    for key,value in service.items():
      if type(value) == str:
        service[key] == value.lower()
    
    payment = service["payment"]
    payment.pop("insured")
    payment.pop("logger")
    payment.pop("service_id")
    
    for scheme in service["schemes"]:
      for price in scheme["prices"]:
        for pay_scheme,pay_details in payment.items():
          if scheme["scheme_name"].lower() == pay_scheme.lower():
            scheme["scheme_id"] = pay_details["scheme_id"]
            price["logger"] = self.user.username
            price["copayment"] = pay_details["copayment"]
            price["price_range"] = pay_details["price_range"]
            price["min"] = pay_details["min"]
            price["max"] = pay_details["max"]
            price["standard"] = pay_details["standard"]
            price["priority"] = pay_details["priority"]
            price["topup"] = pay_details["topup"]
    service.pop("payment")
    
    if update:
      status = update_service(service)
    else:
      status = register_service(service)

    ui.notify(message=status["message"],type=status["type"],position=status["position"])

    self.initial_data()
        
    self.ServicesDisplay(services=self.services)
    
  def pricings(self,service:dict):
    """Returns a namedtuple object with prices of a 'service'"""

    for scheme in service["schemes"]:
      for pricing in scheme["prices"]:
        pricing["scheme_item_code"] = scheme["scheme_item_code"]
        pricing["restricted"] = scheme["restricted"]
    
    output = {scheme["scheme_name"]:[pricing for pricing in scheme["prices"] if pricing["active"]][0] for scheme in service["schemes"] if scheme.get("active")}
    output["logger"] = self.user.username
    output["service_id"] = service["service_id"]
    if "nhif" in output:
      output["insured"] = True
    else:
      output["insured"] = False
      output["nhif"] = {
        "scheme_id":f"cash-{service['service_id'].lower()}",
        "scheme_item_code":"",
        "copayment":False,
        "price_range":False,
        "min":0,
        "max":0,
        "standard":0,
        "priority":0,
        "topup":0
      }

    return output

  #DISPLAYS
  def ServicesDisplay(self,services:list):
    """"""
    #FXS
    def Status(service,lg:bool=False):
      _status = service["active"]
      status = ""
      if lg:
        if _status:
          status = "<span class='text-green-600 text-bold' >Active</span>"
        else:
          status = "<span class='text-red-600 text-bold' >Inactive</span>"
      else:
        if _status:
          status = "<span class='fa-solid fa-circle-dot text-green-600 text-bold' ></span>"
        else:
          status = "<span class='fa-solid fa-circle-dot text-red-600 text-bold' ></span>"
      
      return status

    def MiniPayment(service):
      pricings = self.pricings(service)
      pricings.pop("logger")
      pricings.pop("service_id")
      pricings.pop("insured")
      return f"<div class='grid grid-cols-2 gap-2 text-bold uppercase'>{''.join([f'<div class="w-full text-center {'col-start-1 text-harmony' if scheme == 'cash' else 'col-start-2 text-yellow-700'}">{scheme}</div>' for scheme,pricing in pricings.items() if pricing['standard'] or pricing["price_range"]])}</div"
    
    def Payment(service,cash:bool=False,nhif:bool=False):
      def _format_price(price):
        return f"{price:,.2f}"

      pricings = self.pricings(service)
      if cash:
        price = pricings.get("cash")
        if price["price_range"]:
          return f"<div class='text-harmony font-semibold'>{price['min']:,.2f} - {price['max']:,.2f}</div>"
        else:
          return f"<div class='text-harmony font-semibold'>{price['standard']:,.2f}</div>"
      
      if nhif:
        if "nhif" in pricings:
          price = pricings.get("nhif")
          return f"<div class='grid grid-cols-2 gap-5 font-semibold'><div class='grid grid-cols-2 gap-1' ><span class='text-yellow-800' >STANDARD</span><span class='justify-self-end' >{_format_price(price['standard']) if price['standard'] else '---'}</span></div><div class='grid grid-cols-2 gap-1' ><span class='text-yellow-800' >PRIORITY</span><span class='justify-self-end' >{_format_price(price['priority']) if price['priority'] else '---'}</span></div></div>"
        else:
          return f"<div class='grid grid-cols-2 gap-3 font-semibold'><div class='grid grid-cols-2 gap-1' ><span class='text-yellow-800' >STANDARD</span><span class='justify-self-end' >---</span></div><div class='grid grid-cols-2 gap-1' ><span class='text-yellow-800' >PRIORITY</span><span class='justify-self-end' >---</span></div></div>"

    #UI
    self.services_panel.clear()
    with self.services_panel:
      ui.aggrid(
        options={
          "columnDefs":[
            {"headerName":"","field":"sno","width":50},
            {"headerName":"NAME","field":"name","sortable":True,"filter":True,"floatingFilter":True},
            {"headerName":"TYPE","field":"type","width":100},
            {"headerName":"STATUS","field":"status","width":75},
            {"headerName":"CASH PRICES (TZS)","field":"price_cash","sortable":True,"width":150},
            {"headerName":"NHIF PRICES (TZS)","field":"price_nhif","sortable":True,"width":300},
          ],
          "rowData":[
            {
              "sno":services.index(service) + 1,
              "name":service["name"].title(),
              "type":service["type"].capitalize(),
              "status":Status(service,lg=True),
              "price_cash":Payment(service,cash=True),
              "price_nhif":Payment(service,nhif=True),
              "service_id":service["service_id"]
            } for service in services
          ]
        },
        theme="quartz",
        html_columns=[3,4,5]
      ).classes(add="lg-show w-full h-full bg-inherit rounded-b-md text-sm animate__animated animate__fadeIn").on("cellClicked",lambda e:self.ServiceDialog(service=[service for service in self.services if service['service_id'] == e.args['data']['service_id'].lower()][0]))
  
      #Small Screen
      ui.aggrid(
        options={
          "columnDefs":[
            {"headerName":"","field":"status","width":50},
            {"headerName":"NAME","field":"name","sortable":True,"filter":True,"floatingFilter":True,"width":300},
            {"headerName":"TYPE","field":"type","width":200},
            {"headerName":"PAYMENT","field":"payment","sortable":True,"width":150},
          ],
          "rowData":[
            {
              "status":Status(service),
              "name":service["name"].title(),
              "type":service["type"].capitalize(),
              "payment":MiniPayment(service),
              "service_id":service["service_id"]
            } for service in services
          ]
        },
        theme="quartz",
        html_columns=[0,3]
      ).classes(add="lg:hidden w-full h-full bg-inherit rounded-b-md text-sm animate__animated animate__fadeIn").on("cellClicked",lambda e:self.ServiceDialog(service=[service for service in self.services if service['service_id'] == e.args['data']['service_id'].lower()][0]))
  
  def ServiceDialog(self,service:dict|None=None):
    """A method to display dialog for service registration and editing"""
    #FXS
    def close_dialog():
      self.ServicesDisplay(services=self.services)
      self.service_dialog.close()

    # UI
    with ui.dialog().props(add=f"transition-show='jump-up' transition-hide='jump-down' transition-duration='300'") as self.service_dialog,html.div().style(add="min-width:60%;min-height:60%;").classes(add="p-0.5 bg-sky-50 flex flex-col"):
      #Header
      with html.section().classes(add="bg-harmony flex flex-row justify-between"):
        ui.label(service["name"].upper() if service else "SERVICE PANEL").classes(add="bg-inherit p-2 grow text-yellow-600 text-xl lg:text-3xl text-bold text-center")
        ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=close_dialog).classes(add="bg-inherit text-rose-500 text-bold text-base")
      
      #Search Bar
      with html.section().classes(add="w-full p-3 flex flex-row justify-center"):
        ui.select(label="SERVICE NAME",options=self.template_services,with_input=True,on_change=lambda e:self.retrieve_service(service=e.value)).props(add=f"popup-content-class='capitalize'").classes(add="col-span-3 px-1 bg-white shadow-md shadow-[#07004d] rounded text-lg")

      #Service details
      with html.section().classes(add="grow w-full flex flex-col") as self.service_panel:
        self.ServiceDetailsForm(service=service,edit=True if service else False)
        
    self.service_dialog.open()
  
  def ServiceDetailsForm(self,service:dict,edit:bool=False):
    #DATA
    if service:
      if edit:
        data = service
        data["payment"] = self.pricings(service)
      else:
        data = service
    
    else:
      data = {
        "service_id":"",
        "name":self.template_services[0],
        "alternative_name":"",
        "type":"",
        "payment":{
          "logger":self.user.username,
          "service_id":"",
          "insured":False,
          "cash":{
            "scheme_id":f"",
            "logger":self.user.username,
            "copayment":False,
            "price_range":False,
            "min":0,
            "max":0,
            "standard":0,
            "priority":0,
            "topup":0
          },
          "nhif":{
            "scheme_id":"",
            "logger":self.user.username,
            "copayment":False,
            "price_range":False,
            "min":0,
            "max":0,
            "standard":0,
            "priority":0,
            "topup":0
          }
        }
      }

    #FXS
    def update_service_prices(nhif:bool=False):
      data["payment"] = retrieve_updated_prices(data=data["payment"],nhif=nhif)
      display_nhif_prices()
      
    def display_nhif_prices():
      nhif_prices_display.clear()
      with nhif_prices_display:
        ui.button(text="update",color="",on_click=lambda e:update_service_prices(nhif=True)).props(add="glossy").classes(add="bg-harmony text-xl text-yellow-500 font-medium").bind_visibility_from(data["payment"],"insured")
        nhif_standard_display = ui.number(label="STANDARD").props(add="readonly stack-label label-color='#07004d'").classes(add="w-full px-1 bg-white shadow-sm shadow-[#07004d] rounded-sm text-lg").bind_value(data["payment"]["nhif"],"standard").bind_visibility_from(data["payment"],"insured")
        nhif_priority_display = ui.number(label="PRIORITY").props(add="readonly required stack-label label-color='#07004d'").classes(add="w-full px-1 bg-white shadow-sm shadow-[#07004d] rounded-sm text-lg").bind_value(data["payment"]["nhif"],"priority").bind_visibility_from(data["payment"],"insured")
        #Message if its not insured
        ui.label("Not Insured by NHIF").classes(add="col-span-3 text-lg text-gray-500 font-semibold italic text-center fa-fade").bind_visibility_from(data["payment"],"insured",backward=lambda insured:not insured)
      
    #UI
    self.service_panel.clear()
    with self.service_panel:
      with html.form().classes(add="w-full py-1 px-0 grid grid-cols-1 lg:grid-cols-5 gap-2"):
        #General Details
        with html.section().classes(add="lg:col-span-2 w-full flex flex-col gap-2"):
          ui.label('GENERAL DETAILS').classes(add="grow w-full px-1 shadow-md shadow-[#07004d] text-bold text-xl text-harmony")
          with html.div().classes(add="w-full p-1 grid grid-cols-3 gap-2"):
            ui.input(label="NAME").props(add="readonly stack-label type='text'").classes(add="col-span-3 px-1 bg-white shadow-sm shadow-[#07004d] rounded text-lg").bind_value(data,"name",backward=lambda service_name:service_name.title() if service_name else service_name)
            ui.input(label="OTHER NAME (Optional)").props(add="readonly stack-label type='text'").classes(add="col-span-2 lg:col-span-3 bg-white shadow-sm shadow-[#07004d] rounded px-1 text-lg").bind_value_from(data,"alternative_name",backward=lambda service_alt_name:service_alt_name.title() if service_alt_name else service_alt_name)
            ui.input(label="SERVICE TYPE").props(add="readonly required stack-label").classes(add="col-span-1 lg:col-span-3 bg-white shadow-sm shadow-[#07004d] rounded px-1 text-lg").bind_value(data,"type",backward=lambda service_type:service_type.title() if service_type else service_type)
        
        #Prices
        with html.section().classes(add="lg:col-span-3 grow w-full flex flex-col gap-2"):
          ui.label('PRICING DETAILS').classes(add="w-full px-1 shadow-md shadow-[#07004d] text-bold text-xl text-harmony")
          #CASH Pricing
          with html.div().classes(add="grow w-full p-1 flex flex-col gap-2"):
            ui.label("CASH PRICES").classes(add="col-span-3 w-full px-1 shadow-sm shadow-[#07004d] text-bold text-xl text-harmony")
            with html.div().classes(add="grid grid-cols-3 gap-2") as cash_prices_display:
              ui.switch("PRICE RANGE").props(add="left-label size='lg' unchecked-icon='fa-regular fa-circle-xmark' checked-icon='fa-solid fa-check-double' color='green-8'").classes(add="px-1 bg-sky-50 shadow-sm shadow-[#07004d] text-harmony font-medium").bind_value(data["payment"]["cash"],"price_range")
            
              ui.number(label="STANDARD").props(add="stack-label label-color='#07004d'").classes(add="w-full px-1 bg-white shadow-sm shadow-[#07004d] rounded-sm text-lg").bind_value(data["payment"]["cash"],"standard").bind_visibility_from(data["payment"]["cash"],"price_range",backward=lambda price_range:not price_range)
              ui.number(label="PRIORITY").props(add="required").classes(add="w-full px-1 bg-white shadow-sm shadow-[#07004d] rounded-sm text-lg").bind_value(data["payment"]["cash"],"priority").bind_visibility_from(data["payment"]["cash"],"price_range",backward=lambda price_range:not price_range)

              ui.number(label="CASH MIN").props(add="stack-label label-color='#07004d'").style(add="caret-color:#daa520;").classes(add="w-full px-1 bg-white shadow-sm shadow-[#07004d] rounded text-lg").bind_value(data["payment"]["cash"],"min").bind_visibility_from(data["payment"]["cash"],"price_range")
              ui.number(label="CASH MAX").props(add="stack-label label-color='#07004d'").style(add="caret-color:#daa520;").classes(add="w-full px-1 bg-white shadow-sm shadow-[#07004d] rounded text-lg").bind_value(data["payment"]["cash"],"max").bind_visibility_from(data["payment"]["cash"],"price_range")
          
          #NHIF Pricing
          with html.div().classes(add="grow w-full p-1 flex flex-col gap-2"):
            ui.label("NHIF PRICES").classes(add="col-span-3 w-full px-1 shadow-sm shadow-[#07004d] text-bold text-xl text-harmony")
            with html.div().classes(add="grid grid-cols-3 gap-2") as nhif_prices_display:
              display_nhif_prices()
        
        #Buttons
        with html.div().classes(add="lg:col-span-5 w-full py-2 flex flex-row justify-center"):
          ui.button(text="SAVE SERVICE",color="",on_click=lambda e:self.save_service(service=data,update=True if edit else False)).props(add="glossy").classes(add="bg-harmony text-yellow-500 text-bold text-xl")
          



