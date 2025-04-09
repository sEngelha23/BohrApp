import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd

import numpy as np
import pandas as pd
from enum import Enum

import os
import itertools
import datetime

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from ...model.core import Core
from ...ui.application import MLDOGApplication

from .drill_capture_model import ApplicationState, MeasurementSeries, DrillCaptureModel



class DrillCaptureApplication(MLDOGApplication):
    """
    The Drill-Capture-Application used to capture drill sensor data.
    """

    def __init__(self, core: Core, parent: tk.Frame):
        MLDOGApplication.__init__(self, 'Datenaufzeichnung', core, parent)
        # super().__init__('Datenaufzeichnung', core, parent)

        self.model: DrillCaptureModel = DrillCaptureModel(core)

        # override default Frame ui component of application with notebook
        self._ui = ttk.Notebook(parent, style='Tabless.TNotebook')

        # ---------- setup ui components
        self.config_ui: MeasurementSeriesConfigurator = MeasurementSeriesConfigurator(self._ui, self.model)
        self.recorder_ui: MeasurementSeriesRecorder = MeasurementSeriesRecorder(self._ui, self.model)
        self.confirm_dialog: ConfirmMeasurementDialog = ConfirmMeasurementDialog(parent.winfo_toplevel(),
                                                       lambda: self.model.storeMeasurement(),
                                                       lambda: self.model.discardMeasurement())

        self._ui.add(self.config_ui)
        self._ui.add(self.recorder_ui)

        # setup event listeners
        self.model.addListener('state_changed', self.onStateChange)
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

        # unregister event listeners
        self.model.removeListener('state_changed', self.onStateChange)
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

        self._ui.select(0 if self.model.getState() == ApplicationState.CONFIGURE else 1)


    def onMeasurementDataChange(self) -> None:
        """
        Method for handling new drill data of the model.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        
        if self.model.hasMeasurementData():
            self.confirm_dialog.show(self.model.getMeasurementData())



class MeasurementSeriesConfigurator(tk.Frame):
    """
    Measurement series configurator ui component.
    """

    def __init__(self, parent: tk.Widget, model: DrillCaptureModel) -> None:
        """
        Default constructor.

        Parameters
        ----------
        parent : Widget
            The parent widget.
        """

        super().__init__(parent)

        self.model: DrillCaptureModel = model

        self.operators: tk.StringVar = tk.StringVar(value='Operator 1, Operator 2')
        self.materials: tk.StringVar = tk.StringVar(value='holz-eiche')
        self.drill_sizes: tk.StringVar = tk.StringVar(value='6')
        self.gears: tk.StringVar = tk.StringVar(value='2')
        self.n_recordings: tk.IntVar = tk.IntVar(value=10)
        self.target_dir: tk.StringVar = tk.StringVar(value='recordings')

        self.start_recording_btn: tk.Button = None
        self.continue_recording_btn: tk.Button = None

        self.setupUI()
    

    def setupUI(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=0)

        # title label
        row = 0
        label = ttk.Label(self, text="Messreihenkonfigurator", style='Heading.TLabel')
        # label = ttk.Label(self, text="Measurement series Configurator", style='Heading.TLabel')
        label.grid(column=0, row=row, pady=20)


        # config pane
        row = row + 1
        config_pane = ttk.LabelFrame(self, text = "Messreihe", style='Heading.TLabelframe')
        # config_pane = ttk.LabelFrame(self, text = "Measurement Series")
        config_pane.columnconfigure(0, weight=1)
        config_pane.columnconfigure(1, weight=1)
        config_pane.columnconfigure(2, weight=1)
        config_pane.columnconfigure(3, weight=1)
        config_pane.rowconfigure(0, weight=0)
        config_pane.rowconfigure(1, weight=0)
        config_pane.rowconfigure(2, weight=0)
        config_pane.rowconfigure(3, weight=0)
        config_pane.rowconfigure(4, weight=0)
        config_pane.rowconfigure(5, weight=0)
        config_pane.grid(column=0, row=row, padx=20, pady=10, sticky=tk.NSEW)

        # operators
        c_row = 0
        label = ttk.Label(config_pane, text='Benutzer:', style='Label.TLabel')
        # label = ttk.Label(config_pane, text='Operators:', style='Label.TLabel')
        label.grid(column=0, row=c_row, padx=(20, 5), pady=10, sticky=tk.E)

        operators_input = ttk.Entry(config_pane, textvariable = self.operators)
        operators_input.grid(column=1, row=c_row, padx=(5, 20), pady=10, ipady=3, sticky = tk.NSEW, columnspan=3)

        # materials
        c_row = c_row + 1
        label = ttk.Label(config_pane, text='Materialien:', style='Label.TLabel')
        # label = ttk.Label(config_pane, text='Materials:', style='Label.TLabel')
        label.grid(column=0, row=c_row, padx=(20, 5), pady=10, sticky=tk.E)

        materials_input = ttk.Entry(config_pane, textvariable = self.materials)
        materials_input.grid(column=1, row=c_row, padx=(5, 20), pady=10, ipady=3, sticky = tk.NSEW, columnspan=3)

        # drill sizes
        c_row = c_row + 1
        label = ttk.Label(config_pane, text='Bohrergrößen (mm):', style='Label.TLabel')
        # label = ttk.Label(config_pane, text='Drill Size (mm):', style='Label.TLabel')
        label.grid(column=0, row=c_row, padx=(20, 5), pady=10, sticky=tk.E)

        drill_size_input = ttk.Entry(config_pane, textvariable = self.drill_sizes)
        drill_size_input.grid(column=1, row=c_row, padx=(5, 20), pady=10, ipady=3, sticky = tk.NSEW, columnspan=3)

        # gears
        c_row = c_row + 1
        label = ttk.Label(config_pane, text='Gänge:', style='Label.TLabel')
        # label = ttk.Label(self, text='Transmissions:', style='Label.TLabel')
        label.grid(column=0, row=c_row, padx=(20, 5), pady=10, sticky=tk.E)

        radio_btn = ttk.Radiobutton(config_pane, text='Gear 1', value='1', variable=self.gears)
        radio_btn.grid(column=1, row=c_row, padx=(5, 20), pady=10, sticky = tk.NSEW)

        radio_btn = ttk.Radiobutton(config_pane, text='Gear 2', value='2', variable=self.gears)
        radio_btn.grid(column=2, row=c_row, padx=(5, 20), pady=10, sticky = tk.NSEW)

        radio_btn = ttk.Radiobutton(config_pane, text='Both', value='1,2', variable=self.gears)
        radio_btn.grid(column=3, row=c_row, padx=(5, 20), pady=10, sticky = tk.NSEW)

        # number of recordings
        c_row = c_row + 1
        label = ttk.Label(config_pane, text='Anzahl Aufnahmen:', style='Label.TLabel')
        # label = ttk.Label(config_pane, text='Num. Recordings:', style='Label.TLabel')
        label.grid(column=0, row=c_row, padx=(20, 5), pady=10, sticky=tk.E)

        n_recordings_box = ttk.Spinbox(config_pane, from_=1, to=100, textvariable=self.n_recordings)
        n_recordings_box.grid(column=1, row=c_row, padx=(5, 20), pady=10, ipady=3, sticky = tk.EW, columnspan=3)

        # TODO: Add result_dir entry

        # note
        c_row = c_row + 1
        label = ttk.Label(config_pane, text='Hinweis:', style='Label.TLabel')
        # label = ttk.Label(config_pane, text='Note:', style='Label.TLabel')
        label.grid(column=0, row=c_row, padx=(20, 5), pady=10, sticky=tk.E)

        label = ttk.Label(config_pane, text='Mehrfacheinträge per Komma trennen.')
        # label = ttk.Label(config_pane, text='Note: Use comma separated values for multiple entries.')
        label.grid(column=1, row=c_row, padx=(5, 20), pady=10, sticky=tk.W, columnspan=3)

        # separator
        row = row + 1
        sep = ttk.Separator(self, orient=tk.HORIZONTAL)
        sep.grid(column=0, row=row, sticky = (tk.EW, tk.S))

        # ---------- bottom controls
        row = row + 1
        btn_row = tk.Frame(self)

        self.start_recording_btn = ttk.Button(btn_row, text='Aufzeichnung Starten', command = self.startRecording, padding='20 15')
        self.start_recording_btn.grid(column=0, row=0, padx=20)

        self.continue_recording_btn = ttk.Button(btn_row, text='Messreihe Fortsetzen', command = self.continueRecording, padding='20 15')
        self.continue_recording_btn.grid(column=1, row=0, padx=20)

        btn_row.grid(column=0, row=row, pady=20)


    def startRecording(self) -> None:
        """
        Event handler method for start-recording button.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.model.generateMeasurementSeries(self.getMeasurementSeriesConfig(),
                                             self.n_recordings.get(),
                                             self.target_dir.get())
        self.model.startCapturing()


    def continueRecording(self) -> None:
        """
        Event handler method for continue recording button.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # show open dialog to select a measurement series directory
        ms_dir = fd.askdirectory(initialdir='./recordings')

        if len(ms_dir) > 0:
            self.model.openMeasurementSeries(ms_dir)
            self.model.startCapturing()
    

    def getMeasurementSeriesConfig(self) -> dict:
        """
        Retrieve a measurement series configuration as a dictionary with categories as keys and possible values as list of values.

        Parameters
        ----------
        None

        Returns
        -------
        m_series_config : dict
            The currently configured measurement configuration.
        """

        return {
            'operator': [o.strip() for o in self.operators.get().split(',')],
            'material': [m.strip() for m in self.materials.get().split(',')],
            'drillSize': [float(s.strip()) for s in self.drill_sizes.get().split(',')],
            'drillType': ['universal'],
            'transmission': [int(g) for g in self.gears.get().split(',')],
            'sampleRate': ['96000']
        }



class MeasurementSeriesRecorder(ttk.Frame):
    """
    Measurement series recorder ui component.
    """

    def __init__(self, parent: tk.Widget, model: DrillCaptureModel) -> None:
        """
        Default constructor.

        Parameters
        ----------
        parent : Widget
            The parent widget.
        """

        super().__init__(parent)

        self.model: DrillCaptureModel = model

        self.measurement: tk.StringVar = tk.StringVar(value='n/a')
        self.operator: tk.StringVar = tk.StringVar(value='n/a')
        self.material: tk.StringVar = tk.StringVar(value='n/a')
        self.drill_size: tk.StringVar = tk.StringVar(value='n/a')
        self.drill_type: tk.StringVar = tk.StringVar(value='n/a')
        self.gear: tk.StringVar = tk.StringVar(value='n/a')

        self.status_info: tk.StringVar = tk.StringVar(value='Preparation')
        self.status_description: tk.StringVar = tk.StringVar(value='Bereiten Sie die Bohrmaschine für die angezeigte Messung vor.')
        self.toggle_preparation_text: tk.StringVar = tk.StringVar(value='Aufzeichnung Fortsetzen')

        self.stop_recording_btn: tk.Button = None
        self.toggle_preparation_btn: tk.Button = None

        self.setupUI()

        self.model.addListener('measurement_index_changed', self.refreshMeasurementInfo)
        self.model.addListener('measurement_series_changed', self.refreshMeasurementInfo)
        self.model.addListener('pausing_changed', self.refreshStatusInfo)
    

    def setupUI(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=0)

        # title label
        row = 0
        label = ttk.Label(self, text="Messreihenrecorder", style='Heading.TLabel')
        label.grid(column=0, row=row, pady=20)


        # info pane
        row = row + 1
        info_pane = ttk.LabelFrame(self, text = "Aktuelle Messung", style='Heading.TLabelframe')
        # info_pane = ttk.LabelFrame(self, text = "Current Measurement")
        info_pane.columnconfigure(0, weight=1)
        info_pane.columnconfigure(1, weight=3)
        info_pane.rowconfigure(0, weight=0)
        info_pane.rowconfigure(1, weight=0)
        info_pane.rowconfigure(2, weight=0)
        info_pane.rowconfigure(3, weight=0)
        info_pane.rowconfigure(4, weight=0)
        info_pane.rowconfigure(5, weight=0)
        info_pane.rowconfigure(6, weight=1)
        info_pane.grid(column=0, row=row, padx=20, pady=10, sticky=tk.NSEW)

        # measurement id
        mi_row = 0
        label = ttk.Label(info_pane, text='Messungs-ID:', style='Label.TLabel')
        # label = ttk.Label(info_pane, text='Measurement ID.:', style='Label.TLabel')
        label.grid(column=0, row=mi_row, padx=(20, 5), pady=10, sticky=tk.E)

        label = ttk.Label(info_pane, textvariable = self.measurement, style='Normal.TLabel')
        label.grid(column=1, row=mi_row, padx=(5, 20), pady=10, sticky=tk.W)

        # operator
        mi_row = mi_row + 1
        label = ttk.Label(info_pane, text='Benutzer:', style='Label.TLabel')
        # label = ttk.Label(info_pane, text='Operator:', style='Label.TLabel')
        label.grid(column=0, row=mi_row, padx=(20, 5), pady=10, sticky=tk.E)

        label = ttk.Label(info_pane, textvariable = self.operator, style='Highlight.TLabel')
        label.grid(column=1, row=mi_row, padx=(5, 20), pady=10, sticky=tk.W)

        # material
        mi_row = mi_row + 1
        label = ttk.Label(info_pane, text='Material:', style='Label.TLabel')
        # label = ttk.Label(info_pane, text='Material:', style='Label.TLabel')
        label.grid(column=0, row=mi_row, padx=(20, 5), pady=10, sticky=tk.E)

        label = ttk.Label(info_pane, textvariable = self.material, style='Highlight.TLabel')
        label.grid(column=1, row=mi_row, padx=(5, 20), pady=10, sticky=tk.W)

        # drill size
        mi_row = mi_row + 1
        label = ttk.Label(info_pane, text='Bohrergröße (mm):', style='Label.TLabel')
        # label = ttk.Label(info_pane, text='Drill Size (mm):', style='Label.TLabel')
        label.grid(column=0, row=mi_row, padx=(20, 5), pady=10, sticky=tk.E)

        label = ttk.Label(info_pane, textvariable = self.drill_size, style='Highlight.TLabel')
        label.grid(column=1, row=mi_row, padx=(5, 20), pady=10, sticky=tk.W)

        # drill type
        mi_row = mi_row + 1
        label = ttk.Label(info_pane, text='Bohrertyp:', style='Label.TLabel')
        # label = ttk.Label(info_pane, text='Drill Type:', style='Label.TLabel')
        label.grid(column=0, row=mi_row, padx=(20, 5), pady=10, sticky=tk.E)

        label = ttk.Label(info_pane, textvariable = self.drill_type, style='Highlight.TLabel')
        label.grid(column=1, row=mi_row, padx=(5, 20), pady=10, sticky=tk.W)

        # transmission
        mi_row = mi_row + 1
        label = ttk.Label(info_pane, text='Gang:', style='Label.TLabel')
        # label = ttk.Label(info_pane, text='Transmission:', style='Label.TLabel')
        label.grid(column=0, row=mi_row, padx=(20, 5), pady=10, sticky=tk.E)

        label = ttk.Label(info_pane, textvariable = self.gear, style='Highlight.TLabel')
        label.grid(column=1, row=mi_row, padx=(5, 20), pady=10, sticky=tk.W)


        # status pane
        row = row + 1
        status_pane = ttk.LabelFrame(self, text = "Recorder Status", style='Heading.TLabelframe')
        # status_pane = ttk.LabelFrame(self, text = "Recorder State")
        status_pane.columnconfigure(0, weight=0)
        status_pane.columnconfigure(1, weight=3)
        status_pane.rowconfigure(0, weight=0)
        status_pane.rowconfigure(1, weight=0)
        status_pane.rowconfigure(2, weight=0)
        status_pane.grid(column=0, row=row, padx=20, pady=10, sticky=tk.NSEW)

        # ---------- status info
        s_row = 0
        label = ttk.Label(status_pane, text='Status:', style='Label.TLabel')
        # label = ttk.Label(status_pane, text='State:', style='Label.TLabel')
        label.grid(column=0, row=s_row, padx=(20, 5), pady=10, sticky=tk.E)

        label = ttk.Label(status_pane, textvariable = self.status_info, style='Highlight.TLabel')
        label.grid(column=1, row=s_row, padx=(5, 20), pady=10, sticky=tk.W)

        s_row = s_row + 1
        label = ttk.Label(status_pane, text='Aktion:', style='Label.TLabel')
        # label = ttk.Label(status_pane, text='Action:', style='Label.TLabel')
        label.grid(column=0, row=s_row, padx=(20, 5), pady=10, sticky=tk.E)
        
        label = ttk.Label(status_pane, textvariable = self.status_description, style='Highlight.TLabel')
        label.grid(column=1, row=s_row, padx=(5, 20), pady=10, sticky=tk.W)

        # s_row = s_row + 1
        # self.toggle_preparation_btn = ttk.Button(status_pane, textvariable=self.toggle_preparation_text, command = self.togglePreparation, padding='20 15')
        # self.toggle_preparation_btn.grid(column=0, row=s_row, padx=20, pady=10, columnspan=2)

        # separator
        row = row + 1
        sep = ttk.Separator(self, orient=tk.HORIZONTAL)
        sep.grid(column=0, row=row, sticky = (tk.EW, tk.S), columnspan=4)

        # ---------- bottom controls
        row = row + 1
        btn_row = tk.Frame(self)

        self.stop_recording_btn = ttk.Button(btn_row, text='Aufzeichnung Abbrechen', command = self.stopRecording, padding='20 15')
        self.stop_recording_btn.grid(column=0, row=0, padx=20)

        self.toggle_preparation_btn = ttk.Button(btn_row, textvariable=self.toggle_preparation_text, command = self.togglePreparation, padding='20 15')
        self.toggle_preparation_btn.grid(column=1, row=0, padx=20)

        btn_row.grid(column=0, row=row, pady=20)


    def refreshMeasurementInfo(self) -> None:
        """
        Update ui controls with the current measurement information.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        if self.model.getNumberOfRemainingMeasurements() > 0:
            m_idx = self.model.getMeasurementIndex()
            m_series = self.model.getMeasurementSeries()
            m_config = m_series.getMeasurementConfig(m_idx)
            n_recordings = m_series.getNumberOfMeasurements()

            self.measurement.set(f'{m_idx+1} / {n_recordings}')
            self.operator.set(m_config['operator'])
            self.material.set(m_config['material'])
            self.drill_size.set(m_config['drillSize'])
            self.drill_type.set(m_config['drillType'])
            self.gear.set(m_config['transmission'])
        else:
            self.measurement.set('n/a')
            self.operator.set('n/a')
            self.material.set('n/a')
            self.drill_size.set('n/a')
            self.drill_type.set('n/a')
            self.gear.set('n/a')


    def refreshStatusInfo(self) -> None:
        """
        Update status information.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.status_info.set('Preparation' if self.model.isPausing() else 'Active')
        self.status_description.set('Bereiten Sie die Bohrmaschine für die angezeigte Messung vor.' if self.model.isPausing() else 'Führen Sie die angezeigte Messung durch.')
        self.toggle_preparation_text.set('Aufzeichnung Fortsetzen' if self.model.isPausing() else 'Aufzeichnung Pausieren')

    def stopRecording(self) -> None:
        """
        Event handler method for stop-recording button.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.model.stopCapturing()


    def togglePreparation(self) -> None:
        """
        Event handler method for toggle preparation button.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.model.setPausing(not self.model.isPausing())



class ConfirmMeasurementDialog():
    """
    Confirm Measurement Dialog.
    """

    def __init__(self, win: tk.Toplevel, onConfirm: callable, onDiscard: callable = None) -> None:
        """
        Default constructor.

        Parameters
        ----------
        win : Toplevel
            The Toplevel window component.
        """

        self.win: tk.Toplevel = win
        self.on_confirm: callable = onConfirm
        self.on_discard: callable = onDiscard

        self.dialog: tk.Toplevel = None
        self.fig = None
    

    def close(self) -> None:
        """
        Close confirm dialog.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # close figure and dialog
        plt.close(self.fig)
        self.dialog.destroy()

        # clear references
        self.dialog = None
        self.fig = None
    

    def show(self, drill_data: np.ndarray) -> None:
        """
        Show confirm dialog for the given drill data.

        Parameters
        ----------
        drill_data : np.ndarray
            The drill data to confirm.

        Returns
        -------
        None
        """

        if self.dialog is None:
            self.dialog = tk.Toplevel(self.win)

            # set dialog title
            self.dialog.title("Neue Bohrung")

            # set dialog dimensions
            width = 700
            height = 500

            x = self.win.winfo_x() + self.win.winfo_width() // 2 - width // 2
            y = self.win.winfo_y() + self.win.winfo_height() // 2 - height // 2
            self.dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))

            # configure layout
            self.dialog.columnconfigure(0, weight=1)
            self.dialog.rowconfigure(1, weight=1)

            # add title label
            label = tk.Label(self.dialog, text="Neue Bohrung", font=(None, 14))
            label.grid(column=0, row=0, pady=20)

            # add figure and plotcanvas
            self.fig = plt.figure(figsize=(16, 9), dpi=100)
            ax = self.fig.add_subplot(1, 1, 1)

            xVals = np.arange(len(drill_data))
            line, = ax.plot(xVals, drill_data[:, 0])
            line, = ax.plot(xVals, drill_data[:, 1])
            line, = ax.plot(xVals, drill_data[:, 2])
            
            ax.legend(['Ton', 'Spannung', 'Strom'])
            ax.grid()

            plotcanvas = FigureCanvasTkAgg(self.fig, self.dialog)
            plotcanvas.get_tk_widget().grid(column=0, row=1, pady=20)

            # add button row
            btnRow = tk.PanedWindow(self.dialog, orient=tk.HORIZONTAL, sashpad=20)

            button = ttk.Button(btnRow, text='Übernehmen', command = self.confirm, padding='30 20')
            btnRow.add(button)

            button = ttk.Button(btnRow, text='Verwerfen', command = self.discard, padding='30 20')
            btnRow.add(button)

            btnRow.grid(column=0, row=2, pady=20)

            # general window settings
            self.dialog.protocol('WM_DELETE_WINDOW', lambda: self.on_discard())

            # grab focus
            self.dialog.focus_set() # take over input focus,
            self.dialog.grab_set() # disable other windows while I'm open,
            self.dialog.wait_window() # and wait here until win destroyed
        else:
            # clear axes
            ax = self.fig.axes[0]
            ax.clear()

            # plot data
            xVals = np.arange(len(drill_data))
            line, = ax.plot(xVals, drill_data[:, 0])
            line, = ax.plot(xVals, drill_data[:, 1])
            line, = ax.plot(xVals, drill_data[:, 2])
            
            ax.legend(['Ton', 'Spannung', 'Strom'])
            ax.grid()
    

    def confirm(self) -> None:
        """
        Handle confirm action.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # close dialog
        self.close()

        # forward discard event
        if self.on_confirm is not None:
            self.on_confirm()
    

    def discard(self) -> None:
        """
        Handle discard action.

        Parameters
        ----------
        drill_data : np.ndarray
            The drill data to confirm.

        Returns
        -------
        None
        """

        # close dialog
        self.close()

        # forward discard event
        if self.on_discard is not None:
            self.on_discard()
