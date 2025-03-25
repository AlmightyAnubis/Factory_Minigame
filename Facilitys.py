import copy
import tkinter as tk
from tkinter import ttk

import Global_vars
import Plant_Builder


def create_base(facility_id, frame, game):
    frame.place(x=200, y=200)
    frame.bind("<Button-1>", lambda e: game.click_start(e, frame, facility_id))
    frame.bind_all("<B1-Motion>", lambda e: game.move_mouse(e))
    progress = ttk.Progressbar(frame, orient="horizontal", mode="determinate", style="custom.Horizontal.TProgressbar",maximum=1000)
    progress.bind("<Button-1>", lambda e: game.click_start(e, frame, facility_id))
    Global_vars.factory_frames.append(frame)
    Global_vars.progress_bars[facility_id] = progress
    Global_vars.connections[facility_id] = {}
    return progress

def create_reactor(game:Plant_Builder.FactoryGame):
    if game.money >= 50:
        game.money -= 50
        game.money_change_event()
        facility_id = Global_vars.facility_count
        frame = ttk.Frame(game.container, padding=2, borderwidth=2, relief="ridge")
        # frame.place(x=counter//reaction_grid_width * 40, y=counter% reaction_grid_width * 40)
        progress = create_base(facility_id, frame,game)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure([0, 1], weight=1)

        reactions = game.get_unlocked_reactions()

        in_frame = tk.Frame(frame, background="lightblue", borderwidth=2, relief="ridge", width=20,
                            name="in_" + str(facility_id))
        in_frame.grid(column=0, row=0, rowspan=4, sticky=tk.NS, padx=2, pady=2)
        Global_vars.inputs[facility_id] = in_frame

        out_frame = tk.Frame(frame, background="orange", borderwidth=2, relief="ridge", width=20,
                             name="out_" + str(facility_id))
        out_frame.grid(column=3, row=0, rowspan=4, sticky=tk.NS, padx=2, pady=2)
        out_frame.bind("<Button-1>", lambda e: game.line_start(e, [frame]))
        Global_vars.outputs[facility_id] = {0:(out_frame,1)}



        n = tk.StringVar()
        dropdown = ttk.Combobox(frame, textvariable=n, state="readonly", width=50, font=Global_vars.factory_font)
        dropdown["values"] = reactions
        dropdown.bind("<<ComboboxSelected>>", lambda e, el_id=facility_id: update_reaction(game,e, el_id))
        dropdown.grid(column=1, row=0, columnspan=2, sticky=tk.NSEW, padx=2, pady=2)

        progress.grid(column=1, row=1, columnspan=2, sticky=tk.NSEW, padx=2, pady=2)

        # How to store upgrade when changing reaction?


        btn = tk.Button(frame, text=f"-",
                        command=lambda b=facility_id: game.upgrade_branch(b), font=Global_vars.factory_font)
        # if data["base_cost"] * self.upgrade_cost_scaling > self.money:
        #    btn.configure(fg="red")
        btn.grid(column=1, row=2, sticky=tk.NSEW)

        pwr_btn = tk.Button(frame, text=f"Off", command=lambda: game.toggle_branch(facility_id), font=Global_vars.factory_font)
        pwr_btn.grid(column=2, row=2, sticky=tk.NSEW)

        label = ttk.Label(frame, text="", style="Bold.TLabel")
        label.bind("<Button-1>", lambda e: game.click_start(e, frame, facility_id))
        label.grid(column=1, row=3, columnspan=2, sticky=tk.NSEW, padx=2, pady=2)

        Global_vars.facilities[facility_id] = dict()
        Global_vars.power_buttons[facility_id] = pwr_btn
        Global_vars.upgrade_buttons[facility_id] = btn
        Global_vars.storage_label[facility_id] = label
        Global_vars.dropdown[facility_id] = dropdown
        Global_vars.in_production[facility_id] = 0
        Global_vars.production_state[facility_id] = 0
        Global_vars.storage[facility_id] = {}

        Global_vars.facility_count -= - 1
    else:
        game.purchase_fail_event()

def update_reaction(game,event: tk.Event , facility_id):
    Global_vars.start = True
    wg: ttk.Combobox
    wg = event.widget
    selected = wg.get()
    selected = selected[:25].strip()
    if selected not in game.reaction:
        raise KeyError(selected + "not found. Might be to long, max 25 characters")
    data = copy.deepcopy(game.reaction[selected])
    Global_vars.facilities[facility_id] = data
    Global_vars.in_production[facility_id] = 0

    Global_vars.upgrade_buttons[facility_id].config(text=f"Upgrade (${data["base_cost"]  * game.upgrade_cost_scaling:.0f})",state=tk.NORMAL)

max_outputs = 10

def update_outputs(game,event: tk.Event , facility_id):
    Global_vars.start = True
    wg: ttk.Combobox
    wg = event.widget
    out_count = int(wg.get())
    outputs = Global_vars.outputs[facility_id]
    for i in range(max_outputs):
        out_frame = outputs[i][0]
        scale = Global_vars.outputs_scales[facility_id][i]
        if i < out_count:
            scale.grid(column=0, row=i, sticky=tk.NS, padx=2, pady=2)
            out_frame.grid(column=1, row=i, sticky=tk.NS, padx=2, pady=2)
        else:
            Global_vars.outputs[facility_id][i] = (out_frame, 0)
            scale.set(0)
            out_frame.grid_forget()
            scale.grid_forget()

def update_fractions(game,event: tk.Event , facility_id):
    Global_vars.start = True
    wg: ttk.Combobox
    wg = event.widget
    out_count = int(wg.get())
    outputs = Global_vars.outputs[facility_id]
    for i in range(max_outputs):
        out_frame = outputs[i][0]
        scale = Global_vars.outputs_chem[facility_id][i]
        if i < out_count:
            scale.grid(column=0, row=i, sticky=tk.NS, padx=2, pady=2)
            out_frame.grid(column=1, row=i, sticky=tk.NS, padx=2, pady=2)
        else:
            Global_vars.outputs[facility_id][i] = (out_frame, 0)
            scale.set(0)
            out_frame.grid_forget()
            scale.grid_forget()

def update_value(event: tk.Event,facility_id, nr):
    scale: tk.Scale
    scale = event.widget
    current = Global_vars.outputs[facility_id][nr]
    Global_vars.outputs[facility_id][nr] = (current[0],scale.get())

def update_chem(event: tk.Event,facility_id, nr):
    scale: tk.Scale
    scale = event.widget
    current = Global_vars.outputs[facility_id][nr]
    Global_vars.outputs[facility_id][nr] = (current[0],scale.get())

def create_splitter(game:Plant_Builder.FactoryGame):
    if game.money >= 5:
        game.money -= 5
        game.money_change_event()
        facility_id = Global_vars.facility_count
        frame = ttk.Frame(game.container, padding=2, borderwidth=2, relief="ridge")
        # frame.place(x=counter//reaction_grid_width * 40, y=counter% reaction_grid_width * 40)
        progress = create_base(facility_id, frame,game)
        frame.grid_columnconfigure([0, 1], weight=1)


        reactions = list(range(1,max_outputs+1))

        in_frame = tk.Frame(frame, background="lightblue", borderwidth=2, relief="ridge", width=20,
                            name="in_" + str(facility_id))
        in_frame.grid(column=0, row=0, rowspan=4, sticky=tk.NS, padx=2, pady=2)
        Global_vars.inputs[facility_id] = in_frame

        out_container = tk.Frame(frame, borderwidth=2, relief="ridge")
        out_container.grid(column=3, row=0, rowspan=4, sticky=tk.NS, padx=2, pady=2)
        out_container.grid_columnconfigure([0, 1], weight=1)

        Global_vars.outputs_scales[facility_id] = {}
        Global_vars.outputs[facility_id] = {}
        for i in range(max_outputs):
            scale = tk.Scale(out_container,from_=0,to=10,orient=tk.HORIZONTAL,font=Global_vars.factory_font)

            scale.bind("<ButtonRelease-1>", lambda e, fac= facility_id, nr = i: update_value(e,fac,nr))
            scale.grid(column=0, row=i, sticky=tk.NS, padx=2, pady=2)
            out_frame = tk.Frame(out_container, background="orange", borderwidth=2, relief="ridge", width=100,
                                 name="out_" + str(facility_id) + str(i))
            out_frame.grid(column=1, row=i, sticky=tk.NS, padx=2, pady=2)
            out_frame.bind("<Button-1>", lambda e: game.line_start(e, [frame, out_container]))
            Global_vars.outputs_scales[facility_id][i] =scale
            if i<2:
                scale.set(1)
                Global_vars.outputs[facility_id][i] = (out_frame,1)
            else:
                scale.set(0)
                Global_vars.outputs[facility_id][i] = (out_frame,0)
                out_frame.grid_forget()
                scale.grid_forget()

        n = tk.StringVar()
        dropdown = ttk.Combobox(frame, textvariable=n, state="readonly", width=30, font=Global_vars.factory_font)
        dropdown["values"] = reactions
        dropdown.current(1)
        dropdown.bind("<<ComboboxSelected>>", lambda e, el_id=facility_id: update_outputs(game,e, el_id))
        dropdown.grid(column=1, row=0, sticky=tk.EW, padx=2, pady=2)

        progress.grid(column=1, row=1, sticky=tk.NSEW, padx=2, pady=2)

        pwr_btn = tk.Button(frame, text=f"Off", command=lambda: game.toggle_branch(facility_id), font=Global_vars.factory_font)
        pwr_btn.grid(column=1, row=2, sticky=tk.NSEW)

        label = ttk.Label(frame, text="", style="Bold.TLabel")
        label.bind("<Button-1>", lambda e: game.click_start(e, frame, facility_id))
        label.grid(column=1, row=3, columnspan=2, sticky=tk.NSEW, padx=2, pady=2)

        Global_vars.facilities[facility_id] = {"unlocked":True,"educts":{"splitter":0},"products":{"splitter":0},"progress":0,"speed":5 * game.speed_div}
        Global_vars.power_buttons[facility_id] = pwr_btn
        Global_vars.storage_label[facility_id] = label
        Global_vars.in_production[facility_id] = 0
        Global_vars.production_state[facility_id] = 0
        Global_vars.storage[facility_id] = {}

        Global_vars.facility_count -= - 1
    else:
        game.purchase_fail_event()


def create_distillery(game:Plant_Builder.FactoryGame):
    if game.money >= 500:
        game.money -= 500
        game.money_change_event()
        facility_id = Global_vars.facility_count
        frame = ttk.Frame(game.container, padding=2, borderwidth=2, relief="ridge")
        # frame.place(x=counter//reaction_grid_width * 40, y=counter% reaction_grid_width * 40)
        progress = create_base(facility_id, frame,game)
        frame.grid_columnconfigure([0, 1], weight=1)


        reactions = list(range(1,max_outputs+1))

        in_frame = tk.Frame(frame, background="lightblue", borderwidth=2, relief="ridge", width=20,
                            name="in_" + str(facility_id))
        in_frame.grid(column=0, row=0, rowspan=4, sticky=tk.NS, padx=2, pady=2)
        Global_vars.inputs[facility_id] = in_frame

        out_container = tk.Frame(frame, borderwidth=2, relief="ridge")
        out_container.grid(column=3, row=0, rowspan=4, sticky=tk.NS, padx=2, pady=2)
        out_container.grid_columnconfigure([0, 1], weight=1)

        Global_vars.outputs_chem[facility_id] = {}
        Global_vars.outputs[facility_id] = {}
        for i in range(max_outputs):
            n = tk.StringVar()
            scale = ttk.Combobox(out_container, textvariable=n, state="readonly", width=10, font=Global_vars.factory_font)
            scale.bind("<<ComboboxSelected>>", lambda e, fac=facility_id, nr=i: update_chem(e, fac, nr))

            chems = list()
            chems.append("None")
            chems.extend(list(game.chem_map.keys()))
            scale["values"] = chems
            scale.grid(column=0, row=i, sticky=tk.NS, padx=2, pady=2)
            out_frame = tk.Frame(out_container, background="orange", borderwidth=2, relief="ridge", width=100,
                                 name="out_" + str(facility_id) + str(i))
            out_frame.grid(column=1, row=i, sticky=tk.NS, padx=2, pady=2)
            out_frame.bind("<Button-1>", lambda e: game.line_start(e, [frame, out_container]))
            Global_vars.outputs_chem[facility_id][i] = scale
            if i<2:
                scale.set(1)
                Global_vars.outputs[facility_id][i] = (out_frame,1)
            else:
                scale.set(0)
                Global_vars.outputs[facility_id][i] = (out_frame,0)
                out_frame.grid_forget()
                scale.grid_forget()

        n = tk.StringVar()
        dropdown = ttk.Combobox(frame, textvariable=n, state="readonly", width=30, font=Global_vars.factory_font)
        dropdown["values"] = reactions
        dropdown.current(1)
        dropdown.bind("<<ComboboxSelected>>", lambda e, el_id=facility_id: update_fractions(game,e, el_id))
        dropdown.grid(column=1, row=0, sticky=tk.EW, padx=2, pady=2)

        progress.grid(column=1, row=1, sticky=tk.NSEW, padx=2, pady=2)


        pwr_btn = tk.Button(frame, text=f"Off", command=lambda: game.toggle_branch(facility_id), font=Global_vars.factory_font)
        pwr_btn.grid(column=1, row=2, sticky=tk.NSEW)

        label = ttk.Label(frame, text="", style="Bold.TLabel")
        label.bind("<Button-1>", lambda e: game.click_start(e, frame, facility_id))
        label.grid(column=1, row=3, columnspan=2, sticky=tk.NSEW, padx=2, pady=2)

        Global_vars.facilities[facility_id] = {"unlocked":True,"educts":{"distillery":0},"products":{"distillery":0},"progress":0,"speed":2 * game.speed_div}
        Global_vars.power_buttons[facility_id] = pwr_btn
        Global_vars.storage_label[facility_id] = label
        Global_vars.in_production[facility_id] = 0
        Global_vars.production_state[facility_id] = 0
        Global_vars.storage[facility_id] = {}

        Global_vars.facility_count -= - 1
    else:
        game.purchase_fail_event()


def create_factory(game:Plant_Builder.FactoryGame, branch):
    if game.money >= game.production[branch]["base_cost"]:
        game.money -= game.production[branch]["base_cost"]
        game.money_change_event()
        facility_id = Global_vars.facility_count
        frame = ttk.Frame(game.container, padding=2, borderwidth=2, relief="ridge")
        progress = create_base(facility_id, frame, game)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure([0, 1], weight=1)

        text = f"{branch}"
        text = text.ljust(20)
        data = game.production[branch]
        ed = data["educts"]
        if len(ed) > 0:
            for educt, amount in ed.items():
                if amount != 1:
                    text += f"{amount} "
                text += game.chem_map[educt] + " + "
            text = text[:-3]
        text += " => "
        pr = data["products"]
        if len(pr) > 0:
            in_frame = tk.Frame(frame, background="orange", borderwidth=2, relief="ridge",width=20)
            in_frame.grid(column=2, row=0, rowspan=3, sticky=tk.NS, padx=2, pady=2)
            in_frame.bind("<Button-1>", lambda e: game.line_start(e, [frame]))
            Global_vars.outputs[facility_id] = {0:(in_frame,1)}
            for prod, amount in pr.items():
                if amount != 1:
                    text += f"{amount} "
                text += game.chem_map[prod] + " + "
            text = text[:-3]
        text = text.ljust(40)

        label = ttk.Label(frame, text=text, style="Factory.Bold.TLabel")
        label.bind("<Button-1>", lambda e: game.click_start(e, frame, facility_id))
        label.grid(column=0, row=0, columnspan=2, sticky=tk.NSEW, padx=2, pady=2)

        progress.grid(column=0, row=1, columnspan=2, sticky=tk.NSEW, padx=2, pady=2)

        btn = tk.Button(frame, text=f"Upgrade ($" + str(data["base_cost"] * game.upgrade_cost_scaling) + ")",
                        command=lambda b=facility_id: game.upgrade_branch(b), font=Global_vars.factory_font)
        if data["base_cost"] * game.upgrade_cost_scaling > game.money:
            btn.configure(fg="red")
        btn.grid(column=0, row=2, sticky=tk.NSEW)


        pwr_btn = tk.Button(frame, text=f"Off", command=lambda b=facility_id: game.toggle_branch(b), font=Global_vars.factory_font)
        pwr_btn.grid(column=1, row=2, sticky=tk.NSEW)

        Global_vars.facilities[facility_id] = copy.deepcopy(data)
        Global_vars.power_buttons[facility_id] = pwr_btn
        Global_vars.upgrade_buttons[facility_id] = btn
        Global_vars.in_production[facility_id] = 0
        Global_vars.production_state[facility_id] = 0

        Global_vars.facility_count -=- 1
    else:
        game.purchase_fail_event()
