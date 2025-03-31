import json
import tkinter
from tkinter import ttk, simpledialog

import Reaction_Shop


class ReactionConfigManager(tkinter.Tk):
    buttons: list
    reactions: dict
    container: tkinter.Frame
    dropdown: ttk.Combobox
    string_vars: dict[str, tkinter.Variable]

    def __init__(self, mode):
        super().__init__()

        self.mode = mode
        output_file = open(mode + "_Configuration.json", "r")
        json_ob = output_file.read()
        output_file.close()
        self.reactions = json.loads(json_ob)

        self.result = ""
        self.buttons = list()
        label = tkinter.Label(self, text=mode + " Config", font=('Arial', 20))
        label.grid(column=0, row=0, columnspan=2, sticky=tkinter.NSEW)

        self.dropdown = ttk.Combobox(self, values=list(self.reactions.keys()), state="readonly")
        self.dropdown.bind("<<ComboboxSelected>>", self.update_container)
        self.dropdown.grid(column=0, row=1, columnspan=2, rowspan=2, padx=5, pady=5, sticky=tkinter.NSEW)

        self.pixel = tkinter.PhotoImage(width=1, height=1)
        add_btn = tkinter.Button(self, text=" + ", font=('Arial', 10), height=10, width=10, image=self.pixel,
                                 compound="center", command=self.add_reaction)
        add_btn.grid(column=2, row=1, sticky=tkinter.NSEW)
        del_btn = tkinter.Button(self, text=" - ", font=('Arial', 10), height=10, width=10, image=self.pixel,
                                 compound="center", command=self.remove_reaction)
        del_btn.grid(column=2, row=2, sticky=tkinter.NSEW)

        self.container = tkinter.Frame(self)
        self.container.grid(column=0, row=3, columnspan=2, sticky=tkinter.NSEW)

        save_btn = tkinter.Button(self, text="Save", font=('Arial', 15), command=self.on_ok)
        save_btn.grid(column=0, row=4, padx=5, pady=5, sticky=tkinter.NSEW)
        close_btn = tkinter.Button(self, text="Close (Don't save)", font=('Arial', 15), command=self.destroy)
        close_btn.grid(column=1, row=4, padx=5, pady=5, sticky=tkinter.NSEW)

    def add_reaction(self):
        print("Adding reaction")
        name = tkinter.simpledialog.askstring('Add Reaction', 'Enter Name of Reaction:')
        if not name:
            return
        new_reaction = {"level": 1, "products": {}, "educts": {}, "speed": 10000, "base_cost": 0, "unlock_cost": 0,
                        "progress": 0, "value": 0, "unlocked": False}
        self.reactions[name] = new_reaction
        self.dropdown.set(name)
        self.update_container()

    def remove_reaction(self):
        self.reactions.pop(self.dropdown.get())
        self.dropdown.set(None)
        self.update_container()

    def update_container(self, event=None):
        menu: ttk.Combobox
        children = self.container.winfo_children()
        for child in children:
            child.destroy()

        reaction = self.dropdown.get()
        if not reaction:
            return
        selected = self.reactions[reaction]
        i = 0

        self.string_vars = {}

        if mode == "Reaction":
            label = tkinter.Label(self.container, text="Educts", font=('Arial', 12))
            label.grid(column=0, row=i, sticky=tkinter.NSEW)
            add_btn = tkinter.Button(self.container, text="+", font=('Arial', 12), command=self.add_educt)
            add_btn.grid(column=1, row=i, sticky=tkinter.NSEW)
            i -= - 1
            educts: dict
            educts = selected["educts"]
            for educt, amount in educts.items():
                label = tkinter.Label(self.container, text=educt, font=('Arial', 10))
                label.grid(column=0, row=i, sticky=tkinter.NSEW)
                self.string_vars["e:" + educt] = tkinter.DoubleVar(value=amount)
                entry = tkinter.Entry(self.container, textvariable=self.string_vars["e:" + educt], font=('Arial', 10))
                self.string_vars["e:" + educt].trace_add("write",
                                                         lambda name, index, mode, e=educt: self.update_educt(e))
                entry.grid(column=1, row=i, sticky=tkinter.NSEW)
                del_btn = tkinter.Button(self.container, text="-", font=('Arial', 12),
                                         command=lambda p=educt: self.del_educt(p))
                del_btn.grid(column=2, row=i, sticky=tkinter.NSEW)
                i -= - 1

        label = tkinter.Label(self.container, text="Products", font=('Arial', 12))
        label.grid(column=0, row=i, sticky=tkinter.NSEW)
        add_btn = tkinter.Button(self.container, text="+", font=('Arial', 12), command=self.add_prod)
        add_btn.grid(column=1, row=i, sticky=tkinter.NSEW)
        i -= - 1
        products: dict
        products = selected["products"]
        for product, amount in products.items():
            label = tkinter.Label(self.container, text=product, font=('Arial', 10))
            label.grid(column=0, row=i, sticky=tkinter.NSEW)
            self.string_vars["p:" + product] = tkinter.DoubleVar(value=amount)
            entry = tkinter.Entry(self.container, textvariable=self.string_vars["p:" + product], font=('Arial', 10))
            self.string_vars["p:" + product].trace_add("write",
                                                       lambda name, index, mode, p=product: self.update_product(p))
            entry.grid(column=1, row=i, sticky=tkinter.NSEW)
            del_btn = tkinter.Button(self.container, text="-", font=('Arial', 12),
                                     command=lambda p=product: self.del_prod(p))
            del_btn.grid(column=2, row=i, sticky=tkinter.NSEW)
            i -= - 1

        self.add_value_config(i, "speed", "Speed")
        i -= - 1
        self.add_value_config(i, "base_cost", "Base Cost")
        i -= - 1
        self.add_value_config(i, "unlock_cost", "Unlock Cost")
        i -= - 1

        label = tkinter.Label(self.container, text="Default Unlocked", font=('Arial', 10))
        label.grid(column=0, row=i, sticky=tkinter.NSEW)
        self.string_vars["unlocked"] = tkinter.BooleanVar(value=selected["unlocked"])
        entry = tkinter.Checkbutton(self.container, text="Unlocked", onvalue=True, offvalue=False,
                                    variable=self.string_vars["unlocked"])
        self.string_vars["unlocked"].trace_add("write", lambda a, b, c: self.update_value("unlocked"))
        entry.grid(column=1, row=i, sticky=tkinter.NSEW)
        i -= - 1

        # "speed": 20000,
        # "base_cost": 20,
        # "unlock_cost": 10,
        # "unlocked": true

    def add_value_config(self, i, name, display_name=None):
        if display_name is None:
            display_name = name
        selected = self.reactions[self.dropdown.get()]
        label = tkinter.Label(self.container, text=display_name, font=('Arial', 10))
        label.grid(column=0, row=i, sticky=tkinter.NSEW)
        self.string_vars[name] = tkinter.DoubleVar(value=selected[name])
        entry = tkinter.Entry(self.container, textvariable=self.string_vars[name], font=('Arial', 10))
        self.string_vars[name].trace_add("write", lambda a, b, c: self.update_value(name))
        entry.grid(column=1, row=i, sticky=tkinter.NSEW)

    def del_educt(self, name):
        reaction = self.dropdown.get()
        selected = self.reactions[reaction]
        educts: dict
        educts = selected["educts"]
        educts.pop(name)
        self.update_container()

    def del_prod(self, name):
        reaction = self.dropdown.get()
        selected = self.reactions[reaction]
        products: dict
        products = selected["products"]
        products.pop(name)
        self.update_container()

    def add_educt(self):
        name = tkinter.simpledialog.askstring('Add Educt', 'Enter Name of Educt:')
        if not name:
            return
        reaction = self.dropdown.get()
        selected = self.reactions[reaction]
        educts: dict
        educts = selected["educts"]
        educts[name] = 0
        self.update_container()

    def add_prod(self):
        name = tkinter.simpledialog.askstring('Add Product', 'Enter Name of Product:')
        if not name:
            return
        reaction = self.dropdown.get()
        selected = self.reactions[reaction]
        products: dict
        products = selected["products"]
        products[name] = 0
        self.update_container()

    def update_educt(self, e):
        reaction = self.dropdown.get()
        selected = self.reactions[reaction]
        products: dict
        products = selected["educts"]
        var = self.string_vars["e:" + e]
        products[e] = var.get()

    def update_product(self, p):
        reaction = self.dropdown.get()
        selected = self.reactions[reaction]
        products: dict
        products = selected["products"]
        var = self.string_vars["p:" + p]
        products[p] = var.get()

    def update_value(self, name):
        selected = self.reactions[self.dropdown.get()]
        var = self.string_vars[name]
        try:
            selected[name] = var.get()
        except tkinter.TclError:
            return

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
        y = int(((screen_height / 3) - (height / 2)) * scale_factor)
        self.geometry('+%d+%d' % (x, y))
        return self

    def on_ok(self):
        json_ob = json.dumps(self.reactions, indent=2)

        output_file = open(self.mode + "_Configuration.json", "w")
        output_file.write(json_ob)
        output_file.close()

        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.wait_window()
        return self.result


keys = ["Reaction", "Production"]
mode = Reaction_Shop.GeneralDialog("Select Config to edit",
                                   keys).center().show()

dialog = ReactionConfigManager(mode)
dialog.center()
dialog.mainloop()
