import tkinter as tk
from tkinter import ttk

from ..model.core import Core



class Wizard:
    """
    Base class for wizards.
    """

    def __init__(self, name:str, title: str):
        self.wizard = None

        self.ui: tk.Frame = None
        self.core: Core = None

        self.name: str = name
        self.title: str = title

        self.wizard_panes: list(tk.Frame) = []

        self.finish_btn: tk.Button = None
        self.cancel_btn: tk.Button = None


    def show(self, ui: tk.Frame, core: Core, width=400, height=280):
        self.ui = ui
        self.core = core

        win = ui.winfo_toplevel()

        self.wizard = tk.Toplevel(win)
        self.wizard.title(self.title)

        x = win.winfo_x() + win.winfo_width() // 2 - width // 2
        y = win.winfo_y() + win.winfo_height() // 2 - height // 2
        self.wizard.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        self.wizard.columnconfigure(0, weight=1)
        self.wizard.rowconfigure(0, weight=1)

        # construct actual wizard panes
        self.wizard_pane = self.constructWizardPane()

        self.wizard_pane.grid(column=0, row=0, pady=20, padx=20, sticky=(tk.N, tk.E, tk.S, tk.W))

        # Separator
        sep = ttk.Separator(self.wizard, orient=tk.HORIZONTAL)
        sep.grid(column=0, row=1, sticky=(tk.E, tk.W))
        
        # bottom button row
        btn_row = tk.Frame(self.wizard)
        btn_row.columnconfigure(0, weight=1)

        self.cancel_btn = ttk.Button(btn_row, text='Cancel', command = self.cancel, padding='20 10')
        self.cancel_btn.grid(column=0, row=0, padx=10, sticky=tk.E)

        self.finish_btn = ttk.Button(btn_row, text='Finish', command = self.finish, padding='20 10')
        self.finish_btn.grid(column=1, row=0, padx=10)

        btn_row.grid(column=0, row=2, pady=15, padx=10, sticky=(tk.W, tk.E))

        self.wizard.focus_set() # take over input focus
        self.wizard.grab_set() # disable other windows
        self.wizard.protocol('WM_DELETE_WINDOW', lambda: self.wizard.after_idle(self.reset))
        self.wizard.wait_window() # and wait here until win destroyed
    

    def constructWizardPane(self) -> tk.Frame:
        return None


    def cancel(self):
        self.wizard.after_idle(self.reset)


    def finish(self):
        self.wizard.after_idle(self.reset)


    def reset(self):
        self.wizard.grab_release()
        self.wizard.destroy()
        self.wizard = None

        self.wizard_panes = []

        self.finish_btn = None
        self.cancel_btn = None
