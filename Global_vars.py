import tkinter as tk
import tkinter.font as tk_font
from tkinter import ttk

import networkx

font: tk_font.Font
factory_font: tk_font.Font

start = False
stop = False

facilities: dict[int, dict] = {}
facility_count = 0

progress_bars: dict[int, ttk.Progressbar] = {}
upgrade_buttons = {}
power_buttons = {}
storage_label = {}
dropdown = {}
inputs = {}
outputs: dict[int, dict[int, tuple[tk.Frame, float, ttk.Label | tk.StringVar | None]]] = {}
outputs_scales: dict[int, dict[int, tk.Scale]] = {}
outputs_chem: dict[int, dict[int, ttk.Combobox]] = {}
storage: dict[int, dict] = {}
connections: dict[int, dict[int, tuple[int, int]]] = {}
in_production = {}
production_state = {}

unlocked = {}

factory_frames: list[ttk.Frame] = []
style: ttk.Style
factory_style: ttk.Style
bar_style: ttk.Style

window_dimensions: tuple[int, int, int, int]

current_graph : networkx.MultiDiGraph = networkx.MultiDiGraph()
graph_label: dict = dict()

complete_graph : networkx.MultiDiGraph = networkx.MultiDiGraph()
