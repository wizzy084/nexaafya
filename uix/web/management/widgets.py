"""A module to degign widgets for 'manager' functionality"""

#GENERAL IMPORTS
import calendar
from datetime import datetime

#NiceGUI IMPORTS
from nicegui import html,ui

#ADMIN IMPORTS
from services.provider.admin.constants import *
from services.provider.admin.db import register_staff,register_service,update_staff,update_service,update_formulary
from services.provider.admin.processor import get_staffs,get_services,get_formulary,get_requisitions
from services.provider.clients.processor import get_visits,get_procedures,get_imagings

#UIX IMPORTS
from ..tools._snippets import is_in_range
from ..tools.widgets import *




###
class ManagementDisplay():
  """A class for UI functionalities for facility manager"""

  def __init__(self,user):
    #DATA
    self.user = user
    self.initial_data()

    sections = ["dashboard","settings","staff","services","formulary","inventory","assets"]

    #UI
    with html.div().classes(add="w-full h-full p-0 flex flex-col") as self.master_container:
      #Small Screen
      with html.section().classes(add="lg:hidden grow w-full flex flex-col"):
        #Tabs
        with html.div().classes(add="w-full p-0 rounded-b shadow-sm shadow-[#07004d]"):
          with ui.tabs(value=sections[0]).props(add="inline-label mobile-arrows outside-arrows active-class='text-sky-500'").classes(add="w-full rounded-b bg-harmony py-1 text-yellow-500 font-bold") as small_management_tabs:
            for section in sections:
              ui.tab(name=section).props(add="dense")
        
        #Panels
        with html.div().classes(add="order-first grow w-full rounded-br flex flex-col"):
          with ui.tab_panels(tabs=small_management_tabs,value=sections[3]).props(add="animated infinite transition-prev='jump-right' transition-next='jump-left' transition-duration='700'").classes(add="bg-inherit grow w-full grid grid-cols-1"):
            #Dashboard
            with ui.tab_panel(name="dashboard").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col gap-0.5"):
              ui.label('dashbodi')
            
            #Site Settings
            with ui.tab_panel(name="settings").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col gap-0.5"):
              ui.label('settings')

            #Staff Management
            with ui.tab_panel(name="staff").classes(add="w-full h-full p-0 rounded-0 flex flex-col"):
              StaffManager(user=self.user)
            
            #Services Management
            with ui.tab_panel(name="services").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col justify-around gap-0.5"):
              ServicesManager(user=self.user)
            
            #Formulary Management
            with ui.tab_panel(name="formulary").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col justify-around gap-0.5"):
              ui.label('Fomulali')
            
            #Inventory Management
            with ui.tab_panel(name="inventory").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col justify-between gap-0.5"):
              ui.label('Stocku')
            
            #Assets Management
            with ui.tab_panel(name="assets").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col gap-0.5"):
              ui.label('assets')
              
      #Large Screen
      with html.section().classes(add="grow w-full lg-flex flex-row"):
        #Tabs
        with html.div().classes(add="p-1 rounded-none shadow-sm shadow-[#07004d]"):
          with ui.tabs(value=sections[0]).props(add="inline-label mobile-arrows outside-arrows stretch vertical active-class='text-sky-500'").classes(add="w-full py-1 text-yellow-500 font-bold") as management_tabs:
            for section in sections:
              ui.tab(name=section).props(add="").classes(add="bg-harmony my-1 rounded-sm")
        
        #Panels
        with html.div().classes(add="grow rounded-br flex flex-col"):
          with ui.tab_panels(tabs=management_tabs,value=sections[3]).props(add="animated infinite transition-prev='jump-down' transition-next='jump-up' transition-duration='500'").classes(add="bg-inherit grow w-full grid grid-cols-1"):
            #Dashboard
            with ui.tab_panel(name="dashboard").classes(add="w-full h-full p-1 rounded-br flex flex-col lg:justify-around") as self.hpi_panel:
              ui.label('dashbodi')
            
            #Site Settings
            with ui.tab_panel(name="settings").classes(add="w-full h-full p-1 rounded-br flex flex-col lg:justify-around") as self.hpi_panel:
              ui.label('setups')
            
            #Staff Management
            with ui.tab_panel(name="staff").classes(add="w-full h-full p-0 rounded-0 flex flex-col"):
              StaffManager(user=self.user)
            
            #Services Management
            with ui.tab_panel(name="services").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col justify-around gap-0.5"):
              ServicesManager(user=self.user)
            
            #Formulary Management
            with ui.tab_panel(name="formulary").classes(add="w-full h-full p-0.5 rounded-0 flex flex-col justify-around gap-0.5"):
              ui.label('fomula')
            
            #Inventory
            with ui.tab_panel(name="inventory").classes(add="w-full h-full p-0.5 rounded-0 grid grid-cols-2 gap-0.5"):
              ui.label('inventoi')
            
            #Assets
            with ui.tab_panel(name="assets").classes(add="w-full h-full p-0.5 rounded-0 grid grid-cols-2 gap-0.5"):
              ui.label('assets')
      

  #FUNCTIONALITIES
  def initial_data(self):
    #ADMINself.services = get_services()
    self.formulary = get_formulary()
    self.requisitions = get_requisitions()
    #CLIENTS APP
    self.visits = get_visits()
  
  def client_visits(self,all:bool=False,year:bool=False,month:bool=False,day:bool=False):
    """Returns a dictionary with visit counts corresponding to date range"""
    #OUTPUTS
    total,new,revisits = 0,0,0

    visits = self.visits
    if all:
      total = len(visits)
    #Year data
    if year:
      annual_visits = [visit for visit in visits if visit["start_time"].year == datetime.now().year]
      new_visits = [visit for visit in annual_visits if visit["client_created_on"].year == visit["start_time"].year]
      revisits = [visit for visit in annual_visits if visit["client_created_on"].year != visit["start_time"].year]

      total,new,revisits = len(annual_visits),len(new_visits),len(revisits)
    #Month data
    if month:
      start_date,end_date = f"{datetime.now().strftime('%Y-%m')}-01",f"{datetime.now().strftime('%Y-%m')}-{calendar.monthrange(datetime.now().year,datetime.now().month)[1]}"
      monthly_visits = [visit for visit in visits if is_in_range(start_date=start_date,end_date=end_date,target_date=visit["start_time"])]
      new_visits = [visit for visit in monthly_visits if visit["client_created_on"].strftime("%Y-%m") == visit["start_time"].strftime("%Y-%m")]
      revisits = [visit for visit in monthly_visits if visit["client_created_on"].strftime("%Y-%m") != visit["start_time"].strftime("%Y-%m")]

      total,new,revisits = len(monthly_visits),len(new_visits),len(revisits)
    #Daily data
    if day:
      start_date,end_date = datetime.now().strftime("%Y-%m-%d"),datetime.now().strftime("%Y-%m-%d")
      daily_visits = [visit for visit in visits if visit["start_time"].date() == datetime.now().date()]
      new_visits = [visit for visit in daily_visits if visit["client_created_on"].date() == datetime.now().date()]
      revisits = [visit for visit in daily_visits if visit["client_created_on"].date() != datetime.now().date()]

      total,new,revisits = len(daily_visits),len(new_visits),len(revisits)
    
    #Returns
    return {"total":total,"new":new,"revisits":revisits}

  def client_services(self,all:bool=False,year:bool=False,month:bool=False,day:bool=False):
    """Returns a dictionary with visit counts corresponding to date range"""
    #OUTPUTS
    consults,imagings,procedures,pharmacy = 0,0,0,0

    visits = self.visits
    _consultations = [visit for visit in visits if visit["consultations"]]
    _pharmacy = [visit for visit in visits if visit["medications"]]
    _imagings,_procedures = [],[]
    for visit in visits:
      if visit["imagings"]:
        _imagings += visit["imagings"]
      if visit["procedures"]:
        _procedures += visit["procedures"]


    if all:
      consults,imagings,procedures,pharmacy = len(_consultations),len(_imagings),len(_procedures),len(_pharmacy)
    #Year data
    if year:
      annual_consults = [consult for consult in _consultations if consult["start_time"].year == datetime.now().year]
      annual_imagings = [imaging for imaging in _imagings if imaging["request_time"].year == datetime.now().year]
      annual_procedures = [procedure for procedure in _procedures if procedure["ordered_on"].year == datetime.now().year]
      annual_pharmacy =  [visit for visit in annual_consults if visit["medications"]]

      consults,imagings,procedures,pharmacy = len(annual_consults),len(annual_imagings),len(annual_procedures),len(annual_pharmacy)
    #Month data
    if month:
      monthly_consults = [consult for consult in _consultations if consult["start_time"].strftime("%Y-%m") == datetime.now().strftime("%Y-%m")]
      monthly_imagings = [imaging for imaging in _imagings if imaging["request_time"].strftime("%Y-%m") == datetime.now().strftime("%Y-%m")]
      monthly_procedures = [procedure for procedure in _procedures if procedure["ordered_on"].strftime("%Y-%m") == datetime.now().strftime("%Y-%m")]
      monthly_pharmacy =  [visit for visit in monthly_consults if visit["medications"]]

      consults,imagings,procedures,pharmacy = len(monthly_consults),len(monthly_imagings),len(monthly_procedures),len(monthly_pharmacy)
    #Daily data
    if day:
      today_consults = [consult for consult in _consultations if consult["start_time"].date() == datetime.now().date()]
      today_imagings = [imaging for imaging in _imagings if imaging["request_time"].date() == datetime.now().date()]
      today_procedures = [procedure for procedure in _procedures if procedure["ordered_on"].date() == datetime.now().date()]
      today_pharmacy =  [visit for visit in today_consults if visit["medications"]]

      consults,imagings,procedures,pharmacy = len(today_consults),len(today_imagings),len(today_procedures),len(today_pharmacy)
    
    #Returns
    return {"consults":consults,"imagings":imagings,"procedures":procedures,"pharmacy":pharmacy}

  def revenues(self,all:bool=False,year:bool=False,month:bool=False,day:bool=False):
    """A method that returns dictionary of revenues from client services"""
    #OUTPUTS
    consults,imagings,procedures,pharmacy = 0,0,0,0

    visits = self.visits
    _consults,_imagings,_pharmacy,_procedures = [],[],[],[]
    for visit in visits:
      if visit["consultations"]:
        _consults += visit["consultations"]
        for _consult in _consults:
          _consult["start_time"] = visit["start_time"]
      if visit["medications"]:
        _pharmacy += visit["medications"]
      if visit["imagings"]:
        _imagings += visit["imagings"]
      if visit["procedures"]:
        _procedures += visit["procedures"]

    #All
    if all:
      consults = sum([consult["payment"]["paid_amount"] for consult in _consults])
      imagings = sum([imaging["payment"]["paid_amount"] for imaging in _imagings])
      procedures = sum([procedure["payment"]["paid_amount"] for procedure in _procedures])
      pharmacy = sum([medicine["payment"]["paid_amount"] for medicine in _pharmacy])
    #Year data
    if year:
      annual_consults = sum([consult["payment"]["paid_amount"] for consult in _consults if consult["start_time"].year == datetime.now().year])
      annual_imagings = sum([imaging["payment"]["paid_amount"] for imaging in _imagings if imaging["request_time"].year == datetime.now().year])
      annual_procedures = sum([procedure["payment"]["paid_amount"] for procedure in _procedures if procedure["ordered_on"].year == datetime.now().year])
      annual_pharmacy =  sum([medicine["payment"]["paid_amount"] for medicine in _pharmacy if medicine["prescribed_on"].year == datetime.now().year])

      consults,imagings,procedures,pharmacy = annual_consults,annual_imagings,annual_procedures,annual_pharmacy
    #Month data
    if month:
      monthly_consults = sum([consult["payment"]["paid_amount"] for consult in _consults if consult["start_time"].strftime("%Y-%m") == datetime.now().strftime("%Y-%m")])
      monthly_imagings = sum([imaging["payment"]["paid_amount"] for imaging in _imagings if imaging["request_time"].strftime("%Y-%m") == datetime.now().strftime("%Y-%m")])
      monthly_procedures = sum([procedure["payment"]["paid_amount"] for procedure in _procedures if procedure["ordered_on"].strftime("%Y-%m") == datetime.now().strftime("%Y-%m")])
      monthly_pharmacy =  sum([medicine["payment"]["paid_amount"] for medicine in _pharmacy if medicine["prescribed_on"].strftime("%Y-%m") == datetime.now().strftime("%Y-%m")])

      consults,imagings,procedures,pharmacy = monthly_consults,monthly_imagings,monthly_procedures,monthly_pharmacy
    #Daily data
    if day:
      today_consults = sum([consult["payment"]["paid_amount"] for consult in _consults if consult["start_time"].date() == datetime.now().date()])
      today_imagings = sum([imaging["payment"]["paid_amount"] for imaging in _imagings if imaging["request_time"].date() == datetime.now().date()])
      today_procedures = sum([procedure["payment"]["paid_amount"] for procedure in _procedures if procedure["ordered_on"].date() == datetime.now().date()])
      today_pharmacy =  sum([medicine["payment"]["paid_amount"] for medicine in _pharmacy if medicine["prescribed_on"].date() == datetime.now().date()])

      consults,imagings,procedures,pharmacy = today_consults,today_imagings,today_procedures,today_pharmacy
    
    #Returns
    return {"consults":consults,"imagings":imagings,"procedures":procedures,"pharmacy":pharmacy}

  
  def update_formulary(self,data,edit=True):
    """"""

    if edit:
      data = {key:value.lower() for key,value in data.items() if type(value) == str}
      
      status = update_formulary(data)

      ui.notify(message=status["message"],type=status["type"],position=status["position"])
    
    self.formulary = get_formulary()
    self.FormularyAggrid(self.formulary)
    self.medicine_dialog.close()

  #DISPLAYS
  @ui.refreshable_method
  def Carousel(self):
    with ui.carousel(value="dashboard",animated=True).style(add="overflow-y:hidden;").classes(add="q-pa-none p-0.5 h-[87%] w-full bg-inherit rounded ring-1 ring-blue-400 shadow-md shadow-blue-400 animate__animated animate__fadeIn") as carousel:
      with carousel.add_slot("default"):
        with ui.carousel_slide(name="dashboard").classes(add="q-pa-none p-0.5 gap-0 w-full h-full rounded bg-inherit"):
          with html.div().classes(add="w-full h-full bg-inherit") as self.dashboard_panel:
            self.DashboardGrid()

        with ui.carousel_slide(name="staffs & services").classes(add="q-pa-none p-0.5 gap-0 w-full h-full rounded light-blur"):
          with html.div().props(add="elevated").classes(add="w-full h-full grid grid-cols-1 lg:grid-cols-2 gap-2"):
            #Staff Management
            with html.div().classes(add="w-full h-full grid grid-rows-8 rounded-md light-blur ring-1 ring-blue-500 shadow-lg shadow-blue-500"):
              #Header
              with html.div().classes(add="row-span-1 w-full flex flex-row bg-gray-900 rounded-t-md"):
                ui.label("STAFF MANAGEMENT PANEL").classes(add="rounded-t-md py-1 grow bg-inherit text-yellow-500 text-center text-2xl uppercase text-bold")
                ui.button(icon="fas fa-circle-plus",color="",on_click=self.StaffDialog).classes(add="size-12 rounded-[50%] bg-inherit ring-xs ring-yellow-500 text-yellow-500")
              #Body
              
          
            #Service Management
            with html.div().classes(add="w-full h-full grid grid-rows-8 rounded-md light-blur ring-1 ring-blue-500 shadow-lg shadow-blue-500"):
              #Body
              with html.div().classes(add="row-span-7 w-full h-full p-0.5 rounded") as self.services_panel:
                pass

        with ui.carousel_slide(name="assets").classes(add="q-pa-none gap-0 w-full h-full rounded light-blur"):
          with html.div().props(add="elevated").classes(add="w-full h-full grid grid-cols-1 lg:grid-cols-3 gap-2"):
            #Assets Management
            with html.div().classes(add="w-full h-full grid grid-rows-8 rounded-md light-blur ring-1 ring-blue-500 shadow-lg shadow-blue-500"):
              #Header
              with html.div().classes(add="row-span-1 w-full flex flex-row bg-gray-900 rounded-t-md"):
                ui.label("ASSETS").classes(add="rounded-t-md py-1 grow bg-inherit text-yellow-500 text-center text-2xl uppercase text-bold")
                ui.button(icon="fas fa-circle-plus",color="",on_click=self.StaffDialog).classes(add="size-12 rounded-[50%] bg-inherit ring-xs ring-yellow-500 text-yellow-500")
              #Body
              with html.div().classes(add="row-span-7 w-full h-full p-0.5 rounded") as self.assets_panel:
                pass
          
            #Formulary
            with html.div().classes(add="w-full h-full grid grid-rows-8 rounded-md light-blur ring-1 ring-blue-500 shadow-lg shadow-blue-500"):
              #Header
              with html.div().classes(add="row-span-1 w-full flex flex-row bg-gray-900 rounded-t-md"):
                ui.label("FACILITY FORMULARY").classes(add="rounded-t-md py-1 grow bg-inherit text-yellow-500 text-center text-2xl uppercase text-bold")
                ui.button(icon="fas fa-circle-plus",color="",on_click=self.MedicineDialog).classes(add="hidden size-12 rounded-[50%] bg-inherit ring-xs ring-yellow-500 text-yellow-500")
              #Body
              with html.div().classes(add="row-span-7 w-full h-full p-0.5 rounded") as self.formulary_panel:
                self.FormularyAggrid(self.formulary)
                
            #Requisition
            with html.div().classes(add="w-full h-full grid grid-rows-8 rounded-md light-blur ring-1 ring-blue-500 shadow-lg shadow-blue-500"):
              Requisitions(user=self.user,formulary=self.formulary,requisitions=self.requisitions)

    #Controls
    with html.div().classes(add="w-full h-[13%] py-3 flex flex-row justify-center gap-5 lg:gap-7"):
      ui.toggle(options=["dashboard","staffs & services","assets"]).props(add="glossy size='lg' toggle-color='bg-inerit' toggle-text-color='sky-500' text-color='yellow-500'").classes(add="bg-inherit rounded-full ring-1 ring-blue-400 shadow-md shadow-sky-500 text-bold").bind_value(carousel)
  
  
  
  def FormularyAggrid(self,formulary:list[dict]):
    """"""
    self.formulary_panel.clear()
    with self.formulary_panel:
      ui.aggrid(
        options={
          "columnDefs":[
            {"headerName":"S/N","field":"sno","width":40},
            {"headerName":"NAME","field":"name","sortable":True,"filter":True}
          ],
          "rowData":[
            {
              "sno":formulary.index(medicine) + 1,
              "name":medicine["name"].capitalize()
            } for medicine in formulary
          ]
        },
        theme="quartz"
      ).classes(add="w-full h-full bg-inherit rounded-b-md text-sm animate__animated animate__fadeIn").on("cellClicked",lambda e:self.MedicineDialog(medicine=[medicine for medicine in formulary if medicine['name'] == e.args['data']['name'].lower()][0]))

  

  
  def MedicineDialog(self,medicine:dict|None=None):
    """A method to display dialog for medicine editing"""
    # UI
    with ui.dialog().classes(add="rounded-sm") as self.medicine_dialog,html.div().style(add="min-width:80%;").classes(add="p-0.5 rounded-md ring-1 ring-blue-500 shadow-md shadow-blue-400 animate__animated animate__backInRight"):
      with html.div().classes(add="dialog-bg flex flex-col gap-3 rounded-sm rounded-md "):
        #Header
        with html.div().classes(add="bg-gray-900 flex flex-row justify-between"):
          ui.label("MEDICINE DETAILS").classes(add="bg-inherit p-2 grow text-yellow-600 text-3xl text-bold text-center")
          ui.button(icon="fas fa-circle-xmark fa-lg",color="",on_click=self.medicine_dialog.close).classes(add="bg-inherit text-rose-500 text-bold text-base")
        
        #Switch board
        if medicine:
          self.MedicineDetailsForm(medicine=medicine)
        else:
          self.MedicineDetailsForm()
    
    self.medicine_dialog.open()

  
  def MedicineDetailsForm(self,medicine:dict|None=None):
    #DATA
    MEDICINE_OPTIONS = [option.capitalize() for option in MEDICINE_TYPES]

    if medicine:
      data = medicine
      for key,value in data.items():
        if type(value) == str:
          data[key] = value.title()
    
    else:
      data = {
        "medicine_id":None,"name":None,"type":None,"drug_class":None,"active":None,
        "fda_pregnancy_category_1":None,"pregnancy_category_2":None,"fda_pregnancy_category_3":None,"prescription_level":None,
      }

    #UI
    with html.form().classes(add="w-full pt-0.5 pb-1 px-1 flex flex-col gap-2"):
      #General Details
      with html.fieldset().classes(add=" grid grid-cols-3 gap-3 p-2 rounded-sm ring-1 ring-gray-500 bg-sky-50"):
        html.legend('GENERAL DETAILS').classes(add="bg-sky-50 rounded-sm px-2 ring-1 ring-gray-500 text-bold text-xl text-yellow-600")
        ui.input(label="MEDICINE ID").props(add="readonly type='text'").style(add="caret-color:#daa520;").classes(add="px-1 outline outline-gray-300 rounded-sm  shadow-md shadow-sky-300 text-lg").bind_value(data,"medicine_id")
        ui.input(label="NAME").props(add="readonly type='text'").style(add="caret-color:#daa520;").classes(add="px-1 outline outline-gray-300 rounded-sm  shadow-md shadow-sky-300 text-lg").bind_value(data,"name")
        ui.select(label="TYPE",options=MEDICINE_OPTIONS).props(add="readonly type='text'").classes(add="px-1 outline outline-gray-300 rounded-sm  shadow-md shadow-sky-300 text-lg").bind_value(data,"type")
        ui.switch(text="ACTIVE").bind_value(data,"active").classes(add=f"px-1 bg-sky-100 outline outline-gray-300 rounded-sm shadow-md shadow-sky-300 {'text-yellow-600' if data['active'] else 'text-gray-500'} text-bold text-lg")
      #Prices
      with html.fieldset().classes(add=" grid grid-cols-2 lg:grid-cols-3 gap-2 p-2 rounded-sm ring-1 ring-gray-500 bg-sky-50 text-bold"):
        html.legend('PRESCRIPTION').classes(add="bg-sky-50 rounded-sm px-2 ring-1 ring-gray-500 text-bold text-xl text-yellow-600")
        with html.fieldset().classes(add="bg-sky-100 rounded-sm shadow-md shadow-sky-300"):
          html.legend("PREGNANCY CATEGORY(1ST TRIM)").classes(add="bg-skyy-100 rounded-sm px-1 small-caps text-bold text-md text-yellow-600")
          ui.radio(options=[None,"A","B","C","D","X"]).props(add="inline").bind_value(data,"fda_pregnancy_category_1")
        with html.fieldset().classes(add="bg-sky-100 rounded-sm shadow-md shadow-sky-300"):
          html.legend("PREGNANCY CATEGORY(2ND TRIM)").classes(add="bg-sky-100 rounded-sm px-1 small-caps text-bold text-md text-yellow-600")
          ui.radio(options=[None,"A","B","C","D","X"]).props(add="inline").bind_value(data,"fda_pregnancy_category_2")
        with html.fieldset().classes(add="bg-sky-100 rounded-sm shadow-md shadow-sky-300"):
          html.legend("PREGNANCY CATEGORY(3RD TRIM)").classes(add="bg-sky-100 rounded-sm px-1 small-caps text-bold text-md text-yellow-600")
          ui.radio(options=[None,"A","B","C","D","X"]).props(add="inline").bind_value(data,"fda_pregnancy_category_3")
        with html.fieldset().classes(add="bg-sky-100 rounded-sm shadow-md shadow-sky-300"):
          html.legend("PRESCRIPTION LEVEL").classes(add="bg-sky-100 rounded-sm px-1 small-caps text-bold text-md text-yellow-600")
          ui.radio(options=[None,"A","B","C","D","S"]).props(add="inline").bind_value(data,"prescription_level")

      #Buttons
      with html.div().classes(add=f"w-full pb-1 flex flex-row {'justify-around' if medicine else 'justify-center'}"):
        if medicine:
          ui.button(text="SAVE EDITS",icon="fas fa-user-pen",color="gray-900",on_click=lambda e:self.update_formulary(data=data,edit=True)).classes(add="text-yellow-500 text-bold text-xl shadow-md shadow-blue-400")
          ui.button(text="DELETE MEDICINE",icon="fas fa-user-pen",color="gray-900",on_click=lambda e:self.update_formulary(data=data,delete=True)).classes(add="hidden text-red-500 text-bold text-xl shadow-md shadow-blue-400")
        else:
          ui.button(text="SAVE SERVICE",icon="fa-regular fa-floppy-disk",color="gray-900").classes(add="text-yellow-500 text-bold text-xl shadow-md shadow-blue-400")

  def DashboardGrid(self):
    #DATA
    requisition = self.requisitions[0]
    #FXS
    def load_stats(period:str="today"):
      self.ReceptionStats(period=period)
      self.ServicesStats(period=period)
      self.RevenueStats(period=period)

    #UI
    self.dashboard_panel.clear()
    with self.dashboard_panel:
      with html.div().style(add="overflow-y:hidden;").classes(add="w-full h-full grid grid-cols-6 gap-1 bg-inherit rounded selectable-none"):
        #Reception Stats
        with html.div().classes(add="col-span-2 flex flex-col gap-1 rounded"):
          ui.toggle(options=["today","monthly","annual","all"],value="today",on_change=lambda e:load_stats(period=e.value)).props(add="glossy stretch size='lg' toggle-color='bg-inerit' toggle-text-color='sky-500' text-color='yellow-500'").classes(add="w-full bg-gray-900 rounded-t text-bold")
          with html.div().classes(add="rounded"):
            #ReceptionStats
            with html.div().classes(add="w-full rounded-b bg-gray-800") as self.reception_stats_panel:
              self.ReceptionStats()
            ui.separator().classes(add="w-full bg-yellow-500")
            #ServicesStats
            with html.div().classes(add="w-full rounded-b bg-gray-800") as self.services_stats_panel:
              self.ServicesStats()
            ui.separator().classes(add="w-full bg-yellow-500")
            #RevenueStats
            with html.div().classes(add="w-full rounded-b bg-gray-800") as self.revenue_stats_panel:
              self.RevenueStats()
        #Stock Analysis
        with html.div().classes(add="col-span-2"):
          #StockAnalysisDisplay(requisition=requisition)
          pass
        #Dispensing Management
        with html.div().classes(add="col-span-2"):
          DispensingStoreManagement(requisition=requisition)
  
  def ReceptionStats(self,period:str="today"):
    """A widget to display dynamic data of visits"""
    #DATA
    if period == "today":
      visits = self.client_visits(day=True)
    elif period == "monthly":
      visits = self.client_visits(month=True)
    elif period == "yearly":
      visits = self.client_visits(year=True)
    else:
      visits = self.client_visits(all=True)
    
    #UI
    self.reception_stats_panel.clear()
    with self.reception_stats_panel:
      with ui.label().props(add="glossy").classes(add="w-full p-1 bg-gray-800 rounded-b flex flex-row justify-between animate__animated animate__fadeIn") as imagings_button:
        #Total
        with ui.chip(text="VISITS",text_color="",color="").props(add="dense").classes(add="h-full m-0 bg-inherit rounded text-xl text-sky-300 text-bold animate__animated animate__fadeIn"):
          ui.chip(text=f"{visits['total']:,.0f}",color="").classes(add="h-full m-0 bg-inherit text-lg text-white animate__animated animate__zoomIn")
        #New
        with ui.chip(text="NEW",text_color="teal-12",color="").props(add="dense").classes(add=f"{'hidden' if period == 'all' else ''} h-full m-0 bg-inherit text-lg text-bold animate__animated animate__fadeIn"):
          ui.chip(text=f"{visits['new']:,.0f}",color="").classes(add=f"{'hidden' if period == 'all' else ''} h-full m-0 bg-inherit text-lg text-white animate__animated animate__zoomIn")
        #Revisits
        with ui.chip(text="REVISITS",text_color="teal-12",color="").props(add="dense").classes(add=f"{'hidden' if period == 'all' else ''} h-full m-0 bg-inherit text-lg text-bold animate__animated animate__fadeIn"):
          ui.chip(text=f"{visits['revisits']:,.0f}",color="").classes(add="h-full m-0 bg-inherit text-lg text-white animate__animated animated__zoomIn")
 
  def ServicesStats(self,period:str="today"):
    """A widget to display dynamic data of services"""
    #DATA
    if period == "today":
      services = self.client_services(day=True)
    elif period == "monthly":
      services = self.client_services(month=True)
    elif period == "yearly":
      services = self.client_services(year=True)
    else:
      services = self.client_services(all=True)
    
    #UI
    self.services_stats_panel.clear()
    with self.services_stats_panel:
      with html.div().classes(add="w-full px-2 pt-2 flex flex-row justify-between"):
        with ui.label("SERVICES").classes(add="text-sky-300 text-bold text-xl"):
          ui.label(f"{services['consults'] + services['imagings'] + services['procedures'] + services['pharmacy']:,.0f}").classes(add="inline ml-3 text-white text-bold animate__aniamted animate__zoomIn")
        #space for pop pup button
      with ui.label().classes(add="w-full p-1 bg-gray-800 rounded-b grid grid-cols-2 animate__animated animate__fadeIn"):
        #Consultations
        with ui.chip(text="CONSULTATIONS",text_color="teal-12",color="").props(add="dense").classes(add="w-full h-full m-0 bg-inherit text-lg text-bold animate__animated animate__fadeIn"):
          ui.chip(text=f"{services['consults']:,.0f}",color="").classes(add="h-full m-0 bg-inherit text-lg text-white animate__animated animate__zoomIn animate__slow")
        #Imagings
        with ui.chip(text="IMAGINGS",text_color="teal-12",color="").props(add="dense").classes(add=f"w-full h-full m-0 bg-inherit text-lg text-bold animate__animated animate__fadeIn"):
          ui.chip(text=f"{services['imagings']:,.0f}",color="").classes(add=f"h-full m-0 bg-inherit text-lg text-white animate__animated animate__zoomIn animate__slow")
        #Procedures
        with ui.chip(text="PROCEDURES",text_color="teal-12",color="").props(add="dense").classes(add=f"w-full h-full m-0 bg-inherit text-lg text-bold animate__animated animate__fadeIn"):
          ui.chip(text=f"{services['procedures']:,.0f}",color="").classes(add="h-full m-0 bg-inherit text-lg text-white animate__animated animate__zoomIn animate__slow")
        #Pharmacy
        with ui.chip(text="PHARMACY",text_color="teal-12",color="").props(add="dense").classes(add=f"w-full h-full m-0 bg-inherit text-lg text-bold animate__animated animate__fadeIn"):
          ui.chip(text=f"{services['pharmacy']:,.0f}",color="").classes(add="h-full m-0 bg-inherit text-lg text-white animate__animated animate__zoomIn animate__slow")
 
  def RevenueStats(self,period:str="today"):
    """A widget to display dynamic data of services"""
    #DATA
    if period == "today":
      revenue = self.revenues(day=True)
    elif period == "monthly":
      revenue = self.revenues(month=True)
    elif period == "yearly":
      revenue = self.revenues(year=True)
    else:
      revenue = self.revenues(all=True)
    
    #UI
    self.revenue_stats_panel.clear()
    with self.revenue_stats_panel:
      with html.div().classes(add="w-full px-2 py-2 flex flex-row justify-between"):
        with ui.label("REVENUES").classes(add="text-sky-300 text-bold text-xl"):
          ui.label(f"{revenue['consults'] + revenue['imagings'] + revenue['procedures'] + revenue['pharmacy']:,.2f} TZS").classes(add="inline ml-3 text-white text-bold")
        #space for pop pup button
      with ui.label().classes(add="w-full p-1 bg-gray-800 rounded-b grid grid-cols-2 grid-rows-4 animate__animated animate__fadeIn"):
        #Consultations
        ui.chip(text="CONSULTATIONS",text_color="teal-12",color="").props(add="dense").classes(add="row-start-1 col-start-1 w-full m-0 bg-inherit text-lg text-bold animate__animated animate__fadeIn")
        ui.chip(text=f"{revenue['consults']:,.2f} TZS",color="").classes(add="row-start-1 col-start-2 justify-self-center m-0 bg-inherit text-lg text-bold text-white animate__animated animate__zoomIn")
        #Imagings
        ui.chip(text="IMAGINGS",text_color="teal-12",color="").props(add="dense").classes(add=f"row-start-2 col-start-1 w-full m-0 bg-inherit text-lg text-bold animate__animated animate__fadeIn")
        ui.chip(text=f"{revenue['imagings']:,.2f} TZS",color="").classes(add=f"row-start-2 col-start-2 justify-self-center m-0 bg-inherit text-lg text-bold text-white animate__animated animate__zoomIn")
        #Procedures
        ui.chip(text="PROCEDURES",text_color="teal-12",color="").props(add="dense").classes(add=f"row-start-3 col-start-1 w-full m-0 bg-inherit text-lg text-bold animate__animated animate__fadeIn")
        ui.chip(text=f"{revenue['procedures']:,.2f} TZS",color="").classes(add="row-start-3 col-start-2 justify-self-center m-0 bg-inherit text-lg text-bold text-white animate__animated animate__zoomIn")
        #Pharmacy
        ui.chip(text="PHARMACY",text_color="teal-12",color="").props(add="dense").classes(add=f"row-start-4 col-start-1 w-full m-0 bg-inherit text-lg text-bold animate__animated animate__fadeIn")
        ui.chip(text=f"{revenue['pharmacy']:,.2f} TZS",color="").classes(add="row-start-4 col-start-2 justify-self-center m-0 bg-inherit text-lg text-bold text-white animate__animated animate__zoomIn")
 



      








    











