import tkinter as tk
from tkinter import ttk

from .model.core import Core
from .ui.application import MLDOGApplication
from .ui.wizard import Wizard



class PluginDescription():
    """
    Base class for plugin descriptions.
    """

    def __init__(self, cls: type, name: str = ''):
        """
        Default constructor.
        """

        self.cls = cls
        self.name = name

    def getName(self) -> str:
        """
        Retrieve the plugin name.

        Parameters
        ----------
        None

        Returns
        -------
        name : str
            The name of the plugin.
        """

        return self.name

    def create(self) -> object:
        """
        Create a new instance of the plugin.

        Parameters
        ----------
        None

        Returns
        -------
        app : object
            A new instance of the plugin.
        """

        return self.cls()



class MLDOGApplicationDescription(PluginDescription):
    """
    Simple factory class for representing an application plugin within the application framework.
    """

    def __init__(self, cls: type, name: str = ''):
        """
        Default constructor.
        """

        PluginDescription.__init__(self, cls, name)
        # super().__init__(cls, name)

    def create(self, core: Core, parent: tk.Frame) -> MLDOGApplication:
        """
        Create a new instance of the plugin.

        Parameters
        ----------
        name : Core
            The application framework core model.
        parent : Frame
            The parent frame.
        
        Returns
        -------
        app : MLDOGApplication
            A new instance of the application plugin.
        """

        return self.cls(core, parent)



class DataSourceWizardDescription(PluginDescription):
    """
    Simple factory class for representing an data source wizard plugin within the application framework.
    """

    def __init__(self, cls: type, name: str = ''):
        """
        Default constructor.
        """
        
        PluginDescription.__init__(self, cls, name)
        # super().__init__(cls, name)

    def create(self) -> Wizard:
        """
        Create a new instance of the data source wizard plugin.

        Parameters
        ----------
        None
        
        Returns
        -------
        wizard : Wizard
            A new instance of the data source wizard plugin.
        """

        return self.cls()
