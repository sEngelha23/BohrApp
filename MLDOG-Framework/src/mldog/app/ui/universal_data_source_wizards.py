import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import threading
from ..tasks.drill_procedure_detector_task import DrillProcedureDetectorTask
from os.path import exists
from ..model.pipeline import MaterialClassifier
from ..model.universal_data_sources import DummyDataSource, LogDataSource, UDPDataSource
from .wizard import Wizard
from ..model.core import Core
from ..ui.application import MLDOGApplication


class UDPDataSourceWizard(Wizard):
    """
    Wizard for creating a new UDP data source.
    """

    def __init__(self):
        super().__init__('UDP Data Source', 'New UDP Data Source')

        self.capturame_ip = None
    

    def constructWizardPane(self) -> tk.Frame:
        # initialize parameter
        if self.capturame_ip is None:
            self.capturame_ip = tk.StringVar(value='localhost')

        # panel container
        config_pane = ttk.LabelFrame(self.wizard, text = "Capturama")
        config_pane.columnconfigure(0, weight=0)
        config_pane.columnconfigure(1, weight=1)
        config_pane.rowconfigure(0, weight=0)
        config_pane.rowconfigure(1, weight=1)

        # capturama ip
        label = ttk.Label(config_pane, text='IP:')
        label.grid(column=0, row=0, padx=(20, 5), pady=10, sticky=tk.E)

        ip_input = ttk.Entry(config_pane, textvariable = self.capturame_ip)
        ip_input.grid(column=1, row=0, padx=(5, 20), pady=10, sticky=(tk.E, tk.W))

        return config_pane


    def finish(self):
        super().finish()
        
        self.core.setDataSource(UDPDataSource(capturama_ip = self.capturame_ip.get()))



class LogDataSourceWizard(Wizard):
    """
    Wizard for creating a new log file data source.
    """

    def __init__(self):
        super().__init__('Log Data Source', 'New Log Data Source')

        self.path = None
        self.frequency = None
        self.block_size = None
    

    def constructWizardPane(self) -> tk.Frame:
        # initialize parameter
        if self.path is None:
            self.path = tk.StringVar(value='../data' if exists('../data') else './data')
            self.frequency = tk.IntVar(value=96000)
            self.block_size = tk.IntVar(value=480)

        # panel container
        # config_pane = ttk.Frame(self.wizard)
        config_pane = ttk.LabelFrame(self.wizard, text = "Log Player Properties")
        config_pane.columnconfigure(0, weight=0)
        config_pane.columnconfigure(1, weight=1)
        config_pane.columnconfigure(2, weight=0)
        config_pane.rowconfigure(0, weight=0)
        config_pane.rowconfigure(1, weight=0)
        config_pane.rowconfigure(2, weight=0)
        config_pane.rowconfigure(3, weight=1)

        # path
        label = ttk.Label(config_pane, text='Path:')
        label.grid(column=0, row=0, padx=(20, 5), pady=10, sticky=tk.E)

        path_input = ttk.Entry(config_pane, textvariable = self.path)
        path_input.grid(column=1, row=0, padx=(5, 0), pady=10, sticky = (tk.N, tk.E, tk.S, tk.W))

        file_btn = ttk.Button(config_pane, text='...', command = self.selectDirectory)
        file_btn.grid(column=2, row=0, padx=(5, 20), pady=10, sticky = (tk.E, tk.W))

        # frequency
        label = ttk.Label(config_pane, text='Frequency:')
        label.grid(column=0, row=1, padx=(20, 5), pady=10, sticky=tk.E)

        frequency_box = ttk.Spinbox(config_pane, from_=1, to=96000, textvariable=self.frequency)
        frequency_box.grid(column=1, row=1, padx=(5, 20), pady=10, sticky = (tk.E, tk.W), columnspan=2)

        # block size
        label = ttk.Label(config_pane, text='Block Size:')
        label.grid(column=0, row=2, padx=(20, 5), pady=10, sticky=tk.E)

        block_size_box = ttk.Spinbox(config_pane, from_=1, to=96000, textvariable=self.block_size)
        block_size_box.grid(column=1, row=2, padx=(5, 20), pady=10, sticky = (tk.E, tk.W), columnspan=2)

        return config_pane
    

    def selectDirectory(self):
        dir = fd.askdirectory(initialdir=self.path.get())

        if len(dir) > 0:
            self.path.set(dir)


    def finish(self):
        super().finish()

        if exists(self.path.get()):
            self.core.setDataSource(LogDataSource(self.path.get(), self.block_size.get(), self.frequency.get()))
        else:
            print(f'The selected path: "{self.path.get()}" does not exist!')



class DummyDataSourceWizard(Wizard):
    """
    Wizard for creating a new dummy data source.
    """

    def __init__(self):
        super().__init__('Dummy Data Source', 'New Dummy Data Source')

        self.n_channels = None
        self.frequency = None
        self.block_size = None
    

    def constructWizardPane(self) -> tk.Frame:
        # initialize parameter
        if self.n_channels is None:
            self.n_channels = tk.IntVar(value=3)
            self.frequency = tk.IntVar(value=96000)
            self.block_size = tk.IntVar(value=480)

        # panel container
        config_pane = ttk.LabelFrame(self.wizard, text = "Dummy Data Properties")
        config_pane.columnconfigure(0, weight=0)
        config_pane.columnconfigure(1, weight=1)
        config_pane.rowconfigure(0, weight=0)
        config_pane.rowconfigure(1, weight=0)
        config_pane.rowconfigure(2, weight=0)
        config_pane.rowconfigure(3, weight=1)

        # channels
        label = ttk.Label(config_pane, text='Num. Channels:')
        label.grid(column=0, row=0, padx=(20, 5), pady=10, sticky=tk.E)

        channel_box = ttk.Spinbox(config_pane, from_=1, to=30, textvariable=self.n_channels)
        channel_box.grid(column=1, row=0, padx=(5, 20), pady=10, sticky = (tk.E, tk.W))

        # frequency
        label = ttk.Label(config_pane, text='Frequency:')
        label.grid(column=0, row=1, padx=(20, 5), pady=10, sticky=tk.E)

        frequency_box = ttk.Spinbox(config_pane, from_=1, to=96000, textvariable=self.frequency)
        frequency_box.grid(column=1, row=1, padx=(5, 20), pady=10, sticky = (tk.E, tk.W), columnspan=2)

        # block size
        label = ttk.Label(config_pane, text='Block Size:')
        label.grid(column=0, row=2, padx=(20, 5), pady=10, sticky=tk.E)

        block_size_box = ttk.Spinbox(config_pane, from_=1, to=96000, textvariable=self.block_size)
        block_size_box.grid(column=1, row=2, padx=(5, 20), pady=10, sticky = (tk.E, tk.W), columnspan=2)

        return config_pane


    def finish(self):
        super().finish()
        
        self.core.setDataSource(DummyDataSource(self.n_channels.get(), self.block_size.get(), self.frequency.get()))


# class PredictionWizard(Wizard, DrillProcedureDetectorTask, MLDOGApplication):
#     """
#     Wizard für die Vorhersage ohne Start-Button.
#     """
#     def __init__(self, core: Core):
#         super().__init__('Material Prediction', 'Predictor')
#         self.result = tk.StringVar(value="Predicting . . .")
#         self.event = threading.Event()
#         self.core.setTask(DrillProcedureDetectorTask(), self.wait_for_bohrung)
    

#     def constructWizardPane(self) -> tk.Frame:
#         config_pane = ttk.LabelFrame(self.wizard, text="Prediction")
#         config_pane.columnconfigure(0, weight=1)
#         config_pane.rowconfigure(0, weight=1)

#         self.label = ttk.Label(config_pane, textvariable=self.result, font=("Arial", 10))
#         self.label.grid(row=0, column=0, padx=20, pady=20)

#         threading.Thread(target=self.prediction2, daemon=True).start()
        
#         return config_pane


#     def wait_for_bohrung(self, data: object):
#         self.event.wait() 
#         if data:
#             self.predictionPrediction(data)


#     def predictionPrediction(self, result_data):
#         material = MaterialClassifier().predict1(result_data)
#         self.result.set(f'{material}')
#         self.event.set()