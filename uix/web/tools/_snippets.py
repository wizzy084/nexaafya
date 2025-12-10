"""A module for miscallenous functions for UIX app"""
#GENERAL IMPORTS
from collections import namedtuple
from datetime import date,datetime
from math import ceil




###Objects
Complaints = namedtuple("Complaints","count first second third")

  

###functions
def calculate_age(birthdate:str,days:bool=False,months:bool=False):
  """Calcuates age of client from 'birthdate' in ISO format"""

  _row_age = datetime.now() - datetime.fromisoformat(birthdate)
  row_age = _row_age.days*86400 + _row_age.seconds + _row_age.microseconds/1000000
  calc_years = row_age//(366*86400)
  calc_months = (row_age%(366*86400))//(30.5*86400)
  calc_days = ((row_age%(366*86400))%(30.5*86400))/86400
  
  if days:
    return f"{ceil(calc_years)} years {ceil(calc_months)} months {ceil(calc_days)} days"
  elif months:
    return f"{ceil(calc_years)} years {ceil(calc_months)} months"
  else:
    return f"{ceil(calc_years)} years"

def blink_badge(button):
  """A funciton sets 'fa-fade' and 'display' classes to the 'badge' if its text value is > 0"""

  badge_value = int(button.descendants().__next__().text)
  
  if badge_value > 0:
    return "fa-faded fa-beat"
  else:
    return "hidden"


def db_display_change(changed_value:str,target,target_value_options:list[str]):
  """A function to change 'target_value' based on the value of 'changed_value'"""

  if changed_value.startswith("remote"):
    target.set_text(target_value_options[1])

  elif changed_value.startswith("local"):
    target.set_text(target_value_options[0])

  else:
    return None


def get_duration(row_date:datetime) -> dict[str,int]:
  """Returns duration of 'date' from current time (now)"""
  
  duration = {"years":0,"months":0,"days":0,"hours":0,"minutes":0,"seconds":0,"milliseconds":0,"microseconds":0}

  date,now = row_date,datetime.now()
  delta_time = now - date
  

  years = delta_time.days//365
  months = delta_time.days%365//30
  days = delta_time.days%365%30
  hours = delta_time.seconds//3600
  minutes = delta_time.seconds%3600//60
  seconds = delta_time.seconds%3600%60
  milliseconds = delta_time.microseconds//1000
  microseconds = delta_time.microseconds%1000

  if years > 0:
    duration["years"] = years
  if months > 0:
    duration["months"] = months
  if days > 0:
    duration["days"] = days
  if hours > 0:
    duration["hours"] = hours
  if minutes > 0:
    duration["minutes"] = minutes
  if seconds > 0:
    duration["seconds"] = seconds
  if milliseconds > 0:
    duration["milliseconds"] = milliseconds
  if microseconds > 0:
    duration["microseconds"] = microseconds

  return duration

def format_age(birthdate:str,short:bool=False) -> str:
  """
  Returns a string of formatted age based on the age returned from 'birthdate'.
  if 'short' is True, it returns a shorter version of the age.
  """

  years,months,days,hours,minutes,seconds,milliseconds = "","","","","","",""
  age_data = get_duration(birthdate)
  
  #Years
  if age_data["years"] == 1:
    years = f"{age_data['years']} year "
    if age_data["months"] > 6 and not short:
      months = f"{age_data['months']} months"
  
  elif age_data["years"] > 1:
    years = f"{age_data['years']} years "
    if age_data["months"] > 9:
      if short:
        years = f"{age_data['years'] + 1} years"
      else:
        months = f"{age_data['months']} months"

  #<1 year
  else:
    #Months
    if age_data["months"] == 1:
      months = f"{age_data['months']} month "
      if age_data["days"] > 20:
        if not short:                      #Strange conditional works opposite of design
          months = f"{age_data['months'] + 1}"
        else:
          days = f"{age_data['days']} days"
    elif age_data["months"] > 1:
      months = f"{age_data['months']} months "
      if age_data["days"] > 20:
        if not short:          #Strange conditional works opposite of design
          months = f"{age_data['months'] + 1} months "
        else:
          days = f"{age_data['days']} days"
    
    #<1 month
    else:
      #Days
      if age_data["days"] == 1:
        days = f"{age_data['days']} day"
      
      elif age_data["days"] > 1:
        days = f"{age_data['days']} days"
      
      #<1 day
      else:
        #Hours
        if age_data["hours"] == 1:
          hours = f"{age_data['hours']} hour"
        
        elif age_data["hours"] > 1:
          hours = f"{age_data['hours']} hours"
        
        #<1 hour
        else:
          #Minutes
          if age_data["minutes"] == 1:
            minutes = f"{age_data['minutes']} min"
          
          elif age_data["minutes"] > 1:
            minutes = f"{age_data['minutes']} mins"
          else:
            #Seconds
            if age_data["seconds"] == 1:
              seconds = f"{age_data['seconds']} sec"
          
            elif age_data["seconds"] > 1:
              seconds = f"{age_data['seconds']} secs"
            else:
              #milliseconds
              if age_data["milliseconds"] >= 1:
                minutes = f"{age_data['milliseconds']} ms"
              else:
                return

  
  return f"{years}{months}{days}{hours}{minutes}{seconds}{milliseconds}"

def is_in_range(start_date:str,end_date:str,target_date:date|datetime):
  """Returns True if 'target_date' is between 'start_date' and 'end_date'"""
    
  start_date,end_date,target_date = datetime.fromisoformat(start_date).date(),datetime.fromisoformat(end_date).date(),target_date.date() if type(target_date) == datetime else target_date

  if target_date >= start_date and target_date <= end_date:
    return True
  else:
    return False



#FROM DB
def uom(medicine_name:str,compact:bool=False):
  """Returns a string for name of unit of measure of medicine with medicine_name"""

  suffix = medicine_name.split(" ")[-1].strip()

  if compact:
    data= {"tab":"tb","cap":"cp","sol":"bt","ampoule":"amp","suspension":"bt","gel":"tu"}
    if suffix in data:
      return data[suffix]
    else:
      return "pk"
  else:
    data = {"tab":"tablet","cap":"capsule","sol":"bottle","ampoule":"ampoule","suspension":"bottle","gel":"tube"}
    if suffix in data:
      return data[suffix]
    else:
      return "item"
