import numpy as np

from ..model.task import Task
from ...util.drill.drill_procedure_detector import DrillProcedureDetector
from ..model.pipeline import MaterialClassifier


class DetectorAndPredictorTask(Task):
    """
    Simple task class for detecting drill procedures and extracting the related sensor data from the data stream.
    """
    
    def __init__(self, ttl_max = 150, window_size = 48000, active_power = 50):
        """
        Construct a new task instance.

        Parameters
        ----------
        name : str
            The name of the task.
        """
        super().__init__('Drill Procedure Detector')

        self.detector = DrillProcedureDetector(ttl_max, window_size, active_power)


    def reset(self) -> None:
        """
        Reset internal buffer to start a new detection from scratch.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.detector.reset()


    def process(self, data: np.ndarray) -> None:
        """
        Process new measurement data.

        Measurement data is received in chunks (sequential data portions).
        This method is automatically called by the task thread for each incoming data chunk during an active measurement.
        Any complex / time consuming calculations on measurement data should be performed within this method.

        Parameters
        ----------
        data: ndarray
            The next chunk of measurement data to process.

        Returns
        -------
        None
        """

        # forward steam data to detector instance
        drill_data = self.detector.update(data)
       
        # check for successful drill procedure detection and publish it accordingly
        if drill_data is not None:
            material = MaterialClassifier().predict(drill_data)
            result = [drill_data, material]
            self.publishResult(result)