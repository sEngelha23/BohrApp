from .plugin_descriptor import MLDOGApplicationDescription, DataSourceWizardDescription
# from .ui.wizard import Wizard

from .ui.universal_data_source_wizards import DummyDataSourceWizard, LogDataSourceWizard, UDPDataSourceWizard#, PredictionWizard
from .plugins.plot.drill_plot_app import DrillPlotApplication
from .plugins.example.drill_example_app import DrillExampleApplication
from .plugins.capture.drill_capture_app import DrillCaptureApplication
from .plugins.example.drill_own_app import DrillOwnApplication



class MLDOGContext:
    """
    Base class for application context specifications.
    """
    
    def __init__(self, name: str):
        """
        Construct a new application context instance.

        Parameters
        ----------
        name : str
            The context name.
        """

        self.name: str = name

        self.ds_wizards: list[DataSourceWizardDescription] = []
        self.apps: list[MLDOGApplicationDescription] = []

    def getName(self) -> str:
        """
        Retrieve the application context name.

        Parameters
        ----------
        None

        Returns
        -------
        name : str
            The name of the application context.
        """

        return self.name

    def registerDataSourceWizard(self, wizard_cls: type, name: str = '') -> None:
        """
        Register a new data source wizard instance to this context.

        Parameters
        ----------
        wizard : type
            The wizard plugin class name (type) to register.
        name : str
            The name of the data source wizard plugin.
        
        Returns
        -------
        None
        """

        self.ds_wizards.append(DataSourceWizardDescription(wizard_cls, name))

    def registerApplication(self, app_cls: type, name: str = '') -> None:
        """
        Register a new application plugin class to this context.

        Parameters
        ----------
        app_cls : type
            The application plugin class name (type) to register.
        name : str
            The name of the application plugin.

        Returns
        -------
        None
        """
        self.apps.append(MLDOGApplicationDescription(app_cls, name))



class DefaultDrillContext(MLDOGContext):
    """
    The default drill context specification.
    """
    
    def __init__(self):
        super().__init__('Bohrer')

        # specify data source wizards
        self.registerDataSourceWizard(UDPDataSourceWizard, 'UDP Data Source')
        self.registerDataSourceWizard(LogDataSourceWizard, 'Log Data Source')
        self.registerDataSourceWizard(DummyDataSourceWizard, 'Dummy Data Source')
        #self.registerDataSourceWizard(PredictionWizard, 'Prediction Material')

        # specify application plugins
        self.registerApplication(DrillPlotApplication, 'Sensordaten Plotter')
        self.registerApplication(DrillCaptureApplication, 'Datenaufzeichnung')
        self.registerApplication(DrillExampleApplication, 'Beispielanwendung')
        self.registerApplication(DrillOwnApplication, 'Vorhersage')

        

