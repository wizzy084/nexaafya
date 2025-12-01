"""A module to degign widgets for 'imaging' functionality"""

#GENERAL IMPORTS
import math
from uuid import uuid4

#NiceGUI IMPORTS
from nicegui import html,ui

#APP IMPORTS
from services.provider.admin.db import update_requisition,register_inventory
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
              pass
            #For small screens
            with html.div().classes(add="grow w-full lg:hidden") as self.triages_mini_panel:
              pass
          
          #Dispensing
          with ui.carousel_slide(name="dispensing").classes(add="q-pa-none p-0.5 gap-0 w-full h-full rounded-b"):
            #For large screens
            with html.div().classes(add="w-full grow lg-show") as self.dispensing_panel:
              pass
            #For small screens
            with html.div().classes(add="grow w-full lg:hidden") as self.dispensing_mini_panel:
              pass

      #Controls
      with html.div().classes(add="w-full py-1 flex flex-row justify-center gap-5 lg:gap-7"):
        ui.toggle(options=["triage","dispensing"]).props(add="glossy size='lg' toggle-color='bg-inherit' toggle-text-color='sky-500' text-color='yellow-500'").classes(add="lg-show bg-[#07004d] rounded-full ring-1 ring-blue-500 shadow-md shadow-sky-600 text-bold").bind_value(carousel)
    


#SUBWIDGETS

    
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
    


