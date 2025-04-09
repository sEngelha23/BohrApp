import tkinter as tk
from tkinter import ttk

from ..plugin_descriptor import MLDOGApplicationDescription
from ..model.core import Core
# from .ui import MLDOGUI



class ApplicationChooser(tk.Frame):
    """
    Simple panel for selecting an application.
    """
    
    def __init__(self, parent: tk.Frame, ui, apps: list[MLDOGApplicationDescription]):
        tk.Frame.__init__(self, parent)
        # super().__init__(parent)

        self.columnconfigure(0, weight=1)

        for idx, app in enumerate(apps):
            # Create application button
            btn = ttk.Button(self, text=app.getName(), command=lambda a = app: ui.activateApplication(a), style='Heading.TButton')
            btn.grid(column=0, row=idx, padx=2, pady=2, sticky=(tk.E, tk.W))
