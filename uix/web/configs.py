
#NICEGUI IMPORTS
from nicegui import app




  
#HEAD SECTION TAGS
META_TAGS = [
  "<meta name='theme-color' content='#07004d' />"
]

HEAD_LINKS = [
  "<link rel='stylesheet' type='text/css' href='/icons/css/main.css' >",
  "<link rel='stylesheet' type='text/css' href='/styles/main.css' >",
  "<link rel='stylesheet' type='text/css' href='/styles/animate.min.css' >",
  "<link rel='manifest' href='/scripts/manifest.json' >",
  "<script type='text/javascript' src='/scripts/htmx.js'></script>"
]

BODY_LINKS = [
  "<script type='text/javascript' src='/scripts/main.js'></script>",
]


#STATIC FILES
app.add_static_files(url_path="/icons",local_directory="uix/web/assets/icons")
app.add_static_files(url_path="/styles",local_directory="uix/web/assets/styles")
app.add_static_files(url_path="/scripts",local_directory="uix/web/assets/scripts")
app.add_media_files(url_path="/images",local_directory="uix/web/assets/images")

#MEDIA FILES
app.add_media_files(url_path="/imagings",local_directory="services/provider/media/imagings")

