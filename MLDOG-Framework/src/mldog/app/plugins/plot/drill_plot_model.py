import numpy as np
import pandas as pd
from enum import Enum

from ...model.core import Core
from ...model.event_dispatcher import EventDispatcher

from ...tasks.drill_procedure_detector_task import DrillProcedureDetectorTask
from ...tasks.stream_task import StreamTask



class ApplicationState(Enum):
    LIVE_PLOT = 1
    DRILL_PROCEDURE_PLOT = 2



class DrillPlotModel(EventDispatcher):
    """
    The Drill-Plot-Application model.
    """

    def __init__(self, core: Core, buffer_size: int = 5000):
        """
        Create a plot model instance.

        Parameters
        ----------
        core : Core
            The core model instance.
        buffer_size : int
            The size of the measurement data buffer in live mode.
        """

        EventDispatcher.__init__(self)
        # super().__init__()

        self._core = core
        self._buffer_size = buffer_size
        self._state: ApplicationState = ApplicationState.LIVE_PLOT
        self._pause_processing = False
        self._measurement_data: np.ndarray = np.zeros((self._buffer_size, 3))

        self._core.setTask(StreamTask(), self.handleTaskResult)


    def getState(self) -> ApplicationState:
        """
        Retrieve the currently application state.

        Parameters
        ----------
        None

        Returns
        -------
        state : ApplicationState
            The current application state.
        """

        return self._state
    

    def isPausing(self) -> bool:
        """
        Check if processing of incoming task messages is currently paused.

        Parameters
        ----------
        None

        Returns
        -------
        pause_processing : bool
            True, if processing of incoming task messages is paused, False otherwise.
        """

        return self._pause_processing
    

    def getMeasurementData(self) -> np.ndarray:
        """
        Retrieve the buffered measurement data.

        Parameters
        ----------
        None

        Returns
        -------
        measurement_data : np.ndarray
            The buffered measurement data.
        """

        return self._measurement_data
    

    def reset(self) -> None:
        """
        Reset this model.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self._pause_processing = True
        self._measurement_data = None

        self._dispatchEvent('reset')
    

    def setState(self, new_state: ApplicationState) -> None:
        """
        Switch the application state.

        Parameters
        ----------
        new_state : ApplicationState
            The new application state to switch to.

        Returns
        -------
        None
        """

        if self._state != new_state:
            self._state = new_state

            if self._state == ApplicationState.LIVE_PLOT:
                self._measurement_data: np.ndarray = np.zeros((self._buffer_size, 3))
                self._core.setTask(StreamTask(), self.handleTaskResult)
            else:
                self._core.setTask(DrillProcedureDetectorTask(), self.handleTaskResult)

            # notify state change
            self._dispatchEvent('state_changed')
    

    def setPausing(self, pausing: bool) -> None:
        """
        Enable/Disable pausing of processing.

        Parameters
        ----------
        pausing : bool
            True, if processing of incoming task messages should be paused, False if not.

        Returns
        -------
        None
        """

        if self._pause_processing != pausing:
            self._pause_processing = pausing

            # notify pausing change
            self._dispatchEvent('pausing_changed')
    

    def handleTaskResult(self, msg: object) -> None:
        """
        Handler method for task result messages.

        Parameters
        ----------
        msg : object
            The message from the task.
        """
        
        if self.isPausing():
            # no processing in preparation mode
            return
        
        if type(msg) == np.ndarray:
            (n_points, nSignals) = msg.shape

            if self._state == ApplicationState.LIVE_PLOT:
                # update plotting buffer with new information
                self._measurement_data[0:self._buffer_size - n_points] = self._measurement_data[n_points:]
                self._measurement_data[self._buffer_size - n_points:, :] = msg[:, [1, 2, 0]]
            else:
                # store drill procedure data for further processing
                self._measurement_data = msg

            # notify measurement data change
            self._dispatchEvent('measurement_data_changed')
