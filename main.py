"""A main module for loading the NiceGUI app"""

#GENERAL IMPORTS
import threading
from nicegui import app,ui

#PROJECT IMPORTS
from backend.background_tasks import expire_sessions
from backend.admin.db import populate_db
from uix.pages import router as web_router


#ROUTING
for router in [web_router]:
  app.include_router(router)

#APP INITIALIZATION
if __name__ in {"__main__", "__mp_main__"}:
  #Populate database
  populate_db()

  #MAIN THREAD
  ui.run(
    favicon="uix/assets/icons/favicons/nexasoft5.ico",
    storage_secret='xxx',
    host='0.0.0.0',
    viewport = "width=device-width,initial-scale=1.0,maximum-scale=1.0",
    reload = True,
    reconnect_timeout=10.0,
    dark = False
  )
  
  #BG THREAD
  visits_thread = threading.Thread(target=expire_sessions)

  visits_thread.start()
