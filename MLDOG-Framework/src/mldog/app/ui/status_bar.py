import tkinter as tk
from tkinter import ttk

from ..model.data_source import DataSource



class StatusBar(tk.Frame):
    """
    The application status bar.
    """
    
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.style: ttk.Style = ttk.Style(self)
        self.data_source: DataSource = None

        # Activity indicator
        self.active_label = tk.Label(self, text='\u25CF', bd=1, relief=tk.FLAT, anchor=tk.W, background='white')
        self.active_label.configure(foreground = 'red', background='white')
        self.active_label.grid(column=0, row=0, padx=2, pady=2)

        # Data Source Label
        self.ds_label = tk.Label(self, text='Disconnected', bd=1, relief=tk.FLAT, anchor=tk.W, background='white')
        self.ds_label.grid(column=1, row=0, padx=2, pady=2)

        # Separator
        # sep = ttk.Separator(self, orient=tk.VERTICAL)
        # self.style.configure('Normal.TLabel', font=('Cambria', 10),  foreground='black', background='white')
        # sep.configure(style='Normal.TLabel')
        # sep.grid(column=2, row=0, sticky=(tk.N, tk.S))

        # self.columnconfigure(0, weight=1)


    def setDataSource(self, ds: DataSource):
        """
        Set the active data source.
        """
        
        if self.data_source is not None:
            self.data_source.removeListener('measuring_changed', self.refreshDSActiveLabel)

        self.data_source = ds

        if self.data_source is not None:
            self.ds_label.config(text = self.data_source.getName())
            self.data_source.addListener('measuring_changed', self.refreshDSActiveLabel)
        else:
            self.ds_label.config(text = 'Disconnected')

        self.refreshDSActiveLabel()


    def refreshDSActiveLabel(self):
        """
        Refresh the data source active label.
        """
        
        self.active_label.configure(foreground = 'green' if self.data_source is not None and self.data_source.isMeasuring() else 'red')
