"""A module to store animations"""
"""Styles are in animations.css in assets/ folder"""

#GENERAL IMPORTS
from random import choice
from nicegui import html,ui

#PROJECT IMPORTS
from .components import CompanyName



#Animations
def bubbles(user=None):
  """A function to display bubbles"""
  #DATA
  first,last=["N","E","X","A"],["S","O","F","T"]
  
  #UI
  if user:
    with ui.label().classes(add="absolute bottom-0 right-0"):
      CompanyName()
  for i in range(15):
    with html.span().classes(add="puto"):
      html.span(choice(first) if i%2 else choice(last)).classes(add="dot text-center")


