import tkinter as tk
from tkinter import ttk
import numpy as np
from PIL import Image, ImageTk
import os
from matplotlib import pyplot as plt
import matplotlib.backends.backend_tkagg as tkagg
from ...model.core import Core
from ...ui.application import MLDOGApplication
from ...tasks.detector_and_predictor_task import DetectorAndPredictorTask


class DrillOwnApplication(MLDOGApplication):
    def __init__(self, core: Core, parent: tk.Frame):
        
        MLDOGApplication.__init__(self, 'Vorhersage', core, parent)

        self.fig = None
        self.ax = None
        self.canvas = None
        self._pause_processing = False

        # configure grid layout weights
        self._ui.columnconfigure(0, weight=1)
        self._ui.rowconfigure(0, weight=0)
        self._ui.rowconfigure(1, weight=1)
        self._ui.rowconfigure(2, weight=0)

        # Label für Prediction
        row = 0
        self.label = ttk.Label(self._ui, text='Warten auf Datenempfang...', style='Heading.TLabel', font=('Helvetica', 20), background='white')
        self.label.grid(column=0, row=row, pady=(10, 5), columnspan=2)

        # Plot UI
        row = row + 1
        self.canvas_wrapper = ttk.Frame(self._ui, padding=0)
        self.canvas_wrapper.grid(column=0, row=row, sticky=tk.NSEW)

        self.fig, self.ax = plt.subplots(dpi=100)
        self.canvas = tkagg.FigureCanvasTkAgg(self.fig, self.canvas_wrapper)
        self.toolbar = tkagg.NavigationToolbar2Tk(self.canvas, self.canvas_wrapper)

        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.toolbar.update()

        # Controls
        row = row + 1
        btn_row = tk.Frame(self._ui)

        self.toggle_plotting_text = tk.StringVar(value='Plotten Pausieren')
        self.toggle_plotting_btn = ttk.Button(btn_row, textvariable=self.toggle_plotting_text, command=self.togglePlotting, padding='20 15')
        self.toggle_plotting_btn.grid(column=1, row=0, padx=20)

        # Start Detector and Predictor Task
        self._core.setTask(DetectorAndPredictorTask(), self.handleTaskResult) 


    def handleTaskResult(self, ausgabe: object):
        
        #Einteilung der Ausgabe von selbsterstellter Task

        data = ausgabe[0]
        result = ausgabe[1]

        #Erstellen des Graphen und einzeichnen der Daten

        if not self._pause_processing and type(data) is np.ndarray:
            self.ax.clear()
            xVals = np.arange(len(data)) / 96000
            self.ax.plot(xVals, data[:, 1])
            self.ax.plot(xVals, data[:, 2])
            self.ax.plot(xVals, data[:, 0])

            self.ax.set_xlabel('Zeit in Sekunden')
            self.ax.set_ylabel('Wert')
            self.ax.grid(False)
            self.ax.legend(['Spannung', 'Strom', 'Ton'], loc='upper right', bbox_to_anchor=(1.2, 1.2))
            self.fig.tight_layout()
            self.ax.spines[['top', 'right']].set_visible(False)
            self.canvas.draw()
            self.label.config(text=f'Aufgenommene Daten weisen auf {result} hin')
            self._ui.after(5000, self.clear_prediction)


    def clear_prediction(self):
        self.label.config(text="Warten auf weitere Daten...")


    def togglePlotting(self):
        """
        Toggle (enable / disable) internal processing of detected drill procedures.
        """
        self._pause_processing = not self._pause_processing
        self.toggle_plotting_text.set('Plotten Fortsetzen' if self._pause_processing else 'Plotten Pausieren')