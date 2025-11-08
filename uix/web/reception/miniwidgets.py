"""A module to construct components for widgets"""

#GENERAL IMPORTS
import calendar
from datetime import datetime

#NICEGUI IMPORTS
from nicegui import html,ui

#APP IMPORTS
from services.provider.clients.processor import *
from services.provider.clients.db import *
from services.provider.admin.processor import get_services,database_is_present as db_present

#UIX IMPORT
from ..tools._snippets import get_duration


#
class ReportFrame():
  """A class for structuring report"""
  
  @ui.refreshable_method
  def __init__(self,start_date:str,end_date:str):
    
    #Data retrieval
    self.visits = [visit for visit in get_visits() if self.is_in_range(start_date=start_date,end_date=end_date,target_date=visit["start_time"])]
    #Revisits
    self.new_visits = [visit for visit in self.visits if visit["client_registered"] >= datetime.fromisoformat(start_date)]
    
    #Male visits
    self.male_visits = [visit for visit in self.visits if visit["client_gender"] == "Male"]
    #0 - 7 days
    self.early_neonates = [visit for visit in self.visits if (("years" not in get_duration(visit["client_birthdate"]) and ("months" not in get_duration(visit["client_birthdate"])) and (get_duration(visit["client_birthdate"])["days"] <= 7)))]
    #8 - 28 days
    self.late_neonates = [visit for visit in self.visits if (("years" not in get_duration(visit["client_birthdate"]) and ("months" not in get_duration(visit["client_birthdate"])) and (get_duration(visit["client_birthdate"])["days"] > 7)))]
    #1 - 5 years
    self.toddlers = [visit for visit in [_visit for _visit in self.visits if (get_duration(_visit["client_birthdate"]).get("years"))] if get_duration(visit["client_birthdate"]).get("years") < 5]
    #5 -12 years
    self.children = [visit for visit in [_visit for _visit in self.visits if (get_duration(_visit["client_birthdate"]).get("years"))] if (get_duration(visit["client_birthdate"]).get("years") >= 5 and get_duration(visit["client_birthdate"]).get("years") < 13)]
    #13 - 19 years
    self.adolescents = [visit for visit in [_visit for _visit in self.visits if (get_duration(_visit["client_birthdate"]).get("years"))] if (get_duration(visit["client_birthdate"]).get("years") >= 12 and get_duration(visit["client_birthdate"]).get("years") < 20)]
    #20 - 39 years
    self.adults = [visit for visit in [_visit for _visit in self.visits if (get_duration(_visit["client_birthdate"]).get("years"))] if (get_duration(visit["client_birthdate"]).get("years") >= 20 and get_duration(visit["client_birthdate"]).get("years") < 40)]
    #40 - 59 years
    self.middle_adults = [visit for visit in [_visit for _visit in self.visits if (get_duration(_visit["client_birthdate"]).get("years"))] if (get_duration(visit["client_birthdate"]).get("years") >= 40 and get_duration(visit["client_birthdate"]).get("years") < 60)]
    #Elderly
    self.elderly = [visit for visit in [_visit for _visit in self.visits if (get_duration(_visit["client_birthdate"]).get("years"))] if get_duration(visit["client_birthdate"]).get("years") >= 60]

    #Visits
    with html.div().classes(add="bg-gray-700"):
      with html.span().classes(add="w-full pb-2 flex flex-row text-bold text-lg"):
        ui.label(f"{len(self.visits)}").classes(add="ml-2 mr-1 text-emerald-400 text-bold text-2xl")
        ui.label(text="visits" if (len(self.visits) > 1 or len(self.visits) == 0) else "visit").classes(add="text-sky-400 italic text-2xl")
    
    #Analytics
    with html.div().classes(add="grid grid-cols-4 gap-1 bg-gray-700"):
      #Visit status
      with html.div().classes(add="col-span-2 w-full justify-self-center"):
        ui.label('Visits').classes(add="w-full bg-black px-2 rounded-t text-sky-400 text-bold text-lg uppercase")
        ui.table(
          columns=[
            {"name":"new_visits","label":"New Visits","field":"new_visits"},
            {"name":"revisits","label":"Revisits","field":"revisits"},
          ],
          rows=[
            {"new_visits":len(self.new_visits),"revisits":len(self.visits) - len(self.new_visits)}
          ],
          column_defaults={
            "align":"left",
            "headerClasses":"uppercase text-primary bg-"
          }
        ).classes(add="")

      #Gender
      with html.div().classes(add="col-span-2 w-full justify-self-center"):
        ui.label("Gender").classes(add="w-full bg-black px-2 rounded-t text-sky-400 text-bold text-lg uppercase")
        ui.table(
          columns=[
            {"name":"male","label":"Male","field":"male","align":"left"},
            {"name":"female","label":"Female","field":"female","align":"left"},
          ],
          rows=[
            {"male":len(self.male_visits),"female":len(self.visits) - len(self.male_visits)}
          ],
          column_defaults={
            "align":"left",
            "headerClasses":"text-primary uppercase"
          }
        ).classes(add="")
      
      #Age
      with html.div().classes(add="w-full col-span-4"):
        ui.label("Age distribution").classes(add="w-full bg-black px-2 rounded-t text-sky-400 text-bold text-lg uppercase")
        ui.table(
          columns=[
            {"name":"early_neonates","label":"0 - 7 days","field":"early_neonates"},
            {"name":"late_neonates","label":"8 - 28 days","field":"late_neonates"},
            {"name":"infants","label":"1 - 11 months","field":"infants"},
            {"name":"toddlers","label":"1 - 4 years","field":"toddlers"},
            {"name":"children","label":"5 - 12 years","field":"children"},
            {"name":"adolescents","label":"13 - 19 years","field":"adolescents"},
            {"name":"adults","label":"20 - 39 years","field":"adults"},
            {"name":"middle_aged","label":"40 - 59 years","field":"middle_aged"},
            {"name":"elderly","label":"60+ years","field":"elderly"}
          ],
          rows=[{
            "early_neonates":len(self.early_neonates),
            "late_neonates":len(self.late_neonates),
            "infants":self.count_infants(),
            "toddlers":len(self.toddlers),
            "children":len(self.children),
            "adolescents":len(self.adolescents),
            "adults":len(self.adults),
            "middle_aged":len(self.middle_adults),
            "elderly":len(self.elderly)
          }],
          column_defaults={
            "align":"left",
            "headerClasses":"uppercase text-primary"
            }
        ).classes(add="w-full")
  
  def count_infants(self):
    """A method that returns a length of list of visits from self.visits with age of < 1 year and > 1 month or > 28 days"""
    infants:list = []
    for visit in self.visits:
      if not get_duration(visit["client_birthdate"]).get("years"):
        if get_duration(visit["client_birthdate"]).get("months"):
          infants.append(visit)
        else:
          if get_duration(visit["client_birthdate"]).get("days"):
            if get_duration(visit["client_birthdate"]).get("days") > 28:
              infants.append(visit)

    return len(infants)
  
  def is_in_range(self,start_date:str,end_date:str,target_date:str):
    """Returns True if 'target_date' is between 'start_date' and 'end_date'"""
    
    start_date,end_date,target_date = datetime.fromisoformat(start_date).date(),datetime.fromisoformat(end_date).date(),target_date.date()

    if target_date >= start_date and target_date <= end_date:
      return True
    else:
      return False
