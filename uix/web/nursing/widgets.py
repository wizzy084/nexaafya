"""A module to degign widgets for 'imaging' functionality"""

#GENERAL IMPORTS
import math
from uuid import uuid4

#NiceGUI IMPORTS
from nicegui import html,ui

#APP IMPORTS
from services.provider.admin.db import register_medicine,update_requisition,update_medicine,register_inventory
from services.provider.admin.processor import get_staff as staff,get_requisitions,get_formulary
from services.provider.clients.db import update_medicine as update_client_medicine,register_triage,update_triage
from services.provider.clients.processor import get_active_visits,get_pharmacy_visits

#UIX IMPORTS
from ..tools._snippets import *
from ..tools.components import ClientCard
from ..tools.widgets import Requisitions,StockAnalysisDisplay,FacilityFormulary,DispensingStoreManagement


#WIDGETS
class NursingServicesManagementDisplay():
  """A class for UI displays for nursing services management"""

  def __init__(self,user):
    #DATA
    self.user = user

    #UI
    with html.div().classes(add="w-full h-full flex flex-col p-0 gap-1 bg-inherit animate__animated animate__fadeIn") as self.master_container:
      self.Carousel(triage=False)
  
  #Displays
  def Carousel(self,triage:str|None=None,dispensing:bool=False):
    #DATA
    value = "triage" if triage else "dispensing"
    #UI
    self.master_container.clear()
    with self.master_container.classes(remove=""):
      with ui.carousel(value=value).style(add="overflow-y:hidden;").props(add="animated swipeable transition-prev='jump-right' transition-next='jump-left' transition-duration='100'").classes(add="grow flex flex-col q-pa-none w-full bg-inherit rounded shadow-md shadow-blue-500 animate__animated animate__fadeIn") as carousel:
        with carousel.add_slot("default"):
          #Triage
          with ui.carousel_slide(name="triage").classes(add="q-pa-none gap-0 w-full h-full rounded-b"):
            #For large screens
            with html.div().classes(add="w-full grow lg-show") as self.triages_panel:
              TriageManagementDisplay(user=self.user)
            #For small screens
            with html.div().classes(add="grow w-full lg:hidden") as self.triages_mini_panel:
              TriageManagementDisplay(user=self.user,mini=True)
          
          #Dispensing
          with ui.carousel_slide(name="dispensing").classes(add="q-pa-none p-0.5 gap-0 w-full h-full rounded-b"):
            #For large screens
            with html.div().classes(add="w-full grow lg-show") as self.dispensing_panel:
              DispensingManagementDisplay(user=self.user)
            #For small screens
            with html.div().classes(add="grow w-full lg:hidden") as self.dispensing_mini_panel:
              DispensingManagementDisplay(user=self.user)

      #Controls
      with html.div().classes(add="w-full py-1 flex flex-row justify-center gap-5 lg:gap-7"):
        ui.toggle(options=["triage","dispensing"]).props(add="glossy size='lg' toggle-color='bg-inherit' toggle-text-color='sky-500' text-color='yellow-500'").classes(add="lg-show bg-[#07004d] rounded-full ring-1 ring-blue-500 shadow-md shadow-sky-600 text-bold").bind_value(carousel)
    


#SUBWIDGETS
class TriageManagementDisplay():
  """A class to display UI for triage management"""

  def __init__(self,user,mini:bool=False):
    #DATA
    self.user = user
    self.initial_data()
    
    #UI
    with html.div().classes(add=f"w-full h-full flex flex-col {'' if self.triage_visits else 'justify-center content-center bg-white rounded-b'}"):
      if self.triage_visits:
        ui.separator().classes(add="w-full bg-[#09026f]")
        with html.div().classes(add="w-full p-2 bg-harmony flex flex-row"):
          ui.label("TODAY VISITS").classes(add="").classes(add="bg-inherit grow text-3xl text-yellow-500 text-bold")
          with html.div().classes(add="bg-inherit") as self.stats_panel:
            self.TriageStats()
        #Displays
        with html.div().classes(add="w-full grow bg-white rounded-b") as self.display_panel:
          if mini:
            self.TriagesMiniDisplay()
          else:
            self.TriagesDisplay()
      else:
        with html.div().classes(add="bg-inherit flex flex-col gap-2 p-3 text-bold"):
          ui.label("No clients for now").classes(add="text-3xl text-rose-500")
          ui.label("Just relax and have fun!").classes(add="italic text-center text-2xl text-pink-300")

  #FUNCTIONALITIES
  def initial_data(self):
    self.triage_visits = [visit for visit in get_active_visits() if visit["vital_signs"] or visit["anthropometrics"]]
    self.done_triages = [visit for visit in self.triage_visits if self.triage_status(visit) == "done"]
    self.not_done_triages = [visit for visit in self.triage_visits if self.triage_status(visit) == "not done"]
    self.incomplete_triages = [visit for visit in self.triage_visits if self.triage_status(visit) == "incomplete"]
  
  def payment_status(self,visit:dict):
    """Returns a string representing payment status of imagings"""

    statuses = set()

    triages = visit["vital_signs"] + visit["anthropometrics"]
    
    for triage in triages:
      if triage["payment"]["paid"] and not triage["payment"]["billed"]:
        statuses.add("paid")
      if triage["payment"]["billed"] and not triage["payment"]["paid"]:
        statuses.add("billed")
      if not triage["payment"]["billed"] and not triage["payment"]["paid"]:
        statuses.add("not paid")
    
    if len(statuses) == 1:
      for status in statuses:
        return status
    else:
      return "partial"
    
  def triage_status(self,visit:dict):
    """Returns a string representing payment status of triage services"""

    statuses = set()

    vital = visit["vital_signs"][-1] if visit["vital_signs"] else None
    #Vitals
    if vital:
      if vital["done"]:
        if (vital["temperature"] and vital["pulse_rate"] and vital["resp_rate"] and vital["o2sat"]) or (vital["sbp"] and vital["dbp"]):
          statuses.add("done")
        elif (vital["temperature"] or vital["sbp"] or vital["dbp"] or vital["pulse_rate"] or vital["resp_rate"] or vital["o2sat"]):
          statuses.add("incomplete")
      else:
        statuses.add("not done")
    else:
      statuses.add("not done")
    
    #Anthropometrics
    if visit["anthropometrics"]:
      if get_duration(visit["client_birthdate"])["years"] > 2:
        _anthrops_all = [_anthrop for _anthrop in visit["anthropometrics"] if _anthrop["weight"] and _anthrop["height"]]
        _anthrops_some = [_anthrop for _anthrop in visit["anthropometrics"] if _anthrop["weight"] or _anthrop["height"]]
      else:
        _anthrops_all = [_anthrop for _anthrop in visit["anthropometrics"] if _anthrop["weight"] and _anthrop["height"] and _anthrop["muac"] and _anthrop["head_circum"]]
        _anthrops_some = [_anthrop for _anthrop in visit["anthropometrics"] if _anthrop["weight"] or _anthrop["height"] or _anthrop["muac"] or _anthrop["head_circum"]]
      
      if _anthrops_all:
        statuses.add("done")
      elif _anthrops_some:
        statuses.add("incomplete")
      else:
        statuses.add("not done")
    else:
      statuses.add("not done")
    
    if len(statuses) == 1:
      return statuses.pop()
    else:
      return "incomplete"
    
  def relay_dialogs(self,visit:dict):
    """Decides which dialog to display"""

    status = self.triage_status(visit)

    if status == "Done" or status == "Incomplete":
      self.TriagesDialog(visit)
    else:
      self.NewTriageDialog(visit)

  def save_triage(self,triage:dict,mini:bool=False):
    """register data to database"""

    status = update_triage(triage)
  
    #Notify
    ui.notify(message=status["message"],type=status["type"],position=status["position"])
    
    #Page refresh
    self.initial_data()
    self.TriageStats()
    if mini:
      self.TriagesMiniDisplay()
    else:
      self.TriagesDisplay()

  
  def client_mini(self,visit):
    """Returns a string of html elements for display in small screens"""

    def GenderIcon(visit):
      """Returns a styled gender icon based on client's gender"""

      genders = {"male":"mars","female":"venus"}
      colors = {"male":"sky-600","female":"pink-600"}

      return f"<span class='fa-solid fa-{genders[visit['client_gender'].lower()]} text-{colors[visit['client_gender'].lower()]}'></span>"
    
    age = f"<span class='ml-1'>{format_age(visit['client_birthdate']).split(' ')[0]} {format_age(visit['client_birthdate']).split(' ')[1][0].upper()}</span>"
    gender = GenderIcon(visit)
    payment_mode = f"<span class=''>{visit['payment_mode'].upper()}</span>"

    return f"<span class='h-full'>{gender}{age}</span>"


  #UI
  def TriageStats(self):
    """"""
    self.stats_panel.clear()
    with self.stats_panel:
      with html.span().classes(add="flex flex-row"):
        #Visits
        with ui.label("VISITS").classes(add="rounded-full p-2 text-sky-500"):
          ui.label(str(len(self.triage_visits))).classes(add="ml-1 inline text-bold text-white")
        #Done
        with ui.chip(icon="fa-regular fa-circle-check",text_color="green",color="").classes(add=f"{'' if self.done_triages else 'hidden'} p-2 bg-inherit").tooltip("Completed Triages"):
          ui.label(str(len(self.done_triages))).classes(add="inline text-bold text-white")
        #Pending
        with ui.chip(icon="fas fa-spinner",text_color="yellow",color="").classes(add=f"{'' if self.incomplete_triages else 'hidden'} p-2 bg-inherit").tooltip("Incomplete Triages"):
          ui.label(str(len(self.incomplete_triages))).classes(add="inline text-bold text-white")
        #Not Done
        with ui.chip(icon="fa-regular fa-circle-xmark",text_color="red",color="").classes(add=f"{'' if self.not_done_triages else 'hidden'} p-2 bg-inherit"):
          ui.label(str(len(self.not_done_triages))).classes(add="inline text-bold text-white")

  def TriagesDisplay(self):
    """"""
    #UI
    self.display_panel.clear()
    with self.display_panel:
      self.visit_aggrid = ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/N","field":"sno","width":50},
            {"headerName":"CLIENT ID","field":"client_id","filter":"agTextColumnFilter","floatingFilter":True,"width":100},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","floatingFilter":True},
            {"headerName":"AGE","field":"age","width":80},
            {"headerName":"GENDER","field":"gender","width":80},
            {"headerName":"VISIT TIME","field":"duration","width":120},
            {"headerName":"STATUS","field":"status","width":100,"cellClassRules":{
              "text-green-600 text-bold":"x == 'Done'",
              "text-red-600 text-bold":"x == 'Not Done'",
              "text-yellow-500 text-bold":"x == 'Incomplete'"
              }
            }
          ] ,
          "rowData":[
            {
              "sno":self.triage_visits.index(visit) + 1,
              "client_id":visit["client_id"],
              "visit_id":visit["visit_id"].upper(),
              "name":visit["client_name"].title(),
              "age":f"{format_age(visit['client_birthdate']).split(' ')[0]} {format_age(visit['client_birthdate']).split(' ')[1]}",
              "gender":visit["client_gender"].capitalize(),
              "duration":f"{format_age(visit['start_time'])}",
              "payment":visit["payment_mode"].upper(),
              "status":self.triage_status(visit).title()
            } for visit in self.triage_visits
          ]
        },theme="quartz"
        ).classes(add="w-full h-full animate__animated animate__fadeIn").on("cellClicked",lambda e:self.TriagesDialog(visit=[visit for visit in self.triage_visits if visit['visit_id'] == e.args["data"]["visit_id"].lower()][0]))
  
  def TriagesMiniDisplay(self):
    """Displays the details of clients for small screens"""
    #MODS
    def StatusDot(visit):
      """A function to return a styled icon based on status of client's last visit"""

      status = self.triage_status(visit)
      return f"<span class='fa-solid fa-circle { 'text-green-600' if status == 'done' else 'text-red-600' if status == 'not done' else 'text-yellow-500'}'></span>"
    
    def GenderIcon(visit):
      """Returns a styled gender icon based on client's gender"""

      genders = {"male":"mars","female":"venus"}
      colors = {"male":"sky-600","female":"pink-600"}
      return f"<span class='fa-solid fa-{genders[visit['client_gender'].lower()]} text-{colors[visit['client_gender'].lower()]}'></span>"

    #UI
    self.display_panel.clear()
    with self.display_panel:
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"","field":"status","width":75},
            {"headerName":"CLIENT ID","field":"client_id","filter":"agTextColumnFilter","floatingFilter":True,"width":160},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","floatingFilter":True,"width":300},
            {"headerName":"","field":"details","align":"left","width":150},
          ],
          "rowData":[
            {
              "status":StatusDot(visit),
              "client_id":visit["client_id"],
              "name":f"{visit['client_name'].split(' ')[0]} {visit['client_name'].split(' ')[1][0]}. {visit['client_name'].split(' ')[2]}".title(),
              "details":self.client_mini(visit),
            } for visit in self.triage_visits
          ],
        },
        html_columns=[0,3],
        theme="quartz"
      ).classes(add="w-full h-full animate__animated animate__fadeIn animate__slow").on("cellClicked",lambda e:self.TriagesDialog(visit=[visit for visit in self.triage_visits if visit['client_id'] == e.args["data"]["client_id"]][0],mini=True))

  def NewTriagePanel(self,visit:dict,repeat:bool=False,mini:bool=False):
    """"""
    #DATA
    anthropometrics_1,vitals_1 = visit["anthropometrics"][0],visit["vital_signs"][0]
    
    if repeat:
      vitals = {
        "visit_id":visit["visit_id"],
        "vitals_id":f"{visit['visit_id']}vs{len(visit['vital_signs']) + 1}",
        "attendee_id":self.user.username,
        "temp":None,"sbp":None,"dbp":None,"pr":None,"rr":None,"osat":None,
        "payment":{
          "visit_id":visit["visit_id"],
          "vitals_id":f"{visit['visit_id']}vs{len(visit['vital_signs']) + 1}",
          "payment_id":f"{visit['visit_id']}vs{len(visit['vital_signs']) + 1}pay{len(visit['payments']) + 1}",
          "cost":0,
          "payment_mode":visit["payment_mode"],
          "authorization_no":visit["consultations"][0]["payment"]["authorization_no"] if visit["consultations"] else None,
          "billed":True,
          "paid":True
        }
      }
      anthrops = {
        "visit_id":visit["visit_id"],
        "anthropometrics_id":f"{visit['visit_id']}anp{len(visit['anthropometrics']) + 1}",
        "attendee_id":self.user.username,
        "weight":None,
        "height":None,
        "muac":None,
        "hc":None,
        "payment":{
          "visit_id":visit["visit_id"],
          "anthropometrics_id":f"{visit['visit_id']}anp{len(visit['anthropometrics']) + 1}",
          "payment_id":f"{visit['visit_id']}anp{len(visit['anthropometrics']) + 1}pay{len(visit['payments']) + 1}",
          "cost":0,
          "payment_mode":visit["payment_mode"],
          "authorization_no":visit["consultations"][0]["payment"]["authorization_no"] if visit["consultations"] else None,
          "billed":True,
          "paid":True
        }
      }
      
      triage_data = {"vitals":vitals,"anthropometrics":anthrops}
      register_triage(triage_data)

    else:
      if self.payment_status(visit) == "paid" or self.payment_status(visit) == "billed":
        vitals = {"attendee_id":self.user.username,"vitals_id":vitals_1["vitals_id"],"temp":None,"sbp":None,"dbp":None,"pr":None,"rr":None,"osat":None}
        anthrops = {"attendee_id":self.user.username,"anthropometrics_id":anthropometrics_1["anthropometrics_id"],"weight":None,"height":None,"muac":None,"hc":None}
        triage_data = {"vitals":vitals,"anthropometrics":anthrops}
      elif self.payment_status(visit) == "partial":
        triage_data = {}
        if vitals_1["payment"]["paid"] or vitals_1["payment"]["billed"]:
          vitals = {"attendee_id":self.user.username,"vitals_id":vitals_1["vitals_id"],"temp":None,"sbp":None,"dbp":None,"pr":None,"rr":None,"osat":None}
          triage_data["vitals"] = vitals
        if anthropometrics_1["payment"]["paid"] or anthropometrics_1["payment"]["billed"]:
          anthrops = {"attendee_id":self.user.username,"anthropometrics_id":anthropometrics_1["anthropometrics_id"],"temp":None,"sbp":None,"dbp":None,"pr":None,"rr":None,"osat":None}
          triage_data["anthropometrics"] = anthrops
      else:
        ui.notify(message="Unpaid Service!",type="warning",position="center")
        return
  
    #UI
    self.triages_dialog_panel.clear()
    with self.triages_dialog_panel:
      with html.div().classes(add="grow w-full p-0.5 rounded-b ring-1 ring-blue-400 shadow-md shadow-blue-400 flex flex-col animate__animated animate__fadeIn animate__slow"):
        #TRIAGE
        with html.form().classes(add="grow w-full flex flex-row"):
          #Vital signs
          if "vitals" in triage_data:
            with html.div().classes(add="w-full"):
              ui.label("VITAL SIGNS").classes(add="w-full bg-harmony text-sky-300 text-bold text-center text-3xl")
              with html.div().classes(add="w-full p-3 flex flex-row justify-around gap-5"):
                if get_duration(visit["client_birthdate"])["years"] >= 12:
                  self.sbp_input = ui.number(label="SBP (mmHg)",min=0,max=370).bind_value(vitals,"sbp").classes(add="w-32 bg-white rounded shadow-md shadow-sky-600 px-5 text-lg")
                  self.dbp_input = ui.number(label="DBP (mmHg)",min=0,max=360).bind_value(vitals,"dbp").classes(add="w-32 bg-white rounded shadow-md shadow-sky-600 px-5 text-lg")
                self.pr_input = ui.number(label="PR (bpm)",min=0,max=500).bind_value(vitals,"pr").classes(add="w-32 bg-white rounded shadow-md shadow-sky-600 px-5 text-lg")
                self.temp_input = ui.number(label="TEMP (℃)",min=11.8,max=46.3).props(add="required").bind_value(vitals,"temp").classes(add="w-32 bg-white rounded shadow-md shadow-sky-600 px-5 text-lg")
                self.rr_input = ui.number(label="RR (cpm)",min=0,max=200).bind_value(vitals,"rr").classes(add="w-32 bg-white rounded shadow-md shadow-sky-600 px-5 text-base")
                self.o2sat_input = ui.number(label="O₂ SAT (%)",min=0,max=100).bind_value(vitals,"osat").classes(add="w-32 bg-white rounded shadow-md shadow-sky-600 px-5 text-base")
          
          #Anthropometrics
          if "anthropometrics" in triage_data:
            with html.div().classes(add="w-full"):
              ui.label("ANTHROPOMETRICS").classes(add="w-full bg-harmony text-sky-300 text-bold text-center text-3xl")
              with html.div().classes(add="w-full p-2 flex flex-row justify-around lg:justify-center gap-5"):
                self.weight_input = ui.number(label="WEIGHT (kg)",min=0,max=370).bind_value(anthrops,"weight").classes(add="w-32 bg-white rounded shadow-md shadow-sky-600 px-5 text-lg")
                self.height_input = ui.number(label=f"{'LENGTH' if get_duration(visit['client_birthdate'])['years'] < 2 else 'HEIGHT'} (cm)",min=0,max=360).bind_value(anthrops,"height").classes(add="w-32 bg-white rounded shadow-md shadow-sky-600 px-5 text-lg")
                if get_duration(visit["client_birthdate"])["years"] < 2:
                  self.hc_input = ui.number(label="HC (cm)").bind_value(anthrops,"hc").classes(add="w-32 bg-white rounded shadow-md shadow-harmony px-5 text-lg")
                  self.muac_input = ui.number(label="MUAC (cm))").bind_value(anthrops,"muac").classes(add="w-36 bg-white rounded shadow-md shadow-harmony px-5 text-lg")
        
        #BUTTONS
        with html.div().classes(add="w-full p-1 flex flex-row justify-center"):
          ui.button(text="SAVE",icon="fa-regular fa-floppy-disk fa-sm",color="",on_click=lambda e:self.save_triage(triage=triage_data,mini=mini)).props(add="").classes(add="ring-1 ring-sky-500 bg-harmony shadow-md shadow-harmony text-sky-300 text-xl text-bold")

  def TriagesDialog(self,visit:dict,mini:bool=False):
    """A method to display dialog for triage details pulled from database"""

    #DATA
    details = {
      "name":visit["client_name"],
      "short_name":f"{visit["client_name"].split(" ")[0]} {visit["client_name"].split(" ")[1][0]}. {visit["client_name"].split(" ")[2]}".title(),
      "age":format_age(visit["client_birthdate"]),
      "gender":visit["client_gender"],
      "address":visit["client_address"],
      "last_visit":format_age(visit["start_time"])
    }
    
    vitals = [vital for vital in visit["vital_signs"] if vital["done"]]
    anthrop = visit["anthropometrics"][0]
    #FXS
    def close_dialog():
      self.initial_data()
      self.TriageStats()
      self.TriagesDisplay()
      self.triages_dialog.close()

    #UI
    with ui.dialog().props(add="transition-show='scale' transition-hide='scale' transition-duration='500'") as self.triages_dialog,html.div().style(add="min-width:90%;min-height:60%;").classes(add="bg-sky-100 flex flex-col"):
      #HEADER
      with html.div().classes(add="w-full rounded-t p-1 flex flex-row bg-harmony"):
        with html.div().classes(add="grow"):
          ClientCard(details=details)
        ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=close_dialog).classes(add="bg-inherit text-red-600 text-bold text-base")
      
      #TRIAGES
      with html.div().classes(add="grow w-full flex flex-col justify-between animate___animated animate__fadeIn animate__slow") as self.triages_dialog_panel:
        if len(visit["vital_signs"]) > 1:
          self.TriagesAggrid(visit=visit,mini=mini)
        else:
          if visit["vital_signs"][0]["done"]:
            self.TriagesAggrid(visit=visit,mini=mini)
          else:
            self.NewTriagePanel(visit=visit,mini=mini)

    self.triages_dialog.open()

  def TriagesAggrid(self,visit,mini:bool=False):
    #DATA
    vitals = sorted([vital for vital in visit["vital_signs"] if vital["done"]],key=lambda e:e["vitals_time"],reverse=True)
    if visit["anthropometrics"]:
      _anthrops = [_anthrop for _anthrop in visit["anthropometrics"] if _anthrop["weight"]]
      if _anthrops:
        anthrop = _anthrops[-1]
      else:
        anthrop = {"weight":None,"height":None,"muac":None,"head_circum":None}
    else:
      anthrop = {"weight":None,"height":None,"muac":None,"head_circum":None}

    #UI
    self.triages_dialog_panel.clear()
    with self.triages_dialog_panel.classes(add=""):
      #Separator
      for i in range(2):
        ui.separator().classes(add="w-full bg-[#09026f]")
      #Anthropometrics
      with html.section().classes(add="bg-harmony w-full p-2 flex flex-row gap-5 text-bold text-lg"):
        #Weight
        with ui.label(""):
          ui.label("").classes(add="fa-solid fa-weight-scale text-yellow-500")
          ui.label(f"{str(anthrop['weight'])+'kg' if anthrop['weight'] else '---'}").classes(add="inline ml-0.5 text-sky-300")
        #Height/Length
        with ui.label(""):
          ui.label("").classes(add="fa-solid fa-ruler-vertical text-yellow-500").tooltip(f"")
          ui.label(f"{str(anthrop['height'])+'cm' if anthrop['height'] else '---'}").classes(add="inline ml-0.5 text-sky-300")
        #MUAC
        with ui.label("").classes(add=f"{'' if anthrop['muac'] else 'hidden'}"):
          ui.label("").classes(add="fa-solid fa-child text-yellow-500")
          ui.label(f"{anthrop['muac']} cm").classes(add="inline ml-0.5 text-sky-300")
        #Head Circumference
        with ui.label("").classes(add=f"{'' if anthrop['head_circum'] else 'hidden'}"):
          ui.label("").classes(add="fa-solid fa-child text-yellow-500")
          ui.label(f"{anthrop['head_circum']} cm").classes(add="inline ml-0.5 text-sky-300")
        
      #Vitals
      with html.section().classes(add="grow flex flex-col"):
        #Large screen
        ui.table(
          columns=[
            {"name":"date","label":"DATE","field":"date","align":"left"},
            {"name":"time","label":"TIME","field":"time","align":"left"},
            {"name":"temp","label":"TEMPERATURE (℃)","field":"temp","align":"left"},
            {"name":"sbp","label":"SYSTOLIC BP (mmHg)","field":"sbp","align":"left"},
            {"name":"dbp","label":"DIASTOLIC BP (mmHg)","field":"dbp","align":"left"},
            {"name":"pr","label":"PULSE RATE (bpm)","field":"pr","align":"left"},
            {"name":"rr","label":"RESPIRATORY RATE (cpm)","field":"rr","align":"left"},
            {"name":"osat","label":"O₂ SATURATION (%)","field":"osat","align":"left"}
          ],
          rows=[
            {
              "date":str(int(vital["vitals_time"].strftime("%d")))+ vital["vitals_time"].strftime(" %b %Y"),
              "time":vital["vitals_time"].strftime("%H:%M"),
              "temp":vital["temperature"],
              "sbp":vital["sbp"],
              "dbp":vital["dbp"],
              "pr":vital["pulse_rate"],
              "rr":vital["resp_rate"],
              "osat":vital["o2sat"]
            } for vital in vitals
          ],title="VITAL SIGNS CHART",pagination={"rowsPerPage":5}
        ).classes(add="lg-show w-full grow bg-sky-50")

        #Small screen
        with ui.scroll_area().classes(add="grow lg:hidden"):
          for vital in vitals:
            with html.div().classes(add="rounded shadow-sm shadow-sky-700"):
              with html.div().classes(add="p-1 flex flex-row gap-5 bg-harmony rounded-t text-sky-200 font-semibold"):
                ui.label(f"{vital["vitals_time"].strftime('%d %b %Y')}").classes(add="")
                ui.label(vital["vitals_time"].strftime("%H:%M"))

              with html.div().classes(add="flex flex-row gap-0"):
                #Temp
                ui.chip(text=f"{vital['temperature']}°C" if vital["temperature"] else "---",icon="fa-solid fa-temperature-quarter fa-sm",color="",text_color="sky-900").props(add="").classes(add="bg-inherit px-1 shadow-sm shadow-sky-700 rounded font-semibold")
                #PR/HR
                ui.chip(text=f"{vital['pulse_rate']} bpm" if vital["pulse_rate"] else "---",icon="fa-solid fa-heart-pulse fa-sm",color="",text_color="sky-900").props(add="").classes(add="bg-inherit px-2 shadow-sm shadow-sky-700 rounded font-semibold")
                #RR
                ui.chip(text=f"{vital['resp_rate']} cpm" if vital["resp_rate"] else "---",icon="fa-solid fa-lungs fa-sm",color="",text_color="sky-900").props(add="").classes(add="bg-inherit px-2 shadow-sm shadow-sky-700 rounded font-semibold")
                #SPO2
                with ui.chip(text="O₂ :",color="",text_color="sky-900").props(add="").classes(add="bg-inherit px-2 shadow-sm shadow-sky-700 rounded font-semibold text-md"):
                  ui.label(f"{vital['o2sat']} %" if vital["o2sat"] else "---").classes(add="inline ml-0.5")
                #BP
                with ui.chip(icon="fa-solid fa-stethoscope fa-sm",color="",text_color="sky-900").classes(add="bg-inherit px-2 rounded shadow-sm shadow-sky-700 font-semibold"):
                  ui.label(f"{vital['sbp']}" if vital["sbp"] else "---")
                  ui.label("/").classes(add="inline m-0 p-0")
                  ui.label(f"{vital['dbp']}" if vital["dbp"] else "---").classes(add="inline m-0 p-0")
                  html.span("mmHg").classes(add="bg-inherit ml-0.5")

      #Button
      with html.section().classes(add="w-full p-1 flex flex-row justify-center"):
        ui.button(text="TRIAGE",icon="fa-solid fa-circle-plus fa-sm",color="",on_click=lambda e:self.NewTriagePanel(visit=visit,repeat=True,mini=mini)).classes(add="rounded bg-harmony text-sky-300 text-xl text-bold")

class DispensingManagementDisplay():
  """A class to display UI for managing studies"""

  def __init__(self,user):
    #DATA
    self.user = user
    self.initial_data()
    
    #UI
    with html.div().classes(add=f"w-full h-full flex flex-col {'' if self.visits else 'justify-center content-center bg-white rounded-b'}"):
      if self.visits:
        #Header
        ui.separator().classes(add="w-full bg-[#09026f]")
        with html.div().classes(add="w-full rounded-t px-2 py-1 bg-harmony flex flex-row"):
          ui.label("TODAY VISITS").classes(add="").classes(add="bg-inherit grow text-2xl lg:text-3xl text-yellow-500 text-bold")
          with html.div().classes(add="bg-inherit") as self.stats_panel:
            self.DispensingStats()
        #Displays
        with html.div().classes(add="w-full grow bg-white rounded-b flex flex-col") as self.display_panel:
          self.PharmacyVisitsDisplay()
      
      else:
        with html.div().classes(add="bg-inherit flex flex-col gap-2 p-3 rounded text-bold fa-fade"):
          ui.label("No clients for now").classes(add="text-xl lg:text-3xl text-center text-rose-500")
          ui.label("Just relax and have fun!").classes(add="italic text-center text-lg lg:text-2xl text-pink-400")

  #FUNCTIONALITIES
  def initial_data(self):
    self.pharmacy_visits = [visit for visit in get_pharmacy_visits() if visit["is_active"]]
    self.dispensed_visits = [visit for visit in self.pharmacy_visits if self.dispense_status(visit) == "dispensed"]
    self.not_dispensed_visits = [visit for visit in self.pharmacy_visits if self.dispense_status(visit) == "not dispensed"]
    self.incomplete_visits = [visit for visit in self.pharmacy_visits if self.dispense_status(visit) == "incomplete"]
    self.visits = self.not_dispensed_visits + self.incomplete_visits + self.dispensed_visits
  
  def dispense_status(self,visit:dict):
    """Returns a string representing payment status of imagings"""

    statuses = set()

    medicines = visit["medications"] + visit["medical_items"]
    
    for medicine in medicines:
      if medicine["dispensed"]:
        statuses.add("dispensed")
      else:
        statuses.add("not dispensed")
    
    if len(statuses) == 1:
      return statuses.pop()
    else:
      return "incomplete"
  
  def formatted_medicines(self,visit:dict=None):
    #Integrate with requisition database
    requisition_medicines = get_requisitions()[0]["medicines"]
    visit_medicines = visit["medications"] + visit["medical_items"]
    for requisition_medicine in requisition_medicines:
      for medicine in visit_medicines:
        if medicine["name"] == requisition_medicine["name"]:
          medicine["medicine_id"] = requisition_medicine["medicine_id"]
          medicine["dispensing_balance"] = requisition_medicine["dispensing_balance"]
          medicine["requisition_medicine_id"] = requisition_medicine["requisition_medicine_id"]
    #Format for UI view
    dispensed_medicines = sorted([medicine for medicine in visit_medicines if medicine["dispensed"]],key=lambda e:e["dispensing_time"],reverse=True)
    pending_medicines = sorted([medicine for medicine in visit_medicines if not (medicine["dispensed"] or medicine["cancelled"])],key=lambda e:e["prescribed_on"],reverse=True)
    cancelled_medicines = sorted([medicine for medicine in visit_medicines if medicine["cancelled"]],key=lambda e:e["prescribed_on"],reverse=True)
    medicines = pending_medicines + dispensed_medicines + cancelled_medicines
    
    return medicines

  def _medicines(self,visit):
    """Returns a string representing payment status of imagings"""

    medicines = visit["medications"] + visit["medical_items"]
    _dispensed = [medicine for medicine in medicines if medicine["dispensed"]]
    _pending = [medicine for medicine in medicines if (medicine["payment"]["paid"] or medicine["payment"]["billed"]) and not (medicine["dispensed"] or medicine["cancelled"])]
    _not_dispensed = [medicine for medicine in medicines if not (medicine["payment"]["paid"] or medicine["payment"]["billed"]) and not (medicine["dispensed"] or medicine["cancelled"])]
    _cancelled = [medicine for medicine in medicines if medicine["cancelled"]]

    return f"<span><span class='{'' if _dispensed else 'hidden'} mr-2'><i class='fas fa-check text-green-500'></i><i class='ml-0.5 '>{len(_dispensed)}</i></span><span class='{'' if _pending else 'hidden'} mr-2'><i class='fas fa-spinner text-yellow-500 fa-spin'></i><i class='ml-0.5 '>{len(_pending)}</i></span><span class='{'' if _not_dispensed else 'hidden'} mr-2'><i class='fas fa-xmark text-red-500'></i><i class='ml-0.5'>{len(_not_dispensed)}</i></span><span class='{'' if _cancelled else 'hidden'} mr-2'><i class='fas fa-ban text-gray-500'></i><i class='ml-0.5 '>{len(_cancelled)}</i></span></span>"
    
  def dispense_medicine(self,medicine:dict,count:int):
    """Saves the findings in the database"""
    
    medicine = {
      "visit_id":medicine["visit_id"],
      "medicine_id":medicine["medicine_id"],
      "requisition_medicine_id":medicine["requisition_medicine_id"],
      "medication_id":medicine["medication_id"] if "medication_id" in medicine else None,
      "medical_item_id":medicine["medical_item_id"] if "medical_item_id" in medicine else None,
      "dispensed_items_no":count,
      "dispenser_id":self.user.username
    }
    
    #Update database
    status = update_client_medicine(medicine)
    register_inventory(
      inventory={
        "medicine_id":medicine["medicine_id"],
        "invoice":None,
        "logger":self.user.username,
        "issuer":"dispensing store",
        "receiver":medicine["visit_id"].split("v")[0],
        "amount":count
      },dispensed=True
    )
    
    #Failure notification
    ui.notify(message=status["message"],type=status["type"],position=status["position"])

    #UI Update
    self.initial_data()
    self.DispensingStats()
    self.MedicinesPanel(visit=[visit for visit in self.visits if visit["visit_id"] == medicine["visit_id"]][0])
  
  def client_mini(self,visit):
    """Returns a string of html elements for display in small screens"""

    def GenderIcon(visit):
      """Returns a styled gender icon based on client's gender"""

      genders = {"male":"mars","female":"venus"}
      colors = {"male":"sky-600","female":"pink-600"}

      return f"<span class='fa-solid fa-{genders[visit['client_gender'].lower()]} text-{colors[visit['client_gender'].lower()]}'></span>"
    
    age = f"<span class='ml-1'>{format_age(visit['client_birthdate']).split(' ')[0]} {format_age(visit['client_birthdate']).split(' ')[1][0].upper()}</span>"
    gender = GenderIcon(visit)
    payment_mode = f"<span class=''>{visit['payment_mode'].upper()}</span>"

    return f"<span class='h-full'>{gender}{age}</span>"

  def medicines_mini(self,visit):
    """Returns a string of html elements for display of services in small screens"""
    medicines = visit["medications"] + visit["medical_items"]
    _dispensed = len([medicine for medicine in medicines if medicine["dispensed"]])
    _cancelled = len([medicine for medicine in medicines if medicine["cancelled"]])
    _pending = len([medicine for medicine in medicines if not (medicine["cancelled"] or medicine["dispensed"])])

    dispensed = pending = cancelled = ""

    if _dispensed:
      dispensed = f"<span class='text-green-600'><span class='fas fa-check-double'></span><sup class='ml-0.5 text-bold'>{_dispensed}</sup></span>"

    if _pending:
      pending = f"<span class='text-yellow-600'><span class='fa-solid fa-spinner fa-spin'></span><sup class='ml-0.5 text-bold'>{_pending}</sup></span>"

    if _cancelled:
      cancelled = f"<span class='text-gray-600'><span class='fa-solid fa-ban'></span><sup class='ml-0.5 text-bold'>{_cancelled}</sup></span>"
    
    #Returns
    if _dispensed + _pending + _cancelled:
      return f"<span class='flex flex-row justify-between items-center'>{dispensed}{pending}{cancelled}</span>"
    else:
      return "---"

  
  #DISPLAYS
  def DispensingStats(self):
    """"""
    self.stats_panel.clear()
    with self.stats_panel:
      with html.span().classes(add="flex flex-row"):
        #Visits
        with ui.label("VISITS").classes(add="rounded-full p-2 text-sky-500"):
          ui.label(str(len(self.visits))).classes(add="ml-1 inline text-bold text-white")
        #Done
        with ui.chip(icon="fa-regular fa-circle-check",text_color="green",color="").classes(add=f"{'' if self.dispensed_visits else 'hidden'} p-2 bg-inherit").tooltip("Completed Triages"):
          ui.label(str(len(self.dispensed_visits))).classes(add="inline text-bold text-white")
        #Pending
        with ui.chip(icon="fas fa-spinner",text_color="yellow",color="").classes(add=f"{'' if self.incomplete_visits+self.not_dispensed_visits else 'hidden'} p-2 bg-inherit").tooltip("Incomplete Triages"):
          ui.label(str(len(self.incomplete_visits + self.not_dispensed_visits))).classes(add="inline text-bold text-white")

  def PharmacyVisitsDisplay(self):
    """"""
    #UI
    self.display_panel.clear()
    with self.display_panel:
      #Large Screen
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/N","field":"sno","width":80},
            {"headerName":"CLIENT ID","field":"client_id","filter":"agTextColumnFilter","width":150},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":350},
            {"headerName":"AGE","field":"age"},
            {"headerName":"GENDER","field":"gender","width":100},
            {"headerName":"PRESCRIPTION MODE","field":"prescription_mode"},
            {"headerName":"PAYMENT","field":"payment_mode","width":100},
            {"headerName":"MEDICINES","field":"medicines"}
          ],
          "rowData":[
            {
              "sno":self.visits.index(visit) + 1,
              "client_id":visit["client_id"],
              "name":visit["client_name"].title(),
              "age":format_age(birthdate=visit["client_birthdate"]),
              "gender":visit["client_gender"].capitalize(),
              "prescription_mode":visit["prescription_mode"].capitalize(),
              "payment_mode":" ".join({mode.upper() for mode in [medicine["payment"]["payment_mode"] for medicine in visit["medications"] + visit["medical_items"]]}),
              "medicines":self._medicines(visit)
            }
          for visit in self.visits
          ]
        },
        theme="quartz",
        html_columns = [7]
      ).classes(add="lg-show grow w-full animate__animated animate__fadeIn animate__slow").on("cellClicked",lambda e:self.DispensingDialog(visit=[visit for visit in self.visits if visit["client_id"] == e.args["data"]["client_id"]][0]))

      #Small Screen
      #Small Screen
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"","field":"client_id","filter":"agTextColumnFilter","width":200},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","floatingFilter":True,"width":300},
            {"headerName":"","field":"specs"},
            {"headerName":"","field":"services"}
          ],
          "rowData":[
            {
              "client_id":visit["client_id"],
              "name":f"{visit['client_name'].split(' ')[0]} {visit['client_name'].split(' ')[1][0]}. {visit['client_name'].split(' ')[2]}".title(),
              "specs":self.client_mini(visit),
              "services":self.medicines_mini(visit)
            } for visit in self.visits
          ]
        },
        theme="quartz",
        html_columns=[2,3]
      ).props(add="").classes(add="lg:hidden grow w-full animate__animated animate__fadeIn").on("cellClicked",lambda e:self.DispensingDialog(visit=[visit for visit in self.visits if visit["client_id"] == e.args["data"]["client_id"]][0]))

  def DispensingDialog(self,visit:dict):

    #DATA
    details = {
      "name":visit["client_name"],
      "short_name":f"{visit['client_name'].split()[0]} {visit['client_name'].split()[1][0]} {visit['client_name'].split()[2]}".title(),
      "age":format_age(visit["client_birthdate"]),
      "gender":visit["client_gender"],
      "address":visit["client_address"]}
    
    #FXS
    def close_dialog():
      self.PharmacyVisitsDisplay()
      self.dispensing_dialog.close()

    #UI
    with ui.dialog().props(add="transition-show='scale' transition-hide='scale' transition-duration='500'") as self.dispensing_dialog,html.div().style(add="min-width:100%;min-height:50%;").classes(add="bg-sky-50 ring-1 ring-blue-400 shadow-md shadow-blue-400 overflow-y-hidden"):
      #Dialog Header
      with html.div().classes(add="w-full pr-2 flex flex-row justify-between items-center bg-harmony"):
        with html.div().classes(add="grow"):
          ClientCard(details=details)
        ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=close_dialog).classes(add="bg-inherit shadow-md text-red-500 text-bold")
      
      #Dialog Body
      with html.div().classes(add="w-full") as self.medicines_dialog_panel:
        self.MedicinesPanel(visit=visit)
      
    self.dispensing_dialog.open()

  def MedicinesPanel(self,visit:dict):
    """"""
    #DATA
    medicines = self.formatted_medicines(visit=visit)
    for medicine in medicines:
      medicine["type"] = 'tablet' if medicine['name'].lower().split()[-1].startswith("tab") else "capsule" if medicine['name'].lower().split()[-1].startswith('cap') else 'bottle' if (medicine['name'].lower().split()[-1].startswith('syrup') or medicine['name'].lower().split()[-1].startswith('susp')) else 'vial' if medicine['name'].lower().split()[-1].startswith('vial') else 'ampoule' if medicine['name'].lower().split()[-1].startswith('ampoule') else 'item'
    dispensed_medicines = [medicine for medicine in medicines if medicine["dispensed"]]
    dispensable_medicines = [medicine for medicine in medicines if not (medicine["dispensed"] or medicine["cancelled"])]
    ticked_medicines = []

    #FXS
    def pick_ticked_medicine(ticked_medicine:str,ticked_medicine_count:int,ticked:bool):
      """Returns a list of ticked medicines"""
      if ticked:
        for medicine in dispensable_medicines:
          if medicine["id"] == ticked_medicine:
            medicine["dispensed_items_no"] = ticked_medicine_count
            ticked_medicines.append(medicine)
      else:
        for medicine in ticked_medicines:
          if medicine["id"] == ticked_medicine:
            ticked_medicines.remove(medicine)

    def dispense_all(medicines:list):
      """Dispenses all medicines in the ticked_medicines list"""
      if medicines:
        for medicine in medicines:
          self.dispense_medicine(medicine=medicine,count=medicine["dispensed_items_no"])
      else:
        ui.notify(message="No medicine selected",type="warning",position="center")
      
    #UI
    self.medicines_dialog_panel.clear()
    with self.medicines_dialog_panel.classes(add="p-2"):
      with ui.scroll_area().classes(add="w-full h-[400px] pb-2 bg-white rounded shadow-md shadow-[307004d] animate__animated animate__fadeIn animate__slow"):
        for medicine in medicines:
          attendee = f"{staff(medicine['prescriber_id'])['first_name']} {staff(medicine['prescriber_id'])['last_name']}".title()
          dispenser = f"{self.user.last_name}"
          medicine["id"] = medicine["medication_id"] if "medication_id" in medicine else medicine["medical_item_id"]

          with html.div().classes(add="w-full p-1 rounded bg-sky-50 grid grid-cols-3 gap-1 content-center shadow-md shadow-[#07004d]"):
            #Medicine name
            with html.div().classes(add="col-span-3 lg:col-span-1 flex flex-row"):
              #Checkbox
              ui.checkbox(on_change=lambda e:pick_ticked_medicine(
                ticked_medicine=e.sender.parent_slot.parent.slots["default"].children[1].slots["default"].children[0].props["id"],
                ticked_medicine_count=e.sender.parent_slot.parent.parent_slot.parent.slots["default"].children[1].slots["default"].children[6].props["model-value"]["label"],
                ticked=e.value
              )).props(add=f"{'' if medicine['payment']['paid'] or medicine['payment']['billed'] else 'disable'}").classes(add=f"{'hidden' if medicine['dispensed'] or medicine['cancelled'] else ''} bg-white tiki")
              #Name
              with html.div().classes(add="grow flex flex-col justify-center"):
                html.div(f"{medicines.index(medicine) + 1}. {medicine['name'].upper()}").props(add=f"id={medicine['medication_id'] if 'medication_id' in medicine else 'medical_item_id'}").classes(add="w-full rounded-sm m-0 p-0 bg-inherit text-sky-700 text-lg text-bold")
                if "dosage" in medicine:
                  html.div(medicine["dosage"] if medicine["dosage"] else "---").classes(add="w-full bg-inherit text-base font-medium italic")
            
            #Details
            with html.div().classes(add=f"col-span-3 lg:col-span-2 grid {'grid-cols-12' if medicine['payment']['paid'] or medicine['payment']['billed'] else 'grid-cols-13'} gap-1 content-center"):
              #Timeframe
              ui.chip(text=f"{format_age(datetime.fromisoformat(medicine['prescribed_on'])) if isinstance(medicine['prescribed_on'],str) else format_age(medicine['prescribed_on']) } ago",icon="fa-regular fa-clock fa-lg",text_color="sky-900",color="").classes(add="col-span-4 lg:col-span-2 rounded-sm ml-5 px-0 bg-inherit text-base font-semibold")
              #Odered by
              ui.chip(text=attendee,icon="fa-solid fa-user-doctor fa-lg",text_color="sky-900",color="").classes(add="col-span-5 lg:col-span-2 rounded-sm mx-0 px-0 bg-inherit text-base text-bold")
              #Payment status
              ui.chip(text="Paid" if medicine["payment"]["paid"] else "Billed" if medicine["payment"]["billed"] else "Not Paid",icon=f"{'fa-regular fa-circle-check' if medicine['payment']['paid'] else 'fa-solid fa-file-invoice' if medicine['payment']['billed'] else 'fa-regular fa-circle-xmark'} fa-lg",text_color="green" if medicine["payment"]["paid"] else "purple" if medicine["payment"]["billed"] else "red",color="").classes(add=f"col-span-3 {'lg:col-span-1' if medicine['payment']['paid'] or medicine['payment']['billed'] else 'lg:col-span-2'} rounded-sm mx-0 px-0 bg-inherit text-base text-bold")
              #Dispensing status
              ui.chip(
                text="Cancelled" if medicine["cancelled"] else "Dispensed" if ((medicine["payment"]["paid"] or medicine["payment"]["billed"]) and medicine["dispensed"]) else "Pending" if ((medicine["payment"]["billed"] or medicine["payment"]["paid"]) and not medicine["dispensed"]) else "Not dispensed",
                icon=f"{'fas fa-ban' if medicine['cancelled'] else 'fa-regular fa-circle-check' if ((medicine['payment']['paid'] or medicine['payment']['billed']) and medicine['dispensed']) else 'fa-solid fa-spinner fa-spin' if ((medicine['payment']['billed'] or medicine['payment']['paid']) and not medicine['dispensed']) else 'fa-regular fa-circle-xmark fa-flip'} fa-lg",
                text_color="gray" if medicine["cancelled"] else "green" if ((medicine["payment"]["paid"] or medicine["payment"]["billed"]) and medicine["dispensed"]) else "orange" if ((medicine["payment"]["billed"] or medicine["payment"]["paid"]) and not medicine["dispensed"]) else "red",
                color=""
              ).classes(add=f"col-span-4 justify-self-center lg:col-span-2 lg:justify-self-start rounded-sm mx-0 p-0 bg-inherit text-base text-bold text-wrap")
              #Store status
              ui.chip(text=f"{medicine['dispensing_balance']:,.0f}",icon="fas fa-house-medical fa-lg",text_color="sky-600",color="").classes(add=f"{'hidden' if medicine['dispensed'] or medicine['cancelled'] else ''} col-span-2 mx-1 px-0 bg-inherit text-lg text-bold")
              #Prescribed no
              ui.chip(text=f"{medicine['dispensed_items_no'] if medicine['dispensed_items_no'] else medicine['prescribed_items_no']}",icon=f"fas fa-{'tablets' if medicine['type'] == 'tablet' else 'capsules' if medicine['type'] == 'capsule' else 'prescription-bottle' if medicine['type'] == 'bottle' else 'vial' if medicine['type'] == 'vial' or medicine['type'] == 'ampoule' else 'thermometer'} fa-lg",color="",text_color=f"{'green-600' if medicine['dispensed'] else 'sky-600'}").classes(add=f"{'hidden' if medicine['cancelled'] or not medicine["dispensed"] else ''} col-span-2 lg:col-span-1 mx-0 px-0 bg-inherit text-lg text-bold")
              #Dispensed no
              ui.select(options=[i for i in range(1,medicine["prescribed_items_no"]+1)],value=medicine["prescribed_items_no"],with_input=True).props(add=f"type='number' dense min=1 max={medicine['prescribed_items_no']} {'' if medicine['payment']['paid'] or medicine['payment']['billed'] else 'readonly'}").classes(add=f"{'hidden' if medicine['dispensed'] or medicine['cancelled'] else ''} col-span-2 lg:col-span-1 w-[100%] my-2 px-2 bg-white shadow-md shadow-[#07004d] rounded text-lg")
              #Medication_id holder
              html.small(medicine["id"]).classes("hidden") #Medication_id not for purpose of display
              #Dispense button
              ui.button(text="Dispense",color="",on_click=lambda e:self.dispense_medicine(
                medicine=[medicine for medicine in medicines if medicine["id"].lower() == e.sender.parent_slot.parent.slots["default"].children[7]._text.lower()][0],
                count=int(e.sender.parent_slot.parent.slots["default"].children[6].props["model-value"]["label"])
              )).classes(add=f"{'hidden' if medicine['dispensed'] or medicine['cancelled'] else ''} col-span-4 lg:col-span-2 px-2 bg-harmony text-yellow-500 text-lg text-bold")
              #Dispensing information
              if medicine["dispensed"]:
                #Dispenser
                ui.chip(text=dispenser,icon="fa-solid fa-hospital-user fa-lg",text_color="green-600",color="").classes(add="col-span-2 justify-self-end rounded mx-0 px-2 bg-inherit capitalize text-base text-bold")
                #Timeframe
                ui.chip(text=f"{format_age(datetime.fromisoformat(medicine['dispensing_time'])) if isinstance(medicine['dispensing_time'],str) else format_age(medicine['dispensing_time'])} ago",icon="fa-regular fa-clock",text_color="green-600",color="").classes(add="col-span-2 justify-self-end rounded-sm mx-0  bg-inherit text-base text-bold")
                
      #Buttons
      with html.div().classes(add="w-full p-3 flex flex-col lg:flex-row justify-center items-center gap-3"):
        ui.label(f"{len(medicines)} MEDICINE{'S' if len(medicines)>1 else ''}").classes(add="w-full text-center lg:text-start lg:w-auto lg:grow px-3 font-semibold text-gray-500 text-base italic self-end")
        with html.div().classes(add="grow flex flex-row justify-end gap-10"):
          #Dispense all button
          if dispensable_medicines:
            ui.button(text="DISPENSED TICKED MEDICINES",color="",on_click=lambda e:dispense_all(medicines=ticked_medicines)).classes(add="rounded bg-harmony shadow-md shadow-[#07004d] text-yellow-500 text-lg text-bold")
          #Prin Button
          if dispensed_medicines:
            ui.button(text="PRINT RECEIPT",icon="fas fa-receipt",color="",on_click=lambda e:self.print_receipt(medicines=medicines)).classes(add="hidden rounded bg-harmony shadow-md shadow-[#07004d] text-yellow-300 text-lg text-bold")

  def print_receipt(self,medicines):
    ui.notify(medicines)
    ###Under maintanace
    
class StoresManagementDisplay():
  """A class to display UI for managing pharmacy store"""

  def __init__(self,user):
    #DATA
    self.user = user
    self.initial_data()
    self.formulary_dialog = ui.dialog()

    #UI
    with html.div().classes(add="w-full h-full flex flex-col p-0 gap-1 bg-inherit animate__animated animate__fadeIn") as self.master_container:
      self.Carousel(main=True)

  #Functionalities
  def initial_data(self):
    self.formulary = get_formulary()
    self.requisitions = get_requisitions()
    self.received_requisitions = sorted([requisition for requisition in self.requisitions if requisition["received"]],key=lambda req:req["receive_date"],reverse=True)
    self.stock_valid_requisitions = [requisition for requisition in self.received_requisitions  if not requisition["closed"]]

  def requisition_amount(self,amc,mos):
    """A method returns projected requisition amount based on mos value"""

    if mos < 2:
      return math.ceil((2-mos)*amc)
    else:
      return 0
  
  def save_medicine(self,medicine:dict,new_values:dict):
    """A method to save medicine data related to requisition"""
   
    index = self.medicines.index(medicine)
    self.medicines.remove(medicine)
    medicine["requisition_amount"] = new_values["requested_amount"]
    medicine["unit_price"] = new_values["unit_cost"]
    medicine["total_price"] = new_values["requested_amount"] * new_values["unit_cost"]

    #DB STORAGE
    register_medicine(medicine)
    #UI UPDATE
    self.medicines.insert(index,medicine)

    self.requisition_display_pad.clear()
    with self.requisition_display_pad:
      self.RequisitionDisplay(requisition_id=medicine["requisition_id"],medicines=self.medicines)
    
    self.medicine_dialog.close()

  def update_requisition(self,requisition_id:str,initiate:bool|None=None,order:bool|None=None,receive:bool|None=None,cancel:bool|None=None,medicines:list|None=None):
    """Removes requisition from database table and its corresponding medicines and stationeries in their corresponding tables"""
    
    if cancel:
      status = update_requisition({"requisition_id":requisition_id,"cancelled":True,"cancelled_by":self.user.username})
    if initiate:
      status = update_requisition({"requisition_id":requisition_id,"initiated":True,"initiated_by":self.user.username,"medicines":medicines})
    if order:
      status = update_requisition({"requisition_id":requisition_id,"placed":True,"placed_by":self.user.username})
    if receive:
      unprocessed = len([i for i in medicines if not i['received'] and not i['rejected']])
      if unprocessed > 1:
        ui.notify(message=f"{unprocessed} {'item' if unprocessed == 1 else 'items'} not processed! Review your requisition",type="warning",position="center")
        return
      else:
        status = update_requisition({"requisition_id":requisition_id,"received":True,"received_by":self.user.username})
      


    #NOTIFY
    ui.notify(message=status["message"],type=status["type"],position="top")
    
    ui.navigate.reload()
    self.requisition_dialog.close()

  def update_medicine(self,medicine:dict,new_values:dict,order:bool|None=None,receive:bool|None=None,label:str|None=None):
    """A method to update medicine"""
    #Order
    if order:
      index = self.medicines.index(medicine)
      self.medicines.remove(medicine)
      medicine["order"] = True
      medicine["requisition_amount"] = new_values["requested_amount"]
      medicine["unit_price"] = new_values["unit_cost"]
      medicine["total_price"] = new_values["requested_amount"] * new_values["unit_cost"]

    #Receive
    if receive:
      index = self.medicines.index(medicine)
      self.medicines.remove(medicine)
      medicine["receive"] = True
      medicine["brand_name"] = new_values["brand_name"]
      medicine["manufacturer"] = new_values["manufacturer"]
      medicine["batch_no"] = new_values["batch_no"]
      medicine["mfg_date"] = new_values["mfg_date"]
      medicine["expire_date"] = new_values["expire_date"]
      medicine["received_amount"] = new_values["received_amount"]
      medicine["received_price"] = new_values["received_price"]
      medicine["received_by"] = self.user.username
      medicine["rejected_amount"] = new_values["rejected_amount"]
      medicine["rejected_price"] = new_values["rejected_price"]
      medicine["store_balance"] = medicine["physical_count"] + new_values["received_amount"]
    
    #Update dispensing store
    if label == "dispensing":
      if new_values["dispensing_order_qty"] > medicine["store_balance"]:
        ui.notify(message="Insufficient stock in the store! Adjust the ordered amount",type="warning",position="center")
        return
      else:
        index = self.stock_items.index(medicine)
        self.stock_items.remove(medicine)
        medicine["dispensing"] = True
        medicine["dispensing_balance"] = new_values["dispensing_order_qty"]
        medicine["store_balance"] -= new_values["dispensing_order_qty"]
        
        update_medicine(medicine)
        self.medicine_dialog.close()
        return

    #Updating physical count
    if label == "count":
      index = self.stock_items.index(medicine)
      self.stock_items.remove(medicine)
      medicine["physical_countable"] = True
      medicine["physical_count"] = new_values["physical_count"]
      medicine["store_balance"] -= new_values["physical_count"]

      update_medicine(medicine)
      self.medicine_dialog.close()
      return

    #DB STORAGE
    update_medicine(medicine)

    #UI UPDATE
    self.medicines.insert(index,medicine)

    self.requisition_display_pad.clear()
    with self.requisition_display_pad:
      self.RequisitionDisplay(requisition_id=medicine["requisition_id"],medicines=self.medicines,initiate=None,order=order,receive=receive)
    
    self.medicine_dialog.close()

  
  #DISPLAYS
  def Carousel(self,main:str|None=None):
    #DATA
    value = "main store" if main else "dispensing store"
    #UI
    self.master_container.clear()
    with self.master_container.classes(remove=""):
      with ui.carousel(value=value).style(add="overflow-y:hidden;").props(add="animated swipeable transition-prev='jump-right' transition-next='jump-left' transition-duration='100'").classes(add="grow flex flex-col q-pa-none w-full bg-inherit rounded shadow-md shadow-blue-500 animate__animated animate__fadeIn") as carousel:
        with carousel.add_slot("default"):
          #Main Store
          with ui.carousel_slide(name="main store").classes(add="bg-sky-100 q-pa-none gap-0 w-full h-full rounded-b flex flex-col lg:grid grid-cols-7 gap-1 lg:gap-0"):
            #Stock Analysis
            with html.div().classes(add=" bg-harmony col-span-2 lg:order-2 w-full lg:h-full flex flex-col"):
              if self.received_requisitions:
                #StockAnalysisDisplay(requisitions=self.stock_valid_requisitions)
                pass
              else:
                #StockAnalysisDisplay()
                pass

                        #Formulary
            
            #Requisitions
            with html.div().classes(add="col-span-3 lg:order-3 grow w-full flex flex-col"):
              Requisitions(user=self.user,formulary=self.formulary,requisitions=self.requisitions)
            
            #Formulary
            with html.div().classes(add="col-span-2 lg:order-1 px-1.5 lg:px-0 w-full lg:h-full flex flex-col gap-1"):
              #Small Screen
              ui.separator().classes(add="lg:hidden pt-0.5 w-full bg-[#09026f]")
              ui.button(text="view formulary",color="",on_click=self.FacilityFormularyDialog).props(add="glossy").classes(add="lg:hidden w-full my-1 rounded bg-harmony text-xl text-yellow-500 font-medium")
              ui.separator().classes(add="lg:hidden pt-0.5 w-full bg-[#09026f]")

              #Large Screen
              with html.div().classes(add="lg-flex grow flex-col"):
                FacilityFormulary(formulary=self.formulary,parent=self)

          #Dispensing Store
          #with ui.carousel_slide(name="dispensing store").classes(add="q-pa-none gap-0 w-full h-full rounded-b"):
          #ui.label('Disp Room')
        
      #Controls
      #with html.div().classes(add="w-full py-1 flex flex-row justify-center gap-5 lg:gap-7"):
      #ui.toggle(options=["main store"]).props(add="glossy size='lg' toggle-color='bg-inherit' toggle-text-color='sky-500' text-color='yellow-500'").classes(add="lg-show bg-[#07004d] rounded-full ring-1 ring-blue-500 shadow-md shadow-sky-600 text-bold").bind_value(carousel)
  

  def StoreManagementPanels(self):
    #UI
    with html.div().props(add="elevated").classes(add="w-full h-full grid grid-cols-1 grid-rows-10 lg:grid-cols-3 gap-2"):
      #Requisitions
      with html.div().classes(add="w-full row-span-10 row-start-1 col-start-1 col-span-1 grid grid-rows-8 rounded light-blur ring-1 ring-blue-400 shadow-lg shadow-blue-600"):
        Requisitions(user=self.user,formulary=self.formulary,requisitions=self.requisitions)
      #Universal Search
      ui.select(options=['bia','bingwa','niga'],with_input=True,on_change=lambda e:ui.notify(e.value)).props(add="").classes(add="hidden col-start-2 col-span-1 row-start-1 row-span-1 pl-3 bg-white rounded ring-2 ring-sky-500 shadow-md shadow-blue-500 text-xl")
      #Stock Analysis
      with html.div().classes(add="w-full row-span-10 row-start-1 grid grid-rows-8 rounded-md light-blur ring-1 ring-blue-500 shadow-lg shadow-blue-600"):
        StockAnalysisDisplay(requisition=self.requisitions[0])
      #Dispensing Store
      with html.div().classes(add="w-full row-span-10 row-start-1 col-start-3 col-span-1 grid grid-rows-8 rounded light-blur ring-1 ring-blue-400 shadow-lg shadow-blue-500"):
        DispensingStoreManagement(requisition=self.requisitions[0])
  
  def display_medicine_dialog(self,medicine:dict,order=None,receive=None,initiate=None,view=None,stock_label:str|None=None):
    """A method to display medicine dialog"""
    
    #CONTROLS
    if view or stock_label not in ["dispensing","count"]:
      return
    
    #DATA
    data = {
      "unit_cost":medicine["unit_price"] if not stock_label else 0,
      "requested_amount":medicine["requisition_amount"] if not (receive or stock_label) else None,
      "total_cost":medicine["total_price"] if not (receive or stock_label) else None,
      "mfg_date":datetime.now().strftime("%Y-%m-%d"),"exp_date":datetime.now().strftime("%Y-%m-%d"),
      "brand_name":"","manufacturer":"","batch_no":"",
      "received_qty":medicine["ordered_amount"] if not stock_label else 0,
      "received_cost":medicine["ordered_price"] if not stock_label else 0,
      "rejected_qty":0,"rejected_cost":0,
      "dispensing_order_qty":0,
      "physical_count":0
      }
    
    #UI
    with ui.dialog() as self.medicine_dialog,html.div().classes(add="bg-sky-100 p-0.5"):
      #Title
      ui.label(medicine["name"]).classes(add="w-full bg-gray-800 px-1 rounded-t text-2xl text-bold text-center text-yellow-600 uppercase")
      #Body
      if receive:
        with html.div().classes(add="w-full grid grid-cols-8 grid-rows-3"):
          ui.input(label="BRAND NAME").bind_value(data,"brand_name").classes(add="col-span-2 row-start-1 outline outline-neutral-700 bg-sky-50 rounded-sm m-1 px-2 text-lg")
          ui.input(label="MANUFACTURER").bind_value(data,"manufacturer").classes(add="col-span-4 row-start-1 outline outline-neutral-700 bg-sky-50 rounded-sm m-1 px-2 text-lg")
          ui.input(label="BATCH/LOT NO").bind_value(data,"batch_no").classes(add="col-span-2 row-start-1 outline outline-neutral-700 bg-sky-50 rounded-sm m-1 px-2 text-lg")
          with ui.input(label="MFG DATE").props(add="readonly").classes(add="row-start-2 col-span-4 align-self-start outline outline-neutral-700 bg-sky-50 rounded-sm m-1 px-2 text-lg") as mfg_date_display:
              with ui.dialog() as calendar:
                ui.date(mask='YYYY-MM-DD',on_change=calendar.close).bind_value(mfg_date_display).bind_value(data,"mfg_date")
                with mfg_date_display.add_slot("append"):
                  ui.icon("fas fa-cake-candles",color="pink-500").on("click",calendar.open)
          with ui.input(label="EXPIRY DATE").props(add="id='readonly").classes(add="row-start-2 col-span-4 align-self-end outline outline-neutral-700 bg-sky-50 rounded-sm m-1 px-2 text-lg") as exp_date_display:
              with ui.dialog() as calendar:
                ui.date(mask='YYYY-MM-DD',on_change=calendar.close).bind_value(exp_date_display).bind_value(data,"exp_date")
                with exp_date_display.add_slot("append"):
                  ui.icon("fas fa-cake-candles",color="pink-500").on("click",calendar.open)
          ui.number(label="RECEIVED QTY").bind_value(data,"received_qty").classes(add="row-start-3 col-span-2 w-[95%] outline outline-neutral-700 bg-sky-50 rounded-sm m-1 px-2 text-lg")
          ui.number(label="RECEIVED COST").bind_value(data,"received_cost").classes(add="row-start-3 col-span-2 w-[95%] outline outline-neutral-700 bg-sky-50 rounded-sm m-1 px-2 text-lg")
          ui.number(label="REJECTED QTY").bind_value(data,"rejected_qty").classes(add="row-start-3 col-span-2 w-[95%] outline outline-neutral-700 bg-sky-50 rounded-sm m-1 px-2 text-lg")
          ui.number(label="REJECTED COST").bind_value(data,"rejected_cost").classes(add="row-start-3 col-span-2 w-[95%] outline outline-neutral-700 bg-sky-50 rounded-sm m-1 px-2 text-lg")
        with html.div().classes(add="w-full flex flex-row justify-center py-2"):
          ui.button(text="PROCESS MEDICINE",color="",on_click=lambda e:self.update_medicine(medicine=medicine,receive=True,new_values={"brand_name":data["brand_name"],"manufacturer":data["manufacturer"],"batch_no":data["batch_no"],"mfg_date":datetime.fromisoformat(data["mfg_date"]),"expire_date":datetime.fromisoformat(data["exp_date"]),"received_amount":data["received_qty"],"received_price":data["received_cost"],"rejected_amount":data["rejected_qty"],"rejected_price":data["rejected_cost"]})).classes(add="bg-yellow-600 text-white text-bold text-lg")
      
      if stock_label == "dispensing":
        ui.label(f"STORE BALANCE: {medicine['store_balance']:,.0f}").classes(add="w-full bg-gray-700 text-center text-yellow-600 text-bold text-lg")
        with html.div().classes(add="w-full grid grid-cols-2 gap-2 p-0.5"):
          ui.number(label="ORDER QUANTITY").bind_value(data,"dispensing_order_qty").classes(add="outline outline-gray-700 bg-sky-50 rounded-sm my-0.5 px-2 text-lg")
          ui.button(text="update medicine",color="",on_click=lambda e:self.update_medicine(medicine=medicine,new_values={"dispensing_order_qty":data["dispensing_order_qty"]},label="dispensing")).classes(add="bg-gray-700 text-yellow-500 text-bold text-xl")
      
      if stock_label == "count":
        ui.label(f"STORE BALANCE: {medicine['store_balance']:,.0f}").classes(add="w-full bg-gray-700 text-center text-yellow-600 text-bold text-lg")
        with html.div().classes(add="w-full grid grid-cols-2 gap-2 p-0.5"):
          ui.number(label="PHYSICAL COUNT").bind_value(data,"dispensing_order_qty").classes(add="outline outline-gray-700 bg-sky-50 rounded-sm my-0.5 px-2 text-lg")
          ui.button(text="update medicine",color="",on_click=lambda e:self.update_medicine(medicine=medicine,new_values={"physical_count":data["physical_count"]},label="count")).classes(add="bg-gray-700 text-yellow-500 text-bold text-xl")
      else:
        #Header
        with html.div().classes(add="w-full bg-gray-800 flex flex-row justify-around gap-3 p-2 text-bold"):
          with ui.label("UNIT:").classes(add="rounded outline outline-double outline-sky-50 px-1 text-sky-50 text-base"):
            ui.label(medicine["unit"]).classes(add="inline ml-0.5 text-yellow-600 uppercase")
          with ui.label("CLOSING BALANCE:").classes(add="rounded outline outline-double outline-sky-50 px-1 text-sky-50 text-base"):
            ui.label(medicine["closing_balance"]).classes(add="inline ml-0.5 text-yellow-600 uppercase")
          with ui.label("AMC:").classes(add="rounded outline outline-double outline-sky-50 px-1 text-sky-50 text-base"):
            ui.label(medicine["amc"]).classes(add="inline ml-0.5 text-yellow-600 uppercase")
          with ui.label("MOS:").classes(add="rounded outline outline-double outline-sky-50 px-1 text-sky-50 text-base"):
            ui.label(medicine["mos"]).classes(add="inline ml-0.5 text-yellow-600 uppercase")
        #Main
        with html.div().classes(add="w-full px-0.5 py-2 flex flex-row justify-center gap-5"):
          ui.number(label="REQUEST AMOUNT",min=1,on_change=lambda e:self.medicine_dialog.update()).bind_value(data,"requested_amount").classes(add="w-40 outline outline-gray-300 rounded px-2 text-lg")
          ui.number(label="UNIT COST(TZS)",min=1,on_change=lambda e:self.medicine_dialog.update()).bind_value(data,"unit_cost").classes(add="w-40 outline outline-gray-300 rounded px-2 text-lg")
        if order:
          ui.button(text="update medicine",color="",on_click=lambda e:self.update_medicine(medicine=medicine,order=order,new_values={"unit_cost":data["unit_cost"],"requested_amount":data["requested_amount"]})).classes(add="w-full bg-gray-800 text-yellow-600 text-bold text-lg")


    self.medicine_dialog.open()
  
  def FacilityFormularyDialog(self):
    #DATA

    #UI
    with ui.dialog().props(add="transition-show='jump-up' transition-hide='jump-down' transition-duration='500'") as self.formulary_dialog,html.div().style(add="min-width:100%;min-height:100%;").classes(add="bg-sky-100 p-0.5 flex flex-col"):
      FacilityFormulary(formulary=self.formulary,parent=self)

    self.formulary_dialog.open()


  #STOCKS UI
  def display_stocks_dialog(self,items:list[dict],label:str):
    """A method to display stock status of items"""

    #DATA
    self.stock_items = [
      {
        "name":item["name"],
        "medicine_id":item["medicine_id"],
        "brand_name":item["brand_name"],
        "manufacturer":item["manufacturer"],
        "batch_no":item["batch_no"],
        "expire_date":item["expire_date"],
        "amc":item["average_monthly_consumption"],
        "store_balance":item["store_balance"],
        "dispensing_balance":item["dispensing_balance"],
        "mos":self.mos(amc=item["average_monthly_consumption"],prev_amc=item["average_monthly_consumption"],balance=item["store_balance"]),
        "status":"overstocked" if self.mos(amc=item["average_monthly_consumption"],prev_amc=item["average_monthly_consumption"],balance=item["store_balance"]) > 4 else "understocked" if self.mos(amc=item["average_monthly_consumption"],prev_amc=item["average_monthly_consumption"],balance=item["store_balance"]) < 2 and self.mos(amc=item["average_monthly_consumption"],prev_amc=item["average_monthly_consumption"],balance=item["store_balance"]) > 0 else "stockout" if self.mos(amc=item["average_monthly_consumption"],prev_amc=item["average_monthly_consumption"],balance=item["store_balance"]) == 0 else "adequate"
      }
      for item in items
    ]
    
    title = "overstocked items" if label == "overstock" else "understocked items" if label == "understock" else "out of stock items" if label == "stockout" else "dispensing stockouts" if label == "dispensing" else "adequately stocked items"
    #UI
    with ui.dialog() as stock_dialog,html.div().style(add="min-width:100%;max-height:90%;").classes(add="bg-sky-50 p-1"):
      with html.div().classes(add="w-full flex flex-row justify-between bg-gray-800"):
        ui.label(text=title).classes(add="bg-gray-800 px-2 py-3 uppercase text-lg text-bold text-yellow-600")
        ui.button(icon="fas fa-circle-xmark fa-xl",color="",on_click=stock_dialog.close).classes(add="bg-inherit m-0 px-3 text-lg text-bold text-red-500")
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/No","field":"sno","width":100},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
            {"headerName":"BRAND NAME","field":"brand_name"},
            {"headerName":"BATCH NO","field":"batch_no"},
            {"headerName":"EXPIRY DATE","field":"expire_date"},
            {"headerName":"AMC","field":"amc","width":100},
            {"headerName":"STORE BALANCE","field":"balance"},
            {"headerName":"DISPENSING BALANCE","field":"dispensing","width":250},
            {"headerName":"MOS","field":"mos","width":100},
            {"headerName":"STATUS","field":"status","cellClassRules":{"text-green-600 text-bold":"x == 'adequate'","text-yellow-400":"x == 'understock'","text-red-600 text-bold":"x == 'stockout'","text-red-600":"x == 'overstock'"}},
          ],
          "rowData":[
            {
              "sno":self.stock_items.index(item) + 1,
              "name":item["name"],
              "brand_name":item["brand_name"] if item["brand_name"] else "---",
              "batch_no":item["batch_no"] if item["batch_no"] else "---",
              "expire_date":item["expire_date"].strftime("%b %Y") if item["expire_date"] else "---",
              "amc":f"{item['amc']:,.0f}",
              "balance":f"{item['store_balance']:,.0f}",
              "dispensing":f"{item['dispensing_balance']:,.0f}",
              "mos":item["mos"],
              "status":item["status"],
            }
            for item in self.stock_items
          ]
        }
        ).style(add="height:350px;min-width:100%;").classes(add="w-full bg-sky-300 uppercase").on("cellClicked",lambda e:self.display_medicine_dialog(medicine=[medicine for medicine in self.stock_items if medicine["name"] == e.args["data"]["name"].lower()][0],stock_label=label))
    
    stock_dialog.open()
  
  def display_physical_count_dialog(self):
    """A method to display stock status of items"""

    if not self.latest_requisition:
      ui.notify(message="No Stocked Items",type="warning",position="center")
      return

    #DATA
    self.stock_items = [
      {
        "name":item["name"],
        "medicine_id":item["medicine_id"],
        "brand_name":item["brand_name"],
        "manufacturer":item["manufacturer"],
        "batch_no":item["batch_no"],
        "expire_date":item["expire_date"],
        "store_balance":item["store_balance"],
        "dispensing_balance":item["dispensing_balance"],
        "last_physical_count":f"{item['physical_count_date'].strftime('%d %b %Y')} ({format_age(item['physical_count_date'])} ago)" if item["physical_count_date"] else "---",
        "physical_count":item['physical_count']
      }
      for item in self.latest_requisition[0]["medicines"]
    ]

    #UI
    with ui.dialog() as self.physical_count_dialog,html.div().style(add="min-width:100%;max-height:90%;").classes(add="bg-sky-50 p-1"):
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/No","field":"sno","width":100},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
            {"headerName":"BRAND NAME","field":"brand_name"},
            {"headerName":"BATCH NO","field":"batch_no"},
            {"headerName":"EXPIRY DATE","field":"expire_date"},
            {"headerName":"STORE BALANCE","field":"balance"},
            {"headerName":"DISPENSING BALANCE","field":"dispensing","width":250},
            {"headerName":"LAST COUNT","field":"last_count","width":250},
            {"headerName":"COUNT","field":"count"},
            {"headerName":"DELTA","field":"delta","cellClassRules":{"text-green-600 text-bold":"x == 0","text-red-600":"x > 1"}},
          ],
          "rowData":[
            {
              "sno":self.stock_items.index(item) + 1,
              "name":item["name"],
              "brand_name":item["brand_name"] if item["brand_name"] else "---",
              "batch_no":item["batch_no"] if item["batch_no"] else "---",
              "expire_date":item["expire_date"].strftime("%b %Y") if item["expire_date"] else "---",
              "balance":f"{item['store_balance']:,.0f}",
              "dispensing":f"{item['dispensing_balance']:,.0f}",
              "last_count":item["last_physical_count"],
              "count":item["physical_count"],
              "delta":f"{item['physical_count'] - item['store_balance']:.0f}"
            }
            for item in self.stock_items
          ]
        }
        ).style(add="height:350px;min-width:100%;").classes(add="w-full bg-sky-300 uppercase").on("cellClicked",lambda e:self.display_medicine_dialog(medicine=[medicine for medicine in self.stock_items if medicine["name"] == e.args["data"]["name"].lower()][0],stock_label="count"))
    
    self.physical_count_dialog.open()
    
#
class PharmacyReportDisplay():
  """A class for displaying summary of imagings"""

  def __init__(self,user):
    #DATA
    self.user = user
    


