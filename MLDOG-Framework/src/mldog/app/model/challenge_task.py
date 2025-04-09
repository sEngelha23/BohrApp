import time
import numpy as np



class ChallengeTask:
    """
    The abstract base class for specific challenge tasks.
    """
    
    def __init__(self, name: str = 'Challenge Task'):
        """
        Construct a new challenge task instance.

        Parameters
        ----------
        name : str
            The name of the task, e.g. Team X.
        """
        
        self._name: str = name


    def getName(self) -> str:
        """
        Retrieve the name of this challenge task instance.

        Parameters
        ----------
        None

        Returns
        -------
        name : str
            The name of the challenge task.
        """

        return self._name


    def run(self, drill_data: np.ndarray) -> None:
        """
        The run-method, executed by the challenge task runner.

        Parameters
        ----------
        drill_data: ndarray
            The data of a completed drill procedure.

        Returns
        -------
        (classification_result, runtime) : tuple(str, float)
            The predicted class combined with the runtime for computing the prediction.
        """

        data_copy = drill_data.copy()
        
        # start_time = time.perf_counter()
        start_time = time.process_time()
        result = self.predict(drill_data=data_copy)
        # end_time = time.perf_counter()
        end_time = time.process_time()
        runtime = end_time - start_time

        return result, runtime


    def predict(self, drill_data: np.ndarray) -> str:
        """
        Classify new drill procedure data.

        This method performs a classification of the provided drill procedure data.

        Parameters
        ----------
        drill_data: ndarray
            The data of a completed drill procedure.

        Returns
        -------
        classification_result : str
            The predicted class (e.g. 'holz-span', etc.).
        """
        
        return ''
