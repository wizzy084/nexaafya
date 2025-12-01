"""A module to degign widgets for 'consultation' functionality"""

#GENERAL IMPORT
import string


#NiceGUI IMPORTS
from nicegui import html,ui

#ADMIN APP IMPORTS
from services.provider.clients.processor import get_active_visits,get_clients

#UIX IMPORTS
from ..tools._snippets import format_age
from ..tools.widgets import ConsultationsManager,AppointmentsManager,ProceduresManager





##
class ServicesManagementDisplay():
  """A class of UI for managing consultations"""

  def __init__(self,user):
    #DATA
    self.user = user
    self.initial_data()
    
    #UI
    with html.div().classes(add="w-full h-full flex flex-col p-0 gap-1 bg-inherit animate__animated animate__fadeIn") as self.master_container:
      self.Carousel()  

  def initial_data(self):
    #Consultations
    self.active_clients = sorted([client for client in get_clients() if client["client_id"] in [visit['client_id'] for visit in get_active_visits()]],key=lambda e:e["visits"][-1]["start_time"],reverse=True)
    self.raw_consultations = [visit for visit in [client["visits"][-1] for client in self.active_clients] if visit["consultations"] and (visit["consultations"][0]["payment"]["paid"] or visit["consultations"][0]["payment"]["billed"])]
    self.new_consultations = [visit for visit in self.raw_consultations if not visit["consultations"][0]["initiated"]]
    self.cont_consultations = [visit for visit in self.raw_consultations if visit["consultations"][0]["initiated"]]
    self.consulted_clients = [client for client in self.active_clients if client["client_id"] in [consult["client_id"] for consult in self.new_consultations + self.cont_consultations]]
    self.consulted_visits = self.consultations = self.new_consultations + self.cont_consultations
    self.lab_consultations = []
    self.imaging_consultations = []
    self.procedure_consultations = []
    self.pharmacy_consultations = []
  
  #FUNCTIONALITIES
  
  #UI
  def Carousel(self):
    self.master_container.clear()
    with self.master_container:
      #Display
      with ui.carousel(value="consults").style(add="overflow-y:hidden;").props(add="animated swipeable transition-prev='jump-right' transition-next='jump-left' transition-duration='100'").classes(add="grow flex flex-col q-pa-none w-full bg-inherit rounded shadow-md shadow-blue-500 animate__animated animate__fadeIn") as carousel:
        with carousel.add_slot("default"):
          #Consults
          with ui.carousel_slide(name="consults").classes(add="q-pa-none gap-0 w-full h-full rounded-b bg-sky-100 flex flex-col"):
            ConsultationsManager(user=self.user,consulted_clients=self.consulted_clients,consulted_visits=self.consulted_visits)
              
          with ui.carousel_slide(name="procedures").classes(add="q-pa-none gap-0 w-full h-full rounded-b bg-sky-100 flex flex-col"):
            ProceduresManager(user=self.user)
          
          with ui.carousel_slide(name="appointments").classes(add="q-pa-none p-0.5"):
            with html.div().classes(add="w-full h-full"):
              AppointmentsManager(user=self.user)

      #Controls
      with html.div().classes(add="w-full py-1 flex flex-row justify-center gap-5 lg:gap-7"):
        ui.toggle(options=["consults","procedures","appointments"]).props(add="glossy size='lg' toggle-color='bg-inherit' toggle-text-color='sky-500' text-color='yellow-500'").classes(add="lg-show bg-[#07004d] rounded-full ring-1 ring-blue-500 shadow-md shadow-sky-600 text-bold").bind_value(carousel)
  
  
  

  
class ClinicianReportsManagementDisplay():
  """A class of UI for managing consultations"""

  def __init__(self):

    with html.div():
      ui.label('Reporteeee!')

