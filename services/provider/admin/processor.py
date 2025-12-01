"""A module to analyze the retrieved dicons based on the request provides in .routes.py"""

#GENERAL IMPORTS
from collections import namedtuple
import simple_icd_10 as icd_10

#FastAPI & SQLModel IMPORTS
from sqlmodel import Session,select

#PROJECT IMPORTS
from services.provider.configs import database_engine
from ._snippets import *

##
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
      if staff["first_name"] == first_name and staff["last_name"] == last_name:
        if role:
          if role in staff["roles"]:
            return staff["username"]
        else:
          return staff["username"]
  else:
    return None

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

def get_services():
  """Retrieves rows data from 'service' table and format them into a list of dictionaries"""

  with Session(database_engine) as session:
    db_services:list[Service] = list(session.exec(select(Service)).all())

    return [unmodel_service(db_service) for db_service in db_services]

def get_formulary():
  """Retrieves rows data from 'formulary' table and format them into a list of dictionaries"""

  with Session(database_engine) as session:
    db_formulary:list[Formulary] = list(session.exec(select(Formulary)).all())

    return [unmodel_formulary(db_medicine) for db_medicine in db_formulary]

def get_requisitions():
  """"""
  with Session(database_engine) as session:
    db_requisitions:list[Requisition] = list(session.exec(select(Requisition)).all())

    requisitions = [unmodel_requisition(db_requisition) for db_requisition in db_requisitions]

  return requisitions

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
    db_medicines:list[Medicine] = list(session.exec(select(Medicine)).all())

    return [unmodel_medicine(db_medicine) for db_medicine in db_medicines if db_medicine.active]

def get_pricings(all:bool=False):
  """Returns a list of dictionaries containing price details.By default only active prices are returned"""

  with Session(database_engine) as session:
    if all:
      return [unmodel_pricing(db_pricing) for db_pricing in list(session.exec(select(Pricing)))]
    else:
      return [unmodel_pricing(db_pricing) for db_pricing in list(session.exec(select(Pricing).where(Pricing.active)))]

def get_template_services(verbose:bool=False) -> list:
  """Returns list of template services to be registered in the system"""
  from .template import services
  if verbose:
    return []
  else:
    return [service["name"].title() for service in services]

def get_formulary_medicines(verbose:bool=False) -> list:
  """Returns list of template medicines to be registered in the system"""
  from .template import medicines
  if verbose:
    return []
  else:
    return [medicine["name"].title() for medicine in medicines]

def get_template_service(service:str) -> dict:
  """Return a namedtuple with details of service"""

  with Session(database_engine) as session:
    db_service:Service = session.exec(select(Service).where(Service.name == service.lower())).first()
    return unmodel_service(db_service)

def get_formulary_medicine(medicine:str) -> dict:
  """Return a namedtuple with details of medicine"""

  with Session(database_engine) as session:
    db_medicine:Formulary = session.exec(select(Formulary).where(Formulary.name == medicine.lower())).first()
    return unmodel_formulary(db_medicine)


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

