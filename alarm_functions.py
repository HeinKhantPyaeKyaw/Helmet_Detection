import tkinter as tk

# Functions regarding with indicator light
def change_indicator_color(canvas, color):
  canvas.itemconfig("indicator", fill=color)
  
# Update the indicator light to red because of violation``
def handle_violation(canvas):
  change_indicator_color(canvas, "red")
  
# Reset the indicator light to green
def reset_indicator(canvas):
  change_indicator_color(canvas, "green")
