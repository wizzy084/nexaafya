from sqlmodel import Column,Field,ForeignKey,Integer,JSON,String,Relationship,SQLModel
from datetime import datetime,date,time
from typing import Any,Optional,Union



#CLIENTS

class Client(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'client' table in database"""

    id: int|None = Field(default=None,primary_key=True)
    client_id:int|None = Field(default=None,unique=True)
    first_name:str|None = None
    middle_name:str|None = None
    last_name:str|None = None
    created_on:datetime|None = None
    birthdate:datetime|None = None
    gender:str|None = None
    marital_status:str|None = None
    occupation:str|None = None
    mobile:str|None = None
    address:str|None = None
    payment_mode:str|None = None
    card_no:str|None = None

    kins:list["NextOfKin"] = Relationship(back_populates="client",sa_relationship_kwargs={"cascade":"all,delete"})
    visits:list["Visit"] = Relationship(sa_relationship_kwargs={"cascade":"all,delete"},back_populates="client")
    appointments:list["Appointment"] = Relationship(sa_relationship_kwargs={"cascade":"all,delete"},back_populates="client")

class NextOfKin(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'nextofkin' table in database"""

    id:int|None = Field(default=None,primary_key=True)
    next_kin_id:str|None = Field(default=None,unique=True)
    client_id:int|None = Field(default=None,sa_column=Column(Integer,ForeignKey("client.client_id",ondelete="CASCADE")))

    first_name:str|None = None
    last_name:str|None = None
    relation:str|None = None
    mobile:str|None = None

    client:Client|None = Relationship(back_populates="kins")

class Appointment(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'appointment' table in database"""

    id:int|None = Field(default=None,primary_key=True)
    appointment_id:str|None = Field(default=None,unique=True)
    client_id:int|None = Field(default=None,sa_column=Column(Integer,ForeignKey("client.client_id",ondelete="CASCADE")))

    created_on:datetime|None = None
    created_by:str|None = None
    appointment_time:datetime|None
    attendee_id:str|None = None
    prepaid:bool = False
    made:bool = True
    done:bool = False
    cancelled:bool = False
    rescheduled:bool = False
    rescheduled_on:datetime|None = None
    rescheduler_id:str|None = None

    client:Client|None = Relationship(back_populates="appointments")

class Visit(SQLModel,table=True,extend_existing=True):
    """Model to store visit details in database"""

    id:int|None = Field(default=None,primary_key=True)
    client_id:int|None = Field(default=None,sa_column=Column(Integer,ForeignKey("client.client_id",ondelete="CASCADE")))
    visit_id:str|None = Field(default=None,unique=True)
    
    attendee_id:str|None = None
    start_time:datetime|None = None
    end_time:datetime|None = None
    active:bool = True
    cancelled:bool = False
    payment_mode:str|None = None
    package:str = "standard"
    prescription_no:str|None = None

    client:Client|None = Relationship(back_populates="visits")
    
    payments:list["Payment"] = Relationship(back_populates="visit",sa_relationship_kwargs={"cascade":"all,delete"})
    vital_signs:list["VitalSigns"] = Relationship(back_populates="visit",sa_relationship_kwargs={"cascade":"all,delete"})
    anthropometrics:list["Anthropometrics"] = Relationship(back_populates="visit",sa_relationship_kwargs={"cascade":"all,delete"})
    consultations:list["Consultation"] = Relationship(back_populates="visit",sa_relationship_kwargs={"cascade":"all,delete"})
    laboratory_tests:list["Laboratory"] = Relationship(back_populates="visit",sa_relationship_kwargs={"cascade":"all,delete"})
    imagings:list["Imaging"] = Relationship(back_populates="visit",sa_relationship_kwargs={"cascade":"all,delete"})
    procedures:list["Procedure"] = Relationship(back_populates="visit",sa_relationship_kwargs={"cascade":"all,delete"})
    surgeries:list["Surgery"] = Relationship(back_populates="visit",sa_relationship_kwargs={"cascade":"all,delete"})
    medications:list["Medication"] = Relationship(back_populates="visit",sa_relationship_kwargs={"cascade":"all,delete"})
    medical_items:list["MedicalItem"] = Relationship(back_populates="visit",sa_relationship_kwargs={"cascade":"all,delete"})
    non_pharmacologicals:list["NonPharmacological"] = Relationship(back_populates="visit",sa_relationship_kwargs={"cascade":"all,delete"})
    treatment_logs:list["TreatmentLog"] = Relationship(back_populates="visit",sa_relationship_kwargs={"cascade":"all,delete"})
    bedrest:Optional["Bedrest"] = Relationship(back_populates="visit",sa_relationship_kwargs={"cascade":"all,delete"})
    admission:Optional["Admission"] = Relationship(back_populates="visit",sa_relationship_kwargs={"cascade":"all,delete"})

class Payment(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'payment' table in database"""

    id:int|None = Field(default=None,primary_key=True)
    visit_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("visit.visit_id",ondelete="CASCADE")))
    consultation_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("consultation.consultation_id",ondelete="CASCADE")))
    anthropometrics_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("anthropometrics.anthropometrics_id",ondelete="CASCADE")))
    vitals_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("vitalsigns.vitals_id",ondelete="CASCADE")))
    lab_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("laboratory.lab_id",ondelete="CASCADE")))
    imaging_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("imaging.imaging_id",ondelete="CASCADE")))
    procedure_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("procedure.procedure_id",ondelete="CASCADE")))
    surgery_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("surgery.surgery_id",ondelete="CASCADE")))
    medication_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("medication.medication_id",ondelete="CASCADE")))
    medical_item_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("medicalitem.medical_item_id",ondelete="CASCADE")))
    nonpharmacological_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("nonpharmacological.nonpharmacological_id",ondelete="CASCADE")))
    bedrest_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("bedrest.bedrest_id",ondelete="CASCADE")))
    admission_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("admission.admission_id",ondelete="CASCADE")))

    payment_id:str|None = Field(default=None,unique=True)
    created_on:datetime|None = None

    authorization_no:str|None = None
    cost:float = Field(default=0)
    payment_mode:str|None = None
    billed:bool = False
    billed_amount:float = Field(default=0)
    billing_time:datetime|None = None
    paid:bool = False
    paid_amount:float = Field(default=0)
    payment_time:datetime|None = None
    cancelled:bool = False
    cancel_time:datetime|None = None
    cancelled_by:str|None = None
    refundable:bool = True
    refunded:bool = False
    refunded_amount:float = Field(default=0)
    refunding_time:datetime|None = None

    visit:Visit|None = Relationship(back_populates="payments")
    consultation:Optional["Consultation"] = Relationship(back_populates="payment")
    anthropometrics:Optional["Anthropometrics"] = Relationship(back_populates="payment")
    vitalsigns:Optional["VitalSigns"] = Relationship(back_populates="payment")
    laboratory:Optional["Laboratory"] = Relationship(back_populates="payment")
    imaging:Optional["Imaging"] = Relationship(back_populates="payment")
    procedure:Optional["Procedure"] = Relationship(back_populates="payment")
    surgery:Optional["Surgery"] = Relationship(back_populates="payment")
    medication:Optional["Medication"] = Relationship(back_populates="payment")
    medical_item:Optional["MedicalItem"] = Relationship(back_populates="payment")
    nonpharmacological:Optional["NonPharmacological"] = Relationship(back_populates="payment")
    bedrest:Optional["Bedrest"] = Relationship(back_populates="payment")
    admission:Optional["Admission"] = Relationship(back_populates="payment")

class Anthropometrics(SQLModel,table=True,extend_existing=True):
    """Model to store anthropometrics of client in each visit"""

    id:int|None = Field(default=None,primary_key=True)
    anthropometrics_id:str|None = Field(default=None,unique=True)
    visit_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("visit.visit_id",ondelete="CASCADE")))
    attendee_id:str|None = None
    
    anthropometrics_time:datetime|None = None
    weight:float|None = Field(default=None)
    height:float|None = Field(default=None)
    head_circumference:float|None = Field(default=None)
    muac:float|None = Field(default=None)
    done:bool = False
    

    visit:Visit|None = Relationship(back_populates="anthropometrics")
    payment:Payment|None = Relationship(back_populates="anthropometrics")

class VitalSigns(SQLModel,table=True,extend_existing=True):
    """Model to store and retrieve vital signs of client's particular visit into the database"""

    id:int|None = Field(default=None,primary_key=True)
    vitals_id:str|None = Field(default=None,unique=True)
    visit_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("visit.visit_id",ondelete="CASCADE")))
    attendee_id:str|None = None
    
    vitals_time:datetime|None = None
    systolic_blood_pressure:int|None = Field(default=None)
    diastolic_blood_pressure:int|None = Field(default=None)
    pulse_rate:int|None = Field(default=None)
    respiratory_rate:int|None = Field(default=None)
    temperature:float|None = Field(default=None)
    oxygen_saturation:int|None = Field(default=None)
    done:bool = False
    

    visit:Visit|None = Relationship(back_populates="vital_signs")
    payment:Payment|None = Relationship(back_populates="vitalsigns")

class Laboratory(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'laboratory' table in database"""

    id:int|None = Field(default=None,primary_key=True)
    lab_id:str|None = Field(default=None,unique=True)
    visit_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("visit.visit_id",ondelete="CASCADE")))
    attendee_id:str|None = None

    test:str|None = None
    request_time:datetime|None = None
    results:str|None = None
    results_time:datetime|None = None
    processed:bool = False
    test_performer_id:str|None = None
    results_verifier_id:str|None = None
    results_doc:str|None = None
    cancelled:bool = False
    cancelled_on:datetime|None = None
    cancelled_by:str|None = None
    editable:bool = True
    edited:bool = False
    last_edited_on:datetime|None = None
    editor_id:str|None = None

    visit:Visit|None = Relationship(back_populates="laboratory_tests")
    payment:Payment|None = Relationship(back_populates="laboratory")

class Imaging(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'imaging' table in database"""

    id:int|None = Field(default=None,primary_key=True)
    imaging_id:str|None = Field(default=None,unique=True)
    visit_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("visit.visit_id",ondelete="CASCADE")))
    attendee_id:str|None = None

    study:str|None = None
    notes:str|None = None
    request_time:datetime|None = None
    results:str|None = None
    results_attachments:str|None = None
    results_time:datetime|None = None
    processed:bool = False
    radiographer:str|None = None
    radiologist:str|None = None
    results_img:str|None = None
    results_doc:str|None = None
    cancelled:bool = False
    cancelled_on:datetime|None = None
    cancelled_by:str|None = None
    editable:bool = True
    edited:bool = False
    last_edited_on:datetime|None = None
    editor_id:str|None = None

    visit:Visit|None = Relationship(back_populates="imagings")

    payment:Payment|None = Relationship(back_populates="imaging")

class Procedure(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'cns_exams' table in database"""

    id:int|None = Field(default=None,primary_key=True)
    procedure_id:str|None = Field(default=None,unique=True)
    visit_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("visit.visit_id",ondelete="CASCADE")))
    attendee_id:str|None = None

    name:str|None = None
    count:int = 1
    performer:str|None = None
    assistant:str|None = None
    ordered_on:datetime|None = None
    done:bool = False
    done_on:datetime|None = None
    procedure_notes:str|None = None
    cancelled:bool = False
    cancelled_on:datetime|None = None
    cancelled_by:str|None = None
    editable:bool = True
    edited:bool = False
    last_edited_on:datetime|None = None
    editor_id:str|None = None

    visit:Visit|None = Relationship(back_populates="procedures")

    payment:Payment|None = Relationship(back_populates="procedure")

class Surgery(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'surgery' table in database"""

    id:int|None = Field(default=None,primary_key=True)
    surgery_id:str|None = Field(default=None,unique=True)
    visit_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("visit.visit_id",ondelete="CASCADE")))
    attendee_id:str|None = None

    operation:str|None = None
    count:int = 0
    planned_on:datetime|None = None
    done:bool = False
    operation_time:datetime|None = None
    time_in:datetime|None = None
    time_out:time|None = None
    surgeon:str|None = None
    assistant_surgeon:str|None = None
    scrub_nurse:str|None = None
    running_nurse:str|None = None
    anaesthetist:str|None = None
    anaesthesiologist:str|None = None
    anaesthesia:str|None = None
    surgery_notes:str|None = None
    consent_form:str|None = None
    check_list:str|None = None
    anaesthesia_chart:str|None = None
    cancelled:bool = False
    cancelled_on:datetime|None = None
    cancelled_by:str|None = None
    editable:bool = True
    edited:bool = False
    last_edited_on:datetime|None = None
    editor_id:str|None = None

    visit:Visit|None = Relationship(back_populates="surgeries")

    payment:Payment|None = Relationship(back_populates="surgery")

class Medication(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'medication' table in database"""

    id:int|None = Field(default=None,primary_key=True)
    medication_id:str|None = Field(default=None,unique=True)
    visit_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("visit.visit_id",ondelete="CASCADE")))
    prescriber_id:str|None = None

    name:str|None = None
    dosage:str|None = None
    prescribed_items_no:int = 0
    dispensed_items_no:int = 0
    prescribed_on:datetime|None = None
    cancelled:bool = False
    cancelled_on:datetime|None = None
    cancelled_by:str|None = None
    editable:bool = True
    edited:bool = False
    editor_id:str|None = None
    last_edited_on:datetime|None = None
    dispensed:bool = False
    dispensing_time:datetime|None = None
    dispenser_id:str|None = None


    visit:Visit|None = Relationship(back_populates="medications")

    payment:Payment|None = Relationship(back_populates="medication")

class MedicalItem(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'medicalitem' table in database"""

    id:int|None = Field(default=None,primary_key=True)
    medical_item_id:str|None = Field(default=None,unique=True)
    visit_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("visit.visit_id",ondelete="CASCADE")))
    prescriber_id:str|None = None

    name:str|None = None
    prescribed_items_no:int = 0
    dispensed_items_no:int = 0
    prescribed_on:datetime|None = None
    cancelled:bool = False
    cancelled_on:datetime|None = None
    cancelled_by:str|None = None
    editable:bool = True
    edited:bool = False
    editor_id:str|None = None
    last_edited_on:datetime|None = None
    dispensed:bool = False
    dispensing_time:datetime|None = None
    dispenser_id:str|None = None

    visit:Visit|None = Relationship(back_populates="medical_items")

    payment:Payment|None = Relationship(back_populates="medical_item")

class NonPharmacological(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'nonmedical' table in database"""

    id:int|None = Field(default=None,primary_key=True)
    nonpharmacological_id:str|None = Field(default=None,unique=True)
    visit_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("visit.visit_id",ondelete="CASCADE")))
    attendee_id:str|None = None

    name:str|None = None
    planned_on:str|None = None
    notes:str|None = None
    done:bool = False
    done_on:str|None = None
    cancelled:bool = False
    cancelled_on:str|None = None
    cancelled_by:str|None = None
    editable:bool = True
    edited:bool = False
    last_edited_on:str|None = None
    editor_id:str|None = None

    visit:Visit|None = Relationship(back_populates="non_pharmacologicals")

    payment:Payment|None = Relationship(back_populates="nonpharmacological")


#Consultation
class Consultation(SQLModel,table=True,extend_existing=True):
    """Model to store consultation file details in database"""

    id:int|None = Field(default=None,primary_key=True)
    consultation_id:str|None = Field(default=None,unique=True)
    visit_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("visit.visit_id",ondelete="CASCADE")))
    consultant_id:str|None = None
    
    name:str|None = None
    cadre:str|None = None
    level:str|None = None
    initiated:bool = False
    start_time:datetime|None = None
    cancelled:bool = False

    visit:Visit|None = Relationship(back_populates="consultations")
    
    payment:Payment|None = Relationship(back_populates="consultation",sa_relationship_kwargs={"cascade":"all,delete"})
    clinical_histories:list["ClinicalHistory"] = Relationship(back_populates="consultation",sa_relationship_kwargs={"cascade":"all,delete"})
    derma_exams:list["DermatologicalExamination"] = Relationship(back_populates="consultation",sa_relationship_kwargs={"cascade":"all,delete"})
    mss_exams:list["MusculoskeletalExamination"] = Relationship(back_populates="consultation",sa_relationship_kwargs={"cascade":"all,delete"})
    gus_exams:list["GenitourinaryExamination"] = Relationship(back_populates="consultation",sa_relationship_kwargs={"cascade":"all,delete"})
    abd_exams:list["AbdominalExamination"] = Relationship(back_populates="consultation",sa_relationship_kwargs={"cascade":"all,delete"})
    rs_exams:list["RespiratoryExamination"] = Relationship(back_populates="consultation",sa_relationship_kwargs={"cascade":"all,delete"})
    cvs_exams:list["CardiovascularExamination"] = Relationship(back_populates="consultation",sa_relationship_kwargs={"cascade":"all,delete"})
    cns_exams:list["CNSExamination"] = Relationship(back_populates="consultation",sa_relationship_kwargs={"cascade":"all,delete"})
    orodental_exams:list["OrodentalExamination"] = Relationship(back_populates="consultation",sa_relationship_kwargs={"cascade":"all,delete"})
    ge_exams:list["GeneralExamination"] = Relationship(back_populates="consultation",sa_relationship_kwargs={"cascade":"all,delete"})
    diagnoses:list["Diagnosis"] = Relationship(back_populates="consultation",sa_relationship_kwargs={"cascade":"all,delete"})

class ClinicalHistory(SQLModel,table=True,extend_existing=True):
    """Model to store data about client's clinical history at each given visit"""

    id:int|None = Field(default=None,primary_key=True)
    hx_id:str|None = Field(default=None,unique=True)
    consultation_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("consultation.consultation_id",ondelete="CASCADE")))
    
    history_time:datetime|None = None
    chief_complaints:str|None = Field(default=None)
    hpi1:str|None = Field(default=None)
    hpi2:str|None = Field(default=None)
    hpi3:str|None = Field(default=None)
    systems_review:str|None = Field(default=None)
    medical_history:str|None = Field(default=None)
    surgical_history:str|None = Field(default=None)
    family_history:str|None = Field(default=None)
    social_history:str|None = Field(default=None)
    editable:bool = True
    edited:bool = False
    last_edited_on:datetime|None = None
    editor_id:str|None = None

    consultation:Consultation|None = Relationship(back_populates="clinical_histories")

class GeneralExamination(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'ge_exams' table in database"""

    id:int|None = Field(default=None,primary_key=True)
    ge_id:str|None =  Field(default=None,unique=True)
    consultation_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("consultation.consultation_id",ondelete="CASCADE")))
    
    ge_exam_time:datetime|None = None
    notes:str|None = None
    editable:bool = True
    edited:bool = False
    last_edited_on:datetime|None = None
    editor_id:str|None = None

    consultation:Consultation|None = Relationship(back_populates="ge_exams")

class OrodentalExamination(SQLModel,table=True,extend_existing=True):
    """A model for storing physical examination details in database"""

    id:int|None = Field(default=None,primary_key=True)
    orodental_exam_id:str|None = Field(default=None,unique=True)
    consultation_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("consultation.consultation_id",ondelete="cascade")))
    
    orodental_exam_time:datetime|None = None
    extraoral:str|None = None
    intraoral:str|None = Field(default=None)
    editable:bool = True
    edited:bool = False
    last_edited_on:datetime|None = None
    editor_id:str|None = None

    consultation:Consultation|None = Relationship(back_populates="orodental_exams")

class CNSExamination(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'cns_exams' table in database"""

    id:int|None = Field(default=None,primary_key=True)
    cns_exam_id:str|None = Field(default=None,unique=True)
    consultation_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("consultation.consultation_id",ondelete="CASCADE")))
    
    cns_exam_time:datetime|None = None
    gcs:str = '{"e":4,"v":5,"m":6}'
    cranials:str|None = None
    dermatomes:str|None = None
    myotomes:str|None = None
    gait:str|None = None
    reflexes:str|None = None
    special_tests:str|None = None
    editable:bool = True
    edited:bool = False
    last_edited_on:datetime|None = None
    editor_id:str|None = None

    consultation:Consultation|None = Relationship(back_populates="cns_exams")

class CardiovascularExamination(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'cvs_exams' table in database"""

    id:int|None = Field(default=None,primary_key=True)
    cvs_exam_id:str|None = Field(default=None,unique=True)
    consultation_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("consultation.consultation_id",ondelete="CASCADE")))
    
    cvs_exam_time:datetime|None = None
    inverted_j:str|None = None
    inspection:str|None = None
    palpation:str|None = None
    auscultation:str|None = None
    special_tests:str|None = None
    editable:bool = True
    edited:bool = False
    last_edited_on:datetime|None = None
    editor_id:str|None = None

    consultation:Consultation|None = Relationship(back_populates="cvs_exams")

class RespiratoryExamination(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'rs_exams' table in database"""

    id:int|None = Field(default=None,primary_key=True)
    rs_exam_id:str|None = Field(default=None,unique=True)
    consultation_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("consultation.consultation_id",ondelete="CASCADE")))
    
    rs_exam_time:datetime|None = None
    inspection:str|None = None
    palpation:str|None = None
    percussion:str|None = None
    auscultation:str|None = None
    special_tests:str|None = None
    editable:bool = True
    edited:bool = False
    last_edited_on:datetime|None = None
    editor_id:str|None = None

    consultation:Consultation|None = Relationship(back_populates="rs_exams")

class AbdominalExamination(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'abdominalexamination' table in database"""

    id:int|None = Field(default=None,primary_key=True)
    abd_exam_id:str|None = Field(default=None,unique=True)
    consultation_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("consultation.consultation_id",ondelete="CASCADE")))
    
    abd_exam_time:datetime|None = None
    inspection:str|None = None
    palpation:str|None = None
    percussion:str|None = None
    auscultation:str|None = None
    dre:str|None = None
    special_tests:str|None = None
    editable:bool = True
    edited:bool = False
    last_edited_on:datetime|None = None
    editor_id:str|None = None

    consultation:Consultation|None = Relationship(back_populates="abd_exams")

class GenitourinaryExamination(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'genitourinaryexamination' table in database"""

    id:int|None = Field(default=None,primary_key=True)
    gus_exam_id:str|None = Field(default=None,unique=True)
    consultation_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("consultation.consultation_id",ondelete="CASCADE")))
    
    gus_exam_time:datetime|None = None
    inspection:str|None = None
    palpation:str|None = None
    special_tests:str|None = None
    editable:bool = True
    edited:bool = False
    last_edited_on:datetime|None = None
    editor_id:str|None = None

    consultation:Consultation|None = Relationship(back_populates="gus_exams")

class MusculoskeletalExamination(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'musculoskeletalexamination' table in database"""

    id:int|None = Field(default=None,primary_key=True)
    mss_exam_id:str|None = Field(default=None,unique=True)
    consultation_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("consultation.consultation_id",ondelete="CASCADE")))
    
    mss_exam_time:datetime|None = None
    upper_limbs:str|None = None
    lower_limbs:str|None = None
    special_tests:str|None = None
    editable:bool = True
    edited:bool = False
    last_edited_on:datetime|None = None
    editor_id:str|None = None

    consultation:Consultation|None = Relationship(back_populates="mss_exams")

class DermatologicalExamination(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'dermatologicalexamination' table"""

    id:int|None = Field(default=None,primary_key=True)
    derma_exam_id:str|None = Field(default=None,unique=True)
    consultation_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("consultation.consultation_id",ondelete="CASCADE")))
    
    derma_exam_time:datetime|None = None
    primary_lesions:str|None = None
    secondary_lesions:str|None = None
    special_tests:str|None = None
    editable:bool = True
    edited:bool = False
    last_edited_on:datetime|None = None
    editor_id:str|None = None

    consultation:Consultation|None = Relationship(back_populates="derma_exams")

class Diagnosis(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'diagnosis' table"""

    id:int|None = Field(default=None,primary_key=True)
    diagnosis_id:str|None = Field(default=None,unique=True)
    consultation_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("consultation.consultation_id",ondelete="CASCADE")))

    provisional:str|None = None
    provisional_generic:str|None = None
    provisional_icd:str|None = None
    differentials:str|None = None
    definitive:str|None = None
    definitive_generic:str|None = None
    definitive_icd:str|None = None

    consultation:Consultation|None = Relationship(back_populates="diagnoses")

class Bedrest(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'bedrest' table in database"""

    id:int|None = Field(default=None,primary_key=True)
    bedrest_id:str|None = Field(default=None,unique=True)
    visit_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("visit.visit_id",ondelete="CASCADE")))

    bedrest_time:datetime|None = datetime.now()
    bedrested_by:str|None = None
    discharge_time:datetime|None = None
    discharged_by:str|None = None
    active:bool = True
    cancelled:bool = False
    indications:str|None = None

    department:str|None = None
    section:str|None = None
    ward_no:int|None = None
    ward_name:str|None = None
    bed_no:int|None = None
    new:bool = True
    from_admission:bool = False

    visit:Visit|None = Relationship(back_populates="bedrest")

    payment:Payment|None = Relationship(back_populates="bedrest",sa_relationship_kwargs={"cascade":"all,delete"})

class Admission(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'admission' table in database"""

    id:int|None = Field(default=None,primary_key=True)
    admission_id:str|None = Field(default=None,unique=True)
    visit_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("visit.visit_id",ondelete="CASCADE")))

    admission_time:datetime|None = datetime.now()
    admitted_by:str|None = None
    discharge_time:datetime|None = None
    discharged_by:str|None = None
    active:bool = True
    cancelled:bool = False
    indications:str|None = None

    department:str|None = None
    section:str|None = None
    ward_no:int|None = None
    ward_name:str|None = None
    bed_no:int|None = None
    new:bool = True
    from_bedrest:bool = False

    visit:Visit|None = Relationship(back_populates="admission")

    payment:Payment|None = Relationship(back_populates="admission",sa_relationship_kwargs={"cascade":"all,delete"})

class TreatmentLog(SQLModel,table=True,extend_existing=True):
    """A model to store and retrieve data from 'treatmentlog' table in database"""

    id:int|None = Field(default=None,primary_key=True)
    treatment_log_id:str|None = Field(default=None,unique=True)
    visit_id:str|None = Field(default=None,sa_column=Column(String,ForeignKey("visit.visit_id",ondelete="CASCADE")))
    
    medication:str|None = None
    dosage:str|None = None
    procedure:str|None = None
    surgery:str|None = None
    time:datetime = datetime.now()
    logger:str|None = None
    remarks:str|None = None
    
    visit:Visit|None = Relationship(back_populates="treatment_logs")


