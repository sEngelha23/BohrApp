import numpy as np

from ..model.challenge_task import ChallengeTask



class ExampleChallengeTask(ChallengeTask):
    """
    Simple challenge task class example.
    """
    
    def __init__(self):
        """
        Construct a new example challenge task instance.
        """
        super().__init__('Team Test')

        # setup (load model, etc.)


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
        
        # run prediction pipeline with given drill data...
        material = 'holz-span'
        
        return material
