import numpy as np
import pandas as pd
from enum import Enum

import os
import itertools
import datetime

from ...model.core import Core
from ...model.event_dispatcher import EventDispatcher

from ...tasks.drill_procedure_detector_task import DrillProcedureDetectorTask



class ApplicationState(Enum):
    CONFIGURE = 1
    CAPTURE = 2



class MeasurementSeries:
    """
    Class for representing a measurement series.
    """

    def __init__(self, measurements: pd.DataFrame, output_dir: str = './recordings') -> None:
        """
        Default constructor.
        """

        self.measurements: pd.DataFrame = measurements
        self.output_dir: str = output_dir
    

    def getNumberOfMeasurements(self) -> int:
        """
        Retrieve the amount of measurements.

        Parameters
        ----------
        None

        Returns
        -------
        n_measurements : int
            The number of measurements.
        """
        
        return 0 if self.measurements is None else self.measurements.shape[0]
    

    def getRemainingMeasurementIndices(self) -> int:
        """
        Retrieve the indices of remaining measurements.

        Parameters
        ----------
        None

        Returns
        -------
        remaining_indices : list[int]
            A list of remaining measurement indices.
        """

        empty_rows = self.measurements['dataFile'] == ''
        nan_rows = self.measurements['dataFile'].isna()
        remaining_idxs = empty_rows | nan_rows
        return remaining_idxs.index[remaining_idxs].to_list()
    

    def getNumberOfRemainingMeasurements(self) -> int:
        """
        Retrieve the amount of remaining measurements.

        Parameters
        ----------
        None

        Returns
        -------
        remaining : int
            The number of remaining measurements.
        """

        return len(self.getRemainingMeasurementIndices())
    

    def getNextMeasurementIndex(self) -> int:
        """
        Retrieve the indices of the next measurement.

        Parameters
        ----------
        None

        Returns
        -------
        remaining_indices : list[int]
            The index of the next measurement.
        """

        remaining_idxs = self.getRemainingMeasurementIndices()
        return remaining_idxs[0] if len(remaining_idxs) > 0 else self.getNumberOfMeasurements()
    

    def getMeasurementConfig(self, idx: int) -> pd.Series:
        """
        Retrieve the measurement configuration for the given index.

        Parameters
        ----------
        idx : int
            The index of the measurement configuration.

        Returns
        -------
        m_config : Series
            The measurement configuration as pandas series.
        """
        
        return pd.Series() if self.measurements is None else self.measurements.iloc[idx]



class DrillCaptureModel(EventDispatcher):
    """
    The Drill-Capture-Application model.
    """

    def __init__(self, core: Core):
        """
        Create a capture model instance.
        """

        EventDispatcher.__init__(self)
        # super().__init__()

        self._core = core
        self._state: ApplicationState = ApplicationState.CONFIGURE
        self._m_series: MeasurementSeries = None
        self._m_index: int = 0
        self._pause_processing = True
        self._measurement_data: np.ndarray = None


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
    

    def getMeasurementSeries(self) -> MeasurementSeries:
        """
        Retrieve the currently captured measurement series.

        Parameters
        ----------
        None

        Returns
        -------
        m_series : MeasurementSeries
            The current captured measurement series.
        """

        return self._m_series
    

    def hasValidMeasurementSeries(self) -> bool:
        """
        Check if a valid measurement series is configured.

        Parameters
        ----------
        None

        Returns
        -------
        valid : bool
            True, if the model contains a valid measurement series configuration, False if not.
        """
        
        return self._m_series is not None
    

    def getMeasurementIndex(self) -> int:
        """
        Retrieve the index of the currently measurement.

        Parameters
        ----------
        None

        Returns
        -------
        m_index : int
            The index of the current measurement.
        """

        return self._m_index
    

    def getNumberOfRemainingMeasurements(self) -> int:
        """
        Retrieve the amount of remaining measurements, or 0 if no measurement is present.

        Parameters
        ----------
        None

        Returns
        -------
        remaining : int
            The number of remaining measurements for the present measurement series configuration, or 0 is no configuration is present.
        """

        return 0 if self._m_series is None else self._m_series.getNumberOfRemainingMeasurements()
    

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
        Retrieve the most recent captured drill procedure measurement data.

        Parameters
        ----------
        None

        Returns
        -------
        measurement_data : np.ndarray
            The most recent captured drill procedure measurement data.
        """

        return self._measurement_data
    

    def hasMeasurementData(self) -> bool:
        """
        Check if valid drill procedure measurement data are available.

        Parameters
        ----------
        None

        Returns
        -------
        valid : bool
            True, if the model contains valid drill procedure measurement data, False if not.
        """

        return self._measurement_data is not None
    

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

        self._state = ApplicationState.CAPTURE
        self._m_series = None
        self._m_index = 0
        self._pause_processing = True
        self._measurement_data = None

        self._dispatchEvent('reset')
    

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
    

    def _setState(self, new_state: ApplicationState) -> None:
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

            # set task according to current state
            if self._state == ApplicationState.CONFIGURE:
                self._core.setTask()
            else:
                self._core.setTask(DrillProcedureDetectorTask(), self.handleTaskResult)

            # notify state change
            self._dispatchEvent('state_changed')
    

    def _setMeasurementSeries(self, m_series: MeasurementSeries) -> None:
        """
        Set the current measurement series.

        Parameters
        ----------
        m_series : MeasurementSeries
            the new measurement series instance.

        Returns
        -------
        None
        """

        self._m_series = m_series
        self._m_index = self._m_series.getNextMeasurementIndex()

        # notify state change
        self._dispatchEvent('measurement_series_changed')
    

    def _updateMeasurementIndex(self) -> None:
        """
        Update the measurement index to the next measurement.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        if not self.hasValidMeasurementSeries():
            return

        new_idx = self._m_series.getNextMeasurementIndex()
        if self._m_index != new_idx:
            self._m_index = new_idx

            # notify measurement index change
            self._dispatchEvent('measurement_index_changed')


    def generateMeasurementSeries(self, config: dict, n_recordings: int, target_dir: str = 'recordings') -> None:
        """
        Generate a new measurement series from the given measurement series configuration.

        Parameters
        ----------
        config : dict
            The measurement series configuration, with categories as keys and possible value options as list of values.
        n_recordings : int
            The number of recordings for each individual permutation of the provided configuration options.
        target_dir : str
            The measurement series output directory. (default: 'recordings')

        Returns
        -------
        None
        """

        if self._state == ApplicationState.CAPTURE:
            # prevent overriding the measurement series configuration during capturing
            return

        # construct output directory name based on the current date
        output_dir = os.path.join(target_dir, f'{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}')

        # construct a pandas data frame with all permutations of the configured values
        permutation_dfs = [pd.DataFrame([list(permutation)], columns=config.keys(), index=[0]) for permutation in list(itertools.product(*config.values()))]
        captureTable = pd.concat(permutation_dfs * n_recordings, ignore_index=True)
        captureTable['dataFile'] = ''

        # set new measurement series instance and reset capture index
        self._setMeasurementSeries(MeasurementSeries(captureTable.sample(frac=1).reset_index(drop=True), output_dir))


    def openMeasurementSeries(self, measurement_series_dir: str) -> None:
        """
        Open an existing measurement series.
        
        Parameters
        ----------
        measurement_series_dir : str
            The path to the measurement series directory, containing the measurements.csv as well as already captured measurements.

        Returns
        -------
        None
        """

        if self._state == ApplicationState.CAPTURE:
            # prevent overriding the measurement series configuration during capturing
            return

        # load measurement series from provided path
        m_file = os.path.join(measurement_series_dir, 'measurements.csv')
        if os.path.exists(m_file):
            self._setMeasurementSeries(MeasurementSeries(pd.read_csv(m_file), measurement_series_dir))


    def startCapturing(self) -> None:
        """
        (Re-)Start capturing the configured measurement series.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        
        # check for valid measurement series configuration
        if self.getNumberOfRemainingMeasurements() > 0:
            self._setState(ApplicationState.CAPTURE)


    def stopCapturing(self) -> None:
        """
        Stop capturing the configured measurement series.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # pause processing
        self.setPausing(True)
        
        self._setState(ApplicationState.CONFIGURE)
    

    def handleTaskResult(self, msg: object) -> None:
        """
        Handler method for task result messages.

        Parameters
        ----------
        msg : object
            The message from the task.
        """

        if self._state == ApplicationState.CONFIGURE:
            # no processing in configuration state
            return
        
        if self.isPausing():
            # no processing in preparation mode
            return
        
        if type(msg) == np.ndarray:
            print('Bohrvorgang empfangen')

            # pause further processing
            self.setPausing(True)
            
            # store drill data for further processing
            self._measurement_data = msg

            # notify measurement data change
            self._dispatchEvent('measurement_data_changed')


    def storeMeasurement(self) -> None:
        """
        Store the current drill data as measurement for the current measurement id.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # check for valid measurement series and drill measurement data to store
        if not self.hasValidMeasurementSeries() or not self.hasMeasurementData():
            return
        
        # create output directory if required
        if not os.path.exists(self._m_series.output_dir):
            os.makedirs(self._m_series.output_dir)
        
        # store drill procedure measurement data
        m_file_name = f'{datetime.datetime.now():%Y_%m_%d_%H_%M_%S}_96000Hz.csv'
        m_file_path = os.path.join(self._m_series.output_dir, m_file_name)
        np.savetxt(m_file_path, self._measurement_data, delimiter=',', header='Audio,Voltage,Current', fmt='%2.6f')

        # set measurement file name reference in measurement table
        self._m_series.measurements.loc[self._m_index, 'dataFile'] = m_file_name

        # store / override measurement table
        self._m_series.measurements.to_csv(os.path.join(self._m_series.output_dir, f"measurements.csv"), index=False)

        # clear drill data
        self._measurement_data = None

        # notify measurement data change
        self._dispatchEvent('measurement_data_changed')

        # increment measurement index
        self._updateMeasurementIndex()


    def discardMeasurement(self) -> None:
        """
        Discard the current measurement data.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # check for valid drill data to store
        if not self.hasMeasurementData():
            return

        # enable further processing again
        self.setPausing(False)

        # clear measurement data
        self._measurement_data = None

        # notify measurement data change
        self._dispatchEvent('measurement_data_changed')
