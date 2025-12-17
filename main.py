"""A main module for loading the NiceGUI app"""

#GENERAL IMPORTS
import threading
from nicegui import app,ui

#PROJECT IMPORTS
from services.background_tasks import expire_sessions
from services.provider.ui import populate_db
from uix.web.pages import router as web_router


#ROUTING
for router in [web_router]:
  app.include_router(router)

#APP INITIALIZATION
if __name__ in {"__main__", "__mp_main__"}:
  #Populate database
  populate_db()

  #MAIN THREAD
  ui.run(
    favicon="uix/web/assets/icons/favicons/nexasoft5.ico",
    storage_secret='xxx',
    host='0.0.0.0',
    viewport = "width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no"
  )
  
  #BG THREAD
  visits_thread = threading.Thread(target=expire_sessions)

  visits_thread.start()
