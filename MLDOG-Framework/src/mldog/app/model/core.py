from threading import Thread

from .event_dispatcher import EventDispatcher
from .data_source import DataSource
from .task import Task
from queue import Queue, Empty

from typing import Callable, Any



class Core(EventDispatcher):
    """
    The MLDOG core model class.
    """

    def __init__(self):
        """
        Create a new core instance.

        Parameters
        ----------
        None
        """

        super().__init__()
        
        # the data source (live/dummy/log/etc.)
        self._data_source: DataSource = None

        # the task
        self._task: Task = None

        # the task result listener callback
        self._task_result_callback: Callable[[Any], None] = None

        # the thread instances
        self._data_thread: Thread = None
        self._task_thread: Thread = None

    
    def getActiveDataSource(self) -> DataSource:
        """
        Retrieve the currently active data source.

        Parameters
        ----------
        None

        Returns
        -------
        data_source : DataSource
            The active data source or None in case no data source is currently active.
        """

        return self._data_source

    
    def getActiveTask(self) -> Task:
        """
        Retrieve the currently active task.

        Parameters
        ----------
        None

        Returns
        -------
        task : Task
            The active task or None in case no task is currently active.
        """

        return self._task
    

    def hasActiveDataSource(self) -> bool:
        """
        Check for valid data source instance.

        Parameters
        ----------
        None

        Returns
        -------
        active : bool
            True, if there exists a valid data source instance, False otherwise.
        """

        return self._data_source is not None


    def hasActiveTask(self) -> bool:
        """
        Check for valid task instance.

        Parameters
        ----------
        None

        Returns
        -------
        active : bool
            True, if there exists a valid task instance, False otherwise.
        """

        return self._task is not None


    def setDataSource(self, source: DataSource = None) -> None:
        """
        Set the active data source instance.

        Parameters
        ----------
        source : DataSource
            The new data source instance.

        Returns
        -------
        None
        """

        # stop any active measurements
        self.stopMeasurement()
        
        # shutdown current data source and wait for ml thread to finish
        if self._data_source is not None:
            print(f'===== Shutdown DataSource: "{self._data_source.getName()}"')
            self._data_source.shutdown()

            if self._data_thread is not None:
                print('-> Waiting for receive thread to finish... ', end='')
                self._data_thread.join()
                print('done!')
                self._data_thread = None

        # set new data source
        self._data_source = source

        if self._data_source is not None:
            # open new data source
            print(f'===== Setup DataSource: {self._data_source.getName()}')
            self._data_source.setup()
            print('===== Setup End')

            # start new read/receive thread
            self._data_thread = Thread(target = self._data_source.receiveLoop, daemon = True)
            self._data_thread.start()

        # publish event
        self._dispatchEvent('data_source_changed')


    def setTask(self,
                task: Task = None,
                task_result_callback: Callable[[Any], None] = None,
                autostart: bool = True) -> None:
        """
        Start a new task.

        Parameters
        ----------
        task : Task
            The new task instance to start in a dedicated thread.
        task_result_callback : Callback[[Any], None]
            The method to call for new task results.
        autostart : bool
            True if a new measurement should be automatically started for the given task, False if not.

        Returns
        -------
        None
        """

        # stop any active measurements
        self.stopMeasurement()
        
        # shutdown current task and wait for task thread to finish
        if self._task is not None:
            print(f'===== Shutdown Task: "{self._task.getName()}"')
            self._task.shutdown()

            if self._task_thread is not None:
                print('-> Waiting for processing thread to finish... ', end='')
                self._task_thread.join()
                print('done!')
                self._task_thread = None
        
        # set new task
        self._task = task
        self._task_result_callback = task_result_callback

        if self._task is not None:
            print(f'===== Run Task: "{self._task.getName()}"')

            # start new task thread
            self._task_thread = Thread(target = self._task.run, daemon = True)
            self._task_thread.start()

        # publish event
        self._dispatchEvent('task_changed')

        # autostart a new measurement if requested
        if autostart:
            self.startMeasurement()


    def startMeasurement(self) -> None:
        """
        Instruct the data source to start a new measurement.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        
        if self._data_source is not None and self._task is not None:
            self._data_source.startMeasurement(self._task.getDataQueue())


    def stopMeasurement(self) -> None:
        """
        Instruct the data source to stop an active measurement.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        
        if self._data_source is not None:
            self._data_source.stopMeasurement()
    

    def isMeasuring(self) -> bool:
        """
        Check wether the data source is actively measuring or not.

        Parameters
        ----------
        None

        Returns
        -------
        measuring : bool
            True, if a measurement is active, False otherwise.
        """
        
        return False if self._data_source is None else self._data_source.isMeasuring()
    

    def toggleMeasurement(self) -> None:
        """
        Toggle measurement. Either stop an active measurement, or start a new one.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        
        if self.isMeasuring():
            self.stopMeasurement()
        else:
            self.startMeasurement()


    def checkForTaskResults(self) -> None:
        """
        Check result queue of active task for updates and notify listeners accordingly.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        if self._task is None:
            # no active task, thus nothing to check
            return
        
        result_queue = self._task.getResultQueue()
        while result_queue.qsize() > 0:
            try:
                msg = result_queue.get(block=False)
            except Empty as e:
                # return in case of an empty message
                return
            
            # forward task message to result listener callback
            if not self._task_result_callback is None:
                self._task_result_callback(msg)
