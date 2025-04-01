import ctypes
import random
import tkinter
import tkinter.font as tk_font
from copy import deepcopy
from anytree import Node, RenderTree, NodeMixin

import Global_vars

color_map: dict = dict()

class BaseMixin(NodeMixin):
    def __init__(self, name,parent=None,children=None):
        self.name = name
        self.parent = parent
        if children:
            self.children = children

class Species(BaseMixin):
    def __init__(self, name,parent=None,children=None):
        super().__init__(name,parent,children)

    def __str__(self):
        return self.name

class Reaction(BaseMixin):
    def __init__(self, name, label=None, parent=None, children=None):
        super().__init__(name, parent, children)
        self.label = label

    def __str__(self):
        return self.name




def calculate_path(species: Species, game, used_reactions: list = None, parent_path = None, do_compressed=True):

    if used_reactions is None:
        used_reactions = list()
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
            if product not in base_products:
                if key not in used_reactions:
                    if product in reaction_products:
                        reaction_products[product].append(key)
                        continue
                    reaction_products[product] = [key]
                else:
                    if species.name in reaction_products:
                        print(">Circle detected<")
                        print("Species:", species)
                        print(">Calculating in and output<")
                        print(do_compressed)


    # Check if any production or reaction is available for selected product
    if species.name not in reaction_products and species.name not in base_products:
        return None

    #reaction_dict: dict[:,[list,tkinter.Label]]
    #reaction_dict = dict()
    #result: dict[str,dict] = dict()
    #result[species] =  reaction_dict

    # Production is beginning, so don't go elsewhere from here
    if species.name in base_products:
        for production_key in base_products[species.name]:
            Reaction(production_key, parent=species)
        return
    # Product now is for save in any reaction

    # Get all reactions for the species
    first_reactions = reaction_products[species.name]
    # Scan all reactions
    if do_compressed:
        copied = deepcopy(used_reactions)
        copied.extend(first_reactions)
    for reaction_key in first_reactions:
        reaction_educts = reactions[reaction_key]["educts"]
        reaction = Reaction(reaction_key, parent=species)
        # Check for the input(educts) in the selected reaction
        for educt in reaction_educts:
            if not do_compressed:
                copied = deepcopy(used_reactions)
                copied.append(reaction_key)
            educt_species = Species(educt,parent=reaction)
            calculate_path(educt_species, game, copied, do_compressed=do_compressed)


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
    species = None


    def __init__(self, path: Species, game, expanded = False):
        super().__init__()
        self.title("Reaction Path Calculator")
        self.game = game
        self.species = path

        # path -> result = (species, reaction_dict)
        self.container = tkinter.Canvas(self)
        self.container.grid(row=0, column=0, columnspan = 2, padx=5, pady=5, sticky=tkinter.NSEW)
        row, height = self.generate_reaction_labels(path, 1, 100)
        self.container.grid_columnconfigure(list(range(100-height,100)), minsize=100)
        affected_rows = list(range(row))
        self.container.grid_rowconfigure(affected_rows, minsize=10)
        self.container.update()
        self.generate_flow_arrows(path)
        text = "Expand"
        if expanded:
            text = "Collapse"
        btn = tkinter.Button(self, text=text, font=('Arial', 15), command=lambda e=expanded: self.expand(e))
        btn.grid(column=0, row=1, padx=5, pady=5, sticky=tkinter.NSEW)

        btn = tkinter.Button(self, text="Close", font=('Arial', 15), command=lambda: self.on_ok())
        btn.grid(column=1, row=1, padx=5, pady=5, sticky=tkinter.NSEW)

    def generate_reaction_labels(self, species: BaseMixin, parent_row, parent_column):
        row = parent_row
        labels = list()
        height = 1
        for reaction in species.children:
            if reaction.name not in color_map:
                color_map[reaction.name] = "#{0:06X}".format(
                    random.randrange(128) + 128 + 256 * (
                                random.randrange(128) + 128 + 256 * (random.randrange(128) + 128)))

            #sub_row = 0
            empty_label = None
            if isinstance(reaction, Reaction):
                span_0 = 0
                if len(species.children) > 1:
                    span_0 = 1
                for reaction_species in reaction.children:
                    span, child_height = self.generate_reaction_labels(reaction_species, row + span_0, parent_column - 2)
                    height = max(height, child_height + 2) #
                    if reaction_species.name not in color_map:
                        color_map[reaction_species.name] = "#{0:06X}".format(
                            random.randrange(128) + 256 * (
                                    random.randrange(128) + 256 * (random.randrange(128))))
                    span_0 += span + 1
                if len(species.children) > 1:
                    pass
                else:
                    span_0 -= 1
                span_0 = max(span_0, 1)

                label = tkinter.Label(self.container, text=get_reaction_str(reaction.name, self.game, span_0), font=('Arial', 12), background=color_map[reaction.name], relief="raised")
                label.grid(column=parent_column - 1, row=row, rowspan=span_0, sticky=tkinter.NSEW)
                reaction.label = label
                row += span_0

        return row - parent_row, height

    def generate_flow_arrows(self, species:Species, parent_label= None):
        for reaction in species.children:
            label = reaction.label
            for reaction_species in reaction.children:
                self.generate_flow_arrows(reaction_species, label)
            if parent_label is None:
                continue
            x1 = label.winfo_x()
            y1 = label.winfo_y()
            width1 = label.winfo_width()
            height1 = label.winfo_height()
            start = (x1 + width1,y1 + height1/2)

            x2 = parent_label.winfo_x()
            y2 = parent_label.winfo_y()
            width2 = parent_label.winfo_width()
            height2 = parent_label.winfo_height()
            end = (x2, y2 + height2/2)
            arrow = self.container.create_line(start[0],start[1], end[0], end[1], fill="black", arrow=tkinter.LAST)
            self.container.tag_lower(arrow)
            text_obj = self.container.create_text(start[0] + (end[0] - start[0])/2, start[1] + (end[1] - start[1])/2, font=('Arial', 12,tk_font.BOLD),anchor="center", text=self.game.chem_map[species.name], fill=color_map[species.name])
            bbox = self.container.bbox(text_obj)
            self.container.create_rectangle(bbox[0], bbox[1], bbox[2], bbox[3], fill=self.container["bg"])
            self.container.tag_raise(text_obj)



    def center(self):
        self.update()
        scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
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
        print("Expanding", expanded)
        calculate_path(species, self.game, do_compressed=expanded)
        self.destroy()
        PathDialog(species, self.game,expanded=not expanded).center().show()



    def show(self):
        self.wm_deiconify()
        self.wait_window()
