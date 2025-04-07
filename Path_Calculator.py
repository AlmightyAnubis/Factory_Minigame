import ctypes
import os
import random
import random
import time
import tkinter
import tkinter.font as tk_font
from copy import deepcopy

import matplotlib.pyplot as plt
import networkx
from PIL import ImageGrab

import Global_vars

color_map: dict = dict()

class BaseMixin:
    def __init__(self, name):
        self.name = name


class Species(BaseMixin):
    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        return self.name

class Reaction(BaseMixin):
    def __init__(self, name, label=None):
        super().__init__(name)
        self.label = label

    def __str__(self):
        return self.name


double_use_mode = True

def calculate_path(species: Species, game, parent_reactions = None, parent_path = None, do_compressed=True, debug=0):
    graph = Global_vars.current_graph
    if debug==1:
        print(species)
    if parent_reactions is None:
        parent_reactions = list()
    production_fac = game.production
    reactions = game.reaction
    # Dict that contains all productions for all possible products (maybe generate in the beginning to store global for better performance)
    base_products = dict()
    # Dict that contains all reactions for all possible products (maybe generate in the beginning to store global for better performance)
    reaction_products = dict()

    # Map reaction and production for any product
    for key, item in production_fac.items():
        for product in item["products"]:
            if product in base_products:
                base_products[product].append(key)
                continue
            base_products[product] = [key]

    for key, item in reactions.items():
        for product in item["products"]:
            if product in reaction_products:
                reaction_products[product].append(key)
                continue
            reaction_products[product] = [key]



    # Check if any production or reaction is available for selected product
    if species.name not in reaction_products and species.name not in base_products:
        if debug==1:
            print("<- failed " + species.name)
        return False

    #reaction_dict: dict[:,[list,tkinter.Label]]
    #reaction_dict = dict()
    #result: dict[str,dict] = dict()
    #result[species] =  reaction_dict

    found_path = False
    # Production is beginning, so don't go elsewhere from here
    if species.name in base_products:
        for production_key in base_products[species.name]:
            reaction = Reaction(production_key)
            found_node = False
            if double_use_mode:
                for node in graph:
                    if isinstance(node, Reaction):
                        if node.name == production_key:
                            reaction = node
                            found_node = True
                            break
            if not found_node:
                graph.add_node(reaction)
            graph.add_edge(reaction, species)
        if debug==1:
            print("<- found " + species.name)
        found_path = True

    if species.name not in reaction_products:
        return found_path

    # Product now is for save in any reaction

    # Get all reactions for the species
    first_reactions = reaction_products[species.name]
    # Scan all reactions
    #if do_compressed:
    #    copied = deepcopy(used_reactions)
    #    copied.extend(first_reactions)

    for reaction_key in first_reactions:

        reaction_educts = reactions[reaction_key]["educts"]
        reaction = Reaction(reaction_key)
        found_node = False


        if reaction_key in parent_reactions:
            if debug:
                print("Circle Found for ", species, " from ", reaction_key)
            reaction_list: list[BaseMixin] = list()
            new_key = reaction_key

            reaction_list.append(Reaction(reaction_key))
            reaction_list.append(species)
            pre = list(graph.successors(species))
            new_key = pre[0]
            while new_key.name!=reaction_key:
                reaction_list.append(new_key)
                pre = list(graph.successors(new_key))
                new_key = pre[0]
            suc = list(graph.predecessors(new_key))
            if debug == 1:
                for sub_r in reaction_list:
                    print("->", sub_r, end="")


            reaction_multiplier = 1
            total = dict()
            for i in range(len(reaction_list)//2):
                pre_reaction_multiplier = reaction_multiplier
                circle_reaction = reaction_list[i*2]
                circle_species = reaction_list[i*2+1]
                pre_circle_species = reaction_list[i * 2 - 1]
                if circle_reaction.name in reactions:
                    reaction_educts = reactions[circle_reaction.name]["educts"]
                    reaction_products = reactions[circle_reaction.name]["products"]
                    pre_reaction_multiplier /= reaction_educts[pre_circle_species.name]
                    if debug == 1:
                        print(circle_reaction.name, pre_reaction_multiplier)
                    for educt in reaction_educts:
                        if educt in total:
                            total[educt] -= reaction_educts[educt] * pre_reaction_multiplier
                        else:
                            total[educt] = -reaction_educts[educt] * pre_reaction_multiplier
                    for product in reaction_products:
                        if product in total:
                            total[product] += reaction_products[product] * pre_reaction_multiplier
                        else:
                            total[product] = reaction_products[product] * pre_reaction_multiplier
                    reaction_multiplier = pre_reaction_multiplier * reaction_products[circle_species.name]
            if debug == 1:
                print("Total: ", total)
            if total[species.name] <= 0:
                continue
            if debug == 1:
                print("Found working Loop")
            continue
        else:
            if double_use_mode:
                for node in graph:
                    if isinstance(node, Reaction):
                        if node.name == reaction_key:
                            reaction = node
                            found_node = True
                            found_path = True
                            graph.add_edge(reaction, species)
                            break


        if not found_node:
            graph.add_node(reaction)
            # Check for the input(educts) in the selected reaction
            all_educts = True
            for educt in reaction_educts:
                #if not do_compressed:
                copied = deepcopy(parent_reactions)
                copied.append(reaction_key)
                educt_species = Species(educt)
                graph.add_node(educt_species)
                graph.add_edge(educt_species, reaction)
                graph.add_edge(reaction, species)
                found_sub_path = calculate_path(educt_species, game, parent_reactions = copied, do_compressed=do_compressed, debug=debug)
                all_educts = all_educts and found_sub_path
                if not found_sub_path:
                    graph.remove_node(educt_species)
                    graph.remove_node(reaction)
                    break
                else:
                    for suc in graph.predecessors(educt_species):
                        graph.add_edge(suc, reaction, name=educt_species.name)
                        #Global_vars.graph_label[(suc,reaction)] = educt_species.name
                    graph.remove_node(educt_species)
            found_path = all_educts or found_path
    found_str = ""
    if found_path:
        found_str = "found"
        if debug == 2:
            plt.figure(figsize=(32, 18))
            plt.title(species.name)
            pos = networkx.spring_layout(graph)
            networkx.draw(graph, pos, with_labels=True)
            attributes = networkx.get_edge_attributes(graph, "name")
            networkx.draw_networkx_edge_labels(graph, pos,attributes)
            plt.show()
    else:
        found_str = "failed"
    if debug == 1:
        print("<- " + found_str + " " + species.name)
    return found_path

def get_reaction_str(reaction_name, game, span=1):
    text = reaction_name + "\n"
    data = None
    if reaction_name in game.production:
        data = game.production[reaction_name]
    if reaction_name in game.reaction:
        data = game.reaction[reaction_name]
    if data is None:
        print("No data for reaction", reaction_name)
    ed = data["educts"]
    if len(ed) > 0:
        for educt, amount in ed.items():
            if amount != 1:
                text += f"{amount} "
            text += game.chem_map[educt] + " + "
        text = text[:-3]
    if span > 3:
        text += "\n=>\n"
    else:
        text += " => "
    pr = data["products"]
    if len(pr) > 0:
        for prod, amount in pr.items():
            if amount != 1:
                text += f"{amount} "
            text += game.chem_map[prod] + " + "
        text = text[:-3]
    return text


class PathDialog(tkinter.Tk):
    game = None
    global color_map
    species: Species = None

    min_col_width = 100
    min_row_height = 10

    def __init__(self, path: Species, game, expanded = False):
        super().__init__()
        #options = {
        #    "with_labels": True,
        #    "font_size":40,
        #    "node_shape":"s",
        #    "node_color":"none",
        #    "bbox":dict(facecolor="skyblue", edgecolor="black", boxstyle="round,pad=0.2")
        #}
        #plt.figure(figsize=(128, 72))
        #networkx.draw_spring(,**options)
        #plt.show()
        self.title("Reaction Path Calculator")
        self.game = game
        self.species = path


        graph = Global_vars.current_graph
        output = Reaction("Output")
        for suc in graph.predecessors(path):
            graph.add_edge(suc, output, name=path.name)

        # path -> result = (species, reaction_dict)
        self.container = tkinter.Canvas(self)
        self.container.grid(row=0, column=0, columnspan = 2, padx=5, pady=5, sticky=tkinter.NSEW)
        start_row = 100
        row, height = self.generate_reaction_labels(output, start_row, 100)
        self.container.grid_columnconfigure(list(range(100-height+2,100)), minsize=self.min_col_width)
        affected_rows = list(range(min(start_row, start_row + row),max(start_row,start_row + row)))
        self.container.grid_rowconfigure(affected_rows, minsize=self.min_row_height)
        self.container.update()
        self.generate_flow_arrows(output)
        text = "Expand"
        if expanded:
            text = "Collapse"
        #expand = tkinter.Button(self, text=text, font=('Arial', 15), command=lambda e=expanded: self.expand(e))
        #expand.grid(column=0, row=1, padx=5, pady=5, sticky=tkinter.NSEW)

        screenshot = tkinter.Button(self, text="Save", font=('Arial', 15))
        screenshot.configure(command=lambda s=screenshot: self.capture_window(s))
        screenshot.grid(column=0, row=1, padx=5, pady=5, sticky=tkinter.NSEW)

        close = tkinter.Button(self, text="Close", font=('Arial', 15), command=lambda: self.on_ok())
        close.grid(column=1, row=1, padx=5, pady=5, sticky=tkinter.NSEW)

        #self.bind('<Key>', lambda key: self.locate(key))
        #self.bind('<FocusIn>', print("Focus"))
        self.wm_attributes('-topmost', True)


    def generate_reaction_labels(self, species: Reaction, parent_row, parent_column):
        graph = Global_vars.current_graph
        row = parent_row
        labels = list()
        height = 1
        for reaction in graph.predecessors(species):
            if reaction.name not in color_map:
                color_map[reaction.name] = "#{0:06X}".format(
                    random.randrange(128) + 128 + 256 * (
                                random.randrange(128) + 128 + 256 * (random.randrange(128) + 128)))

            #sub_row = 0
            empty_label = None
            if isinstance(reaction, Reaction):
                span_0 = 0
                if len(list(graph.predecessors(reaction))) > 1:
                    span_0 = 1
                span, child_height = self.generate_reaction_labels(reaction, row + span_0, parent_column - 2)
                height = max(height, child_height + 2) #

                span_0 += span + 1
                if len(list(graph.predecessors(reaction))) > 1:
                    pass
                else:
                    pass
                    #span_0 -= 1
                span_0 = max(span_0, 1)
                if reaction.label is None:
                    label = tkinter.Label(self.container, text=get_reaction_str(reaction.name, self.game, span_0), font=('Arial', 12), background=color_map[reaction.name], relief="raised")
                    label.grid(column=parent_column - 1, row=row, rowspan=span_0, sticky=tkinter.NSEW)
                    reaction.label = label
                else:
                    label = reaction.label
                    old_column = label.grid_info()["column"]
                    new_column =min(parent_column - 1, old_column)
                    old_row = label.grid_info()["row"]
                    new_row =min(row, old_row)
                    if new_row == old_row:
                        new_row = old_row - 2
                    #new_row = row
                    if reaction.name == "Water Pump":
                        print(old_row, row, new_row)
                    span = label.grid_info()["rowspan"]
                    label.grid(column=new_column,row=new_row, rowspan=span, sticky=tkinter.NSEW)
                    label.update()
                    #time.sleep(0.1)

                row += span_0

        return row - parent_row, height

    def generate_flow_arrows(self, parent_reaction:Reaction, parent_label= None):
        graph = Global_vars.current_graph
        attributes = networkx.get_edge_attributes(graph, "name")
        for reaction in graph.predecessors(parent_reaction):
            label = reaction.label
            specieses = graph.get_edge_data(reaction,parent_reaction)
            inital_offset = 0
            for key,species in specieses.items():
                species = species["name"]

                if species not in color_map:
                    color_map[species] = "#{0:06X}".format(
                        random.randrange(128) + 256 * (
                                    random.randrange(128) + 256 * (random.randrange(128))))

                self.generate_flow_arrows(reaction, label)

                if parent_label is None:
                    continue
                x1 = label.winfo_x()
                y1 = label.winfo_y() + inital_offset
                width1 = label.winfo_width()
                height1 = label.winfo_height()
                start = (x1 + width1,y1 + height1/2)

                x2 = parent_label.winfo_x()
                y2 = parent_label.winfo_y()
                width2 = parent_label.winfo_width()
                height2 = parent_label.winfo_height()
                end = (x2, y2 + height2/2)

                color = color_map[species]

                #horizontal = x2-(x1 + width1)<=self.min_col_width
                horizontal = start[1]>y2 #and horizontal
                if end[1] == start[1]  or horizontal:
                    end = (end[0], start[1])
                    arrow = self.container.create_line(start[0],start[1], end[0], end[1], fill=color, arrow=tkinter.LAST)
                    self.container.tag_lower(arrow)
                    text_obj = self.container.create_text(end[0] - self.min_col_width * 3/5, start[1], font=('Arial', 12,tk_font.BOLD), anchor="center", text=self.game.chem_map[species], fill=color)
                    bbox = self.container.bbox(text_obj)
                    self.container.create_rectangle(bbox[0], bbox[1], bbox[2], bbox[3], fill=self.container["bg"])
                    self.container.tag_raise(text_obj)
                else:
                    end = (x2, y2 + height1 / 2)
                    if abs(end[1]-start[1])<= self.min_row_height*1.1:
                        end = (end[0], start[1])
                    arrow1 = self.container.create_line(start[0], start[1], end[0] - self.min_col_width/7 - (x2-x1)/20, start[1], fill=color)
                    arrow2 = self.container.create_line(end[0] - self.min_col_width/7 - (x2-x1)/20, start[1], end[0] - self.min_col_width/7 - (x2-x1)/20, end[1], fill=color)
                    arrow3 = self.container.create_line(end[0] - self.min_col_width/7 - (x2-x1)/20 , end[1], end[0], end[1], fill=color, arrow=tkinter.LAST)
                    self.container.tag_lower(arrow1)
                    self.container.tag_lower(arrow2)
                    self.container.tag_lower(arrow3)
                    text_obj = self.container.create_text(end[0] - self.min_col_width/7 - (x2-x1)/20,start[1] + (end[1] - start[1]) / 2, font=('Arial', 12,tk_font.BOLD), anchor="center", text=self.game.chem_map[species], fill=color)
                    bbox = self.container.bbox(text_obj)
                    self.container.create_rectangle(bbox[0], bbox[1], bbox[2], bbox[3], fill=self.container["bg"], outline=color)
                    self.container.tag_raise(text_obj)
                inital_offset += 24
                self.container.update()

    def capture_window(self, widget:tkinter.Widget):
        scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        x = self.winfo_rootx() * scaleFactor
        y = self.winfo_rooty() * scaleFactor
        width = self.winfo_width() * scaleFactor
        height = self.winfo_height()
        w_height = widget.winfo_height()

        pady = widget.grid_info()["pady"]

        height = int(height - w_height - pady*2) * scaleFactor
        takescreenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height),all_screens=True)
        takescreenshot.save("screenshot.png")


    def center(self):
        self.update()
        screen_width = Global_vars.window_dimensions[3]
        screen_height = Global_vars.window_dimensions[2]
        width = self.winfo_width()
        height = self.winfo_height()
        width = round(width)
        height = round(height)
        x = int(((screen_width / 2) - (width / 2)))
        y = int(((screen_height / 2) - (height / 2)))
        self.geometry(f"{width}x{height}+{x}+{y}")
        return self

    def on_ok(self):
        self.destroy()

    def expand(self, expanded):

        species = Species(self.species.name)
        Global_vars.current_graph = networkx.DiGraph()
        Global_vars.current_graph.add_node(species)
        calculate_path(species, self.game, do_compressed=expanded)
        self.destroy()
        PathDialog(species, self.game,expanded=not expanded).center().show()



    def show(self):
        self.wm_deiconify()
        self.wait_window()
