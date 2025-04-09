import tkinter as tk
from tkinter import ttk

from ..model.core import Core


class MLDOGApplication():
    """
    Base class for application plugins for the MLDOG application framework.
    """

    def __init__(self, name: str, core: Core, parent: tk.Widget):
        """
        Default application plugin constructor.

        Parameters
        ----------
        name : str
            The name of the application.
        core : Core
            The application framework core model.
        parent : Widget
            The parent widget.
        """
        
        super().__init__()

        self._name: str = name
        self._core: Core = core

        self._ui: tk.Widget = tk.Frame(parent)
        self._ui.configure(background='white')

    def getName(self) -> str:
        """
        Retrieve the name of the application.

        Parameters
        ----------
        None

        Returns
        -------
        name : str
            The name of the application.
        """

        return self._name
    

    def getUI(self) -> tk.Widget:
        """
        Retrieve the ui component of the application.

        Parameters
        ----------
        None

        Returns
        -------
        ui : Widget
            The ui component of the application.
        """

        return self._ui
    

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

        # unregister possibly active application components
        self._core.setTask()
