import tkinter as tk
import math


class GeneralDialog(tk.Tk):
    result: str
    buttons: list

    def __init__(self, prompt, answers):
        super().__init__()
        self.result = ""
        self.buttons = list()
        label = tk.Label(self, text=prompt,font=('Arial', 20))
        label.grid(column=0, row=0, columnspan=len(answers), sticky=tk.NSEW)

        height = round(math.sqrt(len(answers)))
        for i in range(len(answers)):
            btn = tk.Button(self, text=answers[i],font=('Arial', 15),command=lambda r=answers[i]: self.on_ok(r))
            self.buttons.append(btn)
            btn.grid(column=i//height, row=i%height+1, padx = 5,pady=5, sticky=tk.NSEW)

    def center(self):
        self.update()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        scale_factor = 1
        width = self.winfo_width()
        height = self.winfo_height()
        width =    round(width/scale_factor)
        height =   round(height/scale_factor)
        x = int(((screen_width / 2) - (width / 2)) * scale_factor)
        y = int(((screen_height / 2) - (height / 1.5)) * scale_factor)
        self.geometry(f"{width}x{height}+{x}+{y}")
        return self

    def on_ok(self, answer):
        self.result = answer
        self.destroy()

    def show(self):
        self.wm_deiconify()
        self.wait_window()
        return self.result

