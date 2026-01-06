"""A module for base operations neccesary in processing semi during database updating and database querrying."""

#GENERAL IMPORTS
import json
from collections import namedtuple

#PROJECT IMPORTS
from .models import *





#UNMODELS
def unmodel_facility(db_facility:Facility):
  """A function to convert Facility model details into a namedtuple"""

  Facility = namedtuple("Facility",["facility_id","name","short_name","tag","postcode","registration_time","category","level","certifications","designations","primary_roles","secondary_roles","services","medicine_types","vendors","mos","titles","marital_statuses","occupations","relationships","id_number_types","years_of_existence","active_payment_modes","payment_packages","subscriptions","departments"])

  return Facility(
    facility_id = db_facility.facility_id,
    name = db_facility.name,
    short_name = db_facility.short_name,
    tag = db_facility.tag,
    postcode = db_facility.postcode,
    registration_time = db_facility.registration_time,
    category = db_facility.category,
    level = db_facility.level,
    certifications = db_facility.certifications,
    designations = db_facility.designations,
    primary_roles = db_facility.primary_roles,
    secondary_roles = db_facility.secondary_roles,
    services = db_facility.services,
    medicine_types = db_facility.medicine_types,
    vendors = db_facility.vendors,
    mos = db_facility.mos,
    titles = db_facility.titles,
    marital_statuses = db_facility.marital_statuses,
    occupations = db_facility.occupations,
    relationships = db_facility.relationships,
    id_number_types = db_facility.id_number_types,
    years_of_existence = db_facility.years_of_existence,
    active_payment_modes = db_facility.active_payment_modes,
    payment_packages = db_facility.payment_packages,
    departments = [unmodel_department(db_department) for db_department in db_facility.departments],
    subscriptions = [unmodel_facility_subscription(db_facility_subscription) for db_facility_subscription in db_facility.subscriptions]
  )

def unmodel_facility_subscription(db_facility_subscription:FacilitySubscription):
  """A function to convert FacilitySubscription model details into a namedtuple"""

  Subscription = namedtuple("Subscription",["facility_id","receipt","tier","active","cost","paid_amount","pending_amount","start_time","end_time"])

  return Subscription(
    facility_id = db_facility_subscription.facility_id,
    receipt = db_facility_subscription.receipt,
    tier = db_facility_subscription.tier,
    active = db_facility_subscription.active,
    cost = db_facility_subscription.cost,
    paid_amount = db_facility_subscription.paid_amount,
    pending_amount = db_facility_subscription.pending_amount,
    start_time = db_facility_subscription.start_time,
    end_time = db_facility_subscription.end_time
  )

def unmodel_login(db_login:Login):
  """A function to convert a Login model instance into a dictionary"""

  _Login = namedtuple("_Login",["login_id","username","logged","login_time","logout_time","login_ip","logout_ip"])
  
  return _Login(
    login_id = db_login.login_id,
    username = db_login.username,
    logged = db_login.logged,
    login_time = db_login.login_time,
    logout_time = db_login.logout_time,
    login_ip = db_login.login_ip,
    logout_ip = db_login.logout_ip
  )

def unmodel_user(db_user:User):
  """A function to convert a User model instance into a dictionary"""

  _User = namedtuple("_User",["username","title","qualification","designation","first_name","middle_name","last_name","birthdate","gender","email","mobile","password","photo","is_super","registered_on","access","roles","active","logins"])

  return _User(
    username = db_user.username,
    title = db_user.title,
    qualification = db_user.qualification,
    designation = db_user.designation,
    first_name = db_user.first_name,
    middle_name = db_user.middle_name,
    last_name = db_user.last_name,
    birthdate = db_user.birthdate,
    gender = db_user.gender,
    email = db_user.email,
    mobile = db_user.mobile,
    password = db_user.password,
    photo = db_user.photo,
    is_super = db_user.is_super,
    registered_on = db_user.registered_on,
    access = json.loads(db_user.access) if db_user.access else None,
    roles = json.loads(db_user.roles) if db_user.roles else [],
    active = db_user.active,
    logins = sorted([unmodel_login(db_login) for db_login in db_user.logins],key=lambda login:login.login_time,reverse=True) if db_user.logins else []
  )

def unmodel_service(db_service:Service):
  """Converts data from service table row(s) into dictionary"""

  _Service = namedtuple("_Service",["service_id","name","alternative_name","type","active","schemes"])

  return _Service(
    service_id = db_service.service_id,
    name = db_service.name,
    alternative_name = db_service.alternative_name,
    type = db_service.type,
    active = db_service.active,
    schemes = [unmodel_scheme(db_scheme) for db_scheme in db_service.schemes]
  )

def unmodel_formulary(db_formulary:Formulary):
  """Reads data from rows in formulary table and returns output as namedtuple object"""

  _Formulary = namedtuple("Formulary",["medicine_id","name","type","category","drug_class","fda_pregnancy_category_1","fda_pregnancy_category_2","fda_pregnancy_category_3","prescribable","prescription_level","active","schemes","requisitions","inventory"])
  
  return _Formulary(
    medicine_id = db_formulary.medicine_id,
    name = db_formulary.name,
    type = db_formulary.type,
    category = db_formulary.category,
    drug_class = db_formulary.drug_class,
    fda_pregnancy_category_1 = db_formulary.fda_pregnancy_category_1,
    fda_pregnancy_category_2 = db_formulary.fda_pregnancy_category_2,
    fda_pregnancy_category_3 = db_formulary.fda_pregnancy_category_3,
    prescribable = db_formulary.prescribable,
    prescription_level = db_formulary.prescription_level,
    active = db_formulary.active,
    schemes = [unmodel_scheme(db_scheme) for db_scheme in db_formulary.schemes],
    requisitions = [unmodel_requisition(db_requisition) for db_requisition in db_formulary.requisitions],
    inventory = [unmodel_inventory(db_inventory) for db_inventory in db_formulary.inventory]
  )

def unmodel_requisition(db_requisition:Requisition):
  """Unmodels a requisition object"""

  _Requisition = namedtuple("Requisition",[
    "requisition_id","medicine_id","medicine_requisition_id","medicine_name",
    "delivery_note","invoice","vendor","brand_name","mfg_date","manufacturer","batch_no","expire_date",
    "balance","active","paid","billed","paid_amount","billed_amount","ordered","ordered_on","ordered_by",
    "order_unit","order_unit_size","ordered_amount","unit_price","ordered_price","received","received_amount",
    "received_price","received_by","received_on","rejected","rejected_amount","rejection_reasons","rejected_price",
    "requisition_ordered","requisition_received","requisition_rejected"
  ])

  return _Requisition(
    requisition_id = db_requisition.requisition_id,
    medicine_id = db_requisition.medicine_id,
    medicine_requisition_id = db_requisition.medicine_requisition_id,
    medicine_name = db_requisition.medicine_name,
    delivery_note = db_requisition.delivery_note,
    invoice = db_requisition.invoice,
    vendor = db_requisition.vendor,
    brand_name = db_requisition.brand_name,
    mfg_date = db_requisition.mfg_date,
    manufacturer = db_requisition.manufacturer,
    batch_no = db_requisition.batch_no,
    expire_date = db_requisition.expire_date,
    balance = db_requisition.balance,
    active = db_requisition.active,
    paid = db_requisition.paid,
    billed = db_requisition.billed,
    paid_amount = db_requisition.paid_amount,
    billed_amount = db_requisition.billed_amount,
    ordered = db_requisition.ordered,
    ordered_by = db_requisition.ordered_by,
    ordered_on = db_requisition.ordered_on,
    order_unit = db_requisition.order_unit,
    order_unit_size = db_requisition.order_unit_size,
    ordered_amount = db_requisition.ordered_amount,
    ordered_price = db_requisition.ordered_price,
    unit_price = db_requisition.unit_price,
    received = db_requisition.received,
    received_by = db_requisition.received_by,
    received_on = db_requisition.received_on,
    received_amount = db_requisition.received_amount,
    received_price = db_requisition.received_price,
    rejected = db_requisition.rejected,
    rejection_reasons = json.loads(db_requisition.rejection_reasons) if db_requisition.rejection_reasons else [],
    rejected_amount = db_requisition.rejected_amount,
    rejected_price = db_requisition.rejected_price,
    requisition_ordered = db_requisition.requisition_ordered,
    requisition_received = db_requisition.requisition_received,
    requisition_rejected = db_requisition.requisition_rejected
  )

def unmodel_inventory(db_inventory:Inventory):
  """"""
  InventoryEntry = namedtuple("InventoryEntry",["medicine_id","invoice","issuer","receiver","issuer_previous_amount","issuer_current_amount","receiver_previous_amount","receiver_current_amount","received","transfer","dispensed","count","default","date","logger"])
  
  return InventoryEntry(
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
    date = db_inventory.date,
    logger = db_inventory.logger
  )

def unmodel_scheme(db_scheme:Scheme):
  """"""
  _Scheme = namedtuple("_Scheme",["scheme_id","medicine_id","service_id","scheme_name","scheme_item_code","active","restricted","prices"])

  return _Scheme(
    scheme_id = db_scheme.scheme_id,
    medicine_id = db_scheme.medicine_id,
    service_id = db_scheme.service_id,
    scheme_name = db_scheme.scheme_name,
    scheme_item_code = db_scheme.scheme_item_code,
    active = db_scheme.active,
    restricted = db_scheme.restricted,
    prices = sorted([unmodel_pricing(db_pricing) for db_pricing in db_scheme.prices],key=lambda pricing:pricing.log_date,reverse=True)
  )

def unmodel_pricing(db_pricing:Pricing):
  """"""
  _Pricing = namedtuple("_Pricing",["scheme_id","logger","log_date","active","copayment","price_range","min","max","standard","priority","topup"])

  return _Pricing(
    scheme_id = db_pricing.scheme_id,
    logger = db_pricing.logger,
    log_date = db_pricing.log_date,
    active = db_pricing.active,
    copayment = db_pricing.copayment,
    price_range = db_pricing.price_range,
    min = db_pricing.min,
    max = db_pricing.max,
    standard = db_pricing.standard,
    priority = db_pricing.priority,
    topup = db_pricing.topup
  )

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

def unmodel_department(db_department:Department):
  
  _Department = namedtuple("_Department",["department_id","facility_id","name","display_name","display_icon","active","clinical","head_of_department","sections"])
  
  return _Department(
    department_id = db_department.department_id,
    facility_id = db_department.facility_id,
    name = db_department.name,
    display_name = db_department.display_name,
    display_icon = db_department.display_icon,
    active = db_department.active,
    clinical = db_department.clinical,
    head_of_department = db_department.head_of_department,
    sections = [unmodel_department_section(db_section) for db_section in db_department.sections]
  )

def unmodel_department_section(db_section:DepartmentSection):

  _DepartmentSection =  namedtuple("_DepartmentSection",["section_id","department_id","name","display_name","display_icon","active","head_of_section","consultation_rooms","wards"])

  return _DepartmentSection(
    section_id = db_section.section_id,
    department_id = db_section.department_id,
    name = db_section.name,
    display_name = db_section.display_name,
    display_icon = db_section.display_icon,
    active = db_section.active,
    head_of_section = db_section.head_of_section,
    consultation_rooms = [unmodel_consultation_room(db_room) for db_room in db_section.consultation_rooms],
    wards = [unmodel_ward(db_ward) for db_ward in db_section.wards]
  )

def unmodel_ward(db_ward:Ward):

  _Ward = namedtuple("_Ward",["ward_id","section_id","ward_no","name","ward_in_charge","icu","sub_icu","hdu","isolation","general","assets"])

  return _Ward(
    ward_id = db_ward.ward_id,
    section_id = db_ward.section_id,
    ward_no = db_ward.ward_no,
    name = db_ward.name,
    ward_in_charge = db_ward.ward_in_charge,
    icu = db_ward.icu,
    sub_icu = db_ward.sub_icu,
    hdu = db_ward.hdu,
    isolation = db_ward.isolation,
    general = db_ward.general,
    assets = [unmodel_asset(db_asset) for db_asset in db_ward.assets]
  )

def unmodel_consultation_room(db_room:ConsultationRoom):

  _ConsultationRoom = namedtuple("_ConsultationRoom",["room_id","section_id","room_no","name","operational","for_priority_clients","occupied","occupied_by","assets"])

  return _ConsultationRoom(
    room_id = db_room.room_id,
    section_id = db_room.section_id,
    room_no = db_room.room_no,
    name = db_room.name,
    operational = db_room.operational,
    for_priority_clients = db_room.for_priority_clients,
    occupied = db_room.occupied,
    occupied_by = db_room.occupied_by,
    assets = [unmodel_asset(db_asset) for db_asset in db_room.assets]
  )

def unmodel_asset(db_asset:Asset):

  _Asset = namedtuple("_Asset",["asset_id","facility_id","department_id","ward_id","room_id","name"])

  return _Asset(
    asset_id = db_asset.asset_id,
    facility_id = db_asset.facility_id,
    department_id = db_asset.department_id,
    ward_id = db_asset.ward_id,
    room_id = db_asset.room_id,
    name = db_asset.name
  )



