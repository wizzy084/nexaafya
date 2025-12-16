"""A module to populate or modify database tables en masse"""

#GENERAL IMPORTS
from datetime import datetime
from sqlalchemy import Boolean,ExceptionContext
from sqlalchemy.engine.base import Engine
from sqlmodel import func,Session,SQLModel
import uuid

#IN-PROJECT IMPORTS
from ._snippets import *
from services.provider.configs import database_engine


#REGISTERING FUNCTIONS
def register_client(client:dict):
  """A function that intergrates 'feed_clilent' and 'feed_next_kin' to store data from 'client' in the respectivedatabase tables"""
  
  db_client = Client(
      created_on=datetime.now(),
      first_name=client["first_name"].lower(),
      middle_name=client["middle_name"].lower(),
      last_name=client["last_name"].lower(),
      client_id=client["client_id"],
      birthdate=client["birthdate"],
      gender=client["gender"].lower(),
      marital_status=client["marital_status"].lower(),
      occupation=client["occupation"],
      mobile= client["mobile"],
      address=client["address"].lower(),
      payment_mode=client["payment_mode"].lower(),
      card_no = client["card_no"]
    )
  
  try:
    with Session(database_engine) as session:
      if list(session.exec(select(Client).where(Client.client_id == db_client.client_id)).all()):
        return {"status":True,"message":"Client already registered!","type":"warning","position":"center"}
      else:
        session.add(db_client)
        session.commit()
    
    return {"status":True,"message":"Client registered successfully!","type":"positive","position":"top"}
  
  except:
    return {"status":False,"message":"Client not registered!","type":"negative","position":"center"}


def feed_next_kin(next_kin:dict,db_client:Client):
  """Adds details of 'next_kin' to create new row in 'next_of_kin' table in database"""

  db_next_kin = NextOfKin(
    next_kin_id = next_kin["next_kin_id"],
    first_name=next_kin["first_name"],
    last_name=next_kin["last_name"],
    relation=next_kin["relation"],
    mobile=f"{next_kin['dial_code']}{next_kin['mobile_no']}",
    client_id=db_client.client_id,
  )

  with Session(database_engine) as session:
    if session.exec(select(NextOfKin).where(NextOfKin.next_kin_id == db_next_kin.next_kin_id)).all():
      return
    else:
      session.add(db_next_kin)
      session.commit()

def feed_visit(visit:dict):
  """Adds details of 'next_kin' to create new row in 'next_of_kin' table in database"""
  
  db_visit = Visit(
    client_id = visit["client_id"],
    visit_id = visit["visit_id"],
    start_time = datetime.now(),
    payment_mode = visit["payment_mode"],
    package = visit["package"].lower(),
    prescription_no = f"{visit['client_id']}{str(uuid.uuid4()).split('-')[1]}",
    attendee_id = visit["attendee_id"]
  )
  

  with Session(database_engine) as session:
    if session.exec(select(Visit).where(Visit.visit_id == db_visit.visit_id)).all():
      return
    else:
      session.add(db_visit)
      session.commit()

def feed_appointment(appointment:dict):
  """Adds details of 'next_kin' to create new row in 'next_of_kin' table in database"""

  db_appointment = Appointment(
    client_id = appointment["client_id"],
    appointment_id = appointment["appointment_id"],
    created_on = datetime.now(),
    appointment_time = appointment["date"],
    attendee_id = appointment["attendee_id"],
  )

  with Session(database_engine) as session:
    if session.exec(select(Appointment).where(Appointment.appointment_id == db_appointment.appointment_id)).all():
      return
    else:
      session.add(db_appointment)
      session.commit()

def feed_payment(payment:dict,consultation_id:str|None=None,anthropometrics_id:str|None=None,vitals_id:str|None=None,lab_id:str|None=None,imaging_id:str|None=None,procedure_id:str|None=None,surgery_id:str|None=None,medication_id:str|None=None,medical_item_id:str|None=None,nonpharmacological_id:str|None=None):
  """Adds details of 'payment' to create new row in 'payment' table in database"""

  db_payment = Payment(
    visit_id = payment["visit_id"],
    payment_id = payment["payment_id"],
    consultation_id = consultation_id,
    anthropometrics_id = anthropometrics_id,
    vitals_id = vitals_id,
    lab_id = lab_id,
    imaging_id = imaging_id,
    procedure_id = procedure_id,
    surgery_id = surgery_id,
    medication_id = medication_id,
    medical_item_id = medical_item_id,
    nonpharmacological_id = nonpharmacological_id,
    created_on = datetime.now(),
    cost = payment["cost"],
    authorization_no = payment["authorization_no"],
    payment_mode = payment["payment_mode"],
    billed = payment["billed"],
    billed_amount = payment["cost"] if payment["billed"] else 0,
    billing_time = datetime.now() if payment["billed"] else None,
    paid = payment["paid"] if "paid" in payment else False,
    paid_amount = payment["cost"] if "paid" in payment else 0,
    payment_time = datetime.now() if "paid" in payment else None,
  )


  with Session(database_engine) as session:
    if session.exec(select(Payment).where(Payment.payment_id == db_payment.payment_id)).all():
      return
    else:
      session.add(db_payment)
      session.commit()

def feed_vital_signs(vital_signs:dict):
  """Creates a row in vitalsigns table and populate it with 'vital_signs' data"""

  db_vital_signs = VitalSigns(
    visit_id = vital_signs["visit_id"],
    vitals_id = vital_signs["vitals_id"]
  )

  with Session(database_engine) as session:
    if session.exec(select(VitalSigns).where(VitalSigns.vitals_id == db_vital_signs.vitals_id)).all():
      return
    else:
      session.add(db_vital_signs)
      session.commit()

def feed_anthropometrics(anthropometrics:dict):
  """Creates a row in anthropometrics table and populate it with 'anthropometrics' data"""

  db_anthropometrics = Anthropometrics(
    visit_id = anthropometrics["visit_id"],
    anthropometrics_id = anthropometrics["anthropometrics_id"]
  )

  with Session(database_engine) as session:
    if session.exec(select(Anthropometrics).where(Anthropometrics.anthropometrics_id == db_anthropometrics.anthropometrics_id)).all():
      return
    else:
      session.add(db_anthropometrics)
      session.commit()

def feed_consultation(consultation:dict):
  """Creates a row in consultation table and populate it with 'consultation' data"""

  db_consultation = Consultation(
    consultation_id = consultation["consultation_id"],
    visit_id = consultation["visit_id"],
    name = consultation["name"]
  )

  with Session(database_engine) as session:
    if session.exec(select(Consultation).where(Consultation.consultation_id == db_consultation.consultation_id)).all():
      return
    else:
      session.add(db_consultation)
      session.commit()

def feed_clinical_history(clinical_history:dict):
  """Creates a row in clinicalhistory table and populate it with 'clinical_history' data"""

  db_clinical_history = ClinicalHistory(
    consultation_id = clinical_history["consultation_id"],
    hx_id = clinical_history["hx_id"],
  )

  with Session(database_engine) as session:
    if session.exec(select(ClinicalHistory).where(ClinicalHistory.hx_id == db_clinical_history.hx_id)).all():
      return
    else:
      session.add(db_clinical_history)
      session.commit()

def feed_general_exam(general_exam:dict):
  """Creates a row in generalexamination table and populate it with 'general_exam' data"""

  db_general_exam = GeneralExamination(
    consultation_id = general_exam["consultation_id"],
    ge_id = general_exam["ge_id"],
  )

  with Session(database_engine) as session:
    if session.exec(select(GeneralExamination).where(GeneralExamination.ge_id == db_general_exam.ge_id)).all():
      return
    else:
      session.add(db_general_exam)
      session.commit()

def feed_orodental_exam(orodental_exam:dict):
  """Creates a row in orodentalexamination table and populate it with 'orodental_exam' data"""

  db_orodental_exam = OrodentalExamination(
    consultation_id = orodental_exam["consultation_id"],
    orodental_exam_id = orodental_exam["orodental_exam_id"],
  )

  with Session(database_engine) as session:
    if session.exec(select(OrodentalExamination).where(OrodentalExamination.orodental_exam_id == db_orodental_exam.orodental_exam_id)).all():
      return
    else:
      session.add(db_orodental_exam)
      session.commit()

def feed_cns_exam(cns_exam:dict):
  """Creates a row in cnsexamination table and populate it with 'cns_exam' data"""

  db_cns_exam = CNSExamination(
    consultation_id = cns_exam["consultation_id"],
    cns_exam_id = cns_exam["cns_exam_id"],
  )

  with Session(database_engine) as session:
    if session.exec(select(CNSExamination).where(CNSExamination.cns_exam_id == db_cns_exam.cns_exam_id)).all():
      return
    else:
      session.add(db_cns_exam)
      session.commit()

def feed_cvs_exam(cvs_exam:dict):
  """Creates a row in cardiovascularexamination table and populate it with 'cvs_exam' data"""

  db_cvs_exam = CardiovascularExamination(
    consultation_id = cvs_exam["consultation_id"],
    cvs_exam_id = cvs_exam["cvs_exam_id"]
  )

  with Session(database_engine) as session:
    if session.exec(select(CardiovascularExamination).where(CardiovascularExamination.cvs_exam_id == db_cvs_exam.cvs_exam_id)).all():
      return
    else:
      session.add(db_cvs_exam)
      session.commit()

def feed_rs_exam(rs_exam:dict):
  """Creates a row in respiratoryexamination table and populate it with 'rs_exam' data"""

  db_rs_exam = RespiratoryExamination(
    consultation_id = rs_exam["consultation_id"],
    rs_exam_id = rs_exam["rs_exam_id"]
  )

  with Session(database_engine) as session:
    if session.exec(select(RespiratoryExamination).where(RespiratoryExamination.rs_exam_id == db_rs_exam.rs_exam_id)).all():
      return
    else:
      session.add(db_rs_exam)
      session.commit()

def feed_abd_exam(abd_exam:dict):
  """Creates a row in abdominalexamination table and populate it with 'abd_exam' data"""

  db_abd_exam = AbdominalExamination(
    consultation_id = abd_exam["consultation_id"],
    abd_exam_id = abd_exam["abd_exam_id"]
  )

  with Session(database_engine) as session:
    if session.exec(select(AbdominalExamination).where(AbdominalExamination.abd_exam_id == db_abd_exam.abd_exam_id)).all():
      return
    else:
      session.add(db_abd_exam)
      session.commit()

def feed_gus_exam(gus_exam:dict):
  """Creates a row in genitourinaryexamination table and populate it with 'gus_exam' data"""

  db_gus_exam = GenitourinaryExamination(
    consultation_id = gus_exam["consultation_id"],
    gus_exam_id = gus_exam["gus_exam_id"]
  )

  with Session(database_engine) as session:
    if session.exec(select(GenitourinaryExamination).where(GenitourinaryExamination.gus_exam_id == db_gus_exam.gus_exam_id)).all():
      return
    else:
      session.add(db_gus_exam)
      session.commit()

def feed_mss_exam(mss_exam:dict):
  """Creates a row in musculoskeletalexamination table and populate it with 'mss_exam' data"""

  db_mss_exam = MusculoskeletalExamination(
    consultation_id = mss_exam["consultation_id"],
    mss_exam_id = mss_exam["mss_exam_id"]
  )

  with Session(database_engine) as session:
    if session.exec(select(MusculoskeletalExamination).where(MusculoskeletalExamination.mss_exam_id == db_mss_exam.mss_exam_id)).all():
      return
    else:
      session.add(db_mss_exam)
      session.commit()

def feed_derma_exam(derma_exam:dict):
  """Creates a row in dermatologicalexamination table and populate it with 'derma_exam' data"""

  db_derma_exam = DermatologicalExamination(
    consultation_id = derma_exam["consultation_id"],
    derma_exam_id = derma_exam["derma_exam_id"]
  )

  with Session(database_engine) as session:
    if session.exec(select(DermatologicalExamination).where(DermatologicalExamination.derma_exam_id == db_derma_exam.derma_exam_id)).all():
      return
    else:
      session.add(db_derma_exam)
      session.commit()

def feed_lab_workup(lab_workup:dict):
  """Creates a row in laboratory table and populate it with 'lab_workup' data"""

  db_lab_workup = Laboratory(
    visit_id = lab_workup["visit_id"],
    lab_id = lab_workup["lab_id"],
    attendee_id = lab_workup["attendee_id"],
    test = lab_workup["test"],
    request_time = datetime.now(),
  )

  with Session(database_engine) as session:
    if session.exec(select(Laboratory).where(Laboratory.lab_id == db_lab_workup.lab_id)).all():
      return
    else:
      session.add(db_lab_workup)
      session.commit()

def feed_imaging(imaging:dict):
  """Creates a row in imaging table and populate it with 'imaging' data"""

  db_imaging = Imaging(
    visit_id = imaging["visit_id"],
    imaging_id = imaging["imaging_id"],
    attendee_id = imaging["attendee_id"],
    study = imaging["study"],
    notes = imaging["notes"],
    request_time = datetime.now(),
  )

  with Session(database_engine) as session:
    if session.exec(select(Imaging).where(Imaging.imaging_id == db_imaging.imaging_id)).all():
      return
    else:
      session.add(db_imaging)
      session.commit()

def feed_diagnosis(diagnosis:dict):
  """Creates a row in diagnosis table and populate it with 'diagnosis' data"""

  db_diagnosis = Diagnosis(
    consultation_id = diagnosis["consultation_id"],
    diagnosis_id = diagnosis["diagnosis_id"],
    provisional = diagnosis["provisional"],
    provisional_generic = diagnosis["provisional_generic"],
    provisional_icd = diagnosis["provisional_icd"],
    differentials = diagnosis["differentials"]
  )

  with Session(database_engine) as session:
    if session.exec(select(Diagnosis).where(Diagnosis.diagnosis_id == db_diagnosis.diagnosis_id)).all():
      return
    else:
      session.add(db_diagnosis)
      session.commit()

def feed_procedure(procedure:dict):
  """Creates a row in procedure table and populate it with 'procedure' data"""
  
  db_procedure = Procedure(
    visit_id = procedure["visit_id"],
    procedure_id = procedure["procedure_id"],
    attendee_id = procedure["attendee_id"],
    name = procedure["name"],
    count = int(procedure["count"]),
    ordered_on = datetime.now()
  )
  
  with Session(database_engine) as session:
    if session.exec(select(Procedure).where(Procedure.procedure_id == db_procedure.procedure_id)).all():
      return
    else:
      session.add(db_procedure)
      session.commit()

def feed_surgery(surgery:dict,payment_id:str):
  """Creates a row in surgery table and populate it with 'surgery' data"""

  db_surgery = Surgery(
    visit_id = surgery["visit_id"],
    surgery_id = surgery["surgery_id"],
    payment_id = payment_id,
    attendee_id = surgery["attendee_id"],
    operation = surgery["operation"],
    planned_on = datetime.now(),
  )

  with Session(database_engine) as session:
    if session.exec(select(Surgery).where(Surgery.surgery_id == db_surgery.surgery_id)).all():
      return
    else:
      session.add(db_surgery)
      session.commit()

def feed_medication(medication:dict):
  """Creates a row in medication table and populate it with 'medication' data"""

  db_medication = Medication(
    visit_id = medication["visit_id"],
    medication_id = medication["medication_id"],
    prescriber_id = medication["prescriber_id"],
    name = medication["name"],
    dosage = medication["dosage"],
    prescribed_items_no = medication["prescribed_items_no"],
    prescribed_on = datetime.now()
  )

  with Session(database_engine) as session:
    if session.exec(select(Medication).where(Medication.medication_id == db_medication.medication_id)).all():
      return
    else:
      session.add(db_medication)
      session.commit()

def feed_medical_item(medical_item:dict):
  """A funtion to utilize data from 'medical_item' dictionary to generate rows in medicalitem table"""

  db_medical_item = MedicalItem(
    medical_item_id = medical_item["medical_item_id"],
    visit_id = medical_item["visit_id"],
    prescriber_id = medical_item["prescriber_id"],
    name = medical_item["name"],
    prescribed_items_no = medical_item["prescribed_items_no"],
    prescribed_on = datetime.now()
  )

  with Session(database_engine) as session:
    if session.exec(select(MedicalItem).where(MedicalItem.medical_item_id == db_medical_item.medical_item_id)).all():
      return
    else:
      session.add(db_medical_item)
      session.commit()

def feed_nonpharmacological(nonpharmacological:dict):
  """Creates a row in nonpharmacological table and populate it with 'nonpharmacological' data"""

  db_nonpharmacological = NonPharmacological(
    visit_id = nonpharmacological["visit_id"],
    nonpharmacological_id = nonpharmacological["nonpharmacological_id"],
    attendee_id = nonpharmacological["attendee_id"],
    name = nonpharmacological["name"],
    planned_on = datetime.now(),
    done = nonpharmacological["done"],
    done_on = nonpharmacological["done_on"],
    notes = nonpharmacological["notes"]
  )

  with Session(database_engine) as session:
    if session.exec(select(NonPharmacological).where(NonPharmacological.nonpharmacological_id == db_nonpharmacological.nonpharmacological_id)).all():
      return
    else:
      session.add(db_nonpharmacological)
      session.commit()


#REGISTER/INITIATE FUNCTIONS
def register_visit(visit:dict):
  """Creates a row in 'visit' table and links to correspoinding row in 'client' table in database"""
  
  if visit["appointment_id"]:
    appointment = {"appointment_id":visit["appointment_id"],"cancelled":False,"done":True}
    update_appointment_status(appointment)

  #Visit
  with Session(database_engine) as session:
    db_client:Client = list(session.exec(select(Client).where(Client.client_id == int(visit["client_id"]))))[0]
    client_visit_count= len(db_client.visits)
    
    if client_visit_count > 0:
      latest_client_visit = db_client.visits[-1]
      if not latest_client_visit.active:
        feed_visit(visit)
        return {"status":True,"message":"Visit successfully initiated!","type":"positive","position":"top"}
      else:
        return {"status":False,"message":"There is an active visit! Close an active visit and try again!","type":"negative","position":"center"}
    else:
      feed_visit(visit)
      return {"status":True,"message":"Visit successfully initiated!","type":"positive","position":"top"}

    session.commit()

def register_appointment(appointment:dict):
  """Creates a new row in 'appointment' table in database using details from 'client_id' interger input"""
 
  with Session(database_engine) as session:
    if session.exec(select(Appointment).where(Appointment.client_id == appointment["client_id"]).where(func.date(Appointment.appointment_time) == datetime.now().date())).first():
      return {"message":"Client has appointment today!","caption":"View appointments tab","position":"top","type":"warning"}
    else:
      feed_appointment(appointment)
    
      return {"message":"Appointment made sucessfully! View it in appointments tab","type":"positive","position":"top"}

def register_consultation(consultation:dict):
  """Ata cjui cha kuandika"""
  
  #Consultation
  consultation_id = f"{consultation['visit_id']}c1"
  consultation["consultation_id"] = consultation_id
  feed_consultation(consultation)

  with Session(database_engine) as session:
    db_consultation:Consultation = list(session.exec(select(Consultation).where(Consultation.consultation_id == consultation_id)).all())[0]
    
    #Payment
    payment = consultation["payment"]
    payment["visit_id"] = consultation["visit_id"]
    payment["payment_id"] = f"{consultation_id}pay{len(db_consultation.visit.payments) + 1}"
    feed_payment(payment=payment,consultation_id=consultation_id)
    
    #Clinical history
    hx = consultation["hx"]
    hx["consultation_id"] = consultation_id
    hx["hx_id"] = f"{consultation_id}hx{len(db_consultation.clinical_histories) + 1}"
    feed_clinical_history(hx)

    #General exam
    ge = consultation["ge"]
    ge["consultation_id"] = consultation_id
    ge["ge_id"] = f"{consultation_id}ge{len(db_consultation.ge_exams) + 1}"
    feed_general_exam(ge)

    #Orodental exam
    orodental = consultation["orodental"]
    orodental["consultation_id"] = consultation_id
    orodental["orodental_exam_id"] = f"{consultation_id}od{len(db_consultation.orodental_exams) + 1}"
    feed_orodental_exam(orodental)

    #CNS exam
    cns = consultation["cns"]
    cns["consultation_id"] = consultation_id
    cns["cns_exam_id"] = f"{consultation_id}cns{len(db_consultation.cns_exams) + 1}"
    feed_cns_exam(cns)

    #CVS exam
    cvs = consultation["cvs"]
    cvs["consultation_id"] = consultation_id
    cvs["cvs_exam_id"] = f"{consultation_id}cvs{len(db_consultation.cvs_exams) + 1}"
    feed_cvs_exam(cvs)

    #RS exam
    rs = consultation["rs"]
    rs["consultation_id"] = consultation_id
    rs["rs_exam_id"] = f"{consultation_id}rs{len(db_consultation.rs_exams) + 1}"
    feed_rs_exam(rs)

    #ABD exam
    abd = consultation["abd"]
    abd["consultation_id"] = consultation_id
    abd["abd_exam_id"] = f"{consultation_id}abd{len(db_consultation.abd_exams) + 1}"
    feed_abd_exam(abd)

    #GUS exam
    gus = consultation["gus"]
    gus["consultation_id"] = consultation_id
    gus["gus_exam_id"] = f"{consultation_id}gus{len(db_consultation.gus_exams) + 1}"
    feed_gus_exam(gus)

    #MSS exam
    mss = consultation["mss"]
    mss["consultation_id"] = consultation_id
    mss["mss_exam_id"] = f"{consultation_id}mss{len(db_consultation.mss_exams) + 1}"
    feed_mss_exam(mss)

    #DERMA exam
    derma = consultation["derma"]
    derma["consultation_id"] = consultation_id
    derma["derma_exam_id"] = f"{consultation_id}derma{len(db_consultation.derma_exams) + 1}"
    feed_derma_exam(derma)

    session.commit()

def register_triage(triage:dict,initial:bool=False):
  """Create new rows in vitalsigns and anthropometrics"""
  
  if "vitals" in triage:
    if initial:
      feed_vital_signs(triage["vitals"])
      feed_payment(payment=triage["vitals"]["payment"],vitals_id=triage["vitals"]["vitals_id"])
    else:
      with Session(database_engine) as session:
        db_vitals = list(session.exec(select(VitalSigns).where(VitalSigns.visit_id == triage["vitals"]["visit_id"])).all())
        last_db_vital:VitalSigns = db_vitals[-1] if db_vitals else None

        if last_db_vital:
          if not last_db_vital.done:
            triage["vitals"]["vitals_id"] = last_db_vital.vitals_id
            triage.pop("anthropometrics")
            update_triage(triage)
          else:
            feed_vital_signs(triage["vitals"])
            feed_payment(payment=triage["vitals"]["payment"],vitals_id=triage["vitals"]["vitals_id"])
        
  if "anthropometrics" in triage:
    if initial:
      feed_anthropometrics(triage["anthropometrics"])
      feed_payment(payment=triage["anthropometrics"]["payment"],anthropometrics_id=triage["anthropometrics"]["anthropometrics_id"])
    else:
      with Session(database_engine) as session:
        db_anthrops = list(session.exec(select(Anthropometrics).where(Anthropometrics.visit_id == triage["anthropometrics"]["visit_id"])).all())
        last_db_anthrop:Anthropometrics = db_anthrops[-1] if db_anthrops else None

        if last_db_anthrop:
          if not last_db_anthrop.done:
            triage["anthropometrics"]["anthropometrics_id"] = last_db_anthrop.anthropometrics_id
            triage.pop("vitals")
            update_triage(triage)
          else:
            feed_anthropometrics(triage["anthropometrics"])
            feed_payment(payment=triage["anthropometrics"]["payment"],anthropometrics_id=triage["anthropometrics"]["anthropometrics_id"])
        
        
def register_vitals(vitals:dict):
  """"""

  with Session(database_engine) as session:
    db_visit:Visit = list(session.exec(select(Visit).where(Visit.visit_id == vitals["visit_id"])).all())[0]
    
    #Vitals
    vitals_id = f"{vitals['visit_id']}v{len(db_visit.vital_signs) + 1}"
    vitals["vitals_id"] = vitals_id
    feed_vital_signs(vitals)

    #Payment
    vitals["payment_id"] = f"{vitals_id}pay{len(db_visit.payments) + 1}"
    feed_payment(payment=vitals,vitals_id=vitals_id)
    
    session.commit()

def register_anthropometrics(anthropometrics:dict):
  """"""

  with Session(database_engine) as session:
    db_visit:Visit = list(session.exec(select(Visit).where(Visit.visit_id == anthropometrics["visit_id"])).all())[0]
    
    #Vitals
    anthropometrics_id = f"{anthropometrics['visit_id']}anthrop{len(db_visit.anthropometrics) + 1}"
    anthropometrics["anthropometrics_id"] = anthropometrics_id
    feed_anthropometrics(anthropometrics)

    #Payment
    anthropometrics["payment_id"] = f"{anthropometrics_id}pay{len(db_visit.payments) + 1}"
    feed_payment(payment=anthropometrics,anthropometrics_id=anthropometrics_id)
    
    session.commit()

def register_labwork(lab:dict):
  """"""

  with Session(database_engine) as session:
    db_visit:Visit = list(session.exec(select(Visit).where(Visit.visit_id == lab["visit_id"])).all())[0]
    
    #Vitals
    lab_id = f"{lab['visit_id']}v{len(db_visit.laboratory_tests) + 1}"
    lab["lab_id"] = lab_id
    feed_lab_workup(lab)

    #Payment
    lab["payment_id"] = f"{lab_id}pay{len(db_visit.payments) + 1}"
    feed_payment(payment=lab,lab_id=lab_id)
    
    session.commit()

def np_present(np_id:str):

  with Session(database_engine) as session:
    if session.exec(select(NonPharmacological).where(NonPharmacological.nonpharmacological_id == nonpharmacological["nonpharmacological_id"])).all():
      return True
    else:
      return False

def register_nonpharmacological(nonpharmacological:dict):
  """"""
  print(np_present(nonpharmacological['nonpharmacological_id']))
  if np_present(nonpharmacological["nonpharmacological_id"]):
    with Session(database_engine) as session:
      db_nonpharmacological:NonPharmacological = list(session.exec(select(NonPharmacological).where(NonPharmacological.nonpharmacological_id == nonpharmacological["nonpharmacological_id"])).all())[0]

      db_nonpharmacological.notes = nonpharmacological["notes"]

      session.commit()

  else:
    feed_nonpharmacological(nonpharmacological)

    #Payment
    nonpharmacological["payment_id"] = f"{nonpharmacological['nonpharmacological_id']}pay{nonpharmacological['payments_count'] + 1}"
    feed_payment(payment=nonpharmacological,nonpharmacological_id=nonpharmacological["nonpharmacological_id"])
    
def register_payment(payment:dict):
  """Creates a new row in 'payment' table in database using details from 'visit_id' interger input"""
  
  with Session(database_engine) as session:
    db_visit:Visit = list(session.exec(select(Visit).where(Visit.visit_id == payment["visit_id"])))[0]
    db_visit_payments:list[Payment] = db_visit.payments
    if db_visit.payments:
      if payment["payment_id"] in [db_visit_payment.payment_id for db_visit_payment in list(db_visit.payments)]:
        return {"message":"Payment already exists!","type":"negative"}
      else:
        payment["payment_id"] = f"{payment['visit_id']}-pay{len(db_visit.payments) + 1}"
        feed_payment(payment,db_visit)
        return {"message":"Payment made sucessfully! View it in payments tab","type":"positive"}
    else:
      feed_payment(payment,db_visit)
      return {"message":"Payment made sucessfully! View it in payments tab","type":"positive"}
  
    session.commit()

def register_clinical_history(clinical_history:dict):
  """Retreives table row form 'clinicalhistory' table and updates the details from 'clinical_history' data"""

  with Session(database_engine) as session:
    db_history:ClinicalHistory = list(session.exec(select(ClinicalHistory).where(ClinicalHistory.hx_id == clinical_history["hx_id"])))[0]

    db_history.chief_complaints = clinical_history["complaints"]
    db_history.presenting_illness = clinical_history["hpi"]
    db_history.systems_review = clinical_history["ros"]
    db_history.medical_history = clinical_history["pmh"]
    db_history.family_history = clinical_history["fsh"]
    db_history.history_time = datetime.now()

    session.commit()

def register_chief_complaints(complaints:dict):
  """A function to create and feed row in clinicalhistory table at the column labelled 'chief_complaints'"""
  
  try:
    with Session(database_engine) as session:
      db_hx:ClinicalHistory = list(session.exec(select(ClinicalHistory).where(ClinicalHistory.hx_id == complaints["hx_id"])))[0]
      
      if complaints["complaints"]:
        db_hx.chief_complaints = complaints["complaints"]
        db_hx.history_time = datetime.now()

        #Initiate consultation
        update_consultation({"consultation_id":db_hx.consultation_id,"consultant_id":complaints["consultant_id"]})

        session.commit()
        return {"message":"Complaints saved!","type":"positive","position":"top"}
      else:
        db_hx.chief_complaints = None
        db_hx.history_time = None
        session.commit()
        return {"message":"No complaints filled","type":"negative","position":"center"}
  except:
    return {"message":"Complaints not saved!","type":"negative","position":"center"}

def register_hpi(hpi:dict):
  """A function to save hpi data in a row in clinicalhistory table where is hpi"""
  
  with Session(database_engine) as session:
    db_hx:ClinicalHistory = list(session.exec(select(ClinicalHistory).where(ClinicalHistory.hx_id == hpi["hx_id"])))[0]
    
    db_hx.hpi1 = hpi["hpi1"].lower() if hpi["hpi1"] else None
    db_hx.hpi2 = hpi["hpi2"].lower() if hpi["hpi2"] else None
    db_hx.hpi3 = hpi["hpi3"].lower() if hpi["hpi3"] else None
    db_hx.editor_id = hpi["editor_id"]
    db_hx.last_edited_on = datetime.now()

    session.commit()
    return {"message":"HPI successfully saved!","type":"positive","position":"top"}

def register_ros(ros:dict):
  """A function to retrieve a systems_review column on a row in clinicalhistory table and updates the row"""

  with Session(database_engine) as session:
    db_hx:ClinicalHistory = list(session.exec(select(ClinicalHistory).where(ClinicalHistory.hx_id == ros["hx_id"])))[0]

    db_hx.systems_review = ros["ros"]

    session.commit()

def register_pmh(pmh:dict):
  """A function to sore pmh data into a row in clinicalhistory table"""
  try:
    with Session(database_engine) as session:
      db_hx:ClinicalHistory = list(session.exec(select(ClinicalHistory).where(ClinicalHistory.hx_id == pmh["hx_id"])))[0]
      
      db_hx.medical_history = pmh["mhx"].lower() if pmh["mhx"] else None
      db_hx.surgical_history = pmh["shx"].lower() if pmh["shx"] else None
      db_hx.editor_id = pmh["editor_id"],
      db_hx.last_edited_on = datetime.now()

      session.commit()

      return  {"message":"Medical & Surgical History saved successfully!","type":"positive","position":"top"}
  except:
    return  {"message":"Medical & Surgical History not saved!","type":"negative","position":"center"}

def register_fsh(fsh:dict):
  try:
    with Session(database_engine) as session:
      db_hx:ClinicalHistory = list(session.exec(select(ClinicalHistory).where(ClinicalHistory.hx_id == fsh["hx_id"])))[0]
    
      db_hx.family_history = fsh["fhx"].lower() if fsh["fhx"] else None
      db_hx.social_history = fsh["shx"].lower() if fsh["shx"] else None
      db_hx.editor_id = fsh["editor_id"]
      db_hx.last_edited_on = datetime.now()

      session.commit()

      return  {"message":"Family & Social History saved successfully!","type":"positive","position":"top"}
  except:
    return  {"message":"Family & Social History not saved!","type":"negative","position":"center"}

def register_general_exam(ge:dict):
  """A function to register 'ge' data into a row in a generalexamination table with relevant id"""
  try:
    with Session(database_engine) as session:
      db_ge_exam:GeneralExamination = list(session.exec(select(GeneralExamination).where(GeneralExamination.ge_id == ge["ge_id"])))[0]

      db_ge_exam.notes = ge["notes"]
      db_ge_exam.editor_id = ge["editor_id"]
      db_ge_exam.ge_exam_time = datetime.now()

      session.commit()

      return  {"message":"General Examination saved successfully!","type":"positive","position":"top"}
  except:
    return  {"message":"General examination Examination not saved successfully!","type":"negative","position":"center"}

def register_cvs_exam(cvs:dict):
  """A function to update a row in cardiovascularexamination table with cvs_exam_id matching cvs['cvs_exam_id']"""

  with Session(database_engine) as session:
    db_cvs_exam:CardiovascularExamination = list(session.exec(select(CardiovascularExamination).where(CardiovascularExamination.cvs_exam_id == cvs["cvs_exam_id"])))[0]

    db_cvs_exam.inverted_j,db_cvs_exam.inspection,db_cvs_exam.palpation,db_cvs_exam.auscultation = cvs["inverted_j"],cvs["inspection"],cvs["palpation"],cvs["auscultation"]
    db_cvs_exam.cvs_exam_time = datetime.now()

    session.commit()

def register_rs_exam(rs:dict):
  """A function to update a row in respiratoryexamination table with rs_exam_id matching rs['rs_exam_id']"""

  with Session(database_engine) as session:
    db_rs_exam:RespiratoryExamination = list(session.exec(select(RespiratoryExamination).where(RespiratoryExamination.rs_exam_id == rs["rs_exam_id"])))[0]

    db_rs_exam.inspection,db_rs_exam.palpation,db_rs_exam.auscultation,db_rs_exam.percussion = rs["inspection"],rs["palpation"],rs["auscultation"],rs["percussion"]
    db_rs_exam.rs_exam_time = datetime.now()
    
    session.commit()

def register_abd_exam(abd:dict):
  """A function to update a row in abdominalexamination table with abd_exam_id matching rs['abd_exam_id']"""

  with Session(database_engine) as session:
    db_abd_exam:AbdominalExamination = list(session.exec(select(AbdominalExamination).where(AbdominalExamination.abd_exam_id == abd["abd_exam_id"])))[0]

    db_abd_exam.inspection,db_abd_exam.palpation,db_abd_exam.auscultation,db_abd_exam.percussion,db_abd_exam.dre = abd["inspection"],abd["palpation"],abd["auscultation"],abd["percussion"],abd["dre"]
    db_abd_exam.abd_exam_time = datetime.now()
    
    session.commit()

def register_gus_exam(gus:dict):
  """A function to update a row in genitourinaryexamination table with gus_exam_id matching gus['gus_exam_id']"""

  with Session(database_engine) as session:
    db_gus_exam:GenitourinaryExamination = list(session.exec(select(GenitourinaryExamination).where(GenitourinaryExamination.gus_exam_id == gus["gus_exam_id"])))[0]

    db_gus_exam.inspection,db_gus_exam.palpation = gus["inspection"],gus["palpation"]
    db_gus_exam.gus_exam_time = datetime.now()
    
    session.commit()

def register_mss_exam(mss:dict):
  """A function to update a row in musculoskeletalexamination table with mss_exam_id matching mss['mss_exam_id']"""

  with Session(database_engine) as session:
    db_mss_exam:MusculoskeletalExamination = list(session.exec(select(MusculoskeletalExamination).where(MusculoskeletalExamination.mss_exam_id == mss["mss_exam_id"])))[0]
    
    if "upper_limbs" in mss:
      db_mss_exam.upper_limbs = mss["upper_limbs"]
    if "lower_limbs" in mss:
      db_mss_exam.lower_limbs = mss["lower_limbs"]
    
    db_mss_exam.mss_exam_time = datetime.now()

    session.commit()

def register_cns_exam(cns:dict):
  """A function to update a row in cnsexamination table with cns_exam_id matching cns['cns_exam_id']"""

  with Session(database_engine) as session:
    db_cns_exam:CNSExamination = list(session.exec(select(CNSExamination).where(CNSExamination.cns_exam_id == cns["cns_exam_id"])))[0]

    db_cns_exam.cranials,db_cns_exam.dermatomes,db_cns_exam.myotomes,db_cns_exam.gait,db_cns_exam.reflexes = cns["cranials"],cns["dermatomes"],cns["myotomes"],cns["gait"],cns["reflexes"]
    db_cns_exam.cns_exam_time = datetime.now()

    session.commit()

def register_orodental_exam(orodental:dict):
  """A function to store orodental data into orodentalexamination table rows"""
  try:
    with Session(database_engine) as session:
      db_orodental_exam:OrodentalExamination = list(session.exec(select(OrodentalExamination).where(OrodentalExamination.orodental_exam_id == orodental["orodental_exam_id"])))[0]
      
      db_orodental_exam.extraoral = orodental["extraoral"] if orodental["extraoral"] else None
      db_orodental_exam.intraoral = orodental["intraoral"] if orodental["intraoral"] else None
      db_orodental_exam.editor_id = orodental["orodental_exam_id"]
      db_orodental_exam.orodental_exam_time = datetime.now()

      session.commit()

      return  {"message":"Orodental Examination saved successfully!","type":"positive","position":"top"}
  except:
    return  {"message":"Orodental Examination not saved!","type":"negative","position":"center"}

def register_diagnosis(diagnosis:dict):
  """A function to store 'diagnosis' data into created rows in diagnosis table"""
  
  #Provisional
  provisional_generic = diagnosis["provisional_icd"].split(".")[0] if "." in diagnosis["provisional_icd"] else diagnosis["provisional_icd"]

  with Session(database_engine) as session:
    db_diagnoses:list[Diagnosis] = list(session.exec(select(Diagnosis).where(Diagnosis.consultation_id == diagnosis["consultation_id"])))

  
    feedable_diagnosis = {
      "consultation_id":diagnosis["consultation_id"],
      "diagnosis_id":diagnosis["diagnosis_id"],
      "provisional":diagnosis["provisional"],
      "provisional_icd":diagnosis["provisional_icd"],
      "provisional_generic":provisional_generic,
      "differentials":json.dumps(diagnosis["differentials"])
      }

    feed_diagnosis(feedable_diagnosis)

    session.commit()
    return {"message":"Provisional Diagnosis saved!","type":"positive","position":"top"}
      
def register_imaging(imaging:dict):
  """Creates a new row in imaging table and adds details from 'imaging' dictionary"""
  try:
    feed_imaging(imaging)
    feed_payment(payment=imaging["payment"],imaging_id=imaging["imaging_id"])
    return {"message":"Imaging Saved Successfully!","position":"top","type":"positive"}
  except:
    return {"message":"Imaging Not Saved!","position":"center","type":"negative"}

def register_procedure(procedure:dict):
  """Creates a new rows in procedure table and adds details from 'procedures' dictionary"""
  
  try:
    feed_procedure(procedure)
    feed_payment(procedure["payment"],procedure_id=procedure["procedure_id"]) 
    
    return {"message":"Procedure Saved Successfully!","position":"top","type":"positive"}
  except:
    return {"message":f"Procecure Not Saved!","position":"center","type":"negative"}

def register_medication(medication_data:dict):
  """Creates a new rows in medication table and adds details from 'medications' dictionary"""
  
  try:
    feed_medication(medication_data)
    feed_payment(payment=medication_data["payment"],medication_id=medication_data["medication_id"])
  
    return {"message":"Medication Prescribed Successfully!","type":"positive","position":"top"}
  except:
    return {"message":"Medication Not Saved","position":"center","type":"negative"}

def register_medical_item(medical_item:dict):
  """Creates a new rows in medicalitem table and adds details from 'medical_items' dictionary"""
  
  try:
    feed_medical_item(medical_item)
    feed_payment(payment=medical_item["payment"],medical_item_id=medical_item["medical_item_id"])
    return {"message":"Medical item successfully saved!","position":"top","type":"success"}
  except:
    return {"message":"Medical item not saved!","position":"top","type":"negative"}

def register_nonpharmacological(nonpharmacological:dict):
  """Creates a new row in nonpharmacological table and adds details from 'nonpharmacological' dictionary"""

  if not "payment" in nonpharmacological:
    nonpharmacological["done"] = True
    nonpharmacological["done_on"] = datetime.now()
    feed_nonpharmacological(nonpharmacological)
  else:
    pass

#UPDATE FUNCTIONS
def update_client(client:dict):
  """A function that retrieves a row in client table and modifies value(s) of its column(s)"""
  
  try:
    with Session(database_engine) as session:
      db_client:Client = list(session.exec(select(Client).where(Client.client_id == client["client_id"])))[0]
      
      db_client.first_name,db_client.middle_name,db_client.last_name = client["first_name"],client["middle_name"],client["last_name"]
      db_client.mobile,db_client.address = client["mobile"],client["address"]
      db_client.gender,db_client.birthdate = client["gender"].lower(),client["birthdate"]
      db_client.marital_status,db_client.occupation = client["marital_status"].lower(),client["occupation"]
      db_client.payment_mode,db_client.card_no = client["payment_mode"].lower(),client["card_no"]

      session.commit()
      return {"message":"Client updated successfully!","type":"positive","position":"top"}
  except Exception as e:
    return {"message":e,"type":"negative","position":"center"}

def update_consultation(consultation:dict):
  
  with Session(database_engine) as session:
    db_consultation:Consultation = list(session.exec(select(Consultation).where(Consultation.consultation_id == consultation["consultation_id"])))[0]
    db_consultation.initiated = True
    db_consultation.consultant_id = consultation["consultant_id"]
    session.commit()

def update_diagnosis(diagnosis:dict):
  """Update the values of definitive diagnosis"""

  with Session(database_engine) as session:
    db_diagnosis = list(session.exec(select(Diagnosis).where(Diagnosis.diagnosis_id == diagnosis["diagnosis_id"])))[0]
    if db_diagnosis.definitive:
      return {"status":False,"message":"Definitive Already ruled out/saved!","type":"warning","position":"top"}
    else:
      db_diagnosis.definitive = diagnosis["definitive"]
      db_diagnosis.definitive_icd = diagnosis["definitive_icd"]
      db_diagnosis.definitive_generic = diagnosis["definitive_generic"]

      session.commit()
      return {"status":True,"message":"Definitive Diagnosis saved!","type":"positive","position":"top"}


def update_visit(visit:dict,close:bool=True):
  """A function that retrieves a row in visit table and modifies value(s) of its column(s)"""

  if close:
    with Session(database_engine) as session:
      db_visit:Visit = list(session.exec(select(Visit).where(Visit.visit_id == visit["visit_id"])))[0]

      db_visit.active = False
      db_visit.end_time = datetime.now()

      session.commit()

def update_triage(triage):
  
  if "vitals" in triage:
    vitals = triage["vitals"]

    with Session(database_engine) as session:
      db_vital_signs:VitalSigns = list(session.exec(select(VitalSigns).where(VitalSigns.vitals_id == vitals["vitals_id"])))[0]
      if vitals["sbp"] or vitals["dbp"] or vitals["temp"] or vitals["pr"] or vitals["rr"] or vitals["osat"]:
        db_vital_signs.systolic_blood_pressure = vitals["sbp"]
        db_vital_signs.diastolic_blood_pressure = vitals["dbp"]
        db_vital_signs.temperature = vitals["temp"],
        db_vital_signs.pulse_rate = vitals["pr"]
        db_vital_signs.respiratory_rate = vitals["rr"]
        db_vital_signs.oxygen_saturation = vitals["osat"]
        db_vital_signs.done = True
        db_vital_signs.attendee_id = vitals["attendee_id"]
        db_vital_signs.vitals_time = datetime.now()

      session.commit()

  if "anthropometrics" in triage:
    anthropometrics = triage["anthropometrics"]

    with Session(database_engine) as session:
      db_anthropometrics:Anthropometrics = list(session.exec(select(Anthropometrics).where(Anthropometrics.anthropometrics_id == anthropometrics["anthropometrics_id"])))[0]
      if anthropometrics["weight"] or anthropometrics["height"] or anthropometrics["muac"] or anthropometrics["hc"]:
        db_anthropometrics.weight = anthropometrics["weight"]
        db_anthropometrics.height = anthropometrics["height"]
        db_anthropometrics.muac = anthropometrics["muac"]
        db_anthropometrics.head_circumference = anthropometrics["hc"]
        db_anthropometrics.done = True
        db_anthropometrics.anthropometrics_time = datetime.now()
        db_anthropometrics.attendee_id = anthropometrics["attendee_id"]

      session.commit()
  
  
  return {"message":"Triage data successfully saved!","type":"positive","position":"top"}   
    
def update_appointment_status(appointment:dict):
  """Change value of 'status' column in a given row in 'appointment' table"""
  
  if appointment["cancelled"]:
    with Session(database_engine) as session:
      db_appointment:Appointment = list(session.exec(select(Appointment).where(Appointment.appointment_id == appointment["appointment_id"])))[0]
      db_appointment.cancelled = True

      session.commit()
    
    return {"message":"Appointment cancelled successfully!","type":"positive","position":"top"}

  if appointment["done"]:
    with Session(database_engine) as session:
      db_appointment:Appointment = list(session.exec(select(Appointment).where(Appointment.appointment_id == appointment["appointment_id"])))[0]
      
      db_appointment.done = True

      session.commit()

    return {"message":"Appointment status updated successfully!","type":"positive","position":"top"}
  
def reschedule_appointment(appointment:dict):
  """Change value of 'date' column in a given row in 'appointment' table"""

  with Session(database_engine) as session:
    db_appointment:Appointment = list(session.exec(select(Appointment).where(Appointment.appointment_id == appointment["appointment_id"])))[0]
    db_appointment.appointment_time = appointment["new_date"]

    session.commit()

  return {"message":"Appointment rescheduled successfully!","type":"positive","position":"top"}

def just_update_triage_payment(triages:list,billed:bool=False,paid:bool=False,cancelled:bool=False):
  """Update payment of triage services if consultation is paid or billed """
  #Anthropometrics
  with Session(database_engine) as session:
    anthrop_payment:Payment = list(session.exec(select(Payment).where(Payment.payment_id == triages[0])))[0]

    anthrop_payment.billed = billed
    anthrop_payment.paid = paid
    anthrop_payment.cancelled = cancelled
    anthrop_payment.billing_time = datetime.now() if billed else None
    anthrop_payment.payment_time = datetime.now() if paid else None
    anthrop_payment.cancel_time = datetime.now() if cancelled else None

    session.commit()
  
  #vitals
  with Session(database_engine) as session:
    vitals_payment:Payment = list(session.exec(select(Payment).where(Payment.payment_id == triages[1])))[0]

    vitals_payment.billed = billed
    vitals_payment.paid = paid
    vitals_payment.cancelled = cancelled
    vitals_payment.billing_time = datetime.now() if billed else None
    vitals_payment.payment_time = datetime.now() if paid else None
    vitals_payment.cancel_time = datetime.now() if cancelled else None

    session.commit()

def update_payment(payment_data:dict):
  """Updates row in 'payment' table based on 'payment_data'"""
  
  with Session(database_engine) as session:
    db_payment:Payment = list(session.exec(select(Payment).where(Payment.payment_id == payment_data["payment_id"])))[0]

    if payment_data["cancelled"]:
      db_payment.cancelled = True
      db_payment.cancel_time = datetime.now()
      #Triages (if its consultation-associated)
      if payment_data["consultation"]:
        just_update_triage_payment(triages=payment_data["triages"],cancelled=True)
    elif payment_data["billed_amount"]:
      db_payment.billed = True
      db_payment.billed_amount = payment_data["billed_amount"]
      db_payment.billing_time = datetime.now()
      #Triages (if its consultation-associated)
      if payment_data["consultation"]:
        just_update_triage_payment(triages=payment_data["triages"],billed=True)
    elif payment_data["paid_amount"]:
      if db_payment.cost:
        if payment_data["paid_amount"] == db_payment.cost:
          db_payment.paid,db_payment.billed = True,False
          db_payment.paid_amount = payment_data["paid_amount"]
          db_payment.billed_amount = 0
          db_payment.payment_time = datetime.now()
          #Triages (if its consultation-associated)
          if payment_data["consultation"]:
            just_update_triage_payment(triages=payment_data["triages"],paid=True)
        else:
          #Unpaid
          if (not db_payment.paid) and (not db_payment.billed):
            db_payment.paid = db_payment.billed = True
            db_payment.paid_amount = payment_data["paid_amount"]
            db_payment.billed_amount = db_payment.cost - payment_data["paid_amount"]
            db_payment.payment_time = db_payment.billing_time = datetime.now()
          #Billed
          elif db_payment.billed and not db_payment.paid:
            db_payment.paid = True
            db_payment.paid_amount = payment_data["paid_amount"]
            db_payment.billed_amount -= payment_data["paid_amount"]
            db_payment.payment_time = db_payment.billing_time = datetime.now()
          #Incomplete
          elif db_payment.billed and db_payment.paid:
            if payment_data["paid_amount"] == db_payment.billed_amount:
              db_payment.paid_amount += payment_data["paid_amount"]
              db_payment.billed,db_payment.billed_amount = False,0
              db_payment.payment_time = datetime.now()
            else:
              db_payment.paid_amount += payment_data["paid_amount"]
              db_payment.billed_amount -= payment_data["paid_amount"]
              db_payment.payment_time = datetime.now()
          else:
            return
      else:
        db_payment.paid,db_payment.billed = True,False
        db_payment.paid_amount = db_payment.cost = payment_data["paid_amount"]
        db_payment.billed_amount = 0
        db_payment.payment_time = datetime.now()
        #Triages (if its consultation-associated)
        if payment_data["consultation"]:
          just_update_triage_payment(triages=payment_data["triages"],paid=True)
      
    elif payment_data["refunded_amount"]:
      db_payment.refunded = db_payment.cancelled = True
      db_payment.billed = db_payment.paid = False
      db_payment.refunded_amount = payment_data["refunded_amount"]
      db_payment.refunding_time = db_payment.cancel_time = datetime.now()
      
    elif payment_data["unbilled_amount"]:
      db_payment.billed_amount = db_payment.paid_amount = 0
      db_payment.billed = db_payment.paid = False
      db_payment.cancelled = True
      db_payment.cancel_time = datetime.now()
      db_payment.billing_time = db_payment.payment_time = None
    else:
      return
       
    session.commit()

    return {"message":"Payment processed successfully","type":"positive","position":"top"}

def update_imaging(imaging_data:dict,delete:bool=False):
  """Retrieves a row in imaging data and updates the row with 'imaging_data' data"""

  if delete:
    with Session(database_engine) as session:
      db_imaging:Imaging = list(session.exec(select(Imaging).where(Imaging.imaging_id == imaging_data["imaging_id"])).all())[0]
      session.delete(db_imaging)

      session.commit()

  else:
    try:
      with Session(database_engine) as session:
        db_imaging:Imaging = list(session.exec(select(Imaging).where(Imaging.imaging_id == imaging_data["imaging_id"])).all())[0]

        db_imaging.results = imaging_data["results"]
        db_imaging.results_img = imaging_data["results_img"]
        db_imaging.radiographer = imaging_data["radiographer"]
        db_imaging.radiologist = imaging_data["radiologist"]
        db_imaging.processed = True
        db_imaging.results_time = datetime.now()

        session.commit()
        return {"message":"Imaging processed successfully!","type":"positive","position":"top"}
    except:
      return {"message":"Imaging not processed!","type":"negative","position":"center"}

def update_procedure(procedure:dict):
  """Retrieves a row in procedure data and updates the row with 'imaging_data' data"""
  
  with Session(database_engine) as session:
    db_procedure:Procedure = list(session.exec(select(Procedure).where(Procedure.procedure_id == procedure["procedure_id"])).all())[0]

    db_procedure.performer = procedure["performer"]
    db_procedure.assistant = procedure["assistant"]
    db_procedure.procedure_notes = procedure["procedure_notes"]
    db_procedure.done = True
    db_procedure.done_on = datetime.now()

    session.commit()

    return {"message":"Procedure updated successfully!","type":"positive","position":"top"}

def update_medicine(medicine:dict):
  """Select a row in medication or medicalitem table and updates values of column"""

  try:
    #Client Update
    with Session(database_engine) as session:
      #Update medication
      if medicine["medication_id"]:
        db_medication:Medication = list(session.exec(select(Medication).where(Medication.medication_id == medicine["medication_id"])))[0]
        
        db_medication.dispensed = True
        db_medication.dispensed_items_no = medicine["dispensed_items_no"]
        db_medication.dispenser_id = medicine["dispenser_id"]
        db_medication.editable = False
        db_medication.dispensing_time = datetime.now()

      #Update medical item
      if medicine["medical_item_id"]:
        db_medical_item:MedicalItem = list(session.exec(select(MedicalItem).where(MedicalItem.medical_item_id == medicine["medical_item_id"])))[0]
        
        db_medical_item.dispensed = True
        db_medical_item.dispensed_items_no = medicine["dispensed_items_no"]
        db_medical_item.dispenser_id = medicine["dispenser_id"]
        db_medical_item.editable = False
        db_medical_item.dispensing_time = datetime.now()

      session.commit()

    #Return
    return {"message":"Medicine dispensed successfully!","type":"positive","position":"top"}
  
  except:
    return {"message":"Medicine not dispensed!","type":"negative","position":"center"}

#TERMINATE FUNCTIONS
def cancel_payment(payment_id):
  with Session(database_engine) as session:
    db_payment:Payment = list(session.exec(select(Payment).where(Payment.payment_id == payment_id)))[0]
    db_payment.cancelled = True
    db_payment.cancel_time = datetime.now()

    session.commit()

def terminate_visits(client_id:str):
  """Retrives a row from 'client' table and using it to retrieve a respective row in 'visit' table and then change the value of 'is_active' column into False"""

  with Session(database_engine) as session:
    db_visits:list[Visit] = list(session.exec(select(Visit).where(Visit.client_id == int(client_id))))

    for db_visit in db_visits:
      db_visit.is_active = False
      db_visit.end_time = datetime.now()
    
    session.commit()

  return {"status":True,"message":"Visit(s) terminated successfully!","type":"positive"}

def cancel_procedure(procedure:dict):
  """A function to cancel a procedure and update the payment status"""
  
  try:
    with Session(database_engine) as session:
      db_procedure:Procedure = list(session.exec(select(Procedure).where(Procedure.procedure_id == procedure["procedure_id"])))[0]
      db_procedure.cancelled = True
      db_procedure.cancelled_on = datetime.now()
      db_procedure.cancelled_by = procedure["cancelled_by"]

      procedure_payment_id = db_procedure.payments[-1].payment_id
      cancel_payment(payment_id=procedure_payment_id)
      session.commit()
    
    return {"message":"Cancelled Sucessfully!","type":"positive","position":"top"}
  except:
    return {"message":"Procedure Not Cancelled!","type":"negative","position":"center"}

def cancel_medication(medication:dict):
  """A function to cancel a medication and update the payment status"""

  with Session(database_engine) as session:
    db_medication:Medication = list(session.exec(select(Medication).where(Medication.medication_id == medication["medication_id"])))[0]
    db_medication.cancelled = True
    db_medication.cancelled_on = datetime.now()
    db_medication.cancelled_by = medication["cancelled_by"]
    db_medication.payment.cancelled = True
    db_medication.payment.cancel_time = datetime.now()

    session.commit()






