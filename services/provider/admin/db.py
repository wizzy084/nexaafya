"""A module for creating and updating rows in the database tables """

#GENERAL IMPORTS
from sqlmodel import SQLModel,Session

#PROJECT IMPORTS
from services.provider.configs import database_engine
from services.provider.admin import template
from services.provider.clients.models import *
from ._snippets import *



#DATABASE POPULATION
def populate_db():
  #creating database tables
  SQLModel.metadata.create_all(database_engine)

  #Initial users
  with Session(database_engine) as session:
    db_users:list[User] = list(session.exec(select(User)).all())
    if not db_users:
      for user in template.users:
        register_staff(user)
      
  #Initial services
  with Session(database_engine) as session:
    db_services:list[Service] = list(session.exec(select(Service)).all())
    if not db_services:
      for service in template.services:
        register_service(service)

  #Initial formulary
  with Session(database_engine) as session:
    db_formulary:list[Formulary] = list(session.exec(select(Formulary)).all())
    if not db_formulary:
      register_formulary(template.medicines)

  #Initial requisition
  with Session(database_engine) as session:
    db_requisitions:list[Requisition] = list(session.exec(select(Requisition)).all())
    
    if not db_requisitions:
      register_requisition(template.requisition)
      initiate_requisition(template.requisition)
      order_requisition(template.requisition)
      receive_requisition(template.requisition)
      #Initial medicines
      for medicine in template.medicines:
        medicine["active"] = True
        register_medicine(medicine)
        update_medicine(medicine=medicine,order=True,receive=True)

  
#REGISTER FUNCTIONS
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

def register_service(service:dict):
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
          register_scheme(scheme)
          
    return {"status":True,"message":"Service successfully added!","type":"positive","position":"top"}
  except:
    return {"status":False,"message":"Service not added!","type":"negative","position":"center"}

def register_formulary(medicines:list[dict]):
  """A function to create row in formulary table and populate it in database table"""
  
  try:
    for medicine in medicines:
      #Formaulary
      db_medicine = Formulary(
        medicine_id = medicine["medicine_id"],
        name = medicine["name"],
        type = medicine["type"],
        category = medicine["category"],
        drug_class = medicine["drug_class"] if "drug_class" in medicine else None,
        fda_pregnancy_category_1 = medicine["fda_pregnancy_category_1"] if "fda_pregnancy_category_1" in medicine else None,
        fda_pregnancy_category_2 = medicine["fda_pregnancy_category_2"] if "fda_pregnancy_category_2" in medicine else None,
        fda_pregnancy_category_3 = medicine["fda_pregnancy_category_3"] if "fda_pregnancy_category_3" in medicine else None,
        prescribable = medicine["prescribable"] if "prescribable" in medicine else None,
        prescription_level = medicine["prescription_level"] if "prescription_level" in medicine else None,
        active = True
      )
      
      with Session(database_engine) as session:
        if list(session.exec(select(Formulary).where(Formulary.medicine_id == db_medicine.medicine_id)).all()):
          return
        else:
          session.add(db_medicine)
          session.commit()
      
      #Register inventory
      inventory = {"medicine_id":medicine["medicine_id"],"default":True}
      register_inventory(inventory)

      #Initiate Schemes
      schemes = medicine["schemes"]
      for scheme in schemes:
        register_scheme(scheme)
          
    return {"message":"Medicine successfully added to the formulary!","position":"top","type":"positive"}
  except:
    return {"message":"Medicine couldn't be added!","position":"center","type":"negative"}

def register_inventory(inventory:dict):
  """Adds a new row in inventory table and populates columns with corresponding data from inventory dictionary"""
  
  if "default" in inventory:
    db_inventory = Inventory(
      medicine_id = inventory["medicine_id"],
      default = True
    )
  
    with Session(database_engine) as session:
      session.add(db_inventory)
      session.commit()

  else:
    db_inventory = Inventory(
      medicine_id = inventory["medicine_id"],
      invoice = inventory["invoice"],
      issuer = inventory["issuer"],
      receiver = inventory["receiver"],
      issuer_previous_amount = inventory["issuer_previous_amount"],
      issuer_current_amount = inventory["issuer_current_amount"],
      receiver_previous_amount = inventory["receiver_previous_amount"],
      receiver_current_amount = inventory["receiver_current_amount"],
      receiving = inventory["receiving"] if "receiving" in inventory else False,
      transfer = inventory["transfer"] if "transfer" in inventory else False,
      dispensing = inventory["dispensing"] if "dispensing" in inventory else False,
      physical_count = inventory["physical_count"] if "physical_count" in inventory else False,
    )

    with Session(database_engine) as session:
      db_inventory_entries:Inventory = session.exec(select(Inventory).where(Inventory.medicine_id == db_inventory.medicine_id)).last()
      session.add(db_inventory)
      session.commit()

def register_scheme(scheme:dict):
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
    if list(session.exec(select(Scheme).where(Scheme.scheme_id == db_scheme.scheme_id))):
      return
    else:
      session.add(db_scheme)
      session.commit()
  
  #REGISTER PRICINGS
  pricings = scheme["prices"]
  for pricing in pricings:
    pricing["scheme_id"] = f"{scheme['scheme_name']}-{scheme['service_id'] if 'service_id' in scheme else scheme['medicine_id'] if 'medicine_id' in scheme else 000}".lower()
    register_pricing(pricing)
  
def register_pricing(pricing:dict):
  """Adds a row in pricing table from data in 'pricing' dictionary"""
  #Turn off the previous pricing
  update_pricing(pricing)
  
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

def register_requisition(requisition:dict):
  """A function to create row in requisition table and populate it in database table"""

  db_requisition = Requisition(
    requisition_id = requisition["requisition_id"],
  )
  
  #Register
  with Session(database_engine) as session:
    if list(session.exec(select(Requisition).where(Requisition.requisition_id == db_requisition.requisition_id)).all()):
      return
    else:
      session.add(db_requisition)
      session.commit()
  
  #Initiate
  initiate_requisition(requisition)

def register_medicine(medicine:dict):
  """A function to create row in medicine table and populate it in database table"""
  
  db_medicine = Medicine(
    requisition_id = medicine["requisition_id"],
    medicine_id = medicine["medicine_id"],
    requisition_medicine_id = f"{medicine['medicine_id']}{medicine['requisition_id']}",
    name = medicine["name"],
    type = medicine["type"],
    category = medicine["category"],
    drug_class = medicine["drug_class"] if "drug_class" in medicine else None,
    fda_pregnancy_category_1 = medicine["fda_pregnancy_category_1"] if "fda_pregnancy_category_1" in medicine else None,
    fda_pregnancy_category_2 = medicine["fda_pregnancy_category_2"] if "fda_pregnancy_category_2" in medicine else None,
    fda_pregnancy_category_3 = medicine["fda_pregnancy_category_3"] if "fda_pregnancy_category_3" in medicine else None,
    prescription_level = medicine["prescription_level"],
    order_unit = medicine["order_unit"],
    order_unit_size = medicine["order_unit_size"],
    initial_store_balance = medicine["initial_store_balance"],
    store_balance = medicine["store_balance"],
    physical_count = medicine["physical_count"],
    amc = medicine["amc"] if "amc" in medicine else None,
    mos = medicine["mos"] if "mos" in medicine else None,
    ordered = medicine["ordered"],
    ordered_amount = medicine["ordered_amount"],
    ordered_price = medicine["ordered_price"],
    unit_price = medicine["unit_price"],
    ordered_by = medicine["ordered_by"],
    ordered_on = datetime.now()
  )

  with Session(database_engine) as session:
    if list(session.exec(select(Medicine).where(Medicine.requisition_medicine_id == db_medicine.requisition_medicine_id))): 
      return
    else:
      session.add(db_medicine)
      session.commit()

def register_stationery(stationery:dict):
  """A function to create row in stationery table and populate it with 'stationery' data"""

  db_stationery = Stationery(
    stationery_id = stationery["stationery_id"],
    requisition_id = stationery["requisition_id"],
    ordered = True,
    ordered_amount = stationery["ordered_amount"],
    ordered_price = stationery["ordered_price"],
  )

  with Session(database_engine) as session:
    if list(session.exec(select(Stationery).where(Stationery.stationery_id == db_stationery.stationery_id)).all()):
      return
    else:
      session.add(db_stationery)
      session.commit()

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

def initiate_requisition(requisition:dict):
  """"""

  #Requisition
  try:
    with Session(database_engine) as session:
      db_requisition:Requisition = list(session.exec(select(Requisition).where(Requisition.requisition_id == requisition["requisition_id"])))[0]
      db_requisition.initiated = True
      db_requisition.initiated_by = requisition["initiated_by"]
      db_requisition.initiation_date = datetime.now()
    
      session.commit()
    #Medicines
    with Session(database_engine) as session:
      db_medicines:list[Medicine] = list(session.exec(select(Medicine).where(Medicine.requisition_id == requisition["requisition_id"])))
      db_medicines_ids = [db_medicine.medicine_id for db_medicine in db_medicines]

      for medicine in requisition["medicines"]:
        if medicine["medicine_id"] not in db_medicines_ids:
          register_medicine(medicine)

      return {"message":"Requisition initiated successfully","type":"positive","position":"top"}
  except:
    return {"message":"Requisition not initiated!","type":"negative","position":"center"}


#UPDATE FUNCTIONS
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
    with Session(database_engine) as session:
      db_service:Service = list(session.exec(select(Service).where(Service.service_id == service["service_id"])))[0]

      db_service.alternative_name = service["alternative_name"]
      db_service.type = service["type"]
      db_service.active = service["active"]

      session.commit()

      return {"status":True,"message":"Service updated successfully!","type":"positive","position":"top"}
  
  except:
    return {"status":True,"message":"Service not updated!","type":"negative","position":"center"}

def update_formulary(medicine:dict,delete:bool=False):
  """"""
  
  if delete:
    with Session(database_engine) as session:
      db_medicine:Formulary = list(session.exec(select(Formulary).where(Formulary.medicine_id == medicine["medicine_id"])))[0]
      if db_medicine:
        session.delete(db_medicine)
      session.commit()

      return {"message":"Medicine delete successfully from the formulary!","type":"positive","position":"top"}
    
  else:
    with Session(database_engine) as session:
      db_medicine:Formulary = list(session.exec(select(Formulary).where(Formulary.medicine_id == medicine["medicine_id"])))[0]

      db_medicine.name = medicine["name"]
      db_medicine.type = medicine["type"]
      db_medicine.type = medicine["category"],
      db_medicine.drug_class = medicine["drug_class"] if "drug class" in medicine else None
      db_medicine.fda_pregnancy_category_1 = medicine["fda_pregnancy_category_1"]
      db_medicine.fda_pregnancy_category_2 = medicine["fda_pregnancy_category_2"]
      db_medicine.fda_pregnancy_category_3 = medicine["fda_pregnancy_category_3"]
      db_medicine.prescription_level = medicine["prescription_level"],
      db_medicine.active = True

      session.commit()

      return {"status":True,"message":"Formulary updated successfully!","type":"positive","position":"top"}

def update_pricing(pricing:dict):

  if "medicine_id" in pricing:
    with Session(database_engine) as session:
      db_pricings:list[Pricing] = list(session.exec(select(Pricing).where(Pricing.payment_scheme_id == pricing["payment_scheme_id"])))
      
      if db_pricings:
        db_pricing = sorted(db_pricings,key=lambda pricing:pricing.log_date,reverse=True)[0]
        db_pricing.active = False
      else:
        return
      
      session.commit()

  if "service_id" in pricing:
    with Session(database_engine) as session:
      db_pricings:list[Pricing] = list(session.exec(select(Pricing).where(Pricing.service_id == pricing["service_id"])))
      
      if db_pricings:
        db_pricing = sorted(db_pricings,key=lambda pricing:pricing.log_date,reverse=True)[0]
        db_pricing.active = False
      else:
        return
      
      session.commit()

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
    with Session(database_engine) as session:
      db_medicine:Medicine = list(session.exec(select(Medicine).where(Medicine.requisition_medicine_id == medicine['requisition_medicine_id'])))[0]
    
      db_medicine.dispensing_balance = medicine["dispensing_balance"]
      db_medicine.store_balance = medicine["store_balance"]

      session.commit()

  if count:
    with Session(database_engine) as session:
      db_medicine:Medicine = list(session.exec(select(Medicine).where(Medicine.requisition_medicine_id == medicine['requisition_medicine_id'])))[0]
    
      db_medicine.store_balance = medicine["store_balance"]
      db_medicine.dispensing_balance = medicine["dispensing_balance"]
      db_medicine.physical_count = medicine["physical_count"]
      db_medicine.active = True if medicine["physical_count"] else False
      db_medicine.count_unit = medicine["count_unit"]
      db_medicine.physical_count_date = datetime.now()

      session.commit()

def update_requisition(requisition:dict,cancel:bool=False,initiate:bool=False,order:bool=False,receive:bool=False):
  """Updates the row in requisition table based on values of requisition dict"""
  
  if initiate:
    return initiate_requisition(requisition)

  if order:
    return order_requisition(requisition)

  if receive:
    return receive_requisition(requisition)

  if cancel:
    return cancel_requisition(requisition)

def order_requisition(requisition:dict):
  """"""

  try:
    with Session(database_engine) as session:
      db_requisition:Requisition = list(session.exec(select(Requisition).where(Requisition.requisition_id == requisition["requisition_id"])))[0]
      db_requisition.placed = True
      db_requisition.vendor = requisition["vendor"].lower()
      db_requisition.placed_by = requisition["placed_by"]
      db_requisition.placement_date = datetime.now()

      session.commit()

      return {"message":"Requisition ordered successfully","type":"positive","position":"top"}
  except:
    return {"message":"Requisition couldn't be order.Review it again!","type":"negative","position":"center"}

def receive_requisition(requisition:dict):

  try:
    with Session(database_engine) as session:
      db_requisition:Requisition = list(session.exec(select(Requisition).where(Requisition.requisition_id == requisition["requisition_id"])))[0]
      db_requisition.received = True
      db_requisition.received_by = requisition["received_by"]
      db_requisition.receive_date = datetime.now()
      db_requisition.invoice_id = requisition["invoice_id"]
      db_requisition.delivery_note_id = requisition["delivery_note_id"]

      session.commit()

      return {"message":"Requisition received successfully","type":"positive","position":"top"}
  except:
    return {"message":"Requisition couldn't be received.Review it again!","type":"negative","position":"center"}


   #Cancelling

def close_requisitions():
  """Changes value of column 'closed' from False to True if all rows in its child table Medicine have column 'active' with value False"""
  
  with Session(database_engine) as session:
    db_requisitions:list[Requisition] = list(session.exec(select(Requisition).where(Requisition.closed == False)))
    
    for db_requisition in db_requisitions:
      availables = [db_medicine.medicine_id for db_medicine in db_requisition.medicines if db_medicine.active]
      
      if not availables:
        db_requisition.closed = True
  
    session.commit()

#CANCEL FUNCTIONS
def cancel_requisition(requisition:dict):
  """A function to cancel a requisition"""

  try:
    with Session(database_engine) as session:
      db_requisition:Requisition = list(session.exec(select(Requisition).where(Requisition.requisition_id == requisition["requisition_id"])))[0]
      db_requisition.cancelled = True
      db_requisition.closed = True
      db_requisition.cancelled_by = requisition["cancelled_by"]
      db_requisition.cancel_date = datetime.now()

      session.commit()

    return {"message":"Requisition cancelled successfully","type":"positive","position":"top"}
  except:
    return {"message":"Requisition couldn't be cancelled!","type":"negative","position":"top"}
  








