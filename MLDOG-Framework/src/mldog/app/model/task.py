from queue import Empty, Queue
import numpy as np



class Task:
    """
    The abstract base class for specific tasks.
    """
    
    def __init__(self, name: str = 'Task'):
        """
        Construct a new task instance.

        Parameters
        ----------
        name : str
            The name of the task.
        """
        
        self._name: str = name
        self._shutdown: bool = False
        self._data_queue: Queue = Queue()
        self._result_queue: Queue = Queue()


    def getName(self) -> str:
        """
        Retrieve the name of this task controller instance.

        Parameters
        ----------
        None

        Returns
        -------
        name : str
            The name of the task.
        """

        return self._name


    def setup(self) -> None:
        """
        Setup task components.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        
        pass


    def getDataQueue(self) -> Queue:
        """
        Retrieve the task data input queue.

        Parameters
        ----------
        None

        Returns
        -------
        data_queue : Queue
            The task data input queue.
        """
        
        return self._data_queue


    def getResultQueue(self) -> Queue:
        """
        Retrieve the task result output queue.

        Parameters
        ----------
        None

        Returns
        -------
        result_queue : Queue
            The task result output queue.
        """
        
        return self._result_queue


    def publishResult(self, result_obj: object) -> None:
        """
        Publish a new result data message object.

        Parameters
        ----------
        result_obj : object
            The result message object to publish.

        Returns
        -------
        None
        """

        self._result_queue.put(result_obj)


    def shutdown(self) -> None:
        """
        Shutdown this task instance.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        
        # trigger shutdown
        self._shutdown = True


    def run(self) -> None:
        """
        The task run-method, executed by the task thread.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        
        self._shutdown = False

        while not self._shutdown:
            # fetch next chunk of data
            try:
                data = self._data_queue.get(block=True, timeout=1)
            except Empty as e:
                # skip processing of empty data chunk
                # print('Skip processing...')
                continue

            # process data chunk
            self.process(data)

        # print('Exiting Task')


    def process(self, data: np.ndarray) -> None:
        """
        Process new measurement data.

        Measurement data is received in chunks (sequential data portions).
        This method is automatically called by the task thread for each incoming data chunk during an active measurement.
        Any complex / time consuming calculations on measurement data should be performed within this method.

        Note: As visualization is handled in a separate thread, remember to use tkinter .after_idle(), etc. methods for triggering ui-updates!

        Parameters
        ----------
        data: ndarray
            The next chunk of measurement data to process.

        Returns
        -------
        None
        """
        
        pass
