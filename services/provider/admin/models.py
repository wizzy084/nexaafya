"""A module for formatting and storing users in databse"""
#IMPORTS
from sqlmodel import Column,Field,ForeignKey,Integer,JSON,String,Relationship,SQLModel
from datetime import datetime,date,time
from typing import Any,Optional,Union


#MODELS
class User(SQLModel,table=True,extend_existing=True):
  """A model class for user"""

  __tablename__:str = "users"
  
  id:int|None = Field(default=None,primary_key=True)
  username:str|None = Field(default=None,unique=True)
  title:str|None = None
  qualification:str|None = None
  designation:str|None = None
  first_name:str|None = None
  middle_name:str|None = None
  last_name:str|None = None
  birthdate:datetime|None = None
  gender:str|None = None
  email:str|None = None
  mobile:str|None = None
  password:str|None = None
  photo:str|None = None
  roles:str|None = None
  is_super:bool = False
  registered_on:datetime|None = None
  active:bool = True
  suspended:bool = False
  
  logins:list["Login"] = Relationship(back_populates="user",sa_relationship_kwargs={"cascade":"all,delete"})

class Login(SQLModel,table=True,extend_existing=True):
  """A model class for login"""

  id:int|None = Field(default=None,primary_key=True)
  login_id:str|None = Field(default=None,unique=True)
  username:str|None = Field(default=None,sa_column=Column(String,ForeignKey("users.username",ondelete="CASCADE")))

  logged:bool = True
  login_time:datetime|None = None
  logout_time:datetime|None = None
  login_ip:str|None = None
  logout_ip:str|None = None

  user:User|None = Relationship(back_populates="logins")

class Service(SQLModel,table=True,extend_existing=True):
  """A model for storing details of service(s)"""

  id:int|None = Field(default=None)
  service_id:str|None = Field(default=None,primary_key=True)
  name:str|None = Field(default=None,unique=True)
  alternative_name:str|None = None
  type:str|None = None
  active:bool = True
  
  schemes:list["Scheme"] = Relationship(back_populates="service",sa_relationship_kwargs={"cascade":"all,delete"})

class Formulary(SQLModel,table=True,extend_exisiting=True):
  """A model to store and retrieve data from formulary table in database"""

  id:int|None = Field(default=None,primary_key=True)
  medicine_id:str|None = Field(default=None,unique=True)

  name:str|None = None
  type:str|None = None
  category:str|None = None
  drug_class:str|None = None
  fda_pregnancy_category_1:str|None = None
  fda_pregnancy_category_2:str|None = None
  fda_pregnancy_category_3:str|None = None
  prescribable:bool = True
  prescription_level:str|None = None
  active:bool = True

  schemes:list["Scheme"] = Relationship(back_populates="medicine",sa_relationship_kwargs={"cascade":"all,delete"})
  inventory:list["Inventory"] = Relationship(back_populates="medicine",sa_relationship_kwargs={"cascade":"all,delete"})

class Inventory(SQLModel,table=True,extend_existing=True):
  """A model for storing inventory ledger details of consumable items (variable assets???)"""

  id:int|None = Field(default=None,primary_key=True)
  medicine_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("formulary.medicine_id",ondelete="CASCADE")))

  invoice:str = "nexasoft001"               #nexasoft is the default in the initial setup
  issuer:str|None = "nexasoft"                   #vendor|main store|dispensing_store
  receiver:str|None = "main store"               #main store|dispensing store|client

  issuer_previous_amount:int = 0
  issuer_current_amount:int = 0
  receiver_previous_amount:int = 0
  receiver_current_amount:int = 0

  received:bool = False
  transfer:bool = False
  dispensed:bool = False
  count:bool = False
  default:bool = False

  date:datetime = datetime.now()
  logger:str|None = None

  medicine:Formulary|None = Relationship(back_populates="inventory")

class Requisition(SQLModel,table=True,extend_existing=True):
  """A model for storing procurement details"""

  id:int|None = Field(default=None,primary_key=True)
  requisition_id:str|None = Field(default=None,unique=True)
  delivery_note_id:str|None = None
  invoice_id:str|None = None
  vendor:str|None = None

  paid:bool = False
  billed:bool = False
  paid_amount:float = 0
  billed_amount:float = 0
  
  initiated:bool = False
  cancelled:bool = False
  placed:bool = False
  received:bool = False
  initiation_date:datetime|None = None
  cancel_date:datetime|None = None
  placement_date:datetime|None = None
  receive_date:datetime|None = None
  initiated_by:str|None = None
  cancelled_by:str|None = None
  placed_by:str|None = None
  received_by:str|None = None
  closed:bool = False  #True if store_balance + dispensing_balance = 0 for all medicines in a given requisition

  medicines:list["Medicine"] = Relationship(back_populates="requisition",sa_relationship_kwargs={"cascade":"all,delete"})
  stationeries:list["Stationery"] = Relationship(back_populates="requisition",sa_relationship_kwargs={"cascade":"all,delete"})

class Medicine(SQLModel,table=True,extend_existing=True):
  """A model for storing medicine studies"""

  id:int|None = Field(default=None,primary_key=True)
  medicine_id:str|None = Field(default=None)
  requisition_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("requisition.requisition_id",ondelete="CASCADE")))
  requisition_medicine_id:str|None = Field(default=None,unique=True)

  name:str|None = None
  type:str|None = None
  category:str|None = None
  drug_class:str|None = None
  fda_pregnancy_category_1:str|None = None
  fda_pregnancy_category_2:str|None = None
  fda_pregnancy_category_3:str|None = None
  prescription_level:str|None = None
  
  cancelled:bool = False
  cancelled_by:str|None = None
  cancelled_on:str|None = None
  ordered:bool = False
  ordered_on:datetime|None = None
  ordered_by:str|None = None
  order_unit:str|None = None
  order_unit_size:float = 0
  ordered_amount:float = 0
  unit_price:float = 0
  ordered_price:float = 0
  received:bool = False
  received_amount:float = 0
  received_price:float = 0
  received_by:str|None = None
  received_on:datetime|None = None
  rejected:bool = False
  rejected_amount:float = 0   #Change to rejection_reasons
  rejected_price:float = 0
  brand_name:str|None = None
  mfg_date:date|None = None
  manufacturer:str|None = None
  batch_no:str|None = None
  expire_date:date|None = None
  active:bool = False
  
  initial_store_balance:float = 0
  store_balance:float = 0
  average_monthly_consumption:float = 0
  average_daily_consumption:float = 0
  dispensing_balance:float = 0
  physical_count:float = 0
  count_unit:str|None = None
  counted_by:str = "nexasoft"
  physical_count_date:datetime|None = None

  requisition:Requisition|None = Relationship(back_populates="medicines")

class Stationery(SQLModel,table=True,extend_existing=True):
  """A model for storing stationeries"""

  id:int|None = Field(default=None,primary_key=True)
  stationery_id:str|None = Field(default=None,unique=True)
  requisition_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("requisition.requisition_id",ondelete="CASCADE")))
  
  cancelled:bool = False
  cancelled_by:str|None = None
  cancelled_on:datetime|None = None
  ordered:bool = False
  ordered_by:str|None = None
  ordered_on:datetime|None = None
  ordered_amount:float = 0
  ordered_price:float = 0
  received:bool = False
  received_by:str|None = None
  received_on:datetime|None = None
  received_amount:float = 0
  received_price:float = 0
  rejected:bool = False,
  rejected_amount:float = 0
  rejected_price:float = 0
  brand_name:str|None = None

  store_balance:float = 0
  average_monthly_consumption:float = 0
  average_daily_consumption:float = 0
  dispensing_balance:float = 0
  physical_count:float = 0
  buying_price:float|None = None

  requisition:Requisition|None = Relationship(back_populates="stationeries")

class Scheme(SQLModel,table=True,extend_exisiting=True):
  """A model to store and retrieve data from paymentscheme table in database"""

  id:int|None = Field(default=None,primary_key=True)
  scheme_id:str|None = Field(default=None,unique=True)

  medicine_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("formulary.medicine_id",ondelete="CASCADE")))
  service_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("service.service_id",ondelete="CASCADE")))

  scheme_name:str|None = Field(default=None)
  scheme_item_code:str|None = None
  active:bool = True
  restricted:bool = False
  
  medicine:Formulary|None = Relationship(back_populates="schemes")
  service:Service|None = Relationship(back_populates="schemes")
  prices:list["Pricing"] = Relationship(back_populates="scheme",sa_relationship_kwargs={"cascade":"all,delete"})

class Pricing(SQLModel,table=True,extend_exisiting=True):
  """A model to store and retrieve data from pricing table in database"""

  id:int|None = Field(default=None,primary_key=True)
  scheme_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("scheme.scheme_id",ondelete="CASCADE")))
  log_date:datetime = datetime.now()
  logger:str = "nexasoft"
  active:bool = True 

  copayment:bool = False
  price_range:bool = False
  min:float = 0
  max:float = 0
  standard:float = 0
  priority:float = 0
  topup:float = 0

  scheme:Scheme|None = Relationship(back_populates="prices")

class ICD10Diagnosis(SQLModel,table=True,extend_existing=True):
  """A model for storing imaging studies"""

  id:int|None = Field(default=None,primary_key=True)
  code:str|None = None
  name:str|None = None

class ICD11Diagnosis(SQLModel,table=True,extend_existing=True):
  """A model for storing imaging studies"""

  id:int|None = Field(default=None,primary_key=True)
  code:str|None = None
  name:str|None = None





