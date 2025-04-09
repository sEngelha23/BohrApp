import tkinter as tk
from tkinter import ttk
import numpy as np

from matplotlib import pyplot as plt
import matplotlib.backends.backend_tkagg as tkagg

from ...model.core import Core
from ...ui.application import MLDOGApplication
from ...tasks.drill_procedure_detector_task import DrillProcedureDetectorTask


class DrillExampleApplication(MLDOGApplication):
    """
    The Drill-Example-Application, plotting detected drill procedures.
    """

    def __init__(self, core: Core, parent: tk.Frame):
        MLDOGApplication.__init__(self, 'Example Application', core, parent)
        # super().__init__('Example Application', core, parent)

        self.fig = None
        self.ax = None
        self.canvas = None

        self._pause_processing = False

        # configure grid layout weights
        self._ui.columnconfigure(0, weight=1)
        self._ui.rowconfigure(0, weight=0)
        self._ui.rowconfigure(1, weight=1)
        self._ui.rowconfigure(2, weight=0)

        row = 0
        label = ttk.Label(self._ui, text="Beispielanwendung: Bohrvorgang Plotter", style='Heading.TLabel')
        # label = ttk.Label(self._ui, text="Example Application: Drill Procedure Plotter", style='Heading.TLabel')
        label.grid(column=0, row=row, pady=(20, 5), columnspan=2)

        # plot ui
        row = row + 1

        self.canvas_wrapper = ttk.Frame(self._ui, padding='12')
        self.canvas_wrapper.grid(column=0, row=row, sticky=tk.NSEW)

        self.fig, self.ax = plt.subplots(dpi=100)
        self.canvas = tkagg.FigureCanvasTkAgg(self.fig, self.canvas_wrapper)
        self.toolbar = tkagg.NavigationToolbar2Tk(self.canvas, self.canvas_wrapper)

        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.toolbar.update()

        # controls
        row = row + 1
        btn_row = tk.Frame(self._ui)

        self.toggle_plotting_text = tk.StringVar(value='Plotten Pausieren')
        self.toggle_plotting_btn = ttk.Button(btn_row, textvariable=self.toggle_plotting_text, command = self.togglePlotting, padding='20 15')
        self.toggle_plotting_btn.grid(column=1, row=0, padx=20)

        btn_row.grid(column=0, row=row, pady=20, columnspan=2)

        # start drill procedure detection task
        self._core.setTask(DrillProcedureDetectorTask(), self.handleTaskResult)


    def handleTaskResult(self, data: object) -> None:
        """
        Handler method for task result messages.

        Parameters
        ----------
        data : object
            The message from the task.
        """

        if not self._pause_processing and type(data) is np.ndarray:
            # clear current plot
            self.ax.clear()

            # plot new drill data
            xVals = np.arange(len(data))
            line, = self.ax.plot(xVals, data[:, 1])
            line, = self.ax.plot(xVals, data[:, 2])
            line, = self.ax.plot(xVals, data[:, 0])
            self.ax.set_xlabel('Zeitschritt [#]')
            self.ax.set_ylabel('Wert')
            self.ax.legend(['Spannung [V]', 'Strom [A]', 'Ton [-]'])
            self.ax.grid()
            self.fig.tight_layout()
            self.canvas.draw()

    def togglePlotting(self):
        """
        Toggle (enable / disable) internal processing of detected drill procedures.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self._pause_processing = not self._pause_processing
        self.toggle_plotting_text.set('Plotten Fortsetzen' if self._pause_processing else 'Plotten Pausieren')



