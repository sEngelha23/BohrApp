import numpy as np


__all__ = ['DrillProcedureDetector']


class DrillProcedureDetector():
    """
    Utility component for detecting and extracting drilling procedures from live stream data chunks.

    A common use case in the drill domain is the processing of a whole drilling procedure.
    The `DrillProcedureDetector` monitors the live data stream and checks for each time step if the drill was active or not based on power consumption.
    Once the drill is considered active, the data stream is written into an internal buffer.
    After the drill is considered inactive again, the internal buffer is returned - signaling the end of a drilling procedure - and reset for further processing.
    Using default settings, the `DrillProcedureDetector` will include 48000 measurements (0.5 seconds) before and after the detected drilling procedure.
    """

    def __init__(self, ttl_max = 150, window_size = 48000, active_power = 20):
        """
        Construct a new drill procedure detector.

        Parameters
        ----------
        ttl_max : int
            The TTL (time-to-live) counter reset value.
        window_size : int
            The number of measurements before and after a detected drill procedure.
        active_power : int
            The power level beyond which the drill is considered active / drilling (and inactive below).
        """

        self.buffer = np.zeros((0, 3))
        self.start_detected = False
        self.ttl_max = ttl_max
        self.ttl = ttl_max
        self.window_size = window_size
        self.active_power = active_power


    def reset(self):
        """
        Reset internal buffer to start a new detection from scratch.
        """

        self.buffer = np.zeros((0, 3))


    def update(self, data: np.ndarray) -> np.ndarray:
        """
        Update the internal buffer with new stream data and check if a drilling procedure has been completed.

        Parameters
        ----------
        data : ndarray
            The next chunk of (stream) data.
        
        Returns
        -------
        drill_data : np.ndarray | None
            The data for a complete detected drill procedure if the drill procedure just ended with the given data package, None otherwise.
        """
        
        # store new data in history buffer
        self.buffer = np.vstack([self.buffer, data])

        # initialize dummy result
        result = None

        # determine if the drill is currently active
        max_power = np.max(np.abs(data[:, 1] * data[:, 2]))
        is_active = True if max_power > self.active_power else False

        # debugging output
        # print(f'MaxPower: {max_power} \tActive: {is_active}')

        if not self.start_detected:
            if is_active:
                # start detected
                self.start_detected = True
                self.ttl = self.ttl_max
            else:
                # limit history
                if len(self.buffer) > self.window_size:
                    self.buffer = self.buffer[-self.window_size:]
        else:
            if is_active:
                # reset ttl as long as the drill is active
                self.ttl = self.ttl_max
            else:
                self.ttl = self.ttl - 1
                if self.ttl == 0:
                    # ttl expired -> end of drill procedure
                    result = self.buffer
                    self.buffer = np.zeros((0, 3))
                    self.start_detected = False
        
        return result
