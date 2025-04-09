import tkinter as tk
from tkinter import ttk

import numpy as np

from matplotlib import pyplot as plt
import matplotlib.backends.backend_tkagg as tkagg

from ...model.core import Core
from ...ui.application import MLDOGApplication

from .drill_plot_model import ApplicationState, DrillPlotModel



class DrillPlotApplication(MLDOGApplication):
    """
    The Drill-Plot-Application, providing various plotting options for drill sensor data.
    """

    def __init__(self, core: Core, parent: tk.Frame):
        MLDOGApplication.__init__(self, 'Sensordaten Plotter', core, parent)
        # super().__init__('Sensordaten Plotter', core, parent)

        self.model: DrillPlotModel = DrillPlotModel(core)

        self.plot_type: tk.IntVar = tk.IntVar(value=0)

        self.tabs: ttk.Notebook = None

        self.toggle_plotting_text: tk.StringVar = None
        self.toggle_plotting_btn: tk.Button = None

        self.live_plot_ui: PlotUI = None
        self.drill_plot_ui: PlotUI = None

        # configure grid layout weights
        self._ui.columnconfigure(0, weight=1)
        self._ui.columnconfigure(1, weight=1)
        self._ui.rowconfigure(0, weight=0)
        self._ui.rowconfigure(1, weight=0)
        self._ui.rowconfigure(2, weight=1)
        self._ui.rowconfigure(3, weight=0)

        row = 0
        label = ttk.Label(self._ui, text="Sensordaten Plotter", style='Heading.TLabel')
        # label = ttk.Label(self._ui, text="Data Plotter", style='Heading.TLabel')
        label.grid(column=0, row=row, pady=(20, 5), columnspan=2)

        row = row + 1
        radio_btn = ttk.Radiobutton(self._ui, text='Live Plot', value=0, variable=self.plot_type, command=self.refreshPlotType)
        radio_btn.grid(column=0, row=row, padx=20, pady=10)

        radio_btn = ttk.Radiobutton(self._ui, text='Bohrvorgang', value=1, variable=self.plot_type, command=self.refreshPlotType)
        radio_btn.grid(column=1, row=row, padx=20, pady=10)

        # plot uis
        row = row + 1
        self.tabs = ttk.Notebook(self._ui, style='Tabless.TNotebook')
        self.tabs.grid(column=0, row=row, padx=20, columnspan=2)

        self.live_plot_ui = LivePlotUI(self.tabs)
        self.drill_plot_ui = DrillProcedurePlotUI(self.tabs)

        self.tabs.add(self.live_plot_ui)
        self.tabs.add(self.drill_plot_ui)

        # controls
        row = row + 1
        btn_row = tk.Frame(self._ui)

        self.toggle_plotting_text = tk.StringVar(value='Plotten Pausieren')
        self.toggle_plotting_btn = ttk.Button(btn_row, textvariable=self.toggle_plotting_text, command = self.togglePlotting, padding='20 15')
        self.toggle_plotting_btn.grid(column=1, row=0, padx=20)

        btn_row.grid(column=0, row=row, pady=20, columnspan=2)

        # register model listeners
        self.model.addListener('state_changed', self.onStateChange)
        self.model.addListener('pausing_changed', self.onPausingChange)
        self.model.addListener('measurement_data_changed', self.onMeasurementDataChange)
    

    def shutdown(self) -> None:
        """
        Shutdown this application.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        super().shutdown()
    
        # unregister model listeners
        self.model.removeListener('state_changed', self.onStateChange)
        self.model.removeListener('pausing_changed', self.onPausingChange)
        self.model.removeListener('measurement_data_changed', self.onMeasurementDataChange)


    def onStateChange(self) -> None:
        """
        Handler method for model state changes.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.tabs.select(0 if self.model.getState() == ApplicationState.LIVE_PLOT else 1)


    def onPausingChange(self) -> None:
        """
        Handler method for model state changes.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.toggle_plotting_text.set('Plotten Fortsetzen' if self.model.isPausing() else 'Plotten Pausieren')


    def onMeasurementDataChange(self) -> None:
        """
        Handler method for model state changes.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        if self.model.getState() == ApplicationState.LIVE_PLOT:
            self.live_plot_ui.update(self.model.getMeasurementData())
        else:
            self.drill_plot_ui.update(self.model.getMeasurementData())


    def refreshPlotType(self):
        """
        Update plot type of model.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.model.setState(ApplicationState.LIVE_PLOT if self.plot_type.get() == 0 else ApplicationState.DRILL_PROCEDURE_PLOT)


    def togglePlotting(self):
        """
        Toggle (enable / disable) internal processing of incoming sensor data.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.model.setPausing(not self.model.isPausing())



class PlotUI(tk.Frame):
    """
    Base class for plot ui components.
    """

    def __init__(self, parent: tk.Widget) -> None:
        """
        Default constructor.

        Parameters
        ----------
        parent : Widget
            The parent widget.
        """

        tk.Frame.__init__(self, parent)
        # super().__init__(parent)


    def update(self, data: np.ndarray) -> None:
        """
        Update sensor data buffer.

        Parameters
        ----------
        data : ndarray
            The new sensor data.

        Returns
        -------
        None
        """

        pass



class LivePlotUI(PlotUI):
    """
    UI component for plotting live sensor data.
    """

    def __init__(self, parent: tk.Widget, canvas_width: int = 5000) -> None:
        """
        Default constructor.

        Parameters
        ----------
        parent : Widget
            The parent Widget.
        """
        
        PlotUI.__init__(self, parent)
        # super().__init__(parent)

        self.colors: list[str] = ['red', 'green', 'blue']

        self.canvas: tk.Canvas = tk.Canvas(self, width=canvas_width, height=100, bg='#eeeeee')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.draw_ttl: int = 0


    def update(self, data: np.ndarray) -> None:
        """
        Update sensor data buffer.

        Parameters
        ----------
        data : ndarray
            The new sensor data.

        Returns
        -------
        None
        """

        # only draw every nth processing call
        self.draw_ttl += 1
        if self.draw_ttl % 10 == 0:
            # remove all lines
            self.canvas.delete(tk.ALL)

            # scale data for plotting
            canvas_height_2 = int(self.canvas.winfo_height() / 2)
            scale = canvas_height_2 / -30
            scaled_data = data * scale + canvas_height_2 * 1.5

            # draw new lines
            c_data = np.empty((data.shape[0] * 2, ), dtype = data.dtype)
            c_data[0::2] = np.linspace(0, int(self.canvas.winfo_width()), data.shape[0])
            for c_idx in range(scaled_data.shape[1]):
                c_data[1::2] = scaled_data[:, c_idx]
                self.canvas.create_line(*c_data, fill = self.colors[c_idx])



class DrillProcedurePlotUI(PlotUI):
    """
    UI component for plotting drill procedure data.
    """

    def __init__(self, parent: tk.Widget) -> None:
        """
        Default constructor.

        Parameters
        ----------
        parent : Widget
            The parent Widget.
        """

        PlotUI.__init__(self, parent)
        # super().__init__(parent)

        self.fig = None
        self.ax = None
        self.canvas = None

        self.fig, self.ax = plt.subplots(dpi=100)

        self.canvas = tkagg.FigureCanvasTkAgg(self.fig, self)
        self.toolbar = tkagg.NavigationToolbar2Tk(self.canvas, self)

        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.toolbar.update()


    def update(self, data: np.ndarray):
        """
        Update sensor data buffer.

        Parameters
        ----------
        data : ndarray
            The new sensor data.

        Returns
        -------
        None
        """
        
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
