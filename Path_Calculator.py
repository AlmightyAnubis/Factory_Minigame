import random
import tkinter
import tkinter.font as tk_font
from copy import deepcopy
from anytree import Node, RenderTree

color_map: dict = dict()


def calculate_path(species, game, used_reactions: list = None, parent_path = None):
    if used_reactions is None:
        used_reactions = list()
    production_fac = game.production
    reactions = game.reaction
    base_products = dict()
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
                    print(">Circle detected<")
                    print(">Calculating in and output<")



    # Check if any production is available for selected product
    if species not in reaction_products and species not in base_products:
        return None

    reaction_dict: dict[:,[list,tkinter.Label]]
    reaction_dict = dict()
    result = (species, reaction_dict)

    if species in base_products:
        for product in base_products[species]:
            reaction_dict[product] = [list(),None]
        return result

    first_reactions = reaction_products[species]
    for reaction_key in first_reactions:
        reaction_educts = reactions[reaction_key]["educts"]
        reaction_dict[reaction_key] = [list(),None]
        used_reactions.append(reaction_key)
        copied = deepcopy(used_reactions)
        for educt in reaction_educts:
            educt_reactions = calculate_path(educt, game, copied)
            if educt_reactions is not None:
                reaction_dict[reaction_key][0].append(deepcopy(educt_reactions))
        if not reaction_dict[reaction_key]:
            return None
    return result


def get_reaction_str(reaction_name, game, span=1):
    text = reaction_name + "\n"

    if reaction_name in game.production:
        data = game.production[reaction_name]
    if reaction_name in game.reaction:
        data = game.reaction[reaction_name]
    ed = data["educts"]
    if len(ed) > 0:
        for educt, amount in ed.items():
            if amount != 1:
                text += f"{amount} "
            text += game.chem_map[educt] + " + "
        text = text[:-3]
    if span > 2:
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

    def __init__(self, path: tuple[str, dict], game):
        super().__init__()
        self.title("Reaction Path Calculator")
        self.game = game
        print("Open Path Dialog")

        # path -> result = (species, reaction_dict)
        self.container = tkinter.Canvas(self)
        self.container.grid(row=0, column=0, sticky=tkinter.NSEW)
        row, height = self.generate_reaction_labels(path, 0, 100)
        self.container.grid_columnconfigure(list(range(100-height,100)), minsize=100)
        affected_rows = list(range(row))
        self.container.grid_rowconfigure(affected_rows, minsize=5)
        self.container.update()
        self.generate_flow_arrows(path)

        btn = tkinter.Button(self, text="Close", font=('Arial', 15), command=lambda: self.on_ok())
        btn.grid(column=1000, row=row, padx=5, pady=5, sticky=tkinter.NSEW)

    def generate_reaction_labels(self, path, parent_row, parent_column):
        row = parent_row
        labels = list()
        height = 1
        for key, reactions in path[1].items():
            if key not in color_map:
                color_map[key] = "#{0:06X}".format(
                    random.randrange(128) + 128 + 256 * (
                                random.randrange(128) + 128 + 256 * (random.randrange(128) + 128)))
            span_0 = 1
            #sub_row = 0
            empty_label = None
            for reaction in reactions[0]:
                if len(reactions[0]) == 1:
                    span_0 = 0
                span, child_height = self.generate_reaction_labels(reaction, row + span_0, parent_column - 2)
                height = max(height, child_height + 2)
                if reaction[0] not in color_map:
                    color_map[reaction[0]] = "#{0:06X}".format(
                        random.randrange(128) + 256 * (
                                random.randrange(128) + 256 * (random.randrange(128))))
                #label = tkinter.Label(self.container, text="---" + self.game.chem_map[reaction[0]] + "-->", font=('Arial', 10), background=color_map[reaction[0]], relief="raised")
                #label = tkinter.Frame(self.container, width=len(self.game.chem_map[reaction[0]])*30, height=0)
                #label.grid(column=parent_column - 2, row=row + sub_row, rowspan=span, sticky=tkinter.NE)
                #empty_label = tkinter.Frame(self.container, width=len(self.game.chem_map[reaction[0]])*30)
                #empty_label.grid(column=parent_column-2, row=row + sub_row + span, sticky=tkinter.NE)

                #sub_row += span + 1
                if len(reactions[0]) == 1:
                    span_0 += span
                else:
                    span_0 += span + 1
            #if span_0==3:
            #    span_0 -= 2

            #if empty_label is not None:
            #    empty_label.grid_forget()
            #
            label = tkinter.Label(self.container, text=get_reaction_str(key, self.game, span_0), font=('Arial', 12), background=color_map[key], relief="raised")
            label.grid(column=parent_column - 1, row=row, rowspan=span_0, sticky=tkinter.NSEW)
            path[1][key][1] = label
            row += span_0
        return row - parent_row, height

    def generate_flow_arrows(self, path, parent_label= None):
        for key, reactions in path[1].items():
            label = reactions[1]
            for reaction in reactions[0]:
                self.generate_flow_arrows(reaction, label)
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
            font = tk_font.Font(size=1) # , weight=tk_font.BOLD
            text_obj = self.container.create_text(start[0] + (end[0] - start[0])/2, start[1] + (end[1] - start[1])/2, font=('Arial', 12,tk_font.BOLD),anchor="center", text=self.game.chem_map[path[0]], fill=color_map[path[0]])
            bbox = self.container.bbox(text_obj)
            self.container.create_rectangle(bbox[0], bbox[1], bbox[2], bbox[3], fill=self.container["bg"])
            self.container.tag_raise(text_obj)
            self.container.update()


    def center(self):
        self.update()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        scale_factor = 1
        width = self.winfo_width()
        height = self.winfo_height()
        width = round(width / scale_factor)
        height = round(height / scale_factor)
        x = int(((screen_width / 2) - (width / 2)) * scale_factor)
        y = int(((screen_height / 2) - (height / 1.5)) * scale_factor)
        self.geometry(f"{width}x{height}+{x}+{y}")
        return self

    def on_ok(self):
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.wait_window()
