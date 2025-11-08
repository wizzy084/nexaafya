"""A module in auth subpackage to process API authentication and authorization processes"""

#GENERAL IMPORTS
import json,os
from dotenv import load_dotenv

#FASTAPI IMPORTS
from fastapi import Request

#LOADING ENVIRONMENT VARIABLES
load_dotenv()

#AUTHENTICATION TOKENS
ACTIVE_API_TOKENS:list = json.loads(os.getenv("ACTIVE_API_TOKENS"))
EXPIRED_API_TOKENS:list = json.loads(os.getenv("EXPIRED_API_TOKENS"))





#FUNCTIONS
def request_is_valid(request:Request=None):
  """Takes in a Request object and return boolean value base on whether there is Bearer token in request object and whether"""
  
  if "authorization" in request.headers and request.headers["authorization"].startswith("Bearer"):
    request_token = request.headers["authorization"].split(" ")[1]
    if request_token in ACTIVE_API_TOKENS:
      return {"status":True}
    elif request_token in EXPIRED_API_TOKENS:
      return {"status":False,"detail":"Expired"}
    else:
      return {"status":False,"detail":"Invalid"}
  else:
    return {"status":False,"detail":"No Token"}
