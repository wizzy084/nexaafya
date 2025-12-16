"""A module for processing backgroundtasks"""

#GENERAL IMPORTS
import string,time
from datetime import datetime

#APP IMPORTS
from .provider.admin.db import register_icd_diagnosis
from .provider.admin.processor import get_diagnoses
from .provider.clients.db import update_visit,update_appointment_status
from .provider.clients.processor import get_active_visits,get_appointments


#

#ENDING ACTIVE VISITS
def expire_sessions():
  """"""

  while True:
    #visits
    to_be_expired_visits = [visit for visit in get_active_visits() if (datetime.now() - visit.start_time).days >= 1]

    for visit in to_be_expired_visits:
      update_visit({"visit_id":visit.visit_id},close=True)

    #Appointments
    expired_appointments = [appointment for appointment in get_appointments() if (datetime.now() - appointment.appointment_time).days >= 1]
    for appointment in expired_appointments:
      appointment = appointment._asdict()
      appointment["cancelled"] = True
      update_appointment_status(appointment)


    
    
    