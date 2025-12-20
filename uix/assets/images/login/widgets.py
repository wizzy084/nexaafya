
#GENERAL IMPORTS
import asyncio,calendar,json,math,random,time as time_delay,uuid
from collections import namedtuple
from pathlib import Path
from datetime import date,datetime,timedelta
from nicegui import html,ui

#SERVICES IMPORTS
from services.provider.admin import constants
from services.provider.admin.db import *
from services.provider.admin.constants import *
from services.provider.admin.processor import *
from services.provider.clients import db as clients_db
from services.provider.clients.processor import get_appointments,get_clients,get_active_procedures,get_active_visits,get_consultation_diagnoses

#UIX IMPORTS
from .components import *
from ._snippets import *



#WIDGETS
#Login
class Login():
  """"""

  def __init__(self):
    #DATA
    self.data()


    #UI
    with html.div().classes(add="login-blur w-[75%] lg:w-[60%] p-1 ring-1 ring-green-900 rounded shadow-md shadow-green-600 animate__animated animate__fadeIn animate__slow flex flex-col gap-0") as self.login_panel:
      #Title
      with html.section().classes(add="w-full flex flex-col gap-3"):
        with html.div().classes(add="pt-3 text-center"):
          BrandName(size="text-5xl")
        with html.div().classes(add="w-full"):
          ui.label("Hospital Information Management System").style(add="text-shadow:1px 1px #505050;").classes(add="select-none text-xl lg:text-3xl [1.35rem] text-italic text-center text-bold text-teal-400")
        
      #Info & Login form
      with html.section().classes(add="grow pt-5 flex flex-col gap-3 lg:grid grid-cols-2"):
        #Info Carousel
        with ui.carousel(value=random.choice(self.login_posters).name).props(add="animated autoplay infinite swipeable transition-prev='jump-right' transition-next='jump-right' transition-duration='3000'").style(add="overflow:hidden;").classes(add="lg-show grow q-pa-none bg-inherit") as carousel:
          for login_poster in self.login_posters:
            with ui.carousel_slide(name=login_poster.name).classes(add="bg-inherit p-0"):
              with html.picture().classes(add="w-full h-full"):
                ui.image(source=login_poster).classes(add="w-full h-full")
        
        #Login
        with html.div().classes(add="grow rounded-sm flex flex-col justify-center items-center content-center gap-1 py-5"):
          #Header
          ui.label("STAFF LOGIN").style(add="").classes(add="select-none text-3xl text-sky-200 font-bold lg:text-4xl")

          #Login Form
          with html.form().props(add=f"action='/dashboard' target='_parent'").classes(add="w-full rounded-sm flex flex-col items-center content-center gap-5 py-5"):
            #Username Input
            with ui.input(label="USERNAME").props(add="autofocus hide-bottom-space required stack-label standout outlined label-color='blue-9' bg-color='light-blue-1' input-class='text-lg text-blue-10 font-medium italic' type='text' name='username' id='username'").classes(add="w-72") as username_input:
              with username_input.add_slot("prepend"):
                ui.icon(name="fa-solid fa-user").classes(add="mr-2 text-blue-9")
                ui.separator().props(add="vertical")

            #Password Input
            with ui.input(label="PASSWORD",password_toggle_button=True).props(add="hide-bottom-space required stack-label standout outlined label-color='blue-9' color='light-blue-9' bg-color='light-blue-1' input-class='text-lg text-blue-10 font-medium italic' type='password' name='password' id='password'").classes(add="w-72") as password_input:
              with password_input.add_slot("prepend"):
                ui.icon(name="fa-solid fa-user-lock").classes(add="mr-2 text-blue-9")
                ui.separator().props(add="vertical")

            #Submit button
            ui.button(text="log in",color="black").props(add="dense glossy type='submit'").classes(add="w-36 shadow-sm shadow-green-500 text-2xl text-sky-200")

      #Company brand
      with html.section().classes(add="w-full p-1 flex flex-row justify-end"):
        CompanyName()
    
  #FUNCTIONALITIES
  def data(self):
    login_posters_path = Path("./uix/web/assets/images/login")

    self.login_posters = [poster for poster in login_posters_path.iterdir() if login_posters_path.exists() and login_posters_path.is_dir()]

#Store
class Requisitions():
  """A class to display and process requisitions"""

  def __init__(self,user,formulary:list[dict],requisitions:list[dict]):
    #DATA
    self.user = user
    self.formulary = formulary
    self.raw_requisitions = requisitions
    self.initial_data()

    #UI
    with html.div().classes(add="grow w-full flex flex-col"):
      #Separator
      for i in range(2):
        ui.separator().classes(add="w-full bg-[#09026f]")
      #Header
      with html.section().classes(add="w-full p-1 flex flex-row bg-harmony text-yellow-500"):
        with html.div().classes(add="lg:order-2 grow bg-inherit flex flex-row content-center"):
          ui.label("REQUISITIONS").classes(add="w-full rounded-t text-3xl text-bold")
        ui.button(icon="fas fa-circle-plus",color="",on_click=self.ConfirmNewRequisitionDialog).classes(add="lg:order-1 size-8 bg-inherit")
      #Body
      with html.section().classes(add="grow w-full p-0.5 flex flex-col rounded") as self.requisitions_panel:
        if self.requisitions:
          self.RequisitionsPanel(self.requisitions)
        else:
          with html.div().classes(add="w-full h-full content-center justify-center bg-sky-100 p-5"):
            ui.label("No requisitions found").classes(add="text-center text-2xl text-red-400 font-semibold")
            ui.label("Click the right upper '+' button to initiate new requisition").classes(add="text-center text-lg italic text-gray-500")
  
  #Functionalities
  def initial_data(self):
    self.base_requisition = self.raw_requisitions[0]
    self.requisitions = self.raw_requisitions[:-1] if len(self.raw_requisitions) > 2 else self.raw_requisitions
    
  def last_medicine(self,medicine:dict):
    """"""

    last_requisition = self.requisitions[-1] if len(self.requisitions) > 1 else self.base_requisition

    return [_medicine for _medicine in last_requisition["medicines"] if _medicine["medicine_id"] == medicine["medicine_id"]][0]

  def physical_count_was_done(self,requisition:dict):
    container = set()

    for medicine in requisition["medicines"]:
      if not medicine["physical_count_date"]:
        container.add(medicine["name"])
    
    return (False,len(container),requisition["requisition_id"]) if container else (True,0)
  
  def amc(self,medicine):
    """A method that returns 'amc' based on the inputs"""
    start_balance = medicine["initial_store_balance"]
    closing_balance = medicine["physical_count"]

    if self.last_medicine(medicine)["received_on"]:
      duration = math.ceil((datetime.now() - self.last_medicine(medicine)["received_on"]).days/30)
      return math.ceil(((start_balance - closing_balance)/duration)) if duration > 0 else 0
    else:
      return 0
  
  def mos(self,medicine):
    """A method that returns value of mos based on the input values"""
    balance = medicine["physical_count"]
    amc = self.amc(medicine)
    
    if amc > 0:
      return round(balance/amc,1)
    else:
      return 2 if balance > 0 else 0
  
  def uom(self,medicine):
    uom = ""

    if medicine["order_unit"] == "tablet":
      uom = f"{int(medicine['order_unit_size'])}tb"
    elif medicine["order_unit"] == "capsule":
      uom = f"{int(medicine['order_unit_size'])}cp"
    elif medicine["order_unit"] == "bottle":
      uom = f"{int(medicine['order_unit_size'])}bt"
    elif medicine["order_unit"] == "tube":
      uom = f"{int(medicine['order_unit_size'])}tu"
    elif medicine["order_unit"] == "ampoule":
      uom = f"{int(medicine['order_unit_size'])}amp"
    elif medicine["order_unit"] == "pack":
      uom = f"{int(medicine['order_unit_size'])}pk"
    elif medicine["order_unit"] == "piece":
      uom = f"{int(medicine['order_unit_size'])}pc"
    elif medicine["order_unit"] == "vial":
      uom = f"{int(medicine['order_unit_size'])}vl"

    return uom

  def requisition_label(self):

    lapse = (datetime.now() - self.requisitions[-1]["receive_date"]).days/30

    if lapse < MOS[0]:
      return "x"
    else:
      return "r"
  
  def stock_status_color(self,medicine:dict):
    result = ""

    if self.amc(medicine) > 0:
      if self.mos(medicine) > 4:
        result = "purple-600"
      elif self.mos(medicine) < 2:
        result = "yellow-500"
      elif self.mos(medicine) == 0:
        result = "rose-600"
      else:
        result = ""
    else:
      result = "gray-400"

    return result

  def requisition_amount(self,amc,mos):
    """A method returns projected requisition amount based on mos value"""

    if mos < 2:
      return math.ceil((2-mos)*amc)
    else:
      return 0
  
  def rejected_medicines(self,requisition):

    """A method to return rejected medicines"""
    
    rejected_medicines = [medicine for medicine in requisition["medicines"] if medicine["rejected"]]
    rejected_medicines_count = len(rejected_medicines)
    rejected_medicines_cost = sum([medicine["rejected_price"] for medicine in requisition["medicines"] if medicine["rejected"]])

    return [
      rejected_medicines_count if rejected_medicines else 0,
      rejected_medicines_cost if rejected_medicines else 0,
      rejected_medicines if rejected_medicines else []
    ]

  def save_medicine(self,medicine:dict,requisition:dict):
    """A method to save medicine data related to requisition"""
   
    medicine["ordered_by"] = self.user.username

    #DB STORAGE
    medicine["requisition_medicine_id"] = f"{medicine['medicine_id']}{medicine['requisition_id']}"
    register_medicine(medicine)
    

    for self_medicine in self.medicines:
      if self_medicine["medicine_id"] == medicine["medicine_id"]:
        index = self.medicines.index(self_medicine)
        self.medicines.remove(self_medicine)
        self.medicines.insert(index,medicine)
    
    requisition["medicines"] = self.medicines

    self.requisition_display_pad.clear()
    with self.requisition_display_pad:
      self.RequisitionAggrid(requisition=requisition)
    
    self.medicine_dialog.close()

  def update_requisition(self,requisition:dict,initiate:bool|None=None,order:bool|None=None,receive:bool|None=None,cancel:bool|None=None):
    """Removes requisition from database table and its corresponding medicines and stationeries in their corresponding tables"""
    
    if cancel:
      requisition["cancelled"] = True
      requisition["cancelled_by"] = self.user.username
      status = update_requisition(requisition=requisition,cancel=True)

    if initiate:
      requisition["initiated"] = True
      requisition["initiated_by"] = self.user.username
      status = update_requisition(requisition=requisition,initiate=True)

    if order:
      requisition["placed"] = True
      requisition["placed_by"] = self.user.username

      status = update_requisition(requisition=requisition,order=True)

    if receive:
      unprocessed = len([i for i in requisition["medicines"] if i['ordered'] and not (i['received'] or i['rejected'])])
      if unprocessed > 0:
        ui.notify(message=f"{unprocessed} {'item' if unprocessed == 1 else 'items'} not processed! Review your requisition",type="warning",position="center")
        return
      else:
        requisition["received"] = True
        requisition["received_by"] = self.user.username
        status = update_requisition(requisition=requisition,receive=True)
      
    ui.notify(message=status["message"],type=status["type"],position=status["position"])

    self.requisition_dialog.close()
    self.initial_data()
    self.RequisitionsPanel(requisitions=self.requisitions)

  def update_medicine(self,medicine:dict,requisition:dict,cancel:bool|None=None,transfer:bool|None=None,count:bool|None=None,receive:bool|None=None,order:bool|None=None):
    """A method to update medicine"""

    #Transfer
    if transfer:
      medicine["store_balance"] -= medicine["transfer_balance"]
      medicine["dispensing_balance"] += medicine["transfer_balance"]
      medicine["transferred_by"] = self.user.username
      update_medicine(medicine=medicine,transfer=True)

      for self_medicine in self.medicines:
        if self_medicine["medicine_id"] == medicine["medicine_id"]:
          index = self.medicines.index(self_medicine)
          self.medicines.remove(self_medicine)
          self.medicines.insert(index,medicine)
    
    if count:
      medicine["count_unit"] = self.last_medicine(medicine)["count_unit"]
      medicine["physical_count"] = medicine["store_balance"] + medicine["dispensing_balance"]
      medicine["counted_by"] = self.user.username
      medicine["physical_count_date"] = datetime.now()

      update_medicine(medicine=medicine,count=True)

      for self_medicine in self.medicines:
        if self_medicine["medicine_id"] == medicine["medicine_id"]:
          index = self.medicines.index(self_medicine)
          self.medicines.remove(self_medicine)
          self.medicines.insert(index,medicine)

    if cancel:
      medicine["cancelled"] = True
      medicine["cancelled_by"] = self.user.username

      update_medicine(medicine=medicine,cancel=True)

      for self_medicine in self.medicines:
        if self_medicine["medicine_id"] == medicine["medicine_id"]:
          index = self.medicines.index(self_medicine)
          self.medicines.remove(self_medicine)
          self.medicines.insert(index,medicine)
      
    if receive:
      medicine["mfg_date"] = datetime.fromisoformat(medicine["mfg_date"])
      medicine["expire_date"] = datetime.fromisoformat(medicine["expire_date"])
      for self_medicine in self.medicines:
        if self_medicine["medicine_id"] == medicine["medicine_id"]:
          index = self.medicines.index(self_medicine)
          self.medicines.remove(medicine)
      
      medicine["invoice"] = None
      medicine["count_unit"] = self.last_medicine(medicine)["count_unit"]
      medicine["received"] = True if medicine["received_amount"] else False
      medicine["active"] = True if medicine["received_amount"] else False
      medicine["received_by"] = self.user.username if medicine["received_amount"] else None
      medicine["rejected"] = True if medicine["rejected_amount"] else False
      medicine["rejected_amount"] = medicine["rejected_amount"] if medicine["rejected_amount"] else 0
      medicine["rejected_price"] = medicine["rejected_price"] if medicine["rejected_price"] else 0
      medicine["store_balance"] = medicine["initial_store_balance"] = medicine["physical_count"] = medicine["received_amount"]

      update_medicine(medicine=medicine,receive=True)

      self.medicines.insert(index,medicine)
    
    if order:
      medicine["ordered_by"] = self.user.username
      medicine["ordered"] = True if medicine["ordered_amount"] else False
      medicine["ordered_price"] = medicine["unit_price"] * round(medicine["ordered_amount"]/medicine["order_unit_size"])

      update_medicine(medicine=medicine,order=True)

      for self_medicine in self.medicines:
        if self_medicine["medicine_id"] == medicine["medicine_id"]:
          index = self.medicines.index(self_medicine)
          self.medicines.remove(self_medicine)
          self.medicines.insert(index,medicine)

    requisition["medicines"] = self.medicines

    self.requisition_display_pad.clear()
    with self.requisition_display_pad:
      self.RequisitionAggrid(requisition=requisition)
    
    self.medicine_dialog.close()

  #DISPLAYS
  def RequisitionsPanel(self,requisitions:list[dict]):
    """A method to display list of requisitions"""
    #DATA
    
    #UI
    self.requisitions_panel.clear()
    with self.requisitions_panel:
      with ui.scroll_area().classes(add="grow w-full"):
        with html.div().classes(add="w-full flex flex-col gap-3 animate__animated animate__fadeIn"):
          for requisition in requisitions:
            #Requisition
            with ui.button(color="",on_click=lambda e:self.RequisitionDialog(requisition=[requisition for requisition in requisitions if requisition["requisition_id"] == e.sender.slots["default"].children[0].slots["default"].children[0].props["id"].lower()][0])).props(add="elevated").classes(add=f"{'bg-green-600 shadow-md shadow-green-600' if  requisition['received'] else 'bg-teal-500 shadow-md shadow-teal-500' if requisition['placed'] and not requisition['received'] else 'bg-violet-500 shadow-md shadow-violet-500' if requisition['initiated'] and not requisition['placed'] else 'bg-gray-500 shadow-md shadow-gray-500' if not requisition['initiated'] or requisition['cancelled'] else ''} h-fit rounded p-0.5 text-2xl text-bold"):
              #Header
              with html.header().classes(add="w-full rounded-t bg-harmony flex flex-row justify-between"):
                ui.label(requisition["requisition_id"].split("-")[0].upper()).props(add=f"id='{requisition["requisition_id"]}'").classes(add=f"rounded-t px-1 text-{'green-500' if  requisition['received'] else 'teal-500' if requisition['placed'] and not requisition['received'] else 'purple-400' if requisition['initiated'] and not requisition['placed'] else 'gray-500' if not requisition['initiated'] or requisition['cancelled'] else ''} text-lg")
                ui.chip(icon=f"{'fa-regular fa-circle-check' if requisition['received'] else 'fas fa-spinner fa-spin'}",text_color=f"{'green' if requisition['received'] else 'teal' if requisition['placed'] else 'purple' if requisition['initiated'] and not requisition['placed'] else 'red' }",color="").classes(add="m-0 p-0 bg-inherit text-violet-500")
              ui.separator()
              #Body
              with html.main().classes(add=f"w-full rounded-b p-0.5 bg-harmony grid grid-cols-7 {'grid-rows-4' if requisition['cancelled'] and self.rejected_medicines(requisition)[0] else 'grid-rows-3' if requisition['cancelled'] or self.rejected_medicines(requisition)[0] else 'grid-rows-2'}"):
                #Dates
                with ui.label("ORDERED:").classes(add=f"col-span-4 row-start-1 text-start text-xs {'text-gray-400' if requisition['cancelled'] else 'text-sky-50'}"):
                  ui.label(f"{requisition['placement_date'].strftime('%d %b %Y')} ({format_age(requisition['placement_date'])} ago)" if requisition["placed"] else " - - -").classes(add=f"inline ml-0.5 text-{'green-500' if  requisition['received'] else 'teal-500' if requisition['placed'] and not requisition['received'] else 'purple-400' if requisition['initiated'] and not requisition['placed'] else 'gray-500' if not requisition['initiated'] or requisition['cancelled'] else ''}")
                with ui.label("RECEIVED:").classes(add=f"col-span-4 row-start-2 text-start text-xs {'text-gray-400' if requisition['cancelled'] else 'text-sky-50'}"):
                  ui.label(f"{requisition['receive_date'].strftime('%d %b %Y')} ({format_age(requisition['receive_date'])} ago)" if requisition["received"] else " - - -").classes(add=f"inline ml-0.5 text-{'green-500' if  requisition['received'] else 'teal-500' if requisition['placed'] and not requisition['received'] else 'purple-400' if requisition['initiated'] and not requisition['placed'] else 'gray-500' if not requisition['initiated'] or requisition['cancelled'] else ''}")
                with ui.label("REJECTED:").classes(add=f"{'' if self.rejected_medicines(requisition)[0] else 'hidden' } col-span-4 row-start-3 text-start text-xs text-sky-50"):
                  ui.label(f"{requisition['receive_date'].strftime('%d %b %Y')} ({format_age(requisition['receive_date'])} ago)" if requisition["received"] else " - - -").classes(add=f"inline ml-0.5 text-{'green-500' if  requisition['received'] else 'teal-500' if requisition['placed'] and not requisition['received'] else 'purple-400' if requisition['initiated'] and not requisition['placed'] else 'gray-500' if not requisition['initiated'] or requisition['cancelled'] else ''}")
                if requisition["cancelled"]:
                  with ui.label("CANCELLED:").classes(add=f"col-span-4 row-start-4 text-start text-xs {'text-gray-400' if requisition['cancelled'] else 'text-sky-50'}"):
                    ui.label(f"{requisition['cancel_date'].strftime('%d %b %Y')} ({format_age(requisition['cancel_date'])} ago)" if requisition['cancelled'] else " - - -").classes(add=f"inline ml-0.5 text-{'green-500' if  requisition['received'] else 'teal-500' if requisition['placed'] and not requisition['received'] else 'purple-400' if requisition['initiated'] and not requisition['placed'] else 'gray-500' if not requisition['initiated'] or requisition['cancelled'] else ''}")
                      
                #Items
                #Ordered medicines
                with ui.label(f"{len([medicine for medicine in requisition['medicines'] if medicine['ordered'] and not medicine['cancelled']]):,}" if requisition["placed"] else "").classes(add=f"col-start-5 row-start-1 w-full text-xs uppercase text-{'green-500' if  requisition['received'] else 'teal-500' if requisition['placed'] and not requisition['received'] else 'purple-400' if requisition['initiated'] and not requisition['placed'] else 'gray-500' if not requisition['initiated'] or requisition['cancelled'] else ''}"):
                  ui.label("ITEMS" if requisition["placed"] else "").classes(add=f"inline ml-1 text-white text-xs")
                #Received medicines count
                with ui.label(f"{len([medicine for medicine in requisition['medicines'] if medicine['received']]):,}" if (requisition['received']) else "").classes(add=f"col-start-5 row-start-2 w-full text-xs uppercase text-{'green-500' if  requisition['received'] else 'teal-500' if requisition['placed'] and not requisition['received'] else 'purple-400' if requisition['initiated'] and not requisition['placed'] else 'gray-500' if not requisition['initiated'] or requisition['cancelled'] else ''}"):
                  ui.label("ITEMS" if (requisition["received"]) else "").classes(add=f"inline ml-1 text-white text-xs")
                #Rejected medicines count
                with ui.label(f"{self.rejected_medicines(requisition)[0]:,}" if (requisition['received']) else "").classes(add=f"{'' if self.rejected_medicines(requisition)[0] else 'hidden'} col-start-5 row-start-3 w-full text-xs uppercase text-{'green-500' if  requisition['received'] else 'teal-500' if requisition['placed'] and not requisition['received'] else 'purple-400' if requisition['initiated'] and not requisition['placed'] else 'gray-500' if not requisition['initiated'] or requisition['cancelled'] else ''}"):
                  ui.label("ITEMS" if (requisition["received"]) else "").classes(add=f"inline ml-1 text-white text-xs")
                #Cancelled
                if requisition["cancelled"]:
                  with ui.label("By").classes(add=f"col-span-4 row-start-4 text-xs text-white"):
                    ui.label(f"{get_staff(requisition['cancelled_by'])['title'].capitalize()} {get_staff(requisition['cancelled_by'])['first_name'].capitalize()} {get_staff(requisition['cancelled_by'])['last_name'].capitalize()}" if requisition["cancelled"] else " - - -").classes(add=f"inline ml-1 {'green-600' if  requisition['received'] else 'yellow-500' if requisition['placed'] and not requisition['received'] else 'purple-400' if requisition['initiated'] and not requisition['placed'] else 'gray-500' if not requisition['initiated'] or requisition['cancelled'] else ''}")

                #Cost
                #Ordered medicines cost
                with ui.label(f"{sum([medicine['ordered_price'] for medicine in requisition['medicines'] if medicine['ordered'] and not medicine['cancelled']]):,.2f}" if requisition["placed"] else "").classes(add=f"col-start-6 col-span-2 row-start-1 w-full text-end text-xs uppercase text-{'green-500' if  requisition['received'] else 'teal-500' if requisition['placed'] and not requisition['received'] else 'purple-400' if requisition['initiated'] and not requisition['placed'] else 'gray-500' if not requisition['initiated'] or requisition['cancelled'] else ''}"):
                  ui.label("TZS" if requisition["placed"] else "").classes(add=f"inline ml-1 text-white text-xs")
                #Received medicines cost
                with ui.label(f"{sum([medicine['received_price'] for medicine in requisition['medicines'] if medicine['received']]):,.2f}" if requisition["received"] else "").classes(add=f"col-start-6 col-span-2 row-start-2 w-full text-end text-xs uppercase text-{'green-500' if  requisition['received'] else 'teal-500' if requisition['placed'] and not requisition['received'] else 'purple-400' if requisition['initiated'] and not requisition['placed'] else 'gray-500' if not requisition['initiated'] or requisition['cancelled'] else ''}"):
                  ui.label("TZS" if (requisition["received"]) else "").classes(add=f"inline ml-1 text-white text-xs")
                #Rejected medicines cost
                with ui.label(f"{self.rejected_medicines(requisition)[1]:,.2f}" if requisition["received"] else "").classes(add=f"{'' if self.rejected_medicines(requisition)[0] else 'hidden'} col-start-6 col-span-2 row-start-3 w-full text-end text-xs uppercase text-{'green-500' if  requisition['received'] else 'teal-500' if requisition['placed'] and not requisition['received'] else 'purple-400' if requisition['initiated'] and not requisition['placed'] else 'gray-500' if not requisition['initiated'] or requisition['cancelled'] else ''}"):
                  ui.label("TZS" if (requisition["received"]) else "").classes(add=f"inline ml-1 text-white text-xs")

  def ConfirmNewRequisitionDialog(self):

    if not self.requisitions[0]["received"]:
      ui.notify(message="There is an active requisition.Please visit Requisitions panel",type="warning",position="center")
      return

    #Confirm requisition instantiation
    with ui.dialog().props(add="transition-show='jump-up' transition-hide='jump-down' transition-duration='500'") as self.confirm_new_requisition_dialog,html.div().style(add="min-width:30%;").classes(add="rounded-md bg-sky-100 p-0.5"):
      with html.div().classes(add="w-full p-2 flex flex-col gap-5 rounded bg-sky-100"):
        ui.label("Create New Requisition?").classes(add="w-full p-2 text-center text-3xl text-bold")
        with html.div().classes(add="w-full py-1 flex flex-row justify-center gap-5"):
          ui.button(text="YES",icon="fa-regular fa-circle-check",color="",on_click=self.RequisitionDialog).props(add="glossy").classes(add="rounded bg-harmony text-bold text-green-500 text-lg lg:text-xl")
          ui.button(text="NO",icon="fa-regular fa-circle-xmark",color="",on_click=self.confirm_new_requisition_dialog.close).props(add="glossy").classes(add="rounded bg-harmony text-red-500 text-bold text-lg lg:text-xl")
    
    self.confirm_new_requisition_dialog.open()
  
  def RequisitionConfirmationDialog(self,requisition:dict,initiate:bool=False,order:bool=False,receive:bool=False,cancel:bool=False): 
    """A generic dialog for confirmation of commands in requisitions"""
    #DATA
    requisition = requisition
    requisition["vendor"] = VENDORS[2]

    #UI
    with ui.dialog().props(add="transition-show='jump-up' transition-hide='jump-down' transition-duration='500'") as self.requisition_confirmation_dialog,html.div().style(add="min-width:50%;").classes(add="rounded-md bg-sky-100 p-0.5"):
      with html.div().classes(add="w-full p-0.5 flex flex-col gap-5 rounded bg-sky-100"):
        if initiate:
          ui.label("Do you want to initiate ?").classes(add="w-full p-2 text-center text-xl lg:text-3xl text-bold")
          with html.div().classes(add="w-full py-1 flex flex-row justify-center gap-5"):
            ui.button(text="YES",icon="fa-regular fa-circle-check",color="",on_click=lambda e:self.update_requisition(requisition=requisition,initiate=True)).props(add="glossy").classes(add="bg-harmony text-bold text-green-600 text-lg lg:text-xl")
            ui.button(text="NO",icon="fa-regular fa-circle-xmark",color="",on_click=self.requisition_confirmation_dialog.close).props(add="glossy").classes(add="bg-harmony text-red-500 text-bold text-lg lg:text-xl")

        if order:
          ui.label("REQUISITION ORDER").classes(add="w-full p-2 bg-harmony rounded-t text-2xl lg:text-5xl font-bold text-yellow-500")
          with html.div().classes(add="grow w-full p-3 flex flex-col justify-around items-center gap-3"):
            #Vendor
            ui.select(label="VENDOR",options=VENDORS).props(add="bordered input-class='px-1' label-color='#07004d' popup-content-class='capitalize' transition-show='jump-down' transition-hide='jump-up' transition-duration='500'").classes(add="w-full lg:w-72 shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-xl capitalize").bind_value(requisition,"vendor")

            #Proceed
            with html.div().classes(add="w-full py-1 flex flex-row justify-center gap-5"):
              ui.button(text="YES",icon="fa-regular fa-circle-check",color="",on_click=lambda e:self.update_requisition(requisition=requisition,order=True)).props(add="glossy").classes(add="bg-harmony text-bold text-green-600 text-lg lg:text-xl")
              ui.button(text="NO",icon="fa-regular fa-circle-xmark",color="",on_click=self.requisition_confirmation_dialog.close).props(add="glossy").classes(add="bg-harmony text-red-500 text-bold text-lg lg:text-xl")
          
        if receive:
          with html.section().classes(add="w-full P-3 flex flex-col lg:flex-row justify-around gap-5"):
            ui.input(label="INVOICE NUMBER").props(add="bordered").classes(add="w-full lg:w-52 shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value(requisition,"invoice_id")
            ui.input(label="DELIVERY NOTE NUMBER").props(add="bordered").classes(add="w-full lg:w-52 shadow-md shadow-[#07004d] bg-white rounded-sm px-2 text-lg").bind_value(requisition,"delivery_note_id")
            ui.button(text="CONFIRM",icon="fa-regular fa-circle-check",color="",on_click=lambda e:self.update_requisition(requisition=requisition,receive=True)).props(add="glossy").classes(add="bg-harmony text-bold text-green-600 text-lg lg:text-xl")

        if cancel:
          ui.label("Do you want to cancel this requisition...?").classes(add="w-full p-2 text-center text-xl lg:text-3xl text-bold")
          with html.div().classes(add="w-full py-1 flex flex-row justify-center gap-5"):
            ui.button(text="YES",icon="fa-regular fa-circle-check",color="",on_click=lambda e:self.update_requisition(requisition=requisition,cancel=True)).props(add="glossy").classes(add="bg-harmony text-bold text-green-600 text-lg lg:text-xl")
            ui.button(text="NO",icon="fa-regular fa-circle-xmark",color="",on_click=self.requisition_confirmation_dialog.close).props(add="glossy").classes(add="bg-harmony text-red-500 text-bold text-lg lg:text-xl")
    
    self.requisition_confirmation_dialog.open()

  def RequisitionDialog(self,requisition:dict|None=None):
    """A method for displaying requisistion form"""

    #DATA
    if requisition:
      data = requisition
    else:
      last_requisition = self.requisitions[-1]
      if not last_requisition["received"]:
        ui.notify(message=f"There is a pending requisition {last_requisition['requisition_id'].upper()}!",type="warning",position="center")
        return
      else:
        #Warn if physical count not done
        physical_count = self.physical_count_was_done(requisition=last_requisition)
        if not physical_count[0]:
          ui.notify(
            message=f"Physical count wasn't completed for {physical_count[1]} items in requisition {physical_count[2].upper()}!",
            type="warning",
            position="center",
            icon="fa-solid fa-exclamation-circle fa-fade"
          )
          self.confirm_new_requisition_dialog.close()
          return

        #Build new requisition
        new_requisition_id = f"req{datetime.now().strftime('%y%m')}{self.requisition_label()}-{uuid.uuid4()}"
        self.new_medicines = [
          {
            "name":medicine["name"],
            "medicine_id":medicine["medicine_id"],
            "requisition_medicine_id":medicine["medicine_id"] + new_requisition_id,
            "type":medicine["type"],
            "category":medicine["category"],
            "drug_class":medicine["drug_class"],
            "fda_pregnancy_category_1":medicine["fda_pregnancy_category_1"],
            "fda_pregnancy_category_2":medicine["fda_pregnancy_category_2"],
            "fda_pregnancy_category_3":medicine["fda_pregnancy_category_3"],
            "prescription_level":medicine["prescription_level"],
            "order_unit":self.last_medicine(medicine)["order_unit"],
            "order_unit_size":self.last_medicine(medicine)["order_unit_size"],
            "amc":self.amc(self.last_medicine(medicine)),
            "mos":self.mos(self.last_medicine(medicine)),
            "initial_store_balance":self.last_medicine(medicine)["physical_count"],
            "store_balance":self.last_medicine(medicine)["physical_count"],
            "physical_count":self.last_medicine(medicine)["physical_count"],
            "ordered_amount":self.requisition_amount(amc=self.amc(self.last_medicine(medicine)),mos=self.mos(self.last_medicine(medicine))),
            "unit_price":self.last_medicine(medicine)["unit_price"],
            "ordered_price":(self.requisition_amount(amc=self.amc(self.last_medicine(medicine)),mos=self.mos(self.last_medicine(medicine)))/self.last_medicine(medicine)["order_unit_size"]) * self.last_medicine(medicine)["unit_price"],
            "ordered_by":self.user.username,
            "cancelled":False,
            "ordered":False,
            "received":False,
            "prices":self.last_medicine(medicine)["prices"]
          }
          for medicine in self.formulary
        ]

        data = {
          "requisition_id":new_requisition_id,
          "initiated":True,
          "initiated_by":self.user.username,
          "placed":False,
          "received":False,
          "medicines":self.new_medicines
        }

        #Register new requisition and initial medicines
        register_requisition(data)
        for new_medicine in self.new_medicines:
          new_medicine["requisition_id"] = data["requisition_id"]
          register_medicine(new_medicine)
      
    #UI
    with ui.dialog().props(add="transition-show='jump-up' transition-hide='jump-down' transition-duration='500'") as self.requisition_dialog,html.div().style(add="min-width:100%;min-height:100%;").classes(add="bg-sky-100 p-0.5 flex flex-col"):
      with html.div().classes(add="grow w-full flex flex-col") as self.requisition_display_pad:
        self.RequisitionAggrid(requisition=data)
        
    self.requisition_dialog.open()
    
  def RequisitionAggrid(self,requisition:dict):
    """"""
    #DATA
    requisition = requisition
    self.medicines = sorted(requisition["medicines"],key=lambda medicine:medicine["name"])
    ordered_medicines = [medicine for medicine in self.medicines if medicine["ordered"]]

    #UI
    self.requisition_display_pad.clear()
    with self.requisition_display_pad:
      #Header
      with html.header().classes(add="w-full rounded-t bg-harmony flex flex-row"):
        with html.section().classes(add="grow px-1 flex flex-col content-start lg:flex-row lg:content-center lg:justify-between"):
          #Requisition ID
          with ui.label("REQUISITION ID:").classes(add="text-bold text-sky-300 text-lg"):
            ui.label(requisition["requisition_id"].split("-")[0]).classes(add="inline ml-1 text-yellow-500 text-bold uppercase")
          
          if requisition["received"]:
            #Invoice ID
            with ui.label("INVOICE NO: ").classes(add="text-bold text-sky-300 text-lg"):
              ui.label(f"{requisition['invoice_id']}").classes(add="inline ml-0.5 text-yellow-500 text-bold uppercase")
            #Receive date
            with ui.label("RECEIVED ON: ").classes(add="text-bold text-sky-300 text-bold text-lg"):
              ui.label(f"{requisition['receive_date'].strftime('%d %b %Y')}").classes(add="inline ml-0.5 text-bold text-yellow-500 uppercase")
            #Received items
            with ui.label("RECEIVED ITEMS: ").classes(add="text-bold text-sky-300 text-bold text-lg"):
              ui.label(str(len([item for item in requisition["medicines"] if item["received"]]))).classes(add="inline ml-0.5 text-bold text-yellow-500 uppercase")
            #Cost
            with ui.label("COST: ").classes(add="text-bold text-sky-300 text-lg"):
              ui.label(f"{sum([item['received_price'] for item in requisition['medicines'] if not item['cancelled'] and item['ordered']]):,.2f} TZS").classes(add="inline ml-1 text-yellow-500 text-bold uppercase")
          
          elif requisition["placed"]:
            #Order date
            with ui.label("ORDERED ON: ").classes(add="text-bold text-sky-300 text-bold text-lg"):
              ui.label(f"{requisition['placement_date'].strftime('%d %b %Y')}").classes(add="inline ml-0.5 text-bold text-yellow-500 uppercase")
            #Ordered Items
            with ui.label("ORDERED ITEMS: ").classes(add="text-bold text-sky-300 text-lg"):
              ui.label(str(len([item for item in requisition["medicines"] if item["ordered"]]))).classes(add="inline ml-1 text-yellow-500 uppercase")
            #Order cost
            with ui.label("COST: ").classes(add="text-bold text-sky-300 text-lg"):
              ui.label(f"{sum([item['ordered_price'] for item in requisition['medicines'] if not item['cancelled'] and item['ordered']]):,.2f} TZS").classes(add="inline ml-1 text-yellow-500 text-bold uppercase")
          
          elif requisition["initiated"]:
            #Ordered Items
            with ui.label("ITEMS: ").classes(add="text-bold text-sky-300 text-lg"):
              ui.label(str(len([item for item in requisition["medicines"] if item["ordered"]]))).classes(add="inline ml-1 text-yellow-500 uppercase")
            #Order cost
            with ui.label("COST: ").classes(add="text-bold text-sky-300 text-lg"):
              ui.label(f"{sum([item['ordered_price'] for item in requisition['medicines'] if not item['cancelled'] and item['ordered']]):,.2f} TZS").classes(add="inline ml-1 text-yellow-500 text-bold uppercase")
        
        with html.section().classes(add="flex flex-col justify-center"):
          ui.button(icon="fas fa-circle-xmark fa-xl",color="",on_click=self.requisition_dialog.close).classes(add="bg-inherit m-0 px-3 text-lg text-bold text-red-500")
    
      #Display
      with html.div().classes(add="grow w-full p-1 flex flex-col gap-3"):
        if requisition["received"]:
          #Small screen
          with ui.scroll_area().classes(add="lg:hidden grow w-full rounded shadow-md shadow-[#07004d] py-3"):
            for medicine in self.medicines:
              with ui.button(color="",on_click=lambda e:self.MedicineDialog(medicine=[medicine for medicine in self.medicines if medicine["requisition_medicine_id"] == e.sender.props["id"].lower()][0],requisition=requisition,ordered=requisition["placed"])).props(add=f"elevated id={medicine['requisition_medicine_id']}").classes(add=f"w-full h-fit p-1 bg-sky-100 shadow-md shadow-[#07004d] flex flex-row"):
                #Index
                ui.label(str(self.medicines.index(medicine) + 1)).classes(add="size-8 rounded-full ring-1 ring-offset-1 ring-[#07004d] bg-harmony flex flex-col justify-center text-sky-300 text-lg font-semibold")
                #Details
                with html.div().classes(add="grow ml-1 h-full flex flex-col gap-1"):
                  #Identity
                  with html.section().classes(add="w-full px-1 flex flex-col md:flex-row justify-between font-semibold"):
                    ui.label(medicine['name']).classes(add="text-start text-lg")
                  
                  #Stock details
                  with html.section().classes(add="w-full px-1 flex flex-row justify-between gap-3 font-semibold"):
                    ui.label(medicine['type']).classes(add="text-start md:text-end italic text-gray-700")
                    with ui.label("AMC").classes(add="text-gray-700"):
                      ui.label(f"{self.amc(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")
                    with ui.label("MOS").classes(add="text-gray-700"):
                      ui.label(f"{self.mos(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")
    
                  #Stats
                  with html.div().classes(add="w-full px-1 flex flex-row justify-between font-semibold"):
                    with ui.label("MAIN STORE").classes(add="text-gray-700"):
                      ui.label(f"{medicine['store_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")
                    with ui.label("DISPENSING STORE").classes(add="text-gray-700"):
                      ui.label(f"{medicine['dispensing_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")

          #Large screen
          ui.aggrid(
            {
              "columnDefs":[
                {"headerName":"S/No","field":"sno","width":100},
                {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","floatingFilter":True,"width":450},
                {"headerName":"TYPE","field":"type","width":150},
                {"headerName":"UNIT","field":"unit","width":150},
                {"headerName":"BRAND NAME","field":"brand_name"},
                {"headerName":"MANUFACTURER","field":"manufacturer"},
                {"headerName":"EXPIRY DATE","field":"expire_date","width":200},
                {"headerName":"STORE","field":"store_balance","width":150},
                {"headerName":"DISPENSING","field":"dispensing_balance"}
              ],
              "rowData":[
                {
                  "sno":self.medicines.index(medicine) + 1,
                  "name":medicine["name"],
                  "type":medicine["type"],
                  "unit":medicine["order_unit"],
                  "brand_name":medicine["brand_name"] if medicine["brand_name"] else "---",
                  "manufacturer":medicine["manufacturer"] if medicine["manufacturer"] else "---",
                  "expire_date":medicine["expire_date"].strftime("%b %Y") if medicine["expire_date"] else "---",
                  "store_balance":f"{medicine['store_balance']:,.0f}",
                  "dispensing_balance":f"{medicine['dispensing_balance']:,.0f}"
                }
                for medicine in self.medicines
              ]
            },theme="quartz"
            ).style(add="height:350px").classes(add="lg-show grow w-full bg-sky-300 text-sm uppercase").on("cellClicked",lambda e:self.MedicineDialog(medicine=[medicine for medicine in self.medicines if medicine["name"] == e.args["data"]["name"].lower()][0],requisition=requisition,ordered=requisition["placed"]))
          
        elif requisition["placed"]:
          #Small screen
          with ui.scroll_area().classes(add="lg:hidden grow w-full"):
            for medicine in ordered_medicines:
              with ui.button(color="",on_click=lambda e:self.MedicineDialog(medicine=[medicine for medicine in self.medicines if medicine["requisition_medicine_id"] == e.sender.props["id"].lower()][0],requisition=requisition,ordered=requisition["placed"])).props(add=f"elevated id={medicine['requisition_medicine_id']}").classes(add=f"w-full h-fit p-1 bg-sky-100 ring-2 ring-{self.stock_status_color(medicine)} flex flex-row"):
                #Index
                ui.label(str(self.medicines.index(medicine) + 1)).classes(add="size-8 rounded-full ring-1 ring-offset-1 ring-[#07004d] bg-harmony flex flex-col justify-center text-sky-300 text-lg font-semibold")
                #Details
                with html.div().classes(add="grow ml-1 h-full flex flex-col gap-1"):
                  #Identity
                  with html.section().classes(add="w-full px-1 font-semibold"):
                    ui.label(medicine['name']).classes(add="text-start text-lg")
                  with html.section().classes(add="w-full px-1 flex flex-row justify-between font-semibold"):
                    ui.label(medicine['type']).classes(add="text-start md:text-end italic text-gray-600")
                    ui.label(self.uom(medicine)).classes(add="text-start md:text-end italic text-gray-600")
                  
                  #Manufacturing details
                  with html.section().classes(add="w-full px-1 flex flex-row justify-between font-semibold"):
                    with html.span():
                      html.span().classes(add="mr-1 fa-solid fa-hands-asl-interpreting text-gray-700")
                      html.span(medicine["brand_name"] if medicine["brand_name"] else "---").classes(add="text-sky-700")
                    with html.span():
                      html.span().classes(add="mr-1 fa-solid fa-industry text-gray-700")
                      html.span(medicine['manufacturer'] if medicine["manufacturer"] else "---").classes(add="text-sky-700")
                    with html.span():
                      html.span().classes(add="mr-1 fa-solid fa-hourglass-end text-gray-700")
                      html.span(medicine["expire_date"].strftime("%b %Y") if medicine["expire_date"] else "---").classes(add="text-sky-700")
    
                  #Stats
                  with html.div().classes(add="w-full px-1 flex flex-row justify-between font-semibold"):
                    with ui.label("STORE BALANCE").classes(add="text-gray-600"):
                      ui.label(f"{medicine['store_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")
                    with ui.label("DISPENSING BALANCE").classes(add="text-gray-600"):
                      ui.label(f"{medicine['dispensing_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")
            
          #Large Screen
          ui.aggrid(
            {
              "columnDefs":[
                {"headerName":"S/No","field":"sno","width":100},
                {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
                {"headerName":"TYPE","field":"type","width":150},
                {"headerName":"UNIT","field":"unit","width":150},
                {"headerName":"BRAND NAME","field":"brand_name"},
                {"headerName":"MANUFACTURER","field":"manufacturer"},
                {"headerName":"BATCH NO","field":"batch_no"},
                {"headerName":"MFG DATE","field":"mfg_date","width":200},
                {"headerName":"EXPIRY DATE","field":"expire_date","width":200},
                {"headerName":"STATUS","field":"status","cellClassRules":{"text-green-600 text-bold":"x == 'Received'","text-red-600 text-bold":"x == 'Rejected'"}},
                {"headerName":"AMOUNT","field":"amount"},
                {"headerName":"COST (TZS)","field":"cost"}
              ],
              "rowData":[
                {
                  "sno":self.medicines.index(medicine) + 1,
                  "name":medicine["name"],
                  "type":medicine["type"],
                  "unit":self.uom(medicine),
                  "brand_name":medicine["brand_name"] if medicine["brand_name"] else "---",
                  "manufacturer":medicine["manufacturer"] if medicine["manufacturer"] else "---",
                  "batch_no":medicine["batch_no"] if medicine["batch_no"] else "---",
                  "mfg_date":medicine["mfg_date"].strftime("%b %Y") if medicine["mfg_date"] else "---",
                  "expire_date":medicine["expire_date"].strftime("%b %Y") if medicine["expire_date"] else "---",
                  "status":"Received" if medicine["received_amount"] else "Rejected" if medicine["rejected"] else "---",
                  "amount":f"{medicine['received_amount']:,.0f}" if medicine['received'] else f"{medicine['rejected_amount']:,.0f}" if medicine["rejected"] else "---",
                  "cost":f"{medicine['received_price']:,.2f}" if medicine['received'] else f"{medicine['rejected_price']:,.2f}" if medicine["rejected"] else "---"
                }
                for medicine in self.medicines
              ]
            },theme="quartz"
            ).style(add="height:350px").classes(add="lg-show grow w-full bg-sky-300 text-sm uppercase").on("cellClicked",lambda e:self.MedicineDialog(medicine=[medicine for medicine in self.medicines if medicine["name"] == e.args["data"]["name"].lower()][0],requisition=requisition,ordered=requisition["placed"]))
          
          #Totals & Buttons
          with html.div().classes(add="w-full p-2 flex flex-row justify-between gap-5"):
            #Totals
            with html.div().classes(add="w-full lg:w-fit flex flex-row justify-center lg:justify-between"):
              with ui.label("TOTAL COST").classes(add="w-fit rounded p-2 shadow-md shadow-[#07004d] text-xl text-bold text-black"):
                ui.label(f"{sum([medicine['received_price'] for medicine in self.medicines if not medicine['cancelled']]):,.2f} TZS").classes(add="inline ml-2 text-sky-700")
            #Buttons
            with html.div().classes(add="w-full lg:w-fit flex flex-row justify-center lg:justify-between gap-5"):
              ui.button(text="RECEIVE",color="",on_click=lambda e:self.RequisitionConfirmationDialog(requisition=requisition,receive=True)).props(add="glossy").classes(add="bg-harmony text-yellow-500 text-bold text-xl")
      
        elif requisition["initiated"]:
          #Small screen
          with ui.scroll_area().classes(add="lg:hidden grow w-full py-3 rounded shadow-md shadow-[#07004d]"):
            for medicine in self.medicines:
              with ui.button(color="",on_click=lambda e:self.MedicineDialog(medicine=[medicine for medicine in self.medicines if medicine["requisition_medicine_id"] == e.sender.props["id"].lower()][0],requisition=requisition,ordered=requisition["placed"])).props(add=f"elevated id={medicine['requisition_medicine_id']}").classes(add=f"w-full h-fit p-1 bg-sky-100 shadow-md shadow-[#07004d] flex flex-row"):
                #Index
                ui.label(str(self.medicines.index(medicine) + 1)).classes(add="size-8 rounded-full ring-1 ring-offset-1 ring-[#07004d] bg-harmony flex flex-col ga-2 justify-center text-sky-300 text-lg font-semibold")
                #Details
                with html.div().classes(add="grow ml-1 h-full flex flex-col gap-1"):
                  #Identity
                  with html.section().classes(add="w-full p1-2 shadow-xs shadow-[#07004d] font-semibold"):
                    with html.div().classes(add=""):
                      ui.label(medicine['name']).classes(add="text-start text-lg")
                    with html.section().classes(add="w-full px-1 flex flex-row justify-between font-semibold"):
                      ui.label(medicine['type']).classes(add="text-start md:text-end italic text-gray-600")
                      ui.label(self.uom(medicine)).classes(add="text-start md:text-end italic text-gray-600")
                      ui.label(f"{medicine['unit_price']} TZS/Unit").classes(add="text-start md:text-end italic text-gray-600")
                                
                  #Stock details
                  with html.section().classes(add="w-full px-1 grid grid-cols-3 justify-start font-semibold"):
                    #Start balance
                    with ui.label("START BALANCE").classes(add="col-start-1 col-span-2 row-start-1 text-start text-gray-700"):
                      ui.label(f"{medicine["initial_store_balance"]:,}").classes(add="inline ml-1 text-sky-600")
                    #Closing balance
                    with ui.label("CLOSING BALANCE").classes(add="col-start-1 col-span-2 row-start-2 text-start text-gray-700"):
                      ui.label(f"{medicine["physical_count"]:,}").classes(add="inline ml-1 text-sky-600")
                    #AMC
                    with ui.label("AMC").classes(add="col-start-3 row-start-1 text-end text-gray-700"):
                      ui.label(f"{medicine["amc"]:,}").classes(add="inline ml-1 text-sky-600")
                    #MOS
                    with ui.label("MOS").classes(add="col-start-3 row-start-2 text-end text-gray-700"):
                      ui.label(f"{self.mos(medicine):,}").classes(add="inline ml-1 text-sky-600")
    
                  #Current Order
                  with html.div().classes(add="w-full px-1 flex flex-row justify-between font-semibold"):
                    #Order Amount
                    with ui.label("ORDER QTY").classes(add="col-start-1 row-start-1 text-start text-gray-700"):
                      ui.label(f"{medicine["ordered_amount"]:,}").classes(add="inline ml-1 text-sky-600")
                    #Total cost
                    with ui.label("TOTAL COST").classes(add="col-start-1 row-start-1 text-start text-gray-700"):
                      ui.label(f"{medicine['ordered_price']:,.2f}").classes(add="inline ml-1 text-sky-600")
          
          #Large Screen
          ui.aggrid(
            {
              "columnDefs":[
                {"headerName":"S/No","field":"sno","width":100},
                {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
                {"headerName":"TYPE","field":"type"},
                {"headerName":"UoM","field":"uom","width":170},
                {"headerName":"START BALANCE","field":"start_balance"},
                {"headerName":"AMC","field":"amc","width":120},
                {"headerName":"CLOSING BALANCE","field":"closing_balance"},
                {"headerName":"MOS","field":"mos","width":120},
                {"headerName":"ORDER AMOUNT","field":"order_amount"},
                {"headerName":"UNIT PRICE (TZS)","field":"unit_price"},
                {"headerName":"TOTAL PRICE (TZS)","field":"cost"}
              ],
              "rowData":[
                {
                  "sno":self.medicines.index(medicine) + 1,
                  "name":medicine["name"],
                  "type":medicine["type"],
                  "uom":self.uom(medicine),
                  "start_balance":medicine["initial_store_balance"],
                  "amc":medicine["amc"],
                  "closing_balance":medicine["physical_count"],
                  "mos":self.mos(medicine),
                  "order_amount":medicine["ordered_amount"],
                  "unit_price":medicine["unit_price"],
                  "cost":f"{medicine['ordered_price']:,.2f}"
                }
                for medicine in self.medicines
              ]
            },theme="quartz"
            ).style(add="height:350px").classes(add="lg-show grow w-full bg-sky-300 uppercase").on("cellClicked",lambda e:self.MedicineDialog(medicine=[medicine for medicine in self.medicines if medicine["name"] == e.args["data"]["name"].lower()][0],requisition=requisition,ordered=requisition["placed"]))
          #Totals & Buttons
          with html.div().classes(add="w-full p-2 flex flex-row justify-between gap-5"):
            #Totals
            with html.div().classes(add="w-full lg:w-fit flex flex-row justify-center lg:justify-between"):
              with ui.label("TOTAL COST").classes(add="w-fit rounded p-2 shadow-md shadow-[#07004d] text-xl text-bold text-black"):
                ui.label(f"{sum([medicine['ordered_price'] for medicine in self.medicines if not medicine['cancelled']]):,.2f} TZS").classes(add="inline ml-2 text-sky-700")
            #Buttons
            with html.div().classes(add="w-full lg:w-fit flex flex-row justify-center lg:justify-between gap-5"):
              ui.button(text="ORDER",color="",on_click=lambda e:self.RequisitionConfirmationDialog(requisition=requisition,order=True)).props(add="glossy").classes(add="bg-harmony text-yellow-500 text-bold text-xl")
              ui.button(text="CANCEL",color="",on_click=lambda e:self.RequisitionConfirmationDialog(requisition=requisition,cancel=True)).props(add="glossy").classes(add="bg-harmony text-rose-500 text-bold text-xl")
      
        else:
          #Small screen
          with ui.scroll_area().classes(add="lg:hidden grow w-full py-3 rounded shadow-md shadow-[#07004d]"):
            for medicine in self.medicines:
              with ui.button(color="",on_click=lambda e:self.MedicineDialog(medicine=[medicine for medicine in self.medicines if medicine["requisition_medicine_id"] == e.sender.props["id"].lower()][0],requisition=requisition,ordered=requisition["placed"])).props(add=f"elevated id={medicine['requisition_medicine_id']}").classes(add=f"w-full h-fit p-1 bg-sky-100 shadow-md shadow-[#07004d] flex flex-row"):
                #Index
                ui.label(str(self.medicines.index(medicine) + 1)).classes(add="size-8 rounded-full ring-1 ring-offset-1 ring-[#07004d] bg-harmony flex flex-col ga-2 justify-center text-sky-300 text-lg font-semibold")
                #Details
                with html.div().classes(add="grow ml-1 h-full flex flex-col gap-1"):
                  #Identity
                  with html.section().classes(add="w-full p1-2 shadow-xs shadow-[#07004d] font-semibold"):
                    with html.div().classes(add=""):
                      ui.label(medicine['name']).classes(add="text-start text-lg")
                    with html.section().classes(add="w-full px-1 flex flex-row justify-between font-semibold"):
                      ui.label(medicine['type']).classes(add="text-start md:text-end italic text-gray-600")
                      ui.label(self.uom(medicine)).classes(add="text-start md:text-end italic text-gray-600")
                      ui.label(f"{medicine['unit_price']:,.2f} TZS/Unit").classes(add="text-start md:text-end italic text-gray-600")
                                
                  #Stock details
                  with html.section().classes(add="w-full px-1 grid grid-cols-3 justify-start font-semibold"):
                    #Start balance
                    with ui.label("START BALANCE").classes(add="col-start-1 col-span-2 row-start-1 text-start text-gray-700"):
                      ui.label(f"{medicine["initial_store_balance"]:,.0f}").classes(add="inline ml-1 text-sky-600")
                    #Closing balance
                    with ui.label("CLOSING BALANCE").classes(add="col-start-1 col-span-2 row-start-2 text-start text-gray-700"):
                      ui.label(f"{medicine["physical_count"]:,.0f}").classes(add="inline ml-1 text-sky-600")
                    #AMC
                    with ui.label("AMC").classes(add="col-start-3 row-start-1 text-end text-gray-700"):
                      ui.label(f"{medicine["amc"]:,.0f}").classes(add="inline ml-1 text-sky-600")
                    #MOS
                    with ui.label("MOS").classes(add="col-start-3 row-start-2 text-end text-gray-700"):
                      ui.label(f"{self.mos(medicine):,}").classes(add="inline ml-1 text-sky-600")
    
                  #Current Order
                  with html.div().classes(add="w-full px-1 flex flex-row justify-between font-semibold"):
                    #Order Amount
                    with ui.label("ORDER QTY").classes(add="col-start-1 row-start-1 text-start text-gray-700"):
                      ui.label(f"{medicine["ordered_amount"]:,}").classes(add="inline ml-1 text-sky-600")
                    #Total cost
                    with ui.label("TOTAL COST").classes(add="col-start-1 row-start-1 text-start text-gray-700"):
                      ui.label(f"{medicine['ordered_price']:,.2f}").classes(add="inline ml-1 text-sky-600")
          
          #Large Screen
          ui.aggrid(
            {
              "columnDefs":[
                {"headerName":"S/No","field":"sno","width":100},
                {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
                {"headerName":"TYPE","field":"type"},
                {"headerName":"UoM","field":"uom","width":170},
                {"headerName":"START BALANCE","field":"start_balance"},
                {"headerName":"AMC","field":"amc","width":120},
                {"headerName":"CLOSING BALANCE","field":"closing_balance"},
                {"headerName":"MOS","field":"mos","width":120},
                {"headerName":"ORDER AMOUNT","field":"order_amount"},
                {"headerName":"UNIT PRICE (TZS)","field":"unit_price"},
                {"headerName":"TOTAL PRICE (TZS)","field":"cost"}
              ],
              "rowData":[
                {
                  "sno":self.medicines.index(medicine) + 1,
                  "name":medicine["name"],
                  "type":medicine["type"],
                  "uom":self.uom(medicine),
                  "start_balance":medicine["initial_store_balance"],
                  "amc":medicine["amc"],
                  "closing_balance":medicine["physical_count"],
                  "mos":self.mos(medicine),
                  "order_amount":medicine["ordered_amount"],
                  "unit_price":medicine["unit_price"],
                  "cost":f"{medicine['ordered_price']:,.2f}"
                }
                for medicine in self.medicines
              ]
            },theme="quartz"
            ).style(add="height:350px").classes(add="lg-show grow w-full bg-sky-300 uppercase").on("cellClicked",lambda e:self.MedicineDialog(medicine=[medicine for medicine in self.medicines if medicine["name"] == e.args["data"]["name"].lower()][0],requisition=requisition,ordered=requisition["placed"]))
          #Totals & Buttons
          with html.div().classes(add="w-full p-2 flex flex-row justify-between gap-5"):
            #Totals
            with html.div().classes(add="w-full lg:w-fit flex flex-row justify-center lg:justify-between"):
              with ui.label("TOTAL COST").classes(add="w-fit rounded p-2 shadow-md shadow-[#07004d] text-xl text-bold text-black"):
                ui.label(f"{sum([medicine['ordered_price'] for medicine in self.medicines if not medicine['cancelled']]):,.2f} TZS").classes(add="inline ml-2 text-sky-700")
            #Buttons
            with html.div().classes(add="w-full lg:w-fit flex flex-row justify-center lg:justify-between gap-5"):
              ui.button(text="INITIATE",color="",on_click=lambda e:self.RequisitionConfirmationDialog(requisition=requisition,initiate=True)).props(add="glossy").classes(add="bg-harmony text-yellow-500 text-bold text-xl")
              ui.button(text="CANCEL",color="",on_click=lambda e:self.RequisitionConfirmationDialog(requisition=requisition,cancel=True)).props(add="glossy").classes(add="bg-harmony text-rose-500 text-bold text-xl")
    
  def MedicineDialog(self,medicine:dict,requisition:dict,ordered:bool):
    """A method to display medicine dialog"""
    #ALERTS
    if not ordered and self.mos(medicine) > 4:
      ui.notify(message="This item is overstocked!",type="warning",position="center")
    
    #DATA
    medicine = medicine
    medicine["transfer_balance"] = 0
    if not requisition["received"]:
      medicine["received_amount"] = medicine["ordered_amount"]
      medicine["received_price"] = medicine["ordered_price"]

    #MODS
    def display_units(amount=None):
      if not amount:
        return

      #Update units display
      units_display.clear()
      with units_display.classes(add="animated__animate animate__fadeIn animate__slow"):
        if amount:
          ui.label(f"{round(int(amount)/medicine['order_unit_size']):,}").classes(add="text-center text-sky-700")
        else:
          ui.label(str(0)).classes(add="w-full text-center text-sky-700")
    
      #Update medicine dialog
      self.medicine_dialog.update()
    
    #UI
    with ui.dialog() as self.medicine_dialog,html.div().style(add=f"min-width:{ '50' if medicine['received'] else '60'}%;").classes(add="bg-sky-100 p-0.5"):
      #Title
      ui.label(medicine["name"]).classes(add="w-full bg-harmony p-1 rounded-t text-2xl lg:text-3xl text-bold text-center text-yellow-500 uppercase")
      #Separator
      ui.separator().classes(add="w-full bg-[#09026f]")
      
      #Updating received medicine
      if medicine["received"]:
        with html.div().classes(add="w-full p-3 flex flex-col gap-5"):
          #Transfer to dispensing store
          with ui.expansion(text="TRANSFER TO DISPENSING STORE").classes(add="w-full rounded shadow-md shadow-[#07004d]"):
            with html.div().classes(add="w-full bg-harmony flex flex-row justify-around gap-2 p-2"):
              with ui.label("STORE:").classes(add="bg-inherit text-center text-sky-300 text-bold text-xl lg:text-3xl"):
                ui.label(f"{medicine['store_balance']:,.0f}").classes(add="inline ml-0.5 bg-inherit text-yellow-500 text-bold text-xl lg:text-3xl")
              with ui.label("DISPENSING:").classes(add="bg-inherit text-center text-yellow-50 text-bold text-xl lg:text-3xl"):
                ui.label(f"{medicine['dispensing_balance']:,.0f}").classes(add="inline ml-0.5 bg-inherit text-yellow-500 text-bold text-xl lg:text-3xl")
            with html.div().classes(add="w-full flex flex-row justify-center gap-5 p-0.5"):
              ui.number(label=f"No of {medicine['order_unit']}s",min=1,max=medicine["store_balance"]).bind_value(medicine,"transfer_balance").props(add=f"{'' if medicine['store_balance'] else 'disable'} label-color='#07004d' input-class='font-medium'").classes(add="w-40 rounded shadow-md shadow-[#07004d] px-5 bg-sky-50 text-lg")
              ui.button(text="TRANSFER",color="",on_click=lambda e:self.update_medicine(medicine=medicine,requisition=requisition,transfer=True)).props(add=f"{'' if medicine['store_balance'] else 'disable'} glossy").classes(add="bg-harmony text-yellow-500 text-bold text-xl")
          
          #Physical count
          with ui.expansion(text="PHYSICAL COUNT").classes(add="w-full rounded shadow-md shadow-[#07004d]"):
            with html.div().classes(add="w-full bg-harmony flex flex-row justify-around gap-2 p-2"):
              with ui.label("STORE BALANCE:").classes(add="w-full bg-inherit text-center text-sky-300 text-bold text-xl lg:text-3xl"):
                ui.label(f"{medicine['store_balance']:,.0f}").classes(add="inline ml-0.5 bg-inherit text-yellow-500 text-bold text-xl lg:text-3xl")
              if medicine["physical_count_date"]:
                with ui.label().classes(add="w-full py-0 bg-inherit italic text-md text-center"):
                  html.span("Last physical count was").classes(add="text-sky-200")
                  html.span(f"{format_age(medicine['physical_count_date'])} ago").classes(add="ml-1 text-yellow-500")
            with html.div().classes(add="w-full flex flex-row justify-around gap-x-2 gap-y-5 p-0.5"):
              ui.number(label="MAIN STORE").bind_value(medicine,"store_balance").classes(add="w-40 rounded shadow-md shadow-[#07004d] px-5 bg-sky-50 text-lg")
              ui.number(label="DISPENSING STORE").bind_value(medicine,"dispensing_balance").classes(add="w-40 rounded shadow-md shadow-[#07004d] px-5 bg-sky-50 text-lg")
              ui.button(text="update count",color="",on_click=lambda e:self.update_medicine(medicine=medicine,requisition=requisition,count=True)).props(add="glossy").classes(add="bg-harmony text-yellow-500 text-bold text-xl")
       
      else:
        #Receive medicine
        if ordered:
          #Identity
          with html.section().classes(add="w-full p-2 flex flex-row justify-around gap-3 lg:gap-0"):
            ui.input(label="BRAND NAME").bind_value(medicine,"brand_name").classes(add="w-full lg:w-auto rounded shadow-md shadow-[#07004d] px-3 bg-white text-lg lg:text-xl uppercase")
            ui.input(label="MANUFACTURER").bind_value(medicine,"manufacturer").classes(add="w-full lg:w-auto rounded shadow-md shadow-[#07004d] px-3 bg-white text-lg lg:text-xl uppercase")
            ui.input(label="BATCH/LOT NO").bind_value(medicine,"batch_no").classes(add="w-full lg:w-auto rounded shadow-md shadow-[#07004d] px-3 bg-white text-lg lg:text-xl uppercase")
          #Dates
          with html.section().classes(add="w-full p-2 grid grid-cols-2 gap-3"):
            with ui.input(label="MFG DATE").props(add="readonly").classes(add="w-full shadow-md shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl") as mfg_date_display:
              with ui.dialog() as calendar:
                ui.date(mask='YYYY-MM-DD',on_change=calendar.close).props(add=f"bordered square today-btn color='harmony' event-color='orange' first-day-of-week='1' navigation-max-year-month='{datetime.now().strftime("%Y/%m")}'").bind_value(mfg_date_display).bind_value(medicine,"mfg_date")
                with mfg_date_display.add_slot("prepend"):
                  ui.icon("fas fa-cake-candles",color="").classes(add="text-harmony").on("click",calendar.open)
            with ui.input(label="EXPIRY DATE").props(add="id='readonly").classes(add="w-full rounded shadow-md shadow-[#07004d] px-3 bg-white text-lg lg:text-xl") as exp_date_display:
              with ui.dialog() as calendar:
                ui.date(mask='YYYY-MM-DD',on_change=calendar.close).props(add=f"bordered square today-btn color='harmony' event-color='orange' first-day-of-week='1' navigation-min-year-month='{datetime.now().strftime("%Y/%m")}'").bind_value(exp_date_display).bind_value(medicine,"expire_date")
                with exp_date_display.add_slot("prepend"):
                  ui.icon("fas fa-cake-candles",color="").classes(add="text-harmony").on("click",calendar.open)
          #Quantity
          with html.section().classes(add="w-full p-2 grid grid-cols-2  gap-3"):
            ui.number(label="RECEIVED QTY",placeholder=f"Ordered: {medicine['ordered_amount']:,.0f}").bind_value(medicine,"received_amount").classes(add="w-full shadow-md shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl")
            ui.number(label="RECEIVED COST",placeholder=f"Ordered: {medicine['ordered_price']:,.0f}").bind_value(medicine,"received_price").classes(add="w-full shadow-md shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl")
            ui.number(label="REJECTED QTY",placeholder=f"Ordered: {medicine['ordered_amount']:,.0f}").bind_value(medicine,"rejected_amount").classes(add="w-full shadow-md shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl")
            ui.number(label="REJECTED COST",placeholder=f"Ordered: {medicine['ordered_price']:,.0f}").bind_value(medicine,"rejected_price").classes(add="w-full shadow-md shadow-[#07004d] bg-white rounded px-2 text-lg lg:text-xl")
          #Button
          with html.div().classes(add="w-full py-2 flex flex-row justify-center"):
            ui.button(text="RECEIVE MEDICINE",color="",on_click=lambda e:self.update_medicine(medicine=medicine,requisition=requisition,receive=True)).classes(add="bg-harmony text-yellow-500 text-bold text-lg")
        
        #Edit medicine order
        else:
          #Header
          with html.div().classes(add="w-full bg-harmony flex flex-row justify-around gap-3 p-2 text-bold"):
            #Details
            with ui.label("UoM:").classes(add="text-sky-300 text-lg lg:text-xl"):
              ui.label(self.uom(medicine)).classes(add="inline ml-0.5 text-yellow-500 uppercase")
            with ui.label("BALANCE:").classes(add="text-sky-300 text-lg lg:text-xl"):
              ui.label(medicine["physical_count"]).classes(add="inline ml-0.5 text-yellow-500 uppercase")
            with ui.label("AMC:").classes(add="text-sky-300 text-lg lg:text-xl"):
              ui.label(medicine["amc"]).classes(add="inline ml-0.5 text-yellow-500 uppercase")
            with ui.label("MOS:").classes(add="text-sky-300 text-lg lg:text-xl"):
              ui.label(self.mos(medicine)).classes(add="inline ml-0.5 text-yellow-500 uppercase")
          
          #Ordering
          with html.div().classes(add="w-full p-2 flex flex-row justify-center lg:justify-around gap-5"):
            #Order amount
            ui.number(label=f"{medicine['order_unit']}s to order",min=1,on_change=lambda e:display_units(e.value)).bind_value(medicine,"ordered_amount").classes(add="w-36 rounded shadow-md shadow-[#07004d] px-3 bg-sky-50 text-lg lg:text-xl uppercase")
            #Units display
            with html.span().classes(add="px-1 rounded shadow-md shadow-[#07004d] flex flex-col text-lg lg:text-xl text-harmony font-semibold"):
              ui.label("UNITS").classes(add="w-full text-center")
              with html.span().classes(add="w-full") as units_display:
                display_units(medicine["ordered_amount"])
            #Unit cost
            ui.number(label="UNIT COST(TZS)",min=0,on_change=lambda e:self.medicine_dialog.update()).bind_value(medicine,"unit_price").classes(add="w-32 rounded shadow-md shadow-[#07004d] px-3 bg-sky-50 text-lg lg:text-xl uppercase")
            #Buttons
            if not (medicine["ordered"] and medicine["received"]):
              with html.div().classes(add="w-full lg:w-fit flex flex-row justify-center"):
                ui.button(text="order medicine",color="",on_click=lambda e:self.update_medicine(medicine=medicine,requisition=requisition,order=True)).props(add="glossy").classes(add="bg-harmony text-yellow-500 text-bold text-lg")

    self.medicine_dialog.open()


class StockAnalysisDisplay():
  """A class for UI and functionalities of stock analysis"""

  def __init__(self,requisitions=None):
    self.requisitions = requisitions

    #UI
    with html.div().classes(add="grow w-full flex flex-col"):
      #Separator
      for i in range(2):
        ui.separator().classes(add="w-full bg-[#09026f]")
      #Header
      with html.section().classes(add="w-full p-1 flex flex-row bg-harmony text-yellow-500"):
        with html.div().classes(add="rounded-t-md grow bg-inherit flex flex-row content-center"):
          ui.label("STOCK STATUS").classes(add="w-full rounded-t text-3xl text-bold")
      
      with html.div().classes(add="grow w-full p-1 flex flex-col justify-center content-center") as self.stocks_panel:
        if self.requisitions:
          self.StocksPanel()
        else:
          ui.label("No received requisition!").classes(add="m-5 text-rose-500 text-2xl lg:text-3xl italic font-semibold fa-fade")
  
  #FUNCTIONALITES
  def amc(self,medicine:dict):
    """A method that calculates average monthly consumption of medicine"""

    initial_amount,final_amount = medicine["initial_store_balance"],medicine["store_balance"] + medicine["dispensing_balance"]
    duration = (datetime.now().date() - medicine["received_on"].date()).days/30
    
    return math.ceil((initial_amount-final_amount)/duration) if duration else 0
  
  def dos(self,medicine:dict):
    "A method to that returns a calculated number of days of stock based on data from medicine input"

    final_amount = medicine["store_balance"] + medicine["dispensing_balance"]
    amc = self.amc(medicine)
    
    if medicine["initial_store_balance"]:
      if amc:
        return round((final_amount/amc)*30)
      else:
        return 150
    else:
      return 0

  def mos(self,medicine:dict):
    """A method that returns value of mos based on the input values"""
    final_amount = medicine["store_balance"] + medicine["dispensing_balance"]
    amc = self.amc(medicine)
    
    if medicine["initial_store_balance"]:
      if amc:
        return round(final_amount/amc)
      else:
        return 2
    else:
      return 0
  
  def stock(self):
    """A method that returns a dictionary with stock details"""
    medicines = self.requisition["medicines"]
    
    no_demand,overstocks,understocks,stockouts,stocked = [],[],[],[],[]

    for medicine in medicines:
      amc = self.amc(medicine=medicine)
      mos = self.mos(medicine=medicine)
      dos = self.dos(medicine=medicine)

      if amc > 0:
        overstocks.append(medicine) if mos > 4 else understocks.append(medicine) if ((mos > 0 and mos < 2) or (mos == 0 and dos > 0)) else stockouts.append(medicine) if mos == 0 else stocked.append(medicine)
      else:
        no_demand.append(medicine)
      
    return {"no_demand":no_demand,"overstocks":overstocks,"stocked":stocked,"understocks":understocks,"stockouts":stockouts}

  #DISPLAYS
  def StocksPanel(self):
    """A Main display"""
    #DATA
    stocks = self.stock()
    stockouts,understocks,stocked,overstocks,no_demand = stocks["stockouts"],stocks["understocks"],stocks["stocked"],stocks["overstocks"],stocks["no_demand"]
    #UI
    self.stocks_panel.clear()
    with self.stocks_panel:
      with html.div().classes(add="grow w-full lg:p-1 flex flex-row lg:flex-col justify-between gap-1 lg:gap-3"):
        #Adequate
        with ui.button(color="green-600",on_click=lambda e:self.StocksDialog(stocked=stocked)).props(add="dense glossy padding='2px 2px'").classes(add="w-full lg:w-auto rounded") as stocked_button:
          with stocked_button.add_slot("default"):
            with html.span().classes(add="w-full flex flex-row justify-between gap-5 bg-gray-900 rounded p-2"):
              ui.label("ADEQUATE STOCKS").classes(add="bg-inherit text-green-600 font-medium text-xl lg:text-2xl")
              ui.badge(text=str(len(stocked)),color="").classes(add="bg-inherit flex flex-col justify-center size-8 rounded-full ring-1 ring-green-600 shadow-md shadow-green-600 text-green-600 text-2xl text-bold")
        #Stockouts
        with ui.button(color="red-500",on_click=lambda e:self.StocksDialog(stockouts=stockouts)).props(add="dense glossy padding='2px 2px'").classes(add="w-[49%] lg:w-auto inline rounded") as stockouts_button:
          with stockouts_button.add_slot("default"):
            with html.span().classes(add="w-full flex flex-row justify-between gap-5 bg-gray-900 rounded p-2"):
              ui.label("STOCKOUTS").classes(add="bg-inherit text-red-500 font-medium text-xl lg:text-2xl")
              ui.badge(text=str(len(stockouts)),color="").classes(add=f"bg-inherit flex flex-col justify-center size-8 rounded-full ring-1 ring-red-500 shadow-md shadow-red-500 text-red-500 text-xl lg:text-2xl text-bold {'fa-beat-fade' if stockouts else ''}")
        #Understocks
        with ui.button(color="yellow-400",on_click=lambda e:self.StocksDialog(understocks=understocks)).props(add="dense glossy padding='2px 2px'").classes(add="w-[49%] lg:w-auto inline rounded") as understocks_button:
          with understocks_button.add_slot("default"):
            with html.span().classes(add="w-full flex flex-row justify-between gap-5 bg-gray-900 rounded p-2"):
              ui.label("UNDERSTOCKS").classes(add="bg-inherit text-yellow-400 font-medium text-xl lg:text-2xl")
              ui.badge(text=str(len(understocks)),color="").classes(add=f"bg-inherit flex flex-col justify-center size-8 rounded-full ring-1 ring-yellow-400 shadow-md shadow-yellow-400 text-yellow-400 text-xl lg:text-2xl text-bold {'fa-beat-fade' if understocks else ''}")
        #Overstocks
        with ui.button(color="purple-500",on_click=lambda e:self.StocksDialog(overstocks=overstocks)).props(add="dense glossy padding='2px 2px'").classes(add="w-[49%] lg:w-auto rounded") as overstocks_button:
          with overstocks_button.add_slot("default"):
            with html.span().classes(add="w-full flex flex-row justify-between gap-5 bg-gray-900 rounded p-2"):
              ui.label("OVERSTOCKS").classes(add="bg-inherit text-purple-500 font-medium text-xl lg:text-2xl")
              ui.badge(text=str(len(overstocks)),color="").classes(add=f"bg-inherit flex flex-col justify-center size-8 rounded-full ring-1 ring-purple-500 shadow-md shadow-purple-500 text-purple-500 text-xl text-bold {'fa-beat-fade' if overstocks else ''}")
        #No Demand
        with ui.button(color="gray-400",on_click=lambda e:self.StocksDialog(no_demand=no_demand)).props(add="dense glossy padding='2px 2px'").classes(add="w-[49%] lg:w-auto rounded") as no_demand_button:
          with no_demand_button.add_slot("default"):
            with html.span().classes(add="w-full flex flex-row justify-between gap-5 bg-gray-900 rounded p-2"):
              ui.label("NO DEMAND").classes(add="bg-inherit text-gray-400 font-medium text-xl lg:text-2xl")
              ui.badge(text=str(len(no_demand)),color="").classes(add=f"bg-inherit flex flex-col justify-center size-8 rounded-full ring-1 ring-gray-500 shadow-md shadow-gray-500 text-gray-400 text-xl text-bold {'fa-beat-fade' if no_demand else ''}")
           
  def StocksDialog(self,no_demand=None,overstocks=None,stocked=None,understocks=None,stockouts=None):
    #DATA
    if no_demand or overstocks or stocked or understocks or stockouts:
      requisition = self.requisition
      medicines = no_demand if no_demand else stockouts if stockouts else understocks if understocks else stocked if stocked else overstocks if overstocks else []
    else:
      ui.notify(message=f"No {'undemanded items' if type(no_demand) is list else 'stockouts' if type(stockouts) is list else 'understocks' if type(understocks) is list else 'adequately stocked items' if type(stocked) is list else 'overstocks' if type(overstocks) is list else ''}!",type="info",position="top",color=f"{'red-600' if type(stockouts) is list else 'yellow-500' if type(understocks) is list else 'green-500' if type(stocked) is list else 'violet-500' if type(overstocks) is list else ''}")
      return
    
    #UI
    with ui.dialog().props(add="transition-show='jump-up' transition-hide='jump-down' transition-duration='500'") as self.stocks_dialog,html.div().style(add="min-width:100%;max-height:95%;").classes(add="bg-sky-100 p-0.5 flex flex-col"):
      #Dialog Header
      with html.div().classes(add="w-full flex flex-row place-center bg-harmony"):
        #Details
        with html.div().classes(add="grow bg-inherit flex-col flex lg:flex-row justify-between content-center lg:items-center pl-3"):
          #Title
          ui.label("NO DEMAND" if type(no_demand) is list else "OVERSTOCKS" if type(overstocks) is list else "ADEQUATELY STOCKED" if type(stocked) is list else "UNDERSTOCKS" if type(understocks) is list else "STOCKOUTS" if type(stockouts) is list else "").classes(add=f"text-{'red-600' if type(stockouts) == list else 'yellow-400' if type(understocks) is list else 'green-500' if type(stocked) == list else 'purple-600' if type(overstocks) == list else 'gray-300' if type(no_demand) == list else ''} text-2xl lg:text-3xl text-bold")
          #Requisition ID
          with ui.label("REQUISITION ID:").classes(add="w-full lg:w-auto font-medium text-sky-300 text-lg"):
            ui.label(requisition["requisition_id"]).classes(add="inline ml-0.5 text-yellow-500 text-bold uppercase")
          #Stock count
          with ui.label(f"ITEMS").classes(add="w-full lg:w-auto text-bold text-sky-300 text-lg"):
            ui.label(str(len(medicines))).classes(add="inline ml-1 text-yellow-500 uppercase")
        #Close button
        with html.div().classes(add="flex flex-col justify-center"):
          ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=self.stocks_dialog.close).classes(add="size-12 bg-inherit rounded-full text-red-600 text-bold text-base hover:scale-[1.1]")
      
      #Stocks Display
      with html.div().classes(add="grow w-full animate__animated animate__fadeIn animate__slow"):
        with html.div().classes(add="grow lg:hidden flex flex-col"):
          self.StockMedicinesMiniDisplay(no_demand=no_demand,overstocks=overstocks,stocked=stocked,understocks=understocks,stockouts=stockouts)
        with html.div().classes(add="grow lg-flex flex-col"):
          self.StocksAggrid(no_demand=no_demand,overstocks=overstocks,stocked=stocked,understocks=understocks,stockouts=stockouts)
    
    self.stocks_dialog.open()
  
  def StocksAggrid(self,stockouts=None,understocks=None,stocked=None,overstocks=None,no_demand=None):
    """"""
    #DATA
    medicines = stockouts if stockouts else understocks if understocks else stocked if stocked else overstocks if overstocks else no_demand if no_demand else []
    
    #UI
    if stockouts:
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/No","field":"sno","width":70},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
            {"headerName":"TYPE","field":"type","width":150},
            {"headerName":"UNIT","field":"unit","width":150},
            {"headerName":"BRAND NAME","field":"brand_name"},
            {"headerName":"MANUFACTURER","field":"manufacturer"},
            {"headerName":"AMC","field":"amc","width":150},
          ],
          "rowData":[
            {
              "sno":medicines.index(medicine) + 1,
              "name":medicine["name"],
              "type":medicine["type"],
              "unit":medicine["order_unit"],
              "brand_name":medicine["brand_name"] if medicine["brand_name"] else "---",
              "manufacturer":medicine["manufacturer"] if medicine["manufacturer"] else "---",
              "amc":f"{self.amc(medicine):,.0f}",
            }
            for medicine in medicines
          ]
        },theme="quartz"
        ).classes(add="w-full grow bg-sky-300 text-sm uppercase")
    
    elif understocks:
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/No","field":"sno","width":100},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
            {"headerName":"TYPE","field":"type","width":150},
            {"headerName":"UNIT","field":"unit","width":150},
            {"headerName":"BRAND NAME","field":"brand_name"},
            {"headerName":"MANUFACTURER","field":"manufacturer"},
            {"headerName":"BATCH NO","field":"batch_no"},
            {"headerName":"EXPIRY DATE","field":"expire_date","width":200},
            {"headerName":"AMC","field":"amc"},
            {"headerName":"MOS","field":"mos"},
            {"headerName":"STOCK DAYS","field":"dos"}
          ],
          "rowData":[
            {
              "sno":medicines.index(medicine) + 1,
              "name":medicine["name"],
              "type":medicine["type"],
              "unit":medicine["order_unit"],
              "brand_name":medicine["brand_name"] if medicine["brand_name"] else "---",
              "manufacturer":medicine["manufacturer"] if medicine["manufacturer"] else "---",
              "batch_no":medicine["batch_no"] if medicine["batch_no"] else "---",
              "expire_date":medicine["expire_date"].strftime("%b %Y") if medicine["expire_date"] else "---",
              "amc":f"{self.amc(medicine):,.0f}",
              "mos":f"{self.mos(medicine):,.0f}",
              "dos":self.dos(medicine)
            }
            for medicine in medicines
          ]
        },theme="quartz"
        ).style(add="height:350px").classes(add="grow w-full bg-sky-300 text-sm uppercase")
      
    elif stocked:
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/N","field":"sno","width":80},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
            {"headerName":"TYPE","field":"type","width":150},
            {"headerName":"UNIT","field":"unit","width":150},
            {"headerName":"BRAND NAME","field":"brand_name"},
            {"headerName":"MANUFACTURER","field":"manufacturer"},
            {"headerName":"BATCH NO","field":"batch_no"},
            {"headerName":"EXPIRY DATE","field":"expire_date","width":200},
            {"headerName":"AMC","field":"amc"},
            {"headerName":"MOS","field":"mos"},
            {"headerName":"STOCK DAYS","field":"dos"}
          ],
          "rowData":[
            {
              "sno":medicines.index(medicine) + 1,
              "name":medicine["name"],
              "type":medicine["type"],
              "unit":medicine["order_unit"],
              "brand_name":medicine["brand_name"] if medicine["brand_name"] else "---",
              "manufacturer":medicine["manufacturer"] if medicine["manufacturer"] else "---",
              "batch_no":medicine["batch_no"] if medicine["batch_no"] else "---",
              "expire_date":medicine["expire_date"].strftime("%b %Y") if medicine["expire_date"] else "---",
              "amc":f"{self.amc(medicine):,.0f}",
              "mos":f"{self.mos(medicine):,.0f}",
              "dos":f"{self.dos(medicine):,.0f}"
            }
            for medicine in medicines
          ]
        },theme="quartz"
        ).style(add="height:350px").classes(add="grow w-full bg-sky-300 text-sm uppercase")

    elif overstocks:
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/No","field":"sno","width":100},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
            {"headerName":"TYPE","field":"type","width":150},
            {"headerName":"UNIT","field":"unit","width":150},
            {"headerName":"BRAND NAME","field":"brand_name"},
            {"headerName":"MANUFACTURER","field":"manufacturer"},
            {"headerName":"BATCH NO","field":"batch_no"},
            {"headerName":"EXPIRY DATE","field":"expire_date","width":200},
            {"headerName":"AMC","field":"amc"},
            {"headerName":"MOS","field":"mos"}
          ],
          "rowData":[
            {
              "sno":medicines.index(medicine) + 1,
              "name":medicine["name"],
              "type":medicine["type"],
              "unit":medicine["order_unit"],
              "brand_name":medicine["brand_name"] if medicine["brand_name"] else "---",
              "manufacturer":medicine["manufacturer"] if medicine["manufacturer"] else "---",
              "batch_no":medicine["batch_no"] if medicine["batch_no"] else "---",
              "expire_date":medicine["expire_date"].strftime("%b %Y") if medicine["expire_date"] else "---",
              "amc":f"{self.amc(medicine):,.0f}",
              "mos":f"{self.mos(medicine):,.0f}"
            }
            for medicine in medicines
          ]
        },theme="quartz"
        ).style(add="height:350px").classes(add="grow w-full bg-sky-300 text-sm uppercase")
    
    elif no_demand:
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/No","field":"sno","width":100},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
            {"headerName":"TYPE","field":"type","width":150},
            {"headerName":"UNIT","field":"unit","width":150},
            {"headerName":"BRAND NAME","field":"brand_name"},
            {"headerName":"MANUFACTURER","field":"manufacturer"},
            {"headerName":"BATCH NO","field":"batch_no"},
            {"headerName":"EXPIRY DATE","field":"expire_date","width":200},
            {"headerName":"MOS","field":"mos"}
          ],
          "rowData":[
            {
              "sno":medicines.index(medicine) + 1,
              "name":medicine["name"],
              "type":medicine["type"],
              "unit":medicine["order_unit"],
              "brand_name":medicine["brand_name"] if medicine["brand_name"] else "---",
              "manufacturer":medicine["manufacturer"] if medicine["manufacturer"] else "---",
              "batch_no":medicine["batch_no"] if medicine["batch_no"] else "---",
              "expire_date":medicine["expire_date"].strftime("%b %Y") if medicine["expire_date"] else "---",
              "mos":f"{self.mos(medicine):,.0f}"
            }
            for medicine in medicines
          ]
        },theme="quartz"
        ).style(add="height:350px").classes(add="grow w-full bg-sky-300 text-sm uppercase")

  def StockMedicinesMiniDisplay(self,no_demand=None,overstocks=None,stocked=None,understocks=None,stockouts=None):

    #DATA
    medicines = stockouts if stockouts else understocks if understocks else stocked if stocked else overstocks if overstocks else no_demand if no_demand else []

    #UI
    with ui.scroll_area().classes(add="lg:hidden grow w-full rounded shadow-md shadow-[#07004d] py-3"):
      if no_demand:
        for medicine in medicines:
          with ui.button(color="").props(add=f"elevated id={medicine['requisition_medicine_id']}").classes(add=f"w-full h-fit p-1 bg-sky-100 shadow-md shadow-[#07004d] flex flex-row"):
            #Index
            ui.label(str(medicines.index(medicine) + 1)).classes(add="size-8 rounded-full ring-1 ring-offset-1 ring-[#07004d] bg-harmony flex flex-col justify-center text-sky-300 text-lg font-semibold")
            #Details
            with html.div().classes(add="grow ml-1 h-full flex flex-col gap-1"):
              #Identity
              with html.section().classes(add="w-full px-1 flex flex-col md:flex-row justify-between font-semibold"):
                ui.label(medicine['name']).classes(add="text-start text-lg")
              
              #Stock details
              with html.section().classes(add="w-full px-1 flex flex-row justify-between gap-3 font-semibold"):
                ui.label(medicine['type']).classes(add="text-start md:text-end italic text-gray-700")
                with ui.label("MOS").classes(add="text-gray-700"):
                  ui.label(f"{self.mos(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")

              #Stats
              with html.div().classes(add="w-full px-1 flex flex-row justify-between font-semibold"):
                with ui.label("MAIN STORE").classes(add="text-gray-700"):
                  ui.label(f"{medicine['store_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("DISPENSING STORE").classes(add="text-gray-700"):
                  ui.label(f"{medicine['dispensing_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")

      if overstocks:
        for medicine in medicines:
          with ui.button(color="").props(add=f"elevated id={medicine['requisition_medicine_id']}").classes(add=f"w-full h-fit p-1 bg-sky-100 shadow-md shadow-[#07004d] flex flex-row"):
            #Index
            ui.label(str(medicines.index(medicine) + 1)).classes(add="size-8 rounded-full ring-1 ring-offset-1 ring-[#07004d] bg-harmony flex flex-col justify-center text-sky-300 text-lg font-semibold")
            #Details
            with html.div().classes(add="grow ml-1 h-full flex flex-col gap-1"):
              #Identity
              with html.section().classes(add="w-full px-1 flex flex-col md:flex-row justify-between font-semibold"):
                ui.label(medicine['name']).classes(add="text-start text-lg")
              
              #Stock details
              with html.section().classes(add="w-full px-1 flex flex-row justify-between gap-3 font-semibold"):
                ui.label(medicine['type']).classes(add="text-start md:text-end italic text-gray-700")
                with ui.label("AMC").classes(add="text-gray-700"):
                  ui.label(f"{self.amc(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("MOS").classes(add="text-gray-700"):
                  ui.label(f"{self.mos(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")

              #Stats
              with html.div().classes(add="w-full px-1 flex flex-row justify-between font-semibold"):
                with ui.label("MAIN STORE").classes(add="text-gray-700"):
                  ui.label(f"{medicine['store_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("DISPENSING STORE").classes(add="text-gray-700"):
                  ui.label(f"{medicine['dispensing_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")

      if stocked:
        for medicine in medicines:
          with ui.button(color="").props(add=f"elevated id={medicine['requisition_medicine_id']}").classes(add=f"w-full h-fit p-1 bg-sky-100 shadow-md shadow-[#07004d] flex flex-row"):
            #Index
            ui.label(str(medicines.index(medicine) + 1)).classes(add="size-8 rounded-full ring-1 ring-offset-1 ring-[#07004d] bg-harmony flex flex-col justify-center text-sky-300 text-lg font-semibold")
            #Details
            with html.div().classes(add="grow ml-1 h-full flex flex-col gap-1"):
              #Identity
              with html.section().classes(add="w-full px-1 flex flex-col md:flex-row justify-between font-semibold"):
                ui.label(medicine['name']).classes(add="text-start text-lg")
              
              #Stock details
              with html.section().classes(add="w-full px-1 flex flex-row justify-between gap-3 font-semibold"):
                ui.label(medicine['type']).classes(add="text-start md:text-end italic text-gray-700")
                with ui.label("AMC").classes(add="text-gray-700"):
                  ui.label(f"{self.amc(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("MOS").classes(add="text-gray-700"):
                  ui.label(f"{self.mos(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")

              #Stats
              with html.div().classes(add="w-full px-1 flex flex-row justify-between font-semibold"):
                with ui.label("MAIN STORE").classes(add="text-gray-700"):
                  ui.label(f"{medicine['store_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("DISPENSING STORE").classes(add="text-gray-700"):
                  ui.label(f"{medicine['dispensing_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")

      if understocks:
        for medicine in medicines:
          with ui.button(color="").props(add=f"elevated id={medicine['requisition_medicine_id']}").classes(add=f"w-full h-fit p-1 bg-sky-100 shadow-md shadow-[#07004d] flex flex-row"):
            #Index
            ui.label(str(medicines.index(medicine) + 1)).classes(add="size-8 rounded-full ring-1 ring-offset-1 ring-[#07004d] bg-harmony flex flex-col justify-center text-sky-300 text-lg font-semibold")
            #Details
            with html.div().classes(add="grow ml-1 h-full flex flex-col gap-1"):
              #Identity
              with html.section().classes(add="w-full px-1 flex flex-col md:flex-row justify-between font-semibold"):
                ui.label(medicine['name']).classes(add="text-start text-lg")
              
              #Stock details
              with html.section().classes(add="w-full px-1 flex flex-row justify-between gap-3 font-semibold"):
                ui.label(medicine['type']).classes(add="text-start md:text-end italic text-gray-700")
                with ui.label("AMC").classes(add="text-gray-700"):
                  ui.label(f"{self.amc(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("MOS").classes(add="text-gray-700"):
                  ui.label(f"{self.mos(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("DOS").classes(add="text-gray-700"):
                  ui.label(f"{self.dos(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")

              #Stats
              with html.div().classes(add="w-full px-1 flex flex-row justify-between font-semibold"):
                with ui.label("MAIN STORE").classes(add="text-gray-700"):
                  ui.label(f"{medicine['store_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("DISPENSING STORE").classes(add="text-gray-700"):
                  ui.label(f"{medicine['dispensing_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")

      if stockouts:
        for medicine in medicines:
          with ui.button(color="").props(add=f"elevated id={medicine['requisition_medicine_id']}").classes(add=f"w-full h-fit p-1 bg-sky-100 shadow-md shadow-[#07004d] flex flex-row"):
            #Index
            ui.label(str(medicines.index(medicine) + 1)).classes(add="size-8 rounded-full ring-1 ring-offset-1 ring-[#07004d] bg-harmony flex flex-col justify-center text-sky-300 text-lg font-semibold")
            #Details
            with html.div().classes(add="grow ml-1 h-full flex flex-col gap-1"):
              #Identity
              with html.section().classes(add="w-full px-1 flex flex-col md:flex-row justify-between font-semibold"):
                ui.label(medicine['name']).classes(add="text-start text-lg")
              
              #Stock details
              with html.section().classes(add="w-full px-1 flex flex-row justify-between gap-3 font-semibold"):
                ui.label(medicine['type']).classes(add="text-start md:text-end italic text-gray-700")
                with ui.label("AMC").classes(add="text-gray-700"):
                  ui.label(f"{self.amc(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("MOS").classes(add="text-gray-700"):
                  ui.label(f"{self.mos(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("DOS").classes(add="text-gray-700"):
                  ui.label(f"{self.dos(medicine):,.0f}").classes(add="inline ml-1 text-sky-700")

              #Stats
              with html.div().classes(add="w-full px-1 flex flex-row justify-between font-semibold"):
                with ui.label("MAIN STORE").classes(add="text-gray-700"):
                  ui.label(f"{medicine['store_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")
                with ui.label("DISPENSING STORE").classes(add="text-gray-700"):
                  ui.label(f"{medicine['dispensing_balance']:,.0f}").classes(add="inline ml-1 text-sky-700")

class FacilityFormulary():
  def __init__(self,user,formulary=None,parent=None):
    #DATA
    self.user = user
    self.initial_data()

    #UI
    with html.div().classes(add="grow w-full flex flex-col"):
      #Separator
      for i in range(2):
        ui.separator().classes(add="lg-show w-full bg-[#09026f]")
      #Header
      with html.section().classes(add="w-full p-1 rounded-t lg:rounded-0 flex flex-row bg-harmony text-yellow-500"):
        with html.div().classes(add="rounded-t-md grow bg-inherit flex flex-row content-center gap-5 lg:gap-1"):
          ui.label("FORMULARY").classes(add="lg:order-2 grow rounded-t text-2xl lg:text-3xl text-bold")
          ui.button(icon="fa-solid fa-circle-plus",color="",on_click=self.MedicineDialog).classes(add="lg:order-1 size-8 rounded-[50%] bg-inherit text-yellow-500")
          #ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=self.parent.formulary_dialog.close if self.parent.formulary_dialog else None).classes(add="lg:hidden size-8 bg-inherit text-red-500")
      
      #Body
      with html.div().classes(add="grow w-full flex flex-col justify-center content-center") as self.formulary_panel:
        if self.medicines:
          self.FormularyAggrid(self.medicines)
          
        else:
          with html.div().classes(add=""):
            ui.label("There is no hospital formulary!").classes(add="m-5 text-rose-500 text-center text-2xl lg:text-3xl italic font-semibold fa-fade")
            ui.label("Create a formulary by clicking a + button").classes(add="text-center text-rose-400 text-xl lg:text-2xl")

  #FUNCTIONALITIES
  def initial_data(self):
    self.medicines = get_formulary()
    self.template_medicines = get_formulary_medicines()

  def retrieve_medicine(self,medicine:str):
    """A method that retrieves service details and populate details in ServiceDetailsForm"""
    if not medicine:
      return
    
    medicine = get_formulary_medicine(medicine.lower())
    medicine["payment"] = self.pricings(medicine)
    
    self.MedicineDetailsForm(medicine)


  def pricings(self,medicine:dict):
    """Returns a namedtuple object with prices of a 'medicine'"""

    for scheme in medicine["schemes"]:
      for pricing in scheme["prices"]:
        pricing["scheme_item_code"] = scheme["scheme_item_code"]
        pricing["restricted"] = scheme["restricted"]
    
    output = {scheme["scheme_name"]:[pricing for pricing in scheme["prices"] if pricing["active"]][0] for scheme in medicine["schemes"] if scheme.get("active")}
    output["logger"] = self.user.username
    output["medicine_id"] = medicine["medicine_id"]
    if "nhif" in output:
      output["insured"] = True
    else:
      output["insured"] = False
      output["nhif"] = {
        "scheme_id":f"cash-{medicine['medicine_id'].lower()}",
        "scheme_item_code":"",
        "copayment":False,
        "price_range":False,
        "min":0,
        "max":0,
        "standard":0,
        "priority":0,
        "topup":0
      }

    return output

  def update_formulary(self,data,edit:bool=False,delete:bool=False):
    """"""

    data = {key:value.lower() for key,value in data.items() if type(value) == str}

    if edit:
      status = update_formulary(medicine=data)
    elif delete:
      status = update_formulary(medicine=data,delete=True)
    else:
      status = register_formulary([data])

    ui.notify(message=status["message"],type=status["type"],position=status["position"])
  
    self.medicines = get_formulary()
    self.FormularyAggrid(self.medicines)
    self.medicine_dialog.close()

  #DISPLAYS
  def FormularyAggrid(self,formulary:list[dict]):
    """"""
    #FXS
    def Status(medicine,lg:bool=False):
      _status = medicine["active"]
      status = ""
      if lg:
        if _status:
          status = "<span class='text-green-600 text-bold' >Active</span>"
        else:
          status = "<span class='text-red-600 text-bold' >Inactive</span>"
      else:
        if _status:
          status = "<span class='fa-solid fa-circle-dot text-green-600 text-bold' ></span>"
        else:
          status = "<span class='fa-solid fa-circle-dot text-red-600 text-bold' ></span>"
      
      return status

    def MiniPayment(medicine):
      pricings = self.pricings(medicine)
      pricings.pop("logger")
      pricings.pop("medicine_id")
      pricings.pop("insured")
      return f"<div class='grid grid-cols-2 gap-2 text-bold uppercase'>{''.join([f'<div class="w-full text-center {'col-start-1 text-harmony' if scheme == 'cash' else 'col-start-2 text-yellow-700'}">{scheme}</div>' for scheme,pricing in pricings.items() if pricing['standard'] or pricing["price_range"]])}</div"
    
    def Payment(medicine:dict,cash:bool=False,nhif:bool=False):
      def _format_price(price):
        return f"{price:,.2f}"

      pricings = self.pricings(medicine)
      if cash:
        price = pricings.get("cash")
        if price["price_range"]:
          return f"<div class='text-harmony font-semibold'>{price['min']:,.2f} - {price['max']:,.2f}</div>"
        else:
          return f"<div class='text-harmony font-semibold'>{price['standard']:,.2f}</div>"
      
      if nhif:
        if "nhif" in pricings:
          price = pricings.get("nhif")
          return f"<div class='grid grid-cols-2 gap-5 font-semibold'><div class='grid grid-cols-2 gap-1' ><span class='text-yellow-800' >STANDARD</span><span class='justify-self-end' >{_format_price(price['standard']) if price['standard'] else '---'}</span></div><div class='grid grid-cols-2 gap-1' ><span class='text-yellow-800' >PRIORITY</span><span class='justify-self-end' >{_format_price(price['priority']) if price['priority'] else '---'}</span></div></div>"
        else:
          return f"<div class='grid grid-cols-2 gap-3 font-semibold'><div class='grid grid-cols-2 gap-1' ><span class='text-yellow-800' >STANDARD</span><span class='justify-self-end' >---</span></div><div class='grid grid-cols-2 gap-1' ><span class='text-yellow-800' >PRIORITY</span><span class='justify-self-end' >---</span></div></div>"

    #UI
    self.formulary_panel.clear()
    with self.formulary_panel.classes(add=""):
      #Small Screen
      ui.aggrid(
        options={
          "columnDefs":[
            {"headerName":"","field":"status","width":40},
            {"headerName":"NAME","field":"name","sortable":True,"filter":True,"floatingFilter":True,"width":500},
            {"headerName":"TYPE","field":"type","width":200},
            {"headerName":"","field":"prices"}
          ],
          "rowData":[
            {
              "name":medicine["name"].upper(),
              "status":Status(medicine),
              "type":medicine["type"].title(),
              "prices":MiniPayment(medicine),
              "medicine_id":medicine["medicine_id"]
            } for medicine in formulary
          ]
        },
        theme="quartz",
        html_columns=[0,3]
      ).classes(add="lg:hidden grow w-full bg-inherit text-sm animate__animated animate__fadeIn").on("cellClicked",lambda e:self.MedicineDialog(medicine=[medicine for medicine in formulary if medicine['medicine_id'] == e.args['data']['medicine_id'].lower()][0]))

      #Large Screen
      ui.aggrid(
        options={
          "columnDefs":[
            {"headerName":"","field":"sno","width":75},
            {"headerName":"NAME","field":"name","sortable":True,"filter":True,"floatingFilter":True,"width":500},
            {"headerName":"TYPE","field":"type","width":150},
            {"headerName":"LEVEL","field":"prescription_level","width":100},
            {"headerName":"STATUS","field":"status","width":100},
            {"headerName":"CASH (TZS)","field":"cash_prices","width":150},
            {"headerName":"NHIF PRICES","field":"nhif_prices","width":500}
          ],
          "rowData":[
            {
              "sno":formulary.index(medicine) + 1,
              "name":medicine["name"].upper(),
              "status":Status(medicine=medicine,lg=True),
              "type":medicine["type"].upper(),
              "prescription_level":medicine["prescription_level"].upper() if medicine["prescription_level"] else "-",
              "cash_prices":Payment(medicine=medicine,cash=True),
              "nhif_prices":Payment(medicine=medicine,nhif=True),
              "medicine_id":medicine["medicine_id"]
            } for medicine in formulary
          ]
        },
        theme="quartz",
        html_columns=[4,5,6]
      ).classes(add="lg-show grow w-full bg-inherit text-sm animate__animated animate__fadeIn").on("cellClicked",lambda e:self.MedicineDialog(medicine=[medicine for medicine in formulary if medicine['medicine_id'] == e.args['data']['medicine_id'].lower()][0]))

  def MedicineDialog(self,medicine:dict|None=None):
    """A method to display dialog for medicine editing"""
    #DATA
    if medicine:
      medicine["payment"] = self.pricings(medicine=medicine)

    # UI
    with ui.dialog().props(add="transition-show='jump-up' transition-hide='jump-down' transition-duration='500'") as self.medicine_dialog,html.div().style(add="min-width:40%;min-height:70%;").classes(add="p-0.5 rounded bg-sky-100 flex flex-col"):
      #Header
      with html.div().classes(add="bg-harmony rounded-t p-1 flex flex-row justify-between"):
        ui.label("MEDICINE DETAILS").classes(add="bg-inherit grow text-yellow-500 text-2xl lg:text-3xl text-bold")
        ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=self.medicine_dialog.close).classes(add="size-8 bg-inherit text-rose-500")
      
      #Body
      with html.div().classes(add="grow p-1 flex flex-col gap-5"):
        if medicine:
          self.MedicineDetailsForm(medicine=medicine,edit=True)
        else:
          ui.select(label="MEDICINE NAME",options=self.template_medicines,with_input=True,on_change=lambda e:self.retrieve_medicine(medicine=e.value)).props(add=f"popup-content-class='uppercase'").classes(add="px-1 bg-white shadow-md shadow-[#07004d] rounded text-lg")
          with html.div().classes(add="w-full grow flex flex-row justify-center items-center"):
            ui.label("Choose medicine above to add to the formulary").classes(add="text-red-600 text-xl italic font-semibold fa-fade")
    
    self.medicine_dialog.open()
  
  def MedicineDetailsForm(self,medicine:dict|None=None,edit:bool=False):
    #DATA
    tab_sections = ["general","pricing"]
    
    if edit:
      data = medicine
      for key,value in data.items():
        if type(value) == str:
          data[key] = value.title()
    
    else:
      if medicine:
        data = medicine
      data = {
        "medicine_id":None,"name":None,"type":None,"drug_class":None,"active":True,
        "fda_pregnancy_category_1":None,"pregnancy_category_2":None,"fda_pregnancy_category_3":None,"prescription_level":None,
      }
    
    #UI
    with html.form().classes(add="grow w-full px-1 flex flex-col gap-3"):
      #General Details
      ui.input(label="NAME").props(add="type='text'").props(add="readonly").classes(add="col-span-2 w-full px-2 rounded bg-white shadow-sm shadow-[#07004d] text-lg uppercase").bind_value(data,"name")
      
      #Tabs
      with html.div().classes(add="w-full p-0 rounded-b shadow-sm shadow-[#07004d]"):
        with ui.tabs(value=tab_sections[0]).props(add="inline-label mobile-arrows outside-arrows active-class='text-sky-500'").classes(add="w-full rounded-b bg-harmony py-1 text-yellow-500 font-bold") as medicine_tabs:
          for section in tab_sections:
            ui.tab(name=section).props(add="dense")
      
      #Panels
      with html.div().classes(add="grow w-full rounded-br flex flex-col"):
        with ui.tab_panels(tabs=medicine_tabs,value=tab_sections[0]).props(add="animated infinite transition-prev='jump-right' transition-next='jump-left' transition-duration='700'").classes(add="bg-inherit grow w-full grid grid-cols-1"):
          #Profile
          with ui.tab_panel(name="general").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col gap-0.5"):
            #General
            with html.section().classes(add="w-full grid grid-cols-2 gap-3"):
              ui.input(label="TYPE").props(add="type='text'").props(add="readonly").classes(add="w-full px-2 rounded bg-white shadow-sm shadow-[#07004d] text-lg").bind_value(data,"type")
              ui.toggle(options={True:"active",False:"inactive"},value=True,on_change=lambda e:ui.notify(e.value)).props(add="glossy spread size='lg' toggle-color='bg-inherit' toggle-text-color='sky-500' text-color='yellow-500'").classes(add="w-full bg-harmony font-semibold")
            
            #Other details
            with html.section().classes(add="w-full p-1 flex flex-col justify-between gap-3"):
              #Pregnancy Category (1st Trimester)
              with html.div().classes(add="p-1 rounded bg-sky-50 shadow-sm shadow-[#07004d]"):
                ui.label("PREGNANCY CATEGORY (1ST TIMESTER))").props(add="inline").classes(add="font-medium")
                ui.radio(options=[None,"A","B","C","D","X"]).props(add="inline left-label").classes(add="").bind_value(data,"fda_pregnancy_category_1")

              #Pregnancy Category (2nd Trimester)
              with html.div().classes(add="p-1 rounded bg-sky-50 shadow-sm shadow-[#07004d]"):
                ui.label("PREGNANCY CATEGORY (2ND TRIMESTER)").classes(add="font-medium")
                ui.radio(options=[None,"A","B","C","D","X"]).props(add="inline left-label").classes(add="").bind_value(data,"fda_pregnancy_category_2")
              
              #Pregnancy Category (3rd Trimester)
              with html.div().classes(add="p-1 rounded bg-sky-50 shadow-sm shadow-[#07004d]"):
                ui.label("PREGNANCY CATEGORY (3RD TRIMESTER)").classes(add="font-medium")
                ui.radio(options=[None,"A","B","C","D","X"]).props(add="inline left-label").classes(add="").bind_value(data,"fda_pregnancy_category_3")
              
              #Prescription Level
              with html.div().classes(add="p-1 rounded bg-sky-50 shadow-sm shadow-[#07004d]"):
                ui.label("PRESCRIPTION LEVEL").classes(add="font-medium")
                ui.radio(options=[None,"A","B","C","D","S"]).props(add="inline left-label").classes(add="").bind_value(data,"prescription_level")

          
          #Logs
          with ui.tab_panel(name="pricing").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col gap-0.5"):
            pass
        
      
      #Buttons
      with html.div().classes(add=f"w-full flex flex-row {'justify-center gap-5' if medicine else 'justify-center'}"):
        ui.button(text="SAVE",color="",on_click=lambda e:self.update_formulary(data=data,edit=True if medicine else False)).props(add="glossy").classes(add=" bg-harmony text-yellow-500 text-bold text-xl")
        if medicine:
          ui.button(text="DELETE",color="",on_click=lambda e:self.update_formulary(data=data,delete=True)).props(add="glossy").classes(add="bg-harmony text-red-600 text-bold text-xl")

#Nursing
class DispensingStoreManagement():
  """A class for UI and functionalities of dispensing store management"""

  def __init__(self,requisition):
    self.requisition = requisition
    self.visits = len(get_active_visits())

    #UI
    with html.div().classes(add="w-full h-full rounded-t"):
      ui.label("DISPENSING STORE").classes(add="w-full py-1 rounded-t bg-gray-900 px-0 py-3 text-sky-300 text-center text-3xl text-bold")
      with html.div().classes(add="grow w-full p-3 rounded") as self.stocks_panel:
        self.StocksPanel()
  
  #FUNCTIONALITES
  def adc(self,medicine:dict):
    """A method that calculates average daily consumption of medicine"""
    
    pharmacy_visits = (self.visits * 0.75)
    #Capsules or tableets
    if medicine["order_unit"] == "capsule" or medicine["order_unit"] == "tablet":
      return math.ceil(pharmacy_visits * 20)  #Min=10 Max=30 Avg=20
    elif medicine["order_unit"] == "tube" or medicine["order_unit"] == "bottle" or medicine["order_unit"] == "pack":
      return math.ceil(pharmacy_visits)
    else:
      return math.ceil(pharmacy_visits * 0.3)
  
  def dos(self,medicine:dict):
    "A method to that returns a calculated number of days of stock based on data from medicine input"

    available_amount = medicine["dispensing_balance"]
    adc = self.adc(medicine)
    
    if medicine["dispensing_balance"]:
      if adc:
        return round((available_amount/adc))
      else:
        return 1
    else:
      return 0
    
  def stock(self):
    """A method that returns a dictionary with stock details"""
    medicines = self.requisition["medicines"]
    
    overstocks,understocks,stockouts,stocked = [],[],[],[]

    for medicine in medicines:
      dos = self.dos(medicine=medicine)
      stockouts.append(medicine) if dos == 0 else understocks.append(medicine) if dos < 7 else overstocks.append(medicine) if dos >= 14 else stocked.append(medicine)
      
    return {"overstocks":overstocks,"stocked":stocked,"understocks":understocks,"stockouts":stockouts}

  #DISPLAYS
  def StocksPanel(self):
    """A Main display"""
    #DATA
    stocks = self.stock()
    stockouts,understocks,stocked,overstocks = stocks["stockouts"],stocks["understocks"],stocks["stocked"],stocks["overstocks"]
    #UI
    self.stocks_panel.clear()
    with self.stocks_panel:
      with html.div().classes(add="w-full flex flex-col gap-5"):
        #Adequate
        with ui.button(color="green-600",on_click=lambda e:self.StocksDialog(stocked=stocked)).props(add="dense glossy padding='2px 2px'").classes(add="w-full rounded ring-1 ring-green-600 shadow-md shadow-green-600 hover:shadow-green-500") as stocked_button:
          with stocked_button.add_slot("default"):
            with html.span().classes(add="w-full flex flex-row justify-between bg-gray-900 rounded p-2"):
              ui.label("ADEQUATE STOCKS").classes(add="bg-inherit text-green-600 font-medium text-2xl")
              ui.badge(text=str(len(stocked)),color="").classes(add=f"{'px-2 text-2xl' if len(stocked) < 10 else 'pl-1 text-xl'}  bg-inherit size-8 rounded-full ring-1 ring-green-600 shadow-md shadow-green-600 text-green-600 text-bold")
        #Stockouts
        with ui.button(color="red-500",on_click=lambda e:self.StocksDialog(stockouts=stockouts)).props(add="dense glossy padding='2px 2px'").classes(add="w-full rounded ring-1 ring-red-500 shadow-md shadow-red-500 hover:shadow-red-400") as stockouts_button:
          with stockouts_button.add_slot("default"):
            with html.span().classes(add="w-full flex flex-row justify-between bg-gray-900 rounded p-2"):
              ui.label("STOCKOUTS").classes(add="bg-inherit text-red-500 font-medium text-2xl")
              ui.badge(text=str(len(stockouts)),color="").classes(add=f"{'px-2 text-2xl' if len(stockouts) < 10 else 'pl-1 text-xl'} bg-inherit size-8 rounded-full ring-1 ring-red-500 shadow-md shadow-red-500 text-red-500 text-bold {'fa-beat-fade' if stockouts else ''}")
        #Understocks
        with ui.button(color="yellow-400",on_click=lambda e:self.StocksDialog(understocks=understocks)).props(add="dense glossy padding='2px 2px'").classes(add="w-full rounded ring-1 ring-yellow-400 shadow-md shadow-yellow-400 hover:shadow-yellow-300") as understocks_button:
          with understocks_button.add_slot("default"):
            with html.span().classes(add="w-full flex flex-row justify-between bg-gray-900 rounded p-2"):
              ui.label("UNDERSTOCKS").classes(add="bg-inherit text-yellow-400 font-medium text-2xl")
              ui.badge(text=str(len(understocks)),color="").classes(add=f"{'px-2 text-2xl' if len(understocks) < 10 else 'pl-1 text-xl'} bg-inherit size-8 rounded-full ring-1 ring-yellow-400 shadow-md shadow-yellow-400 text-yellow-400 text-bold {'fa-beat-fade' if understocks else ''}")
        #Overstocks
        with ui.button(color="purple-500",on_click=lambda e:self.StocksDialog(overstocks)).props(add="dense glossy padding='2px 2px'").classes(add="w-full rounded ring-1 ring-purple-500 shadow-md shadow-purple-500 hover:shadow-purple-400") as overstocks_button:
          with overstocks_button.add_slot("default"):
            with html.span().classes(add="w-full flex flex-row justify-between bg-gray-900 rounded p-2"):
              ui.label("OVERSTOCKS").classes(add="bg-inherit text-purple-500 font-medium text-2xl")
              ui.badge(text=str(len(overstocks)),color="").classes(add=f"{'px-2 text-2xl' if len(overstocks) < 10 else 'pl-1 text-xl'} bg-inherit size-8 rounded-full ring-1 ring-purple-500 shadow-md shadow-purple-500 text-purple-500 text-bold {'fa-beat-fade' if overstocks else ''}")
        
  def StocksDialog(self,overstocks=None,stocked=None,understocks=None,stockouts=None):
    #DATA
    if overstocks or stocked or understocks or stockouts:
      requisition = self.requisition
      medicines = stockouts if type(stockouts) == list else understocks if type(understocks) == list else stocked if type(stocked) == list else overstocks if type(overstocks) == list else []
    else:
      ui.notify(message=f"No {'stockouts' if type(stockouts) is list else 'understocks' if type(understocks) is list else 'adequately stocked items' if type(stocked) is list else 'overstocks' if type(overstocks) is list else ''}!",type="info",position="top",color=f"{'red-600' if type(stockouts) is list else 'yellow-500' if type(understocks) is list else 'green-500' if type(stocked) is list else 'violet-500' if type(overstocks) is list else ''}")
      return
    
    #UI
    with ui.dialog().props(add="transition-show='scale' transition-hide='scale' transition-duration='500'") as self.stocks_dialog,html.div().style(add="min-width:100%;max-height:95%;").classes(add="bg-white ring-1 ring-blue-400 shadow-md shadow-blue-400"):
      #Dialog Header
      with html.div().classes(add="w-full py-1 pr-2 flex flex-row gap-5 place-center bg-gray-900"):
        #Details
        with html.div().classes(add="grow bg-inherit flex flex-row justify-between content-center pl-3"):
          #Title
          ui.label("STOCKOUTS" if type(stockouts) is list else "UNDERSTOCKS" if type(understocks) is list else "ADEQUATE STOCKS" if type(stocked) is list else "OVERSTOCKS" if type(overstocks) is list else "").classes(add=f"text-{'red-600' if type(stockouts) is list else 'yellow-400' if type(understocks) is list else 'green-600' if type(stocked) is list else 'purple-600' if type(overstocks) is list else ''} text-3xl text-bold")
          #Requisition ID
          with ui.label("REQUISITION ID:").classes(add="h-fit rounded-t font-medium text-sky-50 text-lg"):
            ui.label(requisition["requisition_id"]).classes(add="inline ml-0.5 text-yellow-500 text-bold uppercase")
          #Stock count
          with ui.label(str(len(medicines))).classes(add="h-fit rounded-t text-bold text-yellow-500 text-lg"):
            ui.label(f"ITEM{'' if len(medicines) == 1 else 'S'}").classes(add="inline ml-1 text-sky-50 uppercase")
        #Close button
        ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=self.stocks_dialog.close).classes(add="my-2 size-12 bg-inherit rounded-full text-red-600 text-bold text-base hover:scale-[1.1]")
      #Stocks Aggrid
      with html.div().classes(add="w-full animate__animated animate__fadeIn animate__slow"):
        self.StocksAggrid(overstocks=overstocks,stocked=stocked,understocks=understocks,stockouts=stockouts)
    
    self.stocks_dialog.open()
  
  def StocksAggrid(self,stockouts=None,understocks=None,stocked=None,overstocks=None):
    """"""
    #DATA
    medicines = stockouts if stockouts else understocks if understocks else stocked if stocked else overstocks if overstocks else []
    
    #UI
    if stockouts:
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/No","field":"sno","width":70},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
            {"headerName":"TYPE","field":"type","width":150},
            {"headerName":"UNIT","field":"unit","width":150},
            {"headerName":"BRAND NAME","field":"brand_name"},
            {"headerName":"MANUFACTURER","field":"manufacturer"},
            {"headerName":"DAILY CONSUMPTION","field":"adc","width":150},
          ],
          "rowData":[
            {
              "sno":medicines.index(medicine) + 1,
              "name":medicine["name"],
              "type":medicine["type"],
              "unit":medicine["order_unit"],
              "brand_name":medicine["brand_name"] if medicine["brand_name"] else "---",
              "manufacturer":medicine["manufacturer"] if medicine["manufacturer"] else "---",
              "adc":f"{self.adc(medicine):,.0f}",
            }
            for medicine in medicines
          ]
        },theme="quartz"
        ).classes(add="w-full h-[350px] bg-sky-300 text-sm uppercase")
    
    elif understocks:
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/No","field":"sno","width":100},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
            {"headerName":"TYPE","field":"type","width":150},
            {"headerName":"UNIT","field":"unit","width":150},
            {"headerName":"BRAND NAME","field":"brand_name"},
            {"headerName":"EXPIRY DATE","field":"expire_date","width":200},
            {"headerName":"BALANCE","field":"balance"},
            {"headerName":"DAILY CONSUMPTION","field":"adc"},
            {"headerName":"STOCK DAYS","field":"dos"}
          ],
          "rowData":[
            {
              "sno":medicines.index(medicine) + 1,
              "name":medicine["name"],
              "type":medicine["type"],
              "unit":medicine["order_unit"],
              "brand_name":medicine["brand_name"] if medicine["brand_name"] else "---",
              "expire_date":medicine["expire_date"].strftime("%b %Y") if medicine["expire_date"] else "---",
              "balance":f"{medicine['dispensing_balance']:,.0f}",
              "adc":f"{self.adc(medicine):,.0f}",
              "dos":self.dos(medicine)
            }
            for medicine in medicines
          ]
        },theme="quartz"
        ).style(add="height:350px").classes(add="w-full bg-sky-300 text-sm uppercase")
      
    elif stocked:
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/N","field":"sno","width":80},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
            {"headerName":"TYPE","field":"type","width":150},
            {"headerName":"UNIT","field":"unit","width":150},
            {"headerName":"BRAND NAME","field":"brand_name"},
            {"headerName":"EXPIRY DATE","field":"expire_date","width":200},
            {"headerName":"BALANCE","field":"balance"},
            {"headerName":"DAILY CONSUMPTION","field":"adc"},
            {"headerName":"STOCK DAYS","field":"dos"}
          ],
          "rowData":[
            {
              "sno":medicines.index(medicine) + 1,
              "name":medicine["name"],
              "type":medicine["type"],
              "unit":medicine["order_unit"],
              "brand_name":medicine["brand_name"] if medicine["brand_name"] else "---",
              "expire_date":medicine["expire_date"].strftime("%b %Y") if medicine["expire_date"] else "---",
              "balance":f"{medicine['dispensing_balance']:,.0f}",
              "adc":f"{self.adc(medicine):,.0f}",
              "dos":self.dos(medicine)
            }
            for medicine in medicines
          ]
        },theme="quartz"
        ).style(add="height:350px").classes(add="w-full bg-sky-300 text-sm uppercase")

    elif overstocks:
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/No","field":"sno","width":100},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","width":450},
            {"headerName":"TYPE","field":"type","width":150},
            {"headerName":"UNIT","field":"unit","width":150},
            {"headerName":"BRAND NAME","field":"brand_name"},
            {"headerName":"EXPIRY DATE","field":"expire_date","width":200},
            {"headerName":"DISPENSING BALANCE","field":"balance"},
            {"headerName":"DAILY CONSUMPTION","field":"adc"},
            {"headerName":"STOCK DAYS","field":"dos"}
          ],
          "rowData":[
            {
              "sno":medicines.index(medicine) + 1,
              "name":medicine["name"],
              "type":medicine["type"],
              "unit":medicine["order_unit"],
              "brand_name":medicine["brand_name"] if medicine["brand_name"] else "---",
              "expire_date":medicine["expire_date"].strftime("%b %Y") if medicine["expire_date"] else "---",
              "balance":f"{medicine['dispensing_balance']:,.0f}",
              "adc":f"{self.adc(medicine):,.0f}",
              "dos":self.dos(medicine)
            }
            for medicine in medicines
          ]
        },theme="quartz"
        ).style(add="height:350px").classes(add="w-full bg-sky-300 text-sm uppercase")

#Consultations
class ConsultationsManager():
  """"""
  def __init__(self,user,consulted_clients:list,consulted_visits:list):
    #DATA
    self.user,self.clients,self.visits = user,consulted_clients,consulted_visits
    self.initial_data()

    #UI
    with html.div().classes(add="grow w-full flex flex-col"):
      #Separator
      for i in range(2):
        ui.separator().classes(add="w-full bg-[#09026f]")
      
      #Header
      with html.section().classes(add="w-full p-1 bg-harmony"):
        ui.label("CONSULTATIONS").classes(add="w-full rounded-t text-2xl lg:text-3xl text-yellow-500 font-semibold")

      #Body
      with html.div().classes(add="grow w-full p-1 flex flex-col justify-center content-center") as self.consultations_panel:
        if self.visits:
          self.ConsultationsAggrid(visits=self.visits)
        else:
          ui.label("No clients for consultation now!").classes(add="m-5 text-rose-500 text-2xl lg:text-3xl italic font-semibold fa-fade")
  
  #FUNCTIONALITIES
  def initial_data(self):
    self.diagnoses = get_diagnoses()
    self.active_consultation = None

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
  
  def services(self,imagings=None,medicines=None,procedures=None):

    if procedures:
      _done = [procedure for procedure in procedures if procedure["done"]]
      _pending = [procedure for procedure in procedures if (procedure["payment"]["paid"] or procedure["payment"]["billed"]) and not (procedure["done"] or procedure["cancelled"])]
      _not_done = [procedure for procedure in procedures if not (procedure["payment"]["paid"] or procedure["payment"]["billed"]) and not (procedure["done"] or procedure["cancelled"])]
      _cancelled = [procedure for procedure in procedures if procedure["cancelled"]]

      return f"<span><span class='{'' if _done else 'hidden'} mx-0.5'><i class='fas fa-check text-green-500'></i><i class='ml-0.5 '>{len(_done)}</i></span><span class='{'' if _pending else 'hidden'} mx-0.5'><i class='fas fa-spinner text-yellow-500 fa-spin'></i><i class='ml-0.5 '>{len(_pending)}</i></span><span class='{'' if _not_done else 'hidden'} mx-0.5'><i class='fas fa-xmark text-red-500 '></i><i class='ml-0.5'>{len(_not_done)}</i></span><span class='{'' if _cancelled else 'hidden'} mx-0.5'><i class='fas fa-ban text-gray-500'></i><i class='ml-0.5'>{len(_cancelled)}</i></span></span>"
    
    elif imagings:
      _processed = [imaging for imaging in imagings if imaging["processed"]]
      _pending = [imaging for imaging in imagings if (imaging["payment"]["paid"] or imaging["payment"]["billed"]) and not (imaging["processed"] or imaging["cancelled"])]
      _not_processed = [imaging for imaging in imagings if not (imaging["payment"]["paid"] or imaging["payment"]["billed"]) and not (imaging["processed"] or imaging["cancelled"])]
      _cancelled = [imaging for imaging in imagings if imaging["cancelled"]]

      return f"<span><span class='{'' if _processed else 'hidden'} mx-0.5'><i class='fas fa-check text-green-500'></i><i class='ml-0.5 '>{len(_processed)}</i></span><span class='{'' if _pending else 'hidden'} mx-0.5'><i class='fas fa-spinner text-yellow-500 fa-spin'></i><i class='ml-0.5 '>{len(_pending)}</i></span><span class='{'' if _not_processed else 'hidden'} mx-0.5'><i class='fas fa-xmark text-red-500'></i><i class='ml-0.5'>{len(_not_processed)}</i></span><span class='{'' if _cancelled else 'hidden'} mx-0.5'><i class='fas fa-ban text-gray-500'></i><i class='ml-0.5 '>{len(_cancelled)}</i></span></span>"
     
    elif medicines:
      _dispensed = [medicine for medicine in medicines if medicine["dispensed"]]
      _pending = [medicine for medicine in medicines if (medicine["payment"]["paid"] or medicine["payment"]["billed"]) and not (medicine["dispensed"] or medicine["cancelled"])]
      _not_dispensed = [medicine for medicine in medicines if not (medicine["payment"]["paid"] or medicine["payment"]["billed"]) and not (medicine["dispensed"] or medicine["cancelled"])]
      _cancelled = [medicine for medicine in medicines if medicine["cancelled"]]

      return f"<span><span class='{'' if _dispensed else 'hidden'} mx-0.5'><i class='fas fa-check text-green-500'></i><i class='ml-0.5 '>{len(_dispensed)}</i></span><span class='{'' if _pending else 'hidden'} mx-0.5'><i class='fas fa-spinner text-yellow-500 fa-spin'></i><i class='ml-0.5 '>{len(_pending)}</i></span><span class='{'' if _not_dispensed else 'hidden'} mx-0.5'><i class='fas fa-xmark text-red-500'></i><i class='ml-0.5'>{len(_not_dispensed)}</i></span><span class='{'' if _cancelled else 'hidden'} mx-0.5'><i class='fas fa-ban text-gray-500'></i><i class='ml-0.5 '>{len(_cancelled)}</i></span></span>"
    
    else:
      return "---"

  def services_mini(self,visit):
    """Returns a string of html elements for display of services in small screens"""

    imgs = procs = meds = ""

    if visit["imagings"]:
      imgs = f"<span class=''><span class='fas fa-x-ray'></span><sup class=''>{len(visit['imagings'])}</sup></span>"

    if visit["procedures"]:
      procs = f"<span class=''><span class=''></span><sup class=' fa-solid fa-stethoscope'>{len(visit['procedures'])}</sup></span>"

    if visit["medications"] + visit["medical_items"]:
      meds = f"<span class=''><span class='fa-solid fa-pills'></span><sup class=''>{len(visit['medications'] + visit['medical_items'])}</sup></span>"
    
    #Returns
    if imgs + procs + meds:
      return f"<span class='flex flex-row justify-between items-center'>{imgs}{procs}{meds}</span>"
    else:
      return "---"

  def vitals(self,visit:dict):
    """Returns status of vital signs measurement and their interpretation"""

    if visit["vital_signs"]:
      vitals = visit["vital_signs"][-1]
      temp,sbp,dbp,pr,rr,osat = vitals["temperature"],vitals["sbp"],vitals["dbp"],vitals["pulse_rate"],vitals["resp_rate"],vitals["o2sat"]

      if temp or sbp or dbp or rr or osat:
        return f"<span><span class='{'' if temp else 'hidden'} mr-1'><i class='mr-0.5 '>T</i><i class='fas {'fa-check text-green-600' if self.normal(t=temp) else 'fa-exclamation fa-fade text-red-600'}'></i></span><span class='{'' if sbp else 'hidden'} mr-1'><i class='mr-0.5 '>BP</i><i class='fas {'fa-check text-green-600' if self.normal(sbp=sbp,dbp=dbp) else 'fa-exclamation fa-fade text-red-600'}'></i></span><span class='{'' if pr else 'hidden'} mr-1'><i class='mr-0.5'>PR</i><i class='fas {'fa-check text-green-600' if self.normal(pr=pr) else 'fa-exclamation fa-fade text-red-600'}'></i></span><span class='{'' if rr else 'hidden'} mr-1'><i class='mr-0.5'>RR</i><i class='fas {'fa-check text-green-600' if self.normal(rr=rr) else 'fa-exclamation fa-fade text-red-600'}'></i></span><span class='{'' if osat else 'hidden'}'><i class='mr-0.5'>O₂</i><i class='fas {'fa-check text-green-600' if self.normal(osat=osat) else 'fa-exclamation fa-fade text-red-600'}'></i></span></span>"
      else:
        return "-----"
    else:
      return "-----"

  def normal(self,sbp:int|None=None,dbp:int|None=None,pr:int|None=None,rr:int|None=None,t:float|None=None,osat:int|None=None):
    """Returns True if vital is within normal range"""
    
    #Temperature
    if t:
      if t <= 37.5 and t >= 36.5:
        return True
      else:
        return False
      
    #Blood Pressure
    if sbp and dbp:
      if (sbp < 140 and sbp >= 100): #and (dbp < 90 and dbp >= 60):
        return True
      else:
        return False

    #Pulse Rate
    if pr:
      if pr <= 100 and pr >= 60:
        return True
      else:
        return False

    #Respiratory Rate
    if rr:
      if rr <= 20 and rr >= 12:
        return True
      else:
        return False

    #Oxygen Saturation
    if osat:
      if osat >= 95:
        return True
      else:
        return False

  def last_visit(self,client):
    """A method that takes in client and returns"""
    
    if len(client["visits"]) > 0:
      last_visit = [visit for visit in client["visits"]][-1]
      
      #Active visit status
      if last_visit["is_active"] == True:
        last_visit["status"] = "active"
      else:
        last_visit["status"] = "inactive"
    
      return {"time":last_visit["start_time"],"duration":f"{format_age(last_visit['start_time']).split(' ')[0]} {format_age(last_visit['start_time']).split(' ')[1]} ago","status":last_visit["status"]}
    else:
      return {"time":"No prior visit!","duration":"---","status":"---"}
 
  def register_appointment(self,appointment:dict):
    """Register a new appointment and store data to database"""
    
    appointment["attendee_id"] = get_staff_username(first_name=appointment["consultant"].split(" ")[0].lower(),last_name=appointment["consultant"].split(" ")[0].lower(),role="doctor")

    status = clients_db.register_appointment(appointment)

    #Notification
    ui.notify(message=status["message"],type=status["type"],position="center")
    
  #DISPLAYS
  def ConsultationsAggrid(self,visits:list[dict]):
    """"""
    #UI
    self.consultations_panel.clear()
    with self.consultations_panel:
      #Large screen
      ui.aggrid(
        {
          "columnDefs":[
            {"headerName":"S/N","field":"sno","width":70},
            {"headerName":"CLIENT ID","field":"client_id","filter":"agTextColumnFilter","floatingFilter":True,"width":130},
            {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","floatingFilter":True},
            {"headerName":"AGE","field":"age","width":100},
            {"headerName":"GENDER","field":"gender","width":100},
            {"headerName":"PAYMENT","field":"payment","width":110},
            {"headerName":"VITAL SIGNS","field":"vitals","width":220},
            {"headerName":"IMAGINGS","field":"imagings"},
            {"headerName":"PROCEDURES","field":"procedures"},
            {"headerName":"MEDICATIONS","field":"medications"}
          ],
          "rowData":[
            {
              "sno":visits.index(visit) + 1,
              "client_id":visit["client_id"],
              "name":visit["client_name"].title(),
              "age":f"{format_age(visit['client_birthdate']).split(' ')[0]} {format_age(visit['client_birthdate']).split(' ')[1]}",
              "gender":visit["client_gender"].capitalize(),
              "payment":visit["payment_mode"].upper(),
              "vitals":self.vitals(visit),
              "imagings":self.services(imagings=visit["imagings"]),
              "procedures":self.services(procedures=visit["procedures"]),
              "medications":self.services(medicines=visit["medications"]+visit["medical_items"]),
            } for visit in visits
          ]
        },
        theme="quartz",
        html_columns=[6,7,8,9]
      ).props(add="").classes(add="lg-show grow w-full animate__animated animate__fadeIn").on("cellClicked",lambda e:self.ConsultationsDialog(client=[client for client in self.clients if client["client_id"] == e.args["data"]["client_id"]][0]))

      #Small screen
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
              "name":f"{visit['client_name'].split(' ')[0]} {visit['client_name'].split(' ')[-1]}".title(),
              "specs":self.client_mini(visit),
              "services":self.services_mini(visit)
            } for visit in visits
          ]
        },
        theme="quartz",
        html_columns=[2,3]
      ).props(add="").classes(add="lg:hidden grow w-full animate__animated animate__fadeIn").on("cellClicked",lambda e:self.ConsultationsDialog(client=[client for client in self.clients if client["client_id"] == e.args["data"]["client_id"]][0]))

  async def ConsultationsDialog(self,client:dict):
    """Displays from consultations in the previous visits"""

    #DATA
    details = {
      "name":f"{client['first_name']} {client['middle_name'] if client['middle_name'] else ''} {client['last_name']}".title(),
      "short_name":f"{client['first_name']} {client['middle_name'][0] if client['middle_name'] else ''} {client['last_name']}".title(),
      "age":format_age(birthdate=client["birthdate"],short=True),
      "gender":client["gender"],
      "address":client["address"],
      "last_visit":f"{format_age(client['visits'][-2]['start_time'])} ago" if len(client["visits"]) > 1 else "---"
    }
    
    visits = sorted(client["visits"],key=lambda e:e["start_time"],reverse=True)
    active_visit = [visit for visit in visits if visit["is_active"]][0]
    
    #FXS
    def close_dialog():
      self.ConsultationsAggrid(visits=self.visits)

    #UI
    with ui.dialog().props(add="transition-show='jump-up' transition-hide='jump-down' transition-duration='500'") as self.consultations_dialog,html.div().style(add="min-width:100%;min-height:90%;").classes(add="bg-sky-50 p-0.5 overflowhidden flex flex-col gap-0.5"):
      #Dialog Header
      with html.div().classes(add="w-full pr-2 rounded-t flex flex-row justify-between items-center bg-harmony"):
        with html.div().classes(add="grow"):
          ClientCard(details=details)
        ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=close_dialog).classes(add="bg-inherit size-8 rounded-full text-red-500 text-bold")
      
      #Dialog Body
      with html.div().classes(add="grow w-full flex flex-col items-center justify-center") as self.visit_panel:
        with html.div().classes(add="flex flex-col gap-5"):
          ui.spinner(type="puff",size="xl").classes(add="grow w-full text-xl text-sky-600 font-bold")
          ui.label("Please wait...").classes(add="w-full text-xl text-sky-600 font-semibold italic fa-fade")
        
    self.consultations_dialog.open()
    await asyncio.sleep(1.5)
    self.ActiveConsultationPanel(visit=active_visit)

  
  def xxx(self):
    with html.div():
      with html.div():
        #Small screen
        with html.div().classes(add="lg:hidden w-full grow flex flex-col gap-1"):
          #Tabs
          with html.div().classes(add="w-full px-1 grid grid-cols-10 items-center gap-1 shadow-sm shadow-[#07004d]"):
            ui.label(len(visits)).classes(add="col-span-1 size-8 rounded-full flex justify-center items-center bg-harmony ring-1 ring-offset-1 ring-[#07004d] text-bold text-lg lg:text-xl text-yellow-500 italic")
            with ui.tabs(value=visits[0]["visit_id"]).props(add="inline-label mobile-arrows outside-arrows active-class='text-sky-700 font-bold'").classes(add="col-span-9 py-1") as visits_mini_tabs:
              for visit in visits:
                ui.tab(name=visit["visit_id"],label=f"{visits.index(visit) + 1}.  {visit['start_time'].strftime('%d %b %Y')}",icon="fas fa-user-doctor" if visit["consultations"] else "fas fa-x-ray").props(add="dense")
          
          #Panels
          with html.div().classes(add="grow w-full rounded-br flex flex-col"):
            with ui.tab_panels(tabs=visits_mini_tabs,value=visits[0]["visit_id"]).props(add="animated infinite transition-prev='jump-right' transition-next='jump-left' transition-duration='700'").classes(add="bg-inherit grow w-full grid grid-cols-1"):
              for visit in visits:
                with ui.tab_panel(name=visit["visit_id"]).classes(add="w-full h-full p-0.5 rounded") as self.visit_tab:
                  #For active/current visit
                  if visit["is_active"]:
                    self.ActiveConsultationPanel(visit)
                  else:
                    self.PreviousVisitPanel(visit)
        
        #Large screen
        with html.div().classes(add="lg-flex grow h-full flex-row gap-1 bg-sky-100"):
          #Tabs
          with html.div().classes(add=""):
            ui.label(f"{len(visits)} VISITS").classes(add="text-center bg-harmony mb-1 font-semibold text-xl text-yellow-500 italic")
            with ui.tabs(value=visits[0]["visit_id"]).props(add="vertical inline-label outside-arrows active-class='shadow-sm shadow-[#07004d] text-sky-700 font-bold'").classes(add="h-[450px]") as visits_tabs:
              for visit in visits:
                ui.tab(name=visit["visit_id"],label=f"{visits.index(visit) + 1}.  {visit['start_time'].strftime('%d %b %Y')}",icon="fas fa-user-doctor" if visit["consultations"] else "fas fa-x-ray").props(add="dense").classes(add="rounded")

          #Panels
          with html.div().classes(add="grow rounded-br flex flex-col"):
            with ui.tab_panels(tabs=visits_tabs,value=visits[0]["visit_id"]).props(add="animated infinite transition-prev='jump-up' transition-next='jump-down' transition-duration='700'").classes(add="bg-inherit grow w-full h-full grid grid-cols-1"):
              for visit in visits:
                with ui.tab_panel(name=visit["visit_id"]).classes(add="w-full h-full p-0 rounded") as self.visit_tab:
                  #For active/current visit
                  if visit["is_active"]:
                    self.ActiveConsultationPanel(visit)
                  else:
                    self.PreviousVisitPanel(visit)
            
      self.consultations_dialog.open()
  
  def PreviousVisitPanel(self,visit:dict):
    """A display for previous visits"""
    #DATA
    consultation = visit["consultations"][0] if visit["consultations"] else None
    clinical_history = visit["consultations"][0]["clinical_history"] if visit["consultations"] else None
    
    #FXS
    def hpis(clinical_history):
      complaints,hpis = clinical_history["chief_complaints"],[clinical_history["hpi1"],clinical_history["hpi2"],clinical_history["hpi3"]]
      hpis = zip(complaints,hpis)
      return list(hpis)

    #UI
    self.visit_tab.clear()
    with self.visit_tab.classes(add="bg-sky-100"):
      with ui.scroll_area().classes(add="h-[600px] lg:h-[500px]"):
        with ui.timeline(side="right",layout="dense").classes(add=""):
          #Consultation
          if visit["consultations"]:
            #HPI
            with ui.timeline_entry(icon="fas fa-notes-medical").props(add="color='green-6'") as hpi_entry:
              #Subtitle
              with hpi_entry.add_slot("subtitle"):
                if clinical_history["history_time"]:
                  with ui.label(clinical_history["history_time"].strftime("%a %-d %b %Y")).classes(add="text-base text-bold text-blue-700"):
                    ui.label(clinical_history["history_time"].strftime("%H:%M")).classes(add="inline ml-5 text-base text-bold text-green-700")
              #Title
              with hpi_entry.add_slot("title"):
                ui.label('HISTORY OF PRESENTING ILLNESS').classes(add="w-full text-sky-600 text-bold text-3xl italic")
              #Body
              with hpi_entry.add_slot("default"):
                if clinical_history["chief_complaints"]:
                  with html.form().classes(add="w-full grid grid-cols-1 lg:grid-cols-2 gap-2"):                
                    for hpi in hpis(clinical_history):
                      if hpi[0]:
                        with ui.label(text=f"{hpis(clinical_history).index(hpi) + 1}. {hpi[0].capitalize()}").classes(add="my-2 text-bold text-xl"):
                          if hpi[1]:
                            html.p(hpi[1].capitalize()).classes(add="block text-md font-light italic")
                          else:
                            html.p("No notes available!").classes(add="block text-red-400 font-normal text-md italic")
                else:
                  html.p("No notes available!").classes(add="block text-red-400 font-normal text-lg italic")
            
            #PMH & FSH
            with ui.timeline_entry(icon="fas fa-notes-medical").props(add="color='green-6'") as past_hx_entry:
              #Subtitle
              with past_hx_entry.add_slot("subtitle"):
                if clinical_history["history_time"]:
                  with ui.label(clinical_history["history_time"].strftime("%a %-d %b %Y")).classes(add="text-base text-bold text-blue-700"):
                    ui.label(clinical_history["history_time"].strftime("%H:%M")).classes(add="inline ml-5 text-base text-bold text-green-700")
              #Title
              with past_hx_entry.add_slot("title"):
                ui.label('PAST CLINICAL AND SOCIAL HISTORY').classes(add="w-full text-sky-600 text-bold text-3xl italic")
              #Body
              with past_hx_entry.add_slot("default"):
                with html.div().classes(add="w-full grid grid-cols-1 lg:grid-cols-2 gap-2"):
                  #Medical/Surgical
                  with html.div().classes(add="w-full text-lg"):
                    ui.label("PAST MEDICAL & SURGICAL HISTORY").classes(add="text-bold text-xl")
                    if clinical_history["medical_history"] or clinical_history["surgical_history"]:
                      if clinical_history["medical_history"]:
                        ui.markdown(content=clinical_history["medical_history"].capitalize()).classes(add="text-md font-light italic")
                      if clinical_history["surgical_history"]:
                        ui.markdown(content=clinical_history["surgical_history"].capitalize()).classes(add="text-md font-light italic")
                    else:
                      html.p("No notes available!").classes(add="block text-red-400 font-normal text-lg italic")

                  #Family/Social
                  with html.div().classes(add="w-full text-lg"):
                    html.label("FAMILY & SOCIAL HISTORY").classes(add="text-bold text-xl")
                    if clinical_history["family_history"] or clinical_history["social_history"]:
                      if clinical_history["family_history"]:
                        html.p(clinical_history["family_history"].capitalize()).classes(add="text-base font-light italic")
                      if clinical_history["social_history"]:
                        html.p(clinical_history["social_history"].capitalize()).classes(add="text-base font-light italic")
                    else:
                      html.p("No notes available!").classes(add="block text-red-400 font-normal text-lg italic")
            
            #PHYSICAL EXAM
            with ui.timeline_entry(icon="fas fa-stethoscope").props(add="color='green-6'") as pe_entry:
              #Subtitle
              with pe_entry.add_slot("subtitle"):
                if consultation["general_exam"]["ge_exam_time"]:
                  with ui.label(consultation["general_exam"]["ge_exam_time"].strftime("%a %-d %b %Y")).classes(add="text-base text-bold text-blue-700"):
                    ui.label(consultation["general_exam"]["ge_exam_time"].strftime("%H:%M")).classes(add="inline ml-5 text-base text-bold text-green-700")
              #Title
              with pe_entry.add_slot("title"):
                ui.label('PHYSICAL EXAMINATION').classes(add="w-full text-sky-600 text-bold text-3xl italic")
              #Body
              with pe_entry.add_slot("default"):
                with html.div().classes(add="w-full grid grid-cols-1 lg:grid-cols-2 gap-2"):
                  #General exam
                  with html.div().classes(add="w-full text-lg"):
                    ui.label("GENERAL EXAMINATION").classes(add="text-bold text-xl")
                    if consultation["general_exam"]["notes"]:
                      ui.markdown(content=consultation["general_exam"]["notes"].capitalize()).classes(add="text-md font-light italic")
                    else:
                      html.p("No notes available!").classes(add="block text-red-400 font-normal text-lg italic")

                  #Orodental exam
                  with html.div().classes(add="w-full text-lg"):
                    html.label("ORODENTAL EXAMINATION").classes(add="text-bold text-xl")
                    if consultation["orodental_exam"]["intraoral"] or consultation["orodental_exam"]["extraoral"]:
                      if consultation["orodental_exam"]["intraoral"]:
                        html.p(consultation["orodental_exam"]["intraoral"].capitalize()).classes(add="text-base font-light italic")
                      if consultation["orodental_exam"]["extraoral"]:
                        html.p(consultation["orodental_exam"]["extraoral"].capitalize()).classes(add="text-base font-light italic")
                    else:
                      html.p("No notes available!").classes(add="block text-red-400 font-normal text-lg italic")
          
          #Imagings
          if visit["imagings"]:
            imagings = visit["imagings"]
            first_imaging = imagings[0]
            with ui.timeline_entry(icon="fas fa-x-ray").props(add="color='green-6'") as img_entry:
              #Subtitle
              with img_entry.add_slot("subtitle"):
                with ui.label(first_imaging["request_time"].strftime("%a %-d %b %Y")).classes(add="text-base text-bold text-blue-700"):
                  ui.label(first_imaging["request_time"].strftime("%H:%M")).classes(add="inline ml-5 text-base text-bold text-green-700")
              #Title
              with img_entry.add_slot("title"):
                ui.label('IMAGINGS').classes(add="w-full text-sky-600 text-bold text-3xl italic")
              #Body
              with img_entry.add_slot("default"):
                with html.div().classes(add="w-full"):
                  ImagingResultsForm(visit=visit)

          #Procedures
          if visit["procedures"]:
            procedures = visit["procedures"]
            first_procedure = procedures[0]
            with ui.timeline_entry(icon="fas fa-tooth").props(add="color='green-6'") as proc_entry:
              #Subtitle
              with proc_entry.add_slot("subtitle"):
                with ui.label(first_procedure["ordered_on"].strftime("%a %-d %b %Y")).classes(add="text-base text-bold text-blue-700"):
                  ui.label(first_procedure["ordered_on"].strftime("%H:%M")).classes(add="inline ml-5 text-base text-bold text-green-700")
              #Title
              with proc_entry.add_slot("title"):
                ui.label('PROCEDURES').classes(add="w-full text-sky-600 text-bold text-3xl italic")
              #Body
              with proc_entry.add_slot("default"):
                if procedures:
                    ui.table(
                      columns=[
                        {"name":"sno","label":"S/No","field":"sno","width":50},
                        {"name":"name","label":"NAME","field":"name"},
                        {"name":"status","label":"STATUS","field":"status"}
                      ],
                      rows=[
                        {
                          "sno":procedures.index(procedure) + 1,
                          "name":procedure["name"],
                          "status":"done" if procedure["done"] else "not done"
                        } for procedure in procedures
                      ],
                      column_defaults={
                        "align":"left"
                      },
                      pagination=5,title="PROCEDURES"
                    ).props(add="dense rows-per-page-label='procedures per page'").classes(add="w-1/2 uppercase")

          #Medicines
          if visit["medications"] or visit["medical_items"]:
            medications,medical_items = visit["medications"],visit["medical_items"]
            first_item = medications[0] if medications else medical_items[0]
            with ui.timeline_entry(icon="fas fa-file-prescription").props(add="color='green-6'") as med_entry:
              #Subtitle
              with med_entry.add_slot("subtitle"):
                with ui.label(first_item["prescribed_on"].strftime("%a %-d %b %Y")).classes(add="text-base text-bold text-blue-700"):
                  ui.label(first_item["prescribed_on"].strftime("%H:%M")).classes(add="inline ml-5 text-base text-bold text-green-700")
              #Title
              with med_entry.add_slot("title"):
                ui.label('MEDICATIONS & MEDICAL ITEMS').classes(add="w-full text-sky-600 text-bold text-3xl italic")
              #Body
              with med_entry.add_slot("default"):
                with html.div().classes(add="w-full p-0.5"):
                  #Medications
                  if medications:
                    ui.table(
                      columns=[
                        {"name":"sno","label":"S/No","field":"sno","width":50},
                        {"name":"name","label":"NAME","field":"name"},
                        {"name":"dosage","label":"DOSAGE","field":"dosage"},
                        {"name":"prescribed_items","label":"PRESCRIBED ITEMS","field":"prescribed_items","width":50},
                        {"name":"status","label":"STATUS","field":"status"}
                      ],
                      rows=[
                        {
                          "sno":medications.index(medication) + 1,
                          "name":medication["name"],
                          "dosage":medication["dosage"],
                          "prescribed_items":medication["prescribed_items_no"],
                          "status":"dispensed" if medication["dispensed"] else "not dispensed"
                        } for medication in medications
                      ],
                      column_defaults={
                        "align":"left"
                      },
                      pagination=5,title="MEDICATIONS"
                    ).props(add="dense rows-per-page-label='medications per page' ").classes(add="uppercase")

                  #Medical items
                  if medical_items:
                    ui.table(
                      columns=[
                        {"name":"sno","label":"S/No","field":"sno","width":50},
                        {"name":"name","label":"NAME","field":"name"},
                        {"name":"prescribed_items","label":"PRESCRIBED ITEMS","field":"prescribed_items","width":50},
                        {"name":"status","label":"STATUS","field":"status"}
                      ],
                      rows=[
                        {
                          "sno":medications.index(medication) + 1,
                          "name":medication["name"],
                          "prescribed_items":medication["prescribed_items_no"],
                          "status":"dispensed" if medication["dispensed"] else "not dispensed"
                        } for medication in medical_items
                      ],
                      column_defaults={
                        "align":"left"
                      },
                      pagination=5,title="MEDICAL ITEMS"
                    ).classes(add="uppercase")
            
  def ActiveConsultationPanel(self,visit:dict,edit:bool=False):
    """"""
    #DATA
    self.active_visit = visit
    _anthrops = sorted([anthrop for anthrop in self.active_visit["anthropometrics"] if anthrop["done"] and anthrop["weight"]],key=lambda anthrop:anthrop["anthropometrics_time"],reverse=True)
    anthrops = _anthrops[0] if _anthrops else self.active_visit["anthropometrics"][-1]
    _vitals = sorted([vital for vital in self.active_visit["vital_signs"] if vital["done"]],key=lambda vital:vital["vitals_time"],reverse=True)
    vitals = _vitals[0] if _vitals else self.active_visit["vital_signs"][-1]
    imagings = self.active_visit["imagings"]
    self.active_consultation = self.active_visit["consultations"][0]

    clerkship_sections = ["present history","medical & surgical history","family & social history","physical examination","provisional diagnoses","workup","definitive diagnoses","management"]
    
    #UI
    self.visit_panel.clear()
    with self.visit_panel.classes(add="flex flex-col gap-0.5 animate__animated animate__fadeIn animate__slow"):
      #Triage
      with html.div().classes(add="bg-harmony w-full flex flex-col lg:flex-row"):
        #Anthropometrics
        with html.div().classes(add=f"bg-inherit flex flex-row justify-center items-center lg:justify-around gap-3"):
          #BWt
          with ui.chip(icon="fa-solid fa-weight-scale",color="",text_color="yellow-8").props(add="dense").classes(add="bg-inherit m-0 rounded text-base lg:text-lg text-yellow-500"):
            ui.badge(text=f"{anthrops['weight'] if anthrops['weight'] else '---'} {'kg' if anthrops['weight'] else ''}",color="").classes(add=f"bg-inherit ml-0.5 text-base text-bold text-sky-300")
          #height/Length
          with ui.chip(icon="fa-solid fa-ruler-vertical",color="",text_color="yellow-8").props(add="dense").classes(add="bg-inherit m-0 rounded text-base lg:text-lg text-yellow-500"):
            ui.badge(text=f"{anthrops['height'] if anthrops['height'] else '---'} {'cm' if anthrops['height'] else ''}",color="").classes(add=f"bg-inherit ml-0.5 text-base text-bold text-sky-300")
          
          if get_duration(visit["client_birthdate"])["years"] < 2:
            #MUAC
            with ui.chip(text="MUAC",color="").classes(add="hidden m-0 p-0 bg-inherit rounded text-md text-bold text-yellow-500"):
              ui.badge(text=f"{anthrops['muac'] if anthrops['muac'] else '---'} {'cm' if anthrops['muac'] else ''}",color="").props(add="dense").classes(add=f"bg-inherit ml-0.5 text-lg text-bold text-sky-300")
            #Head Circumference
            with ui.chip(text="HC",color="").classes(add="hidden m-0 p-0 bg-inherit rounded text-md text-bold text-yellow-500"):
              ui.badge(text=f"{anthrops['head_circum'] if anthrops['head_circum'] else '---'} {'cm' if anthrops['head_circum'] else ''}",color="").classes(add=f"bg-inherit ml-0.5 text-lg text-bold text-sky-300")

        #Vitals
        with html.div().classes(add="grow bg-inherit p-1 flex flex-row justify-around items-center text-bold"):
          #T
          with ui.chip(icon="fa-solid fa-temperature-high",text_color="yellow-8",color="").classes(add="bg-inherit m-0 px-0.5 py-0 rounded text-md text-yellow-500"):
            ui.badge(text=f"{vitals['temperature'] if vitals['temperature'] else '---'} {'℃' if vitals['temperature'] else ''}",color="").classes(add=f"bg-inherit m-0 p-0 text-base text-bold text-{'sky-300' if (not vitals['temperature']) else 'green-400' if self.normal(t=vitals['temperature']) else 'red-600'}")
          #BP
          with ui.chip(icon="fa-solid fa-pump-medical",text_color="yellow-8",color="").classes(add=f"{'hidden' if get_duration(visit['client_birthdate'])['years'] < 12 else ''} bg-inherit m-0 p-0 rounded text-base text-bold"):
            ui.badge(text=f"{vitals['sbp'] if vitals['sbp'] else '---'}/{vitals['dbp'] if vitals['dbp'] else '---'} {'mmHg' if vitals['sbp'] or vitals['dbp'] else ''}",color="").classes(add=f"bg-inherit m-0 p-0 text-base text-bold text-{'sky-300' if ((not vitals['sbp']) and (not vitals['dbp'])) else 'green-400' if (self.normal(sbp=vitals['sbp']) or self.normal(dbp=vitals['dbp'])) else 'red-600'}")
          #PR
          with ui.chip(icon="fa-solid fa-heart-pulse",text_color="yellow-8",color="").classes(add="bg-inherit m-0 px-0.5 py-0 rounded text-md text-yellow-500"):
            ui.badge(text=f"{vitals['pulse_rate'] if vitals['pulse_rate'] else '---'} {'bpm' if vitals['pulse_rate'] else ''}",color="").classes(add=f"bg-inherit m-0 p-0 text-base text-bold text-{'sky-300' if (not vitals['pulse_rate']) else 'green-400' if self.normal(t=vitals['pulse_rate']) else 'red-600'}")
          #RR
          with ui.chip(icon="fa-solid fa-lungs",text_color="yellow-8",color="").classes(add="bg-inherit m-0 px-0.5 py-0 rounded text-md text-yellow-500"):
            ui.badge(text=f"{vitals['resp_rate'] if vitals['resp_rate'] else '---'} {'cpm' if vitals['resp_rate'] else ''}",color="").classes(add=f"bg-inherit m-0 p-0 text-base text-bold text-{'sky-300' if (not vitals['resp_rate']) else 'green-400' if self.normal(t=vitals['resp_rate']) else 'red-600'}")
          #O2SAT
          with ui.chip(text="O₂",text_color="yellow-8",color="").classes(add="bg-inherit m-0 p-0 rounded text-base text-bold"):
            ui.badge(text=f"{vitals['o2sat'] if vitals['o2sat'] else '---'} {'%' if vitals['o2sat'] else ''}",color="").classes(add=f"bg-inherit m-0 ml-0.5 p-0 text-base text-bold text-{'sky-300' if (not vitals['o2sat']) else 'green-400' if self.normal(osat=vitals['o2sat']) else 'red-600'}")

      #Consultation
      #Small Screen
      with html.section().classes(add="lg:hidden grow w-full flex flex-col"):
        #Tabs
        with html.div().classes(add="w-full p-0 rounded-b shadow-sm shadow-[#07004d]"):
          with ui.tabs(value=clerkship_sections[0]).props(add="inline-label mobile-arrows outside-arrows active-class='text-sky-500'").classes(add="w-full rounded-b bg-harmony py-1 text-yellow-500 font-bold") as clerkship_tabs:
            for section in clerkship_sections:
              ui.tab(name=section).props(add="dense")
        
        #Panels
        with html.div().classes(add="order-first grow w-full rounded-br flex flex-col"):
          with ui.tab_panels(tabs=clerkship_tabs,value=clerkship_sections[0]).props(add="animated infinite transition-prev='jump-right' transition-next='jump-left' transition-duration='700'").classes(add="bg-inherit grow w-full grid grid-cols-1"):
            #Present history
            with ui.tab_panel(name="present history").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col gap-0.5") as self.hpi_panel:
              self.PresentingIllness(consultation=self.active_consultation)
            
            #Medical & Surgical History
            with ui.tab_panel(name="medical & surgical history").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col justify-around gap-0.5"):
              self.PastMedicalSurgicalHistory(consultation=self.active_consultation)
            
            #Family & Social History
            with ui.tab_panel(name="family & social history").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col justify-around gap-0.5"):
              self.FamilySocialHistory(consultation=self.active_consultation)
            
            #Physical Examination
            with ui.tab_panel(name="physical examination").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col justify-between gap-0.5"):
              self.PhysicalExamination(consultation=self.active_consultation)
            
            #Provisional Diagnoses
            with ui.tab_panel(name="provisional diagnoses").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col gap-0.5"):
              self.ProvisionalDiagnoses(consultation=self.active_consultation)
            
            #Workup
            with ui.tab_panel(name="workup").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col gap-0.5"):
              ImagingsForm(parent=self,attendee_id=self.user.username,visit=self.active_visit)
            
            #Definitive Diagnoses
            with ui.tab_panel(name="definitive diagnoses").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col gap-0.5"):
              self.DefinitiveDiagnoses(consultation=self.active_consultation)
            
            #Management
            with ui.tab_panel(name="management").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col gap-0.5"):
              ManagementPlanForm(visit=self.active_visit,parent=self,attendee_id=self.user.username)
              
      #Large Screen
      with html.section().classes(add="grow w-full lg-flex flex-row gap-1"):
        #Tabs
        with html.div().classes(add="p-1 shadow-sm shadow-[#07004d]"):
          with ui.tabs(value=clerkship_sections[0]).props(add="inline-label mobile-arrows outside-arrows stretch vertical active-class='text-sky-500'").classes(add="w-full py-1 text-yellow-500 font-bold") as clerkship_tabs:
            for section in clerkship_sections:
              ui.tab(name=section).props(add="").classes(add="bg-harmony my-1 rounded")
        
        #Panels
        with html.div().classes(add="grow rounded-br flex flex-col"):
          with ui.tab_panels(tabs=clerkship_tabs,value=clerkship_sections[0]).props(add="animated infinite transition-prev='jump-down' transition-next='jump-up' transition-duration='500'").classes(add="bg-inherit grow w-full grid grid-cols-1"):
            #Present history
            with ui.tab_panel(name="present history").classes(add="w-full h-full p-1 rounded-br flex flex-col lg:justify-around") as self.hpi_panel:
              self.PresentingIllness(consultation=self.active_consultation)
            
            #Medical & Surgical History
            with ui.tab_panel(name="medical & surgical history").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col justify-around gap-0.5"):
              self.PastMedicalSurgicalHistory(consultation=self.active_consultation)
            
            #Family & Social History
            with ui.tab_panel(name="family & social history").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col justify-around gap-0.5"):
              self.FamilySocialHistory(consultation=self.active_consultation)
            
            #Physical Examination
            with ui.tab_panel(name="physical examination").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col justify-around gap-0.5"):
              self.PhysicalExamination(consultation=self.active_consultation)
            
            #Provisional Diagnoses
            with ui.tab_panel(name="provisional diagnoses").classes(add="w-full h-full p-0.5 rounded-0 grid grid-cols-2 gap-0.5"):
              self.ProvisionalDiagnoses(consultation=self.active_consultation)
            
            #Workup
            with ui.tab_panel(name="workup").classes(add="w-full h-full p-0.5 rounded-0 grid grid-cols-2 gap-0.5"):
              ImagingsForm(parent=self,attendee_id=self.user.username,visit=self.active_visit)
            
            #Definitive Diagnoses
            with ui.tab_panel(name="definitive diagnoses").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col lg:grid grid-cols-2 lg:h-full gap-0.5"):
              self.DefinitiveDiagnoses(consultation=self.active_consultation)
            
            #Management
            with ui.tab_panel(name="management").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col gap-0.5"):
              ManagementPlanForm(visit=self.active_visit,parent=self,attendee_id=self.user.username)
      
  def PresentingIllness(self,consultation:dict):
    """"""
    #DATA
    history = consultation["clinical_history"]
    complaints = {
      "count":len(history["chief_complaints"]),
      "complaint1":history["chief_complaints"][0] if len(history["chief_complaints"]) > 0 else None,
      "complaint2":history["chief_complaints"][1] if len(history["chief_complaints"]) > 1 else None,
      "complaint3":history["chief_complaints"][2] if len(history["chief_complaints"]) > 2 else None
    }
    hpis = {
      "hpi1":history["hpi1"] if history["hpi1"] else None,
      "hpi2":history["hpi2"] if history["hpi2"] else None,
      "hpi3":history["hpi3"] if history["hpi3"] else None
    }
    
    #FXS
    def HPI():
      hpi_pad.clear()
      with hpi_pad.classes(add=""):
        if complaints["count"]:
          with html.div().classes(add="grow w-full py-0.5 flex flex-col lg:flex-row lg:items-center lg:content-center gap-1 lg:gap-5"):
          #HPI1
            if complaints["complaint1"]:
              ui.textarea(label=complaints["complaint1"].upper(),placeholder="Probe more...").props(add="hide-bottom-space stack-label input-class='h-[100px] lg:h-[250px]' label-color='#07004d'").classes(add="w-full lg:w-[30%] lg:h-full rounded bg-white shadow-md shadow-[#07004d] px-3 text-lg").bind_value(hpis,"hpi1")
            #HPI2
            if complaints["complaint2"]:
              ui.textarea(label=complaints["complaint2"].upper(),placeholder="Probe more...").props(add="hide-bottom-space stack-label input-class='h-[100px] lg:h-[250px]' label-color='#07004d'").classes(add="w-full lg:w-[30%] lg:h-full rounded bg-white shadow-md shadow-[#07004d] px-3 text-lg").bind_value(hpis,"hpi2")
            #HPI3
            if complaints["complaint3"]:
              ui.textarea(label=complaints["complaint3"].upper(),placeholder="Probe more...").props(add="hide-bottom-space stack-label input-class='h-[100px] lg:h-[250px]' label-color='#07004d'").classes(add="w-full lg:w-[30%] lg:h-full rounded bg-white shadow-md shadow-[#07004d] px-3 text-lg").bind_value(hpis,"hpi3")
            
            #BUTTONS
          ui.button(text="SAVE HPI",icon="fa-regular fa-floppy-disk",color="",on_click=save_hpi).classes(add="bg-harmony lg:my-3 w-fit self-center rounded shadow-md shadow-[#07004d] text-xl text-yellow-500 text-bold")
        
        else:
          with html.div().classes(add="grow w-full p-1 rounded flex flex-col justify-center items-center content-center"):
            ui.label("No client's complaint saved!").classes(add="text-red-500 text-xl italic font-bold fa-fade")

    def amplify_complaints():
      #Save complaints
      comps = [comp for key,comp in complaints.items() if key != "count" and comp]
      status = clients_db.register_chief_complaints({"consultant_id":self.user.username,"hx_id":history["hx_id"],"complaints":json.dumps(comps) if comps else None})
      ui.notify(message=status["message"],type=status["type"],position=status["position"])
      
      #Updating complaints
      #Complaint1
      complaints["count"] = len(comps)
      if not complaints["complaint1"]:
        hpis["hpi1"] = None
        if complaints["complaint2"]:
          complaints["complaint1"],hpis["hpi1"] = complaints["complaint2"],hpis["hpi2"]
          complaints["complaint2"],hpis["hpi2"] = None,None
        else:
          if complaints["complaint3"]:
            complaints["complaint1"],hpis["hpi1"] = complaints["complaint3"],hpis["hpi3"]
            complaints["complaint3"],hpis["hpi3"] = None,None
      #Complaint2
      if not complaints["complaint2"]:
        hpis["hpi2"] = None
        if complaints["complaint3"]:
          complaints["complaint2"],hpis["hpi2"] = complaints["complaint3"],hpis["hpi3"]
          complaints["complaint3"],hpis["hpi3"] = None,None
      #Complaint3
      if not complaints["complaint3"]:
        hpis["hpi3"] = None
      
      #Display HPI boxes
      HPI()
     
    def save_hpi():
      #DB SAVING
      status = clients_db.register_hpi({"hx_id":history["hx_id"],"editor_id":self.user.username,"hpi1":hpis["hpi1"],"hpi2":hpis["hpi2"],"hpi3":hpis["hpi3"]})
      #NOTIFY
      ui.notify(message=status["message"],type=status["type"],position=status["position"])
    
    #UI
    self.hpi_panel.clear()
    with self.hpi_panel:
      #Complaints
      with html.form().classes(add="w-full grid grid-cols-2 lg:grid-cols-4 gap-1 lg:gap-3"):
        #Complaint1
        ui.input(label="1ST COMPLAINT").props(add=f"clearable").classes(add="bg-white shadow-md shadow-[#07004d] rounded px-5 text-base").bind_value(complaints,"complaint1")
        #Complaint2
        ui.input(label="2ND COMPLAINT").props(add="clearable").classes(add="bg-white shadow-md shadow-[#07004d] rounded px-5 text-base").bind_value(complaints,"complaint2")
        #Complaint3
        ui.input(label="3RD COMPLAINT").props(add="clearable").classes(add="bg-white shadow-md shadow-[#07004d] rounded px-5 text-base").bind_value(complaints,"complaint3")
      
        #Buttons
        ui.button(text="AMPLIFY",color="",on_click=amplify_complaints).classes(add="lg:col-span 2 w-full lg:w-1/2 place-self-center rounded bg-harmony shadow-md shadow-[#07004d] text-yellow-500 text-bold text-xl")
    
      #HPI
      with html.section().classes(add="w-full grow flex flex-col lg:justify-around gap-y-0.5") as hpi_pad:
        HPI()
  
  def PastMedicalSurgicalHistory(self,consultation:dict):
    """"""
    #DATA
    history = consultation["clinical_history"]
    pmh = {
      "hx_id":history["hx_id"],
      "mhx":history["medical_history"],
      "shx":history["surgical_history"],
      "editor_id":self.user.username
    }

    #FXS
    def save_medical_surgical_history():
      #DATABASE SAVING
      status = clients_db.register_pmh(pmh)

      #NOTIFY
      ui.notify(message=status["message"],type=status["type"],position=status["position"])

    #UI
    with html.div().classes(add="w-full flex flex-col lg:flex-row gap-3"):
      #Medical Hx
      ui.textarea(label="MEDICAL HISTORY",placeholder="...").props(add="clearable stack-label input-class='lg:h-[300px]' label-color='#07004d'").classes(add="grow shadow-md shadow-[#07004d] bg-white rounded px-3 text-lg").bind_value(pmh,"mhx")
      #Surgical Hx
      ui.textarea(label="SURGICAL HISTORY",placeholder="...").props(add="clearable stack-label input-class='lg:h-[300px]' label-color='#07004d'").classes(add="grow shadow-md shadow-[#07004d] bg-white rounded px-3 text-lg").bind_value(pmh,"shx")
  
    #BUTTONS
    with html.div().classes(add="w-full flex flex-row justify-center"):
      ui.button(text="SAVE",icon="fa-regular fa-floppy-disk",color="",on_click=save_medical_surgical_history).classes(add="bg-harmony rounded shadow-md shadow-[#07004d] text-lg lg:text-xl text-yellow-500 text-bold")

  def FamilySocialHistory(self,consultation:dict):
    """"""
    #DATA
    history = consultation["clinical_history"]
    fsh = {
      "hx_id":history["hx_id"],
      "fhx":history["family_history"],
      "shx":history["social_history"],
      "editor_id":self.user.username
    }

    #FXS
    def save_family_social_history():
      #DATABASE SAVING
      status = clients_db.register_fsh(fsh)

      #NOTIFY
      ui.notify(message=status["message"],type=status["type"],position=status["position"])

    #UI
    with html.div().classes(add="w-full flex flex-col lg:flex-row gap-3"):
      #Family Hx
      ui.textarea(label="FAMILY HISTORY").props(add="clearable stack-label input-class='lg:h-[300px]' label-color='#07004d'").classes(add="grow shadow-md shadow-[#07004d] bg-white rounded px-3 text-lg").bind_value(fsh,"fhx")
      #Social Hx
      ui.textarea(label="SOCIAL HISTORY").props(add="clearable stack-label input-class='lg:h-[300px]' label-color='#07004d'").classes(add="grow shadow-md shadow-[#07004d] bg-white rounded px-3 text-lg").bind_value(fsh,"shx")
  
    #BUTTONS
    with html.div().classes(add="w-full flex flex-row justify-center"):
      ui.button(text="SAVE",icon="fa-regular fa-floppy-disk",color="",on_click=save_family_social_history).classes(add="bg-harmony rounded shadow-md shadow-[#07004d] text-lg lg:text-xl text-yellow-500 text-bold")

  def PhysicalExamination(self,consultation:dict):
    """"""
    #DATA
    ge = {
      "ge_id":consultation["general_exam"]["ge_id"],
      "editor_id":self.user.username,
      "notes":consultation["general_exam"]["notes"]
    }
    orodental = {
      "orodental_exam_id":consultation["orodental_exam"]["orodental_exam_id"],
      "editor_id":self.user.username,
      "intraoral":consultation["orodental_exam"]["intraoral"] if consultation["orodental_exam"]["intraoral"] else None,
      "extraoral":consultation["orodental_exam"]["extraoral"] if consultation["orodental_exam"]["extraoral"] else None
    }
    

    #FXS
    def save_examination():
      #DATABASE SAVING
      ge_status = clients_db.register_general_exam(ge)
      orodental_status = clients_db.register_orodental_exam(orodental)

      #NOTIFY
      status = set()
      status.add(orodental_status["type"])
      status.add(ge_status["type"])
      if len(status) == 1:
        ui.notify(message="Physical Examination saved successfully!",type="positive",position="top")
      else:
        u.notify(message="Physical Examination not saved!",type="negative",position="center")

    #UI
    with html.div().classes(add="w-full flex flex-col lg:flex-row gap-1"):
      #GE
      ui.textarea(label="GENERAL EXAMINATION").props(add="clearable stack-label input-class='lg:h-[300px]' label-color='#07004d'").classes(add="grow shadow-md shadow-[#07004d] bg-white rounded px-3 text-lg").bind_value(ge,"notes")
      #ODE
      ui.textarea(label="EXTRAORAL EXAMINATION").props(add="clearable stack-label input-class='lg:h-[300px]' label-color='#07004d'").classes(add="grow shadow-md shadow-[#07004d] bg-white rounded px-3 text-lg").bind_value(orodental,"extraoral")
      ui.textarea(label="INTRAORAL EXAMINATION").props(add="clearable stack-label input-class='lg:h-[300px]' label-color='#07004d'").classes(add="grow shadow-md shadow-[#07004d] bg-white rounded px-3 text-lg").bind_value(orodental,"intraoral")
      
    #BUTTONS
    with html.div().classes(add="w-full py-1 flex flex-row justify-center"):
      ui.button(text="SAVE",icon="fa-regular fa-floppy-disk",color="",on_click=save_examination).classes(add="rounded bg-harmony shadow-md shadow-[#07004d] text-lg lg:text-xl text-yellow-500 text-bold")

  def ProvisionalDiagnoses(self,consultation:dict):

    #DATA
    displayable_dxs = consultation["diagnoses"]
    newly_uploaded_dxs = []
    if consultation["diagnoses"] + newly_uploaded_dxs:
      _pdxs = [f"{dx["provisional_icd"]} : {dx["provisional"]}" for dx in consultation["diagnoses"] + newly_uploaded_dxs]
      _ddxs = []
      for consult_diagnosis in consultation["diagnoses"] + newly_uploaded_dxs:
        for consult_ddx in consult_diagnosis["differentials"]:
          _ddxs.append(consult_ddx)
      consultation_dxs = _pdxs + _ddxs
    else:
      consultation_dxs = []
    

    #FXS
    def display_pdxs():

      pdx_panel.clear()
      if displayable_dxs:
        with pdx_panel.classes(remove="flex"):
          for diagnosis in displayable_dxs:
            dx = f"{diagnosis['provisional_icd']} : {diagnosis['provisional']}"
            with ui.list().props(add=f"dense pdx='{dx}'").classes(add="px-2 mb-2 bg-sky-50 rounded shadow-sm shadow-[#07004d] uppercase").on("click",lambda e:DifferentialDiagnosesDialog(raw_pdx=e.sender.props['pdx'],raw_ddxs=e.sender.props['ddxs'])):
              ui.item_label(text=dx).classes(add="text-xl text-sky-700 text-bold")

              for ddx in diagnosis['differentials']:
                ui.item(text=ddx).classes(add="px-2 text-lg text-bold text-harmony italic")
      
      else:
        with pdx_panel.classes(add="flex flex-col justify-center items-center"):
          ui.label("No Provisional Diagnosis!").classes(add="text-red-500 font-bold italic text-xl fa-fade")

    def DifferentialDiagnosesDialog(pdx:str|None=None,raw_pdx:str|None=None,raw_ddxs:list|None=None):
      pdx = f"{pdx.split(':')[0]} : {pdx.split(':')[1]}" if pdx else raw_pdx if raw_pdx else None
      ddxs = set(json.loads(raw_ddxs)) if raw_ddxs else set()

      def _display_pdx(pdx,ddxs):
        _raw_dx = {"provisional_icd":pdx.split(" : ")[0],"provisional":pdx.split(" : ")[1],"differentials":ddxs}
        if pdx not in consultation_dxs:
          newly_uploaded_dxs.append(_raw_dx)
          displayable_dxs.append(_raw_dx)

          dx_data = {"consultation_id":consultation["consultation_id"],"provisional":pdx.lower(),"differentials":json.dumps(list(ddxs))}
          status = clients_db.register_diagnosis(dx_data)
          ui.notify(message=status["message"],type=status["type"],position=status["position"])

        else:
          ui.notify(message="Diagnosis already added!",status="warning",position="top")

        display_pdxs()
        
        ddx_dialog.close()

      def add_ddx_and_display(ddx):
        if not ddx:
          return 

        ddxs.add(f"{ddx.split(':')[0]} : {ddx.split(':')[1]}".lower())
        
        ddx_display.clear()
        with ddx_display:
          for ddx in ddxs:
            ui.chip(text=ddx,color="sky-50",text_color="sky-600",removable=True,on_value_change=lambda e:remove_ddx_and_display(e.sender._text)).props(add="icon-remove='fas fa-circle-xmark' ripple").classes(add="rounded shadow-sm shadow-[#07004d] m-0 pl-2 pr-5 py-1 text-lg text-wrap text-bold animate__animated animate__fadeIn")
       
      def remove_ddx_and_display(ddx):
        ddxs.remove(ddx)
        
        ddx_display.clear()
        with ddx_display:
          for ddx in ddxs:
            ui.chip(text=ddx,color="sky-50",text_color="sky-600",removable=True,on_value_change=lambda e:remove_ddx_and_display(e.sender._text)).props(add="icon-remove='fas fa-circle-xmark' ripple").classes(add="rounded shadow-sm shadow-[#07004d] m-0 pl-2 pr-5 py-1 text-lg text-bold animate__animated animate__fadeIn")
      
      def delete_diagnosis(pdx):
        pass

      with ui.dialog().props(add="transition-show='jump-up' transition-hide='jump-down' transition-duration='500' ") as ddx_dialog,html.div().style(add="min-width:50%;min-height:60%;").classes(add="bg-sky-100 p-0.5 flex flex-col items-center gap-y-3"):
        ui.label(text=pdx).classes(add="w-full p-3 bg-harmony text-center text-yellow-500 text-2xl text-bold")

        ui.select(options=self.diagnoses,label="DIFFERENTIAL DIAGNOSIS",with_input=True,on_change=lambda e:add_ddx_and_display(ddx=e.value)).props(add="clearable").classes(add="lg:w-3/5 mx-5 px-5 rounded shadow-md shadow-[#07004d] bg-white text-lg")
        
        with html.div().classes(add="w-full grid grid-cols-1 gap-y-3 p-1") as ddx_display:
         pass
        
        ui.space()
        with html.div().classes(add=f"w-full p-3 justify-self-end flex flex-row justify-center gap-5"):
          ui.button(text="save diagnosis",color="",on_click=lambda e:_display_pdx(pdx=pdx,ddxs=ddxs)).classes(add="bg-harmony text-yellow-500 text-lg lg:text-xl")
          ui.button(text="delete diagnosis",color="",on_click=lambda e:delete_pdx(pdx=raw_pdx)).classes(add="hidden bg-harmony text-red-500 text-lg lg:text-xl")
    
      ddx_dialog.open()

    #UI
    with html.section().classes(add="w-full p-2 lg:h-full flex flex-col items-center gap-3"):
      #Dx Selector
      ui.select(options=self.diagnoses,label="PROVISIONAL DIAGNOSIS",with_input=True,on_change=lambda e:DifferentialDiagnosesDialog(pdx=e.value)).props(add="clearable").classes(add="lg:w-3/5 px-5 rounded shadow-md shadow-[#07004d] bg-white text-lg")

      #Clinical Summary
      with html.div().classes(add="lg-show grow w-full"):
        ui.label('')

    #Display
    with html.section().classes(add="grow p-2 w-full lg:h-full") as pdx_panel:
      display_pdxs()

  def DefinitiveDiagnoses(self,consultation:dict):
    #DATA
    consultation_dxs = consultation["diagnoses"]
    selectable_diagnoses = [f"{dx['provisional_icd'].upper()} : {dx['provisional'].title()}" for dx in consultation_dxs]
    _ddxs = []
    for dx in consultation_dxs:
      for ddx in dx["differentials"]:
        _ddxs.append(ddx.title())
    selectable_diagnoses.extend(_ddxs)
    def_dxs = [f"{dx['definitive_icd'].upper()} : {dx['definitive'].title()}" for dx in consultation_dxs if dx["definitive"]]

    #FXS
    def display_dxs():
      
      dx_panel.clear()
      if def_dxs:
        with dx_panel.classes(remove="justify-center items-center",add="gap-3"):
          for dx in def_dxs:
            ui.chip(text=dx,color="sky-50",text_color="sky-700").props(add=" icon-remove='fa-regular fa-circle-xmark' ripple").classes(add=f"shadow-[#07004d] w-full rounded shadow-sm m-0 pl-2 pr-5 py-1 text-xl text-bold uppercase")
      
      else:
        with dx_panel.classes(add="flex flex-col justify-center items-center"):
          ui.label("No definitive diagnosis saved!").classes(add="text-bold italic text-red-500 text-xl fa-fade")
      
    def save_diagnosis(dx:str):
      if not dx:
        return

      if dx in def_dxs:
        ui.notify(message="Diagnosis already saved!",position="top",type="warning")
        return

      icd,defn = dx.split(" : ")[0].lower(),dx.split(" : ")[1].lower()
      
      #Save Dx
      for diagnosis in consultation_dxs:
        if diagnosis["provisional_icd"].lower() == icd:
          data = {"diagnosis_id":diagnosis["diagnosis_id"],"definitive_icd":icd,"definitive":defn,"definitive_generic":icd.split(".")[0] if "." in icd else icd}
          clients_db.register_diagnosis(data)
          
        else:
          if dx.lower() in [ddx.lower() for ddx in diagnosis["differentials"]]:
            data = {"diagnosis_id":diagnosis["diagnosis_id"],"definitive_icd":icd,"definitive":defn,"definitive_generic":icd.split(".")[0] if "." in icd else icd}
            clients_db.register_diagnosis(diagnosis=data)

      
      #Display
      def_dxs.append(f"{icd.upper()} : {defn.title()}")

      display_dxs()

    #UI
    with html.section().classes(add="w-full lg:w-auto p-2 lg:h-full flex flex-col items-center gap-3"):
      #Dx Selector
      ui.select(options=selectable_diagnoses,label="DEFINITIVE DIAGNOSIS",with_input=True,on_change=lambda e:save_diagnosis(dx=e.value)).props(add="clearable").classes(add="lg:w-3/5 px-5 rounded shadow-md shadow-[#07004d] bg-white text-lg")

      #Clinical Summary
      with html.div().classes(add="lg-show grow w-full"):
        ui.label('')

    #Display
    with html.section().classes(add="p-2 w-full lg:w-auto lg:h-full flex flex-col") as dx_panel:
      display_dxs()

class ImagingsForm():
  """A class to display form inputs fo requesting imagings"""

  def __init__(self,parent,visit:dict,attendee_id:str):
    #DATA
    self.parent,self.visit,self.attendee_id = parent,visit,attendee_id
    self.initial_data()
    
    #UI
    #Imaging select
    with html.div().classes(add="w-full lg:w-auto lg:h-full flex flex-col"):
      with html.section().classes(add="w-full p-5 flex flex-row justify-center"):
        ui.select(options=self.selectable_imagings,label="IMAGINGS",on_change=lambda e:self.ImagingDialog(e.value)).props(add="clearable stacked-label").classes(add="w-52 px-5 rounded shadow-md shadow-[#07004d] bg-white text-lg uppercase")
      
      #Commentary
      with html.section().classes(add="grow lg-show w-full"):
        pass
      
    #Imaging display
    with html.div().classes(add="grow w-full lg:w-auto lg:h-full p-2  flex flex-col gap-3") as self.imaging_details_display:
      self.display_imagings()

  #FUNCTIONALITIES
  def initial_data(self):
    self.insurance_authorization_no = self.visit["consultations"][0]["payment"]["authorization_no"]
    self.imagings = [self.format_imaging(service) for service in get_services() if service["type"] == "imaging"]
    self.visit_imagings = self.visit["imagings"]
    self.selectable_imagings = [imaging["name"].upper() for imaging in self.imagings]
    
  def save_imaging(self,imaging:dict):
    """A method to save the imaging(s) in the database"""

    self.visit_imagings.append(imaging)

    status = clients_db.register_imaging(imaging)
    ui.notify(message=status["message"],type=status["type"],position=status["position"])
      
    self.display_imagings()

    #MAIN UI UPDATE
    self.parent.initial_data()

    self.imaging_dialog.close()
 
  def cancel_imaging(self,imaging_id:str):
    """Cancel imaging request"""

    clients_db.update_imaging(imaging_data={"imaging_id":imaging_id},delete=True)
  
  def format_imaging(self,imaging):
    if self.visit["payment_mode"] != "cash":
      imaging_payment_schemes = [scheme for scheme in imaging["schemes"] if scheme["scheme_name"] == self.visit["payment_mode"].lower() and scheme["active"]]
      if imaging_payment_schemes:
        imaging_payment_scheme = imaging_payment_schemes[0]
        payment_mode = self.visit["payment_mode"]
      else:
        imaging_payment_scheme = [scheme for scheme in imaging_payment_schemes if scheme["scheme_name"] == "cash"][0]
        payment_mode = "cash"
    else:
      imaging_payment_scheme = [scheme for scheme in imaging["schemes"] if scheme["scheme_name"] == "cash" and scheme["active"]][0]
      payment_mode = "cash"
    
    visit_id = self.visit["visit_id"]
    imaging_id = f"{visit_id}img{uuid.uuid4()}"
    imaging_price = [price for price in imaging_payment_scheme["prices"] if price["active"]][0]

    displayable_price = f"{imaging_price['min']:,.2f} - {imaging_price['max']:,.2f} TZS" if imaging_price["price_range"] else f"{imaging_price[self.visit['package']]:,.2f} TZS"
    db_price = None if imaging_price["price_range"] else imaging_price[f"{self.visit["package"]}"]

    imaging.update({
      "visit_id":visit_id,
      "imaging_id":imaging_id,
      "attendee_id":self.attendee_id,
      "request_time":datetime.now(),
      "displayable_price":displayable_price,
      "study":imaging["name"],
      "notes":None,
      "cancelled":False,
      "processed":False,
      "payment":{
        "visit_id":visit_id,
        "payment_id":f"{imaging_id}pay{uuid.uuid4()}",
        "authorization_no":self.insurance_authorization_no,
        "payment_mode":payment_mode,
        "cost":db_price,
        "billed":True,
        "paid":False
      }
    })

    return imaging


  #DISPLAYS
  def display_imagings(self):
    """A method to display diagnoses from db"""
    
    self.imaging_details_display.clear()
    if self.visit_imagings:
      with self.imaging_details_display:
        for imaging in self.visit_imagings:
          ui.chip(text=imaging["study"].title(),color="sky-50",text_color=f"{'green-900' if imaging["processed"] else 'sky-700'}",removable=False if imaging["processed"] else True,on_click=lambda e:self.ImagingsDisplayDialog([img for img in self.visit_imagings if img['imaging_id'] == e.sender.props['id']][0]),on_value_change=lambda e:self.cancel_imaging(imaging["imaging_id"])).props(add=f"id={imaging['imaging_id']} icon-remove='fa-regular fa-circle-xmark' ripple").classes(add=f"{'ring-1 ring-green-600 shadow-green-900' if imaging['processed'] else 'shadow-[#07004d]'} w-full rounded shadow-sm m-0 pl-2 pr-5 py-1 text-xl text-bold uppercase")
    else:
      with self.imaging_details_display.classes(add="justify-center items-center"):
        ui.label("No imaging requested!").classes(add="text-bold italic text-red-500 text-xl fa-fade")

  def ImagingDialog(self,imaging:str):
    """A method to display a dialog for differential diagnoses"""

    if not imaging:
      return
    
    #Notification if imaging already ordered
    if imaging.lower() in [imaging["study"].lower() for imaging in self.visit_imagings]:
      ui.notify(message="Imaging already requested in this visit",type="warning",position="top")
      return

    #DATA
    imaging = [_imaging for _imaging in self.imagings if _imaging["study"].lower() == imaging.lower()][0]

    #UI
    with ui.dialog().props(add="transition-show='jump-up' transition-hide='jump-down' transition-duration='500' ") as self.imaging_dialog,html.div().style(add="min-width:50%;").classes(add="bg-sky-50 p-0.5"):
      #Imaging details
      with html.div().classes(add="w-full bg-harmony px-1 rounded-t"):
        ui.label(text=imaging["study"]).classes(add="w-full p-3 text-center text-yellow-500 text-3xl text-bold")
      ui.separator()
      with html.div().classes(add="w-full bg-harmony flex flex-row justify-around"):
        #Payment details
        ui.chip(text=imaging["payment"]["payment_mode"],icon="fas fa-wallet",color="",text_color="yellow").classes(add=f"uppercase bg-inherit text-bold text-base")
        ui.chip(text=imaging["displayable_price"],icon="fas fa-coins",color="",text_color="yellow").classes(add="bg-inherit text-bold text-base")

      #Imaging notes
      with html.div().classes(add="w-full flex flex-row justify-center p-3"):
        ui.textarea(label="ADDITIONAL NOTES",placeholder="Write any additional details to help radiologist/radiographer").props(add="clearable stack-label input-class='").classes(add="w-4/5 px-5 rounded shadow-md shadow-[#07004d] bg-white text-lg").bind_value(imaging,"notes")
      #Buttons
      with html.div().classes(add="w-full p-2 flex flex-row justify-around gap-x-2"):
        ui.button(text="REQUEST IMAGING",color="",on_click=lambda e:self.save_imaging(imaging=imaging)).classes(add="rounded bg-harmony shadow-md shadow-[#07004d] text-yellow-500 text-lg text-bold")
        #ui.button(text="CANCEL",icon="fa-regular fa-circle-xmark",color="",on_click=self.cancel_imaging).classes(add="rounded bg-harmony shadow-md shadow-[#07004d] text-red-500 text-lg text-bold")
    
    self.imaging_dialog.open()
  
  def ImagingsDisplayDialog(self,imaging:dict):

    #DATA
    if imaging["processed"]:
      ui.notify(message="Imaging results not yet processed!",type="warning",position="center")
      return
    else:
      imaging_path = Path(f"services/provider/media/imagings/{imaging['visit_id'].upper()}/{'uss' if 'uss' in imaging['study'] else 'xrays'}/{imaging['study'].split(' ')[0]}")
      
      if imaging_path.exists():
        image_paths =list(imaging_path.iterdir())
      else:
        return
      
    #UI
    with ui.dialog().props(add="transition-show='scale' transition-hide='scale' transition-duration='500'") as self.images_display_dialog,html.div().style(add="min-width:100%;min-height:50%;").classes(add="mrelative bg-sky-50 ring-1 ring-sky-500"):
      #Imaging details
      with html.div().classes(add="w-full flex flex-row gap-x-5 bg-gray-900 p-2 rounded-t"):
        #Name
        ui.label(text=imaging["study"].upper()).classes(add="grow p-1 text-center text-yellow-500 text-3xl text-bold")
        #Download Button
        ui.button(icon="fas fa-download fa-lg",color="",on_click=lambda e:self.download_attachments(attachments=image_paths)).classes(add="bg-inherit size-8 rounded-full ring-1 ring-sky-300 shadow-md shadow-sky-500 text-sky-500 text-bold").tooltip("Download Radiographs")
        #Close Button
        ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=self.images_display_dialog.close).classes(add="bg-inherit size-12 text-red-500 text-bold")

      #Images
      with html.div().classes(add="w-full h-[520px] flex flex-row justify-center bg-red-200"):
        with ui.carousel().props(add="animated infinite navigation swipeable thumbnails transition-prev='fade' transition-next='fade' transition-duration='300' navigation-position='bottom' navigation-icon='fas fa-circle-dot' navigation-active-icon='fas fa-eye' control-type='outline' control-text-color='light-blue-5'").classes(add="w-full h-full"):
          for image_path in image_paths:
            with ui.carousel_slide().classes(add="h-full w-full flex flex-col p-0.5"):
              ui.image(source=image_path).props(add="fit='fill'").classes(add="grow w-full")

    self.images_display_dialog.open()

class ImagingResultsForm():

  def __init__(self,visit:dict):
    #DATA
    self.visit = visit
    self.imagings = self.visit["imagings"]
    #UI
    with html.div().classes(add="w-full"):
      with html.div().classes(add="w-full grid grid-rows-3 gap-3"):
        for imaging in self.imagings:
          with ui.button(icon=f"fa-regular fa-{'circle-check' if imaging['processed'] else 'circle-xmark' }",color="gray-800",on_click=lambda e:self.ImageDialog(imaging=[imaging for imaging in self.imagings if imaging["study"] == e.sender.slots["default"].children[0]._text.lower()][0])).classes(add=f"block rounded-full w-fit text-left text-xl text-{'green-600' if imaging['processed'] else 'red-500'} ring-1 ring-blue-500 ring-offset-2 shadow-md shadow-blue-400 text-bold"):
            ui.label(imaging['study']).classes(add="ml-3 text-sky-400")
  
  #FUNCTIONALITIES
  def download_attachments(self,attachments:list[Path]):
    """A method to download attaachments to a local machine"""

    for attachment in attachments:
      ui.download(src=attachment,filename=f"{self.visit['client_name'].split(' ')[0].upper()}_{self.visit['client_name'].split(' ')[-1].upper()}_{self.visit['start_time'].strftime('%Y%m%d')}_{attachments.index(attachment) + 1}")

  #DISPLAYS
  def ImageDialog(self,imaging:dict):

    #DATA
    if not imaging["processed"]:
      ui.notify(message="Imaging results not yet processed!",type="warning",position="center")
      return
    else:
      imaging_path = Path(f"media/imagings/{imaging['visit_id']}/{'uss' if 'uss' in imaging['study'] else 'xrays'}/{imaging['study'].split(' ')[0]}")

      if imaging_path.exists():
        image_paths =list(imaging_path.iterdir())
      else:
        return
      
    #UI
    with ui.dialog().props(add="transition-show='scale' transition-hide='scale' transition-duration='500'") as self.images_dialog,html.div().style(add="min-width:100%;min-height:100%").classes(add="relative bg-sky-50 ring-1 ring-sky-500"):
      #Imaging details
      with html.div().classes(add="w-full flex flex-row gap-x-5 bg-gray-900 p-2 rounded-t"):
        #Name
        ui.label(text=imaging["study"].upper()).classes(add="grow p-1 text-center text-yellow-500 text-3xl text-bold")
        #Download Button
        ui.button(icon="fas fa-download fa-lg",color="",on_click=lambda e:self.download_attachments(attachments=image_paths)).classes(add="bg-inherit size-12 rounded-full ring-1 ring-sky-300 shadow-md shadow-sky-500 text-sky-500 text-bold").tooltip("Download Radiographs")
        #Close Button
        ui.button(icon="fas fa-circle-xmark",color="",on_click=self.images_dialog.close).classes(add="bg-inherit size-12 rounded-full ring-1 ring-red-500 shadow-md shadow-red-500 text-red-500 text-bold")

      #Images
      with html.div().classes(add="w-full h-[520px] flex flex-row justify-center bg-red-200"):
        with ui.carousel().props(add="animated infinite navigation swipeable thumbnails transition-prev='fade' transition-next='fade' transition-duration='300' navigation-position='bottom' navigation-icon='fas fa-circle-dot' navigation-active-icon='fas fa-eye' control-type='outline' control-text-color='light-blue-5'").classes(add="w-full h-full"):
          for image_path in image_paths:
            with ui.carousel_slide().classes(add="h-full w-full p-0.5"):
              ui.image(source=image_path).props(add="fill='cover'")

    self.images_dialog.open()

class ManagementPlanForm():
  """A class to display form inputs fo requesting imagings"""

  def __init__(self,parent,visit:dict,attendee_id:str):
    #DATA
    self.visit,self.parent,self.attendee_id = visit,parent,attendee_id
    self.initial_data()

    #UI
    with html.div().classes(add="w-full grow flex flex-col"):
      #Management selections
      with html.section().classes(add="w-full p-2 flex flex-row justify-center gap-3"):
        ui.select(options=self.selectable_medicines,label="MEDICINES",with_input=True,on_change=lambda e:self.MedicineDialog(medicine=e.value)).props(add="clearable").classes(add="px-5 rounded shadow-md shadow-[#07004d] bg-white text-lg")
        ui.select(options=self.selectable_procedures,label="PROCEDURES",with_input=True,on_change=lambda e:self.ProcedureDialog(procedure=e.value)).props(add="clearable").classes(add="px-5 rounded shadow-md shadow-[#07004d] bg-white text-lg")

      #Management display
      with html.section().classes(add="grow p-0 w-full flex flex-col shadow-sm shadow-[#07004d]"):
        #Tabs
          with html.div().classes(add="w-full px-1 grid grid-cols-10 items-center gap-1"):
            with ui.tabs(value="medicines" if self.visit_medicines else "procedures").props(add="inline-label active-class='text-sky-700 font-bold'").classes(add="col-span-9 py-1") as management_tabs:
              ui.tab(name="medicines",label=f"MEDICINES",icon="fa-solid fa-pills").props(add="dense")
              ui.tab(name="procedures",label=f"PROCEDURES",icon="fas fa-hospital").props(add="dense")
          
          #Panels
          with html.div().classes(add="grow w-full rounded-br flex flex-col"):
            with ui.tab_panels(tabs=management_tabs,value="medicines" if self.visit_medicines else "procedures").props(add="animated infinite transition-prev='jump-right' transition-next='jump-left' transition-duration='700'").classes(add="bg-inherit grow w-full grid grid-cols-1"):
              #Medicines
              with ui.tab_panel(name="medicines").classes(add="w-full h-full p-0 rounded-0 flex flex-col"):
                with html.div().classes(add="grow w-full h-full flex flex-col") as self.medicines_display:
                  self.MedicinesDisplay(medicines=self.visit_medicines)
              
              #Procedures
              with ui.tab_panel(name="procedures").classes(add="w-full h-full p-0 rounded-0 flex flex-col"):
                with html.div().classes(add="grow w-full h-full flex flex-col") as self.procedures_display:
                  self.ProceduresDisplay(procedures=self.visit_procedures)
          
  
  #FUNCTIONALITIES
  def initial_data(self):
    self.insurance_authorization_no = self.visit["consultations"][0]["payment"]["authorization_no"]
    self.procedures = [self.format_procedure(service) for service in get_services() if service["type"] == "procedure"]
    self.formulary_medicines,self.active_medicines = get_formulary(),get_active_medicines()
    self.medicines = [self.format_medicine(medicine) for medicine in self.formulary_medicines]
    
    self.selectable_medicines = [medicine["name"].upper() for medicine in self.medicines]
    self.selectable_procedures = [procedure["name"].upper() for procedure in self.procedures]

    self.visit_medicines,self.visit_procedures = self.visit["medications"] + self.visit["medical_items"],self.visit["procedures"]
    for medicine in self.visit_medicines:
      medicine["id"] = medicine["medication_id"] if "medication_id" in medicine else medicine["medical_item_id"]
  
  def format_medicine(self,medicine):
    """Format medicine from formulary to include details from requisition medicines"""
    #
    if self.visit["payment_mode"] != "cash":
      medicine_payment_schemes = [scheme for scheme in medicine["schemes"] if scheme["scheme_name"] == self.visit["payment_mode"].lower() and scheme["active"]]
      if medicine_payment_schemes:
        medicine_payment_scheme = medicine_payment_schemes[0]
        payment_mode = self.visit["payment_mode"]
      else:
        medicine_payment_scheme = [scheme for scheme in medicine_payment_schemes if scheme["scheme_name"] == "cash"][0]
        payment_mode = "cash"
    else:
      medicine_payment_scheme = [scheme for scheme in medicine["schemes"] if scheme["scheme_name"] == "cash" and scheme["active"]][0]
      payment_mode = "cash"

    visit_id = self.visit["visit_id"]
    medication_id = f"{visit_id}med{uuid.uuid4()}"
    active_requisition_medicines = sorted([req_medicine for req_medicine in self.active_medicines if medicine["medicine_id"] == req_medicine["medicine_id"]],key=lambda med:med["expire_date"])
    medicine_price = [price for price in medicine_payment_scheme["prices"] if price["active"]][0]

    medicine.update(
      {
      "active_medicines":active_requisition_medicines,
      "id":medication_id,
      "visit_id":visit_id,
      "medication_id":medication_id if medicine["category"] == "medicine" else None,
      "medical_item_id":medication_id if medicine["category"] == "medical supply" else None,
      "prescriber_id":self.attendee_id,
      "dosage":"---",
      "prescribed_items_no":0,
      "dispensable_medicines":sum([med["dispensing_balance"] for med in active_requisition_medicines]),
      "dispensed_items_no":0,
      "prescribed_on":datetime.now(),
      "dispensed":False,
      "dispensing_time":None,
      "dispenser_id":None,
      "cancelled":False,
      "cancelled_on":None,
      "cancelled_by":None,
      "payment":{
        "visit_id":visit_id,
        "payment_id":f"{medication_id}pay{uuid.uuid4()}",
        "medication_id":medication_id if medicine["category"] == "medicine" else None,
        "medical_item_id":medication_id if medicine["category"] == "medical supply" else None,
        "authorization_no":self.insurance_authorization_no,
        "payment_mode":payment_mode,
        "unit_price":medicine_price[self.visit['package'].lower()],
        "cost":0,
        "billed":True
      }
    }
    )
    return medicine

  def format_procedure(self,procedure):
    #
    if self.visit["payment_mode"] != "cash":
      procedure_payment_schemes = [scheme for scheme in procedure["schemes"] if scheme["scheme_name"] == self.visit["payment_mode"].lower() and scheme["active"]]
      if procedure_payment_schemes:
        procedure_payment_scheme = procedure_payment_schemes[0]
        payment_mode = self.visit["payment_mode"]
      else:
        procedure_payment_scheme = [scheme for scheme in procedure_payment_schemes if scheme["scheme_name"] == "cash"][0]
        payment_mode = "cash"
    else:
      procedure_payment_scheme = [scheme for scheme in procedure["schemes"] if scheme["scheme_name"] == "cash" and scheme["active"]][0]
      payment_mode = "cash"
    
    visit_id = self.visit["visit_id"]
    procedure_id = f"{visit_id}proc{uuid.uuid4()}"
    procedure_price = [price for price in procedure_payment_scheme["prices"] if price["active"]][0]
    displayable_price = f"{procedure_price['min']:,.2f} - {procedure_price['max']:,.2f} TZS" if procedure_price["price_range"] else f"{procedure_price[self.visit["package"]]:,.2f} TZS"
    db_price = None if procedure_price["price_range"] else procedure_price[self.visit["package"]]

    procedure.update({
      "id":procedure_id,
      "visit_id":visit_id,
      "procedure_id":procedure_id,
      "attendee_id":self.attendee_id,
      "ordered_on":datetime.now(),
      "displayable_price":displayable_price,
      "cancelled":False,
      "done":False,
      "count":1,
      "payment":{
        "visit_id":visit_id,
        "payment_id":f"{procedure_id}pay{uuid.uuid4()}",
        "authorization_no":self.insurance_authorization_no,
        "payment_mode":payment_mode,
        "unit_cost":db_price,
        "cost":db_price,
        "billed":True,
        "paid":False
      }
    })

    return procedure

  def save_medication(self,medicine:dict,prescription:dict):
    """Saving medication details in class state"""
    #CONTROLS
    if prescription["prescribed_items_no"] > medicine["dispensable_medicines"]:
      ui.notify(message=f"Only {medicine['dispensable_medicines']:,.0f} items available",type="warning",position="top")
      return

    #FXS
    def units(medicine:dict,plural:bool=False):
      if plural:
        return 'TABLETS' if medicine['name'].lower().split()[-1].startswith('tab') else 'CAPSULES' if medicine['name'].lower().split()[-1].startswith('cap') else 'BOTTLES' if (medicine['name'].lower().split()[-1].startswith('syrup') or medicine['name'].lower().split()[-1].startswith('susp')) else 'VIALS' if medicine['name'].lower().split()[-1].startswith('vial') else 'AMPOULES' if medicine['name'].lower().split()[-1].startswith('ampoule') else 'ITEMS'
      else:
        return 'TABLET' if medicine['name'].lower().split()[-1].startswith('tab') else 'CAPSULE' if medicine['name'].lower().split()[-1].startswith('cap') else 'BOTTLE' if (medicine['name'].lower().split()[-1].startswith('syrup') or medicine['name'].lower().split()[-1].startswith('susp')) else 'VIAL' if medicine['name'].lower().split()[-1].startswith('vial') else 'AMPOULE' if medicine['name'].lower().split()[-1].startswith('ampoule') else 'ITEM'
    
    def return_medicine(medicine:dict):
      return medicine

    def dispense_medicine(medicine:dict,prescription:dict):
      medicine = medicine
      index,active_meds_count,remainder = 0,len(medicine["active_medicines"]),0

      while index < active_meds_count:
        med = medicine["active_medicines"][index]
        medicine["remainder"] = med["dispensing_balance"] - prescription["prescribed_items_no"]
        medicine["active_medicines"].pop(index)
        if medicine["remainder"] >= 0:
          medicine["requisition_medicine_id"] = med["requisition_medicine_id"]
          med["dispensing_balance"] -= prescription["prescribed_items_no"]
          med["active"] = True if med["dispensing_balance"] else False
          medicine["active_medicines"].insert(index,med)
          remainder = 0
          return
        else:
          med["dispensing_balance"] = 0
          med["active"] = False
          medicine["active_medicines"].insert(index,med)
          prescription["prescribed_items_no"] = remainder = abs(medicine["remainder"])
          index += 1
      
      if remainder:
        with ui.dialog().props(add="transition-show='scale' transition-hide='scale' transition-duration='500'") as confirm_dialog,html.div().style(add="min-width:50%;").classes(add="bg-sky-100 p-0.5 flex flex-col gap-3"):
          with html.div().classes(add="w-full p-5"):
            ui.label(f"Only {medicine['prescribed_items_no'] - remainder} could be prescribed!").classes(add="w-full text-center italic text-lg text-harmony")
            ui.label("Proceed???").classes(add="w-full text-center text-lg text-harmony italic")
          
          with html.div().classes(add="w-full p-3 flex flex-row justify-center gap-x-5"):
            ui.button(text="NO",color="",on_click=confirm_dialog.close).props(add="").classes(add="rounded bg-harmony shadow-md shadow-[#07004d] text-red-500 text-xl text-bold")
            ui.button(text="YES",color="",on_click=lambda e:return_medicine(medicine)).props(add="").classes(add="rounded bg-harmony shadow-md shadow-[#07004d] text-green-500 text-xl text-bold")
        
        confirm_dialog.open()
      
      else:
        return medicine

    #Update state
    if medicine["category"] == "medicine":
      medicine["dosage"] = prescription["dosage"]
      medicine["prescribed_items_no"] = prescription["prescribed_items_no"]
      medicine["payment"]["cost"] = prescription["cost"]
      #dispense_medicine(medicine=medicine,prescription=prescription)
      

      self.visit_medicines.append(medicine)
      
      status = clients_db.register_medication(medication_data=medicine)

    if medicine["category"] == "medical supply":
      medicine["prescribed_items_no"] = prescription["prescribed_items_no_items"]
      medicine["payment"]["cost"] = prescription["cost"]

      dispense_medicine(medicine=medicine,prescription=prescription)

      self.visit_medicines.append(medicine)

      status = clients_db.register_medical_item(medical_item=medicine)

    #NOTIFY
    ui.notify(message=status["message"],type=status["type"],position=status["position"])

    #UI display
    self.medicine_dialog.close()
    self.MedicinesDisplay(medicines=self.visit_medicines)

  def save_procedure(self,procedure:dict):
    """A method to save the procedure(s) in the database"""
    
    self.visit_procedures.append(procedure)
    
    status = clients_db.register_procedure(procedure)

    ui.notify(message=status["message"],type=status["type"],position=status["position"])

    self.ProceduresDisplay(procedures=self.visit_procedures)

    self.procedure_dialog.close()

    self.parent.initial_data()
    self.initial_data()
  

  #DISPLAYS
  def MedicineDialog(self,medicine):
    """Displays dialog for prescription"""
    #CONTROLS
    if not medicine:
      return

    #DATA
    medicine = [_medicine for _medicine in self.medicines if _medicine['name'] == medicine.lower()][0]
    prescription = {
      "dispensing_balance":sum([_medicine["dispensing_balance"] for _medicine in medicine["active_medicines"]]),
      "dosage":None,
      "prescribed_items_no":0,
      "prescribed_items_no_items":0,
      "cost":0
    }

    #FXS
    def TotalCost(value:float=0):
      """A method to display the total cost of medication or medical items"""

      prescription["prescribed_items_no"] = prescription["prescribed_items_no_items"] if medicine["category"] == "medical supply" else prescription["prescribed_items_no"]
      
      total_cost = f"{medicine['payment']['unit_price'] * prescription['prescribed_items_no']:,.2f}" if prescription["prescribed_items_no"] else "0.00"
      
      prescription["cost"] = medicine['payment']['unit_price'] * prescription['prescribed_items_no'] if prescription['prescribed_items_no'] else 0

      total_cost_pad.clear()  
      with total_cost_pad:
        with ui.chip(text=total_cost,icon="fas fa-tags",color="",text_color="yellow").classes(add="bg-inherit mx-0 text-base text-bold"):
          ui.chip(text="TZS",color="",text_color="yellow").classes(add="bg-inherit p-0 m-0 ml-1 text-base")
    
    def units(medicine:dict,plural:bool=False):
      if plural:
        return 'TABLETS' if medicine['name'].lower().split()[-1].startswith('tab') else 'CAPSULES' if medicine['name'].lower().split()[-1].startswith('cap') else 'BOTTLES' if (medicine['name'].lower().split()[-1].startswith('syrup') or medicine['name'].lower().split()[-1].startswith('susp')) else 'VIALS' if medicine['name'].lower().split()[-1].startswith('vial') else 'AMPOULES' if medicine['name'].lower().split()[-1].startswith('ampoule') else 'ITEMS'
      else:
        return 'TABLET' if medicine['name'].lower().split()[-1].startswith('tab') else 'CAPSULE' if medicine['name'].lower().split()[-1].startswith('cap') else 'BOTTLE' if (medicine['name'].lower().split()[-1].startswith('syrup') or medicine['name'].lower().split()[-1].startswith('susp')) else 'VIAL' if medicine['name'].lower().split()[-1].startswith('vial') else 'AMPOULE' if medicine['name'].lower().split()[-1].startswith('ampoule') else 'ITEM'
    
    def icon(medicine:dict):
      return f"fas fa-{'tablets' if medicine['name'].lower().split()[-1].startswith('tab') else 'capsules' if medicine['name'].lower().split()[-1].startswith('cap') else 'prescription-bottle-medical' if (medicine['name'].lower().split()[-1].startswith('syrup') or medicine['name'].lower().split()[-1].startswith('susp')) else 'vials' if medicine['name'].lower().split()[-1].startswith('vial') or medicine['name'].lower().split()[-1].startswith('ampoule') else 'file-prescription'}"
    
    def servicable(medicine:dict):
      if medicine["active_medicines"]:
        return True
      else:
        False

    #UI
    with ui.dialog().props(add="transition-show='scale' transition-hide='scale' transition-duration='500'") as self.medicine_dialog,html.div().style(add="min-width:50%;").classes(add="bg-sky-100 p-0.5 flex flex-col gap-3"):
      #Header
      with html.div().classes(add="w-full bg-harmony px-1 rounded-t"):
        with html.div().classes(add="w-full flex flex-row justify-between"):
          ui.label(text=medicine["name"]).classes(add="grow p-3 text-center text-yellow-400 text-lg lg:text-3xl text-bold uppercase")
          ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=self.medicine_dialog.close).classes(add="text-red-500 text-lg")

        #Separator
        for i in range(2):
          ui.separator().classes(add="w-full bg-[#09026f]")

        #Medication details
        with html.div().classes(add="w-full grid grid-cols-2 lg:flex lg:justify-between gap-1 small-caps"):
          #Payment mode
          ui.chip(text=medicine["payment"]["payment_mode"],icon="fas fa-wallet",color="",text_color="yellow").classes(add=f"bg-inherit uppercase text-bold text-base")
          #Unit cost
          ui.chip(text=f"{medicine["payment"]['unit_price']:,.2f} TZS/{units(medicine=medicine)}",icon="fas fa-coins",color="",text_color="yellow").classes(add="bg-inherit text-bold text-base")
          #Store balance
          ui.chip(text=f"{prescription['dispensing_balance']:,.0f} {units(medicine=medicine,plural=True)}",icon=icon(medicine),color="",text_color="yellow").classes(add="bg-inherit text-bold text-base")
          #Total cost
          with html.span().classes(add="bg-inherit") as total_cost_pad:
            TotalCost()
      
      #Body
      #Medicine
      if medicine["category"] == "medicine":
        with html.form().classes(add="w-full p-3 flex flex-row gap-3"):
          with html.div().classes(add="grow flex flex-row justify-around"):
            #Dosage
            ui.input(label="DOSAGE",placeholder="e.g. 500mg tds for 5 days").props(add=f"{'' if servicable(medicine) else 'disable'} required stack-label").classes(add="w-48 lg:w-auto rounded shadow-md shadow-[#07004d] px-3 bg-white text-lg").bind_value(prescription,"dosage")
            #Quantity
            ui.number(label=f"No of {units(medicine=medicine,plural=True)}",value=1,min=1,on_change=lambda e:TotalCost(value=e.value)).props(add=f"{'' if servicable(medicine) else 'disable'} stack-label").classes(add="w-48 lg:w-auto rounded shadow-md shadow-[#07004d] px-3 bg-white text-lg").bind_value(prescription,"prescribed_items_no")
          #Buttons
          with html.div().classes(add="w-full flex flex-row justify-center gap-2"):
            ui.button(text="SAVE MEDICATION",color="",on_click=lambda e:self.save_medication(medicine=medicine,prescription=prescription)).props(add=f"{'' if servicable(medicine) else 'disable'}").classes(add="rounded bg-harmony shadow-md shadow-[#07004d] text-yellow-500 text-xl text-bold")
          
      if medicine["category"] == "medical supply":
        with html.div().classes(add="w-full p-3 flex flex-row justify-center gap-5"):
          ui.number(label=f"No of {units(medicine=medicine,plural=True)}",value=1,placeholder="e.g. 2",on_change=lambda e:TotalCost(value=e.value)).props(add=f"{'' if servicable(medicine) else 'disable'} stack-label").classes(add="w-48 lg:w-auto rounded shadow-md shadow-[#07004d] px-3 bg-white text-lg").bind_value(prescription,"prescribed_items_no_items")
          ui.button(text="SAVE ITEM",color="",on_click=lambda e:self.save_medication(medicine=medicine,prescription=prescription)).props(add=f"{'' if servicable(medicine) else 'disable'}").classes(add="rounded bg-harmony shadow-md shadow-[#07004d] text-yellow-500 text-xl text-bold")
          
    self.medicine_dialog.open()

  def ProcedureDialog(self,procedure:str,planned:bool=False):
    """"""
    if not procedure:
      return
    
    #DATA
    procedure = [_procedure for _procedure in self.visit_procedures if _procedure["name"].lower() == procedure.lower()][0] if planned else [_procedure for _procedure in self.procedures if _procedure["name"].lower() == procedure.lower()][0]

    #FXS

    #UI
    with ui.dialog().props(add="transition-show='scale' transition-hide='scale' transition-duration='500'") as self.procedure_dialog,html.div().style(add="min-width:50%;").classes(add="bg-sky-100 p-0.5 flex flex-col gap-3"):
      #Header
      with html.section().classes(add="w-full bg-harmony px-1 rounded-t"):
        with html.div().classes(add="w-full flex flex-row justify-between"):
          ui.label(text=procedure["name"]).classes(add="grow p-3 text-center text-yellow-400 text-lg lg:text-3xl text-bold uppercase")
          ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=self.procedure_dialog.close).classes(add="text-red-500 text-lg")

        #Separator
        for i in range(2):
          ui.separator().classes(add="w-full bg-[#09026f]")

        #Medication details
        with html.div().classes(add="w-full grid grid-cols-2 gap-1 small-caps"):
          #Payment mode
          ui.chip(text=procedure["payment"]["payment_mode"],icon="fas fa-wallet",color="",text_color="yellow").classes(add=f"bg-inherit uppercase text-bold text-base")
          #Price
          ui.chip(text=f"{procedure['displayable_price']}",icon="fas fa-coins",color="",text_color="yellow").classes(add="bg-inherit text-bold text-base").bind_value(procedure["payment"],"cost")
      
      #Body
      with html.section().classes(add="w-full p-5 flex flex-row justify-around lg:justify-center gap-3"):
        ui.number(label=f"HOW MANY...?",min=1).props(add="stack-label").classes(add="w-28 rounded shadow-md shadow-[#07004d] px-3 bg-white text-lg").bind_value(procedure,"count")
        ui.button(text="PLAN A PROCEDURE",color="",on_click=lambda e:self.save_procedure(procedure=procedure)).classes(add="rounded bg-harmony shadow-md shadow-[#07004d] text-yellow-500 text-xl text-bold")
    
    self.procedure_dialog.open()
  
  def MedicinesDisplay(self,medicines:list):
    #DATA
    medicines = medicines

    #FXS
    def MedicineStatus(medicine,lg:bool=False):
      """A function to return a styled icon based on status of client's last visit"""
      if lg:
        return f"<span class=' text-bold text-{"gray-600" if medicine["cancelled"] else "green-600" if medicine["dispensed"] else"yellow-600"}'><span class='{"fa-regular fa-circle-xmark" if medicine["cancelled"] else "fa-solid fa-check-double" if medicine["dispensed"] else "fa-solid fa-spinner fa-spin"}'></span><span class='ml-1'>{"Cancelled" if medicine["cancelled"] else "Dispensed" if medicine["dispensed"] else "Awaiting"}</span></span>"
      else:
        return f"<span class=' text-bold text-{"gray-600" if medicine["cancelled"] else "green-600" if medicine["dispensed"] else"yellow-600"}'><span class='{"fa-regular fa-circle-xmark" if medicine["cancelled"] else "fa-solid fa-check-double" if medicine["dispensed"] else "fa-solid fa-spinner fa-spin"}'></span></span>"
    
    def Prescriber(medicine):
      planner = get_staff(username=medicine["prescriber_id"])

      return f"{planner['title']} {planner['last_name']} {planner['first_name'][0]}.".title()

    def Dosage(medicine):
      if "dosage" in medicine:
        if medicine["dosage"]:
          return medicine["dosage"].upper()
        else:
          return "---"
      else:
        return "---"

    #UI
    self.medicines_display.clear()
    if medicines:
      with self.medicines_display.classes(remove="justify-center items-center"):
        #Small Screen
        ui.aggrid(
          {
            "columnDefs":[
              {"headerName":"","field":"sno","width":75},
              {"headerName":"","field":"name","width":300},
              {"headerName":"ITEMS","field":"items_no","width":100},
              {"headerName":"","field":"status","width":50}
            ],
            "rowData":[
              {
                "sno":medicines.index(medicine) + 1,
                "name":medicine["name"].upper(),
                "items_no":f"{medicine["prescribed_items_no"]:,.0f}",
                "status":MedicineStatus(medicine),
                "id":medicine["id"]
              } for medicine in medicines
            ]
          },
          theme="quartz",
          html_columns=[3]
        ).props(add="").classes(add="lg:hidden grow w-full animate__animated animate__fadeIn")
        
        #Large Screen
        ui.aggrid(
          {
            "columnDefs":[
              {"headerName":"","field":"sno","width":50},
              {"headerName":"NAME","field":"name"},
              {"headerName":"DOSAGE","field":"dosage"},
              {"headerName":"DURATION","field":"duration","width":100},
              {"headerName":"PRESCRIBER","field":"prescriber","width":100},
              {"headerName":"STATUS","field":"status","width":100}
            ],
            "rowData":[
              {
                "sno":medicines.index(medicine) + 1,
                "name":medicine["name"].upper(),
                "prescriber":Prescriber(medicine),
                "duration":format_age(medicine["prescribed_on"]),
                "dosage":Dosage(medicine),
                "status":MedicineStatus(medicine=medicine,lg=True),
                "id":medicine["id"]
              } for medicine in medicines
            ]
          },
          theme="quartz",
          html_columns=[5]
        ).props(add="").classes(add="lg-show grow w-full animate__animated animate__fadeIn")
        

    else:
      with self.medicines_display.classes(add="justify-center items-center"):
        ui.label("No medication/medical item prescribed!").classes(add="text-bold italic text-red-500 text-xl fa-fade")

  def ProceduresDisplay(self,procedures:list):

    #FXS
    def ProcedureStatus(procedure,lg:bool=False):
      """A function to return a styled icon based on status of client's last visit"""
      if lg:
        return f"<span class=' text-bold text-{"gray-600" if procedure["cancelled"] else "green-600" if procedure["done"] else"yellow-600"}'><span class='{"fa-regular fa-circle-xmark" if procedure["cancelled"] else "fa-solid fa-check-double" if procedure["done"] else "fa-solid fa-spinner fa-spin"}'></span><span class='ml-1'>{"Cancelled" if procedure["cancelled"] else "Done" if procedure["done"] else "Awaiting"}</span></span>"
      else:
        return f"<span class=' text-bold text-{"gray-600" if procedure["cancelled"] else "green-600" if procedure["done"] else"yellow-600"}'><span class='{"fa-regular fa-circle-xmark" if procedure["cancelled"] else "fa-solid fa-check-double" if procedure["done"] else "fa-solid fa-spinner fa-spin"}'></span></span></span>"
    
    def ProcedurePlanner(procedure):
      planner = get_staff(username=procedure["attendee_id"])

      return f"{planner['title']} {planner['last_name']} {planner['first_name'][0]}.".title()
    
    def removable(procedure):
      return False if procedure["cancelled"] or procedure["done"] or procedure["payment"]["paid"] else True

    #UI
    self.procedures_display.clear()
    if procedures:
      with self.procedures_display.classes(remove="justify-center items-center"):
        #Small Screen
        ui.aggrid(
          {
            "columnDefs":[
              {"headerName":"","field":"sno","width":50},
              {"headerName":"","field":"name","width":200},
              {"headerName":"COUNT","field":"count","width":100},
              {"headerName":"","field":"status","width":50}
            ],
            "rowData":[
              {
                "sno":procedures.index(procedure) + 1,
                "name":procedure["name"].upper(),
                "count":procedure["count"],
                "status":ProcedureStatus(procedure),
              } for procedure in procedures
            ]
          },
          theme="quartz",
          html_columns=[3]
        ).props(add="").classes(add="lg:hidden grow w-full animate__animated animate__fadeIn")
        
        #Large Screen
        ui.aggrid(
          {
            "columnDefs":[
              {"headerName":"","field":"sno","width":50},
              {"headerName":"NAME","field":"name"},
              {"headerName":"PROCEDURES","field":"count","width":75},
              {"headerName":"PLANNED BY","field":"planner","width":100},
              {"headerName":"DURATION","field":"duration","width":100},
              {"headerName":"STATUS","field":"status","width":110}
            ],
            "rowData":[
              {
                "sno":procedures.index(procedure) + 1,
                "name":procedure["name"].upper(),
                "count":procedure["count"],
                "planner":ProcedurePlanner(procedure),
                "duration":format_age(procedure["ordered_on"]),
                "status":ProcedureStatus(procedure=procedure,lg=True),
              } for procedure in procedures
            ]
          },
          theme="quartz",
          html_columns=[5]
        ).props(add="").classes(add="lg-show grow w-full animate__animated animate__fadeIn")
        
    else:
      with self.procedures_display.classes(add="justify-center items-center"):
        ui.label("No procedure planned!").classes(add="text-bold italic text-red-500 text-xl fa-fade")

  #Counselling
  def save_and_display_counselling_details(self,counselling):
    """multiple Fx"""
    if counselling:
      self.update_counselling(counselling)
      self.update_nonpharmacologicals_count(self.nonpharmacologicals_count + 1)
      self.display_counsellling(counselling=counselling)
      
      if len(counselling.split(" ")) > 5:
        counselling_data = {
          "visit_id":self.visit["visit_id"],
          "nonpharmacological_id":f"{self.visit['visit_id']}NP{self.nonpharmacologicals_count + 1}",
          "attendee_id":self.attendee_id,
          "name":"generic counselling",
          "notes":self.counselling,
          "payment_count":len(self.visit["payments"])
        }

        clients_db.register_nonpharmacological(counselling_data)
  
  def display_counsellling(self,counselling):
    
    self.counselling_display.clear()
    with self.counselling_display:
      ui.label(text="COUNSELLING").classes(add="w-full px-1 bg-gray-800 text-yellow-500 text-start text-xl text-bold")
      ui.markdown(content=self.counselling).classes(add="w-[95%] px-1 text-start")
  
class AppointmentsManager():
  """A class for display and amangemet of appoitments"""
  
  def __init__(self,user,parent=None):
    #DATA
    self.user = user
    if parent:
      self.parent = parent

    self.initial_data()

    self.visit_data = {"client_id":"","visit_id":"","appointment_id":None,"payment_mode":"","service":"","service_option":"","attending_clinician":"","card_no":"","authorization_no":""}

    #UI
    with html.div().style(add="overflow-y:hidden;").classes(add="w-full h-full flex flex-col"):
      self.MainPanel()
    
  #FUNCTIONALITIES
  def initial_data(self):
    self.appointments = get_appointments()
    self.clients = get_clients()
    self.services = {
      "Consultation":["consultant",[service["name"].split(" ")[0] for service in get_services() if service["type"] == "consultation"]],
      "Imaging":["imaging stugy",[service["name"] for service in get_services() if service["type"] == "imaging"]],
      "Procedure":["procedure",[service["name"] for service in get_services() if service["type"] == "procedure"]]
    }
    self.min_period = [staff for staff in get_staffs() if staff["title"] == "master"][0]["registered_on"].strftime("%Y/%m")
    #Weekly view data
    self.target_year = datetime.now().year
    self.today = datetime.now().date()
    self.last_week = self.today + timedelta(days=-7)

    #Monthly view data
    self.picked_year,self.picked_month = datetime.now().year,list(calendar.month_name[1:])[int(datetime.now().month)-1]
    
    self.today_appointments = [appointment for appointment in self.appointments if self.is_in_range(start_date=self.today.strftime("%Y-%m-%d"),end_date=self.today.strftime("%Y-%m-%d"),target_date=appointment["appointment_date"])]

  def is_in_range(self,start_date:str,end_date:str,target_date:date):
    """Returns True if 'target_date' is between 'start_date' and 'end_date'"""
    
    start_date,end_date,target_date = datetime.fromisoformat(start_date).date(),datetime.fromisoformat(end_date).date(),target_date

    if target_date >= start_date and target_date <= end_date:
      return True
    else:
      return False
  
  def last_visit(self,client):
    """A method that takes in client and returns"""
    
    if len(client["visits"]) > 0:
      last_visit = [visit for visit in client["visits"]][-1]
      
      #Active visit status
      if last_visit["is_active"] == True:
        last_visit["status"] = "active"
      else:
        last_visit["status"] = "inactive"
    
      return {"visit_id_index":int(last_visit["visit_id"].split("v")[1]),"time":last_visit["start_time"],"duration":f"{format_age(last_visit['start_time']).split(' ')[0]} {format_age(last_visit['start_time']).split(' ')[1]} ago","status":last_visit["status"]}
    else:
      return {"time":"No prior visit!","duration":"---","status":"---"}
  
  def cancel_appointment(self,appointment:dict):
    """"""
    appointment["cancelled"] = True
    
    status = update_appointment_status(appointment)
    
    ui.notify(message=status["message"],type=status["type"],position=status["position"])
    
    self.initial_data()
    self.AppointmentsCarousel()

  def reschedule_appointment(self,appointment:dict):
    """A method to reschedule an appointment"""
    
    status = reschedule_appointment(appointment)

    ui.notify(message=status["message"],position=status["position"],type=status["type"])
    self.initial_data()
    self.AppointmentsCarousel()

  def initiate_visit(self):
    """A method called from the dialog and create a row in 'visit' table"""
    #Data
    payment_option = self.visit_data["payment_mode"].lower()
    service_option = self.visit_data["service_option"].lower()
    
    #Visit
    visit = {
      "client_id":self.visit_data["client_id"],
      "visit_id":self.visit_data["visit_id"].lower(),
      "payment_mode":self.visit_data["payment_mode"].lower(),"appointment_id":self.visit_data["appointment_id"].lower() if self.visit_data["appointment_id"] else None,
      "attendee_id":self.user.username
    }
    
    #Service & Payment
    selected_service = [service for service in get_services() if service["name"].startswith(service_option)][0]

    #CONSULTATION
    if selected_service["type"] == "consultation":
      #Consultation
      consultation = {
        "visit_id":self.visit_data["visit_id"].lower(),
        "name":selected_service["name"],
        "payment":{
          "payment_mode":payment_option,"cost":selected_service["payment"][payment_option],
          "billed":True,
          "billed_amount":selected_service["payment"][payment_option],
          "authorization_no":self.visit_data["authorization_no"] if payment_option != "cash" else None
        },
        "hx":{},"ge":{},"orodental":{},"cns":{},"cvs":{},"rs":{},"abd":{},"gus":{},"mss":{},"derma":{},"dx":{}
      }
      #Triage
      vitals = {
        "visit_id":self.visit_data["visit_id"].lower(),
        "vitals_id":f"{self.visit_data['visit_id'].lower()}vs1",
        "payment":{
          "visit_id":self.visit_data["visit_id"].lower(),
          "payment_id":f"{self.visit_data['visit_id'].lower()}vs1pay1",
          "payment_mode":self.visit_data["payment_mode"].lower(),
          "cost":0,
          "authorization_no":self.visit_data["authorization_no"] if payment_option != "cash" else None,
          "billed":True
        }
      }
      anthrops = {
        "visit_id":self.visit_data["visit_id"].lower(),
        "anthropometrics_id":f"{self.visit_data['visit_id'].lower()}anp1",
        "payment":{
          "visit_id":self.visit_data["visit_id"].lower(),
          "payment_id":f"{self.visit_data['visit_id'].lower()}anp1pay1",
          "payment_mode":self.visit_data["payment_mode"].lower(),
          "cost":0,
          "authorization_no":self.visit_data["authorization_no"] if payment_option != "cash" else None,
          "billed":True
        }
      }
      status = clients_db.register_visit(visit)
      clients_db.register_consultation(consultation)
      clients_db.register_triage({"vitals":vitals,"anthropometrics":anthrops})
        
    #TRIAGE
    if selected_service["type"] == "triage":
      vitals = {
        "visit_id":self.visit_data["visit_id"].lower(),
        "vitals_id":f"{self.visit_data['visit_id'].lower()}vs1",
        "payment":{
          "visit_id":self.visit_data["visit_id"].lower(),
          "payment_id":f"{self.visit_data['visit_id'].lower()}vs1pay1",
          "payment_mode":self.visit_data["payment_mode"].lower(),"cost":selected_service["payment"][payment_option]/2,
          "authorization_no":None,
          "billed":True
        }
      }
      anthrops = {
        "visit_id":self.visit_data["visit_id"].lower(),
        "anthropometrics_id":f"{self.visit_data['visit_id'].lower()}anp1",
        "payment":{
          "visit_id":self.visit_data["visit_id"].lower(),
          "payment_id":f"{self.visit_data['visit_id'].lower()}anp1pay1",
          "payment_mode":self.visit_data["payment_mode"].lower(),"cost":selected_service["payment"][payment_option]/2,
          "authorization_no":None,
          "billed":True
        }
      }
      status = clients_db.register_visit(visit)
      clients_db.register_triage({"vitals":vitals,"anthropometrics":anthrops})
      
    #LABWORK
    elif selected_service["type"] == "laboratory":
      pass

    #Notification
    ui.notify(message=status["message"],position=status["position"],type=status["type"])
    
    #UI UPDATE
    self.initial_data()
    self.AppointmentsCarousel()

  #UI
  def MainPanel(self):
    #Header
    with html.div().classes(add="w-full bg-[#07004d] p-1 rounded-t flex grid lg:grid-cols-4 gap-0.5"):
      #Title
      with html.div().classes(add="lg:col-span-2 w-full rounded-t px-1 py-0.5 bg-inherit"):
        ui.label("APPOINTMENTS").style(add="text-shadow:2px 2px #505050").classes(add="bg-inherit text-yellow-500 text-bold text-2xl")
    
      #Toggle buttons
      with html.div().classes(add="lg:col-span-2 w-full bg-inherit lg:grid grid-cols-2 gap-1"):
        self.duration_toggle = ui.toggle(options=["daily","weekly","monthly","annual"],value="daily",on_change=lambda e:self.SelectionPanel(duration=e.value)).props(add="glossy spread color='bg-inherit' size='md' toggle-color='bg-inherit' text-color='yellow-400' toggle-text-color='sky-400'").classes(add="lg:justify-self-end align-self-center w-full lg:w-fit lg:rounded-full lg:ring-1 ring-blue-500 text-bold")
      
        #Default selection panel
        with html.div().classes(add="w-full flex flex-row justify-center") as self.selection_panel:
          self.SelectionPanel(duration=self.duration_toggle.value)

    #Appointments panel
    with html.div().classes(add="grow w-full rounded-b") as self.appointments_carousel_pad:
      self.AppointmentsCarousel()
  
  def AppointmentsCarousel(self):
    #DATA
    default_month_start_date = f"{datetime.now().strftime('%Y-%m')}-01"
    default_month_end_date = f"{datetime.now().strftime('%Y-%m')}-{calendar.monthrange(datetime.now().year,datetime.now().month)[1]}"
    default_year_start_date = f"{self.picked_year}-01-01"
    default_year_end_date = f"{self.picked_year}-12-31"
    #UI
    self.appointments_carousel_pad.clear()
    with self.appointments_carousel_pad:
      with ui.carousel().props(add="animated transition-prev='jump-right' transition-next='jump-left' transition-duration='500'").classes(add="w-full h-full rounded-b").bind_value(self.duration_toggle) as self.appointments_carousel:
        
        with ui.carousel_slide(name="daily").classes(add="q-pa-none"):
          with html.div().classes(add="w-full h-full rounded-b") as self.daily_appointments_panel:
            self.AppointmentsDisplay(start_date=self.default_picked_date.value,end_date=self.default_picked_date.value)
            
        with ui.carousel_slide(name="weekly").classes(add="q-pa-none"):
          with html.div().classes(add="w-full h-full") as self.weekly_appointments_panel:
            self.AppointmentsDisplay(start_date=self.last_week.strftime("%Y-%m-%d"),end_date=self.today.strftime("%Y-%m-%d"))
        
        with ui.carousel_slide(name="monthly").classes(add="q-pa-none"):
          with html.div().classes(add="w-full h-full") as self.monthly_appointments_panel:
            self.AppointmentsDisplay(start_date=default_month_start_date,end_date=default_month_end_date)
        
        with ui.carousel_slide(name="annual").classes(add="q-pa-none"):
          with html.div().classes(add="w-full h-full") as self.annual_appointments_panel:
            self.AppointmentsDisplay(start_date=default_year_start_date,end_date=default_year_end_date)

  def SelectionPanel(self,duration:str):
    """"""
    #UI
    self.selection_panel.clear()
    with self.selection_panel:
      if duration == "daily":
        with ui.input(label="PICK DATE",value=datetime.now().strftime("%Y-%m-%d"),on_change=lambda e:self.load_appointments(duration=self.duration_toggle.value,date=e.value)).props(add="autogrow dense filled hidden-bottom-space readonly standout input-class='text-white text-bold' label-color='sky-300'").classes(add="w-fit bg-inherit rounded-full lg:ring-1 ring-blue-400 text-sky-50 text-xl animate__animated animate__zoomIn") as self.default_picked_date:
          with ui.dialog().props(add=" transition-show='jump-up' transition-hide='jump-down' transition-duration='300'").classes(add="ring-1 ring-blue-500") as daily_calendar:
            ui.date(value=datetime.now(),on_change=daily_calendar.close).props(add=f"bordered square today-btn color='harmony' event-color='orange' no-unset today-btn first-day-of-week='1'").bind_value(self.default_picked_date)
          with self.default_picked_date.add_slot("prepend"):
            ui.icon("fas fa-calendar-check fa-xl",color="sky-500").on("click",daily_calendar.open).classes(add="hover:scale-[1.1]")

      if duration == "weekly":
        now = datetime.now()
        today = now.date().strftime("%Y-%m-%d")
        last_week = (now.date() + timedelta(days=-7)).strftime("%Y-%m-%d")
        input_range:str = f"{last_week} | {today}"
        
        #Date range picker
        with ui.input(label="DATE RANGE",value=input_range,on_change=lambda e:self.load_appointments(duration=self.duration_toggle.value,date_range=e.value)).props(add="autogrow dense hidden-bottom-space readonly standout input-class='text-white text-bold' label-color='sky-300'").classes(add="w-3/4 lg:w-full bg-inherit rounded-full lg:ring-1 ring-blue-500 px-7 text-lg animate__animated animate__zoomIn") as date_range_input:
          with ui.dialog() as weekly_calendar:
            ui.date(value=datetime.now(),on_change=weekly_calendar.close).props(add=f"bordered square today-btn color='harmony' event-color='orange' range no-unset today-btn first-day-of-week='1'").bind_value(
              date_range_input,
              forward=lambda x:f'{x["from"]} | {x["to"]}' if x else None,
              backward=lambda x:{'from':x.split(' | ')[0],'to':x.split(' | ')[1]} if ' | ' in (x or '') else None
            )
          with date_range_input.add_slot("prepend"):
            ui.icon("fas fa-calendar-check",color="sky-400").on("click",weekly_calendar.open).classes(add="hover:scale-[1.1]")
    
      if duration == "monthly":
        with ui.button_group().classes(add="bg-inherit w-3/5 lg:w-4/5 flex flex-row gap-3 rounded-full ring-1 ring-blue-400 shadow-md shadow-sky-500 px-3 animate__animated animate__zoomIn"):
          year_label = ui.select(label="YEAR",options=constants.YEARS,on_change=lambda e:self.load_appointments(duration=self.duration_toggle.value)).props(add="dark dense").classes(add="grow pl-2 rounded-l-full text-lg").bind_value(self,"picked_year")
          with year_label.add_slot("prepend"):
            ui.icon("fa-regular fa-calendar-check",color="sky-400")
          month_label = ui.select(label="MONTH",options=list(calendar.month_name)[1:],on_change=lambda e:self.load_appointments(duration=self.duration_toggle.value)).props(add="dark dense").classes(add="grow pl-2 rounded-r-full text-lg").bind_value(self,"picked_month")
          with month_label.add_slot("prepend"):
            ui.icon("fa-regular fa-calendar-check",color="sky-400")
        
      if duration == "annual":
        ui.select(label="YEAR",options=constants.YEARS,on_change=lambda e:self.load_appointments(duration=self.duration_toggle.value)).props(add="dark dense hide-bottom-space").classes(add="bg-inherit ring-1 ring-blue-400 shadow-md shadow-sky-500 w-fit rounded-full px-5 text-lg animate__animated animate__zoomIn").bind_value(self,"picked_year")        
    
  def load_appointments(self,duration:str,date=None,date_range=None):
    #Daily
    if duration == "daily":
      self.daily_appointments_panel.clear()
      with self.daily_appointments_panel:
        self.AppointmentsDisplay(start_date=date,end_date=date)
    
    #Weekly
    if duration == "weekly":
      start_date,end_date = date_range.split(" | ")[0],date_range.split(" | ")[1]
      self.weekly_appointments_panel.clear()
      with self.weekly_appointments_panel:
        self.AppointmentsDisplay(start_date=start_date,end_date=start_date)
    
    #Monthly
    if duration == "monthly":
      _month = list(calendar.month_name).index(self.picked_month)
      if _month >=10:
        start_date = f"{self.picked_year}-{_month}-01"
        end_date = f"{self.picked_year}-{_month}-{calendar.monthrange(self.picked_year,_month)[1]}"
      else:
        start_date = f"{self.picked_year}-0{_month}-01"
        end_date = f"{self.picked_year}-0{_month}-{calendar.monthrange(self.picked_year,_month)[1]}"
      
      self.monthly_appointments_panel.clear()
      with self.monthly_appointments_panel:
        self.AppointmentsDisplay(start_date=start_date,end_date=end_date)

    #Annual
    if duration == "annual":
      start_date = f"{self.picked_year}-01-01"
      end_date = f"{self.picked_year}-12-31"

      self.annual_appointments_panel.clear()
      with self.annual_appointments_panel:
        self.AppointmentsDisplay(start_date=start_date,end_date=end_date)
      
  def AppointmentsDisplay(self,start_date:str,end_date:str):
    """"""
    #DATA
    appointments = sorted([appointment for appointment in self.appointments if self.is_in_range(start_date=start_date,end_date=end_date,target_date=appointment["appointment_date"])],key=lambda e:e["appointment_date"],reverse=True)
    #MODS
    def StatusDot(appointment):
      """A function to return a styled icon based on status of client's last visit"""

      status = "active" if appointment["made"] and not (appointment["done"] or appointment["cancelled"]) else "completed" if appointment["done"] else "cancelled" if appointment["cancelled"] else "---"
      return f"<span class='text-bold fa-solid fa-circle { 'text-green-600' if status == 'active' else 'text-yellow-500' if status == 'completed' else 'text-gray-500' if status == 'cancelled' else 'text-red-600'}'></span>"
    
    def GenderIcon(appointment):
      """Returns a styled gender icon based on client's gender"""

      genders = {"male":"mars","female":"venus"}
      colors = {"male":"sky-600","female":"pink-600"}
      return f"<span class='fa-solid fa-{genders[appointment['client_gender'].lower()]} text-{colors[appointment['client_gender'].lower()]}'></span>"
    
    #UI
    #Large screen
    ui.aggrid(
      {
        "columnDefs":[
          {"headerName":"S/N","field":"sno","width":100},
          {"headerName":"CLIENT ID","field":"client_id","filter":"agTextColumnFilter"},
          {"headerName":"NAME","field":"name","filter":"agTextColumnFilter"},
          {"headerName":"AGE","field":"age"},
          {"headerName":"GENDER","field":"gender"},
          {"headerName":"ADDRESS","field":"address"},
          {"headerName":"APPOINTMENT DATE","field":"appt_date"},
          {"headerName":"STATUS","field":"status","cellClassRules":{
            "text-green-600 text-bold":"x == 'Active'",
            "text-yellow-600 text-bold":"x == 'Completed'",              "text-red-600 text-bold":"x == 'Cancelled'"
          }}
        ] ,
        "rowData":[{
          "sno":appointments.index(appointment) + 1,
          "client_id":appointment["client_id"],
          "name":appointment["client_name"].title(),
          "age":format_age(appointment["client_birthdate"]),
          "gender":appointment["client_gender"].capitalize(),
          "address":appointment["client_address"].capitalize(),
          "appt_date":appointment["appointment_date"].strftime("%d %b %Y"),
          "status":"Active" if appointment["made"] and not (appointment["done"] or appointment["cancelled"]) else "Completed" if appointment["done"] else "Cancelled" if appointment["cancelled"] else "---",
        } for appointment in appointments]
      },theme="quartz").classes(add="lg-show w-full h-full animate__animated animate__fadeIn animate_delay-2s animate__slow").on("cellClicked",lambda e:self.AppointmentDialog(appointment=[appointment for appointment in appointments if appointment["client_id"] == e.args["data"]["client_id"]][0]))
    
    #Small Screens
    ui.aggrid(
          {
            "columnDefs":[
              {"headerName":"","field":"status","width":75},
              {"headerName":"CLIENT ID","field":"client_id","filter":"agTextColumnFilter","floatingFilter":True,"width":160},
              {"headerName":"NAME","field":"name","filter":"agTextColumnFilter","floatingFilter":True,"width":300},
              {"headerName":"","field":"gender","align":"left","width":75},
              {"headerName":"AGE","field":"age","width":150}
            ],
            "rowData":[
              {
                "status":StatusDot(appointment),
                "client_id":appointment["client_id"],
                "name":appointment["client_name"].title(),
                "age":f"{format_age(appointment['client_birthdate']).split(' ')[0]} {format_age(appointment['client_birthdate']).split(' ')[1]}",
                "gender":GenderIcon(appointment)
              } for appointment in appointments
            ],
          },
          html_columns=[0,3],
          theme="quartz"
        ).classes(add="lg:hidden w-full h-full animate__animated animate__fadeIn animate__slow").on("cellClicked",lambda e:self.AppointmentDialog(appointment=[appointment for appointment in appointments if appointment["client_id"] == e.args["data"]["client_id"]][0]))
    
  def AppointmentDialog(self,appointment:dict):
    """"""
    #DATA
    if "receptionist" not in self.user.roles:
      return
    
    details = {
      "name":appointment["client_name"],
      "short_name":f"{appointment['client_name'].split(' ')[0]} {appointment['client_name'].split(' ')[1] if len(appointment['client_name'].split(' ')) > 2 else ''} {appointment['client_name'].split(' ')[2]}".title(),
      "age":format_age(appointment["client_birthdate"]),
      "gender":appointment["client_gender"],
      "address":appointment["client_address"]
    }
    #FXS
    def close_dialog():
      self.AppointmentsCarousel()

    #UI
    with ui.dialog() as self.appointment_dialog,html.div().classes(add="w-fit p-0.5 bg-sky-50"):
      #Header
      with html.div().classes(add="w-full grid grid-cols-11 bg-[#07004d]"):
        with html.div().classes(add="col-span-10 bg-inherit"):
          ClientCard(details=details)
        ui.button(icon="fas fa-circle-xmark",color="",on_click=close_dialog).classes(add="col-span-1 bg-inherit text-red-600 text-bold text-base")
      #Appointment
      with html.div().classes(add="w-full p-2 flex flex-row justify-between") as self.reschedule_panel:
        #Initiate visit button
        ui.button(text="initiate visit",color="gray-900",on_click=lambda e:self.parent.NewVisitDialog(client=[client for client in self.clients if client['client_id'] == appointment['client_id']][0],appointment_id=appointment["appointment_id"],appointments=True)).props(add="bordered dense glossy").classes(add="rounded shadow-md shadow-[#07004d] text-sky-300 text-xl text-bold")
        #Reschedule button
        ui.button(text="reschedule",color="gray-900",on_click=lambda e:self.ReschedulePanel(appointment["appointment_id"])).props(add="bordered dense glossy").classes(add="rounded shadow-md shadow-[#07004d] text-sky-300 text-xl text-bold")
        #Cancel button
        ui.button(text="cancel",color="gray-900",icon="fas fa-calendar-xmark",on_click=lambda e:self.cancel_appointment(appointment)).props(add="bordered dense glossy").classes(add="rounded shadow-md shadow-[#07004d] text-sky-300 text-xl text-bold")
    
    if appointment["cancelled"] or appointment["done"]:
      return
    else:
      self.appointment_dialog.open()
  
  def NewVisitPanel(self,client:dict,appointment_id:str|None=None):
    #DATA
    self.visit_data["client_id"] = client["client_id"]
    self.visit_data["visit_id"] = f"{client['client_id']}v{self.last_visit(client)['visit_id_index'] + 1}"
    self.visit_data["appointment_id"] = appointment_id

    if client["payment_mode"].lower() == "cash":
      payment_options = [client["payment_mode"].upper()]
    else:
      payment_options = [client["payment_mode"].upper(),"CASH"]
    
    #UI
    self.reschedule_panel.clear()
    with self.reschedule_panel:
      with html.div().classes(add="w-full flex flex-col gap-3"):
        #Service
        with html.div().classes(add="w-full p-1 grid grid-cols-5 gap-3"):
          #Service type
          ui.select(options=list(self.services),label="SERVICE",value="Consultation",on_change=self.ServiceOptions).classes(add="col-span-2 ring-2 ring-sky-600 shadow-md shadow-blue-400 bg-sky-50 rounded-sm px-2 text-lg").bind_value_to(self.visit_data,"service")
          #Service pad
          with html.div().classes(add="col-span-2") as self.service_pad:
            self.ServiceOptions()
          #Payment mode
          ui.select(options=payment_options,value=payment_options[0].upper(),label="PAYMENT",on_change=self.switch_payment_mode).props(add="disable").classes(add="ring-2 ring-sky-600 shadow-md shaodw-blue-400 bg-sky-50 rounded-sm px-2 text-lg").bind_value_to(self.visit_data,"payment_mode")
        
        #Payment details
        if client["payment_mode"] != "cash":
          ui.separator()
          with html.div().classes(add="w-full p-1 grid grid-cols-3 gap-3"):
            #Card No
            with html.div().classes(add="col-span-2 flex flex-row gap-5") as self.insurance_pad:
              self.CardNumberDisplay(client=client)
            #Authorization details
            with html.div().classes(add="col-span-1") as self.authorization_pad:
              self.AuthorizationPad()
          ui.separator()

        #Action buttons
        with html.span().classes(add="w-full my-2 flex flex-row justify-center gap-3"):
          ui.button(text="initiate visit",color="gray-900",on_click=self.initiate_visit).classes(add="ring-1 ring-blue-500 shadow-md shadow-blue-500  text-sky-300 text-xl text-bold")
  
  def ServiceOptions(self):
    """A method to display service_options"""
    #DATA
    service:str = self.visit_data["service"].capitalize()
    
    #UI
    self.service_pad.clear()
    with self.service_pad:
      ui.select(options=[_service.title() for _service in self.services[service][1]],value=self.services[service][1][0].title(),label=self.services[service][0].upper()).props(add="name='visit-consult' id='visit-consult'").classes(add="w-full ring-2 ring-sky-600 shadow-md shadow-blue-400 bg-white rounded px-2 text-xl").bind_value_to(self.visit_data,"service_option")

  def switch_payment_mode(self):
    """A method to change display based on payment mode selected in visit initiation"""
    
    #DATA
    scheme = self.visit_data["payment_mode"]
    
    if scheme == "CASH":
      self.insurance_pad.clear()
      self.authorization_pad.clear()
    else:
      self.CardNumberDisplay()
      self.AuthorizationPad()

  def ReschedulePanel(self,appointment_id:str):
    """A method to display dialog for rescheduling an appointment"""
    #DATA
    _tomorrow = datetime.now() + timedelta(days=1)
    if _tomorrow.month >=10:
      tomorrow = f"{_tomorrow.year}/{_tomorrow.month}/{_tomorrow.day}"
    else:
      tomorrow = f"{_tomorrow.year}/0{_tomorrow.month}/{_tomorrow.day}"
    
    appointment = {"new_date":"","appointment_id":appointment_id}

    #UI
    self.reschedule_panel.clear()
    with self.reschedule_panel.classes(add="p-0.5 flex-col gap-2",remove="p-2 flex-row"):
      ui.date(value=datetime.now()+timedelta(days=1)).props(add="bordered dense glossy square today-btn color='harmony' event-color='orange'").classes(add="w-full shadow-md shadow-[#07004d] text-[#07004d] text-xl text-bold").bind_value_to(appointment,"new_date")
      ui.button(text="reschedule",color="",on_click=lambda e:self.reschedule_appointment(appointment)).classes(add="w-full bg-[#07004d] text-lg text-sky-300 text-bold")

class ProceduresManager():
  """A class of UI for managing consultations"""
  
  def __init__(self,user):
    self.user = user
    self.initial_data()

    #UI
    with html.div().classes(add="grow w-full bg-inherit flex flex-col") as self.main_panel:
      #Header
      #Separator
      for i in range(2):
        ui.separator().classes(add="w-full bg-[#09026f]")

      ui.label("PROCEDURES").classes(add="w-full rounded-none bg-harmony text-bold text-xl lg:text-3xl text-yellow-500 p-2")
      with html.div().classes(add="grow w-full rounded-b flex flex-col") as self.procedures_panel:
        self.ProceduresDisplay(visits=self.procedure_visits)

  #FUNCTIONALITIES
  def initial_data(self):
    _procedure_visits = get_active_procedures()
    done_procedure_visits = sorted([procedure_visit for procedure_visit in _procedure_visits if self.procedures_status(procedure_visit["procedures"]) == "done"],key=lambda e:e["procedures"][-1]["done_on"],reverse=True)
    pending_procedure_visits = [procedure_visit for procedure_visit in _procedure_visits if self.procedures_status(procedure_visit["procedures"]) == "pending" or self.procedures_status(procedure_visit["procedures"]) == "partial"]
    undone_procedure_visits = sorted([procedure_visit for procedure_visit in _procedure_visits if self.procedures_status(procedure_visit["procedures"]) == "not done"],key=lambda e:e["procedures"][-1]["ordered_on"])
    self.procedure_visits = pending_procedure_visits + undone_procedure_visits + done_procedure_visits
    #Activee Procedures
    self.active_procedures = []
    for visit in _procedure_visits:
      for procedure in visit["procedures"]:
        if not (procedure["done"] or procedure["cancelled"]):
          self.active_procedures.append(procedure)
    
    self.staffs = [f"{staff['first_name']} {staff['last_name']}".title() for staff in get_staffs()[1:]]

  def is_in_range(self,start_date:str,end_date:str,target_date:str):
    """Returns True if 'target_date' is between 'start_date' and 'end_date'"""
    
    start_date,end_date,target_date = datetime.fromisoformat(start_date).date(),datetime.fromisoformat(end_date),datetime.fromisoformat(target_date)

  def procedures_status(self,procedures:list[dict]):
    """Returns value depending on whether the procedure has been done"""
    
    procedures = [procedure for procedure in procedures if not procedure["cancelled"]]
    statuses = set()

    for procedure in procedures:
      if (procedure["payment"]["paid"] or procedure["payment"]["billed"]) and not procedure["done"]:
        statuses.add("pending")
      if (procedure["payment"]["paid"] or procedure["payment"]["billed"]) and procedure["done"]:
        statuses.add("done")
      if not (procedure["payment"]["paid"] or procedure["payment"]["billed"]) and not procedure["done"]:
        statuses.add("not done")
    
    if len(statuses) == 1:
      for status in statuses:
        return status
    else:
      return "partial"
  
  def procedures(self,procedures:list[dict]):
    """Returns a list of procedures"""
    
    procedures_string = ""
    for procedure in procedures:
      if not procedure["cancelled"]:
        _substring = f"<span class='px-1'><i class='fas {'fa-check text-green-500' if procedure['done'] else 'fa-ban text-gray-400' if procedure['cancelled'] else 'fa-xmark text-red-500' if ((procedure['payment']['billed'] or procedure['payment']['paid']) and not procedure['done']) else 'fa-spinner fa-spin text-yellow-500'} fa-lg'></i><i class='ml-1 '>{procedure['name'].title()}</i></span><br>"
        procedures_string += _substring
    
    return procedures_string

  def save_procedure(self,procedure:dict):
    """Saves the findings in the database"""
    visit_id = procedure["visit_id"]

    status = clients_db.update_procedure(procedure=procedure)
    ui.notify(message=status["message"],type=status["type"],position=status["position"])
    
    self.initial_data()
    self.ProceduresPanel(visit=[visit for visit in self.procedure_visits if visit["visit_id"] == visit_id][0])

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

  def procedures_mini(self,visit):
    """Returns a string of html elements for display of services in small screens"""
    procedures = visit["procedures"]
    _done = len([procedure for procedure in procedures if procedure["done"]])
    _cancelled = len([procedure for procedure in procedures if procedure["cancelled"]])
    _pending = len([procedure for procedure in procedures if not (procedure["cancelled"] or procedure["done"])])

    done = pending = cancelled = ""

    if _done:
      done = f"<span class='text-green-600'><span class='fas fa-check-double'></span><sup class='ml-0.5 text-bold'>{_done}</sup></span>"

    if _pending:
      pending = f"<span class='text-yellow-600'><span class='fa-solid fa-spinner fa-spin'></span><sup class='ml-0.5 text-bold'>{_pending}</sup></span>"

    if _cancelled:
      cancelled = f"<span class='text-gray-600'><span class='fa-solid fa-ban'></span><sup class='ml-0.5 text-bold'>{_cancelled}</sup></span>"
    
    #Returns
    if _done + _pending + _cancelled:
      return f"<span class='flex flex-row justify-between items-center'>{done}{pending}{cancelled}</span>"
    else:
      return "---"

  #UI
  def ProceduresDisplay(self,visits:dict):
    """A default panel to display procedures"""
    
    self.procedures_panel.clear()
    if visits:
      with self.procedures_panel.classes(remove="items-center justify-center"):
        #Large Screen
        ui.aggrid(
          {
            "columnDefs":[
              {"headerName":"S/N","field":"sno","width":50},
              {"headerName":"CLIENT ID","field":"client_id","filter":"agTextColumnFilter","width":100},
              {"headerName":"NAME","field":"name","filter":"agTextColumnFilter"},
              {"headerName":"AGE","field":"age","width":100},
              {"headerName":"GENDER","field":"gender","width":100},
              {"headerName":"ADDRESS","field":"address","width":120},
              {"headerName":"PROCEDURES","field":"procedures","filter":"agTextColumnFilter","floatingFilter":True}
            ],
            "rowData":[
              {
                "sno":visits.index(visit) + 1,
                "client_id":visit["client_id"],
                "name":visit["client_name"].title(),
                "age":format_age(visit["client_birthdate"]),
                "gender":visit["client_gender"].capitalize(),
                "address":visit["client_address"].title(),
                "procedures":self.procedures(visit["procedures"]),
              } for visit in visits
            ]
          },
          theme="quartz",
          html_columns=[6]
        ).style(add="overflow-x:hidden;").classes(add="lg-show grow w-full animate__animated animate__fadeIn").on("cellClicked",lambda e:self.ProceduresDialog(visit=[visit for visit in self.procedure_visits if visit["client_id"] == e.args["data"]["client_id"]][0]))

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
                "services":self.procedures_mini(visit)
              } for visit in visits
            ]
          },
          theme="quartz",
          html_columns=[2,3]
        ).props(add="").classes(add="lg:hidden grow w-full animate__animated animate__fadeIn").on("cellClicked",lambda e:self.ProceduresDialog(visit=[visit for visit in self.procedure_visits if visit["client_id"] == e.args["data"]["client_id"]][0]))

    else:
      with self.procedures_panel.classes(add="justify-center items-center"):
        ui.label("No procedure(s) planned currently").classes(add="text-red-500 font-bold italic text-xl fa-fade")
    
  def ProceduresDialog(self,visit:dict):
    """A dialog to display details of a procedure visit"""
    
    #DATA
    self.details = {
      "name":visit["client_name"],
      "short_name":f"{visit['client_name'].split()[0]} {visit['client_name'].split()[1][0] if len(visit['client_name'].split(' ')) > 2 else ''} {visit['client_name'].split()[2]}".title(),
      "age":format_age(visit["client_birthdate"],short=True),
      "gender":visit["client_gender"],
      "address":visit["client_address"]
    }
    #FXS
    def close_dialog():
      self.initial_data()
      self.procedures_dialog.close()

    #UI
    with ui.dialog().props(add=f"transition-show='jump-up' transition-hide='jump-down' transition-duration='300'") as self.procedures_dialog,html.div().style(add="min-width:100%;min-height:100%;").classes(add="bg-sky-50 flex flex-col"):
      #Dialog Header
      with html.div().classes(add="bg-harmony w-full p-1 rounded-t flex flex-row items-center"):
        with html.div().classes(add="grow"):
          ClientCard(details=self.details)
        ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=close_dialog).classes(add="size-12 bg-inherit text-rose-600 text-bold text-lg")
      
      #Procedures
      with html.div().classes(add="grow w-full flex flex-col") as self.procedures_dialog_panel:
        self.ProceduresPanel(visit=visit)
    
    self.procedures_dialog.open()

  def ProceduresPanel(self,visit):
    """Panel for procedures listing and processing"""
    #DATA
    _procedures = [procedure for procedure in visit["procedures"]]
    cancelled_procedures = [procedure for procedure in _procedures if procedure["cancelled"]]
    done_procedures = [procedure for procedure in _procedures if procedure["done"]]
    not_done_procedures = [procedure for procedure in _procedures if not (procedure["cancelled"] or procedure["done"])]
    procedures = not_done_procedures + done_procedures + cancelled_procedures
    #UI
    self.procedures_dialog_panel.clear()
    with self.procedures_dialog_panel:
      with ui.scroll_area().classes(add="grow w-full animate__animated animate__fadeIn"):
        for procedure in procedures:
          #Data
          procedure_data = {
            "procedure_id":procedure["procedure_id"],
            "procedure_notes":procedure["procedure_notes"] if procedure["procedure_notes"] else None,
            "performer":f"{get_staff(procedure['performer'])['first_name']} {get_staff(procedure['performer'])['last_name']}".title() if procedure['performer'] else f"{self.user.first_name} {self.user.last_name}".title(),
            "assistant":f"{get_staff(procedure['assistant'])['first_name']} {get_staff(procedure['assistant'])['last_name']}".title() if procedure["assistant"] else None,
          }
          #miniUI
          with ui.expansion(value=True if procedures.index(procedure) == 0 and not (procedure["done"] or procedure["cancelled"]) else False,group="procedures_group").props(add=f"{'disable' if procedure['cancelled'] else ''} duration=500 expand-icon='fas fa-angles-down fa-lg' expand-icon-class='text-harmony text-bold' header-class='q-pa-none {'bg-gray-300' if procedure['cancelled'] else 'bg-sky-100'}'").classes(add="w-full rounded bg-sky-50 shadow-md shadow-[#07004d]") as expansion:
            with expansion.add_slot("header"):
              with html.div().classes(add="w-full grid grid-cols-6"):
                #Study
                ui.chip(text=procedure["name"].title(),text_color="sky-900",color="").classes(add="col-span-6 lg:col-span-2 rounded-sm m-0 px-2 bg-inherit text-xl text-bold")
                #Timeframe
                ui.chip(text=f"{format_age(procedure['ordered_on'])} ago",icon="fa-regular fa-clock fa-lg",text_color="sky-900",color="").classes(add="col-span-2 lg:col-span-1 rounded-sm px-2 bg-inherit text-base text-bold")
                #Payment status
                ui.chip(text="Paid" if procedure["payment"]["paid"] else "Billed" if procedure["payment"]["billed"] else "Not Paid",icon=f"{'fa-regular fa-circle-check' if procedure['payment']['paid'] else 'fa-solid fa-file-invoice' if procedure['payment']['billed'] else 'fa-regular fa-circle-xmark'} fa-lg",text_color="teal" if procedure["payment"]["paid"] else "purple" if procedure["payment"]["billed"] else "red",color="").classes(add="col-span-2 lg:col-span-1 rounded-sm px-2 bg-inherit text-base text-bold")
                #Imaging status
                ui.chip(
                  text="Done" if ((procedure["payment"]["paid"] or procedure["payment"]["billed"]) and procedure["done"]) else "Pending" if ((procedure["payment"]["billed"] or procedure["payment"]["paid"]) and not procedure["done"]) else "Not done",
                  icon=f"{'fa-regular fa-circle-check' if ((procedure['payment']['paid'] or procedure['payment']['billed']) and procedure['done']) else 'fa-solid fa-spinner fa-spin' if ((procedure['payment']['billed'] or procedure['payment']['paid']) and not procedure['done']) else 'fa-regular fa-circle-xmark fa-flip'} fa-lg",
                  text_color="teal" if ((procedure["payment"]["paid"] or procedure["payment"]["billed"]) and procedure["done"]) else "orange" if ((procedure["payment"]["billed"] or procedure["payment"]["paid"]) and not procedure["done"]) else "red",
                  color=""
                  ).classes(add="col-span-2 lg:col-span-1 rounded-sm px-2 bg-inherit text-base text-bold")
            
            if not procedure["cancelled"]:
              with expansion.add_slot("default"):
                with html.div().classes(add="w-full p-1 flex flex-col gap-5"):
                  with html.div().classes(add="w-full grid grid-cols-3 gap-3"):
                    with html.div().classes(add="col-span-3 lg:col-span-1 w-full p-1 flex flex-col gap-2 justify-around"):
                      performer = ui.select(options=self.staffs,value=procedure_data['performer'],label="PERFORMED BY").props(add=f"{'' if procedure['payment']['paid'] or procedure['payment']['billed'] else 'readonly'} stack-label label-color='#07004d'").classes(add="w-full rounded bg-white shadow-md shadow-[#07004d] px-2 text-lg").bind_value(procedure_data,"performer")
                      assistant = ui.select(options=self.staffs,label="ASSISTED BY").props(add=f"{'' if procedure['payment']['paid'] or procedure['payment']['billed'] else 'readonly'} stack-label label-color='#07004d'").classes(add="w-full rounded bg-white shadow-md shadow-[#07004d] px-2 text-lg").bind_value(procedure_data,"assistant")
                    #Findings
                    notes = ui.textarea(label="PROCEDURE NOTES",placeholder="Write your observations and interventions done...").props(add="" if (procedure["payment"]["paid"] or procedure["payment"]["billed"]) else "readonly").props(add="autogrow clearable stack-label input-style='min-height:200px;' label-color='#07004d' bg-color='white' clear-icon='fa-regular fa-circle-xmark'").classes(add="col-span-3 lg:col-span-2 w-full bg-white shadow-md shadow-[#07004d] px-3 text-lg").bind_value(procedure_data,"procedure_notes")
                  
                  with html.div().classes(add="w-full flex flex-row justify-center"):
                    ider = ui.label(procedure['procedure_id']).classes(add="hidden") 
                    ui.button(text="submit results",color="",on_click=lambda e:self.save_procedure({
                      "procedure_id":e.sender.parent_slot.parent.slots["default"].children[0]._text,
                      "visit_id":visit["visit_id"],
                      "procedure_notes":notes.value,
                      "performer":get_staff_username(name=performer.value),"assistant":get_staff_username(name=assistant.value)
                      })).props(add="" if (procedure["payment"]["paid"] or procedure["payment"]["billed"]) else "disabled").classes(add="rounded bg-harmony text-lg text-bold text-yellow-500")
  
class StaffManager():
  """This class constructs UI for Staff management interface"""

  def __init__(self,user):
    #DATA
    self.user = user
    self.staffs = [staff for staff in get_staffs() if not staff["is_super"]]

    #UI
    with html.main().classes(add="grow w-full flex flex-col"):
      #Separator
      for i in range(1):
        ui.separator().classes(add="w-full bg-[#09026f]")
      
      #Header
      with html.div().classes(add="w-full flex flex-row items-center bg-harmony"):
        ui.label("STAFF MANAGEMENT PANEL").classes(add="grow bg-inherit text-yellow-500 text-center text-xl uppercase text-bold")
        ui.button(icon="fas fa-circle-plus",color="",on_click=self.StaffDialog).classes(add="lg:hidden size-16 bg-inherit text-yellow-500")
        ui.button(icon="fas fa-circle-plus",color="",on_click=lambda e:self.StaffPanel(lg=True)).classes(add="lg-show size-16 bg-inherit text-yellow-500")
      
      #Body
      with html.section().classes(add="grow w-full p-0.5 grid grid-cols-1 lg:grid-cols-2 gap-x-0.5"):
        #Table of staff
        with html.section().classes(add="w-full h-full flex flex-col") as self.staffs_panel:
          self.StaffsDisplay(staffs=self.staffs)
        
        #Staff Details Interface(for Large screens only)
        with html.section().classes(add="lg-flex w-full h-full flex-col") as self.staff_panel_lg:
          pass
  
  #FUNCTIONALITIES
  def save_staff(self,staff_data:dict,lg:bool=False):
    """"""
    #CONTROLS
    if not (staff_data["first_name"] and staff_data["last_name"] and staff_data["title"] and staff_data["gender"] and staff_data["birthdate"] and staff_data["qualification"] and staff_data["designation"] and staff_data["primary_role"]):
      ui.notify(message="Please fill all required fields",type="negative",position="center")
      return
    #Format data
    data = {
      "first_name":staff_data["first_name"].lower() if staff_data["first_name"] else None,
      "middle_name":staff_data["middle_name"].lower() if staff_data["middle_name"] else None,
      "last_name":staff_data["last_name"].lower() if staff_data["last_name"] else None,
      "username":f"{staff_data['last_name'].lower()}{staff_data['first_name'].lower()[0]}{staff_data['middle_name'].lower()[0] if staff_data['middle_name'] else ''}",
      "title":staff_data["title"].lower() if staff_data["title"] else None,
      "gender":staff_data["gender"].lower() if staff_data["gender"] else None,
      "birthdate":staff_data['birthdate'],
      "qualification":staff_data["qualification"].lower() if staff_data["qualification"] else None,
      "designation":staff_data["designation"].lower() if staff_data["designation"] else None,
      "roles":[staff_data["primary_role"].lower()],
      "primary_role":staff_data["primary_role"],
      "secondary_role":staff_data["secondary_role"],
      "active":True,
      "suspended":False,
      "logins":staff_data["logins"]
    }
    
    if staff_data["secondary_role"]:
      data["roles"].append(staff_data["secondary_role"].lower())
    
    #Save to database
    status = register_staff(data)

    #Notification
    ui.notify(message=status["message"],type=status["type"],position=status["position"])
    
    #UI
    if status["success"]:
      #UI update
      self.staffs = [staff for staff in get_staffs() if not staff["is_super"]]
      if lg:
        self.StaffsDisplay(self.staffs)
        self.StaffPanel(staff=data,lg=True)
      else:
        self.StaffPanel(staff=data)
    
  def update_staff(self,staff_data,suspend:bool=False,activate:bool=False,edit:bool=False,lg:bool=False):
    """"""
    if activate:
      staff_data["username"] = staff_data["username"].lower()
      staff_data["active"],staff_data["suspended"] = True,False
      status = update_staff(staff=staff_data,activate=True)

      #UI update
      self.staffs = [staff for staff in get_staffs() if not staff["is_super"]]
      if lg:
        self.StaffsDisplay(self.staffs)
        self.StaffPanel(staff=staff_data,lg=lg)
      else:
        self.StaffPanel(staff=staff_data)

    if edit:
      data = {
        "first_name":staff_data["first_name"].lower(),
        "middle_name":staff_data["middle_name"].lower(),
        "last_name":staff_data["last_name"].lower(),
        "username":staff_data["username"].lower(),
        "title":staff_data["title"].lower(),
        "gender":staff_data["gender"].lower(),
        "birthdate":staff_data["birthdate"],
        "email":staff_data["email"],
        "mobile":staff_data["mobile"],
        "qualification":staff_data["qualification"].lower(),
        "designation":staff_data["designation"].lower(),
        "roles":[staff_data["primary_role"].lower()],
        "primary":staff_data["primary_role"],
        "secondary_role":staff_data["secondary_role"],
        "active":True,
        "suspended":False
      }

      if staff_data["secondary_role"]:
        data["roles"].append(staff_data["secondary_role"].lower())

      status = update_staff(staff=data,edit=True)

      #UI update
      self.staffs = [staff for staff in get_staffs() if not staff["is_super"]]
      if lg:
        self.StaffsDisplay(self.staffs)
        self.StaffPanel(staff=data,lg=lg)
      else:
        self.StaffPanel(staff=staff_data)
    
    if suspend:
      staff_data["username"] = staff_data["username"].lower()
      staff_data["active"],staff_data["suspended"] = False,True
      status = update_staff(staff=staff_data,suspend=True)

      #UI update
      self.staffs = [staff for staff in get_staffs() if not staff["is_super"]]
      if lg:
        self.StaffsDisplay(self.staffs)
        self.StaffPanel(staff=staff_data,lg=lg)
      else:
        self.StaffPanel(staff=staff_data)
    
    #Notify
    ui.notify(message=status["message"],type=status["type"],position=status["position"])

  #DISPLAYS
  def StaffsDisplay(self,staffs:list) -> None:
    """"""

    self.staffs_panel.clear()
    with self.staffs_panel:
      #Small Screen
      ui.aggrid(
        options={
          "columnDefs":[
            {"headerName":"","field":"status","width":60},
            {"headerName":"NAME","field":"name","sortable":True,"filter":True,"floatingFilter":True},
            {"headerName":"1°  ROLE","field":"primary_role","sortable":True,"filter":True,"width":150},
            {"headerName":"2° ROLE","field":"extra_roles","sortable":True,"filter":True,"width":150}
          ],
          "rowData":[
            {
              "status":StatusDot(active=staff["active"]),
              "name":f"{staff['first_name']} {staff['middle_name'][0].upper() if staff['middle_name'] else ''}. {staff['last_name']}".title(),
              "primary_role":staff['roles'][0].capitalize() if staff["roles"] else "---",
              "extra_roles":" : ".join(staff["roles"][1:]).title() if len(staff["roles"]) > 1 else "---",
              "username":staff["username"]
            } for staff in staffs
          ]
        },
        theme="quartz",
        html_columns=[0]
      ).classes(add="lg:hidden w-full h-full bg-inherit rounded-none text-sm animate__animated animate__fadeIn animate__slow").on("cellClicked",lambda e:self.StaffDialog(staff=[staff for staff in self.staffs if staff['username'] == e.args['data']['username']][0]))


      #Large Screen
      ui.aggrid(
        options={
          "columnDefs":[
            {"headerName":"","field":"status","width":65},
            {"headerName":"NAME","field":"name","sortable":True,"filter":True,"floatingFilter":True},
            {"headerName":"DESIGNATION","field":"designation","width":150},
            {"headerName":"PRIMARY ROLE","field":"primary_role","sortable":True,"filter":True,"width":200},
            {"headerName":"EXTRA ROLE","field":"extra_roles","sortable":True,"filter":True,"width":150}
          ],
          "rowData":[
            {
              "status":StatusDot(active=staff["active"]),
              "name":f"{staff['first_name']} {staff['middle_name'][0].upper() if staff['middle_name'] else ''}. {staff['last_name']}".title(),
              "designation":staff["designation"].title() if staff["designation"] else "---",
              "primary_role":staff['roles'][0].capitalize() if staff["roles"] else "---",
              "extra_roles":" : ".join(staff["roles"][1:]).title() if len(staff["roles"]) > 1 else "---",
              "username":staff["username"]
            } for staff in staffs
          ]
        },
        theme="quartz",
        html_columns=[0]
      ).classes(add="lg-show w-full h-full bg-inherit rounded-b-md text-sm animate__animated animate__fadeIn").on("cellClicked",lambda e:self.StaffPanel(staff=[staff for staff in self.staffs if staff['username'].lower() == e.args['data']['username'].lower()][0],lg=True))

  def StaffDialog(self,staff:dict|None=None):
    """A method to display dialog for staff registration"""
    #FXS
    def close_dialog():
      self.StaffsDisplay(staffs=self.staffs)
      self.staff_dialog.close()
    
    # UI
    with ui.dialog().props(add=f"transition-show='jump-up' transition-hide='jump-down' transition-duration='500'") as self.staff_dialog,html.div().style(add="min-width:75%;min-height:75%;").classes(add="p-0.5 bg-sky-100 flex flex-col"):
      #Header
      with html.section().classes(add="bg-harmony rounded-t flex flex-row justify-between"):
        ui.label(f"{staff['first_name']} {staff['middle_name'] if staff['middle_name'] else ''} {staff['last_name']}".upper() if staff else "NEW STAFF REGISTRATION").classes(add="bg-inherit p-2 grow text-yellow-500 text-2xl text-bold text-center")
        ui.button(icon="fa-regular fa-circle-xmark fa-lg",color="",on_click=close_dialog).classes(add="bg-inherit text-red-500 text-bold text-lg")
      
      #Body
      with html.section().classes(add="grow w-full flex flex-col") as self.staff_panel:
        self.StaffPanel(staff=staff)
  
    self.staff_dialog.open()
  
  def StaffPanel(self,staff:dict|None=None,lg:bool=False):
    """"""
    sections = ["profile","logs"]
    
    if lg:
      self.staff_panel_lg.clear()
      with self.staff_panel_lg:
        if staff:
          #Separator
          for i in range(2):
            ui.separator().classes(add="w-full bg-[#09026f]")

          #Tabs
          with html.div().classes(add="w-full p-0 rounded-b shadow-sm shadow-[#07004d]"):
            with ui.tabs(value=sections[0]).props(add="inline-label mobile-arrows outside-arrows active-class='text-sky-500'").classes(add="w-full rounded-b bg-harmony py-1 text-yellow-500 font-bold") as profile_tabs:
              for section in sections:
                ui.tab(name=section).props(add="dense")
          
          #Panels
          with html.div().classes(add="grow w-full rounded-br flex flex-col"):
            with ui.tab_panels(tabs=profile_tabs,value=sections[0]).props(add="animated infinite transition-prev='jump-right' transition-next='jump-left' transition-duration='700'").classes(add="bg-inherit grow w-full grid grid-cols-1"):
              #Profile
              with ui.tab_panel(name="profile").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col gap-0.5"):
                self.StaffDetailsForm(staff=staff)
              
              #Logs
              with ui.tab_panel(name="logs").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col gap-0.5"):
                self.StaffLogs(staff=staff)

        else:
          self.StaffDetailsForm()
    
    else:
      self.staff_panel.clear()
      with self.staff_panel:
        if staff:
          #Separator
          for i in range(2):
            ui.separator().classes(add="w-full bg-[#09026f]")

          #Tabs
          with html.div().classes(add="w-full p-0 rounded-b shadow-sm shadow-[#07004d]"):
            with ui.tabs(value=sections[0]).props(add="inline-label mobile-arrows outside-arrows active-class='text-sky-500'").classes(add="w-full rounded-b bg-harmony py-1 text-yellow-500 font-bold") as profile_tabs:
              for section in sections:
                ui.tab(name=section).props(add="dense")
          
          #Panels
          with html.div().classes(add="grow w-full rounded-br flex flex-col"):
            with ui.tab_panels(tabs=profile_tabs,value=sections[0]).props(add="animated infinite transition-prev='jump-right' transition-next='jump-left' transition-duration='700'").classes(add="bg-inherit grow w-full grid grid-cols-1"):
              #Profile
              with ui.tab_panel(name="profile").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col gap-0.5"):
                self.StaffDetailsForm(staff=staff)
              
              #Logs
              with ui.tab_panel(name="logs").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col gap-0.5"):
                self.StaffLogs(staff=staff)

        
        else:
          self.StaffDetailsForm()

  def StaffDetailsForm(self,staff:dict|None=None):
    """A structure of form for staff details"""
    #DATA
    edit = bool(staff)
    if staff:
      for key,value in staff.items():
        if type(value) is str:
          staff[key] = value.title()
      staff["title"] = [title for title in TITLES if title.lower() == staff["title"].lower()][0]
      staff["qualification"] = [qualification for qualification in CERTIFICATIONS if qualification.lower() == staff["qualification"].lower()][0]
      staff["designation"] = [designation for designation in DESIGNATIONS if designation.lower() == staff["designation"].lower()][0]
      staff["primary_role"] = [role for role in PRIMARY_ROLES if role.lower() == staff["roles"][0].lower()][0]
      if len(staff["roles"]) > 1:
        staff["secondary_role"] = [role for role in SECONDARY_ROLES if role and role.lower() == staff["roles"][1].lower()][0]
      else:
        staff["secondary_role"] = None

    staff = staff if staff else {"title":"","first_name":"","middle_name":"","last_name": "","birthdate":datetime.fromisoformat("1995-10-06") ,"gender": "","qualification":CERTIFICATIONS[-1],"designation": "","primary_role": "","secondary_role": "","suspended":False,"active":True,"logins":[]}
    
    #UI
    with html.form().classes(add="grow w-full p-2 flex lg:grid grid-cols-2 flex-col justify-between lg:justify-start gap-2 animate__animated animate__fadeIn animate__slow"):
      #Name
      with html.div().classes(add="grid grid-cols-8 gap-2"):
        ui.select(label="TITLE",options=TITLES).props(add=f"{'readonly' if staff['suspended'] else ''} required stack-label type='text'").classes(add="col-span-2 px-2 shadow-md shadow-[#07004d] bg-white rounded text-lg capitalize").bind_value(staff,"title")
        ui.input(label="FIRST NAME").props(add=f"{'readonly' if staff['suspended'] else ''} required stack-label type='text'").classes(add="col-span-3 shadow-md shadow-[#07004d] px-2 bg-white rounded-sm text-lg").bind_value(staff,"first_name")
        ui.input(label="MIDDLE NAME").props(add=f"{'readonly' if staff['suspended'] else ''} stack-label type='text'").classes(add="col-span-3 shadow-md shadow-[#07004d] px-2 bg-white rounded-sm text-lg").bind_value(staff,"middle_name")
        ui.input(label="LAST NAME").props(add=f"{'readonly' if staff['suspended'] else ''} required stack-label type='text'").classes(add="col-span-4 shadow-md shadow-[#07004d] px-2 bg-white rounded-sm text-lg").bind_value(staff,"last_name")
        ui.select(label="GENDER",options=["Male","Female"]).props(add=f"{'readonly' if staff['suspended'] else ''} required type='text'").classes(add="col-span-4 shadow-md shadow-[#07004d] px-2 bg-white rounded-sm text-lg").bind_value(staff,"gender")

      #Details
      with html.section().classes(add="grid grid-cols-2 lg:grid-cols-1  gap-2"):
        #Birthdate
        with ui.input(label="BIRTHDATE").props(add="bordered readonly").classes(add="w-full px-2 shadow-md shadow-[#07004d] bg-white rounded text-lg").bind_value_from(staff,"birthdate",backward=lambda e:e.strftime("%d %b %Y")) as bdate_display:
          with ui.dialog() as calendar:
            ui.date(mask="YYYY-MM-DD",on_change=lambda e:calendar.close()).props(add=f"{'readonly' if staff['suspended'] else ''} bordered square today-btn color='harmony' event-color='orange' first-day-of-week='1' navigation-max-year-month='{datetime.now().strftime("%Y/%m")}'").bind_value(target_object=staff,target_name="birthdate",forward=lambda e:datetime.fromisoformat(str(e)[:10]))
            with bdate_display.add_slot("append"):
              ui.icon("fas fa-cake-candles",color="pink-500").on("click",calendar.open)
        #Age
        ui.input(label="AGE").props(add="readonly stack-label").bind_value_from(target_object=staff,target_name="birthdate",backward=lambda e:format_age(e)).classes(add="w-full shadow-md shadow-[#07004d] bg-sky-50 rounded px-2 text-lg text-bold text-sky-600")
      
      ui.separator().classes(add="lg:hidden my-1 w-full")

      #Academic Details
      with html.div().classes(add="col-span-2 grid grid-cols-2 gap-2 p-1"):
        ui.select(label="QUALIFICATION",options=CERTIFICATIONS).props(add=f"{'readonly' if staff['suspended'] else ''} stack-label type='text'").classes(add="shadow-md shadow-[#07004d] px-2 bg-white rounded text-lg").bind_value(staff,"qualification")
        #Designation
        ui.select(label="DESIGNATION",options=DESIGNATIONS).props(add=f"{'readonly' if staff['suspended'] else ''} required stack-label type='text'").classes(add="shadow-md shadow-[#07004d] px-2 bg-white rounded text-lg").bind_value(staff,"designation")
        #Uploads
        with ui.label().classes(add="hidden col-span-2 rounded flex flex-row justify-center"):
          with ui.dialog().style(add="min-width:50%;") as upload_dialog:
            ui.upload(label="CERTIFICATE UPLOAD",multiple=True,max_file_size=500000,auto_upload=True).props(add="accept='.pdf'").style(add="").classes(add="m-1 w-full bg-sky-50 text-yellow-800")
          ui.button('upload certificates',color="gray-800",on_click=upload_dialog.open).classes(add="justify-self-center text-yellow-500 text-xl text-bold")
        
      ui.separator().classes(add="lg:hidden my-1 w-full")
      
      #Roles
      with html.div().classes(add="col-span-2 w-full grid grid-cols-1 lg:grid-cols-2 gap-2"):
        #Primary roles
        with html.div().classes(add="w-full p-0.5 rounded bg-sky-50 shadow-md shadow-[#07004d]"):
          ui.label('primary roles').classes(add="rounded small-caps text-bold text-xl text-harmony")
          ui.radio(options=PRIMARY_ROLES).props(add=f"{'disable' if staff['suspended'] else ''} inline required").bind_value(staff,"primary_role")
        #Secondary roles
        with html.div().classes(add="w-full p-0.5 rounded bg-sky-50 shadow-md shadow-[#07004d]"):
          ui.label('secondary roles').classes(add="rounded small-caps text-bold text-xl text-harmony")
          ui.radio(options=SECONDARY_ROLES).props(add=f"{'disable' if staff['suspended'] else ''} inline").classes(add="lg:self-start").bind_value(staff,"secondary_role")
        
          #Lg buttons
          with html.div().classes(add=f"lg-flex col-start-2 col-span-1 self-end w-full flex-row justify-center gap-5"):
            if staff["suspended"]:
              ui.button(text="ACTIVATE",color="",on_click=lambda e:self.update_staff(staff_data=staff,activate=True,lg=True)).classes(add="bg-harmony text-yellow-500 text-bold text-xl")
            else:
              if edit:
                ui.button(text="SAVE",color="",on_click=lambda e:self.update_staff(staff_data=staff,edit=True,lg=True)).classes(add="bg-harmony text-yellow-500 text-bold text-xl")
                ui.button(text="SUSPEND",color="",on_click=lambda e:self.update_staff(staff_data=staff,suspend=True)).classes(add="bg-harmony text-yellow-500 text-bold text-xl")
                
              else:
                ui.button(text="SAVE",color="",on_click=lambda e:self.save_staff(staff_data=staff,lg=True)).classes(add="bg-harmony text-yellow-500 text-bold text-xl")


      #Buttons
      with html.div().classes(add=f"lg:hidden w-full flex flex-row justify-center gap-5"):
        if staff["suspended"]:
          ui.button(text="ACTIVATE",color="",on_click=lambda e:self.update_staff(staff_data=staff,activate=True)).classes(add="bg-harmony text-yellow-500 text-bold text-xl")
        else:
          if edit:
            ui.button(text="SAVE",color="",on_click=lambda e:self.update_staff(staff_data=staff,edit=True)).classes(add="bg-harmony text-yellow-500 text-bold text-xl")
            ui.button(text="SUSPEND",color="",on_click=lambda e:self.update_staff(staff_data=staff,suspend=True)).classes(add="bg-harmony text-yellow-500 text-bold text-xl")
            
          else:
            ui.button(text="SAVE",color="",on_click=lambda e:self.save_staff(staff)).classes(add="bg-harmony text-yellow-500 text-bold text-xl")

  def StaffLogs(self,staff:dict):
    """Displays details of logins of staff"""
    #DATA
    logs = sorted(staff["logins"],key=lambda log:log["login_time"],reverse=True)

    #UI
    with html.div().classes(add="grow w-full flex flex-col") as logs_container:
      if logs:
        with ui.scroll_area().classes(add="grow w-full") as logs_container:
          for log in logs:
            with ui.button(color="").props(add="glossy").classes(add=f"w-full m-0 p-0 bg-sky-50 rounded shadow-sm shadow-[#07004d] {'ring-2 ring-green-600 ring-offset-1' if log['logged'] else ''}"):
              #Login
              with html.span().classes(add="w-full p-1 grid grid-cols-2"):
                ui.label("LOGIN").classes(add="w-full font-semibold text-sky-600 text-lg text-start")
                ui.label(log["login_time"].strftime("%d %b %Y %H:%M") if log["login_time"] else "---").classes(add="w-full font-medium text-harmony text-lg")
              
              #Separator
              ui.separator().classes(add="w-full")

              #Logout
              with html.span().classes(add="p-1 w-full grid grid-cols-2"):
                ui.label("LOGOUT").classes(add="w-full font-semibold text-sky-600 text-lg text-start")
                ui.label(log["logout_time"].strftime("%d %b %Y %H:%M") if log["logout_time"] else "---").classes(add="w-full font-medium text-harmony text-lg")

      else:
        with logs_container.classes(add="justify-center items-center"):
          ui.label("This staff has no logs!").classes(add="italic font-semibold text-red-600 text-xl fa-fade")

class ServicesManager():

  def __init__(self,user):
    #DATA
    self.user = user
    self.initial_data()

    #UI
    with html.main().classes(add="grow w-full flex flex-col"):
      #Separator
      for i in range(1):
        ui.separator().classes(add="w-full bg-[#09026f]")
      
      #Header
      with html.div().classes(add="w-full flex flex-row items-center bg-harmony"):
        ui.label("SERVICES MANAGEMENT PANEL").classes(add="grow bg-inherit text-yellow-500 text-center text-xl lg:text-2xl uppercase text-bold")
        ui.button(icon="fas fa-circle-plus",color="",on_click=self.ServiceDialog).classes(add="size-16 bg-inherit text-yellow-500")
      
      #Body
      with html.section().classes(add="grow w-full p-0.5 flex flex-col") as self.services_panel:
        self.ServicesDisplay(self.services)
        
  #FUNCTIONALITIES
  def initial_data(self):
    self.services = get_services()
    self.template_services = get_template_services()

  def retrieve_service(self,service:str):
    """A method that retrieves service details and populate details in ServiceDetailsForm"""
    if not service:
      return
    
    service = get_template_service(service.lower())
    service["payment"] = self.pricings(service)
    
    self.ServiceDetailsForm(service)

  def save_service(self,service:dict,update:bool=False):
    """"""

    for key,value in service.items():
      if type(value) == str:
        service[key] == value.lower()
    
    payment = service["payment"]
    payment.pop("insured")
    payment.pop("logger")
    payment.pop("service_id")
    
    for scheme in service["schemes"]:
      for price in scheme["prices"]:
        for pay_scheme,pay_details in payment.items():
          if scheme["scheme_name"].lower() == pay_scheme.lower():
            scheme["scheme_id"] = pay_details["scheme_id"]
            price["logger"] = self.user.username
            price["copayment"] = pay_details["copayment"]
            price["price_range"] = pay_details["price_range"]
            price["min"] = pay_details["min"]
            price["max"] = pay_details["max"]
            price["standard"] = pay_details["standard"]
            price["priority"] = pay_details["priority"]
            price["topup"] = pay_details["topup"]
    service.pop("payment")
    
    if update:
      status = update_service(service)
    else:
      status = register_service(service)

    ui.notify(message=status["message"],type=status["type"],position=status["position"])

    self.initial_data()
        
    self.ServicesDisplay(services=self.services)
    
  def pricings(self,service:dict):
    """Returns a namedtuple object with prices of a 'service'"""

    for scheme in service["schemes"]:
      for pricing in scheme["prices"]:
        pricing["scheme_item_code"] = scheme["scheme_item_code"]
        pricing["restricted"] = scheme["restricted"]
    
    output = {scheme["scheme_name"]:[pricing for pricing in scheme["prices"] if pricing["active"]][0] for scheme in service["schemes"] if scheme.get("active")}
    output["logger"] = self.user.username
    output["service_id"] = service["service_id"]
    if "nhif" in output:
      output["insured"] = True
    else:
      output["insured"] = False
      output["nhif"] = {
        "scheme_id":f"cash-{service['service_id'].lower()}",
        "scheme_item_code":"",
        "copayment":False,
        "price_range":False,
        "min":0,
        "max":0,
        "standard":0,
        "priority":0,
        "topup":0
      }

    return output

  #DISPLAYS
  def ServicesDisplay(self,services:list):
    """"""
    #FXS
    def Status(service,lg:bool=False):
      _status = service["active"]
      status = ""
      if lg:
        if _status:
          status = "<span class='text-green-600 text-bold' >Active</span>"
        else:
          status = "<span class='text-red-600 text-bold' >Inactive</span>"
      else:
        if _status:
          status = "<span class='fa-solid fa-circle-dot text-green-600 text-bold' ></span>"
        else:
          status = "<span class='fa-solid fa-circle-dot text-red-600 text-bold' ></span>"
      
      return status

    def MiniPayment(service):
      pricings = self.pricings(service)
      pricings.pop("logger")
      pricings.pop("service_id")
      pricings.pop("insured")
      return f"<div class='grid grid-cols-2 gap-2 text-bold uppercase'>{''.join([f'<div class="w-full text-center {'col-start-1 text-harmony' if scheme == 'cash' else 'col-start-2 text-yellow-700'}">{scheme}</div>' for scheme,pricing in pricings.items() if pricing['standard'] or pricing["price_range"]])}</div"
    
    def Payment(service,cash:bool=False,nhif:bool=False):
      def _format_price(price):
        return f"{price:,.2f}"

      pricings = self.pricings(service)
      if cash:
        price = pricings.get("cash")
        if price["price_range"]:
          return f"<div class='text-harmony font-semibold'>{price['min']:,.2f} - {price['max']:,.2f}</div>"
        else:
          return f"<div class='text-harmony font-semibold'>{price['standard']:,.2f}</div>"
      
      if nhif:
        if "nhif" in pricings:
          price = pricings.get("nhif")
          return f"<div class='grid grid-cols-2 gap-5 font-semibold'><div class='grid grid-cols-2 gap-1' ><span class='text-yellow-800' >STANDARD</span><span class='justify-self-end' >{_format_price(price['standard']) if price['standard'] else '---'}</span></div><div class='grid grid-cols-2 gap-1' ><span class='text-yellow-800' >PRIORITY</span><span class='justify-self-end' >{_format_price(price['priority']) if price['priority'] else '---'}</span></div></div>"
        else:
          return f"<div class='grid grid-cols-2 gap-3 font-semibold'><div class='grid grid-cols-2 gap-1' ><span class='text-yellow-800' >STANDARD</span><span class='justify-self-end' >---</span></div><div class='grid grid-cols-2 gap-1' ><span class='text-yellow-800' >PRIORITY</span><span class='justify-self-end' >---</span></div></div>"

    #UI
    self.services_panel.clear()
    with self.services_panel:
      ui.aggrid(
        options={
          "columnDefs":[
            {"headerName":"","field":"sno","width":50},
            {"headerName":"NAME","field":"name","sortable":True,"filter":True,"floatingFilter":True},
            {"headerName":"TYPE","field":"type","width":100},
            {"headerName":"STATUS","field":"status","width":75},
            {"headerName":"CASH PRICES (TZS)","field":"price_cash","sortable":True,"width":150},
            {"headerName":"NHIF PRICES (TZS)","field":"price_nhif","sortable":True,"width":300},
          ],
          "rowData":[
            {
              "sno":services.index(service) + 1,
              "name":service["name"].title(),
              "type":service["type"].capitalize(),
              "status":Status(service,lg=True),
              "price_cash":Payment(service,cash=True),
              "price_nhif":Payment(service,nhif=True),
              "service_id":service["service_id"]
            } for service in services
          ]
        },
        theme="quartz",
        html_columns=[3,4,5]
      ).classes(add="lg-show w-full h-full bg-inherit rounded-b-md text-sm animate__animated animate__fadeIn").on("cellClicked",lambda e:self.ServiceDialog(service=[service for service in self.services if service['service_id'] == e.args['data']['service_id'].lower()][0]))
  
      #Small Screen
      ui.aggrid(
        options={
          "columnDefs":[
            {"headerName":"","field":"status","width":50},
            {"headerName":"NAME","field":"name","sortable":True,"filter":True,"floatingFilter":True,"width":300},
            {"headerName":"TYPE","field":"type","width":200},
            {"headerName":"PAYMENT","field":"payment","sortable":True,"width":150},
          ],
          "rowData":[
            {
              "status":Status(service),
              "name":service["name"].title(),
              "type":service["type"].capitalize(),
              "payment":MiniPayment(service),
              "service_id":service["service_id"]
            } for service in services
          ]
        },
        theme="quartz",
        html_columns=[0,3]
      ).classes(add="lg:hidden w-full h-full bg-inherit rounded-b-md text-sm animate__animated animate__fadeIn").on("cellClicked",lambda e:self.ServiceDialog(service=[service for service in self.services if service['service_id'] == e.args['data']['service_id'].lower()][0]))
  
  def ServiceDialog(self,service:dict|None=None):
    """A method to display dialog for service registration and editing"""
    #FXS
    def close_dialog():
      self.ServicesDisplay(services=self.services)
      self.service_dialog.close()

    # UI
    with ui.dialog().props(add=f"transition-show='jump-up' transition-hide='jump-down' transition-duration='300'") as self.service_dialog,html.div().style(add="min-width:60%;min-height:60%;").classes(add="p-0.5 bg-sky-50 flex flex-col"):
      #Header
      with html.section().classes(add="bg-harmony flex flex-row justify-between"):
        ui.label(service["name"].upper() if service else "SERVICE PANEL").classes(add="bg-inherit p-2 grow text-yellow-600 text-xl lg:text-3xl text-bold text-center")
        ui.button(icon="fa-regular fa-circle-xmark",color="",on_click=close_dialog).classes(add="bg-inherit text-rose-500 text-bold text-base")
      
      #Search Bar
      with html.section().classes(add="w-full p-3 flex flex-row justify-center"):
        ui.select(label="SERVICE NAME",options=self.template_services,with_input=True,on_change=lambda e:self.retrieve_service(service=e.value)).props(add=f"popup-content-class='capitalize'").classes(add="col-span-3 px-1 bg-white shadow-md shadow-[#07004d] rounded text-lg")

      #Service details
      with html.section().classes(add="grow w-full flex flex-col") as self.service_panel:
        self.ServiceDetailsForm(service=service,edit=True if service else False)
        
    self.service_dialog.open()
  
  def ServiceDetailsForm(self,service:dict,edit:bool=False):
    #DATA
    if service:
      if edit:
        data = service
        data["payment"] = self.pricings(service)
      else:
        data = service
    
    else:
      data = {
        "service_id":"",
        "name":self.template_services[0],
        "alternative_name":"",
        "type":"",
        "payment":{
          "logger":self.user.username,
          "service_id":"",
          "insured":False,
          "cash":{
            "scheme_id":f"",
            "logger":self.user.username,
            "copayment":False,
            "price_range":False,
            "min":0,
            "max":0,
            "standard":0,
            "priority":0,
            "topup":0
          },
          "nhif":{
            "scheme_id":"",
            "logger":self.user.username,
            "copayment":False,
            "price_range":False,
            "min":0,
            "max":0,
            "standard":0,
            "priority":0,
            "topup":0
          }
        }
      }

    #FXS
    def update_service_prices(nhif:bool=False):
      data["payment"] = retrieve_updated_prices(data=data["payment"],nhif=nhif)
      display_nhif_prices()
      
    def display_nhif_prices():
      nhif_prices_display.clear()
      with nhif_prices_display:
        ui.button(text="update",color="",on_click=lambda e:update_service_prices(nhif=True)).props(add="glossy").classes(add="bg-harmony text-xl text-yellow-500 font-medium").bind_visibility_from(data["payment"],"insured")
        nhif_standard_display = ui.number(label="STANDARD").props(add="readonly stack-label label-color='#07004d'").classes(add="w-full px-1 bg-white shadow-sm shadow-[#07004d] rounded-sm text-lg").bind_value(data["payment"]["nhif"],"standard").bind_visibility_from(data["payment"],"insured")
        nhif_priority_display = ui.number(label="PRIORITY").props(add="readonly required stack-label label-color='#07004d'").classes(add="w-full px-1 bg-white shadow-sm shadow-[#07004d] rounded-sm text-lg").bind_value(data["payment"]["nhif"],"priority").bind_visibility_from(data["payment"],"insured")
        #Message if its not insured
        ui.label("Not Insured by NHIF").classes(add="col-span-3 text-lg text-gray-500 font-semibold italic text-center fa-fade").bind_visibility_from(data["payment"],"insured",backward=lambda insured:not insured)
      
    #UI
    self.service_panel.clear()
    with self.service_panel:
      with html.form().classes(add="w-full py-1 px-0 grid grid-cols-1 lg:grid-cols-5 gap-2"):
        #General Details
        with html.section().classes(add="lg:col-span-2 w-full flex flex-col gap-2"):
          ui.label('GENERAL DETAILS').classes(add="grow w-full px-1 shadow-md shadow-[#07004d] text-bold text-xl text-harmony")
          with html.div().classes(add="w-full p-1 grid grid-cols-3 gap-2"):
            ui.input(label="NAME").props(add="readonly stack-label type='text'").classes(add="col-span-3 px-1 bg-white shadow-sm shadow-[#07004d] rounded text-lg").bind_value(data,"name",backward=lambda service_name:service_name.title() if service_name else service_name)
            ui.input(label="OTHER NAME (Optional)").props(add="readonly stack-label type='text'").classes(add="col-span-2 lg:col-span-3 bg-white shadow-sm shadow-[#07004d] rounded px-1 text-lg").bind_value_from(data,"alternative_name",backward=lambda service_alt_name:service_alt_name.title() if service_alt_name else service_alt_name)
            ui.input(label="SERVICE TYPE").props(add="readonly required stack-label").classes(add="col-span-1 lg:col-span-3 bg-white shadow-sm shadow-[#07004d] rounded px-1 text-lg").bind_value(data,"type",backward=lambda service_type:service_type.title() if service_type else service_type)
        
        #Prices
        with html.section().classes(add="lg:col-span-3 grow w-full flex flex-col gap-2"):
          ui.label('PRICING DETAILS').classes(add="w-full px-1 shadow-md shadow-[#07004d] text-bold text-xl text-harmony")
          #CASH Pricing
          with html.div().classes(add="grow w-full p-1 flex flex-col gap-2"):
            ui.label("CASH PRICES").classes(add="col-span-3 w-full px-1 shadow-sm shadow-[#07004d] text-bold text-xl text-harmony")
            with html.div().classes(add="grid grid-cols-3 gap-2") as cash_prices_display:
              ui.switch("PRICE RANGE").props(add="left-label size='lg' unchecked-icon='fa-regular fa-circle-xmark' checked-icon='fa-solid fa-check-double' color='green-8'").classes(add="px-1 bg-sky-50 shadow-sm shadow-[#07004d] text-harmony font-medium").bind_value(data["payment"]["cash"],"price_range")
            
              ui.number(label="STANDARD").props(add="stack-label label-color='#07004d'").classes(add="w-full px-1 bg-white shadow-sm shadow-[#07004d] rounded-sm text-lg").bind_value(data["payment"]["cash"],"standard").bind_visibility_from(data["payment"]["cash"],"price_range",backward=lambda price_range:not price_range)
              ui.number(label="PRIORITY").props(add="required").classes(add="w-full px-1 bg-white shadow-sm shadow-[#07004d] rounded-sm text-lg").bind_value(data["payment"]["cash"],"priority").bind_visibility_from(data["payment"]["cash"],"price_range",backward=lambda price_range:not price_range)

              ui.number(label="CASH MIN").props(add="stack-label label-color='#07004d'").style(add="caret-color:#daa520;").classes(add="w-full px-1 bg-white shadow-sm shadow-[#07004d] rounded text-lg").bind_value(data["payment"]["cash"],"min").bind_visibility_from(data["payment"]["cash"],"price_range")
              ui.number(label="CASH MAX").props(add="stack-label label-color='#07004d'").style(add="caret-color:#daa520;").classes(add="w-full px-1 bg-white shadow-sm shadow-[#07004d] rounded text-lg").bind_value(data["payment"]["cash"],"max").bind_visibility_from(data["payment"]["cash"],"price_range")
          
          #NHIF Pricing
          with html.div().classes(add="grow w-full p-1 flex flex-col gap-2"):
            ui.label("NHIF PRICES").classes(add="col-span-3 w-full px-1 shadow-sm shadow-[#07004d] text-bold text-xl text-harmony")
            with html.div().classes(add="grid grid-cols-3 gap-2") as nhif_prices_display:
              display_nhif_prices()
        
        #Buttons
        with html.div().classes(add="lg:col-span-5 w-full py-2 flex flex-row justify-center"):
          ui.button(text="SAVE SERVICE",color="",on_click=lambda e:self.save_service(service=data,update=True if edit else False)).props(add="glossy").classes(add="bg-harmony text-yellow-500 text-bold text-xl")
          


