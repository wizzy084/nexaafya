"""A module for processing backgroundtasks"""

#GENERAL IMPORTS
import string,time
from datetime import datetime
from simple_icd_11 import ICDExplorer

#APP IMPORTS
from .provider.admin.db import register_icd_diagnosis
from .provider.admin.processor import get_diagnoses
from .provider.clients.db import update_visit,update_appointment_status
from .provider.clients.processor import get_active_visits,get_appointments


#
#Storing ICD diagnoses
def store_icd_diagnoses():
  icd11explorer = ICDExplorer(
    language="en",
    clientId='b3aa23fa-4c0f-461a-8430-8951dabc3eca_fa7b99fe-ad61-49bf-b4dd-cf28d659eecd',
    clientSecret='PL8CRymESvOZ36aHJyOqosyBKObSJW0YfbUBTKHzZEQ='
  )
  
  db_codes = [code.split(":")[0].lower() for code in get_diagnoses()] if get_diagnoses() else []
  alphanums = string.ascii_lowercase + string.digits
  _codes = []
  
  #Creating base_icds
  #1st character
  for char_1 in alphanums:
    if char_1 > '0' and char_1 < 'q':
      #2nd character
      for char_2 in alphanums:
        if char_2.isalpha() and char_2 < 'n':
          #3rd character
          for char_3 in alphanums:
            if char_3.isdigit():
              #Fine tune#
              if (char_1 + char_2 == "ac") and int(char_3) > 0:
                break
              #4th character
              for char_4 in alphanums:
                if (char_4.isdigit() and int(char_4) < 7) or char_4 in ["y","z"]:
                  _code = f"{char_1}{char_2}{char_3}{char_4}"
                  _codes.append(_code)
  
  #Filters
  base_codes = [code for code in _codes if code not in db_codes]
  #print([x for x in _codes if x.startswith('ac')])

  #Storing
  counter=0
  print(f"FROM DB:{len(db_codes)}\nPOSSIBLES:{len(_codes)}")
  try:
    print("HERE WE GO...!!!")
    for base_code in base_codes:
      if icd11explorer.isValidCode(base_code):
        counter += 1
        base_entity = icd11explorer.getEntityFromCode(base_code)
        counter += 1
        #Register base code
        register_icd_diagnosis(
            diagnosis={"name":base_entity.getTitle().lower(),"code":base_entity.getCode().lower()}
          )
        counter+=1
        #Register entity children
        if base_entity.getChildren():
          counter+=1
          for entity in base_entity.getChildren():
            register_icd_diagnosis(
              diagnosis={"name":entity.getTitle().lower(),"code":entity.getCode().lower()}
            )
        print(base_code)
      
      if counter > 50:
        print('HOLD OON...!!!')
        counter = 0
        time.sleep(30)
  except:
    print(f"Requests:{counter}")
          



#ENDING ACTIVE VISITS
def expire_sessions():
  """"""

  while True:
    #visits
    to_be_expired_visits = [visit for visit in get_active_visits() if (datetime.now() - visit.start_time).days >= 1]

    for visit in to_be_expired_visits:
      update_visit({"visit_id":visit.visit_id,"active":False})

    #Appointments
    expired_appointments = [appointment for appointment in get_appointments() if (datetime.now() - appointment.appointment_time).days >= 1]
    for appointment in expired_appointments:
      appointment = appointment._asdict()
      appointment["cancelled"] = True
      update_appointment_status(appointment)


    
    
    