"""A module for small UI widgets that can be used in the main application"""

#GENERAL IMPORTS
from nicegui import html,ui



###
def CompanyName():
  """A company name"""

  with html.strong().classes(add=f"text-xl"):
    html.span("Nexa").classes(add="bg-inherit text-bold text-sky-400 m-0 p-0 text-base")
    html.span("Soft").classes(add="bg-inherit  text-bold text-green-400 m-0 p-0 text-base")

def BrandName(size:str=None):
  """A brand name"""

  with html.strong().classes(add="select-none"):
    ui.badge(text="Nexa",color="").classes(add=f"bg-inherit text-sky-500 text-bold m-0 p-0 {size}")
    ui.badge(text="Clinic",color="").classes(add=f"bg-inherit text-green-500 text-bold m-0 p-0 {size}")
   
class ClientCard():
  """A class to construct a card for client data display"""

  def __init__(self,details:dict[str,str],name_only:bool=False,small:bool=False):
    """
    Displays display card with basic client information.
    if small is set to True, then the middle name is denoted as an initial.
    If name_only is set to True, then only names are displayed
    """
    
    with html.div().classes(f"{'hidden' if name_only else ''} w-full h-full rounded bg-inherit text-yellow-500"):
      #Name
      ui.label(text=f"{details['short_name'].lower()}").style(add="text-shadow:2px 2px #505050").classes(add="lg:hidden w-full px-1 bg-inherit small-caps text-bold text-3xl text-center")     #For small screen
      ui.label(text=f"{details['name'].lower()}").style(add="text-shadow:2px 2px #505050").classes(add="lg-show w-full px-1 bg-inherit small-caps text-bold text-3xl text-center")     #For large screen
      #Particulars
      with html.span().classes(add=f"w-full flex flex-row justify-center flex-wrap"):
        #Client age
        ui.chip(text=details["age"],text_color="yellow-500",color="").props(add="dense").classes(add="rounded-sm bg-inherit text-base text-bold shadow-sm shadow-yellow-500")
        #Client gender
        ui.chip(text=details["gender"].capitalize(),text_color="yellow-500",color="").props(add="dense").classes(add="rounded-sm bg-inherit text-base text-bold shadow-sm shadow-yellow-500")
        #Client address
        ui.chip(text=details["address"].title(),text_color="yellow-500",color="").props(add="dense").classes(add="rounded-sm bg-inherit text-base text-bold shadow-sm shadow-yellow-500")
        #Last visit
        if "last_visit" in details:
          ui.chip(text=details["last_visit"],text_color="red" if details["last_visit"].lower().startswith("no") else "yellow-500",color="").props(add="dense").classes(add="rounded-sm bg-inherit text-base text-bold shadow-sm shadow-yellow-500")

def GenderAge(data:dict):
  """Returns a string of html elements for display in small screens"""

  def GenderIcon(data):
    """Returns a styled gender icon based on gender key in data input"""

    genders = {"male":"mars","female":"venus"}
    colors = {"male":"sky-600","female":"pink-600"}

    return f"<span class='fa-solid fa-{genders[data['gender'].lower()]} text-{colors[data['gender'].lower()]}'></span>"
  
  age = f"<span class='ml-1'>{data['age'].split(' ')[0]} {data['age'].split(' ')[1][0].upper()}</span>"
  gender = GenderIcon(visit)

  return f"<span class='h-full'>{gender}{age}</span>"

def StatusDot(active:bool=True):
  """A function to return a styled icon based on value of active"""

  return f"<span class='fa-solid fa-circle { 'text-green-600' if active  else 'text-red-600'}'></span>"


###

class SystemsReview():
  """A class for displaying Systems Review"""

  def __init__(self):

    with html.div().classes(add="w-full rounded grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 gap-3"):
      self.display_ros_cns()
      self.display_ros_cvs()
      self.display_ros_rs()
      self.display_ros_git()
      self.display_ros_gus()
      self.display_ros_mss()
      self.display_ros_derma()
      self.display_ros_ent()
  
  @ui.refreshable_method
  def display_ros_cns(self):
    """A method to display CVS box"""

    self.ros_cns,set_ros_cns = ui.state("")

    ui.textarea(label="CNS",value=self.ros_cns,on_change=lambda e:set_ros_cns(e.value)).props(add="autofocus clearable").classes(add="w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_ros_cvs(self):
    """A method to display CVS box"""

    self.ros_cvs,set_ros_cvs = ui.state("")

    ui.textarea(label="CARDIOVASCULAR",value=self.ros_cvs,on_change=lambda e:set_ros_cvs(e.value)).props(add="autofocus clearable").classes(add="w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_ros_rs(self):
    """A method to display RS box"""

    self.ros_rs,set_ros_rs = ui.state("")

    ui.textarea(label="RESPIRATORY",value=self.ros_rs,on_change=lambda e:set_ros_rs(e.value)).props(add="autofocus clearable").classes(add="w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_ros_git(self):
    """A method to display GIT box"""

    self.ros_git,set_ros_git = ui.state("")

    ui.textarea(label="GIT",value=self.ros_git,on_change=lambda e:set_ros_git(e.value)).props(add="autofocus clearable").classes(add="w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_ros_gus(self):
    """A method to display GUS box"""

    self.ros_gus,set_ros_gus = ui.state("")

    ui.textarea(label="GENITOURINARY",value=self.ros_gus,on_change=lambda e:set_ros_gus(e.value)).props(add="autofocus clearable").classes(add="w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_ros_mss(self):
    """A method to display MSS box"""

    self.ros_mss,set_ros_mss = ui.state("")

    ui.textarea(label="MUSCULOSKELETAL",value=self.ros_mss,on_change=lambda e:set_ros_mss(e.value)).props(add="autofocus clearable").classes(add="w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_ros_derma(self):
    """A method to display DERMA box"""

    self.ros_derma,set_ros_derma = ui.state("")

    ui.textarea(label="INTEGUMENTARY",value=self.ros_derma,on_change=lambda e:set_ros_derma(e.value)).props(add="autofocus clearable").classes(add="w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_ros_ent(self):
    """A method to display ENT box"""

    self.ros_ent,set_ros_ent = ui.state("")

    ui.textarea(label="ENT",value=self.ros_ent,on_change=lambda e:set_ros_ent(e.value)).props(add="autofocus clearable").classes(add="w-full outline outline-sky-700 rounded-sm px-3 text-sm")

class GeneralExaminationForm():
  """A class to display,edit and save general examination data"""

  @ui.refreshable_method
  def __init__(self,ge:dict):
    #DATA
    self.ge = ge
    self.findings,self.set_findings = ui.state("")
    #UI
    with html.div().classes(add="w-full rounded"):
      #GE
      ui.textarea(label="GENERAL EXAM",value=self.findings,on_change=lambda e:self.save_notes(e.value)).props(add="autofocus clearable").classes(add="w-full outline outline-yellow-800 rounded-md px-3 text-sm")
  
  def save_notes(self,notes:str):

    self.set_findings(notes)
    
    register_general_exam({"ge_id":self.ge["ge_id"],"notes":notes})

class CardiovascularExaminationForm():
  """A class to display,edit and save general examination data"""
  
  def __init__(self):
    #UI
    with html.div().classes(add="w-full rounded grid sm:grid-cols-4 gap-2"):
      self.display_auscultation()
      self.display_palpation()
      self.display_inspection()
      self.display_inverted_j()

  @ui.refreshable_method
  def display_inverted_j(self):
    """Display for CVS inspection"""

    self.cvs_inverted_j,set_cvs_inverted_j = ui.state("")

    ui.textarea(label="INVERTED J",value=self.cvs_inverted_j,on_change=lambda e:set_cvs_inverted_j(e.value)).props(add="autofocus").classes(add="order-first w-full outline outline-sky-700 rounded-sm px-3 text-sm")

  @ui.refreshable_method
  def display_inspection(self):
    """Display for CVS inspection"""

    self.cvs_inspection,set_cvs_inspection = ui.state("")

    ui.textarea(label="PRECORDIAL INSPECTION",value=self.cvs_inspection,on_change=lambda e:set_cvs_inspection(e.value)).props(add="autofocus").classes(add="order-2 w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_palpation(self):
    """Display for CVS palpation"""

    self.cvs_palpation,set_cvs_palpation = ui.state("")

    ui.textarea(label="PRECORDIAL PALPATION",value=self.cvs_palpation,on_change=lambda e:set_cvs_palpation(e.value)).props(add="autofocus").classes(add="order-3 w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_auscultation(self):
    """Display for CVS auscultation"""

    self.cvs_auscultation,set_cvs_auscultation = ui.state("")

    ui.textarea(label="PRECORDIAL AUSCULTATION",value=self.cvs_auscultation,on_change=lambda e:set_cvs_auscultation(e.value)).props(add="autofocus").classes(add="order-last w-full outline outline-sky-700 rounded-sm px-3 text-sm")

class RespiratoryExaminationForm():
  """A class to display Respiratory examination functionality"""

  def __init__(self):
    with html.div().classes(add="w-full rounded grid sm:grid-cols-4 gap-2"):
      self.display_palpation()
      self.display_percussion()
      self.display_auscultation()
      self.display_inspection()
    
  @ui.refreshable_method
  def display_inspection(self):
    """A method to display inspection box"""

    self.rs_inspection,set_rs_inspection = ui.state("")

    ui.textarea(label="INSPECTION",value=self.rs_inspection,on_change=lambda e:set_rs_inspection(e.value)).props(add="autofocus").classes(add="order-first w-full outline outline-sky-700 rounded-sm px-3 text-sm")
    
  @ui.refreshable_method
  def display_palpation(self):
    """A method to display palpation box"""
    
    self.rs_palpation,set_rs_palpation = ui.state("")

    ui.textarea(label="PALPATION",value=self.rs_palpation,on_change=lambda e:set_rs_palpation(e.value)).props(add="autofocus").classes(add="order-2 w-full outline outline-sky-700 rounded-sm px-3 text-sm")

  @ui.refreshable_method
  def display_percussion(self):
    """A method to display percussion box"""
    
    self.rs_percussion,set_rs_percussion = ui.state("")

    ui.textarea(label="PERCUSSION",value=self.rs_percussion,on_change=lambda e:set_rs_percussion(e.value)).props(add="autofocus").classes(add="order-3 w-full outline outline-sky-700 rounded-sm px-3 text-sm")

  @ui.refreshable_method
  def display_auscultation(self):
    """A method to display auscultation box"""
    
    self.rs_auscultation,set_rs_auscultation = ui.state("")

    ui.textarea(label="AUSCULTATION",value=self.rs_auscultation,on_change=lambda e:set_rs_auscultation(e.value)).props(add="autofocus").classes(add="order-4 w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
class AbdominalExaminationForm():
  """A class to display Abdominal examination functionalities"""

  def __init__(self):
    with html.div().classes(add="w-full rounded grid sm:grid-cols-5 gap-2"):
      self.display_dre()
      self.display_palpation()
      self.display_percussion()
      self.display_auscultation()
      self.display_inspection()
    
  @ui.refreshable_method
  def display_inspection(self):
    """A method to display inspection box"""

    self.abd_inspection,set_abd_inspection = ui.state("")

    ui.textarea(label="INSPECTION",value=self.abd_inspection,on_change=lambda e:set_abd_inspection(e.value)).props(add="autofocus").classes(add="order-first w-full outline outline-sky-700 rounded-sm px-3 text-sm")
    
  @ui.refreshable_method
  def display_palpation(self):
    """A method to display palpation box"""
    
    self.abd_palpation,set_abd_palpation = ui.state("")

    ui.textarea(label="PALPATION",value=self.abd_palpation,on_change=lambda e:set_abd_palpation(e.value)).props(add="autofocus").classes(add="order-2 w-full outline outline-sky-700 rounded-sm px-3 text-sm")

  @ui.refreshable_method
  def display_percussion(self):
    """A method to display percussion box"""
    
    self.abd_percussion,set_abd_percussion = ui.state("")

    ui.textarea(label="PERCUSSION",value=self.abd_percussion,on_change=lambda e:set_abd_percussion(e.value)).props(add="autofocus").classes(add="order-3 w-full outline outline-sky-700 rounded-sm px-3 text-sm")

  @ui.refreshable_method
  def display_auscultation(self):
    """A method to display auscultation box"""
    
    self.abd_auscultation,set_abd_auscultation = ui.state("")

    ui.textarea(label="AUSCULTATION",value=self.abd_auscultation,on_change=lambda e:set_abd_auscultation(e.value)).props(add="autofocus").classes(add="order-4 w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_dre(self):
    """A method to display DRE box"""
    
    self.dre,set_dre = ui.state("")

    ui.textarea(label="DIGITAL RECTAL EXAM",value=self.dre,on_change=lambda e:set_dre(e.value)).props(add="autofocus").classes(add="order-5 w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
class GenitourinayExaminationForm():
  """A class to display GUS examination functionalities"""

  def __init__(self):
    with html.div().classes(add="w-full rounded grid sm:grid-cols-2 gap-2"):
      self.display_palpation()
      self.display_inspection()
    
  @ui.refreshable_method
  def display_inspection(self):
    """A method to display inspection box"""

    self.gus_inspection,set_gus_inspection = ui.state("")

    ui.textarea(label="INSPECTION",value=self.gus_inspection,on_change=lambda e:set_gus_inspection(e.value)).props(add="autofocus").classes(add="order-first w-full outline outline-sky-700 rounded-sm px-3 text-sm")
    
  @ui.refreshable_method
  def display_palpation(self):
    """A method to display palpation box"""
    
    self.gus_palpation,set_gus_palpation = ui.state("")

    ui.textarea(label="PALPATION",value=self.gus_palpation,on_change=lambda e:set_gus_palpation(e.value)).props(add="autofocus").classes(add="order-2 w-full outline outline-sky-700 rounded-sm px-3 text-sm")

class CNSExaminationForm():
  """A class for CNS Exam display functionalities"""

  def __init__(self):
    with html.div().classes(add="w-full rounded grid sm:grid-cols-5 gap-2"):
      self.display_reflexes()
      self.display_myotomes()
      self.display_dermatomes()
      self.display_cranials()
      self.display_gait()
    
  @ui.refreshable_method
  def display_cranials(self):
    """A method to display cranial nerves box"""

    self.cranials,set_cranials = ui.state("")

    ui.textarea(label="CRANIAL NERVES",value=self.cranials,on_change=lambda e:set_cranials(e.value)).props(add="autofocus").classes(add="order-first w-full outline outline-sky-700 rounded-sm px-3 text-sm")
    
  @ui.refreshable_method
  def display_dermatomes(self):
    """A method to display dermatomes box"""
    
    self.dermatomes,set_dermatomes = ui.state("")

    ui.textarea(label="DERMATOMES",value=self.dermatomes,on_change=lambda e:set_dermatomes(e.value)).props(add="autofocus").classes(add="order-2 w-full outline outline-sky-700 rounded-sm px-3 text-sm")

  @ui.refreshable_method
  def display_myotomes(self):
    """A method to display myotomes box"""
    
    self.myotomes,set_myotomes = ui.state("")

    ui.textarea(label="MYOTOMES",value=self.myotomes,on_change=lambda e:set_myotomes(e.value)).props(add="autofocus").classes(add="order-3 w-full outline outline-sky-700 rounded-sm px-3 text-sm")

  @ui.refreshable_method
  def display_reflexes(self):
    """A method to display reflexes box"""
    
    self.cns_reflexes,set_cns_reflexes = ui.state("")

    ui.textarea(label="REFLEXES",value=self.cns_reflexes,on_change=lambda e:set_cns_reflexes(e.value)).props(add="autofocus").classes(add="order-4 w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_gait(self):
    """A method to display reflexes box"""
    
    self.cns_gait,set_cns_gait = ui.state("Normal")
    gaits = ["Normal","Limping","Waddling","Sciccoring","Steppage","Propulsive"]
    
    with html.div().classes(add="order-last w-full outline outline-sky-700 rounded-sm"):
      ui.label(text="GAIT").classes(add="w-full bg-sky-700 text-bold text-lg text-sky-50")
      ui.radio(options=gaits,value=self.cns_gait,on_change=lambda e:set_cns_gait(e.value)).props(add="inline").classes(add="")
    

    ui.textarea(label="REFLEXES",value=self.cns_reflexes,on_change=lambda e:set_cns_reflexes(e.value)).props(add="autofocus").classes(add="hidden order-5 w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
class MusculoskeletalExaminationForm():
  """A class for MSS examination functionalities"""

  def __init__(self):
    
    with html.div().classes(add="w-full text-center"):
      self.display_toggle()
      with html.div().classes(add="w-full rounded gap-3") as self.table_panel:
        self.display_upper_limbs_table()
          
  #Overall methods
  @ui.refreshable_method
  def display_toggle(self):
    """A method to display toggle"""

    self.mss_toggle,self.set_mss_toggle = ui.state("upper limbs")

    ui.toggle(options=["upper limbs","lower limbs"],value=self.mss_toggle,on_change=lambda e:self.make_it_happen(e.value)).classes(add="mb-3")

  def make_it_happen(self,value:str):
    """A method to execute toggle commands"""

    self.set_mss_toggle(value)
    self.display_table(limbs=value.split(" ")[0])

  def display_table(self,limbs:str):
    """A method to display tables"""

    if limbs == "upper":
      self.display_upper_limbs_table()
    if limbs == "lower":
      self.display_lower_limbs_table()

  @ui.refreshable_method
  def display_upper_limbs_table(self):
    
    self.table_panel.clear()
    with self.table_panel:
      with html.div().classes(add="order-first outline outline-gray-800 rounded-sm"):
        ui.label(text="UPPER LIMBS").classes(add="w-full rounded-sm bg-gray-900 text-sky-500 text-2xl text-bold text-center")
        with html.table().classes(add="w-full rounded-sm"):
          #LEFT
          with html.tr():
            #Left label
            with html.th().classes(add="w-24 bg-gray-400 px-3 text-lg text-bold text-sky-50"):
              ui.label("Left")
            #Inspection
            with html.th():
              self.display_left_ul_inspection()
            #Palpation
            with html.th():
              self.display_left_ul_palpation()
            #Tone
            with html.th():
              self.display_left_ul_tone()
            #Power
            with html.th():
              self.display_left_ul_power()
            #Sensation
            with html.th():
              self.display_left_ul_sensation()
            #Reflexes
            with html.th():
              self.display_left_ul_reflexes()
            #ROM
            with html.th():
              self.display_left_ul_rom()
          
          #RIGHT
          with html.tr():
            #Right label
            with html.th().classes(add="w-24 bg-gray-400 px-3 text-lg text-bold text-sky-50"):
              ui.label("Right")
            #Inspection
            with html.th():
              self.display_right_ul_inspection()
            #Palpation
            with html.th():
              self.display_right_ul_palpation()
            #Tone
            with html.th():
              self.display_right_ul_tone()
            #Power
            with html.th().classes(add="w-32"):
              self.display_right_ul_power()
            #Sensation
            with html.th():
              self.display_right_ul_sensation()
            #Reflexes
            with html.th():
              self.display_right_ul_reflexes()
            #ROM
            with html.th().classes(add="w-44"):
              self.display_right_ul_rom()
             
  @ui.refreshable_method
  def display_lower_limbs_table(self):

    self.table_panel.clear()
    with self.table_panel:
      with html.div().classes(add="order-first outline outline-gray-800 rounded-sm"):
        ui.label(text="LOWER LIMBS").classes(add="w-full rounded-sm bg-gray-900 text-sky-500 text-2xl text-bold text-center")
        with html.table().classes(add="w-full rounded-sm"):
          #LEFT
          with html.tr():
            #Left label
            with html.th().classes(add="w-24 bg-gray-400 px-3 text-lg text-bold text-sky-50"):
              ui.label("Left")
            #Inspection
            with html.th():
              self.display_left_ll_inspection()
            #Palpation
            with html.th():
              self.display_left_ll_palpation()
            #Tone
            with html.th():
              self.display_left_ll_tone()
            #Power
            with html.th():
              self.display_left_ll_power()
            #Sensation
            with html.th():
              self.display_left_ll_sensation()
            #Reflexes
            with html.th():
              self.display_left_ll_reflexes()
            #ROM
            with html.th():
              self.display_left_ll_rom()
          
          #RIGHT
          with html.tr():
            #Right label
            with html.th().classes(add="w-24 bg-gray-400 px-3 text-lg text-bold text-sky-50"):
              ui.label("Right")
            #Inspection
            with html.th():
              self.display_right_ll_inspection()
            #Palpation
            with html.th():
              self.display_right_ll_palpation()
            #Tone
            with html.th():
              self.display_right_ll_tone()
            #Power
            with html.th().classes(add="w-32"):
              self.display_right_ll_power()
            #Sensation
            with html.th():
              self.display_right_ll_sensation()
            #Reflexes
            with html.th():
              self.display_right_ll_reflexes()
            #ROM
            with html.th().classes(add="w-44"):
              self.display_right_ll_rom()
             
  #UL methods
  @ui.refreshable_method
  def display_left_ul_inspection(self):
    """A method to display inspection  box"""

    self.left_ul_inspection,set_left_ul_inspection = ui.state("")

    ui.input(label="INSPECTION",value=self.left_ul_inspection,on_change=lambda e:set_left_ul_inspection(e.value)).props(add="autofocus").classes(add="order-first w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_right_ul_inspection(self):
    """A method to display inspection  box"""

    self.right_ul_inspection,set_right_ul_inspection = ui.state("")

    ui.input(label="INSPECTION",value=self.right_ul_inspection,on_change=lambda e:set_right_ul_inspection(e.value)).props(add="autofocus").classes(add="order-first w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_left_ul_palpation(self):
    """A method to display palpation box"""
    
    self.left_ul_palpation,set_left_ul_palpation = ui.state("")

    ui.input(label="PALPATION",value=self.left_ul_palpation,on_change=lambda e:set_left_ul_palpation(e.value)).props(add="autofocus").classes(add="order-3 w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_right_ul_palpation(self):
    """A method to display palpation box"""
    
    self.right_ul_palpation,set_right_ul_palpation = ui.state("")

    ui.input(label="PALPATION",value=self.right_ul_palpation,on_change=lambda e:set_right_ul_palpation(e.value)).props(add="autofocus").classes(add="order-4 w-full outline outline-sky-700 rounded-sm px-3 text-sm")

  @ui.refreshable_method
  def display_left_ul_tone(self):
    """A method to display tone box"""
    
    self.left_ul_tone,set_left_ul_tone = ui.state("Normal")

    ui.select(label="TONE",options=["Normal","Hypertonia","Hypotonia","Atonia"],value=self.left_ul_tone,on_change=lambda e:set_left_ul_tone(e.value)).props(add="autofocus").classes(add="order-5 w-full outline outline-sky-700 rounded-sm px-3 text-sm")

  @ui.refreshable_method
  def display_right_ul_tone(self):
    """A method to display tone box"""
    
    self.right_ul_tone,set_right_ul_tone = ui.state("Normal")

    ui.select(label="TONE",options=["Normal","Hypertonia","Hypotonia","Atonia"],value=self.right_ul_tone,on_change=lambda e:set_right_ul_tone(e.value)).props(add="autofocus").classes(add="order-6 w-full outline outline-sky-700 rounded-sm px-3 text-sm")

  @ui.refreshable_method
  def display_left_ul_power(self):
    """A method to display power box"""
    
    self.left_ul_power,set_left_ul_power = ui.state(5)

    ui.select(label="POWER",options=[i for i in range(6)],value=self.left_ul_power,on_change=lambda e:set_left_ul_power(e.value)).props(add="autofocus").classes(add="order-7 w-full outline outline-sky-700 rounded-sm px-3 text-sm")

  @ui.refreshable_method
  def display_right_ul_power(self):
    """A method to display power box"""
    
    self.right_ul_power,set_right_ul_power = ui.state(5)

    ui.select(label="POWER",options=[i for i in range(6)],value=self.right_ul_power,on_change=lambda e:set_right_ul_power(e.value)).props(add="autofocus").classes(add="order-8 w-full outline outline-sky-700 rounded-sm px-3 text-sm")

  @ui.refreshable_method
  def display_left_ul_sensation(self):
    """A method to display sensation box"""
    
    self.left_ul_sensation,set_left_ul_sensation = ui.state("Normal")

    ui.select(label="SENSATION",options=["Hyperaesthesia","Paraesthesia","Normal","Hypoaesthesia","Anaesthesia"],value=self.left_ul_sensation,on_change=lambda e:set_left_ul_sensation(e.value)).props(add="autofocus").classes(add="order-9 w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_right_ul_sensation(self):
    """A method to display sensation box"""
    
    self.right_ul_sensation,set_right_ul_sensation = ui.state("Normal")

    ui.select(label="SENSATION",options=["Hyperaesthesia","Paraesthesia","Normal","Hypoaesthesia","Anaesthesia"],value=self.right_ul_sensation,on_change=lambda e:set_right_ul_sensation(e.value)).props(add="autofocus").classes(add="order-10 w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_left_ul_reflexes(self):
    """A method to display reflexes box"""
    
    self.left_ul_reflexes,set_left_ul_reflexes = ui.state("Normal")

    ui.select(label="REFLEXES",options=["Hyperreflexia","Normal","Hyporeflexia","Areflexia"],value=self.left_ul_reflexes,on_change=lambda e:set_left_ul_reflexes(e.value)).props(add="autofocus").classes(add="order-11 w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_right_ul_reflexes(self):
    """A method to display reflexes box"""
    
    self.right_ul_reflexes,set_right_ul_reflexes = ui.state("Normal")

    ui.select(label="REFLEXES",options=["Hyperreflexia","Normal","Hyporeflexia","Areflexia"],value=self.right_ul_reflexes,on_change=lambda e:set_right_ul_reflexes(e.value)).props(add="autofocus").classes(add="order-12 w-full outline outline-sky-700 rounded-sm px-3 text-sm")

  @ui.refreshable_method
  def display_left_ul_rom(self):
    """A method to display ROM box"""
    
    self.left_ul_rom,set_left_ul_rom = ui.state("")

    ui.input(label="RANGE OF MOTION",value=self.left_ul_rom,on_change=lambda e:set_left_ul_rom(e.value)).props(add="autofocus").classes(add="order-13 w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_right_ul_rom(self):
    """A method to display ROM box"""
    
    self.right_ul_rom,set_right_ul_rom = ui.state("")

    ui.input(label="RANGE OF MOTION",value=self.right_ul_rom,on_change=lambda e:set_right_ul_rom(e.value)).props(add="autofocus").classes(add="order-last w-full outline outline-sky-700 rounded-sm px-3 text-sm")

  #LL methods
  @ui.refreshable_method
  def display_left_ll_inspection(self):
    """A method to display inspection  box"""

    self.left_ll_inspection,set_left_ll_inspection = ui.state("")

    ui.input(label="INSPECTION",value=self.left_ll_inspection,on_change=lambda e:set_left_ll_inspection(e.value)).props(add="autofocus").classes(add="order-15 w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_right_ll_inspection(self):
    """A method to display inspection  box"""

    self.right_ll_inspection,set_right_ll_inspection = ui.state("")

    ui.input(label="INSPECTION",value=self.right_ll_inspection,on_change=lambda e:set_right_ll_inspection(e.value)).props(add="autofocus").classes(add="order-16 w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_left_ll_palpation(self):
    """A method to display palpation box"""
    
    self.left_ll_palpation,set_left_ll_palpation = ui.state("")

    ui.input(label="PALPATION",value=self.left_ll_palpation,on_change=lambda e:set_left_ll_palpation(e.value)).props(add="autofocus").classes(add="order-3 w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_right_ll_palpation(self):
    """A method to display palpation box"""
    
    self.right_ll_palpation,set_right_ll_palpation = ui.state("")

    ui.input(label="PALPATION",value=self.right_ll_palpation,on_change=lambda e:set_right_ll_palpation(e.value)).props(add="autofocus").classes(add="order-4 w-full outline outline-sky-700 rounded-sm px-3 text-sm")

  @ui.refreshable_method
  def display_left_ll_tone(self):
    """A method to display tone box"""
    
    self.left_ll_tone,set_left_ll_tone = ui.state("Normal")

    ui.select(label="TONE",options=["Normal","Hypertonia","Hypotonia","Atonia"],value=self.left_ll_tone,on_change=lambda e:set_left_ll_tone(e.value)).props(add="autofocus").classes(add="order-5 w-full outline outline-sky-700 rounded-sm px-3 text-sm")

  @ui.refreshable_method
  def display_right_ll_tone(self):
    """A method to display tone box"""
    
    self.right_ll_tone,set_right_ll_tone = ui.state("Normal")

    ui.select(label="TONE",options=["Normal","Hypertonia","Hypotonia","Atonia"],value=self.right_ll_tone,on_change=lambda e:set_right_ll_tone(e.value)).props(add="autofocus").classes(add="order-6 w-full outline outline-sky-700 rounded-sm px-3 text-sm")

  @ui.refreshable_method
  def display_left_ll_power(self):
    """A method to display power box"""
    
    self.left_ll_power,set_left_ll_power = ui.state(5)

    ui.select(label="POWER",options=[i for i in range(6)],value=self.left_ll_power,on_change=lambda e:set_left_ll_power(e.value)).props(add="autofocus").classes(add="order-7 w-full outline outline-sky-700 rounded-sm px-3 text-sm")

  @ui.refreshable_method
  def display_right_ll_power(self):
    """A method to display power box"""
    
    self.right_ll_power,set_right_ll_power = ui.state(5)

    ui.select(label="POWER",options=[i for i in range(6)],value=self.right_ll_power,on_change=lambda e:set_right_ll_power(e.value)).props(add="autofocus").classes(add="order-8 w-full outline outline-sky-700 rounded-sm px-3 text-sm")

  @ui.refreshable_method
  def display_left_ll_sensation(self):
    """A method to display sensation box"""
    
    self.left_ll_sensation,set_left_ll_sensation = ui.state("Normal")

    ui.select(label="SENSATION",options=["Hyperaesthesia","Paraesthesia","Normal","Hypoaesthesia","Anaesthesia"],value=self.left_ll_sensation,on_change=lambda e:set_left_ll_sensation(e.value)).props(add="autofocus").classes(add="order-9 w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_right_ll_sensation(self):
    """A method to display sensation box"""
    
    self.right_ll_sensation,set_right_ll_sensation = ui.state("Normal")

    ui.select(label="SENSATION",options=["Hyperaesthesia","Paraesthesia","Normal","Hypoaesthesia","Anaesthesia"],value=self.right_ll_sensation,on_change=lambda e:set_right_ll_sensation(e.value)).props(add="autofocus").classes(add="order-10 w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_left_ll_reflexes(self):
    """A method to display reflexes box"""
    
    self.left_ll_reflexes,set_left_ll_reflexes = ui.state("Normal")

    ui.select(label="REFLEXES",options=["Hyperreflexia","Normal","Hyporeflexia","Areflexia"],value=self.left_ll_reflexes,on_change=lambda e:set_left_ll_reflexes(e.value)).props(add="autofocus").classes(add="order-11 w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_right_ll_reflexes(self):
    """A method to display reflexes box"""
    
    self.right_ll_reflexes,set_right_ll_reflexes = ui.state("Normal")

    ui.select(label="REFLEXES",options=["Hyperreflexia","Normal","Hyporeflexia","Areflexia"],value=self.right_ll_reflexes,on_change=lambda e:set_right_ll_reflexes(e.value)).props(add="autofocus").classes(add="order-12 w-full outline outline-sky-700 rounded-sm px-3 text-sm")

  @ui.refreshable_method
  def display_left_ll_rom(self):
    """A method to display ROM box"""
    
    self.left_ll_rom,set_left_ll_rom = ui.state("")

    ui.input(label="RANGE OF MOTION",value=self.left_ll_rom,on_change=lambda e:set_left_ll_rom(e.value)).props(add="autofocus").classes(add="order-13 w-full outline outline-sky-700 rounded-sm px-3 text-sm")
  
  @ui.refreshable_method
  def display_right_ll_rom(self):
    """A method to display ROM box"""
    
    self.right_ll_rom,set_right_ll_rom = ui.state("")

    ui.input(label="RANGE OF MOTION",value=self.right_ll_rom,on_change=lambda e:set_right_ll_rom(e.value)).props(add="autofocus").classes(add="order-14 w-full outline outline-sky-700 rounded-sm px-3 text-sm")

