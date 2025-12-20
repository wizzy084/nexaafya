"""A module to analyze the retrieved dicons based on the request provides in .routes.py"""

#GENERAL IMPORTS
import math,uuid
from collections import namedtuple
from datetime import datetime,timedelta
import simple_icd_10 as icd_10

#FastAPI & SQLModel IMPORTS
from sqlmodel import Session,select,or_

#PROJECT IMPORTS
from ..configs import database_engine
from . import template
from ._snippets import *

##
#Facility
def get_facility_data(minimal:bool=False):
  with Session(database_engine) as session:
    db_facility = unmodel_facility(session.exec(select(Facility)).first())
    if minimal:
      return db_facility._replace(subscriptions=[])
    else:
      return unmodel_facility(db_facility)

def subscription_countdown():
  """Returns number of days remaining between current datetime and 'end_time' value in the facilitysubscription table with with active column set to 't'.If it's past 'now', the negative values will be returned."""
  
  now = datetime.now()

  with Session(database_engine) as session:
    subscription:FacilitySubscription = session.exec(select(FacilitySubscription).where(FacilitySubscription.active).order_by(FacilitySubscription.end_time).limit(1)).first()

    if subscription.end_time >= now:
      return (subscription.end_time - now).days
    else:
      return -(now - subscription.end_time).days

#Staff
def get_staffs(private:bool=False,short:bool=False):
  """Retrieves rows data from 'users' table and format them into a list of dictionaries"""

  users = []
  _shortName = namedtuple("shortName",["username","name","roles"])

  with Session(database_engine) as session:
    db_users:list[User] = list(session.exec(select(User)).all())

    if short:
      users = [_shortName(username=db_user.username,name=f"{db_user.first_name} {db_user.last_name}",roles=db_user.roles) for db_user in db_users]
    
    else:
      users = [unmodel_user(db_user) for db_user in db_users]

      if not private:
        for user in users:
          user._replace(password=None)
  
  return users

def get_staff(username:str,private:bool=False):
  """"""
  staff = None

  with Session(database_engine) as session:
    db_user:User = session.exec(select(User).where(User.username == username.lower())).first()
    staff = unmodel_user(db_user)

    if not private:
      staff = staff._replace(password=None)
    
  return staff
    
def get_staff_username(name:str|None,role:str|None=None):
  """"""
  if name:
    first_name,last_name = name.lower().split(" ")

    for staff in get_staffs():
      if staff.first_name == first_name and staff.last_name == last_name:
        if role:
          if role in staff.roles:
            return staff.username
        else:
          return staff.username
  else:
    return None

#Diagnoses
def get_diagnoses(icd10=True,icd11=False):
  """Returns a list of diagnoses based on version of icd selected"""

  #ICD10Diagnosis
  if icd10:
    codes = icd_10.get_all_codes()
    return [f"{code}:{icd_10.get_description(code)}" for code in codes]
  
  #ICD11Diagnosis
  if icd11:
    with Session(database_engine) as session:
      db_diagnoses:list[ICD11Diagnosis] = list(session.exec(select(ICD11Diagnosis)).all())
      diagnoses = [unmodel_icd11_diagnosis(db_diagnosis) for db_diagnosis in db_diagnoses]
      return [f"{diagnosis['code'].upper()}:{diagnosis['name'].title()}" for diagnosis in diagnoses]

#Services & Medicines
def get_services():
  """Retrieves rows data from 'service' table and format them into a list of dictionaries"""

  with Session(database_engine) as session:
    db_services:list[Service] = list(session.exec(select(Service)).all())

    return [unmodel_service(db_service) for db_service in db_services]

def get_formulary(skim:bool=False):
  """Retrieves rows data from 'formulary' table and format them into a list of dictionaries"""

  medicines = []

  with Session(database_engine) as session:
    db_formulary:list[Formulary] = list(session.exec(select(Formulary)).all())
    medicines = [unmodel_formulary(db_medicine) for db_medicine in db_formulary]

  
  return medicines

def get_requisitions(skim:bool=False):
  """"""
  if skim:
    skimmed_requisitions = {"initiated":[],"ordered":[],"received":[]}
    with Session(database_engine) as session:
      db_requisitions:list[Requisition] = list(session.exec(select(Requisition)).all())
      if db_requisitions:
        requisition_labels = {db_requisition.requisition_id.lower() for db_requisition in db_requisitions}

        for requisition_label in requisition_labels:
          #Stats
          medicines =[unmodel_requisition(db_requisition) for db_requisition in list(filter(lambda requisition:requisition.requisition_id.lower() == requisition_label,db_requisitions))]
          ordered_medicines = [medicine for medicine in medicines if medicine.ordered]
          received_medicines = [medicine for medicine in medicines if medicine.received]
          rejected_medicines = [medicine for medicine in medicines if medicine.rejected]
          
          #STATUSES
          ordered_status = {medicine.requisition_ordered for medicine in medicines}
          received_status = {medicine.requisition_received for medicine in medicines}
          rejected_status = {medicine.requisition_rejected for medicine in medicines}

          req_ordered = True if len(ordered_status) == 1 and list(ordered_status)[0] else False
          req_received = True if len(received_status) == 1 and list(received_status)[0] else False
          req_rejected = True if len(ordered_status) == 1 and list(ordered_status)[0] else False

          if req_received:
            skimmed_requisitions["received"].append(requisition_label)
          elif req_ordered:
            skimmed_requisitions["ordered"].append(requisition_label)
          else:
            skimmed_requisitions["initiated"].append(requisition_label)
    
    return skimmed_requisitions
          
  else:
    _Requisition = namedtuple("_Requisition",["name","invoice","delivery_note","requisition_initiated","requisition_ordered","ordered","ordered_on","ordered_price","requisition_received","received","received_on","received_price","rejected","rejected_price","medicines"])
    requisitions = []

    with Session(database_engine) as session:
      db_requisitions:list[Requisition] = list(session.exec(select(Requisition)).all())
      if db_requisitions:
        requisition_labels = {db_requisition.requisition_id.lower() for db_requisition in db_requisitions}

        for requisition_label in requisition_labels:
          #Stats
          medicines =[unmodel_requisition(db_requisition) for db_requisition in list(filter(lambda requisition:requisition.requisition_id.lower() == requisition_label,db_requisitions))]
          ordered_medicines = [medicine for medicine in medicines if medicine.ordered]
          received_medicines = [medicine for medicine in medicines if medicine.received]
          rejected_medicines = [medicine for medicine in medicines if medicine.rejected]
          
          #STATUSES
          ordered_status = {medicine.requisition_ordered for medicine in medicines}
          received_status = {medicine.requisition_received for medicine in medicines}
          rejected_status = {medicine.requisition_rejected for medicine in medicines}

          req_ordered = True if len(ordered_status) == 1 and list(ordered_status)[0] else False
          req_received = True if len(received_status) == 1 and list(received_status)[0] else False
          req_rejected = True if len(ordered_status) == 1 and list(ordered_status)[0] else False


          requisition = _Requisition(
            name  = requisition_label,
            invoice = received_medicines[0].invoice if received_medicines else None,
            delivery_note = received_medicines[0].delivery_note if received_medicines else None,
            medicines = medicines,
            requisition_initiated = False if (req_ordered or req_received) else True,
            requisition_ordered = req_ordered,
            ordered = len(ordered_medicines),
            ordered_on = ordered_medicines[0].ordered_on if ordered_medicines else None,
            ordered_price = sum([medicine.ordered_price for medicine in ordered_medicines]),
            requisition_received = req_received,
            received = len(received_medicines),
            received_on = received_medicines[0].received_on if received_medicines else None,
            received_price = sum([medicine.received_price for medicine in received_medicines]),
            rejected = len(rejected_medicines),
            rejected_price = sum([medicine.rejected_price for medicine in rejected_medicines])
          )

          requisitions.append(requisition)
    
    return sorted(requisitions,key=lambda req:req.ordered_on,reverse=True)

def get_inventory_balance(medicine_id:str,time:datetime):
  InventoryBalance = namedtuple("InventoryBalance",["main","main_store_log_date","dispensing","dispensing_log_date","total"])

  dispensing_balance,dispensing_log_date = 0,datetime.now()
  main_store_balance,main_store_log_date = 0,datetime.now()

  with Session(database_engine) as session:
    main_inventory = session.exec(select(Inventory).where(Inventory.medicine_id == medicine_id.lower()).where(or_(Inventory.issuer == "main store",Inventory.receiver =="main store")).where(Inventory.date <= time).order_by(Inventory.date.desc())).first()
    dispensing_inventory = session.exec(select(Inventory).where(Inventory.medicine_id == medicine_id.lower()).where(or_(Inventory.issuer == "dispensing",Inventory.receiver =="dispensing")).where(Inventory.date <= time).order_by(Inventory.date.desc())).first()
    
    if main_inventory:
      main_store_balance = main_inventory.issuer_current_amount if main_inventory.issuer == "main store" else main_inventory.receiver_current_amount
      main_store_log_date = main_inventory.date
    if dispensing_inventory:
      dispensing_balance = dispensing_inventory.issuer_current_amount if dispensing_inventory.issuer == "dispensing" else dispensing_inventory.receiver_current_amount
      dispensing_log_date = dispensing_inventory.date
  
  inventory_balance = InventoryBalance(
    main = main_store_balance,
    dispensing = dispensing_balance,
    main_store_log_date = main_store_log_date,
    dispensing_log_date = dispensing_log_date,
    total = main_store_balance + dispensing_balance
  )
  
  return inventory_balance

def get_consumption_data(medicine_id:str):
  """"""
  #Output object
  AverageConsumption = namedtuple("AverageConsumption",["daily","monthly"],defaults=[0,0])
  consumption = {"averages":None,"balance":None}

  #Data
  closing_balance = get_inventory_balance(medicine_id=medicine_id,time=datetime.now())
  closing_balance_time = sorted([time for time in [closing_balance.main_store_log_date,closing_balance.dispensing_log_date]])[1]
  initial_balance = 0
  
  consumption["balance"] = closing_balance

  days = 30
  
  #Scanning to get initial_balance
  with Session(database_engine) as session:
    while days > 0:
      inv_time = datetime.now() - timedelta(days=days)
      
      main_inv = session.exec(select(Inventory).where(Inventory.medicine_id == medicine_id.lower()).where(or_(Inventory.issuer == "main store",Inventory.receiver =="main store")).where(Inventory.date <= inv_time).order_by(Inventory.date.desc())).first()
      disp_inv = session.exec(select(Inventory).where(Inventory.medicine_id == medicine_id.lower()).where(or_(Inventory.issuer == "dispensing",Inventory.receiver =="dispensing")).where(Inventory.date <= inv_time).order_by(Inventory.date.desc())).first()

      if main_inv and disp_inv:
        initial_balance = get_inventory_balance(medicine_id=medicine_id,time=inv_time)
        break
      else:
        days -= 10
  
  #Calculating average consumptions(monthly & daily)
  if initial_balance:
    initial_balance_time = sorted([time for time in [initial_balance.main_store_log_date,initial_balance.dispensing_log_date]])[0]
    days = (closing_balance_time - initial_balance_time).days+1
    months = days/30

    _consumption = initial_balance.total - closing_balance.total
    
    average_daily_consumption = math.ceil(_consumption/days)
    average_monthly_consumption = math.ceil(_consumption/months)

    consumption["averages"] = AverageConsumption(daily=average_daily_consumption,monthly=average_monthly_consumption)

  else:
    consumption["averages"] = AverageConsumption()
  
  return consumption

def get_physical_count(medicine_id,time:datetime):

  with Session(database_engine) as session:
    inv = session.exec(select(Inventory).where(Inventory.medicine_id == medicine_id.lower()).where(Inventory.count).where(Inventory.date <= time).order_by(Inventory.date.desc())).first()
    if inv:
      return unmodel_inventory(inv)
    else:
      return None

async def get_inventory_data(medicine_id:str):
  
  now = datetime.now()

  return {
    "balance":get_inventory_balance(medicine_id=medicine_id,time=now),
    "last_count":get_physical_count(medicine_id=medicine_id,time=now)
  }




def get_medicines():
  """Retrieving data from rows in medicine table and return as list of dictionaries"""

  #Process database
  with Session(database_engine) as session:
    db_medicines:list[Medicine] = list(session.exec(select(Medicine)).all())

    return [unmodel_medicine(db_medicine) for db_medicine in db_medicines]

def get_active_medicines():
  """Returns a list of dictionaries each modelling details of Medicine table row with column active set to True"""

  #Process database
  with Session(database_engine) as session:
    db_medicines:list[Formulary] = list(session.exec(select(Formulary)).all())

    return [unmodel_medicine(db_medicine) for db_medicine in db_medicines if db_medicine.active]

def get_pricings(all:bool=False):
  """Returns a list of dictionaries containing price details.By default only active prices are returned"""

  with Session(database_engine) as session:
    if all:
      return [unmodel_pricing(db_pricing) for db_pricing in list(session.exec(select(Pricing)))]
    else:
      return [unmodel_pricing(db_pricing) for db_pricing in list(session.exec(select(Pricing).where(Pricing.active)))]


##APIiiiishh
async def get_template_payment_schemes():
  return [scheme["name"] for scheme in template.payment_schemes]

async def retrieve_payment_scheme(name:str,medicine=None,service=None):
  if not name:
    return
  
  scheme_names = await get_template_payment_schemes()

  if name not in scheme_names:
    return None
  
  else:
    raw_scheme = [scheme for scheme in template.payment_schemes if scheme["name"].lower() == name][0]
    scheme_id = f"{name}-{medicine['medicine_id'] if medicine else service['service_id']}".lower()

    scheme = {
      "scheme_id":scheme_id,
      "scheme_name":name,
      "medicine_id":medicine["medicine_id"].lower() if medicine else None,
      "service_id":service["service_id"].lower() if service else None,
      "active":True,
      "restricted":False,
      "prices":{
        "scheme_id":scheme_id,
        "copayment":False,
        "price_range":False,
        "min":0.0,
        "max":0.0,
        "standard":0.0,
        "priority":0.0,
        "topup":0.0,
        "active":True
      }
    }
    if name == "cash":
      scheme["scheme_item_code"] = medicine["medicine_id"] if medicine else service["service_id"]
    else:
      scheme["scheme_item_code"] = str(uuid.uuid4()).split("-")[2]

  
  return scheme

def get_template_services(verbose:bool=False) -> list:
  """Returns list of template services to be registered in the system"""
  services = template.services + template.other_services
  if verbose:
    return []
  else:
    return [service["name"].title() for service in services]

def get_formulary_medicines(verbose:bool=False) -> list:
  """Returns list of template medicines to be registered in the system"""
  
  if verbose:
    return []
  else:
    return [medicine["name"].title() for medicine in template.medicines + template.xx]

def get_template_service(service:str) -> dict:
  """Return a namedtuple with details of service"""
  service_str = service
  for service in template.services + template.other_services:
    if service["name"] == service_str.lower():
      return service

def get_formulary_medicine(medicine:str) -> dict:
  """Return a namedtuple with details of medicine"""
  meds = template.medicines + template.xx

  return [med for med in meds if med['name'] == medicine.lower()][0]

def retrieve_updated_prices(data:dict,nhif:bool=False):
  """Retrieves prices of a service from NHIF API"""

  data = data

  if nhif:
    nhif_api_data = None
    data["nhif"] = {
      "service_id":data["service_id"],
      "scheme_id":f"nhif={data['service_id']}",
      "logger":data["logger"],
      "copayment":False,
      "price_range":False,
      "min":0,
      "max":0,
      "standard":0,
      "priority":0,
      "topup":0
    }

  return data

