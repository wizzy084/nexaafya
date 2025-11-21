"""A module to degign widgets for 'imaging' functionality"""

#GENERAL IMPORTS
import json
from pathlib import Path

#NiceGUI IMPORTS
from nicegui import html,ui

#ADMIN APP IMPORTS
from services.provider.admin.processor import get_staff as staff,get_facility_data
from services.provider.clients.db import update_imaging
from services.provider.clients.processor import get_active_imagings,get_imagings

#UIX IMPORTS
from ..tools._snippets import *


#WIDGETS
class StudiesManagementDisplay():
  """A class to display UI for managing studies"""

  def __init__(self,user):
    #DATA
    self.user = user
    self.initial_data()
    
    #STATE
    self.state()
    #UI
    with html.div().classes(add="w-full h-full p-2") as master_container:
      with html.div().classes(add="w-full h-[96%] flex flex-col rounded ring-1 ring-blue-400 shadow-md shadow-sky-500"):
        if self.today_visits:
          with html.div().classes(add="w-full rounded-t p-2 bg-gray-900 flex flex-row"):
            ui.label("TODAY VISITS").classes(add="").classes(add="bg-inherit grow text-3xl text-yellow-500 text-bold")
            with html.div().classes(add="bg-inherit") as self.stats_panel:
              self.ImagingStats()
          #Displays
          with html.div().classes(add="w-full grow bg-white") as self.display_panel:
            self.ImagingsDisplay()
        else:
          with html.div().classes(add="self-center flex flex-col gap-2 p-3 rounded light-blur ring-1 ring-blue-400 shadow-md shadow-sky-500 text-bold"):
            ui.label("No Imagings for you").classes(add="text-5xl text-rose-500")
            ui.label("Just Relax and have fun!").classes(add="italic text-center text-2xl text-pink-300")

  @ui.refreshable_method
  def state(self):
    self.attachments,self.update_attachments = ui.state([])
    self.findings,self.update_findings = ui.state("")
  
  #FUNCTIONALITIES
  def initial_data(self):
    self.today_visits = get_active_imagings()
    self.pending_visits = [visit for visit in self.today_visits if self.imaging_status(visit["imagings"]) == "pending" or self.imaging_status(visit["imagings"]) == "partial"]
    self.done_visits = [visit for visit in self.today_visits if self.imaging_status(visit["imagings"]) == "done"]
    self.visits = self.pending_visits + self.done_visits
    
    self.imagings = [imaging for imaging in  get_imagings() if imaging["visit_id"] in [visit["visit_id"] for visit in self.today_visits]]
    self.processed_imagings = [imaging for imaging in self.imagings if imaging["processed"]]
    self.pending_imagings = [imaging for imaging in self.imagings if (imaging["payment"]["paid"] or imaging["payment"]["billed"]) and not (imaging["processed"] or imaging["cancelled"])]
    self.unprocessed_imagings = [imaging for imaging in self.imagings if not (imaging["payment"]["paid"] or imaging["payment"]["billed"] or imaging["cancelled"])]
    self.cancelled_imagings = [imaging for imaging in self.imagings if imaging["cancelled"]]

  def imaging_status(self,imagings:list[dict]):
    """Returns value depending on whether the imaging has been done"""

    statuses = set()

    for imaging in imagings:
      if (imaging["payment"]["paid"] or imaging["payment"]["billed"]) and not imaging["processed"]:
        statuses.add("pending")
      if (imaging["payment"]["paid"] or imaging["payment"]["billed"]) and imaging["processed"]:
        statuses.add("done")
      if not (imaging["payment"]["paid"] or imaging["payment"]["billed"]) and not imaging["processed"]:
        statuses.add("not done")
    
    if len(statuses) == 1:
      for status in statuses:
        return status
    else:
      return "partial"
  
  def _imagings(self,imagings:list[dict]):
    """Returns a list of procedures"""

    def format_study(study):
      study = study.lower()
      if "opg" in study:
        _study_root,_study_stem = study.split("(")[0].title(),study.split("(")[1]
        _bracketed_study = _study_stem.split(")")[0].upper()
        return f"{_study_root.capitalize()} ({_bracketed_study})"
      else:
        return study.title()
    
    if imagings:
      imagings_string = ""
      for imaging in imagings:
        _substring = f"<span class='px-1'><i class='fas {'fa-check text-green-500' if imaging['processed'] else 'fa-ban text-gray-400' if imaging['cancelled'] else 'fa-spinner fa-spin text-yellow-500' if ((imaging['payment']['billed'] or imaging['payment']['paid']) and not imaging['processed']) else 'fa-xmark text-red-500'} fa-lg'></i><i class='ml-1 '>{format_study(imaging['study'])}</i></span><br>"
        imagings_string += _substring
      return imagings_string
    else:
      return "---"

  def upload_attachments(self,imaging_data:dict,attachments:list,types:list[str]):
    """Adds file to a directory   and references to the database"""

    attachments = list(zip(types,attachments))

    #File upload
    target_dir:Path = imaging_data["target_dir"]
    try:
      target_dir.mkdir(parents=True)
    except FileExistsError:
      return
    finally:
      if imaging_data["upload_mode"] == "replace":
        for file in list(target_dir.iterdir()):
          file.unlink()
      current_attachments:list[str] = []
      for attachment in attachments:
        file_type,file = attachment
        file_destination_stem = f"{imaging_data['imaging_id']}{imaging_data['saved_files_count'] + attachments.index(attachment) + 1}.{file_type.split('/')[1]}"
        file_destination = target_dir.joinpath(f"{file_destination_stem}")
        with open(file=file_destination,mode="wb") as img_file:
          img_file.write(file.read())
        
        current_attachments.append(file_destination_stem)
      
      self.update_attachments(current_attachments)
      
      self.ImagingsPanel(imaging_data["imaging_id"].lower().split("img")[0])
      self.upload_dialog.close()

      ui.notify(message="Attachments successfully saved",type="positive",position="top")

  def save_results(self,imaging_id:str,findings:str|None=None):
    """Saves the findings in the database"""

    self.update_findings(findings)

    results_data = {
      "imaging_id":imaging_id,
      "results":self.findings,
      "results_img":json.dumps(self.attachments),
      "radiographer":self.user.username if "radiographer" in self.user.roles else None,
      "radiologist":self.user.username if "radiologist" in self.user.roles else None
    }

    status = update_imaging(results_data)
    ui.notify(message=status["message"],type=status["type"],position="top")

    self.initial_data()
    self.ImagingStats()
    self.ImagingsPanel(visit_id=imaging_id.lower().split("img")[0])
     
  #UI
  def ImagingStats(self):
    """"""
    self.stats_panel.clear()
    with self.stats_panel:
      with html.span().classes(add="flex flex-row"):
        #Visits
        with ui.label("VISITS").classes(add="rounded-full p-2 text-sky-500"):
          ui.label(str(len(self.today_visits))).classes(add="ml-1 inline text-bold text-white")
        #Imagings
        with ui.label("IMAGINGS").classes(add="rounded-full p-2 text-sky-500"):
          ui.label(str(len(self.imagings))).classes(add="ml-1 inline text-bold text-white")
        #Done
        with ui.chip(icon="fa-regular fa-circle-check",text_color="green",color="").classes(add=f"{'' if self.processed_imagings else 'hidden'} p-2 bg-inherit").tooltip("Processed Imagings"):
          ui.label(str(len(self.processed_imagings))).classes(add="inline text-bold text-white")
        #Pending
        with ui.chip(icon="fas fa-spinner fa-spin",text_color="yellow",color="").classes(add=f"{'' if self.pending_imagings else 'hidden'} p-2 bg-inherit").tooltip("Awaiting Processing"):
          ui.label(str(len(self.pending_imagings))).classes(add="inline text-bold text-white")
        #Not Paid/Billed
        with ui.chip(icon="fa-regular fa-circle-xmark",text_color="red",color="").classes(add=f"{'' if self.unprocessed_imagings else 'hidden'} p-2 bg-inherit"):
          ui.label(str(len(self.unprocessed_imagings))).classes(add="inline text-bold text-white")
        #Cancelled
        with ui.chip(icon="fas fa-ban",text_color="grey",color="").classes(add=f"{'' if self.cancelled_imagings else 'hidden'} p-2 bg-inherit"):
          ui.label(str(len(self.cancelled_imagings))).classes(add="inline text-bold text-white")

  def ImagingsDisplay(self):
    """Main display"""

    self.display_panel.clear()
    with self.display_panel:
      #AGGRID
        ui.aggrid(
          {
            "columnDefs":[
              {"headerName":"S/N","field":"sno","width":50},
              {"headerName":"CLIENT ID","field":"client_id","filter":"agTextColumnFilter","width":100},
              {"headerName":"NAME","field":"name","filter":"agTextColumnFilter"},
              {"headerName":"AGE","field":"age","width":150},
              {"headerName":"GENDER","field":"gender","width":100},
              {"headerName":"REQUEST MODE","field":"request_mode","width":150},
              {"headerName":"PAYMENT","field":"payment_mode","width":100},
              {"headerName":"STUDIES","field":"studies","wrapText":True,"autoHeight":True}
            ],
            "rowData":[
              {
                "sno":self.today_visits.index(visit) + 1,
                "client_id":visit["client_id"],
                "name":visit["client_name"].title(),
                "age":visit["client_age"],
                "gender":visit["client_gender"].capitalize(),
                "request_mode":visit["request_mode"].capitalize(),
                "payment_mode":" ".join({mode.upper() for mode in [imaging_item["payment"]["payment_mode"] for imaging_item in visit["imagings"]]}),
                "studies":self._imagings(visit["imagings"])
              }
            for visit in self.visits
            ]
          },
          html_columns=[7],
          theme="quartz"
        ).classes(add="w-full h-full animate__animated animate__fadeIn animate__slow").on("cellClicked",lambda e:self.ImagingsDialog([imaging_visit for imaging_visit in self.visits if imaging_visit["client_id"] == e.args["data"]["client_id"]][0]))

  def ImagingsDialog(self,visit:dict):
    
    #DATA
    self.details = {"name":visit["client_name"],"age":visit["client_age"],"gender":visit["client_gender"],"address":visit["client_address"]}
    #FXS
    def close_dialog():
      self.ImagingsDisplay()
    #UI
    with ui.dialog() as self.imagings_dialog,html.div().style(add="min-width:85%;max-height:90%;").classes(add="bg-white ring-1 ring-blue-400 shadow-md shadow-sky-500"):
      #Dialog Header
      with html.div().classes(add="w-full grid grid-cols-12 bg-gray-900"):
        with html.div().classes(add="col-span-11"):
          ClientCard(details=self.details)
        ui.button(icon="fas fa-circle-xmark",color="",on_click=close_dialog).classes(add="col-span-1 bg-inherit text-red-600 text-bold text-base")
      #Imagings
      with html.div().classes(add="w-full h-full") as self.imagings_dialog_panel:
        self.ImagingsPanel(visit["visit_id"])

    self.imagings_dialog.open()

  def ImagesUploadDialog(self,imaging_data:dict):
    """A display to show options fo rfile upload"""
    
    
    if imaging_data["saved_files_count"] > 0:
      imaging_data["upload_mode"] = "replace"
    else:
      imaging_data["upload_mode"] = "save"

    with ui.dialog() as self.upload_dialog,html.div().style(add="min-width:70%;max-height:70%;").classes(add="bg-white"):
      ui.label(text=imaging_data["study"].upper()).classes(add="w-full bg-gray-900 text-2xl text-bold text-center text-yellow-500")
      with html.div().classes(add="w-full p-1 flex flex-row justify-center"):
        ui.upload(
          label="UPLOAD ATTACHMENTS",
          multiple=True,
          auto_upload=True,
          on_multi_upload=lambda e:self.upload_attachments(imaging_data=imaging_data,attachments=e.contents,types=e.types)
        ).classes(add="w-full h-full")
    
    self.upload_dialog.open()
  
  def ImagingsPanel(self,visit_id:str):
    """"""
    #DATA
    imagings = [visit["imagings"] for visit in self.today_visits if visit["visit_id"] == visit_id][0]
    for imaging in imagings:
      if "x ray" in imaging["study"].lower() or "opg" in imaging["study"].lower():
        imaging["modality"] = "xray"
      if "uss" in imaging["study"].lower():
        imaging["modality"] = "uss"
  
    #UI
    self.imagings_dialog_panel.clear()
    with self.imagings_dialog_panel:
      with html.div().classes(add="w-full bg-sky-50 p-3 flex flex-col gap-5 animate__animated animate__fadeIn"):
        for imaging in imagings:
          with html.div().classes(add="w-full") as self.image_panel:
            self.ImagePanel(imaging,imagings)
          
  def ImagePanel(self,imaging:dict,imagings:list):
    #DATA
    imaging_path = Path(f"media/imagings/{imaging['visit_id']}/{'uss' if 'uss' in imaging['study'] else 'xrays'}/{imaging['study'].split(' ')[0]}")
    if imaging_path.exists():
      paths =list(imaging_path.iterdir())
    else:
      paths = None
    
    attendee = f"{staff(imaging['attendee_id'])['first_name']} {staff(imaging['attendee_id'])['last_name']}"
    target_dir:Path = Path(f"media/imagings/{imaging['imaging_id'].lower().split('img')[0]}/{'xrays' if imaging['modality'].startswith('xray') else 'uss'}/{imaging['study'].split()[0]}")
    imaging_data = {
      "visit_id":imaging["visit_id"],
      "imaging_id":imaging["imaging_id"],
      "study":imaging["study"],
      "modality":imaging["modality"],
      "target_dir":target_dir, 
    }

    if imaging_data["target_dir"].exists():
      imaging_data["target_dir"] = target_dir
      imaging_data["saved_files_count"] = len([file for file in imaging_data["target_dir"].iterdir()])
    else:
      imaging_data["saved_files_count"] = 0
    
    #FXS
    def update_attachments_panel(paths,path):
      if len(paths) > 1:
        path.unlink()
      else:
        path.unlink()
        #Attachments
        attachments_panel.clear()
        with attachments_panel.classes(add="justify-center"):
          ui.label("No attachments").classes(add="text-gray-500 text-2xl italic")
        #Buttons
        buttons_panel.clear()
        with buttons_panel:
          ui.button(text="save images",icon="file-image fa-lg",color="gray-900",on_click=lambda e:self.ImagesUploadDialog(imaging_data)).props(add="" if (imaging["payment"]["paid"] or imaging["payment"]["billed"]) else "disabled").classes(add="rounded-full ring-1 ring-sky-400 ring-offset-2 shadow-md shadow-sky-400 text-lg text-bold text-sky-300")
          ui.button(text="submit results",icon="fas fa-floppy-disk",color="gray-900",on_click=lambda e:self.save_results(imaging_id=imaging["imaging_id"],findings=findings_box.value)).props(add="" if (imaging["payment"]["paid"] or imaging["payment"]["billed"]) else "disabled").classes(add="rounded-full ring-1 ring-sky-400 ring-offset-2 shadow-md shadow-sky-400 text-lg text-bold text-sky-300")

    #UI
    with self.image_panel:
      with ui.expansion(value=True if (imagings.index(imaging) == 0 and not imaging["processed"]) else False,group="imagings_group").props(add="duration=500 expand-icon='fas fa-angles-down fa-lg' expand-icon-class='text-green-600 text-bold' header-class='q-pa-none bg-sky-100'").classes(add="rounded bg-sky-50 ring-1 ring-blue-300 shadow-md shadow-sky-600") as expansion:
        #Header
        with expansion.add_slot("header"):
          with html.div().classes(add="w-full grid grid-cols-5"):
            #Study
            ui.chip(text=imaging["study"].split("(")[0].capitalize() if "opg" in imaging["study"].lower() else  imaging["study"].title(),text_color="sky-900",color="").classes(add="rounded-sm m-0 px-2 bg-inherit text-xl text-bold")
            #Timeframe
            ui.chip(text=f"{format_age(imaging['request_time'])} ago",icon="fa-regular fa-clock fa-lg",text_color="sky-900",color="").classes(add="rounded-sm px-2 bg-inherit text-base text-bold")
            #Odered by
            ui.chip(text=attendee.title(),icon="fa-regular fa-doctor-user fa-lg",text_color="sky-900",color="").classes(add="rounded-sm px-2 bg-inherit text-base text-bold")
            #Payment status
            ui.chip(text="Paid" if imaging["payment"]["paid"] else "Billed" if imaging["payment"]["billed"] else "Not Paid",icon=f"{'fa-regular fa-circle-check' if imaging['payment']['paid'] else 'fa-solid fa-file-invoice' if imaging['payment']['billed'] else 'fa-regular fa-circle-xmark'} fa-lg",text_color="teal" if imaging["payment"]["paid"] else "purple" if imaging["payment"]["billed"] else "red",color="").classes(add="rounded-sm px-2 bg-inherit text-base text-bold")
            #Imaging status
            ui.chip(
              text="Done" if ((imaging["payment"]["paid"] or imaging["payment"]["billed"]) and imaging["processed"]) else "Pending" if ((imaging["payment"]["billed"] or imaging["payment"]["paid"]) and not imaging["processed"]) else "Not done",
              icon=f"{'fa-regular fa-circle-check' if ((imaging['payment']['paid'] or imaging['payment']['billed']) and imaging['processed']) else 'fa-solid fa-spinner fa-spin' if ((imaging['payment']['billed'] or imaging['payment']['paid']) and not imaging['processed']) else 'fa-regular fa-circle-xmark fa-flip'} fa-lg",
              text_color="teal" if ((imaging["payment"]["paid"] or imaging["payment"]["billed"]) and imaging["processed"]) else "orange" if ((imaging["payment"]["billed"] or imaging["payment"]["paid"]) and not imaging["processed"]) else "red",
              color=""
              ).classes(add="rounded-sm px-2 bg-inherit text-base text-bold")
        
        #Findings
        with html.form().classes(add="w-full grid grid-cols-3"):
          #Additional info
          if imaging["notes"]:
            with html.fieldset().classes(add="col-span-1 ring-1 ring-blue-200 shadow-md shadow-sky-300 p-1 rounded text-lg text-bold italic"):
              html.legend("ADDITIONAL INSTRUCTIONS").classes(add="bg-sky-50 px-2 text-sky-700")
              html.textarea(imaging["notes"].capitalize()).props(add="readonly").classes(add="w-full h-full px-2 rounded bg-inherit font-normal")
          else:
            ui.label("No additional instructions!").classes(add="col-span-1 my-7 text-center text-lg text-bold italic text-gray-500")
          
          #Findings
          findings_box = ui.textarea(label="FINDINGS",value=imaging["results"],placeholder="Write down important findings").props(add="" if (imaging["payment"]["paid"] or imaging["payment"]["billed"]) else "readonly").classes(add="col-span-2 justify-self-end w-[95%] bg-white rounded ring-1 ring-blue-300 ring-offset-2 shadow-md shadow-sky-600 px-2 text-lg")
        
        #Attachments
        with html.div().classes(add="w-full my-1 p-1 rounded grid grid-cols-3 gap-5 ring-1 ring-blue-100 shadow-sm shadow-sky-300") as attachments_panel:
          if paths:
            for path in paths:
              ui.chip(text=f"IMAGE {paths.index(path)+1}",color="",removable=True,on_click=lambda e:self.ImageViewDialog(path=[path for path in paths if path.stem == e.sender._props["id"]][0]),on_value_change=lambda e:update_attachments_panel(paths=paths,path=[path for path in paths if path.stem == e.sender._props["id"]][0])).props(add=f"icon-remove='fa-regular fa-circle-xmark' id='{path.stem}'").classes(add=f"w-full ring-1 ring-blue-200 bg-inherit rounded uppercase shadow-md shadow-blue-400 text-bold text-sky-700 text-xl")
          else:
            with attachments_panel.classes(add="flex flex-row justify-center",remove="grid grid-cols-3"):
              ui.label("No attachments").classes(add="text-gray-500 text-2xl italic")

        #Buttons
        with html.div().classes(add="w-full flex flex-row justify-center gap-x-5") as buttons_panel:
          ui.button(text=f"{'save' if imaging_data['saved_files_count'] == 0 else 'replace'} images",icon=f"fas fa-{'repeat fa-rotate-90' if imaging_data['saved_files_count'] > 0 else 'file-image'} fa-lg",color="gray-900",on_click=lambda e:self.ImagesUploadDialog(imaging_data)).props(add="" if (imaging["payment"]["paid"] or imaging["payment"]["billed"]) else "disabled").classes(add="rounded-full ring-1 ring-sky-400 ring-offset-2 shadow-md shadow-sky-400 text-lg text-bold text-sky-300")
          ui.button(text="submit results",icon="fas fa-floppy-disk",color="gray-900",on_click=lambda e:self.save_results(imaging_id=imaging["imaging_id"],findings=findings_box.value)).props(add="" if (imaging["payment"]["paid"] or imaging["payment"]["billed"]) else "disabled").classes(add="rounded-full ring-1 ring-sky-400 ring-offset-2 shadow-md shadow-sky-400 text-lg text-bold text-sky-300")
 
  def ImageViewDialog(self,path:Path):
    """A display to show images"""
    #UI
    with ui.dialog() as self.image_view_dialog,html.div().style(add="min-width:70%;min-height:70%;").classes(add="bg-white p-1"):
      ui.image(path).classes(add="w-full h-full rounded")
    
    self.image_view_dialog.open()

class ImagingReportdisplay():
  """A class for displaying summary of imagings"""

  def __init__(self,user):
    #DATA
    self.user = user
    