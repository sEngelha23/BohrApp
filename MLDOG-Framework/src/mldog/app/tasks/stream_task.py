from queue import Empty, Queue
import numpy as np

from ..model.task import Task



class StreamTask(Task):
    """
    Simple task class for directly forwarding sensor data.
    """
    
    def __init__(self):
        """
        Construct a new task instance.

        Parameters
        ----------
        name : str
            The name of the task.
        """
        super().__init__('Stream')

        # self.buffer = ...


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

        self.publishResult(data)
