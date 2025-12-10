"""A module for base operations neccesary in processing dicons during database updating and database querrying."""

#GENERAL IMPORTS
import json,re
from collections import namedtuple
from typing import Sequence

#SQLMODEL IMPORTS
from sqlalchemy import Boolean, Engine, false
from sqlmodel import Session,select

#CUSTOM IMPORTS
from .models import *


#
def unmodel_payment(db_payment:Payment):
  """Converts a row(s) in payment table into a dictionary 'payment'"""

  _Payment = namedtuple("_Payment",["visit_id","payment_id","created","client_name","client_gender","client_birthdate","service","service_type","authorization_no","payment_mode","cost","paid","paid_amount","payment_time","billed","billed_amount","billing_time","cancelled","cancel_time","cancelled_by","refundable","refunded","refunded_amount","refunding_time"])

  return _Payment(
    visit_id = db_payment.visit_id,
    payment_id = db_payment.payment_id,
    created = db_payment.created_on,
    client_name = f"{db_payment.visit.client.first_name} {db_payment.visit.client.middle_name} {db_payment.visit.client.last_name}",
    client_gender = db_payment.visit.client.gender,
    client_birthdate = db_payment.visit.client.birthdate,
    service = db_payment.consultation.name if db_payment.consultation_id else None,
    service_type = "Consultation" if db_payment.consultation_id else None,
    authorization_no = db_payment.authorization_no,
    payment_mode = db_payment.payment_mode,
    cost = db_payment.cost,
    paid = db_payment.paid,
    paid_amount = db_payment.paid_amount,
    payment_time = db_payment.payment_time,
    billed = db_payment.billed,
    billed_amount = db_payment.billed_amount,
    billing_time = db_payment.billing_time,
    cancelled = db_payment.cancelled,
    cancel_time = db_payment.cancel_time,
    cancelled_by = db_payment.cancelled_by,
    refundable = db_payment.refundable,
    refunded = db_payment.refunded,
    refunded_amount = db_payment.refunded_amount,
    refunding_time = db_payment.refunding_time
  )

def unmodel_nonpharmacological(db_nonpharmacological:NonPharmacological):
  """Converts a row in nonpharmacological table into a dictionary"""

  _Nonpharmacological = namedtuple("_Nonpharmacological",["visit_id","nonpharmacological_id","attendee_id","name","planned_on","notes","done","done_on","editable","last_edited_on","editor_id","payment"])

  return _Nonpharmacological(
    visit_id = db_nonpharmacological.visit_id,
    nonpharmacological_id = db_nonpharmacological.nonpharmacological_id,
    attendee_id = db_nonpharmacological.attendee_id,
    name = db_nonpharmacological.name,
    planned_on = db_nonpharmacological.planned_on,
    notes = db_nonpharmacological.notes,
    done = db_nonpharmacological.done,
    done_on = db_nonpharmacological.done_on,
    editable = db_nonpharmacological.editable,
    last_edited_on = db_nonpharmacological.last_edited_on,
    editor_id = db_nonpharmacological.editor_id,
    payment = unmodel_payment(db_nonpharmacological.payment) if db_nonpharmacological.payment else None
  )

def unmodel_medication(db_medication:Medication):
  """Converts a row in medication table into a dictionary 'medication'"""

  _Medication = namedtuple("_Medication",["visit_id","medication_id","prescriber_id","name","dosage","prescribed_items_no","dispensed_items_no","prescribed_on","dispensed","dispensing_time","dispenser_id","cancelled","cancelled_on","cancelled_by","payment"])

  return _Medication(
    visit_id = db_medication.visit_id,
    medication_id = db_medication.medication_id,
    prescriber_id = db_medication.prescriber_id,
    name = db_medication.name,
    dosage = db_medication.dosage,
    prescribed_items_no = db_medication.prescribed_items_no,
    dispensed_items_no = db_medication.dispensed_items_no,
    prescribed_on = db_medication.prescribed_on,
    dispensed = db_medication.dispensed,
    dispensing_time = db_medication.dispensing_time,
    dispenser_id = db_medication.dispenser_id,
    cancelled = db_medication.cancelled,
    cancelled_on = db_medication.cancelled_on,
    cancelled_by = db_medication.cancelled_by,
    payment = unmodel_payment(db_medication.payment)
  )

def unmodel_medical_item(db_medical_item:MedicalItem):
  """"""

  _MedicalItem = namedtuple("_MedicalItem",["visit_id","medical_item_id","prescriber_id","name","prescribed_items_no","dispensed_items_no","prescribed_on","dispensed","dispensing_time","dispenser_id","cancelled","cancelled_on","cancelled_by","payment"])

  return _MedicalItem(
    visit_id = db_medical_item.visit_id,
    medical_item_id = db_medical_item.medical_item_id,
    prescriber_id = db_medical_item.prescriber_id,
    name = db_medical_item.name,
    prescribed_items_no = db_medical_item.prescribed_items_no,
    dispensed_items_no = db_medical_item.dispensed_items_no,
    prescribed_on = db_medical_item.prescribed_on,
    dispensed = db_medical_item.dispensed,
    dispensing_time = db_medical_item.dispensing_time,
    dispenser_id = db_medical_item.dispenser_id,
    cancelled = db_medical_item.cancelled,
    cancelled_on = db_medical_item.cancelled_on,
    cancelled_by = db_medical_item.cancelled_by,
    payment = unmodel_payment(db_medical_item.payment)
  )

def unmodel_vital_signs(db_vital_signs:VitalSigns):
  """Converts a row in vital_signs table into a dictionary"""

  _VitalSigns = namedtuple("_VitalSigns",["visit_id","vitals_id","attendee_id","sbp","dbp","pulse_rate","resp_rate","temperature","o2sat","done","vitals_time","payment"])

  return _VitalSigns(
    visit_id = db_vital_signs.visit_id,
    vitals_id = db_vital_signs.vitals_id,
    attendee_id = db_vital_signs.attendee_id,
    sbp = db_vital_signs.systolic_blood_pressure,
    dbp = db_vital_signs.diastolic_blood_pressure,
    pulse_rate = db_vital_signs.pulse_rate,
    resp_rate = db_vital_signs.respiratory_rate,
    temperature = db_vital_signs.temperature,
    o2sat = db_vital_signs.oxygen_saturation,
    done = db_vital_signs.done,
    vitals_time = db_vital_signs.vitals_time,
    payment = unmodel_payment(db_vital_signs.payment)
  )

def unmodel_anthropometrics(db_anthropometrics:Anthropometrics):
  """Converts a row in anthropometrics into a dictionary"""

  _Anthropometrics = namedtuple("_Anthropometrics",["visit_id","anthropometrics_id","attendee_id","weight","height","head_circum","muac","done","anthropometrics_time","payment"])

  return _Anthropometrics(
    visit_id = db_anthropometrics.visit_id,
    anthropometrics_id = db_anthropometrics.anthropometrics_id,
    attendee_id = db_anthropometrics.attendee_id,
    weight = db_anthropometrics.weight,
    height = db_anthropometrics.height,
    head_circum = db_anthropometrics.head_circumference,
    muac = db_anthropometrics.muac,
    done = db_anthropometrics.done,
    anthropometrics_time = db_anthropometrics.anthropometrics_time,
    payment = unmodel_payment(db_anthropometrics.payment)
  )

def unmodel_clinical_history(db_clinical_history:ClinicalHistory):
  """Converts a row in clinicalhistory table into a dictionary"""

  _ClinicalHistory = namedtuple("_ClinicalHistory",["consultation_id","hx_id","history_time","chief_complaints","hpi1","hpi2","hpi3","medical_history","surgical_history","family_history","social_history","editable","edited","last_edited_on","editor_id"])

  return _ClinicalHistory(
    consultation_id = db_clinical_history.consultation_id,
    hx_id = db_clinical_history.hx_id,
    history_time = db_clinical_history.history_time,
    chief_complaints = json.loads(db_clinical_history.chief_complaints) if db_clinical_history.chief_complaints else [],
    hpi1 = db_clinical_history.hpi1,
    hpi2 = db_clinical_history.hpi2,
    hpi3 = db_clinical_history.hpi3,
    medical_history = db_clinical_history.medical_history,
    surgical_history = db_clinical_history.surgical_history,
    family_history = db_clinical_history.family_history,
    social_history = db_clinical_history.social_history,
    editable = db_clinical_history.editable,
    edited = db_clinical_history.edited,
    last_edited_on = db_clinical_history.last_edited_on,
    editor_id = db_clinical_history.editor_id
  )

def unmodel_ge_exam(db_ge_exam:GeneralExamination):
  """Converts a row in ge_exam into a dictionary"""

  _GeneralExam = namedtuple("_GeneralExam",["consultation_id","ge_id","ge_exam_time","notes","editable","edited","last_edited_on","editor_id"])

  return _GeneralExam(
    consultation_id = db_ge_exam.consultation_id,
    ge_id = db_ge_exam.ge_id,
    ge_exam_time = db_ge_exam.ge_exam_time,
    notes = db_ge_exam.notes,
    editable = db_ge_exam.editable,
    edited = db_ge_exam.edited,
    last_edited_on = db_ge_exam.last_edited_on,
    editor_id = db_ge_exam.editor_id
  )

def unmodel_orodental_exam(db_orodental_exam:OrodentalExamination):
  """Converts orodentalexamination table into a dictionary"""

  _OrodentalExam = namedtuple("_OrodentalExam",["consultation_id","orodental_exam_id","orodental_exam_time","extraoral","intraoral","editable","edited","last_edited_on","editor_id"])

  return _OrodentalExam(
    consultation_id = db_orodental_exam.consultation_id,
    orodental_exam_id = db_orodental_exam.orodental_exam_id,
    orodental_exam_time = db_orodental_exam.orodental_exam_time,
    extraoral = db_orodental_exam.extraoral,
    intraoral = db_orodental_exam.intraoral,
    editable = db_orodental_exam.editable,
    edited = db_orodental_exam.edited,
    last_edited_on = db_orodental_exam.last_edited_on,
    editor_id = db_orodental_exam.editor_id
  )

def unmodel_cns_exam(db_cns_exam:CNSExamination):
  """Converts a cnsexamination table row into a dictionary"""

  _CNSExam = namedtuple("_CNSExam",["consultation_id","cns_exam_id","gcs","cranials","dermatomes","myotomes","gait","reflexes","special_tests","editable","edited","last_edited_on","editor_id"])

  return _CNSExam(
    consultation_id = db_cns_exam.consultation_id,
    cns_exam_id = db_cns_exam.cns_exam_id,
    gcs = json.loads(db_cns_exam.gcs),
    cranials = db_cns_exam.cranials,
    dermatomes = db_cns_exam.dermatomes,
    myotomes = db_cns_exam.myotomes,
    gait = db_cns_exam.gait,
    reflexes = db_cns_exam.reflexes,
    special_tests = db_cns_exam.special_tests,
    editable = db_cns_exam.editable,
    edited = db_cns_exam.edited,
    last_edited_on = db_cns_exam.last_edited_on,
    editor_id = db_cns_exam.editor_id
  )

def unmodel_cvs_exam(db_cvs_exam:CardiovascularExamination):
  """Converts a cardiovascularexamination table rows into dictionaries"""

  _CVSExam = namedtuple("_CVSExam",["consultation_id","cvs_exam_id","cvs_exam_time","inverted_j","inspection","palpation","auscultation","special_tests","editable","edited","last_edited_on","editor_id"])

  return _CVSExam(
    consultation_id = db_cvs_exam.consultation_id,
    cvs_exam_id = db_cvs_exam.cvs_exam_id,
    cvs_exam_time = db_cvs_exam.cvs_exam_time,
    inverted_j = db_cvs_exam.inverted_j,
    inspection = db_cvs_exam.inspection,
    palpation = db_cvs_exam.palpation,
    auscultation = db_cvs_exam.auscultation,
    special_tests = json.loads(db_cvs_exam.special_tests) if db_cvs_exam.special_tests else None,
    editable = db_cvs_exam.editable,
    edited = db_cvs_exam.edited,
    last_edited_on = db_cvs_exam.last_edited_on,
    editor_id = db_cvs_exam.editor_id
  )

def unmodel_rs_exam(db_rs_exam:RespiratoryExamination):
  """Converts data from respiratoryexamination table rows into dictionaries"""

  _RSExam = namedtuple("_RSExam",["consultation_id","rs_exam_id","rs_exam_time","inspection","palpation","percussion","auscultation","special_tests","editable","edited","last_edited_on","editor_id"])

  return _RSExam(
    consultation_id = db_rs_exam.consultation_id,
    rs_exam_id = db_rs_exam.rs_exam_id,
    rs_exam_time = db_rs_exam.rs_exam_time,
    inspection = db_rs_exam.inspection,
    palpation = db_rs_exam.palpation,
    percussion = db_rs_exam.percussion,
    auscultation = db_rs_exam.auscultation,
    special_tests = json.loads(db_rs_exam.special_tests) if db_rs_exam.special_tests else None,
    editable = db_rs_exam.editable,
    edited = db_rs_exam.edited,
    last_edited_on = db_rs_exam.last_edited_on,
    editor_id = db_rs_exam.editor_id
  )

def unmodel_abd_exam(db_abd_exam:AbdominalExamination):
  """Converts data from abdominalexamination table rows into dictionaries"""

  _AbdExam = namedtuple("_AbdExam",["consultation_id","abd_exam_id","inspection","palpation","percussion","auscultation","dre","special_tests","editable","edited","last_edited_on","editor_id"])

  return _AbdExam(
    consultation_id = db_abd_exam.consultation_id,
    abd_exam_id = db_abd_exam.abd_exam_id,
    inspection = db_abd_exam.inspection,
    palpation = db_abd_exam.palpation,
    percussion = db_abd_exam.percussion,
    auscultation = db_abd_exam.auscultation,
    dre = db_abd_exam.dre,
    special_tests = json.loads(db_abd_exam.special_tests) if db_abd_exam.special_tests else None,
    editable = db_abd_exam.editable,
    edited = db_abd_exam.edited,
    last_edited_on = db_abd_exam.last_edited_on,
    editor_id = db_abd_exam.editor_id
  )

def unmodel_gus_exam(db_gus_exam:GenitourinaryExamination):
  """Converts data from genitourinaryexamination table rows into dictionaries"""

  _GUSExam = namedtuple("_GUSExam",["consultation_id","gus_exam_id","gus_exam_time","inspection","palpation","special_tests","editable","edited","last_edited_on","editor_id"])

  return _GUSExam(
    consultation_id = db_gus_exam.consultation_id,
    gus_exam_id = db_gus_exam.gus_exam_id,
    gus_exam_time = db_gus_exam.gus_exam_time,
    inspection = db_gus_exam.inspection,
    palpation = db_gus_exam.palpation,
    special_tests = json.loads(db_gus_exam.special_tests) if db_gus_exam.special_tests else None,
    editable = db_gus_exam.editable,
    edited = db_gus_exam.edited,
    last_edited_on = db_gus_exam.last_edited_on,
    editor_id = db_gus_exam.editor_id
  )

def unmodel_mss_exam(db_mss_exam:MusculoskeletalExamination):
  """Converts data from musculoskeletalexamination table row into dictionaries"""

  _MSSExam = namedtuple("_MSSExam",["consultation_id","mss_exam_id","mss_exam_time","upper_limbs","lower_limbs","special_tests","editable","edited","last_edited_on","editor_id"])
  
  return _MSSExam(
    consultation_id = db_mss_exam.consultation_id,
    mss_exam_id = db_mss_exam.mss_exam_id,
    mss_exam_time = db_mss_exam.mss_exam_time,
    upper_limbs = db_mss_exam.upper_limbs,
    lower_limbs = db_mss_exam.lower_limbs,
    special_tests = json.loads(db_mss_exam.special_tests) if db_mss_exam.special_tests else None,
    editable = db_mss_exam.editable,
    edited = db_mss_exam.edited,
    last_edited_on = db_mss_exam.last_edited_on,
    editor_id = db_mss_exam.editor_id
  )

def unmodel_derma_exam(db_derma_exam:DermatologicalExamination):
  """Converts data from dermatologicalexamination table row into dictionaries"""

  _DermaExam = namedtuple("_DermaExam",["consultation_id","derma_exam_id","derma_exam_time","primary_lesions","secondary_lesions","special_tests","editable","edited","last_edited_on","editor_id"])

  return _DermaExam(
    consultation_id = db_derma_exam.consultation_id,
    derma_exam_id = db_derma_exam.derma_exam_id,
    derma_exam_time = db_derma_exam.derma_exam_time,
    primary_lesions = db_derma_exam.primary_lesions,
    secondary_lesions = db_derma_exam.secondary_lesions,
    special_tests = json.loads(db_derma_exam.special_tests) if db_derma_exam.special_tests else None,
    editable = db_derma_exam.editable,
    edited = db_derma_exam.edited,
    last_edited_on = db_derma_exam.last_edited_on,
    editor_id = db_derma_exam.editor_id
  )

def unmodel_laboratory(db_laboratory:Laboratory):
  """Converts data from laboratory table row into dictionaries"""

  _Lab = namedtuple("_Lab",["visit_id","lab_id","attendee_id","test","request_time","results","results_time","processed","test_performer_id","results_verifier_id","results_doc","cancelled","cancelled_on","cancelled_by","editable","edited","last_edited_on","editor_id","payment"])

  return _Lab(
    visit_id = db_laboratory.visit_id,
    lab_id = db_laboratory.lab_id,
    attendee_id = db_laboratory.attendee_id,
    test = db_laboratory.test,
    request_time = db_laboratory.request_time,
    results = db_laboratory.results,
    results_time = db_laboratory.results_time,
    processed = db_laboratory.processed,
    test_performed_id = db_laboratory.test_performer_id,
    results_verifier_id = db_laboratory.results_verifier_id,
    results_doc = db_laboratory.results_doc,
    cancelled = db_laboratory.cancelled,
    cancelled_on = db_laboratory.cancelled_on,
    cancelled_by = db_laboratory.cancelled_by,
    editable = db_laboratory.editable,
    edited = db_laboratory.edited,
    last_edited_on = db_laboratory.last_edited_on,
    editor_id = db_laboratory.editor_id,
    payment = unmodel_payment(db_laboratory.payment) if db_laboratory.payment else None
  )

def unmodel_imaging(db_imaging:Imaging):
  """Converts data from imaging table row into dictionaries"""

  _Imaging = namedtuple("_Imaging",["visit_id","imaging_id","attendee_id","study","notes","request_time","results","results_attachments","results_time","processed","radiographer","radiologist","results_img","results_doc","cancelled","cancelled_on","cancelled_by","editable","edited","last_edited_on","editor_id","payment"])

  return _Imaging(
    visit_id = db_imaging.visit_id,
    imaging_id = db_imaging.imaging_id,
    attendee_id = db_imaging.attendee_id,
    study = db_imaging.study,
    notes = db_imaging.notes,
    request_time = db_imaging.request_time,
    results = db_imaging.results,
    results_attachments = db_imaging.results_attachments,
    results_time = db_imaging.results_time,
    processed = db_imaging.processed,
    radiographer = db_imaging.radiographer,
    radiologist = db_imaging.radiologist,
    results_img = db_imaging.results_img,
    results_doc = db_imaging.results_doc,
    cancelled = db_imaging.cancelled,
    cancelled_on = db_imaging.cancelled_on,
    cancelled_by = db_imaging.cancelled_by,
    editable = db_imaging.editable,
    edited = db_imaging.edited,
    last_edited_on = db_imaging.last_edited_on,
    editor_id = db_imaging.editor_id,
    payment = [unmodel_payment(payment) for payment in db_imaging.payments][0]
  )

def unmodel_diagnosis(db_diagnosis:Diagnosis):
  """Converts data from diagnosis table row into dictionaries"""

  _Diagnosis = namedtuple("_Diagnosis",["consultation_id","diagnosis_id","provisional","provisional_generic","provisional_icd","differentials","definitive","definitive_generic","definitive_icd"])

  return _Diagnosis(
    consultation_id = db_diagnosis.consultation_id,
    diagnosis_id = db_diagnosis.diagnosis_id,
    provisional = db_diagnosis.provisional,
    provisional_generic = db_diagnosis.provisional_generic,
    provisional_icd = db_diagnosis.provisional_icd,
    differentials = json.loads(db_diagnosis.differentials) if db_diagnosis.differentials else None,
    definitive = db_diagnosis.definitive,
    definitive_generic = db_diagnosis.definitive_generic,
    definitive_icd = db_diagnosis.definitive_icd
  )

def unmodel_procedure(db_procedure:Procedure):
  """Converts data from procedure table rows into dictionaries"""

  _Procedure = namedtuple("_Procedure",["client_id","visit_id","procedure_id","attendee_id","client_name","client_birthdate","active_visit","name","count","ordered_on","performer","assistant","done","done_on","procedure_notes","cancelled","cancelled_on","cancelled_by","editable","edited","last_edited_on","editor_id","payment"])

  return _Procedure(
    client_id = db_procedure.visit.client.client_id,
    visit_id = db_procedure.visit_id,
    procedure_id = db_procedure.procedure_id,
    attendee_id = db_procedure.attendee_id,
    client_name = f"{db_procedure.visit.client.first_name} {db_procedure.visit.client.middle_name if db_procedure.visit.client.middle_name else ''} {db_procedure.visit.client.last_name}",
    client_birthdate = db_procedure.visit.client.birthdate,
    active_visit = db_procedure.visit.active,
    name = db_procedure.name,
    count = db_procedure.count,
    ordered_on = db_procedure.ordered_on,
    performer = db_procedure.performer,
    assistant = db_procedure.assistant,
    done = db_procedure.done,
    done_on = db_procedure.done_on,
    procedure_notes = db_procedure.procedure_notes,
    cancelled = db_procedure.cancelled,
    cancelled_on = db_procedure.cancelled_on,
    cancelled_by = db_procedure.cancelled_by,
    editable = db_procedure.editable,
    edited = db_procedure.edited,
    last_edited_on = db_procedure.last_edited_on,
    editor_id = db_procedure.editor_id,
    payment = unmodel_payment(db_procedure.payment)
  )

def unmodel_surgery(db_surgery:Surgery):
  """Converts data from surgery table rows into dictionaries"""

  _Surgery = namedtuple("_Surgery",["visit_id","surgery_id","attendee_id","operation","planned_on","done","operation_time","count","time_in","time_out","surgeon","assistant_surgeon","scrub_nurse","running_nurse","anaesthetist","anaesthiologist","anaesthesia","surgery_notes","consent_form","check_list","anaesthesia_chart","cancelled","cancelled_by","cancelled_on","editable","edited","last_edited_on","editor_id","payment"])

  return _Surgery(
    visit_id = db_surgery.visit_id,
    surgery_id = db_surgery.surgery_id,
    attendee_id = db_surgery.attendee_id,
    operation = db_surgery.operation,
    planned_on = db_surgery.planned_on,
    done = db_surgery.done,
    operation_date = db_surgery.operation_date,
    count = db_surgery.count,
    time_in = db_surgery.time_in,
    time_out = db_surgery.time_out,
    surgeon = db_surgery.surgeon,
    assistant_surgeon = db_surgery.assistant_surgeon,
    scrub_nurse = db_surgery.scrub_nurse,
    running_nurse = db_surgery.running_nurse,
    anaesthetist = db_surgery.anaesthetist,
    anaesthesiologist = db_surgery.anaesthesiologist,
    anaesthesia = db_surgery.anaesthesia,
    surgery_notes = db_surgery.surgery_notes,
    consent_form = db_surgery.consent_form,
    check_list = db_surgery.check_list,
    anaesthesia_chart = db_surgery.anaesthesia_chart,
    cancelled = db_surgery.cancelled,
    cancelled_on = db_surgery.cancelled_on,
    cancelled_by = db_surgery.cancelled_by,
    editable = db_surgery.editable,
    edited = db_surgery.edited,
    last_edited_on = db_surgery.last_edited_on,
    editor_id = db_surgery.editor_id,
    payment = unmodel_payment(db_surgery.payment)
  )

def unmodel_consultation(db_consultation:Consultation):
  """Converts a row(s) in consultation table into a dictionary"""
  _Consultation = namedtuple("_Consultation",["visit_id","consultation_id","consultant_id","name","cadre","level","initiated","start_time","cancelled","payment","clinical_history","general_exam","orodental_exam","cns_exams","cvs_exams","rs_exams","abd_exams","gus_exams","mss_exams","derma_exams","diagnoses"])
  
  return _Consultation(
    visit_id = db_consultation.visit_id,
    consultation_id = db_consultation.consultation_id,
    consultant_id = db_consultation.consultant_id,
    name = db_consultation.name,
    cadre = db_consultation.cadre,
    level = db_consultation.level,
    initiated = db_consultation.initiated,
    start_time = db_consultation.start_time,
    cancelled = db_consultation.cancelled,
    payment = unmodel_payment(db_consultation.payment) if db_consultation.payment else None,
    clinical_history = unmodel_clinical_history(db_consultation.clinical_histories[0]),
    general_exam = unmodel_ge_exam(db_consultation.ge_exams[-1]),
    orodental_exam = unmodel_orodental_exam(db_consultation.orodental_exams[-1]),
    cns_exams = [unmodel_cns_exam(db_cns_exam) for db_cns_exam in db_consultation.cns_exams],
    cvs_exams = [unmodel_cvs_exam(db_cvs_exam) for db_cvs_exam in db_consultation.cvs_exams],
    rs_exams = [unmodel_rs_exam(db_rs_exam) for db_rs_exam in db_consultation.rs_exams],
    abd_exams = [unmodel_abd_exam(db_abd_exam) for db_abd_exam in db_consultation.abd_exams],
    gus_exams = [unmodel_gus_exam(db_gus_exam) for db_gus_exam in db_consultation.gus_exams],
    mss_exams = [unmodel_mss_exam(db_mss_exam) for db_mss_exam in db_consultation.mss_exams],
    derma_exams = [unmodel_derma_exam(db_derma_exam) for db_derma_exam in db_consultation.derma_exams],
    diagnoses = [unmodel_diagnosis(db_diagnosis) for db_diagnosis in db_consultation.diagnoses]
  )

def unmodel_visit(db_visit:Visit):
  """Converts a row(s) in visit table into a dictionary 'visit'"""
  _Visit = namedtuple("_Visit",["client_id","client_name","client_created_on","client_birthdate","client_gender","client_address","visit_id","start_time","end_time","active","cancelled","payment_mode","package","prescription_no","payments","consultations","anthropometrics","vital_signs","labs","imagings","procedures","surgeries","medications","medical_items","nonpharmacologicals"])

  return _Visit(
    client_id = db_visit.client_id,
    client_name = f"{db_visit.client.first_name} {db_visit.client.middle_name} {db_visit.client.last_name}",
    client_created_on = db_visit.client.created_on,
    client_birthdate = db_visit.client.birthdate,
    client_gender = db_visit.client.gender,
    client_address = db_visit.client.address,
    visit_id = db_visit.visit_id,
    start_time = db_visit.start_time,
    end_time =db_visit.end_time,
    active = db_visit.active,
    cancelled = db_visit.cancelled,
    payment_mode = db_visit.payment_mode.lower(),
    package = db_visit.package,
    prescription_no = db_visit.prescription_no,
    payments = [unmodel_payment(db_payment) for db_payment in db_visit.payments],
    consultations = [unmodel_consultation(db_consultation) for db_consultation in db_visit.consultations],
    anthropometrics = [unmodel_anthropometrics(db_anthropometrics) for db_anthropometrics in db_visit.anthropometrics],
    vital_signs = [unmodel_vital_signs(db_vital_signs) for db_vital_signs in db_visit.vital_signs],
    labs = [unmodel_laboratory(db_laboratory_test) for db_laboratory_test in db_visit.laboratory_tests],
    imagings = [unmodel_imaging(db_imaging) for db_imaging in db_visit.imagings],
    procedures = [unmodel_procedure(db_procedure) for db_procedure in db_visit.procedures],
    surgeries = [unmodel_surgery(db_surgery) for db_surgery  in db_visit.surgeries],
    medications = [unmodel_medication(db_medication) for db_medication in db_visit.medications],
    medical_items = [unmodel_medical_item(db_medical_item) for db_medical_item in db_visit.medical_items],
    nonpharmacologicals = [unmodel_nonpharmacological(db_nonpharmacological) for db_nonpharmacological in db_visit.non_pharmacologicals]
  )

def unmodel_appointment(db_appointment:Appointment):
  """Converts 'db_appointment' data from 'client' table into python dictionary string/JSON object"""

  _Appointment = namedtuple("_Appointment",["client_id","client_name","client_birthdate","client_gender","client_address","appointment_id","created_on","appointment_time","attendee_id","prepaid","made","done","cancelled","rescheduled","rescheduled_on","rescheduler_id"])

  return _Appointment(
    client_id = db_appointment.client.client_id,
    client_name = f"{db_appointment.client.first_name} {db_appointment.client.middle_name[0]} {db_appointment.client.last_name}",
    client_birthdate = db_appointment.client.birthdate,
    client_gender = db_appointment.client.gender,
    client_address = db_appointment.client.address,
    appointment_id = db_appointment.appointment_id,
    created_on = db_appointment.created_on,
    appointment_time = db_appointment.appointment_time,
    attendee_id = db_appointment.attendee_id,
    prepaid = db_appointment.prepaid,
    made = db_appointment.made,
    done = db_appointment.done,
    cancelled = db_appointment.cancelled,
    rescheduled = db_appointment.rescheduled,
    rescheduled_on = db_appointment.rescheduled_on,
    rescheduler_id = db_appointment.rescheduler_id
  )

def unmodel_next_of_kin(db_nextofkin:NextOfKin):
  """Converts row(s) from nextofkin table into dictionaries"""

  _NextOfKin = namedtuple("_NextOfKin",["client_id","next_kin_id","name","relation","mobile"])

  return _NextOfKin(
    client_id = db_nextofkin.client_id,
    next_kin_id = db_nextofkin.next_kin_id,
    name = f"{db_nextofkin.first_name} {db_nextofkin.last_name}",
    relation = db_nextofkin.relation,
    mobile = db_nextofkin.mobile
  )

def unmodel_client(db_client:Client):
  """Converts 'db_client' data from 'client' table into python dictionary string/JSON object"""

  _Client = namedtuple("_Client",["client_id","first_name","middle_name","last_name","created_on","birthdate","gender","marital_status","mobile","address","occupation","payment_mode","card_no","kins","visits","appointments"])

  return _Client(
    client_id = db_client.client_id,
    first_name = db_client.first_name,
    middle_name = db_client.middle_name,
    last_name = db_client.last_name,
    created_on = db_client.created_on,
    birthdate = db_client.birthdate,
    gender = db_client.gender,
    marital_status = db_client.marital_status,
    mobile = db_client.mobile,
    address = db_client.address,
    occupation = db_client.occupation,
    payment_mode = db_client.payment_mode,
    card_no = db_client.card_no,
    kins = [unmodel_next_of_kin(db_nextofkin) for db_nextofkin in db_client.kins],
    visits = [unmodel_visit(db_visit) for db_visit in db_client.visits],
    appointments = [unmodel_appointment(db_appointment) for db_appointment in db_client.appointments]
  )



###MISC FUNCTIONS
def get_duration(row_date:datetime) -> dict[str,int]:
  """Returns duration of 'date' from current time (now)"""
  
  duration = {"years":0,"months":0,"days":0,"hours":0,"minutes":0,"seconds":0,"milliseconds":0,"microseconds":0}

  date,now = row_date,datetime.now()
  delta_time = now - date
  

  years = delta_time.days//365
  months = delta_time.days%365//30
  days = delta_time.days%365%30
  hours = delta_time.seconds//3600
  minutes = delta_time.seconds%3600//60
  seconds = delta_time.seconds%3600%60
  milliseconds = delta_time.microseconds//1000
  microseconds = delta_time.microseconds%1000

  if years > 0:
    duration["years"] = years
  if months > 0:
    duration["months"] = months
  if days > 0:
    duration["days"] = days
  if hours > 0:
    duration["hours"] = hours
  if minutes > 0:
    duration["minutes"] = minutes
  if seconds > 0:
    duration["seconds"] = seconds
  if milliseconds > 0:
    duration["milliseconds"] = milliseconds
  if microseconds > 0:
    duration["microseconds"] = microseconds

  return duration

def format_age(birthdate:str):
  """Returns a string of formatted age based on the age returned from 'birthdate'"""

  years,months,days,hours,minutes = "","","","",""
  age_data = get_duration(birthdate)
  
  #Years
  if age_data["years"] > 0:
    years = f"{age_data['years']} years "
    if age_data["months"] > 6:
      months = f"{age_data['months']} months"
  
  #<1 year
  else:
    #Months
    if age_data["months"] > 0:
      months = f"{age_data['months']} months "
      if age_data["days"] > 20:
        days = f"{age_data['days']} days"
    
    #<1 month
    else:
      #Days
      if age_data["days"] > 0:
        days = f"{age_data['days']} days"
      
      #<1 day
      else:
        #Hours
        if age_data["hours"] > 0:
          hours = f"{age_data['hours']} hours"
        
        #<1 hour
        else:
          #Minutes
          if age_data["minutes"] > 0:
            minutes = f"{age_data['minutes']} minutes"
  
  return f"{years}{months}{days}{hours}{minutes}"

def is_in_range(start_date:str,end_date:str,target_date:datetime):
  """Returns True if 'target_date' is between 'start_date' and 'end_date'"""
    
  start_date,end_date,target_date = datetime.fromisoformat(start_date).date(),datetime.fromisoformat(end_date).date(),target_date.date()

  if target_date >= start_date and target_date <= end_date:
    return True
  else:
    return False
