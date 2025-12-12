"""A module to analyze the retrieved dicons based on the keyword provided by the routes"""

#GENERAL IMPORTS
import json
from collections import namedtuple
from datetime import datetime,timedelta

#SQLMODEL IMPORTS
from sqlalchemy import Boolean,text
from sqlalchemy.engine.base import Engine
from sqlmodel import Session,SQLModel,func,select

#DICONS IMPORTS
from ._snippets import *
from services.provider.configs import database_engine



#FORMATTING
def format_client_id() -> int:
  """Returns an interger representing new client id"""

  id_primer = datetime.now().strftime("%y%m")

  with Session(database_engine) as session:
    latest_id = session.exec(select(Client.client_id).order_by(Client.created_on.desc()).limit(1)).first()
    id_str = str(latest_id) if latest_id else None
    
    #Other Clients
    if id_str and id_str[:4] == id_primer:
      id_end = int(id_str[4:]) + 1

      if id_end < 10:
        new_id_end = f"00{id_end}"
      elif id_end < 100:
        new_id_end = f"0{id_end}"
      else:
        new_id_end = str(id_end)

      return int(f"{id_primer}{new_id_end}")
      
    #First client
    else:
      return int(f"{id_primer}001")

    

#FROM DATABASE
def get_clients(short:bool=False):
  """A function retrieves rows in 'client' table and restructured into python dictionaries"""

  with Session(database_engine) as session:
    db_clients:list[Client] = list(session.exec(select(Client)).all())
    clients = [unmodel_client(db_client) for db_client in db_clients]

    return clients

def get_client(client_id):
  """retrieves a single client from the database by its client_id and returns it as a dictionary"""

  with Session(database_engine) as session:
    db_client:Client = list(session.exec(select(Client).where(Client.client_id == client_id)))[0]
    client = unmodel_client(db_client)

    return client
  
def get_latest_client_id():
  with Session(database_engine) as session:
    latest_client_id = list(session.exec(text("SELECT client_id FROM client ORDER BY client.client_id DESC")))[0][0]

    return str(latest_client_id)

def get_visits():
  """A function retrieves rows in 'visit' table and restructure into python dictionaries"""

  with Session(database_engine) as session:
    db_visits = list(session.exec(select(Visit)).all())
    visits = [unmodel_visit(db_visit) for db_visit in db_visits]

    return visits

def get_active_visits():
  """Returns a list of dictionaries containing details of active visits in the database"""

  with Session(database_engine) as session:
    db_active_visits:list[Visit] = list(session.exec(select(Visit).where(Visit.cancelled == False)))

    return [unmodel_visit(db_active_visit) for db_active_visit in db_active_visits]

def get_appointments():
  """A function that retrives appointment details"""

  with Session(database_engine) as session:
    db_appointments:list[Appointment] = list(session.exec(select(Appointment)).all())
    appointments = [unmodel_appointment(db_appointment) for db_appointment in db_appointments]

    return appointments

def get_new_visits(date:str):
  """pass"""

  hi = [1,2,3,5,6]

  if date == "daily":
    with Session(database_engine) as session:
      db_visits = list((session.exec(select(Visit))).all())
      visits = [unmodel_visit(db_visit) for db_visit in db_visits if db_visit.start_visit_time[:10] == date]
    hi = visits

  return hi

def get_payments():
  """Retrieves rows of 'payment' table and restructures them into python dictionaries"""
  
  with Session(database_engine) as session:
    db_payments = list(session.exec(select(Payment)).all())
    payments = [unmodel_payment(db_payment) for db_payment in db_payments]

    return payments

def get_consultations():
  """Returns a list of dictionaries containing row data from consultation table"""

  with Session(database_engine) as session:
    db_consultations:list[Consultation] = list(session.exec(select(Consultation)).all())

    return [unmodel_consultation(db_consultation) for db_consultation in db_consultations]

def get_specific_complaints(hx_id:str):
  """Retrieves list of complaints stored in the database clinicalhistory table rows at the column labelled chief_complaints"""

  with Session(database_engine) as session:
    db_hx:ClinicalHistory = list(session.exec(select(ClinicalHistory).where(ClinicalHistory.hx_id == hx_id)))[0]
    
    if db_hx.chief_complaints:
      return json.loads(db_hx.chief_complaints)
    else:
      return []

def get_clinical_summary(consultation_id:str):
  """A function to retrieve data from database tables"""

  clinical_summary = []

  with Session(database_engine) as session:
    db_consultation:Consultation = list(session.exec(select(Consultation).where(Consultation.consultation_id == consultation_id)))[0]

    clinical_history:ClinicalHistory = db_consultation.clinical_histories[0]
    
    complaints = json.loads(clinical_history.chief_complaints)

    for complaint in complaints:
      if complaints.index(complaint) == 0:
        clinical_summary.append([complaint,clinical_history.hpi1])
      if complaints.index(complaint) == 1:
        clinical_summary.append([complaint,clinical_history.hpi2])
      if complaints.index(complaint) == 2:
        clinical_summary.append([complaint,clinical_history.hpi3])
  
  return clinical_summary

def get_diagnoses():
  """Retrieves diagnoses from diagnosis database table"""

  with Session(database_engine) as session:
    db_diagnoses:list[Diagnosis] = list(session.exec(select(Diagnosis)).all())
    diagnoses = [unmodel_diagnosis(db_diagnosis) for db_diagnosis in db_diagnoses]

    return diagnoses

def get_active_imagings():
  """Retrieves data from imaging table in the database and returns a list of dictionaries correspondng to the row data"""
  
  with Session(database_engine) as session:
    db_visits:list[Visit] = list(session.exec(select(Visit)).all())
    _imaging_visits = [unmodel_visit(db_visit) for db_visit in db_visits if db_visit.imagings and db_visit.is_active]
    imaging_visits = [
      {
        "client_id":visit["client_id"],
        "visit_id":visit["visit_id"],
        "client_name":visit["client_name"],
        "client_age":format_age(visit["client_birthdate"]),
        "client_gender":visit["client_gender"],
        "client_address":visit["client_address"],
        "request_mode":"Consulted" if visit["consultations"] else "Direct",
        "imagings":visit["imagings"]
      } for visit in _imaging_visits]
    return imaging_visits
    
def get_imagings():

  with Session(database_engine) as session:
    db_imagings:list[Imaging] = list(session.exec(select(Imaging)).all())

    return [unmodel_imaging(db_imaging) for db_imaging in db_imagings]

def get_imaging_visits():
  """Returns row data from visit table with linkage to non-null imaging table associated to it"""

  with Session(database_engine) as session:
    db_visits:list[Visit] = list(session.exec(select(Visit)).all())

    imaging_visits:list[dict] = [unmodel_visit(db_visit) for db_visit in db_visits if db_visit.imagings]

    return imaging_visits

def get_pharmacy_visits():
  """Returns row data from visit table with linkage to non-null medication and medicalitem tables associated to it"""

  pharmacy_visits:list[tuple[str,dict,dict]] = []

  with Session(database_engine) as session:
    db_visits = session.exec(select(Visit).where(Visit.active)).all()
    
    return [unmodel_visit(db_visit) for db_visit in db_visits if db_visit.medications or db_visit.medical_items]

async def get_consultation_diagnoses(consultation_id:str):
  """Retrieves diagnoses associated with consultation"""
  diagnoses = []

  with Session(database_engine) as session:
    db_diagnoses = session.exec(select(Diagnosis).where(Diagnosis.consultation_id == consultation_id.lower())).all()
    if db_diagnoses:
      diagnoses = [unmodel_diagnosis(db_diagnosis) for db_diagnosis in db_diagnoses]

  return diagnoses

def counted_services(payments:list[dict]):
  """A function that returns a dictionary with keys as 'services' and value as the count of such services"""

  services = [{"service":"dentist","amount":0}]

  for payment in payments:
    for service in services:
      if payment["service"] == service["service"]:
        service["amount"] += payment["paid_amount"]
  
  return services

def get_active_visits_with_procedures():
  """Retrieves data from visit table in the database if its linked to non-empty procedure table and returns a list of dictionaries correspondng to the row data"""
  
  with Session(database_engine) as session:
    db_visits = session.exec(select(Visit).where(Visit.active)).all()
    return [unmodel_visit(db_visit) for db_visit in db_visits if db_visit.procedures]    
    
def get_procedures():
  """Retrieved data from rows in procedure table and returns a list of dictionaries"""

  with Session(database_engine) as session:
    db_procedures:list[Procedure] = list(session.exec(select(Procedure)).all())
    procedures = [unmodel_procedure(db_procedure) for db_procedure in db_procedures]

    return procedures

#STATS
def count_today_visits_and_appointments():
  """Returns a namedtuple with two values:visits & appointments"""

  data = {"visits":0,"appointments":0}
  today = namedtuple("Today",["visits","appointments"])

  with Session(database_engine) as session:
    visits_count = session.exec(select(func.count(Visit.visit_id)).where(func.date(Visit.start_time) == datetime.now().date())).one()
    data["visits"] = visits_count if visits_count else 0
  
  with Session(database_engine) as session:
    appointments_count = session.exec(select(func.count(Appointment.appointment_id)).where(func.date(Appointment.appointment_time) == datetime.now().date())).one()
    data["appointments"] = appointments_count if appointments_count else 0
  
  return today(visits=data["visits"],appointments=data["appointments"])
  

#FROM 3RD PARTY APIs
def fetch_insured_client(insurance_data:dict):
  """A function that takes 'insurance_data' and retrieves personal information from relevant APIs"""

  #Do some stuffs

  a = {'payment_mode': 'nhif', 'first_name': 'nadia', 'middle_name': 'wisdom', 'last_name': 'kyando', 'birthdate': '25-12-2025', 'gender': 'female', 'marital_status': 'single', 'occupation': 'child', 'mobile_no': '712887977','card_no':'629302834273'}
  
  return a

def authorize_visit(auth_data:dict):
  """Returns authorization status and authorization number from APIs"""
  auth = {"auth_no":""}
  #
  if True:
    #Do some stuffs
    auth["status"],auth["message"],auth["type"],auth["auth_no"] = True,"Authorized succesfully!","positive","759435015"
  else:
    #Check some stuffs
    auth["status"],auth["message"],auth["type"] = False,"Authorized Failed!\nContact insurance service provider for assistance","negative"


  return auth



