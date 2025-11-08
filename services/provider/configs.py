"""This is a configuration file for project level settings."""
#GENERAL IMPORTS
import os
from dotenv import load_dotenv
from sqlalchemy import Engine
from sqlmodel import create_engine



###
load_dotenv()


#DATABASE ENGINE
database_engine:Engine = create_engine(os.getenv("DB_URL"))


#ROUTES
