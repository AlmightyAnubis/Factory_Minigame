import copy
import datetime
import json
import pathlib
import tkinter as tk
import tkinter.font as tk_font
import tkinter.messagebox
import tkinter.simpledialog
from tkinter import ttk

import networkx
from matplotlib import pyplot as plt

import Facilitys
import Global_vars
import Path_Calculator
from Reaction_Shop import GeneralDialog


#       earnings = (self.products['Hydrogen'] * 2 + self.products['Oxygen'] * 3 + self.products['Carbon'] * 5 +
#                    self.products['Methane'] * 10 + self.products['Ethene'] * 15 +
#                    self.products['Polyethylene'] * 25 + self.products['Ester'] * 30)

class FactoryGame:
    def __init__(self, root: tk.Tk):
        self.quick_mode = True
        self.money = 500.0
        self.time = 60 * 60
        if self.quick_mode:
            self.money = 3000.0
            self.time = 10 * 60
        self.chem_map = {
            "Energy": "Energy",
            "Water": "H2O",
            "Hydrogen": "H2",
            "Oxygen": "O2",
            "Nitrogen": "N2",
            "Carbon": "C",
            "Carbon monoxide": "CO",
            "Carbon dioxide": "CO2",
            "Methane": "CH4",
            "Methanol": "CH3OH",
            "Dimethyl ether": "CH3OCH3",
            "Ethylene": "C2H4",
            "Propylen": "C3H6",
            "Polyethylene": "(-C2H4-)n",
            "Ethanol": "C2H5OH",
            "Acetic acid": "C2H4O2",
            "Ester": "C4H7O3",
            "Paladium": "Pd",
            "Adsorpt Hydrogen": "H*",
            "Adsorpt Carbon monoxide": "CO*",
            "Adsorpt Carbon": "C*",
            "Adsorpt Hydrocarbonmonoxide":"CHO*",
            "Adsorpt Dihydrocarbonmonoxide":"CH2O*",
            "Adsorpt Trihydrocarbonmonoxide":"CH3O*",
            "Adsorpt Methanol":"CH3OH*",
            "Adsorpt Methane": "CH4*",
            "Adsorpt CH3": "CH3*",
            "Adsorpt CH2": "CH2*",
            "Adsorpt CH": "CH*",
            "Adsorpt Oxygen": "O*",
            "Adsorpt Hydroxyl": "OH*"
        }

        # Edit Production_Configuration.json with Config_Manager, don't forget to add new chemicals to self.product_value and self.chem_map
        self.product_value: dict[str, float]
        config_file = open("Prices.json", "r")
        json_ob = config_file.read()
        config_file.close()
        self.product_value = json.loads(json_ob)


        self.production: dict[str, dict]
        config_file = open("Production_Configuration.json", "r")
        json_ob = config_file.read()
        config_file.close()
        self.production = json.loads(json_ob)

        # Edit Reaction_Configuration.json with Config_Manager, don't forget to add new chemicals to self.product_value and self.chem_map
        config_file = open("Reaction_Configuration.json", "r")
        json_ob = config_file.read()
        config_file.close()
        self.reaction = json.loads(json_ob)

        self.upgrade_cost_scaling = 1.5
        self.upgrade_speed_scaling = 1.5
        # END OF CONFIG

        reaction_grid_width = 2 * len(self.production.keys()) // 7
        self.product_amount = {}
        for key in self.chem_map.keys():
            species = Path_Calculator.Species(key)
            Global_vars.current_graph = networkx.MultiDiGraph()
            Global_vars.current_graph.add_node(species)
            found_path = Path_Calculator.calculate_path(species, self)
            if found_path:
                self.product_amount[key] = 0

        Global_vars.complete_graph = networkx.MultiDiGraph()
        comp_graph = Global_vars.complete_graph
        species_list = list()
        for key,reaction in self.reaction.items():
            reaction_node = Path_Calculator.Reaction(key)
            comp_graph.add_node(reaction_node)
            nodes = comp_graph.nodes
            node_map = {}
            for node in nodes:
                node_map[node.name] = node
            educts = reaction["educts"]
            for educt in educts:
                educt_node = None
                if educt in node_map:
                    educt_node = node_map[educt]
                if educt_node is None:
                    educt_node = Path_Calculator.Species(educt)
                    species_list.append(educt_node)
                    comp_graph.add_node(educt_node)
                comp_graph.add_edge(educt_node, reaction_node)

            products = reaction["products"]
            product_node = None
            for product in products:
                if product in node_map:
                    product_node = node_map[product]
                if product_node is None:
                    product_node = Path_Calculator.Species(product)
                    species_list.append(product_node)
                    comp_graph.add_node(product_node)
                comp_graph.add_edge(reaction_node,product_node)

        #for node in species_list:
        #    outputs = list(comp_graph.successors(node))
        #    inputs =list(comp_graph.predecessors(node))
        #    if len(inputs) == 0 or len(outputs) == 0:
        #        continue
        #    for input in inputs:
        #        for output in outputs:
        #            comp_graph.add_edge(input, output, name=node.name)
        #    comp_graph.remove_node(node)


        #plt.figure(figsize=(32, 18), dpi=400)
        #plt.title("Complete Reaction Network")
        #pos = networkx.spring_layout(Global_vars.complete_graph, scale=30, k = 1.8, threshold=0.000001)
        #networkx.draw(Global_vars.complete_graph, pos, with_labels=True)
        #attributes = networkx.get_edge_attributes(Global_vars.complete_graph, "name")
        #networkx.draw_networkx_edge_labels(Global_vars.complete_graph, pos, attributes)
        #plt.show()
        #plt.savefig("screenshot.svg", format='svg')

        self.time *= 1000

        self.root = root
        self.root.title("Chemical Factory Empire")
        root.iconbitmap("Images/logo.ico")

        root.bind_all("<B1-Motion>", lambda e: self.move_mouse(e))
        root.bind_all("<ButtonRelease-1>", lambda e: self.button_release(e))

        root.grid_rowconfigure(4, weight=1)

        self.container: tk.Canvas
        self.container = tk.Canvas(root)
        self.container.bind('<MouseWheel>', self.zoom)
        self.container.bind('<Button-1>', self.move_all_start)

        # container.grid_columnconfigure(list(range(reaction_grid_width)), weight=1)
        # Test for scrollable frame failed

        # canvas_frame = tk.Canvas(container)
        # scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas_frame.yview)
        # scrollable_frame = ttk.Frame(canvas_frame)
        # scrollable_frame.bind("<Configure>", lambda e: canvas_frame.configure(scrollregion=canvas_frame.bbox("all")))
        # canvas_frame.create_window((0, 0), window=scrollable_frame, anchor="nw")
        # canvas_frame.configure(yscrollcommand=scrollbar.set)
        # scrollable_frame.grid_columnconfigure([0, 1], weight=1)
        # canvas_frame.bind_all("<MouseWheel>", on_mouse_wheel)  # Enable scrolling with mouse wheel

        counter = 0
        self.unlock_buttons = {}
        for branch, data in self.production.items():
            if data["unlocked"]:
                button = tk.Button(root, text="Buy: " + branch + f" (${data["base_cost"]})",
                                   command=lambda b=branch: Facilitys.create_factory(self, b))
            else:
                button = tk.Button(root, text="Unlock: " + branch + f" (${data["unlock_cost"]})",
                                   command=lambda b=branch: self.unlock_branch(b))
                self.unlock_buttons[branch] = button
            button.grid(row=3, column=counter, sticky=tk.EW)
            counter -= - 1

        button = tk.Button(root, text="Buy Reactor ($50)",
                           command=lambda b=branch: Facilitys.create_reactor(self), bg="salmon")
        button.grid(row=3, column=counter, sticky=tk.EW)
        counter -= - 1

        button = tk.Button(root, text="Buy Splitter ($5)",
                           command=lambda b=branch: Facilitys.create_splitter(self), bg="lightyellow")
        button.grid(row=3, column=counter, sticky=tk.EW)
        counter -= - 1

        button = tk.Button(root, text="Buy Distillery ($500)",
                           command=lambda b=branch: Facilitys.create_distillery(self), bg="sandybrown")
        button.grid(row=3, column=counter, sticky=tk.EW)
        counter -= - 1

        button = tk.Button(root, text="Buy Reaction",
                           command=lambda: self.buy_reaction(), bg="azure")
        button.grid(row=3, column=counter, sticky=tk.EW)
        counter -= - 1

        root.grid_columnconfigure(list(range(counter)), weight=1)

        small_font = tk_font.Font(size=8)
        creator = tk.Label(root, text="by Florian Jacob", font=small_font)
        creator.grid(row=0, column=0, sticky=tk.NSEW)

        money_font = tk_font.Font(family="FixedSys", size=24)
        self.money_label = tk.Label(root, text=f"Money: ${self.money}", font=money_font)
        self.money_label.grid(row=0, column=1, columnspan=counter - 2, sticky=tk.EW)

        minutes = "{:02n}".format(int(self.time / 1000 // 60))
        seconds = "{:02n}".format(int(self.time / 1000 % 60))
        self.timer = tk.Label(root, text=f"Time Left: {minutes}:{seconds}", font=money_font)
        self.timer.grid(row=0, column=counter - 1, sticky=tk.EW)

        self.production_frame = tk.Frame(root)
        self.production_frame.grid(row=1, column=0, columnspan=counter, sticky=tk.EW)
        row = 0
        column = 0

        #
        key: str

        left_border = tk.Frame(self.production_frame)

        for key in self.product_amount.keys():
            button = tk.Button(self.production_frame, text=key + "($" + str(self.product_value[key]).rjust(3) + "):",
                               command=lambda k=key: self.calculate_path(k))
            button.grid(row=row, column=column + 1, sticky=tk.EW)
            column -= - 1
            label = tk.Label(self.production_frame, text="-", font=Global_vars.font, name=key.lower(), anchor=tk.E)
            label.grid(row=row, column=column + 1, sticky=tk.EW)
            column -= - 1
            if column == 6:
                row += 1
                column = 0
        right_border = tk.Frame(self.production_frame)
        left_border.grid(row=0, column=0, rowspan=row + 1, sticky=tk.NSEW)
        right_border.grid(row=0, column=7, rowspan=row + 1, sticky=tk.NSEW)
        self.production_frame.columnconfigure([0, 7], weight=1)

        self.update_products()

        self.sell_button = tk.Button(root, text="Sell All Products", command=self.sell_products, font=money_font,
                                     bg="light green")
        self.sell_button.grid(row=2, column=0, columnspan=counter)

        for r in self.reaction.keys():
            Global_vars.unlocked[r] = self.reaction[r]["unlocked"]

        self.container.grid(row=4, column=0, columnspan=counter, sticky=tk.NSEW)

        # canvas_frame.grid(row=0,column=0, sticky=tk.NSEW)
        # scrollbar.grid(row = 0, column = 1, sticky = tk.NS)
        if self.quick_mode:
            self.speed_div /= 10
        self.update_production()
        root.state('zoomed')
        self.root.update()
        Global_vars.window_dimensions = (root.winfo_x(),root.winfo_y(),root.winfo_height(),root.winfo_width())

    text_size = 12

    def zoom(self, event: tk.Event):
        if event.delta == -120 and self.text_size > 3:
            self.text_size *= 0.9
        if event.delta == 120 and self.text_size < 30:
            self.text_size /= 0.9
        # print(self.text_size)
        Global_vars.factory_font.configure(size=int(self.text_size))
        Global_vars.bar_style.configure("custom.Horizontal.TProgressbar", thickness=int(self.text_size))
        Global_vars.factory_style.configure("Factory.Bold.TLabel", font=Global_vars.factory_font)

        self.container.update()
        self.update_lines()
        # self.current_line = self.container.create_line(self.start_point[0] + 0.5 * self.start_box.winfo_width(),
        #                                       self.start_point[1] + 0.5 * self.start_box.winfo_height(),
        #                                       line_end[0], line_end[1], width=5)

    def update_lines(self):
        connection_lines = Global_vars.connections
        for key1, value1 in connection_lines.items():
            for key2, value2 in value1.items():
                out_frame = Global_vars.outputs[key1][key2][0]
                in_frame = Global_vars.inputs[value2[0]]

                start_point = self.get_frame_center(out_frame)
                end_point = self.get_frame_center(in_frame)

                self.container.coords(value2[1], start_point[0] + 0.5 * out_frame.winfo_width(),
                                      start_point[1] + 0.5 * out_frame.winfo_height(),
                                      end_point[0] + 0.5 * in_frame.winfo_width(),
                                      end_point[1] + 0.5 * in_frame.winfo_height())

    def get_frame_center(self, out_frame):
        start_point = [out_frame.winfo_x(), out_frame.winfo_y()]
        target_frame = out_frame
        while True:
            parent_frame = target_frame.master
            if parent_frame == self.container:
                break
            start_point[0] += parent_frame.winfo_x()
            start_point[1] += parent_frame.winfo_y()
            target_frame = parent_frame
        return start_point

    def buy_reaction(self):
        keys = list()
        for key, data in Global_vars.unlocked.items():
            if data:
                continue
            text = key + "\n" + str(self.reaction[key]["unlock_cost"])
            keys.append(text)

        reaction = GeneralDialog("Select plot type",
                                 keys).center().show()

        if reaction == "":
            return
        reaction = reaction.split("\n")[0]
        if self.money >= self.reaction[reaction]["unlock_cost"]:
            self.money -= self.reaction[reaction]["unlock_cost"]
            self.money_change_event()
            Global_vars.unlocked[reaction] = True
            unlocked_list = self.get_unlocked_reactions()
            self.reaction[reaction]["unlocked"] = True
            for c in Global_vars.dropdown:
                Global_vars.dropdown[c]["values"] = unlocked_list
        else:
            self.purchase_fail_event()

    def get_unlocked_reactions(self):
        reactions = list()
        for reaction, data in self.reaction.items():
            if not Global_vars.unlocked[reaction]:
                continue
            text = f"{reaction}"
            text = text.ljust(25)
            ed = data["educts"]
            if len(ed) > 0:
                shift = 1
                for educt, amount in ed.items():
                    if amount != 1:
                        text += f"{amount} "
                    text += self.chem_map[educt] + " + "
                text = text[:-3]
            text += " => "
            pr = data["products"]
            if len(pr) > 0:
                for prod, amount in pr.items():
                    if amount != 1:
                        text += f"{amount} "
                    text += self.chem_map[prod] + " + "
                text = text[:-3]
            text = text.ljust(40)
            reactions.append(str(text))
        return reactions

    widget_x = 0
    widget_y = 0
    moving_facility = None
    target: list[tk.Frame]
    started = ""
    current_line = None
    start_box: tk.Widget
    start_point: ()

    def move_all_start(self, event: tk.Event):
        self.widget_x = event.x
        self.widget_y = event.y
        self.started = "move_all"

    def click_start(self, event: tk.Event, frame: tk.Frame, facility_id: int):
        self.widget_x = event.x
        self.widget_y = event.y
        self.target = [frame]
        self.started = "move"
        self.moving_facility = facility_id

    def line_start(self, event: tk.Event, frames: list[tk.Frame]):
        self.widget_x = event.x
        self.widget_y = event.y
        self.target = frames
        self.started = "line"
        self.start_box = event.widget
        self.start_point = (self.start_box.winfo_x(), self.start_box.winfo_y())
        for frame in frames:
            self.start_point = (self.start_point[0] + frame.winfo_x(), self.start_point[1] + frame.winfo_y())

        line_end = (self.start_point[0] + self.widget_x, self.start_point[1] + self.widget_y)
        self.current_line = self.container.create_line(self.start_point[0] + 0.5 * self.start_box.winfo_width(),
                                                       self.start_point[1] + 0.5 * self.start_box.winfo_height(),
                                                       line_end[0], line_end[1], width=5, fill="green")

    def button_release(self, event: tk.Event):
        if self.started != "line":
            self.started = ""
            return
        self.started = ""
        widget: tk.Widget
        widget = event.widget
        widget = widget.winfo_containing(event.x_root, event.y_root)

        output_id = list()
        for key, value_dict in Global_vars.outputs.items():
            for el_id, tup in value_dict.items():
                if self.start_box == tup[0]:
                    output_id.append((key, el_id))

        if len(output_id) > 1:
            raise LookupError("Multiple widgets are equal")
        if len(output_id) == 0:
            raise LookupError("No widgets found")

        output_id = output_id[0]

        if type(widget) is not tk.Frame:
            self.container.delete(self.current_line)
            if output_id[1] in Global_vars.connections[output_id[0]].keys():
                self.container.delete(Global_vars.connections[output_id[0]].pop(output_id[1])[1])
            return

        input_id = [key for key, val in Global_vars.inputs.items() if val == widget]
        if len(input_id) > 1:
            raise LookupError("Multiple widgets are equal")
        if len(input_id) == 0:
            self.container.delete(self.current_line)
            if output_id[1] in Global_vars.connections[output_id[0]].keys():
                self.container.delete(Global_vars.connections[output_id[0]].pop(output_id[1])[1])
            return

        print("Connected: " + str(output_id[0]) + "." + str(output_id[1]) + " and " + str(input_id[0]))

        parent_frame = widget.master
        self.container.coords(self.current_line, self.start_point[0] + 0.5 * self.start_box.winfo_width(),
                              self.start_point[1] + 0.5 * self.start_box.winfo_height(),
                              widget.winfo_x() + parent_frame.winfo_x() + 0.5 * widget.winfo_width(),
                              widget.winfo_y() + parent_frame.winfo_y() + 0.5 * widget.winfo_height())
        self.container.itemconfigure(self.current_line, fill="black")

        if output_id[0] in Global_vars.connections.keys():
            if output_id[1] in Global_vars.connections[output_id[0]].keys():
                self.container.delete(Global_vars.connections[output_id[0]].pop(output_id[1])[1])
        if output_id[0] not in Global_vars.connections.keys():
            Global_vars.connections[output_id[0]] = {}
        Global_vars.connections[output_id[0]][output_id[1]] = (input_id[0], self.current_line)

    def move_mouse(self, event: tk.Event):
        if self.started == "move":
            delta = ((self.widget_x - event.x), (self.widget_y - event.y))
            new_pos = (self.target[0].winfo_x() - delta[0], self.target[0].winfo_y() - delta[1])
            self.target[0].place(x=new_pos[0], y=new_pos[1])
            self.update_lines()
        if self.started == "move_all":
            delta = ((self.widget_x - event.x), (self.widget_y - event.y))
            for frame in Global_vars.factory_frames:
                frame.place(x=frame.winfo_x() - delta[0], y=frame.winfo_y() - delta[1])

            self.widget_x = event.x
            self.widget_y = event.y

            self.update_lines()

        if self.started == "line":
            line_end = (self.start_point[0] + event.x, self.start_point[1] + event.y)
            self.container.coords(self.current_line, self.start_point[0] + 0.5 * self.start_box.winfo_width(),
                                  self.start_point[1] + 0.5 * self.start_box.winfo_height(), line_end[0],
                                  line_end[1])

    def update_products(self):
        for k in self.product_amount.keys():
            widget = self.production_frame.children.get(k.lower())
            if isinstance(widget, tk.Label):
                component: tk.Label = widget
                component.configure(text="{:.1f}".format(self.product_amount[k]%10000).rjust(6))

    def money_change_event(self):
        money = "{:1.1f}".format(self.money)
        self.money_label.config(text="Money: $" + money)
        for branch in self.production:
            if branch in self.unlock_buttons:
                if self.production[branch]["unlock_cost"] > self.money:
                    self.unlock_buttons[branch].configure(fg="red")
                else:
                    self.unlock_buttons[branch].configure(fg="black")

        for key, element in Global_vars.facilities.items():
            if not element:
                continue
            if "level" not in element:
                continue
            current_level = element["level"]
            upgrade_cost = element["base_cost"] * (self.upgrade_cost_scaling ** current_level)

            if upgrade_cost > self.money:
                Global_vars.upgrade_buttons[key].configure(fg="red")
            else:
                Global_vars.upgrade_buttons[key].configure(fg="black")

    def update_time(self):
        minutes = "{:02n}".format(int(self.time / 1000 // 60))
        seconds = "{:02n}".format(int(self.time / 1000 % 60))
        self.timer.config(text=f"Time Left: {minutes}:{seconds}")

    def purchase_fail_event(self):
        self.money_label.configure(fg="red")
        self.root.after(300, lambda: self.money_label.configure(fg="black"))
        self.root.after(600, lambda: self.money_label.configure(fg="red"))
        self.root.after(900, lambda: self.money_label.configure(fg="black"))

    speed_div = 10000

    def update_progress(self, speed):
        return speed / self.speed_div

    timestep = 50

    def update_production(self):
        if not Global_vars.start:
            self.root.after(self.timestep, self.update_production)
            return
        if Global_vars.stop:
            return
        self.time -= self.timestep
        if self.time < 0:
            Global_vars.stop = True
            self.sell_products()
            self.save_highscore()
            return
        self.root.after(0, self.update_time)
        for facility_id, data in Global_vars.facilities.items():
            if not data:
                continue
            if data["unlocked"]:
                if Global_vars.in_production[facility_id] == 0:
                    if Global_vars.production_state[facility_id] == 1:
                        requirements: dict
                        requirements = data["educts"]
                        if "splitter" in requirements.keys():
                            for stored in Global_vars.storage[facility_id].values():
                                if stored > 0:
                                    Global_vars.in_production[facility_id] += 1
                                    break
                        elif "distillery" in requirements.keys():
                            for stored in Global_vars.storage[facility_id].values():
                                if stored > 0:
                                    Global_vars.in_production[facility_id] += 1
                                    break
                        elif all(Global_vars.storage[facility_id].get(req, 0) >= requirements[req] for req in
                                 requirements):
                            for req in requirements:
                                Global_vars.storage[facility_id][req] -= requirements[req]
                                if Global_vars.storage[facility_id][req] == 0:
                                    Global_vars.storage[facility_id].pop(req)
                            self.update_storage(facility_id)
                            Global_vars.in_production[facility_id] += 1
                            data["progress"] = 0
                            data["progress"] += self.update_progress(data["speed"])
                else:
                    if data["progress"] >= 1000:
                        product = copy.deepcopy(data["products"])
                        requirements = data["educts"]
                        if "splitter" in product.keys():
                            product = copy.deepcopy(Global_vars.storage[facility_id])
                            Global_vars.storage[facility_id] = {}
                            self.update_storage(facility_id)
                        if "distillery" in requirements.keys():
                            product = Global_vars.storage[facility_id]

                        out_sum = 1
                        if "distillery" in requirements.keys():
                            pass
                        else:
                            out_sum = 0
                            for output_id, output_data in Global_vars.outputs[facility_id].items():
                                out_sum += output_data[1]
                        if out_sum > 0:
                            prod_copy = copy.deepcopy(product)
                            for output_id, output_data in Global_vars.outputs[facility_id].items():
                                if output_id in Global_vars.connections[facility_id]:
                                    target_id = Global_vars.connections[facility_id][output_id][0]
                                    keys = product.keys()
                                    if "distillery" in requirements.keys():
                                        if output_data[1] in keys:
                                            Global_vars.storage[target_id][output_data[1]] = Global_vars.storage[
                                                                                                 target_id].get(
                                                output_data[1], 0) + product[output_data[1]]
                                            product.pop(output_data[1])
                                            self.update_storage(facility_id)
                                    else:
                                        for prod in keys:
                                            Global_vars.storage[target_id][prod] = Global_vars.storage[target_id].get(
                                                prod, 0) + prod_copy[prod] * output_data[1] / out_sum
                                            product[prod] -= prod_copy[prod] * output_data[1] / out_sum
                                    self.update_storage(target_id)
                                else:
                                    keys = product.keys()
                                    if "distillery" in requirements.keys():
                                        if output_data[1] in keys:
                                            self.product_amount[output_data[1]] += product[output_data[1]]
                                            product.pop(output_data[1])
                                            self.update_storage(facility_id)

                                    else:
                                        for prod in keys:
                                            self.product_amount[prod] = self.product_amount.get(prod, 0) + prod_copy[
                                                prod] * output_data[1] / out_sum
                                            product[prod] -= prod_copy[prod] * output_data[1] / out_sum

                        Global_vars.in_production[facility_id] = 0
                        data["progress"] = 0
                    else:
                        data["progress"] += self.update_progress(data["speed"])

                Global_vars.progress_bars[facility_id]["value"] = data["progress"]

        self.update_products()
        self.root.after(self.timestep, self.update_production)

    def sell_products(self):
        earnings = 0
        for branch, data in self.product_amount.items():
            earnings += self.product_value[branch] * data
        self.money += earnings
        self.product_amount = {k: 0 for k in self.product_amount}
        self.money_change_event()

        self.update_products()
        Global_vars.start = True

    def toggle_branch(self, branch):
        Global_vars.start = True
        if not Global_vars.facilities[branch]:
            return
        if not Global_vars.facilities[branch]["unlocked"]:
            return
        if Global_vars.production_state[branch] == 1:
            Global_vars.production_state[branch] = 0
            Global_vars.power_buttons[branch].config(text=f"Off")
        else:
            Global_vars.production_state[branch] = 1
            Global_vars.power_buttons[branch].config(text=f"On")

    def upgrade_branch(self, branch):
        Global_vars.start = True
        if not Global_vars.facilities[branch]:
            return

        current_level = Global_vars.facilities[branch]["level"]
        upgrade_cost = Global_vars.facilities[branch]["base_cost"] * (self.upgrade_cost_scaling ** current_level)

        if self.money >= upgrade_cost:
            self.money -= upgrade_cost
            Global_vars.facilities[branch]["level"] += 1
            Global_vars.facilities[branch]["speed"] = max(1000, Global_vars.facilities[branch][
                "speed"] * self.upgrade_speed_scaling)  # Faster production
            self.money_change_event()
            self.update_products()
            if Global_vars.facilities[branch][
                "speed"] * self.upgrade_speed_scaling > 2 * self.speed_div * 10000 / self.timestep:
                Global_vars.upgrade_buttons[branch].config(text=f"Upgrade (max)")
                Global_vars.upgrade_buttons[branch].config(state=tk.DISABLED)
            else:
                Global_vars.upgrade_buttons[branch].config(
                    text=f"Upgrade (${upgrade_cost * self.upgrade_cost_scaling:.0f})")
        else:
            self.purchase_fail_event()

    def unlock_branch(self, branch):
        Global_vars.start = True
        if self.money >= self.production[branch]["unlock_cost"]:
            self.money -= self.production[branch]["unlock_cost"]
            self.production[branch]["unlocked"] = True
            self.money_change_event()
            self.unlock_buttons[branch].config(command=lambda: Facilitys.create_factory(self, branch))
            self.unlock_buttons[branch].config(text="Buy: " + branch + f" (${self.production[branch]["base_cost"]})")
            self.unlock_buttons[branch].update()
            self.unlock_buttons.pop(branch)
        else:
            self.purchase_fail_event()

    def update_storage(self, target_id):
        if target_id not in Global_vars.storage:
            return
        string = ""
        for k in Global_vars.storage[target_id].keys():
            string = string + "{:.1f}".format(Global_vars.storage[target_id][k]).rjust(3) + self.chem_map[k] + "  "
        Global_vars.storage_label[target_id].config(text=string)

    def save_highscore(self):
        score_file = pathlib.Path("highscore.txt")
        if not score_file.is_file():
            file = open("highscore.txt", "w")
            file.write("10:00\n")
            file.write("60:00\n")
            file.close()
        file = open("highscore.txt", "r")
        lines = file.read().splitlines()
        file.close()
        short_game = lines.index("10:00")
        long_game = lines.index("60:00")
        short_records = {}
        long_records = {}
        for i in range(short_game + 1, long_game):
            line = lines[i]
            line = line.split("\t")
            short_records[line[0] + "\t" + line[1]] = float(line[2])

        for i in range(long_game + 1, len(lines)):
            line = lines[i]
            line = line.split("\t")
            long_records[line[0] + "\t" + line[1]] = float(line[2])

        name = tkinter.simpledialog.askstring("Enter name", "Enter Player name for highscore:")
        if name == "":
            name = "No Name"
        name = name.replace("\t", "-")
        x = datetime.datetime.now()
        name = name + "\t" + x.strftime("%d.%m.%Y %H:%M")
        if self.quick_mode:
            short_records[name] = self.money
            short_records = dict(sorted(short_records.items(), key=lambda item: -item[1]))
        else:
            long_records[name] = self.money
            long_records = dict(sorted(long_records.items(), key=lambda item: item[1]))

        file = open("highscore.txt", "w")
        file.write("10:00\n")
        for key, value in short_records.items():
            file.write(str(key) + "\t" + str(value) + "\n")
        file.write("60:00\n")
        for key, value in long_records.items():
            file.write(str(key) + "\t" + str(value) + "\n")
        file.close()

        if self.quick_mode:
            result = ""
            items = list(short_records.items())
            for i in range(min(10, len(items))):
                result = result + str(items[i][0]) + "\t" + str(items[i][1]) + "\n"
            tk.messagebox.showinfo("Highscore", result, icon=None)
        else:
            result = ""
            items = list(long_records.items())
            for i in range(min(10, len(items))):
                result = result + str(items[i][0]) + "\t" + str(items[i][1]) + "\n"
            tk.messagebox.showinfo("Highscore", result, icon=None)
        self.root.destroy()

    def calculate_path(self, key):
        species = Path_Calculator.Species(key)
        graph = networkx.MultiDiGraph()
        Global_vars.current_graph = graph
        graph.add_node(species)
        found_path = Path_Calculator.calculate_path(species, self, debug=1)
        if found_path:
            Path_Calculator.PathDialog(species, self).center().show()
        else:
            tk.messagebox.showerror("Reaction missing", "Species not available")

if __name__ == "__main__":
    root = tk.Tk()
    Global_vars.font = tk_font.Font(family="FixedSys", size=10)
    Global_vars.style = ttk.Style()
    Global_vars.style.configure("Bold.TLabel", font=Global_vars.font)
    Global_vars.factory_font = tk_font.Font(size=10)
    Global_vars.factory_style = ttk.Style()
    Global_vars.factory_style.theme_create("factory_style", parent="default")
    Global_vars.factory_style.theme_use("factory_style")
    Global_vars.factory_style.configure("Factory.Bold.TLabel", font=Global_vars.factory_font)
    Global_vars.bar_style = ttk.Style()
    Global_vars.bar_style.theme_create("bar_style", parent="default")
    Global_vars.bar_style.theme_use("bar_style")
    Global_vars.bar_style.configure("Custom.Horizontal.TProgressbar")
    game = FactoryGame(root)
    root.mainloop()
