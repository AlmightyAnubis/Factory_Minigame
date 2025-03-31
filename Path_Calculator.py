import random
import tkinter

color_map: dict = dict()


def calculate_path(species, game, used_reactions: list = None):
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

    # Check if any production is available for selected product
    if species not in reaction_products and species not in base_products:
        return None

    result = tuple()
    reaction_dict = dict()
    result = (species, reaction_dict)

    if species in base_products:
        for product in base_products[species]:
            reaction_dict[product] = list()
        return result

    first_reactions = reaction_products[species]
    educts = list()
    for reaction_key in first_reactions:
        reaction_educts = reactions[reaction_key]["educts"]
        reaction_dict[reaction_key] = list()
        used_reactions.append(reaction_key)
        # deepcopy(used_reactions)
        for educt in reaction_educts:
            educt_reactions = calculate_path(educt, game)
            if educt_reactions is not None:
                reaction_dict[reaction_key].append(educt_reactions)
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

    def __init__(self, path: tuple[str, dict], game):
        super().__init__()
        self.title("Reaction Path Calculator")
        self.game = game
        print(path)

        # path -> result = (species, reaction_dict)
        self.container = tkinter.Canvas(self)
        self.container.grid(row=0, column=0, sticky=tkinter.NSEW)
        row = self.generate_reaction_labels(path, 100, 100)

        btn = tkinter.Button(self, text="Close", font=('Arial', 15), command=lambda: self.on_ok())
        btn.grid(column=1000, row=row, padx=5, pady=5, sticky=tkinter.NSEW)

    def generate_reaction_labels(self, path, parent_row, parent_column):
        row = parent_row
        for key, reactions in path[1].items():
            if key not in color_map:
                color_map[key] = "#{0:06X}".format(
                    random.randrange(128) + 128 + 256 * (
                                random.randrange(128) + 128 + 256 * (random.randrange(128) + 128)))

            span_0 = 1
            sub_row = 0
            empty_label = None
            for reaction in reactions:
                span = self.generate_reaction_labels(reaction, row + sub_row, parent_column - 2)
                if reaction[0] not in color_map:
                    color_map[reaction[0]] = "#{0:06X}".format(
                        random.randrange(128) + 128 + 256 * (
                                random.randrange(128) + 128 + 256 * (random.randrange(128) + 128)))

                label = tkinter.Label(self.container, text="---" + self.game.chem_map[reaction[0]] + "-->", font=('Arial', 10), background=color_map[reaction[0]], relief="raised")
                label.grid(column=parent_column - 2, row=row + sub_row, rowspan=span, sticky=tkinter.NSEW)
                empty_label = tkinter.Label(self.container)
                empty_label.grid(column=parent_column-2, row=row + sub_row + span, sticky=tkinter.NSEW)

                sub_row += span + 1
                span_0 += span + 1
            if empty_label is not None:
                empty_label.grid_forget()

            label = tkinter.Label(self.container, text=get_reaction_str(key, self.game, span_0), font=('Arial', 10),
                                  background=color_map[key], relief="raised")

            label.grid(column=parent_column - 1, row=row, rowspan=span_0, sticky=tkinter.NSEW)
            row += span_0

        return row - parent_row

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
