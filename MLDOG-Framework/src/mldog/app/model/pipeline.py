import pandas as pd
#from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
#from ..model.task import Task

import queue  # Wir benötigen das Modul 'queue' für Warteschlangen
from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import Pipeline
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.metrics import accuracy_score
import pickle
import os



base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join("mldog", "app", "model", "pipelinecdfFulldata.pkl")


with open(model_path,'rb') as modelFile:
    clf = pickle.load(modelFile)



class CsvRestructuring(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self


    def transform(self, X):
        dfFromArray = pd.DataFrame({
            '# Audio': X[:,0],
            'Voltage': X[:,1],
            'Current': X[:,2],
        })
        
        voltAvg = dfFromArray['Voltage'].mean()
        curAvg = dfFromArray['Current'].mean()
        audioAvg = dfFromArray['# Audio'].mean()
        time = dfFromArray.shape[0] / 96000

        dfTransformer = pd.DataFrame({
            'AudioAvg': audioAvg,
            'VoltageAvg': voltAvg,
            'CurrentAvg': curAvg,
            'time': time
        }, index=[0])

        return dfTransformer
    

###########################
# define the transformer
###########################


# class CsvRestructuring(BaseEstimator, TransformerMixin):

#     def fit(self, X, y=None):
#         return self

#     def transform(self, X):
#         from tsfresh.feature_extraction import EfficientFCParameters
#         efficient = EfficientFCParameters()

#         ass = ['partial_autocorrelation' ,'number_cwt_peaks', 
#        'agg_linear_trend', 'augmented_dickey_fuller', 'lempel_ziv_complexity', 'permutation_entropy']

#         for x in ass:
#             del efficient[x]

#         dfFromArray = pd.DataFrame({
#             '# Audio': X[:,0],
#             'Voltage': X[:,1],
#             'Current': X[:,2],
#         })


#         # Per hand features
#         time = dfFromArray.shape[0] / 96000

#         #hinzufügen der ID
#         dfFromArray['ID'] = 0
        


#         features = extract_features(dfFromArray, column_id= 'ID', default_fc_parameters= efficient, n_jobs=0) # MinimalFCParameters() # Minimal
#         features['time'] = time
#         return features


class MaterialClassifier(BaseEstimator):
    def __init__(self):
        self.pipeline = self._create_pipeline()

    def _create_pipeline(self):
            pipe = Pipeline([
                ('csv_scaler', CsvRestructuring()),
                ('classifier', clf)
                ])
            return pipe

    def predict(self, X):
        material = self.pipeline.predict(X)
        if material == ['kunststoff-pom']:
            return "Kunststoff-POM"
        elif material == ['holz-spahn']:
            return "Spanholz"
        # if material == 0:
        #     return "Spanholz"
        # elif material == 1:
        #     return "Kunststoff-POM"
        # elif material == 2:
        #     return "Holz-Eiche"
        # elif material == 3:
        #     return "Metall-Alu"