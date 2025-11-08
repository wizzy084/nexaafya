"""Components for widgets"""

#GENERAL IMPORTS
from datetime import datetime

#NiceGUI IMPORTS
from nicegui import html,ui

#UIX imports
from .microwidgets import *





#
class VisitSummary():
  """A class for summary of client's visit"""

  def __init__(self,visit:dict):
    #DATA
    self.service_icons:dict[str,str] = {"dentist":"tooth","medical officer":"user-doctor","laboratory":"flask","pharmacy":"pills","radiology":"x-ray","procedure":"syringe","surgery":"scalpel"}
    
    #UI
    with html.div().classes(add="w-full bg-blue-700"):
      #General details
      with html.div().classes(add="w-full bg-orange-300"):
        ui.chip(text=f"{self.visit_time(visit['start_time'])[0]} {self.visit_time(visit['start_time'])[1]}",icon=f"fas fa-calendar-check fa-sm",color="sky-500").classes(add="text-bold")
        #Service
        if visit["consultation"]:
          with ui.chip(text=visit["consultation"],icon=f"fas fa-{self.service_icons[visit['consultation']]} fa-sm",color="sky-500").classes(add="text-bold text-yellow capitalize") as xi:
            with xi.add_slot("append"):
              ui.label('urwo83')
        
        #Payment mode
        ui.chip(text=visit["payment_mode"],icon="fas fa-wallet fa-sm",color="sky-500").classes(add="text-bold uppercase")
        
  
  def visit_time(self,datetime_str:str):
    "Returns a tuple with formatted date at index 0 and time at index 1"

    datetime_obj = datetime.fromisoformat(datetime_str)
    __date = datetime_obj.strftime("%d-%b-%Y").split("-")

    _date = f"{int(__date[0])} {__date[1]} {__date[2]}"
    _time = datetime_obj.strftime("%H:%M")


    return (_date,_time)