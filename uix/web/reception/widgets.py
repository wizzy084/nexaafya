"""A module for structuring and styling page components for Panel app functionality"""

#GENERAL IMPORTS
from time import sleep

#APP IMPORTS
from services.provider.admin.constants import *
from services.provider.admin.processor import get_staffs,get_staff,get_staff_username,get_services
from services.provider.clients.db import register_triage,update_payment
from services.provider.clients.processor import get_clients,get_active_visits

#UIX IMPORT
from .miniwidgets import *
from ..tools.widgets import AppointmentsManager
from ..tools.components import ClientCard
from ..tools._snippets import format_age




###
class ClientsManagementDisplay():
  """A class to display UI for managing studies"""

  def __init__(self,user):
    #DATA
    self.user = user
    self.initial_data()
    self.initial_visits_data()
    self.initial_appointments_data()

    #UI
    with html.div().classes(add="w-full h-full flex flex-col p-0.5 gap-1 bg-inherit animate__animated animate__fadeIn") as self.master_container:
      self.Carousel(clients=True)  

  def initial_data(self):
    
    self.consultants = [f"{staff['first_name']} {staff['last_name']}".title() for staff in get_staffs() if "doctor" in staff["roles"]]
    self.services = {
      "Consultation":["consultant",[service["name"].split(" ")[0] for service in get_services() if service["type"] == "consultation"]],
      "Imaging":["imaging study",[service["name"] for service in get_services() if service["type"] == "imaging"]],
      "Procedure":["procedure",[service["name"] for service in get_services() if service["type"] == "procedure"]]
    }
    self.raw_clients = get_clients()

    self.visited_clients = sorted([client for client in self.raw_clients if client["visits"]],key=lambda client:self.last_visit(client)["time"],reverse=True)
    self.new_clients = sorted([client for client in self.raw_clients if not client["visits"]],key=lambda client:client["created_on"],reverse=True)
    self.clients = self.new_clients + self.visited_clients

    self.visits = get_active_visits()
  
  def initial_visits_data(self):
    self.today_visits = [visit for visit in get_active_visits() if visit["start_time"].date() == datetime.now().date()]
    self.consulted_visits = [visit for visit in self.today_visits if visit["consultations"]]
    self.imaging_visits = [visit for visit in self.today_visits if visit["imagings"]]
    self.procedures_visits = [visit for visit in self.today_visits if visit["procedures"]]
    self.pharmacy_visits = [visit for visit in self.today_visits if visit["medications"] + visit["medical_items"]]

  def initial_appointments_data(self):
    self.appointments = get_appointments()
    self.today_appointments = [appointment for appointment in self.appointments if appointment["appointment_date"] == datetime.now().date()]

  #FUNCTIONALITIES
  def is_in_range(self,start_date:str,end_date:str,target_date:date):
    """Returns True if 'target_date' is between 'start_date' and 'end_date'"""
    
    start_date,end_date,target_date = datetime.fromisoformat(start_date).date(),datetime.fromisoformat(end_date).date(),target_date

    if target_date >= start_date and target_date <= end_date:
      return True
    else:
      return False

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
    consultations = visit["consultations"]
    anthropometrics = visit["anthropometrics"]
    vitals =  visit["vital_signs"]
    labs = visit["labs"]

    for consultation in consultations:
      consultation["service_time"] = visit["start_time"]
      consultation["cancelled"] = False
      consultation["triages"] = [visit["anthropometrics"][-1]["payment"]["payment_id"],visit["vital_signs"][-1]["payment"]["payment_id"]]

    imagings = visit["imagings"]
    done_imagings = [imaging for imaging in imagings if imaging["processed"]]
    not_done_imagings = [imaging for imaging in imagings if not (imaging["cancelled"] or imaging["processed"])]
    cancelled_imagings = [imaging for imaging in imagings if imaging["cancelled"]]

    procedures = visit["procedures"]
    done_procedures = [procedure for procedure in procedures if procedure["done"]]
    not_done_procedures = [procedure for procedure in procedures if not (procedure["done"] or procedure["cancelled"])]
    cancelled_procedures = [procedure for procedure in procedures if procedure["cancelled"]]

    medicines = visit["medications"]
    dispensed_medicines = [medicine for medicine in medicines if medicine["dispensed"]]
    not_dispensed_medicines = [medicine for medicine in medicines if not (medicine["dispensed"] or medicine["cancelled"])]
    cancelled_medicines = [medicine for medicine in medicines if medicine["cancelled"]]


    all_services = consultations + imagings + procedures + medicines
    paid_services = [service for service in all_services if service["payment"]["paid"]]
    billed_services = [service for service in all_services if service["payment"]["billed"] and not service["cancelled"]]
    unpaid_services = [service for service in all_services if not (service["payment"]["paid"] or service["payment"]["billed"])]
    cancelled_services = [service for service in all_services if service["payment"]["cancelled"]]
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
    
    for service in services:
      #Consultation
      if "consultant_id" in service:
        service["service_id"] = service["consultation_id"]
        service["attendee_id"] = self.user.username
        service["done"] = service["initiated"]
        service["done_on"] = service["clinical_history"]["history_time"]
        service["done_by"] = service["consultant_id"]
        service["cancelled"] = False
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

    
    return services

  def format_client_id(self):
    """Returns a formatted client id"""
    
    client_id_primer = datetime.today().date().strftime("%y%m")

    try:
      latest_client_id = get_latest_client_id()
      #If month hasnt changed
      if latest_client_id[:4] == client_id_primer:

        raw_id = int(latest_client_id[-3:]) + 1
        
        if raw_id < 10:
          client_id = client_id_primer + f"00{raw_id}"
        elif raw_id <100:
          client_id = client_id_primer + f"0{raw_id}"
        else:
          client_id = client_id_primer + f"{raw_id}"
        
        return client_id
      
      #If month has changed
      else:
        return client_id_primer + "001"

    except IndexError:
      return client_id_primer + "001"

  def last_visit(self,client):
    """A method that takes in client and returns"""
    
    if len(client["visits"]) > 0:
      last_visit = [visit for visit in client["visits"]][-1]
      
      #Active visit status
      if last_visit["is_active"] == True:
        last_visit["status"] = "active"
      else:
        last_visit["status"] = "inactive"
    
      return {"visit_id_index":int(last_visit["visit_id"].split("v")[1]),"time":last_visit["start_time"],"duration":f"{format_age(last_visit['start_time']).split(' ')[0]} {format_age(last_visit['start_time']).split(' ')[1]} ago","status":last_visit["status"]}
    else:
      return {"time":"No prior visit!","duration":"---","status":"---"}
  
  def fetch_insured_client(self,data):
    #Fetching data from API
    client_data = fetch_insured_client(data)
  
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
  
  def reload_clients(self):
    """A method to reload clients data from database"""
    ###NOT ACTIVE!!!!!!!!!!!!!!!!!!!!!!!
    self.initial_data()
    self.initial_visits_data()
    self.initial_appointments_data()

    #UI Update
    self.stats_panel.update()
    self.ClientsStats()
    self.ClientsAggrid(self.clients)
    ui.notify(message="You are updated!",color="primary",position="top")

  def initiate_visit(self,visit_data:dict,clients:bool=False,appointments:bool=False):
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
    selected_service = [service for service in get_services() if service["name"].startswith(visit_data["service_option"].lower())][0]
    selected_service_scheme = [scheme for scheme in selected_service["schemes"] if scheme["scheme_name"] == visit_data["payment_mode"].lower()][0]
    if selected_service_scheme["active"]:
      service_prices = [price for price in selected_service_scheme["prices"] if price["active"]][0]
    else:
      ui.notify(message=f"Visit cannot be started via {visit_data['payment_mode'].upper()}",caption=f"Try another payment mode!",type="warning",position="top")

    #CONSULTATION
    if selected_service["type"] == "consultation":
      
      #Consultation
      consultation = {
        "visit_id":visit_data["visit_id"].lower(),
        "name":selected_service["name"],
        "payment":{
          "payment_mode":visit_data["payment_mode"].lower(),
          "cost":service_prices[visit_data['package'].lower()],
          "billed":True,
          "billed_amount":service_prices[visit_data['package'].lower()],
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
          "payment_id":f"{visit_data['visit_id'].lower()}vs1pay1",
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
          "payment_id":f"{visit_data['visit_id'].lower()}anp1pay1",
          "payment_mode":visit_data["payment_mode"].lower(),
          "cost":0,
          "authorization_no":visit_data["authorization_no"],
          "billed":True
        }
      }
      status = register_visit(visit)
      register_consultation(consultation)
      register_triage(triage={"vitals":vitals,"anthropometrics":anthrops},initial=True)
        
    #TRIAGE
    if selected_service["type"] == "triage":
      vitals = {
        "visit_id":visit_data["visit_id"].lower(),
        "vitals_id":f"{visit_data['visit_id'].lower()}vs1",
        "payment":{
          "visit_id":visit_data["visit_id"].lower(),
          "payment_id":f"{visit_data['visit_id'].lower()}vs1pay1",
          "payment_mode":visit_data["payment_mode"].lower(),
          "cost":service_prices[f"{visit_data['payment_mode']}_{visit_data['package']}".lower()]/2,
          "authorization_no":None,
          "billed":True
        }
      }
      anthrops = {
        "visit_id":self.visit_data["visit_id"].lower(),
        "anthropometrics_id":f"{self.visit_data['visit_id'].lower()}anp1",
        "payment":{
          "visit_id":self.visit_data["visit_id"].lower(),
          "payment_id":f"{self.visit_data['visit_id'].lower()}anp1pay1",
          "payment_mode":self.visit_data["payment_mode"].lower(),
          "cost":service_prices[f"{visit_data['payment_mode']}_{visit_data['package']}".lower()]/2,
          "authorization_no":None,
          "billed":True
        }
      }
      status = register_visit(visit)
      register_triage({"vitals":vitals,"anthropometrics":anthrops})
      
    #LABWORK
    elif selected_service["type"] == "laboratory":
      pass

    #Notification
    ui.notify(message=status["message"],position=status["position"],type=status["type"])
    
    #UI UPDATE
    if clients:
      self.initial_data()
      self.initial_visits_data()
      _client = [client for client in self.clients if client["client_id"] == visit_data["client_id"]][0]
      self.VisitsPanel(client=_client)
    if appointments:
      self.initial_appointments_data()
      self.Carousel(appointments=True)

  def register_appointment(self,appointment:dict,clients:bool=False,visits:bool=False):
    """Register a new appointment and store data to database"""
    
    appointment["attendee_id"] = get_staff_username(name=appointment["consultant"])

    status = register_appointment(appointment)

    #Notification
    ui.notify(message=status["message"],type=status["type"],position="center")
    
    #UI Update
    self.initial_data()
    self.initial_appointments_data()
    if clients:
      self.Carousel(clients=True)
    if visits:
      self.Carousel(visits=True)
      
  def register_client(self,client:dict,edit:bool=False):
    """A method takes 'client_data' and executes a function from clients.processor module to store client's details in the database."""
    
    #Personal details
    for key,value in client.items():
      if type(value) == str:
        client[key] = value.lower()
    #Next of kin details
    if client["kin"]["first_name"]:
      for key,value in client["kin"].items():
        if type(value) == str:
          client["kin"][key] = value.lower()
    
    b_day,b_month,b_year = client["birthdate"].split("-")[0],client["birthdate"].split("-")[1],client["birthdate"].split("-")[2]
    client["birthdate"] = datetime.fromisoformat(f"{b_year}-{b_month}-{b_day}")
    client["mobile"] = f"{client["dial_code"]}{client["mobile_no"]}"
    
    if edit:
      status = update_client(client=client)
    else:
      status = register_client(client=client)

    ui.notify(message=status["message"],type=status["type"],position=status["position"])
    
    self.initial_data()
    _client = get_client(client["client_id"])
    self.ClientMiniDisplay(client=_client,clients=True)

  def process_payment(self,service,complete:bool=False):
    pay_data = {
      "payment_id":service["payment"]["payment_id"],
      "visit_id":service["visit_id"],
      "consultation":True if "triages" in service else False,
      "triages":service["triages"] if "triages" in service else None,
      "paid_amount":service["payment"]["cost"],
      "billed_amount":0,
      "refunded_amount":0,
      "cancelled":False
    }
    status = update_payment(pay_data)

    ui.notify(message=status["message"],type=status["type"],position=status["position"])
    
    #UI Update
    self.initial_data()
    self.initial_visits_data()

    visit =[visit for visit in [client for client in self.clients if client["client_id"] == int(pay_data["visit_id"].split("v")[0])][0]["visits"] if visit["visit_id"] == pay_data["visit_id"]][0]
    services = self.formatted_services(self._services(visit)["services"]["all"])
    self.PaymentsPanel(services=services)

  #GENERAL DISPLAYS
  def Carousel(self,clients:str|None=None,visits:bool=False,appointments:bool=False):
    #DATA
    value = "visits" if visits else "clients" if clients else "appointments"
    #UI
    self.master_container.clear()
    with self.master_container.classes(remove="bg-sky-100"):
      with ui.carousel(value=value).style(add="overflow-y:hidden;").props(add="animated swipeable transition-prev='jump-right' transition-next='jump-left' transition-duration='300'").classes(add="grow flex flex-col q-pa-none p-0.5 w-full bg-inherit rounded shadow-md shadow-blue-500 animate__animated animate__fadeIn") as carousel:
        with carousel.add_slot("default"):
          with ui.carousel_slide(name="appointments").classes(add="q-pa-none p-0.5 gap-0 w-full h-full rounded light-blur"):
            with html.div().classes(add="w-full h-full ring-md ring-blue-500 shadow-md shadow-blue-500 blue-blur relative") as self.appointments_pad:
              AppointmentsManager(user=self.user,parent=self)

          with ui.carousel_slide(name="clients").classes(add="q-pa-none p-0.5 gap-0 w-full h-full rounded light-blur"):
            with html.div().classes(add="w-full h-full flex flex-col rounded"):
              #Header
              with html.header().classes(add="w-full pl-0 pr-2 flex flex-col lg:flex-row justify-between items-center rounded-t bg-[#07004d]"):
                with html.section().classes(add="w-full lg:w-fit flex flex-row gap-1 items-center"):
                  #Registration button
                  #Small screen                  
                  ui.button(text="",icon="fa-solid fa-circle-plus fa-md",color="",on_click=lambda e:self.ClientMiniDisplay(clients=True)).classes(add="lg:hidden bg-inherit p-1 text-lg text-yellow-500")
                  #Large screen
                  ui.button(text="",icon="fa-solid fa-circle-plus fa-md",color="",on_click=lambda e:self.ClientDialog(clients=True)).classes(add="lg-show bg-inherit p-1 text-lg text-yellow-500")

                  ui.label(text="CLIENTS DASHBOARD").style(add="text-shadow:2px 2px #505050;").classes(add="grow bg-inherit text-yellow-500 text-xl lg:text-2xl text-bold")
                  ui.button(icon="fa-solid fa-arrows-rotate",color="",on_click=self.reload_clients).classes(add="hidden size-8 shadow-sm shadow-yellow-500 rounded-full bg-inherit hover:scale-[0.9] text-yellow-500 text-bold justify-self-end self-end lg:hidden")
                with html.section().classes(add="w-full lg:w-fit bg-inherit"):
                  with html.div().classes(add="px-3") as self.stats_panel:
                    self.ClientsStats()
                  with html.div().classes(add="hidden items-center bg-inherit"):
                    ui.button(icon="fa-solid fa-rotate",color="").classes(add="bg-inherit text-yellow-500 text-bold justify-self-end lg:hidden")
              #Body
              with html.div().classes(add="grow w-full bg-white rounded-b flex flex-col"):
                #For large screens
                with html.div().classes(add="w-full grow lg-show") as self.clients_panel:
                  self.ClientsAggrid(self.clients)
                #For small screens
                with html.div().classes(add="grow w-full lg:hidden") as self.clients_mini_panel:
                  self.ClientsMiniView(clients=self.clients)
                
          with ui.carousel_slide(name="visits").classes(add="q-pa-none gap-0 w-full h-full rounded light-blur"):
            with html.div().classes(add="w-full h-full flex flex-col rounded"):
              #Header
              with html.header().classes(add="w-full pl-0 pr-2 flex flex-col lg:flex-row justify-between items-center rounded-t bg-[#07004d]"):
                with html.section().classes(add="w-full lg:w-fit flex flex-row gap-1 items-center"):
                  ui.label(text="ACTIVE VISITS").style(add="p-1 text-shadow:2px 2px #505050;").classes(add="grow bg-inherit text-yellow-500 text-2xl text-bold")
                  ui.button(icon="fa-solid fa-arrows-rotate",color="",on_click=self.reload_clients).classes(add="hidden size-8 shadow-sm shadow-yellow-500 rounded-full bg-inherit hover:scale-[0.9] text-yellow-500 text-bold justify-self-end self-end lg:hidden")
              #Body
              with html.div().classes(add="grow w-full bg-white rounded-b flex flex-col"):
                #For large screens
                with html.div().classes(add="w-full grow lg-show") as self.visits_panel:
                  self.VisitsAggrid(self.visits)
                #For small screens
                with html.div().classes(add="grow w-full lg:hidden") as self.visits_mini_panel:
                  self.VisitsMiniView(visits=self.visits)

      #Controls
      with html.div().classes(add="w-full py-3 flex flex-row justify-center gap-5 lg:gap-7"):
        ui.toggle(options=["clients","visits","appointments"]).props(add="glossy size='lg' toggle-color='bg-inherit' toggle-text-color='sky-500' text-color='yellow-500'").classes(add="lg-show bg-[#07004d] rounded-full ring-1 ring-blue-500 shadow-md shadow-sky-600 text-bold").bind_value(carousel)
    
  def ClientsStats(self):
    """"""
    self.stats_panel.clear()
    with self.stats_panel:
      with html.span().classes(add="flex flex-row gap-3 animate__animated animate__zoomIn"):
        #Visits
        with ui.label("VISITS").classes(add="text-sm lg:text-base text-yellow-500 text-bold"):
          ui.label(str(len(self.today_visits))).classes(add="ml-1 inline text-sky-300")
        #Consultations
        with ui.label("APPOINTMENTS").classes(add="text-sm lg:text-base text-yellow-500 text-bold"):
          ui.label(str(len(self.today_appointments))).classes(add="ml-1 inline text-sky-300")

  def ClientsAggrid(self,clients:list[dict]):
    """Displays the AGGrid of clients in large screens (>992px)"""

    if len(clients) > 0:
      self.clients_panel.clear()
      with self.clients_panel:
        ui.aggrid(
          {
            "columnDefs":[
              {"headerName":"S/N","field":"sno","width":75},
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
                "sno":clients.index(client) + 1,
                "client_id":client["client_id"],
                "name":f"{client['first_name'].capitalize()} {client['middle_name'].capitalize()} {client['last_name'].capitalize()}",
                "age":f"{format_age(client['birthdate']).split(' ')[0]} {format_age(client['birthdate']).split(' ')[1]}",
                "gender":client["gender"].capitalize(),
                "address":client["address"].title(),
                "payment_mode":client["payment_mode"].upper(),
                "card_no":client["card_no"] if client["card_no"] else "---",
                "last_visit":self.last_visit(client)["duration"],
                "status":self.last_visit(client)["status"].capitalize(),
              } for client in clients
            ],
          },theme="quartz"
        ).classes(add="w-full h-full animate__animated animate__fadeIn animate__slow").on("cellClicked",lambda e:self.ClientDialog(client=[client for client in self.clients if client["client_id"] == e.args["data"]["client_id"]][0],clients=True))
    else:
      with html.div().classes(add="w-full h-full py-[20%] sm:py-[10%] text-bold text-center"):
        ui.label("No Clients registered!").classes(add="text-2xl text-gray-500 text-bold")
        ui.label("Start registering by click a 'NEW' button on the left side").classes(add="italic text-xl text-sky-600")
  
  def VisitsAggrid(self,visits:list[dict]):
    #DATA
    visits = sorted(visits,key=lambda e:e["start_time"],reverse=True)
    #UI
    self.visits_panel.clear()
    with self.visits_panel:
      self.visit_aggrid = ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/N","field":"sno","width":50},
            {"headerName":"VISIT ID","field":"visit_id","filter":"agTextColumnFilter","width":100},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter"},
            {"headerName":"AGE","field":"age","width":100},
            {"headerName":"GENDER","field":"gender","width":100},
            {"headerName":"VISIT DURATION","field":"duration","width":150},
            {"headerName":"PAYMENT","field":"payment","width":100},
            {"headerName":"STATUS","field":"status","width":100,"cellClassRules":{
              "text-green-600 text-bold":"x == 'Active'",
              "text-red-600 text-bold":"x == 'Inactive'"
              }
            },
            {"headerName":"PAY STATUS","field":"payment_status","width":120,"cellClassRules":{
              "text-green-600 text-bold":"x == 'Paid'",
              "text-red-600 text-bold":"x == 'Not Paid'",
              "text-purple-600 text-bold":"x == 'Billed'",
              "text-yellow-500 text-bold":"x =='Partial'",
              "text-gray-400 text-bold":"x == 'Cancelled'"
              }}
          ] ,
          "rowData":[
            {
              "sno":visits.index(visit) + 1,
              "visit_id":visit["visit_id"].upper(),
              "name":visit["client_name"].title(),
              "age":f"{format_age(visit['client_birthdate']).split(' ')[0]} {format_age(visit['client_birthdate']).split(' ')[1]}",
              "gender":visit["client_gender"].capitalize(),
              "duration":f"{format_age(visit['start_time'])}",
              "payment":visit["payment_mode"].upper(),
              "auth_no":visit["consultations"][0]["payment"]["authorization_no"] if visit["consultations"] and visit["consultations"][0]["payment"]["payment_mode"].upper() != "CASH" else "---",
              "status":"Active" if visit["is_active"] else "Inactive",
              "payment_status":self.payment_status(visit).title()
            } for visit in visits
          ]
        },theme="quartz"
      ).classes(add="w-full h-full animate__animated animate__fadeIn animate__slow").on("cellClicked",lambda e:self.ClientDialog(client=[client for client in self.clients if e.args["data"]["visit_id"].lower().startswith(str(client['client_id']))][0],visits=True))

  def ClientDialog(self,client:dict|None=None,clients:bool=False,visits:bool=False):
    """"""
    #DATA
    if client:
      details = {
        "name":f"{client['first_name']} {client['middle_name']} {client['last_name']}",
        "short_name":f"{client['first_name'].capitalize()} {client['middle_name'][0].capitalize() if client['middle_name'] else ''}. {client['last_name'].capitalize()}",
        "age":format_age(client["birthdate"]),
        "gender":client["gender"],
        "address":client["address"],
        "last_visit":self.last_visit(client)["duration"] if client["visits"] else self.last_visit(client)["time"]
      }
    #FXS
    def close_dialog():
      self.Carousel(clients=clients,visits=visits)
    #UI
    with ui.dialog().props(add=f"transition-show='jump-up' transition-hide='jump-down' transition-duration='100'") as self.client_dialog,html.div().style(add="min-width:90%;min-height:75%;").classes(add="bg-sky-50 ring-1 ring-blue-400 shadow-blue-400 shadow-md flex flex-col"):
      #Header
      with html.div().classes(add="bg-harmony px3-0.5 p-1 flex flex-row justify-between"):
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
      with html.div().classes(add="grow w-full h-full flex flex-col gap-3") as self.client_details_panel:
        #Client
        if client:
          self.VisitsPanel(client=client)
        #New client
        else:
          self.ClientDetailsForm(client=client)
    
    self.client_dialog.open()
  
  #SMALL SCREEN DISPLAYS
  def ClientsMiniView(self,clients:list[dict]):
    """Displays the details of clients for small screens"""
    #MODS
    def StatusDot(client):
      """A function to return a styled icon based on status of client's last visit"""

      status = self.last_visit(client)["status"]
      return f"<span class='fa-solid fa-circle { 'text-green-600' if status == 'active' else 'text-red-600'}'></span>"
    
    def GenderIcon(client):
      """Returns a styled gender icon based on client's gender"""

      genders = {"male":"mars","female":"venus"}
      colors = {"male":"sky-600","female":"pink-600"}
      return f"<span class='fa-solid fa-{genders[client['gender'].lower()]} text-{colors[client['gender'].lower()]}'></span>"

    #UI
    if len(clients) > 0:
      self.clients_mini_panel.clear()
      with self.clients_mini_panel:
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
                "client_id":client["client_id"],
                "name":f"{client['first_name'].capitalize()} {client['middle_name'].capitalize()} {client['last_name'].capitalize()}",
                "age":f"{format_age(client['birthdate']).split(' ')[0]} {format_age(client['birthdate']).split(' ')[1]}",
                "gender":GenderIcon(client)
              } for client in clients
            ],
          },
          html_columns=[0,3],
          theme="quartz"
        ).classes(add="w-full h-full animate__animated animate__fadeIn animate__slow").on("cellClicked",lambda e:self.ClientMiniDisplay(client=[client for client in self.clients if client["client_id"] == e.args["data"]["client_id"]][0],clients=True))
    else:
      with html.div().classes(add="w-full h-full flex flex-col justify-center items-center"):
        with html.div().classes(add="flex flex-col justify-center items-center"):
          ui.label("No Clients registered!").classes(add="text-xl text-gray-500 text-bold")
          ui.html("<em >Start registering by clicking <strong class='fa-solid fa-circle-plus fa-lg mx-1 text-yellow-600' ></strong> on CLIENTS DASHBOARD</em>").classes(add="text-base text-gray-400 italic")
  
  def VisitsMiniView(self,visits:list[dict]):
    """Displays the details of visits for small screens"""
    #DATA
    visits = visits
    #MODS
    def GenderIcon(visit):
      """Returns a styled gender icon based on client's gender"""

      genders = {"male":"mars","female":"venus"}
      colors = {"male":"sky-600","female":"pink-600"}
      return f"<span class='fa-solid fa-{genders[visit['client_gender'].lower()]} text-{colors[visit['client_gender'].lower()]}'></span>"

    #UI
    if len(visits) > 0:
      self.visits_mini_panel.clear()
      with self.visits_mini_panel:
        ui.aggrid(
          {
            "columnDefs":[
              {"headerName":"CLIENT ID","field":"client_id","filter":"agTextColumnFilter","floatingFilter":True,"width":150},
              {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","floatingFilter":True,"width":300},
              {"headerName":"","field":"gender","align":"left","width":75},
              {"headerName":"AGE","field":"age","width":150}
            ],
            "rowData":[
              {
                "client_id":visit["client_id"],
                "name":f"{visit['client_name'].title()}",
                "age":f"{format_age(visit['client_birthdate']).split(' ')[0]} {format_age(visit['client_birthdate']).split(' ')[1]}",
                "gender":GenderIcon(visit)
              } for visit in visits
            ],
          },
          html_columns=[2],
          theme="quartz"
        ).classes(add="w-full h-full animate__animated animate__fadeIn animate__slow").on("cellClicked",lambda e:self.ClientMiniDisplay(client=[client for client in self.clients if client["client_id"] == e.args["data"]["client_id"]][0],visits=True))
    else:
      with html.div().classes(add="w-full h-full flex flex-col justify-center items-center"):
        with html.div().classes(add="flex flex-col justify-center items-center"):
          ui.label("No Visits Currently!").classes(add="text-xl text-gray-500 text-bold")
    
  def ClientDetailsForm(self,client:dict|None=None):
    """A method to display dialog with registration form"""
    
    #DATA
    self.client_data = {
      "client_id":client["client_id"] if client else self.format_client_id(),
      "payment_mode":client["payment_mode"] if client else PAYMENT_MODES[0],
      "card_no":client["card_no"] if client else "",
      "first_name":client["first_name"].capitalize() if client else "",
      "middle_name":client["middle_name"].capitalize() if client else "",
      "last_name":client["last_name"].capitalize() if client else "",
      "birthdate":client["birthdate"].strftime("%d-%m-%Y") if client else "",
      "gender":client["gender"].capitalize() if client else "",
      "marital_status":client["marital_status"].capitalize() if client else "",
      "occupation":client["occupation"].capitalize() if client else "",
      "address":client["address"].capitalize() if client else "",
      "dial_code":"+255",
      "mobile_no":client["mobile"][4:] if client else "",
      "kin":{"first_name":"","last_name":"","relation":"","dial_code":"+255","mobile_no":""}
    }
    insurance_data = {
      "scheme":self.client_data["payment_mode"] if client else PAYMENT_MODES[0],
      "id_type":"",
      "id_number":self.client_data["card_no"] if client else ""
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
          self.scheme_selectable = ui.select(options=PAYMENT_MODES,label="SCHEME",value=insurance_data["scheme"].upper()).props(add="bordered").classes(add="col-span-3 md:col-span-1 shadow-md shadow-[#07004d] px-2 bg-white rounded-sm text-lg").bind_value_to(insurance_data,"scheme").bind_value_to(self.client_data,"payment_mode")
          #ID Type
          ui.select(options=ID_MODES,label="ID TYPE",value=ID_MODES[0]).props(add="bordered").classes(add="col-span-3 md:col-span-1 shadow-md shadow-[#07004d] px-3 bg-white rounded-sm text-lg").bind_value_to(insurance_data,"id_type").bind_visibility_from(self.scheme_selectable,"value",lambda v: v.lower() != "cash")
          #ID No input
          self.id_number_input = ui.input(label="ID NUMBER").props(add="bordered").classes(add="col-span-4 md:col-span-3  shadow-md shadow-[#07004d] bg-white rounded-sm px-3 text-lg").bind_value(self.client_data,"card_no").bind_visibility_from(self.scheme_selectable,"value",lambda v: v.lower() != "cash")
          #Data Button
          ui.button(text="FETCH CLIENT",on_click=lambda e:self.fetch_insured_client(insurance_data)).props(add="bordered glossy type='button'").classes(add="col-span-2 md:col-span-1 bg-harmony text-yellow-8 text-base text-bold").bind_visibility_from(self.scheme_selectable,"value",lambda v: v.lower() != "cash")

        #Personal details
        with html.form().props(add="").classes(add="lg:col-start-1 lg:col-span-3 grow flex flex-col gap-3 w-full p-2 animate__animated animate__fadeIn"):
          #Client ID
          with ui.label("Client ID").props(add="glossy").classes(add="w-full rounded-sm shadow-md shadow-[#07004d] p-2 small-caps text-2xl text-bold text-gray-500"):
            ui.label().style(add="text-shadow:1px 1px #505050;").classes(add="inline ml-2").bind_text(self.client_data,"client_id")
          #Details
          with html.div().classes(add="w-full grid grid-cols-2 lg:grid-cols-3 gap-3"):
            #First Name
            ui.input(label="First Name",placeholder="Enter First Name").props(add="bordered").classes(add="shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value(self.client_data,"first_name")
            #Middle Name
            ui.input(label="Middle Name",placeholder="Enter Middle Name").props(add="bordered").classes(add="shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value(self.client_data,"middle_name")
            #Last Name
            ui.input(label="Last Name",placeholder="Enter Last Name").props(add="bordered").classes(add="shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value(self.client_data,"last_name")
            #Birthdate
            with ui.input(label="Birthdate").props(add="bordered readonly").classes(add="shadow-md shadow-[#07004d] bg-white rounded px-2 text-lg") as bdate_display:
              with ui.dialog() as calendar:
                ui.date(mask="DD-MM-YYYY",on_change=lambda e:calendar.close()).props(add=f"bordered square today-btn color='harmony' event-color='orange' first-day-of-week='1' navigation-max-year-month='{datetime.now().strftime("%Y/%m")}'").bind_value(bdate_display).bind_value(self.client_data,"birthdate")
                with bdate_display.add_slot("append"):
                  ui.icon("fas fa-cake-candles",color="pink-500").on("click",calendar.open)
            #Gender
            ui.select(options=["Male","Female"],value="Female",label="Gender").props(add="bordered").classes(add="shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value(self.client_data,"gender")
            #Marital status
            ui.select(options=MARITAL_STATUSES,label="Marital Status",value=MARITAL_STATUSES[0]).props(add=" bordered").classes(add="shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value(self.client_data,"marital_status")
            #Occupation
            ui.select(options=OCCUPATIONS,label="Occupation",with_input=True).props(add="bordered").classes(add="shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value(self.client_data,"occupation")
            #Address
            ui.input(label="Address",placeholder="Enter client's location").props(add="bordered type='text'").classes(add="shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value(self.client_data,"address")
            #Mobile No
            with ui.input(label="Mobile No",placeholder="eg.787000111").props(add="bordered type='tel' minlength=9 maxlength=9").classes(add="shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value(self.client_data,"mobile_no") as phone_input:
              with phone_input.add_slot("prepend"):
                ui.select(options=[f"+{code}" for code in range(1,260)],value="+255",with_input=True).classes(add="w-16 bg-white my-1 text-lg text-bold").bind_value(self.client_data["kin"],"dial_code")

        #Next of Kin Details
        with html.div().classes(add="lg:col-start-3 hidden w-full p-2 flex flex-col gap-3"):
          ui.label("NEXT OF KIN").classes(add="w-full rounded-sm shadow-md shadow-[#07004d] p-2 small-caps text-2xl text-bold text-gray-500")
          with html.div().classes(add="w-full grid grid-cols-2 gap-3"):
            #First Name
            ui.input(label="First Name",placeholder="Enter First Name").props(add="bordered").classes(add="shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value(self.client_data["kin"],"first_name")
            #Last Name
            ui.input(label="Last Name",placeholder="Enter Last Name").props(add="bordered").classes(add="shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value(self.client_data["kin"],"last_name")
            #Relationship
            ui.select(options=RELATIONSHIP,label="Relation",with_input=True).props(add="bordered").classes(add="shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value(self.client_data["kin"],"relation")
            #Mobile No
            with ui.input(label="Mobile No",placeholder="eg.787000111").props(add="type='tel' minlength=9 maxlength=9").classes(add="shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value(self.client_data["kin"],"mobile_no") as phone_input:
              with phone_input.add_slot("prepend"):
                ui.select(options=[f"+{code}" for code in range(1,260)],value="+255",with_input=True).classes(add="w-16 bg-white my-1 text-lg text-bold").bind_value(self.client_data["kin"],"dial_code")

        #Buttons
        with html.div().classes(add="lg:col-span-3 w-full flex flex-row justify-center p-2 rounded-sm shadow-sm shadow-[#07004d]"):
          ui.button(text="SAVE EDITED CLIENT" if client else "REGISTER CLIENT",on_click=lambda e:self.register_client(client=self.client_data,edit=True if client else False),color="#07004d").props(add="glossy type='button'").classes(add="text-yellow-500 text-bold text-lg rounded-md ring-1 ring-blue-400 shadow-md shadow-blue-400")
    
  def ClientMiniDisplay(self,client:dict|None=None,clients:bool=False,visits:bool=False):
    """Displays client details for registered client and registration form for new client"""
    #DATA
    if client:
      details = {
        "name":f"{client['first_name'].capitalize()} {client['middle_name'].capitalize()} {client['last_name'].capitalize()}",
        "short_name":f"{client['first_name'].capitalize()} {client['middle_name'][0].capitalize()}. {client['last_name'].capitalize()}",
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
    visits = client["visits"]
    if visits:
      visits = sorted(client["visits"],key=lambda e:e["start_time"],reverse=True)
      last_visit = visits[0]
      details = {
        "name":last_visit["client_name"],
        "age":format_age(last_visit["client_birthdate"]),
        "gender":last_visit["client_gender"],
        "address":last_visit["client_address"],
        "last_visit":f"{format_age(last_visit['start_time'])} ago"
      }

    #UI
    #Button
    self.edit_view_button_panel.clear()
    with self.edit_view_button_panel:
      ui.button(color="",icon="fas fa-user-pen fa-xl",on_click=lambda e:self.ClientDetailsForm(client=client)).props(add="compact").classes(add="bg-inherit text-yellow-500 hover:scale-[1.1] animate__animated animate__zoomIn")
    #Preview visits
    self.client_details_panel.clear()
    with self.client_details_panel.classes(add="flex flex-col gap-2"):
      #Visits
      if visits:
        with html.fieldset().classes(add="grow w-full flex flex-col rounded bg-inherit p-0.5 ring-1 ring-blue-100 shadow-md shadow-sky-500 animate__animated animate__fadeIn"):
          html.legend(f"{len(client['visits'])} VISIT{'' if len(client['visits']) == 1 else 'S'}").classes(add="rounded bg-sky-100 px-3 text-[#07004d] text-xl text-bold")
          with ui.scroll_area().classes(add="grow w-full bg-sky-50 rounded-b") as self.visits_exapansions_panel:
            #Visits
            for visit in visits:
              with html.div().classes(add="w-full") as self.visit_expansion_panel:
                self.VisitExpansion(visit)
      else:
        with html.div().classes(add="grow w-full flex flex-row justify-center items-center shadow-sm shadow-[#07004d]"):
          ui.label("This client has no recorded visits here!").classes(add="bg-inherit text-gray-400 text-bold text-xl")
      
      #Buttons
      with html.div().classes(add="rounded-b w-full flex flex-row justify-center gap-5 p-2 animate__animated animate__fadeIn"):
        if not visits or not last_visit["is_active"]:
          ui.button(text="new visit",icon="fas fa-circle-plus fa-xl",color="#07004d",on_click=lambda e:self.NewVisitDialog(client=client,clients=True)).props(add="bordered dense glossy").classes(add="rounded shadow-md shadow-[#07004d] text-sky-300 text-xl text-bold")    #New Visit
        ui.button(text="appointment",icon="fas fa-circle-plus fa-lg",color="#07004d",on_click=lambda e:self.NewAppointmentDialog(client=client,clients=from_clients,visits=from_visits)).props(add="dense glossy").classes(add="rounded shadow-md shadow-[#07004d] text-sky-300 text-xl text-bold")      #Appointments

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
        text=f"{visit['start_time'].strftime('%d %b %Y %H:%M')}".upper(),
        caption=f"{len(all_services):,.0f} Service{'' if len(all_services) == 1 else 's'} {len(all_services) - len(cancelled_services) } Valid {len(cancelled_services):,.0f} Cancelled",
        group="visits_group"
      ).props(add=f"dense icon='fas fa-notes-medical' header-class='rounded p-1 bg-sky-100 {'bg-sky-100 text-green-600' if visit['is_active'] else 'text-sky-900'}'").classes(add="w-full my-2 bg-sky-50 rounded ring-1 ring-blue-300 shadow-md shadow-blue-400 text-bold text-xl text-black"):
        with html.div().classes(add="w-full grid gap-3 grid-cols-2 lg:grid-cols-5"):
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
            ui.button(text="CONSULTATION",color="").props(add=f"bordered glossy dense unelevated padding='0px 0px' icon-right='fa-regular {'fa-circle-check' if consultation['initiated'] else 'fa-circle-xmark'} fa-xs' padding='5px 5px'").classes(add=f"w-full bg-harmony p-0 rounded-md text-{'green-500' if consultation['initiated'] else 'red-500'} font-semibold text-xl")
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
  
  def NewVisitDialog(self,client:dict,appointment_id:str|None=None,appointments:bool=False,clients:bool=False):
    """Shows a dialog for initiating or ending visit"""
    #DATA
    details = {
      "name":f"{client['first_name']} {client['middle_name']} {client['last_name']}",
      "short_name":f"{client['first_name']} {client['middle_name'][0]}. {client['last_name']}",
      "age":format_age(client["birthdate"],short=True),
      "gender":client["gender"],
      "address":client["address"],
      "last_visit":self.last_visit(client)["duration"] if client["visits"] else self.last_visit(client)["time"]
    }
    visit_data = {
      "client_id":client["client_id"],
      "visit_id":f"{client['client_id']}v{self.last_visit(client)['visit_id_index'] + 1 if client['visits'] else 1}",
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

    payment_options = ["CASH"] if client["payment_mode"].lower() == "cash" else [client["payment_mode"].upper(),"CASH"]
    #MODS
    def get_authorization_number():
      """Retrives authorization number for insured clients and inserts it into visit_data"""

      auth = authorize_visit({"scheme":visit_data["payment_mode"],"card_no":visit_data["card_no"]})

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
    with ui.dialog().props(add="transition-show='jump-down' transition-hide='jump-up' transition-duration='500'") as self.new_visit_dialog,html.div().style(add="min-width:50%;min-height:30%;").classes(add="shadow-md shadow-[#07004d] p-0.5 bg-sky-50 flex flex-col gap-0.5"):
      #Header
      with html.div().classes(add="w-full flex flex-row bg-[#07004d]"):
        with html.div().classes(add="grow bg-inherit"):
          ClientCard(details=details)
        #Close Button
        with html.div().classes(add="flex flex-col justify-center"):
          ui.button(icon="fa-solid fa-circle-xmark",color="",on_click=self.new_visit_dialog.close).classes(add="bg-inherit text-red-600 text-bold text-base hover:scale-[0.9]")
      #Visit details
      with html.div().classes(add="grow w-full flex flex-col gap-3 p-1 bg-sky-100"):
        #Services
        with html.div().classes(add="w-full grid grid-cols-2 gap-3 animate__animated animate__fadeIn"):
          #Service
          with html.div().classes(add="col-span-2 w-full grid grid-cols-2 gap-3"):
            #Service type
            self.service_category = ui.select(options=list(self.services),label="SERVICE",value="Consultation",on_change=lambda e:ServiceOptions(e.value)).classes(add="shadow-md shadow-[#07004d] bg-sky-50 rounded-sm px-2 text-lg").bind_value_to(visit_data,"service")
            #Service Options
            with html.div().classes(add="") as self.service_options_pad:
              ui.select(options=[_service.title() for _service in self.services["Consultation"][1]],value=self.services["Consultation"][1][0].title(),label="CONSULTANT").classes(add="shadow-md shadow-[#07004d] bg-sky-50 rounded-sm px-2 text-lg").bind_value_to(visit_data,"service_option")
            
          #Payment
          with html.div().classes(add="col-span-2 w-full grid grid-cols-2 gap-3"):
            payment_mode = ui.select(options=payment_options,value=payment_options[0],label="PAYMENT MODE").props(add="bordered").classes(add="shadow-md shadow-[#07004d] bg-sky-50 rounded px-2 text-lg").bind_value_to(visit_data,"payment_mode")   #payment mode
            ui.select(options=PAYMENT_PACKAGES,value=PAYMENT_PACKAGES[0],label="PACKAGE").props(add="bordered ").classes(add="shadow-md shadow-[#07004d] bg-sky-50 rounded px-2 text-lg uppercase").bind_value_to(visit_data,"package")
            ui.input(label="CARD/NIDA NO",value=client["card_no"]).props(add="type='text' bordered readonly").bind_visibility_from(payment_mode,"value",lambda v:v != "CASH").classes(add="bg-white shadow-md shadow-[#07004d] rounded-sm px-2 text-lg").bind_value_to(visit_data,"card_no")     #Card No
            authorize_button = ui.button(text="authorize",color="#07004d",on_click=get_authorization_number).props(add="bordered glossy").bind_visibility_from(payment_mode,"value",lambda v:v != "CASH").classes(add="rounded shadow-md shadow-[#07004d] text-sky-300 text-lg lg:text-xl text-bold")   #Authorize button
            self.auth_number = ui.input(label="AUTHORIZATION NO").props(add="bordered glossy readonly").bind_visibility_from(payment_mode,"value",lambda v:v != "CASH").classes(add="col-span-2 w-3/4 justify-self-center bg-white shadow-md shadow-[#07004d] rounded-sm px-2 text-xl text-green-700").bind_value(visit_data,"authorization_no")          #Authorization Number
          
        #Action buttons
        ui.separator().classes(add="col-span-6 w-full")
        with html.span().classes(add="col-span-6 w-full p-2 flex flex-row justify-center animate__animated animate__fadeIn"):
          #Initiate visit
          ui.button(text="initiate visit",color="#07004d",on_click=lambda e:self.initiate_visit(visit_data=visit_data,clients=clients,appointments=appointments)).props(add="bordered").classes(add="w-auto shadow-md shadow-[#07004d] text-sky-300 text-xl lg:text-2xl text-bold")

    self.new_visit_dialog.open()

  def PaymentsDialog(self,services):
    #DATA
    if not services:
      ui.notify(message="No payments requested!",type="warning",position="top")
      return
  
    #FXS
    def close_dialog():
      client =  [client for client in self.clients if client["client_id"] == int(services[0]["visit_id"].split("v")[0])][0]
      self.VisitsPanel(client=client)
      self.payments_dialog.close()
      
    #UI
    with ui.dialog().props(add=f"transition-show='jump-up' transition-hide='jump-down' transition-duration='500'") as self.payments_dialog,html.div().style(add="min-width:100%;").classes(add="bg-sky-50 ring-1 ring-blue-400 shadow-blue-400 shadow-md"):
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
    payable_services = [service for service in services if service["payment"]["payment_mode"].lower() == "cash" and not (service["payment"]["paid"] or service["cancelled"])]
    paid_services = [service for service in services if service["payment"]["paid"]]
    total_bill = sum([service["payment"]["cost"] for service in services if not service["cancelled"]])
    paid_bill = sum([service["payment"]["paid_amount"] for service in paid_services])
    pending_bill = total_bill - paid_bill
    ticked_services = []
    #FXS
    def update_cost(payment_id,cost):
      b4,aft = 'a','b'
      for service in payable_services:
        if service["payment"]["payment_id"] == payment_id:
          service["payment"]["cost"] = cost

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
          if service["payment"]["payment_id"] == ticked_service:
            ticked_services.append(service)
      else:
        for service in ticked_services:
          if service["payment"]["payment_id"] == ticked_service:
            ticked_services.remove(service)
      #UI
      selected_pays.clear()
      with selected_pays:
        if ticked_services:
          ui.label(f"{sum([service['payment']['cost'] for service in ticked_services]):,.2f} TZS").classes(add="inline ml-2 text-purple-600 animate__animated animate__fadeIn")
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
      with ui.scroll_area().classes(add="grow w-full h-[400px] pb-2 bg-white rounded ring-1 ring-blue-200 shadow-md shadow-blue-500 animate__animated animate__fadeIn animate__slow"):
        for service in services:
          with html.div().classes(add=f"w-full p-0.5 rounded grid grid-cols-7 gap-0.5 content-center {'bg-gray-200 ring-1 ring-gray-300 shadow-md shadow-gray-500 text-red-600' if service['cancelled'] else 'bg-sky-50 ring-1 ring-blue-300 shadow-md shadow-sky-500'}"):
            #Service
            with html.div().classes(add="col-span-7 lg:col-span-3 flex flex-row gap-1"):
              if service["cancelled"]:
                ui.chip(icon="fas fa-ban",color="").classes(add="bg-inherit mx-0 ml-1 px-0")
              #Checkbox
              ui.checkbox(text=f"{services.index(service) + 1}.",on_change=lambda e:pick_ticked_service(
                ticked_service=e.sender.parent_slot.parent.slots["default"].children[1].slots["default"].children[0].props["id"],
                ticked=e.value
              )).props(add="dense").classes(add=f"{'hidden' if service['payment']['payment_mode'] != 'cash' or service['payment']['paid'] or service['cancelled'] else ''} text-sky-700 text-bold text-md lg:text-lg")
              #Name
              with html.div().props(add=f"").classes(add="grow bg-inherit flex flex-row items-center"):
                html.em(f"{service['name']}".upper()).props(add=f"id={service['payment']['payment_id']} name={'consult' if 'consultant_id' in service else ''}").classes(add=f"bg-inherit {'text-gray-600' if service['cancelled'] else 'text-sky-700'} text-bold text-md lg:text-lg")
              
            #Details
            with html.div().classes(add=f"col-span-7 lg:col-span-4 grid grid-cols-7 gap-1"):
              #Timeframe
              ui.chip(text=f"{format_age((service['service_time']),short=True) } ago",icon="fa-regular fa-clock fa-lg",text_color=f"{'gray-600' if service['cancelled'] else 'sky-900'}",color="").props(add="dense").classes(add="mx-0 col-span-2 lg:col-span-1 bg-inherit text-md lg:text-base font-semibold")
              #Amount
              if service["payment"]["cost"]:
                ui.chip(text=f"{service['payment']['cost']:,.2f} TZS",icon="fas fa-coins",color="",text_color=f"{'gray-600' if service['cancelled'] else 'amber-10'}").props(add="dense").classes(add=f"mx-0 col-span-2 lg:col-span-2 lg:justify-self-end bg-inherit text-md lg:text-base text-bold text-wrap")
              else:
                with html.span().classes(add="col-span-2 w-full justify-self-end text-end"):
                  serv = [s for s in get_services() if s["name"] == service["name"]][0]
                  min_cost,max_cost = int(serv["payment"]["min_cash"]),int(serv["payment"]["max_cash"])+1
                  html.i().props(add=f"id={service['payment']['payment_id']}").classes(add="hidden")
                  ui.select(options=[i for i in range(min_cost,max_cost,10000)],with_input=True,on_change=lambda e:update_cost(
                    payment_id=e.sender.parent_slot.parent.slots["default"].children[0].props["id"],
                    cost=e.value
                  )).props(add=f"dense hide-dropdown-icon").classes(add=f"justify-self-end w-[60%] bg-white ring-2 ring-blue-300 rounded pl-2 text-md lg:text-xl")
              #Payment Status
              if not service["cancelled"]:
                ui.chip(text="Paid" if service["payment"]["paid"] else "Billed" if service["payment"]["billed"] else "Not Paid",icon=f"{'fa-regular fa-circle-check' if service['payment']['paid'] else 'fa-solid fa-file-invoice' if service['payment']['billed'] else 'fa-regular fa-circle-xmark'} fa-lg",text_color="green" if service["payment"]["paid"] else "purple" if service["payment"]["billed"] else "red",color="").props(add="dense").classes(add=f"mx-0 col-span-2 lg:col-span-1 justify-self-center lg:justify-self-end bg-inherit text-md lg:text-base text-bold")

              #Pay button
              ui.button(text="pay",color="#07004d",on_click=lambda e:self.process_payment(
                service=[service for service in services if service["payment"]["payment_id"] == e.sender.parent_slot.parent.parent_slot.parent.slots["default"].children[0].slots["default"].children[1].slots["default"].children[0].props["id"]][0]
              )).props(add="dense glossy").classes(add=f"{'hidden' if service['payment']['payment_mode'].lower() != 'cash' or service['payment']['paid'] or service['cancelled'] else ''} col-span-1 lg:col-span-3 justify-self-end w-12 lg:w-20 ring-1 ring-blue-200 text-sky-300 text-md text-bold")
              #Payment information
              if service["payment"]["paid"]:
                #Payment Processor
                ui.chip(text=f"{get_staff(self.user.username)['last_name']}".title(),icon="fa-solid fa-hospital-user fa-lg",text_color="green-600",color="").props(add="dense").classes(add="mx-0 col-span-1 justify-self-center lg:justify-self-end bg-inherit text-md lg:text-base text-bold")
                #Timeframe
                ui.chip(text=f"{format_age(service['payment']['payment_time'])} ago",icon="fa-regular fa-clock",text_color="green-600",color="").props(add="dense").classes(add="col-span-3 lg:col-span-2 lg:justify-self-end rounded-sm mx-0  bg-inherit text-md lg:text-base text-bold")
                
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
  
  def NewAppointmentDialog(self,client:dict,clients:bool=False,visits:bool=False):
    """Shows a dialog for initiating or ending visit"""
    #DATA
    details = {
      "name":f"{client['first_name']} {client['middle_name']} {client['last_name']}",
      "short_name":f"{client['first_name']} {client['middle_name'][0]}. {client['last_name']}",
      "age":format_age(client["birthdate"],short=True),
      "gender":client["gender"],
      "address":client["address"],
      "last_visit":self.last_visit(client)["duration"] if client["visits"] else self.last_visit(client)["time"]
    }
    
    appointment_data = {
      "consultant":"",
      "date":"",
      "client_id":client["client_id"],
      "appointment_id":f"{client['client_id']}a{len(client['appointments'])+1}"
    }
    
    _tomorrow = datetime.now() + timedelta(days=1)
    if _tomorrow.month >9:
      tomorrow = f"{_tomorrow.year}/{_tomorrow.month}/{_tomorrow.day}"
    else:
      tomorrow = f"{_tomorrow.year}/0{_tomorrow.month}/{_tomorrow.day}"
    
    #UI
    with ui.dialog().props(add="transition-show='jump-down' transition-hide='jump-up' transition-duration='500'") as self.new_appointment_dialog,html.div().classes(add="shadow-md shadow-[#07004d] p-0.5 bg-sky-50 flex flex-col gap-0.5"):
      #Header
      with html.div().classes(add="w-full flex flex-row bg-[#07004d]"):
        with html.div().classes(add="grow bg-inherit"):
          ClientCard(details=details)
        #Close Button
        with html.div().classes(add="flex flex-col justify-center"):
          ui.button(icon="fa-solid fa-circle-xmark",color="",on_click=self.new_appointment_dialog.close).classes(add="bg-inherit text-red-600 text-bold text-base hover:scale-[0.9]")
      #Appointment
      with html.div().classes(add="grow w-full flex flex-col gap-1"):
        ui.date(value=datetime.now()).props(add=f"bordered square today-btn color='harmony' event-color='orange' first-day-of-week='1' navigation-min-year-month='{_tomorrow.strftime("%Y/%m")}'").classes(add="w-full").bind_value_to(appointment_data,"date")
        #Buttons
        with html.div().classes(add="w-full px-0.5 py-1 grid grid-cols-3 gap-1"):
          ui.select(label="CONSULTANT",options=self.consultants,value=self.consultants[0] if self.consultants else None,with_input=True).bind_value_to(appointment_data,"consultant").classes(add="col-span-2 shadow-md shadow-[#07004d] bg-white rounded px-2 text-lg")
          ui.button(text="plan",color="#07004d",on_click=lambda e:self.register_appointment(appointment=appointment_data,clients=clients,visits=visits)).props(add="dense glossy").classes(add="ring-1 ring-blue-400 shadow-sm shadow-blue-400 text-sky-300 text-bold text-lg")
        
    self.new_appointment_dialog.open()

  
class ReportsDisplay():
  """A class to display reports"""

  def __init__(self):
    #Weekly view data
    self.target_year = datetime.now().year
    self.today = datetime.now().date()
    self.last_week = self.today + timedelta(days=-7)

    #Monthly view data
    self.picked_year,self.picked_month = datetime.now().year,list(calendar.month_name[1:])[int(datetime.now().month)-1]
    #Toggle button
    with html.div().classes(add="w-full py-2 flex flex-row-reverse justify-center"):
      self.duration_toggle = ui.toggle(options=["daily","weekly","monthly","annual"],value="daily",on_change=lambda e:self.load_ranged_report(e.value)).classes(add="bg-gray-200 text-bold")
    
    #Default selection panel
    with html.div().classes(add="w-full flex flex-row justify-center") as self.selection_panel:
      if self.duration_toggle.value == "daily":
        with ui.input(label="Pick date",value=datetime.now().strftime("%Y-%m-%d"),on_change=lambda e:self.load_daily_report(e.value)).props(add="readonly").classes(add="bg-sky-50 rounded-sm m-1 pl-20 text-lg") as self.default_picked_date:
          with ui.dialog() as daily_calendar:
            ui.date(value=datetime.now(),on_change=daily_calendar.close).bind_value(self.default_picked_date)
          with self.default_picked_date.add_slot("prepend"):
            ui.icon("fas fa-calendar-check fa-xl",color="sky-500").on("click",daily_calendar.open)
      
      if self.duration_toggle.value == "weekly":
        now = datetime.now()
        today = now.date().strftime("%Y-%m-%d")
        last_week = (now.date() + timedelta(days=-7)).strftime("%Y-%m-%d")
        input_range:str = f"{last_week} | {today}"
        #Selection panel
        with self.selection_panel:
          #Date range picker
          with ui.input(label="Date range",value=input_range,on_change=lambda e:self.load_weekly_report(e.value)).props(add="range readonly").classes(add="bg-sky-50 rounded m-1 px-20 text-lg") as date_range_input:
            with ui.dialog() as weekly_calendar:
              ui.date(value=datetime.now(),on_change=weekly_calendar.close).props(add="range").bind_value(
                date_range_input,
                forward=lambda x:f'{x["from"]} | {x["to"]}' if x else None,
                backward=lambda x:{'from':x.split(' | ')[0],'to':x.split(' | ')[1]} if ' | ' in (x or '') else None
              )
            with date_range_input.add_slot("prepend"):
              ui.icon("fas fa-calendar-check fa-xl",color="sky-500").on("click",weekly_calendar.open)
      
      if self.duration_toggle.value == "monthly":
        
        with ui.button_group():
          ui.select(label="Year",options=[2025,2024,2023],on_change=self.load_monthly_report).classes(add="px-2 text-lg").bind_value(self,"picked_year")
          ui.select(label="Month",options=list(calendar.month_name)[1:],on_change=self.load_monthly_report).classes(add="px-2 text-lg").bind_value(self,"picked_month")

      if self.duration_toggle.value == "annual":
        
        ui.select(label="Year",options=[2025,2024,2023],on_change=self.load_annual_report).classes(add="w-44 px-2 text-lg").bind_value(self,"picked_year")        
    
    #Default report panel
    with html.div().classes(add="w-full h-full") as self.report_panel:
      if self.duration_toggle.value == "daily":
        ReportFrame(start_date=self.default_picked_date.value,end_date=self.default_picked_date.value)
      if self.duration_toggle.value == "weekly":
        self.report_panel.clear()
        with self.report_panel:
          ReportFrame(start_date=last_week,end_date=today)
      if self.duration_toggle.value == "monthly":
        #Data
        start_date = f"{datetime.now().strftime('%Y-%m')}-01"
        end_date = f"{datetime.now().strftime('%Y-%m')}-{calendar.monthrange(datetime.now().year,datetime.now().month)[1]}"
        #UI
        ReportFrame(start_date=start_date,end_date=end_date)
      if self.duration_toggle.value == "annual":
        #Data
        start_date = f"{self.picked_year}-01-01"
        end_date = f"{self.picked_year}-12-31"
        #UI
        ReportFrame(start_date=start_date,end_date=end_date)
      
  
  def load_ranged_report(self,duration:str):
    """A method which changes the default display of the page based on the value of 'duration'"""

    self.selection_panel.clear()
    self.report_panel.clear()
    #Selection
    if duration == "daily":
      #Default selection panel
      with self.selection_panel:
        with ui.input(label="Pick date",value=datetime.now().strftime("%Y-%m-%d"),on_change=lambda e:self.load_daily_report(e.value)).props(add="readonly").classes(add="bg-sky-50 rounded-sm m-1 px-2 text-lg") as self.picked_date:
          with ui.dialog() as daily_calendar:
            ui.date(value=datetime.now(),on_change=daily_calendar.close).bind_value(self.picked_date)
          with self.picked_date.add_slot("prepend"):
            ui.icon("fas fa-calendar-check fa-xl",color="sky-500").on("click",daily_calendar.open)
      #Default report panel
      with self.report_panel:
        ReportFrame(start_date=self.picked_date.value,end_date=self.picked_date.value)
    
    if duration == "weekly":
      now = datetime.now()
      today = now.date().strftime("%Y-%m-%d")
      last_week = (now.date() + timedelta(days=-7)).strftime("%Y-%m-%d")
      input_range:str = f"{last_week} | {today}"
      #Selection panel
      with self.selection_panel:
        #Date range picker
        with ui.input(label="Date range",value=input_range,on_change=lambda e:self.load_weekly_report(e.value)).props(add="range readonly").classes(add="bg-sky-50 rounded m-1 px-20 text-lg") as date_range_input:
          with ui.dialog() as weekly_calendar:
            ui.date(value=datetime.now(),on_change=lambda e:weekly_calendar.close()).props(add="range").bind_value(
              date_range_input,
              forward=lambda x:f'{x["from"]} | {x["to"]}' if x else None,
              backward=lambda x:{'from':x.split(' | ')[0],'to':x.split(' | ')[1]} if ' | ' in (x or '') else None
            )
          with date_range_input.add_slot("prepend"):
            ui.icon("fas fa-calendar-check fa-xl",color="sky-500").on("click",weekly_calendar.open)
      
      #Default weekly report
      self.report_panel.clear()
      with self.report_panel:
        ReportFrame(start_date=last_week,end_date=today)
    
    if duration == "monthly":
      with self.selection_panel:
        with ui.button_group():
          ui.select(label="Year",options=[2025,2024,2023],on_change=self.load_monthly_report).classes(add="px-2 text-lg").bind_value(self,"picked_year")
          ui.select(label="Month",options=list(calendar.month_name)[1:],on_change=self.load_monthly_report).classes(add="px-2 text-lg").bind_value(self,"picked_month")
      
      with self.report_panel:
        #Data
        start_date = f"{datetime.now().strftime('%Y-%m')}-01"
        end_date = f"{datetime.now().strftime('%Y-%m')}-{calendar.monthrange(datetime.now().year,datetime.now().month)[1]}"
        #UI
        ReportFrame(start_date=start_date,end_date=end_date)

    if duration == "annual":
      with self.selection_panel:
        ui.select(label="Year",options=[2025,2024,2023],on_change=self.load_annual_report).classes(add="w-44 px-2 text-lg").bind_value(self,"picked_year")
      
      with self.report_panel:
        #Data
        start_date = f"{self.picked_year}-01-01"
        end_date = f"{self.picked_year}-12-31"
        #UI
        ReportFrame(start_date=start_date,end_date=end_date)
  
  def load_daily_report(self,date:str):
    """A method to load daily report based on 'date' value"""

    self.report_panel.clear()
    with self.report_panel:
      ReportFrame(start_date=date,end_date=date)
  
  def load_weekly_report(self,date_range:str):
    """A method to load weekly report"""

    if date_range:
      dates:list[str] = date_range.split(" | ")

      self.report_panel.clear()
      with self.report_panel:
        ReportFrame(start_date=dates[0],end_date=dates[1])
  
  def load_monthly_report(self):
    """Displays monthly report based on ' '"""

    #Data
    _month = list(calendar.month_name).index(self.picked_month)
    if _month >=10:
      start_date = f"{self.picked_year}-{_month}-01"
      end_date = f"{self.picked_year}-{_month}-{calendar.monthrange(self.picked_year,_month)[1]}"
    else:
      start_date = f"{self.picked_year}-0{_month}-01"
      end_date = f"{self.picked_year}-0{_month}-{calendar.monthrange(self.picked_year,_month)[1]}"
        
    #UI
    try:
      self.report_panel.clear()
      with self.report_panel:
        ReportFrame(start_date=start_date,end_date=end_date)
    except:
      return
    
  def load_annual_report(self):
    """A method that loads a ReportFrame object with annual statistics calculated from 'self.picked_year'"""

    #Data
    start_date = f"{self.picked_year}-01-01"
    end_date = f"{self.picked_year}-12-31"
    #UI
    try:
      self.report_panel.clear()
      with self.report_panel:
        ReportFrame(start_date=start_date,end_date=end_date)
    except:
      return


