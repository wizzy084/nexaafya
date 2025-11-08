"""A module for constructing widgets for the cashier's page"""

#GENERAL IMPORTS
from datetime import datetime,timedelta
import calendar

#NiceGUI IMPORTS
from nicegui import ui,html

#APP IMPORTS
from services.provider.clients.processor import get_visits,get_payments

#UIX IMPORTS
from ..tools._snippets import format_age
from ..tools.components import ClientCard
#from ..microwidgets import ClientCard,PaymentCard



#WIDGETS
class PaymentsManagementDisplay():
  """A widget for displaying the payment management options"""

  def __init__(self):
    self.visits = [visit for visit in get_visits() if "cash" in [payment["payment_mode"] for payment in visit["payments"]]]
    self.payments = [payment for payment in get_payments()]

    #Management buttons
    with html.div().props(add="elevated").classes(add="w-full py-2 flex flex-row justify-center gap-2 bg-sky-700"):
      ui.button(text="view all",color="sky-600",on_click=self.display_all_payments).classes(add="text-sky-50 text-lg")
      with ui.button(text="unattended",color="sky-600",on_click=self.display_unattended_payments).classes(add="text-sky-50 text-lg"):
        ui.badge(text=str(len(self.get_unattended_visits())),color="gray-600").props(add="floating").classes(add="text-bold")
      with ui.button(text="billed",color="sky-600",on_click=self.display_billed_payments).classes(add="text-sky-50 text-lg"):
        ui.badge(text=str(len(self.get_billed_visits())),color="purple-600").props(add="floating").classes(add="text-bold")
      with ui.button(text="incomplete",color="sky-600",on_click=self.display_incomplete_payments).classes(add="text-sky-50 text-lg"):
        ui.badge(text=str(len(self.get_incomplete_visits())),color="yellow-500").props(add="floating").classes(add="text-bold")
      with ui.button(text="completed",color="sky-600",on_click=self.display_completed_payments).classes(add="text-sky-50 text-lg"):
        ui.badge(text=str(len(self.get_completed_visits())),color="green-600").props(add="floating").classes(add="text-bold")
    
    #Display panel
    with html.div().classes(add="w-full h-full") as self.cashier_panel:
      self.display_all_payments()
  
  def get_visit_payments(self,visit_id:str):
    """Returns a list of payments for a visit with the given visit_id"""

    return [payment for payment in self.payments if (payment["visit_id"] == visit_id) and (payment["payment_mode"] == "cash")]
  
  #Counts
  def get_unattended_visits(self):
    """Returns a string of the number of payments form self.payments if their "is_active" attribute is True but 'paid' and 'billed' attributes are False"""
    
    return [visit for visit in self.visits if len([payment for payment in visit["payments"] if not payment["billed"] and not payment["paid"] and not payment["cancelled"]]) > 0]
  
  def get_billed_visits(self):
    """Returns a string of the number of payments form self.payments if their "is_active" attribute is True but 'paid' and 'billed' attributes are False"""
    
    return [visit for visit in self.visits if len([payment for payment in visit["payments"] if payment["billed"] and not payment["paid"]]) > 0]
  
  def get_incomplete_visits(self):
    """Returns a string of the number of payments form self.payments if their "is_active" attribute is True but 'paid' and 'billed' attributes are False"""
    
    return [visit for visit in self.visits if len([payment for payment in visit["payments"] if payment["billed"] and payment["paid"]]) > 0]
  
  def get_completed_visits(self):
    """Returns a string of the number of payments form self.payments if their "is_active" attribute is True but 'paid' and 'billed' attributes are False"""
    
    return [visit for visit in self.visits if len([payment for payment in visit["payments"] if payment["paid"] and not payment["billed"]]) > 0]
  
  #Other functionalities

  #Displays
  def display_all_payments(self):
    """Displays the unattended payments"""

    self.cashier_panel.clear()
    with self.cashier_panel:
      ui.label(text="all  payable  services").classes(add="w-full bg-sky-700 text-center text-2xl uppercase text-bold text-white")
      ui.aggrid(
        {
        "columnDefs":[
          {"headerName":"Visit ID","field":"visit_id","filter":"agTextColumnFilter"},
          {"headerName":"Name","field":"name","filter":"agTextColumnFilter"},
          {"headerName":"Age","field":"age"},
          {"headerName":"Gender","field":"gender"},
          {"headerName":"Payment Mode","field":"payment_mode"},
          {"headerName":"Services","field":"all_services"},
          {"headerName":"Paid","field":"paid_services","cellClassRules":{"bg-green-500 text-bold":"x > 0"}},
          {"headerName":"Incomplete","field":"incomplete_services","cellClassRules":{"bg-emerald-500 text-bold":"x > 0"}},
          {"headerName":"Billed","field":"billed_services","cellClassRules":{"bg-violet-500 text-bold":"x > 0"}},
          {"headerName":"Cancelled","field":"cancelled_services","cellClassRules":{"bg-gray-400 text-bold":"x > 0"}}
        ] ,
        "rowData":[{
          "visit_id":visit["visit_id"],
          "name":visit["client_name"],
          "age":format_age(visit["client_birthdate"]),
          "gender":visit["client_gender"],
          "payment_mode":visit["payment_mode"].upper(),
          "all_services":len(self.get_visit_payments(visit["visit_id"])),
          "paid_services":len([payment for payment in self.get_visit_payments(visit["visit_id"]) if payment["paid"] and not payment["billed"]]),
          "incomplete_services":len([payment for payment in self.get_visit_payments(visit["visit_id"]) if payment["paid"] and payment["billed"]]),
          "billed_services":len([payment for payment in self.get_visit_payments(visit["visit_id"]) if payment["billed"] and not payment["paid"]]),
          "cancelled_services":len([payment for payment in self.get_visit_payments(visit["visit_id"]) if payment["cancelled"]])
        } for visit in self.visits],
      }
    ).classes(add="w-full h-full").on("cellClicked",lambda e:self.display_payments_dialog(e.args["data"]["visit_id"],"all"))
  
  def display_unattended_payments(self):
    """Displays the unattended payments"""

    self.cashier_panel.clear()
    with self.cashier_panel:
      ui.label(text="unattended payments").classes(add="w-full bg-sky-700 text-center text-2xl uppercase text-bold text-white")
      ui.aggrid(
        {
        "columnDefs":[
          {"headerName":"Visit ID","field":"visit_id","filter":"agTextColumnFilter"},
          {"headerName":"Name","field":"name","filter":"agTextColumnFilter"},
          {"headerName":"Age","field":"age"},
          {"headerName":"Gender","field":"gender"},
          {"headerName":"Payment Mode","field":"payment_mode"},
          {"headerName":"Services","field":"all_services"},
          {"headerName":"Paid","field":"paid_services"},
          {"headerName":"Incomplete","field":"incomplete_services"},
          {"headerName":"Billed","field":"billed_services"},
        ] ,
        "rowData":[{
          "visit_id":visit["visit_id"],
          "name":visit["client_name"],
          "age":format_age(visit["client_birthdate"]),
          "gender":visit["client_gender"],
          "payment_mode":visit["payment_mode"],
          "all_services":len(self.get_visit_payments(visit["visit_id"])),
          "paid_services":len([payment for payment in self.get_visit_payments(visit["visit_id"]) if payment["paid"] and not payment["billed"]]),
          "incomplete_services":len([payment for payment in self.get_visit_payments(visit["visit_id"]) if payment["paid"] and payment["billed"]]),
          "billed_services":len([payment for payment in self.get_visit_payments(visit["visit_id"]) if payment["billed"] and not payment["paid"]])
        } for visit in self.get_unattended_visits()],
      }).classes(add="w-full h-full").on("cellClicked",lambda e:self.display_payments_dialog(e.args["data"]["visit_id"],"unattended"))
  
  def display_billed_payments(self):
    """Displays the unattended payments"""

    self.cashier_panel.clear()
    with self.cashier_panel:
      ui.label(text="billed payments").classes(add="w-full bg-sky-700 text-center text-2xl uppercase text-bold text-white")
      ui.aggrid(
        {
        "columnDefs":[
          {"headerName":"Visit ID","field":"visit_id","filter":"agTextColumnFilter"},
          {"headerName":"Name","field":"name","filter":"agTextColumnFilter"},
          {"headerName":"Age","field":"age"},
          {"headerName":"Gender","field":"gender"},
          {"headerName":"Payment Mode","field":"payment_mode"},
          {"headerName":"Services","field":"all_services"},
          {"headerName":"Billed Payments","field":"billed_services"}
        ] ,
        "rowData":[{
          "visit_id":visit["visit_id"],
          "name":visit["client_name"],
          "age":format_age(visit["client_birthdate"]),
          "gender":visit["client_gender"],
          "payment_mode":visit["payment_mode"].lower(),
          "all_services":len(self.get_visit_payments(visit["visit_id"])),
          "billed_services":len([payment for payment in self.get_visit_payments(visit["visit_id"]) if payment["billed"] and not payment["paid"]])
        } for visit in self.get_billed_visits()]
      }
    ).classes(add="w-full h-full").on("cellClicked",lambda e:self.display_payments_dialog(e.args["data"]["visit_id"],"billed"))
  
  def display_incomplete_payments(self):
    """Displays the unattended payments"""

    self.cashier_panel.clear()
    with self.cashier_panel:
      ui.label(text="incomplete payments").classes(add="w-full bg-sky-700 text-center text-2xl uppercase text-bold text-white")
      ui.aggrid(
        {
        "columnDefs":[
          {"headerName":"Visit ID","field":"visit_id","filter":"agTextColumnFilter"},
          {"headerName":"Name","field":"name","filter":"agTextColumnFilter"},
          {"headerName":"Age","field":"age"},
          {"headerName":"Gender","field":"gender"},
          {"headerName":"Payment Mode","field":"payment_mode"},
          {"headerName":"Services","field":"all_services"},
          {"headerName":"Incomplete Payments","field":"incomplete_services"}
        ] ,
        "rowData":[{
          "visit_id":visit["visit_id"],
          "name":visit["client_name"],
          "age":format_age(visit["client_birthdate"]),
          "gender":visit["client_gender"],
          "payment_mode":visit["payment_mode"].upper(),
          "all_services":len(self.get_visit_payments(visit["visit_id"])),
          "incomplete_services":len([payment for payment in self.get_visit_payments(visit["visit_id"]) if payment["paid"] and payment["billed"]])
        } for visit in self.get_incomplete_visits()],
      }
    ).classes(add="w-full h-full").on("cellClicked",lambda e:self.display_payments_dialog(e.args["data"]["visit_id"],"incomplete"))
    
  def display_completed_payments(self):
    """Displays the unattended payments"""

    self.cashier_panel.clear()
    with self.cashier_panel:
      ui.label(text="completed payments").classes(add="w-full bg-sky-700 text-center text-2xl uppercase text-bold text-white")
      ui.aggrid(
        {
        "columnDefs":[
          {"headerName":"Visit ID","field":"visit_id","filter":"agTextColumnFilter"},
          {"headerName":"Name","field":"name","filter":"agTextColumnFilter"},
          {"headerName":"Age","field":"age"},
          {"headerName":"Gender","field":"gender"},
          {"headerName":"Payment Mode","field":"payment_mode"},
          {"headerName":"Services","field":"all_services"},
          {"headerName":"Completed Payments","field":"paid_services"}
        ] ,
        "rowData":[{
          "visit_id":visit["visit_id"],
          "name":visit["client_name"],
          "age":format_age(visit["client_birthdate"]),
          "gender":visit["client_gender"],
          "payment_mode":visit["payment_mode"].upper(),
          "all_services":len(self.get_visit_payments(visit["visit_id"])),
          "paid_services":len([payment for payment in self.get_visit_payments(visit["visit_id"]) if payment["paid"] and not payment["billed"]]),
        } for visit in self.get_completed_visits()]
      }
    ).classes(add="w-full h-full").on("cellClicked",lambda e:self.display_payments_dialog(e.args["data"]["visit_id"],"completed"))
  
  #Dialogs
  def display_payments_dialog(self,visit_id:str,display_tag:str):
    """Displays a dialog for adding payments"""
    
    visit = [visit for visit in self.visits if visit["visit_id"] == visit_id][0]
    
    completed_payments:list[dict[str,str|float]] = [payment for payment in visit["payments"] if payment["paid"] and not payment["billed"]]
    incomplete_payments = [payment for payment in visit["payments"] if payment["billed"] and payment["paid"]]
    billed_payments = [payment for payment in visit["payments"] if payment["billed"] and not payment["paid"]]
    unpaid_payments = [payment for payment in visit["payments"] if not payment["paid"] and not payment["billed"]]
    
    if display_tag == "all":
      payments = unpaid_payments + billed_payments + incomplete_payments + completed_payments
    if display_tag == "unattended":
      payments = unpaid_payments
    if display_tag == "billed":
      payments = billed_payments
    if display_tag == "incomplete":
      payments = incomplete_payments
    if display_tag == "completed":
      payments = completed_payments

    with ui.dialog() as self.payments_dialog,html.div().classes(add="bg-red-200"):
      #Client details
      ClientCard(details={"name":visit["client_name"],"age":format_age(visit["client_birthdate"]),"gender":visit["client_gender"],"address":visit["client_address"]})
      #Payments
      ui.label(text="PAYMENTS SUMMARY").classes(add="w-full bg-sky-500 text-center text-bold text-lg")
      with html.span().classes(add="bg-gray-500 w-full grid grid-cols-1 gap-y-2 px-1.5 py-2"):
        for payment in payments:
          PaymentCard(payment)

    self.payments_dialog.open()

