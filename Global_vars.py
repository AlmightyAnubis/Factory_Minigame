import tkinter.font as tk_font
import tkinter as tk
from tkinter import ttk

font: tk_font.Font
factory_font: tk_font.Font

start = False
stop = False

facilities: dict[int,dict] = {}
facility_count = 0

progress_bars = {}
upgrade_buttons = {}
power_buttons = {}
storage_label = {}
dropdown = {}
inputs = {}
outputs : dict[int,dict[int,tuple[tk.Frame,float]]] = {}
outputs_scales : dict[int,dict[int,tk.Scale]] = {}
outputs_chem : dict[int,dict[int,ttk.Combobox]] = {}
storage : dict[int,dict] = {}
connections : dict[int,dict[int,tuple[int,int]]] = {}
in_production = {}
production_state = {}

unlocked = {}

factory_frames =[]
style: ttk.Style