"""A module to define Vero project-customized exceptions"""

#FASTAPI IMPORTS
from fastapi import HTTPException,status





#AUTHENTICATION/AUTHORIZATION EXCEPTIONS
def no_authentication():
  """Function to raise HttpException with status code 403 if no authentication is provided by the incoming request"""

  raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No authentication provided!"
  )


def invalid_authentication():
  """Function to raise Http exception with status code 403 if invalid authentication is provided by incoming request"""

  raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication credentials!"
  )

def expired_authentication():
  """Function to raise Http exception with status code 403 if authentication credentials have expired"""

  raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Expired authentication credentials!"
  )
