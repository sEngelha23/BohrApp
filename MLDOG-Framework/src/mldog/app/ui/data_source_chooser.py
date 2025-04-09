import tkinter as tk
from tkinter import ttk

from .wizard import Wizard
from ..model.core import Core



class DataSourceChooser(tk.Frame):
    """
    Simple panel for selecting a data source.
    """
    
    def __init__(self, parent: tk.Frame, core: Core, ds_wizards: list[Wizard]):
        tk.Frame.__init__(self, parent)
        # super().__init__(parent)

        self.columnconfigure(0, weight=1)

        for idx, dsw in enumerate(ds_wizards):
            # Create wizard button
            btn = ttk.Button(self, text=dsw.name, command=lambda wizard = dsw: wizard.show(parent, core), style='Heading.TButton')
            btn.grid(column=0, row=idx, padx=2, pady=2, sticky=(tk.E, tk.W))
