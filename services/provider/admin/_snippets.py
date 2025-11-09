"""A module for base operations neccesary in processing semi during database updating and database querrying."""

#GENERAL IMPORTS
import json,os
from collections import namedtuple
from typing import Any
from dotenv import load_dotenv
from sqlmodel import Session,select



#PROJECT IMPORTS
from .models import *
from services.provider.configs import database_engine


#ENVIRONMENT VARIABLES
load_dotenv()

SUPER_ADMIN=os.getenv("SUPER_ADMIN")
SUPER_PASSKEY=os.getenv("SUPER_PASSKEY")



#API
def is_db_user(username:str) -> Any:
  """Returns True if the user is in the database, False otherwise"""

  with Session(database_engine) as session:
    db_user = session.exec(select(User).where(User.username == username)).first()

    return db_user

def is_superadmin(username:str):
  """Returns True if the user is the superadmin, False otherwise"""
  
  return username == SUPER_ADMIN

def set_guest_in_dropdown(user:User|None=None) -> str:
  """A function to set 'Guest' as username if no user:User is provided in AdminProfile function in widgets.py"""
  
  if user:
    return user.username
  else:
    return "Guest"
  
def set_admin_icon_in_dropdown(user:User|None=None)-> str:
  """A function to set 'user-slash' icon if no user:user is provided in AdminProfile function in widgets.py"""

  if user:
    return "user"
  else:
    return "user-large-slash"

def database_is_present() -> bool:
  """A function returns 'True' boolean value if database session is present, otherwise returns 'False'"""

  with Session(database_engine) as session:
    try:
      users = session.exec(select(User))
      return True
    except:
      return False

def db_display_change(changed_value:str,target:Any,target_value_options:list[str]):
  """A function to change 'target_value' based on the value of 'changed_value'"""

  if changed_value.startswith("remote"):
    target.set_text(target_value_options[1])

  elif changed_value.startswith("local"):
    target.set_text(target_value_options[0])

  else:
    return None


###UNMODELS
def unmodel_login(db_login:Login):
  """A function to convert a Login model instance into a dictionary"""

  return {
    "login_id":db_login.login_id,
    "username":db_login.username,
    "logged":db_login.logged,
    "login_time":db_login.login_time,
    "logout_time":db_login.logout_time,
    "login_ip":db_login.login_ip,
    "logout_ip":db_login.logout_ip
  }

def unmodel_user(db_user:User):
  """A function to convert a User model instance into a dictionary"""

  return {
    "username":db_user.username,
    "title":db_user.title,
    "qualification":db_user.qualification,
    "designation":db_user.designation,
    "first_name":db_user.first_name,
    "middle_name":db_user.middle_name,
    "last_name":db_user.last_name,
    "birthdate":db_user.birthdate,
    "gender":db_user.gender,
    "email":db_user.email,
    "mobile":db_user.mobile,
    "password":db_user.password,
    "photo":db_user.photo,
    "is_super":db_user.is_super,
    "registered_on":db_user.registered_on,
    "roles":json.loads(db_user.roles) if db_user.roles else [],
    "active":db_user.active,
    "suspended":db_user.suspended,
    "logins":[unmodel_login(db_login) for db_login in db_user.logins]
  }

def unmodel_service(db_service:Service):
  """Converts data from service table row(s) into dictionary"""

  return {
    "service_id":db_service.service_id,
    "name":db_service.name,
    "alternative_name":db_service.alternative_name,
    "type":db_service.type,
    "active":db_service.active,
    "schemes":[unmodel_scheme(db_scheme) for db_scheme in db_service.schemes]
  }

def unmodel_formulary(db_formulary:Formulary):
  """"""
  return {
    "medicine_id":db_formulary.medicine_id,
    "name":db_formulary.name,
    "type":db_formulary.type,
    "category":db_formulary.category,
    "drug_class":db_formulary.drug_class,
    "fda_pregnancy_category_1":db_formulary.fda_pregnancy_category_1,
    "fda_pregnancy_category_2":db_formulary.fda_pregnancy_category_2,
    "fda_pregnancy_category_3":db_formulary.fda_pregnancy_category_3,
    "prescribable":db_formulary.prescribable,
    "prescription_level":db_formulary.prescription_level,
    "active":db_formulary.active,
    "schemes":[unmodel_scheme(db_scheme) for db_scheme in db_formulary.schemes],
    "inventory":[unmodel_inventory(db_inventory) for db_inventory in db_formulary.inventory]
  }

def unmodel_inventory(db_inventory:Inventory):
  """"""
  inventory = namedtuple("InventoryEntry",["medicine_id","invoice","issuer","receiver","issuer_previous_amount","issuer_current_amount","receiver_previous_amount","receiver_current_amount","received","transfer","dispensed","count","default","date"])
  
  return inventory(
    medicine_id = db_inventory.medicine_id,
    invoice = db_inventory.invoice,
    issuer = db_inventory.issuer,
    receiver = db_inventory.receiver,
    issuer_previous_amount = db_inventory.issuer_previous_amount,
    issuer_current_amount = db_inventory.issuer_current_amount,
    receiver_previous_amount = db_inventory.receiver_previous_amount,
    receiver_current_amount = db_inventory.receiver_current_amount,
    received = db_inventory.received,
    transfer = db_inventory.transfer,
    count = db_inventory.count,
    default = db_inventory.default,
    dispensed = db_inventory.dispensed,
    date = db_inventory.date
  )

def unmodel_scheme(db_scheme:Scheme):
  """"""
  return {
    "medicine_id":db_scheme.medicine_id,
    "service_id":db_scheme.service_id,
    "scheme_name":db_scheme.scheme_name,
    "scheme_item_code":db_scheme.scheme_item_code,
    "active":db_scheme.active,
    "restricted":db_scheme.restricted,
    "prices":[unmodel_pricing(db_pricing) for db_pricing in db_scheme.prices]
  }

def unmodel_pricing(db_pricing:Pricing):
  """"""
  return {
    "scheme_id":db_pricing.scheme_id,
    "logger":db_pricing.logger,
    "log_date":db_pricing.log_date,
    "active":db_pricing.active,
    "copayment":db_pricing.copayment,
    "price_range":db_pricing.price_range,
    "min":db_pricing.min,
    "max":db_pricing.max,
    "standard":db_pricing.standard,
    "priority":db_pricing.priority,
    "topup":db_pricing.topup
  }

def unmodel_icd10_diagnosis(db_diagnosis:ICD10Diagnosis):
  """A function to convert data from rows in ICD10Diagnosis table into dictionary"""

  return {
    "code":db_diagnosis.code,
    "name":db_diagnosis.name
  }

def unmodel_icd11_diagnosis(db_diagnosis:ICD11Diagnosis):
  """A function to convert data from rows in ICD11Diagnosis table into dictionary"""

  return {
    "code":db_diagnosis.code,
    "name":db_diagnosis.name
  }

def unmodel_medicine(db_medicine:Medicine) -> dict[str,Any]:
  """A function to convert a Medicine model instance into a dictionary"""

  return {
    "medicine_id":db_medicine.medicine_id,
    "requisition_id":db_medicine.requisition_id,
    "requisition_medicine_id":db_medicine.requisition_medicine_id,
    "name":db_medicine.name,
    "type":db_medicine.type,
    "category":db_medicine.category,
    "drug_class":db_medicine.drug_class,
    "fda_pregnancy_category_1":db_medicine.fda_pregnancy_category_1,
    "fda_pregnancy_category_2":db_medicine.fda_pregnancy_category_2,
    "fda_pregnancy_category_3":db_medicine.fda_pregnancy_category_3,
    "prescription_level":db_medicine.prescription_level,
    "cancelled":db_medicine.cancelled,
    "cancelled_by":db_medicine.cancelled_by,
    "cancelled_on":db_medicine.cancelled_on,
    "ordered":db_medicine.ordered,
    "ordered_by":db_medicine.ordered_by,
    "ordered_on":db_medicine.ordered_on,
    "order_unit":db_medicine.order_unit,
    "order_unit_size":db_medicine.order_unit_size,
    "ordered_amount":db_medicine.ordered_amount,
    "ordered_price":db_medicine.ordered_price,
    "unit_price":db_medicine.unit_price,
    "received":db_medicine.received,
    "received_by":db_medicine.received_by,
    "received_on":db_medicine.received_on,
    "received_amount":db_medicine.received_amount,
    "received_price":db_medicine.received_price,
    "rejected":db_medicine.rejected,
    "rejected_amount":db_medicine.rejected_amount,
    "rejected_price":db_medicine.rejected_price,
    "brand_name":db_medicine.brand_name,
    "mfg_date":db_medicine.mfg_date,
    "manufacturer":db_medicine.manufacturer,
    "batch_no":db_medicine.batch_no,
    "expire_date":db_medicine.expire_date,
    "active":db_medicine.active,
    "store_balance":db_medicine.store_balance,
    "amc":db_medicine.average_monthly_consumption,
    "average_daily_consumption":db_medicine.average_daily_consumption,
    "dispensing_balance":db_medicine.dispensing_balance,
    "physical_count":db_medicine.physical_count,
    "count_unit":db_medicine.count_unit,
    "counted_by":db_medicine.counted_by,
    "physical_count_date":db_medicine.physical_count_date,
    "initial_store_balance":db_medicine.initial_store_balance
  }

def unmodel_stationery(db_stationery:Stationery):
  """A function to convert a Stationery model instance into a dictionary"""

  return {
    "stationery_id":db_stationery.stationery_id,
    "requisition_id":db_stationery.requisition_id,
    "cancelled":db_stationery.cancelled,
    "cancelled_by":db_stationery.cancelled_by,
    "cancelled_on":db_stationery.cancelled_on,
    "ordered":db_stationery.ordered,
    "ordered_by":db_stationery.ordered_by,
    "ordered_on":db_stationery.ordered_on,
    "ordered_amount":db_stationery.ordered_amount,
    "ordered_price":db_stationery.ordered_price,
    "received":db_stationery.received,
    "received_by":db_stationery.received_by,
    "received_on":db_stationery.received_on,
    "received_amount":db_stationery.received_amount,
    "received_price":db_stationery.received_price,
    "rejected":db_stationery.rejected,
    "rejected_amount":db_stationery.rejected_amount,
    "rejected_price":db_stationery.rejected_price,
    "brand_name":db_stationery.brand_name,
    "store_balance":db_stationery.store_balance,
    "average_monthly_consumption":db_stationery.average_monthly_consumption,
    "average_daily_consumption":db_stationery.average_daily_consumption,
    "dispensing_balance":db_stationery.dispensing_balance
  }


def unmodel_requisition(db_requisition:Requisition):
  """Unmodels a requisition object"""

  return {
    "requisition_id":db_requisition.requisition_id,
    "delivery_note_id":db_requisition.delivery_note_id,
    "invoice_id":db_requisition.invoice_id,
    "vendor":db_requisition.vendor,
    "paid":db_requisition.paid,
    "billed":db_requisition.billed,
    "paid_amount":db_requisition.paid_amount,
    "billed_amount":db_requisition.billed_amount,
    "initiated":db_requisition.initiated,
    "cancelled":db_requisition.cancelled,
    "cancelled_by":db_requisition.cancelled_by,
    "cancel_date":db_requisition.cancel_date,
    "placed":db_requisition.placed,
    "received":db_requisition.received,
    "initiation_date":db_requisition.initiation_date,
    "placement_date":db_requisition.placement_date,
    "receive_date":db_requisition.receive_date,
    "initiated_by":db_requisition.initiated_by,
    "placed_by":db_requisition.placed_by,
    "received_by":db_requisition.received_by,
    "closed":db_requisition.closed,
    "medicines":[unmodel_medicine(db_medicine) for db_medicine in db_requisition.medicines],
    "stationeries":[unmodel_stationery(db_stationery) for db_stationery in db_requisition.stationeries]
  }