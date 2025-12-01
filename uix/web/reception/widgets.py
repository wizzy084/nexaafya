"""A module for structuring and styling page components for Panel app functionality"""

#GENERAL IMPORTS
from time import sleep
from datetime import date

#APP IMPORTS
from services.provider.admin.processor import get_facility_data,get_staffs,get_staff,get_staff_username,get_services
from services.provider.clients.db import register_triage,update_payment
from services.provider.clients.processor import get_clients,get_active_visits

#UIX IMPORT
from ..tools.widgets import AppointmentsManager
from ..tools.components import ClientCard
from ..tools._snippets import format_age




###

  
class ReportsDisplay():
  """A class to display reports"""

  def __init__(self):
    #Weekly view data
    self.target_year = datetime.now().year
    self.today = datetime.now().date()
    self.last_week = self.today + timedelta(days=-7)

    #Monthly view data
    self.picked_year,self.picked_month = datetime.now().year,list(calendar.month_name[1:])[int(datetime.now().month)-1]
    #Toggle button
    with html.div().classes(add="w-full py-2 flex flex-row-reverse justify-center"):
      self.duration_toggle = ui.toggle(options=["daily","weekly","monthly","annual"],value="daily",on_change=lambda e:self.load_ranged_report(e.value)).classes(add="bg-gray-200 text-bold")
    
    #Default selection panel
    with html.div().classes(add="w-full flex flex-row justify-center") as self.selection_panel:
      if self.duration_toggle.value == "daily":
        with ui.input(label="Pick date",value=datetime.now().strftime("%Y-%m-%d"),on_change=lambda e:self.load_daily_report(e.value)).props(add="readonly").classes(add="bg-sky-50 rounded-sm m-1 pl-20 text-lg") as self.default_picked_date:
          with ui.dialog() as daily_calendar:
            ui.date(value=datetime.now(),on_change=daily_calendar.close).bind_value(self.default_picked_date)
          with self.default_picked_date.add_slot("prepend"):
            ui.icon("fas fa-calendar-check fa-xl",color="sky-500").on("click",daily_calendar.open)
      
      if self.duration_toggle.value == "weekly":
        now = datetime.now()
        today = now.date().strftime("%Y-%m-%d")
        last_week = (now.date() + timedelta(days=-7)).strftime("%Y-%m-%d")
        input_range:str = f"{last_week} | {today}"
        #Selection panel
        with self.selection_panel:
          #Date range picker
          with ui.input(label="Date range",value=input_range,on_change=lambda e:self.load_weekly_report(e.value)).props(add="range readonly").classes(add="bg-sky-50 rounded m-1 px-20 text-lg") as date_range_input:
            with ui.dialog() as weekly_calendar:
              ui.date(value=datetime.now(),on_change=weekly_calendar.close).props(add="range").bind_value(
                date_range_input,
                forward=lambda x:f'{x["from"]} | {x["to"]}' if x else None,
                backward=lambda x:{'from':x.split(' | ')[0],'to':x.split(' | ')[1]} if ' | ' in (x or '') else None
              )
            with date_range_input.add_slot("prepend"):
              ui.icon("fas fa-calendar-check fa-xl",color="sky-500").on("click",weekly_calendar.open)
      
      if self.duration_toggle.value == "monthly":
        
        with ui.button_group():
          ui.select(label="Year",options=[2025,2024,2023],on_change=self.load_monthly_report).classes(add="px-2 text-lg").bind_value(self,"picked_year")
          ui.select(label="Month",options=list(calendar.month_name)[1:],on_change=self.load_monthly_report).classes(add="px-2 text-lg").bind_value(self,"picked_month")

      if self.duration_toggle.value == "annual":
        
        ui.select(label="Year",options=[2025,2024,2023],on_change=self.load_annual_report).classes(add="w-44 px-2 text-lg").bind_value(self,"picked_year")        
    
    #Default report panel
    with html.div().classes(add="w-full h-full") as self.report_panel:
      if self.duration_toggle.value == "daily":
        ReportFrame(start_date=self.default_picked_date.value,end_date=self.default_picked_date.value)
      if self.duration_toggle.value == "weekly":
        self.report_panel.clear()
        with self.report_panel:
          ReportFrame(start_date=last_week,end_date=today)
      if self.duration_toggle.value == "monthly":
        #Data
        start_date = f"{datetime.now().strftime('%Y-%m')}-01"
        end_date = f"{datetime.now().strftime('%Y-%m')}-{calendar.monthrange(datetime.now().year,datetime.now().month)[1]}"
        #UI
        ReportFrame(start_date=start_date,end_date=end_date)
      if self.duration_toggle.value == "annual":
        #Data
        start_date = f"{self.picked_year}-01-01"
        end_date = f"{self.picked_year}-12-31"
        #UI
        ReportFrame(start_date=start_date,end_date=end_date)
      
  
  def load_ranged_report(self,duration:str):
    """A method which changes the default display of the page based on the value of 'duration'"""

    self.selection_panel.clear()
    self.report_panel.clear()
    #Selection
    if duration == "daily":
      #Default selection panel
      with self.selection_panel:
        with ui.input(label="Pick date",value=datetime.now().strftime("%Y-%m-%d"),on_change=lambda e:self.load_daily_report(e.value)).props(add="readonly").classes(add="bg-sky-50 rounded-sm m-1 px-2 text-lg") as self.picked_date:
          with ui.dialog() as daily_calendar:
            ui.date(value=datetime.now(),on_change=daily_calendar.close).bind_value(self.picked_date)
          with self.picked_date.add_slot("prepend"):
            ui.icon("fas fa-calendar-check fa-xl",color="sky-500").on("click",daily_calendar.open)
      #Default report panel
      with self.report_panel:
        ReportFrame(start_date=self.picked_date.value,end_date=self.picked_date.value)
    
    if duration == "weekly":
      now = datetime.now()
      today = now.date().strftime("%Y-%m-%d")
      last_week = (now.date() + timedelta(days=-7)).strftime("%Y-%m-%d")
      input_range:str = f"{last_week} | {today}"
      #Selection panel
      with self.selection_panel:
        #Date range picker
        with ui.input(label="Date range",value=input_range,on_change=lambda e:self.load_weekly_report(e.value)).props(add="range readonly").classes(add="bg-sky-50 rounded m-1 px-20 text-lg") as date_range_input:
          with ui.dialog() as weekly_calendar:
            ui.date(value=datetime.now(),on_change=lambda e:weekly_calendar.close()).props(add="range").bind_value(
              date_range_input,
              forward=lambda x:f'{x["from"]} | {x["to"]}' if x else None,
              backward=lambda x:{'from':x.split(' | ')[0],'to':x.split(' | ')[1]} if ' | ' in (x or '') else None
            )
          with date_range_input.add_slot("prepend"):
            ui.icon("fas fa-calendar-check fa-xl",color="sky-500").on("click",weekly_calendar.open)
      
      #Default weekly report
      self.report_panel.clear()
      with self.report_panel:
        ReportFrame(start_date=last_week,end_date=today)
    
    if duration == "monthly":
      with self.selection_panel:
        with ui.button_group():
          ui.select(label="Year",options=[2025,2024,2023],on_change=self.load_monthly_report).classes(add="px-2 text-lg").bind_value(self,"picked_year")
          ui.select(label="Month",options=list(calendar.month_name)[1:],on_change=self.load_monthly_report).classes(add="px-2 text-lg").bind_value(self,"picked_month")
      
      with self.report_panel:
        #Data
        start_date = f"{datetime.now().strftime('%Y-%m')}-01"
        end_date = f"{datetime.now().strftime('%Y-%m')}-{calendar.monthrange(datetime.now().year,datetime.now().month)[1]}"
        #UI
        ReportFrame(start_date=start_date,end_date=end_date)

    if duration == "annual":
      with self.selection_panel:
        ui.select(label="Year",options=[2025,2024,2023],on_change=self.load_annual_report).classes(add="w-44 px-2 text-lg").bind_value(self,"picked_year")
      
      with self.report_panel:
        #Data
        start_date = f"{self.picked_year}-01-01"
        end_date = f"{self.picked_year}-12-31"
        #UI
        ReportFrame(start_date=start_date,end_date=end_date)
  
  def load_daily_report(self,date:str):
    """A method to load daily report based on 'date' value"""

    self.report_panel.clear()
    with self.report_panel:
      ReportFrame(start_date=date,end_date=date)
  
  def load_weekly_report(self,date_range:str):
    """A method to load weekly report"""

    if date_range:
      dates:list[str] = date_range.split(" | ")

      self.report_panel.clear()
      with self.report_panel:
        ReportFrame(start_date=dates[0],end_date=dates[1])
  
  def load_monthly_report(self):
    """Displays monthly report based on ' '"""

    #Data
    _month = list(calendar.month_name).index(self.picked_month)
    if _month >=10:
      start_date = f"{self.picked_year}-{_month}-01"
      end_date = f"{self.picked_year}-{_month}-{calendar.monthrange(self.picked_year,_month)[1]}"
    else:
      start_date = f"{self.picked_year}-0{_month}-01"
      end_date = f"{self.picked_year}-0{_month}-{calendar.monthrange(self.picked_year,_month)[1]}"
        
    #UI
    try:
      self.report_panel.clear()
      with self.report_panel:
        ReportFrame(start_date=start_date,end_date=end_date)
    except:
      return
    
  def load_annual_report(self):
    """A method that loads a ReportFrame object with annual statistics calculated from 'self.picked_year'"""

    #Data
    start_date = f"{self.picked_year}-01-01"
    end_date = f"{self.picked_year}-12-31"
    #UI
    try:
      self.report_panel.clear()
      with self.report_panel:
        ReportFrame(start_date=start_date,end_date=end_date)
    except:
      return


