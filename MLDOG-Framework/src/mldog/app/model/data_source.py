from queue import Queue

from .event_dispatcher import EventDispatcher



class ChannelConfiguration:
    """
    Class for holding name and id information to a measurement channel.
    """
    
    def __init__(self, id: int, name: str):
        """
        Construct a new channel configuration instance.
        """
        
        self.id: int = id
        self.name: str = name
    

    def __repr__(self):
        return f'Channel {self.id}: {self.name}'



class MeasurementConfiguration:
    """
    Class for specifying combined measurements on multiple measurement channels.

    Measurements are taken simultaneously in a specified frequency for multiple channels, corresponding to different sensor information.
    This class provides general information about the measured sensor information for the various channels and the measurement frequency.
    """
    
    def __init__(self, frequency: int, channels: list[ChannelConfiguration]):
        """
        Construct a new measurement configuration instance.
        """
        self.frequency: int = frequency
        self.channels: list[ChannelConfiguration] = channels
    

    def __repr__(self):
        return f'Measurement: {self.channels} @ {self.frequency}Hz'



class DataSource(EventDispatcher):
    """
    Abstract base class for data sources, providing access to measurement data streams.
    """
    
    def __init__(self, name: str):
        """
        Construct a new data source instance.
        """

        super().__init__()

        self.name: str = name
        self.mconfig: MeasurementConfiguration = None
        self.data_queue: Queue = None
    

    def getName(self) -> str:
        """
        Retrieve the display name of this data source.
        """

        return self.name
    

    def getMeasurementConfiguration(self) -> MeasurementConfiguration:
        """
        Retrieve the configuration of the active measurement.
        """

        return self.mconfig


    def setup(self):
        """
        Setup the data source.
        """
        
        return False


    def shutdown(self):
        """
        Shutdown the data source.
        """
        
        self.data_queue = None


    def startMeasurement(self, data_queue):
        """
        Start a new measurement.
        """

        # print('Starting new Measurement...')

        self.data_queue = data_queue

        self._dispatchEvent('measuring_changed')


    def stopMeasurement(self):
        """
        Stop the active measurement.
        """

        if not self.isMeasuring():
            return

        # print('Stopping Measurement...')

        self.data_queue = None

        self._dispatchEvent('measuring_changed')


    def isMeasuring(self):
        """
        Check if a measurement is currently in progress.
        """

        return self.data_queue is not None


    def publish(self, data_obj):
        """
        Publish a new data object.
        """

        if self.data_queue is not None:
            self.data_queue.put(data_obj)


    def receiveLoop(self):
        """
        The data source receive loop.
        """

        pass
    