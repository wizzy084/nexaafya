"""A module for creating and updating rows in the database tables """

#GENERAL IMPORTS
import json
from collections import namedtuple
from sqlmodel import Session,SQLModel,select
from uuid import uuid4

#PROJECT IMPORTS
from services.provider.configs import database_engine
from services.provider.admin import template
from services.provider.clients.models import *
from ._snippets import *



#DATABASE POPULATION
def populate_db():
  #creating database tables
  SQLModel.metadata.create_all(database_engine)

  #Facility
  with Session(database_engine) as session:
    if not session.exec(select(Facility)).first():
      register_facility(template.facility)
  
  with Session(database_engine) as session:
    register_facility_subscription(template.default_subscription)

  #Users
  with Session(database_engine) as session:
    if not session.exec(select(User)).all():
      for user in template.users:
        register_staff(user)
      
  #Initial services
  with Session(database_engine) as session:
    if not session.exec(select(Service)).all():
      for service in template.services:
        register_service(service,default=True)

  #Initial formulary
  with Session(database_engine) as session:
    if not session.exec(select(Formulary)).all():
      register_formulary(template.medicines,default=True)

  #Initial requisition
  with Session(database_engine) as session:
    db_requisitions:list[Requisition] = list(session.exec(select(Requisition)).all())

#REGISTER FUNCTIONS
def register_facility(facility:dict):
  """Model Facility and saves data into facility table in database"""

  db_facility = Facility(
    facility_id = facility["facility_id"],
    name = facility["name"],
    postcode = facility["postcode"],
    category = facility["category"],
    level = facility["level"],
    certifications = json.dumps(facility["certifications"]),
    designations = json.dumps(facility["designations"]),
    primary_roles = json.dumps(facility["primary_roles"]),
    secondary_roles = json.dumps(facility["secondary_roles"]),
    services = json.dumps(facility["services"]),
    medicine_types = json.dumps(facility["medicine_types"]),
    vendors = json.dumps(facility["vendors"]),
    mos = json.dumps(facility["mos"]),
    occupations = json.dumps(facility["occupations"]),
    years_of_existence = json.dumps(facility["years_of_existence"]),
  )

  with Session(database_engine) as session:
    if session.exec(select(Facility).where(Facility.facility_id == db_facility.facility_id)).first():
      return
    else:
      session.add(db_facility)
      session.commit()

def register_facility_subscription(subscription:dict):
  db_facility_subscription = FacilitySubscription(
    facility_id = subscription["facility_id"],
    receipt = subscription["receipt"],
    tier = subscription["tier"],
    cost = subscription["cost"],
    paid_amount = subscription["paid_amount"],
    pending_amount = subscription["pending_amount"],
    end_time = subscription["end_time"]
  )

  with Session(database_engine) as session:
    if session.exec(select(FacilitySubscription).where(FacilitySubscription.receipt == db_facility_subscription.receipt)).first():
      return
    else:
      session.add(db_facility_subscription)
      session.commit()

def register_staff(staff:dict):
  """A function to add a new row in users table and populate it with data from 'staff' dictionary"""

  db_staff = User(
    username = staff["username"],
    title = staff["title"],
    qualification = staff["qualification"],
    designation = staff["designation"],
    first_name = staff["first_name"],
    middle_name = staff["middle_name"],
    last_name = staff["last_name"],
    birthdate = staff["birthdate"],
    gender = staff["gender"],
    password = staff["password"] if "password" in staff else "1234",
    is_super = True if "super" in staff["roles"] else False,
    roles = json.dumps(staff["roles"]),
    registered_on = datetime.now()
  )

  with Session(database_engine) as session:
    if list(session.exec(select(User).where(User.username == db_staff.username)).all()):
      return {"success":True,"message":f"Staff wth username '{db_staff.username}' exists!","type":"info","position":"center"}
    else:
      try:
        session.add(db_staff)
        session.commit()
        return {"success":True,"message":"Successfull registered!","type":"positive","position":"top"}
      except:
        return {"success":False,"message":"Registration failed!","type":"negative","position":"center"}

def register_login(login:dict):
  
  db_login = Login(
    login_id = login["login_id"],
    username = login["username"],
    login_time = datetime.now()
  )

  with Session(database_engine) as session:
    if list(session.exec(select(Login).where(Login.login_id == db_login.login_id)).all()):
      return
    else:
      session.add(db_login)
      session.commit()

def register_service(service:dict,default:bool=False):
  """"""
  #REGISTER SERVICE
  db_service = Service(
    service_id = service["service_id"],
    name = service["name"],
    alternative_name = service["alternative_name"],
    type = service["type"],
    active = True
  )
  
  try:
    with Session(database_engine) as session:
      if list(session.exec(select(Service).where(Service.service_id == db_service.service_id))):
        return {"status":False,"message":"Service already in the database!","type":"info","position":"top"}
      else:
        session.add(db_service)
        session.commit()
    
        #REGISTER PAYMENT SCHEMES
        schemes = service["schemes"]
        for scheme in schemes:
          register_scheme(scheme,default=default)
          
    return {"status":True,"message":"Service successfully added!","type":"positive","position":"top"}
  except:
    return {"status":False,"message":"Service not added!","type":"negative","position":"center"}

def register_formulary(medicines:list[dict],default:bool=False):
  """A function to create row in formulary table and populate it in database table"""
  
  try:
    print(len(medicines))
    for medicine in medicines:
      #Formulary
      db_medicine = Formulary(
        medicine_id = medicine["medicine_id"].lower(),
        name = medicine["name"].lower(),
        type = medicine["type"].lower(),
        category = medicine["category"].lower(),
        drug_class = medicine["drug_class"].lower() if "drug_class" in medicine else None,
        fda_pregnancy_category_1 = medicine["fda_pregnancy_category_1"].lower() if "fda_pregnancy_category_1" in medicine else None,
        fda_pregnancy_category_2 = medicine["fda_pregnancy_category_2"].lower() if "fda_pregnancy_category_2" in medicine else None,
        fda_pregnancy_category_3 = medicine["fda_pregnancy_category_3"].lower() if "fda_pregnancy_category_3" in medicine else None,
        prescribable = medicine["prescribable"] if "prescribable" in medicine else None,
        prescription_level = medicine["prescription_level"].lower() if "prescription_level" in medicine else True,
      )
      
      with Session(database_engine) as session:
        if session.exec(select(Formulary).where(Formulary.medicine_id == db_medicine.medicine_id)).first():
          return
        else:
          session.add(db_medicine)
          session.commit()

      #Initiate Schemes
      schemes = medicine["schemes"]
      for scheme in schemes:
        register_scheme(scheme,default=default)
      
      #Initial requisition
      default_requisition = medicine["requisition"]
      
      register_requisition(default_requisition)
      update_requisition(requisition=default_requisition,receive=True)
          
    return {"message":"Medicine successfully added to the formulary!","position":"top","type":"positive"}
  except:
    return {"message":"Medicine couldn't be added!","position":"center","type":"negative"}

def register_inventory(inventory:dict,count:bool=False,dispensed:bool=False,transfer:bool=False,received:bool=False):
  """Adds a new row in inventory table and populates columns with corresponding data from inventory dictionary"""

  #FXS
  def last_inventory(inventory_tag:str):
    data = namedtuple("Data",["first","previous_amount"])
    with Session(database_engine) as session:
      db_inventory:Inventory = session.exec(select(Inventory).where(Inventory.medicine_id == inventory["medicine_id"].lower()).where((Inventory.issuer == inventory_tag.lower())|(Inventory.receiver == inventory_tag.lower())).order_by(Inventory.date.desc()).limit(1)).first()

      if db_inventory:
        return data(first=False,previous_amount=db_inventory.issuer_current_amount if db_inventory.issuer == inventory_tag.lower() else db_inventory.receiver_current_amount)
      else:
        return data(first=True,previous_amount=0)
      
  db_inventory = Inventory(
    medicine_id = inventory["medicine_id"],
    invoice = inventory["invoice"],
    issuer = inventory["issuer"],
    receiver = inventory["receiver"],
    issuer_previous_amount = last_inventory(inventory["issuer"]).previous_amount,
    issuer_current_amount = inventory["issuer_amount"] if count else last_inventory(inventory["issuer"]).previous_amount - inventory["amount"],
    receiver_previous_amount = last_inventory(inventory["receiver"]).previous_amount,
    receiver_current_amount = inventory["receiver_amount"] if count else last_inventory(inventory["receiver"]).previous_amount + inventory["amount"],
    logger = inventory["logger"],
    received = received,
    transfer = transfer,
    dispensed = dispensed,
    count = count,
  )

  with Session(database_engine) as session:
    session.add(db_inventory)
    session.commit()

def register_requisition(requisition:dict):
  """A function to create row in requisition table and populate it in database table"""

  db_requisition = Requisition(
    requisition_id = requisition["requisition_id"].lower(),
    medicine_id = requisition["medicine_id"].lower(),
    medicine_requisition_id = f"{requisition['requisition_id']}{requisition['medicine_id']}".lower(),
    vendor = requisition["vendor"].lower(),
    billed_amount = requisition["billed_amount"],
    ordered_by = requisition["ordered_by"].lower(),
    order_unit = requisition["order_unit"].lower(),
    order_unit_size = requisition["order_unit_size"],
    ordered_amount = requisition["ordered_amount"],
    unit_price = requisition["unit_price"],
    ordered_price = requisition["unit_price"] * (requisition["ordered_amount"]/requisition["order_unit_size"])
  )
  
  #Register
  with Session(database_engine) as session:
    if session.exec(select(Requisition).where(Requisition.medicine_requisition_id == db_requisition.medicine_requisition_id)).all():
      return
    else:
      session.add(db_requisition)
      session.commit()

def register_scheme(scheme:dict,default:bool=False):
  """"""
  #REGISTERING SERVICE SCHEMES
  db_scheme = Scheme(
    scheme_id = f"{scheme['scheme_name']}-{scheme['service_id'] if 'service_id' in scheme else scheme['medicine_id'] if 'medicine_id' in scheme else 000}".lower(),
    medicine_id = scheme["medicine_id"].lower() if "medicine_id" in scheme else None,
    service_id = scheme["service_id"].lower() if "service_id" in scheme else None,
    scheme_name = scheme["scheme_name"].lower(),
    scheme_item_code = scheme["scheme_item_code"].lower(),
    restricted = scheme["restricted"] if "restricted" in scheme else False
  )
  
  with Session(database_engine) as session:
    if session.exec(select(Scheme).where(Scheme.scheme_id == db_scheme.scheme_id)).first():
      return
    else:
      session.add(db_scheme)
      session.commit()
  
  #REGISTER PRICINGS
  pricings = scheme["prices"]
  for pricing in pricings:
    pricing["scheme_id"] = f"{scheme['scheme_name']}-{scheme['service_id'] if 'service_id' in scheme else scheme['medicine_id'] if 'medicine_id' in scheme else 000}".lower()
    register_pricing(pricing,default=default)
  
def register_pricing(pricing:dict,default:bool=False):
  """Adds a row in pricing table from data in 'pricing' dictionary"""
  #Turn off the previous pricing
  if default:
    updatable = True
  else:
    updatable = update_pricing(pricing)
  
  if updatable:
    #Enter new pricing
    db_pricing = Pricing(
      scheme_id = pricing["scheme_id"] if "scheme_id" in pricing else None,
      logger = pricing["logger"] if "logger" in pricing else "nexasoft",
      copayment = pricing["copayment"] if "copayment" in pricing else False,
      price_range = pricing["price_range"] if "price_range" in pricing else False,
      min = pricing["min"] if "min" in pricing else 0,
      max = pricing["max"] if "max" in pricing else 0, 
      standard = pricing["standard"] if "standard" in pricing else 0,
      priority = pricing["priority"] if "priority" in pricing else pricing["standard"] if "standard" in pricing else 0,
      topup = pricing["topup"] if "topup" in pricing else 0
    )
    
    with Session(database_engine) as session:
      session.add(db_pricing)
      session.commit()
  
  else:
    return

def register_icd_diagnosis(diagnosis:dict,icd10=False,icd11=True):
  """"""
  #ICD10
  if icd10:
    db_diagnosis = ICD10Diagnosis(
      code = diagnosis["code"],
      name = diagnosis["name"]
    )

    with Session(database_engine) as session:
      if list(session.exec(select(ICD10Diagnosis).where(ICD10Diagnosis.code == db_diagnosis.code)).all()):
        return
      else:
        session.add(db_diagnosis)
        session.commit()
  
  #ICD11
  if icd11:
    db_diagnosis = ICD11Diagnosis(
      code = diagnosis["code"],
      name = diagnosis["name"]
    )

    with Session(database_engine) as session:
      if list(session.exec(select(ICD11Diagnosis).where(ICD11Diagnosis.code == db_diagnosis.code)).all()):
        return
      else:
        session.add(db_diagnosis)
        session.commit()


#UPDATE FUNCTIONS
def update_facility_subscription(subscription:dict):
  """Changes value of active column to 'f' in a facilitysubscription table row with 't' as its value and then add new row"""

  with Session(database_engine) as session:
    last_active_subscription:FacilitySubscription = session.exec(select(FacilitySubscription).where(FacilitySubscription.active)).first()
    
    if last_active_subscription:
      last_active_subscription.active = False
      session.commit()

      register_facility_subscription(subscription)

def update_staff(staff,activate:bool=False,edit:bool=False,suspend:bool=False):
  """"""
  if activate:
    with Session(database_engine) as session:
      db_staff:User = list(session.exec(select(User).where(User.username == staff["username"])))[0]

      db_staff.active,db_staff.suspended = True,False

      session.commit()

      return {"success":True,"message":"Successfull activated!","type":"positive","position":"top"}

  
  if edit:
    with Session(database_engine) as session:
      db_staff:User = list(session.exec(select(User).where(User.username == staff["username"])))[0]

      db_staff.title = staff["title"]
      db_staff.first_name = staff["first_name"]
      db_staff.middle_name = staff["middle_name"]
      db_staff.last_name = staff["last_name"]
      db_staff.gender = staff["gender"]
      db_staff.birthdate = staff["birthdate"]
      db_staff.qualification = staff["qualification"]
      db_staff.designation = staff["designation"]
      db_staff.email = staff["email"]
      db_staff.mobile = staff["mobile"]
      db_staff.roles = json.dumps(staff["roles"])
      db_staff.active = staff["active"]
      db_staff.suspended = staff["suspended"]
      #Password Edit
      if "password" in staff:
        db_staff.password = staff["password"]

      session.commit()

      return {"success":True,"message":"Successfully edited!","type":"positive","position":"top"}
  
  if suspend:
    with Session(database_engine) as session:
      db_staff:User = list(session.exec(select(User).where(User.username == staff["username"])))[0]

      db_staff.active,db_staff.suspended = False,True

      session.commit()

      return {"success":True,"message":"Successfull suspended!","type":"positive","position":"top"}

def update_login(login:dict):
  """A function to alter values on the row of login table"""

  with Session(database_engine) as session:
    db_login:Login = list(session.exec(select(Login).where(Login.login_id == login["login_id"])))[0]
    db_login.logged = False
    db_login.logout_time = datetime.now()
    
    session.commit()

def update_service(service:dict):
  """"""
  
  try:
    #UPDATE SERVICE
    with Session(database_engine) as session:
      db_service:Service = session.exec(select(Service).where(Service.service_id == service["service_id"].lower())).first()
      
      db_service.name = service["name"].lower()
      db_service.alternative_name = service["alternative_name"]
      db_service.type = service["type"].lower()
      db_service.active = service["active"]
      
      session.commit()

    #UPDATE SCHEMES & PRICINGS
    schemes = service["schemes"]
    update_schemes(schemes)

    return {"status":True,"message":"Service updated successfully!","type":"positive","position":"top"}
  
  except:
    return {"status":False,"message":"Service not updated!","type":"negative","position":"top"}

def update_formulary(medicine:dict,suspend:bool=False):
  """"""
  
  if suspend:
    with Session(database_engine) as session:
      db_medicine:Formulary = session.exec(select(Formulary).where(Formulary.medicine_id == medicine["medicine_id"])).first()
      db_medicine.active = False
      session.commit()

      return {"message":"Medicine delete successfully from the formulary!","type":"positive","position":"top"}
    
  else:
    with Session(database_engine) as session:
      db_medicine:Formulary = session.exec(select(Formulary).where(Formulary.medicine_id == medicine["medicine_id"])).first()

      db_medicine.name = medicine["name"]
      db_medicine.type = medicine["type"]
      db_medicine.category = medicine["category"],
      db_medicine.drug_class = medicine["drug_class"] if "drug class" in medicine else None
      db_medicine.fda_pregnancy_category_1 = medicine["fda_pregnancy_category_1"]
      db_medicine.fda_pregnancy_category_2 = medicine["fda_pregnancy_category_2"]
      db_medicine.fda_pregnancy_category_3 = medicine["fda_pregnancy_category_3"]
      db_medicine.prescription_level = medicine["prescription_level"],

      session.commit()

      return {"status":True,"message":"Formulary updated successfully!","type":"positive","position":"top"}

def update_schemes(schemes:list[dict]):
  """Updating schemes of a particular services"""
  
  for scheme in schemes:
    #UPDATING SCHEME
    with Session(database_engine) as session:
      db_scheme:Scheme = session.exec(select(Scheme).where(Scheme.scheme_id == scheme["scheme_id"])).first()
      
      db_scheme.medicine_id = scheme["medicine_id"] if "medicine_id" in scheme else None
      db_scheme.service_id = scheme["service_id"] if "service_id" in scheme else None
      db_scheme.scheme_name = scheme["scheme_name"]
      db_scheme.scheme_item_code = scheme["scheme_item_code"]
      db_scheme.restricted = scheme["restricted"]
      session.commit()
      
    #UPDATING PRICINGS
    pricings = scheme["prices"]
    for pricing in pricings:
      register_pricing(pricing)

def update_pricing(pricing:dict):
  
  def _changed(db_pricing:Pricing):
    if db_pricing.copayment == pricing["copayment"] and db_pricing.price_range == pricing["price_range"] and db_pricing.min == pricing["min"] and db_pricing.max == pricing["max"] and db_pricing.standard == pricing["standard"] and db_pricing.priority == pricing["priority"] and db_pricing.topup == pricing["topup"]:
      return False
    else:
      return True
  
  with Session(database_engine) as session:
    db_pricing:Pricing = session.exec(select(Pricing).where(Pricing.scheme_id == pricing["scheme_id"].lower()).where(Pricing.active)).first()
    if db_pricing:
      if _changed(db_pricing):
        db_pricing.active = False
        session.commit()
        return True
      else:
        return
      
def update_medicine(medicine:dict,transfer:bool=False,count:bool=False,cancel:bool=False,receive:bool=False,order:bool=False):
  """A function to update a row in medicine table and populate it with data from 'medicine' dictionary"""
  """"""

  if order:
    with Session(database_engine) as session:
      db_medicine:Medicine = list(session.exec(select(Medicine).where(Medicine.requisition_medicine_id == medicine['requisition_medicine_id'])))[0]
      
      db_medicine.ordered = True if medicine["ordered_amount"] else False
      db_medicine.ordered_amount = medicine["ordered_amount"]
      db_medicine.unit_price = medicine["unit_price"]
      db_medicine.ordered_amount = medicine["ordered_amount"]
      db_medicine.ordered_price = medicine["ordered_price"]

      session.commit()

  if receive:
    #Updating inventory
    register_inventory(
      inventory={
        "medicine_id":medicine["medicine_id"],
        "invoice":medicine["invoice"],
        "issuer":"vendor",
        "receiver":"main store",
        "logger":medicine["received_by"],
        "amount":medicine["received_amount"]
      },received=True
    )

    #Updating requisition
    with Session(database_engine) as session:
      db_medicine:Medicine = list(session.exec(select(Medicine).where(Medicine.requisition_medicine_id == medicine['requisition_medicine_id'])))[0]

      db_medicine.brand_name = medicine["brand_name"]
      db_medicine.manufacturer = medicine["manufacturer"]
      db_medicine.batch_no = medicine["batch_no"]
      db_medicine.mfg_date = medicine["mfg_date"]
      db_medicine.expire_date = medicine["expire_date"]
      db_medicine.received = medicine["received"]
      db_medicine.active = medicine["active"]
      db_medicine.received_on = datetime.now()
      db_medicine.received_by = medicine["received_by"]
      db_medicine.received_amount = medicine["received_amount"]
      db_medicine.received_price = medicine["received_price"]
      db_medicine.rejected = medicine["rejected"]
      db_medicine.rejected_amount = medicine["rejected_amount"]
      db_medicine.rejected_price = medicine["rejected_price"]
      db_medicine.initial_store_balance = medicine["received_amount"]
      db_medicine.store_balance = medicine["received_amount"]
      db_medicine.physical_count = medicine["received_amount"]
      db_medicine.count_unit = medicine["count_unit"]

      session.commit()
  
  if cancel:
    with Session(database_engine) as session:
      db_medicine:Medicine = list(session.exec(select(Medicine).where(Medicine.requisition_medicine_id == medicine['requisition_medicine_id'])))[0]
    
      db_medicine.cancelled = True
      db_medicine.cancelled_by = medicine["cancelled_by"]
      db_medicine.cancelled_on = datetime.now()

      session.commit()

  if transfer:
    #Updating Inventory table
    register_inventory(
      inventory={
        "medicine_id":medicine["medicine_id"],
        "invoice":str(uuid4()).split("-")[0],
        "issuer":"main store",
        "receiver":"dispensing store",
        "logger":medicine["transferred_by"],
        "amount":medicine["transfer_balance"]
      },transfer=True
    )

    #Updating requisition medicine
    with Session(database_engine) as session:
      db_medicine:Medicine = list(session.exec(select(Medicine).where(Medicine.requisition_medicine_id == medicine['requisition_medicine_id'])))[0]
    
      db_medicine.dispensing_balance = medicine["dispensing_balance"]
      db_medicine.store_balance = medicine["store_balance"]

      session.commit()

  if count:
    inventories = [
      {
        "medicine_id":medicine["medicine_id"],
        "invoice":str(uuid4()).split("-")[0],
        "issuer":"main store",
        "receiver":"main store",
        "logger":medicine["counted_by"],
        "issuer_amount":medicine["store_balance"],
        "receiver_amount":medicine["store_balance"]
      },
      {
        "medicine_id":medicine["medicine_id"],
        "invoice":str(uuid4()).split("-")[0],
        "issuer":"dispensing store",
        "receiver":"dispensing store",
        "logger":medicine["counted_by"],
        "issuer_amount":medicine["dispensing_balance"],
        "receiver_amount":medicine["dispensing_balance"]
      }
    ]
    for inventory in inventories:
      register_inventory(inventory=inventory,count=True)

    #Update Requisition count
    with Session(database_engine) as session:
      db_medicine:Medicine = list(session.exec(select(Medicine).where(Medicine.requisition_medicine_id == medicine['requisition_medicine_id'])))[0]
    
      db_medicine.store_balance = medicine["store_balance"]
      db_medicine.dispensing_balance = medicine["dispensing_balance"]
      db_medicine.physical_count = medicine["physical_count"]
      db_medicine.active = True if medicine["physical_count"] else False
      db_medicine.count_unit = medicine["count_unit"]
      db_medicine.counted_by = medicine["counted_by"]
      db_medicine.physical_count_date = datetime.now()

      session.commit()

def update_requisition(requisition:dict,cancel:bool=False,delete:bool=False,receive:bool=False,count:bool=False):
  """Updates the row in requisition table based on values of requisition dict"""

  requisition["medicine_requisition_id"] = f"{requisition['requisition_id']}{requisition['medicine_id']}".lower()
  
  if receive:
    with Session(database_engine) as session:
      db_requisition:Requisition = session.exec(select(Requisition).where(Requisition.medicine_requisition_id == requisition["medicine_requisition_id"])).first()
      db_requisition.received = True
      db_requisition.received_amount = requisition["received_amount"]
      db_requisition.received_price = requisition["received_price"]
      db_requisition.received_by = requisition["received_by"].lower()
      db_requisition.received_on = datetime.now()
      db_requisition.invoice = requisition["invoice"].lower() if "invoice" in requisition else None
      db_requisition.delivery_note = requisition["delivery_note"].lower() if "delivery_note" in requisition else None
      db_requisition.brand_name = requisition["brand_name"].lower() if "brand_name" in requisition else None
      db_requisition.manufacturer = requisition["manufacturer"].lower() if "manufacturer" in requisition else None
      db_requisition.batch_no = requisition["batch_no"].lower() if "batch_no" in requisition else None
      db_requisition.expire_date = requisition["expire_date"] if "expire_date" in requisition else None
      db_requisition.balance = requisition["received_amount"]

      session.commit()
      
  
  if count:
    pass

  if cancel:
    with Session(database_engine) as session:
      db_requisition:Requisition = session.exec(select(Requisition).where(Requisition.requisition_id == requisition["requisition_id"])).first()
      
      db_requisition.active = False

      session.commit()

  if delete:
    with Session(database_engine) as session:
      db_requisition:Requisition = session.exec(select(Requisition).where(Requisition.requisition_id == requisition["requisition_id"])).first()
      session.delete(db_requisition)
      session.commit()

def update_service_prices(service_id:str,nhif:bool=False):
  """Retrieves updated prices from the respective"""

  pricings = []

  try:
    pass
  except:
    pass
  finally:
    pass




