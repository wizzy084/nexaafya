"""A module to analyze the retrieved dicons based on the request provides in .routes.py"""

#GENERAL IMPORTS
import simple_icd_10 as icd_10

#PROJECT IMPORTS
from ._snippets import *


##
def get_staffs(private:bool=False):
  """Retrieves rows data from 'users' table and format them into a list of dictionaries"""

  with Session(database_engine) as session:
    db_users:list[User] = list(session.exec(select(User)).all())
    users = sorted([unmodel_user(db_user) for db_user in db_users],key=lambda e:e["registered_on"])
    #For full access
    if private:
      return users
    #For public limited access
    else:
      for user in users:
        user.pop("password")
      return users

def get_staff(username:str,private:bool=False):
  """"""
  staff = None

  if private:
    for _staff in get_staffs(private=True):
      if _staff["username"] == username:
        staff = _staff
  else:
    for _staff in get_staffs():
      if _staff["username"] == username:
        staff = _staff
    
  
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
