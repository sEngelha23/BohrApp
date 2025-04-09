# general imports
import sys
sys.path.append('../src')
import os
import numpy as np
import pandas as pd
from tsfresh import extract_features
from tsfresh.feature_extraction import ComprehensiveFCParameters
from tsfresh.feature_extraction import MinimalFCParameters
import pickle

# our own drill util library
import src.mldog.util.drill as dog

# plotting
import matplotlib.pyplot as plt
import plotly_express as px

# Everything around pipeline
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_val_score
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer


dfmeasurements = pd.read_csv('data/measurements.csv')
dfmeasurements.head()

# Liste für train
lisAudioTrain = []
lisVoltTrain = []
lisCurrentTrain = []
lisTimeTrain = []



# # Liste für test
lisVoltTest = []
lisCurrentTest = []
lisTimeTest = []

# Breakpoint for Training and Testdata -> 70th dataframe (90/10)
breakpoint1 = '2024_10_23_10_32_42_96000Hz.csv'


# Listgeneration for Traindataframe
for datafr in dfmeasurements['dataFile']:

    tempdf = pd.read_csv(f'data/{datafr}') # Pfad variiert je nach Pc -> damit funktioniert anpassen

    audioAvg = tempdf['# Audio'].mean()
    voltageAvg = tempdf['Voltage'].mean()
    currentAvg = tempdf['Current'].mean()
    time = tempdf.shape[0] / 96000

    lisVoltTrain += [voltageAvg]
    lisCurrentTrain += [currentAvg]
    lisTimeTrain += [time]
    lisAudioTrain += [audioAvg]

    if datafr == breakpoint1:
        break

        
        

# Listgeneration for Testdataframe
# for datafr in dfmeasurements['dataFile'][70:]:

#     tempdf = pd.read_csv(f'data\gesamtdata/{datafr}') # Pfad variiert je nach Pc -> damit funktioniert anpassen

#     voltageAVG = tempdf['Voltage'].mean()
#     currentAvg = tempdf['Current'].mean()
#     time = tempdf.shape[0] / 96000

#     lisVoltTest += [voltageAVG]
#     lisCurrentTest += [currentAvg]
#     lisTimeTest += [time]

########################################
# Test dataframe and read csv from io
########################################

data_base_path = 'data'

data_file = '2024_10_23_09_58_52_96000Hz.csv'

test = pd.read_csv('data/2024_10_23_09_58_52_96000Hz.csv')
# test2 = dog.io.read_measurement_csv(os.path.join(data_base_path, data_file), set_time_index=True)


################### 
# dataframe dfAvg
###################

# dfAvg = pd.DataFrame({
#     #'AudioAvg': AudioAvgMDF,
#     'VoltageAvg': lisVolt,
#     'CurrentAvg': lisCurrent,
#     'time': lisTime
# })


# dfAvg["Leistung"] = dfAvg["VoltageAvg"] * dfAvg["CurrentAvg"]
# dfAvg["Widerstand"] = dfAvg["VoltageAvg"] / dfAvg["CurrentAvg"]
# dfAvg["ÄnderungsrateWiderstand"] = dfAvg["Widerstand"].diff() / dfAvg["time"].diff()
################### 
# dataframe Train/Test
###################

# Train
dfTrain = pd.DataFrame({
    'AudioAvg': lisAudioTrain,
    'VoltageAvg': lisVoltTrain,
    'CurrentAvg': lisCurrentTrain,
    'time': lisTimeTrain
})

# dfTrain["Leistung"] = dfTrain["VoltageAvg"] * dfTrain["CurrentAvg"]
# dfTrain["Widerstand"] = dfTrain["VoltageAvg"] / dfTrain["CurrentAvg"]
# dfTrain["ÄnderungsrateWiderstand"] = dfTrain["Widerstand"].diff() / dfTrain["time"].diff()

# Test
dfTest = pd.DataFrame({
#     #'AudioAvg': AudioAvgMDF,
    'VoltageAvg': lisVoltTest,
    'CurrentAvg': lisCurrentTest,
    'time': lisTimeTest
})


custom_params = {
    "mean": None,
    #"standard_deviation": None,
    #"maximum": None,
    #"minimum": None,
    #"sum_values": None
}


# featuresvolt = extract_features(test2[['Voltage', 'ID', 'time']], column_id= 'ID', column_sort = 'time', column_value = 'Voltage', default_fc_parameters= custom_params) # MinimalFCParameters()
# featurescur = extract_features(test2[['Current', 'ID', 'time']], column_id= 'ID', column_sort = 'time', column_value = 'Current', default_fc_parameters= custom_params) # MinimalFCParameters()

###########################
# define the transformer
###########################


class CsvRestructuring2(BaseEstimator, TransformerMixin):
    def __init__(self) -> None:
        super().__init__()
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):

        ################
        # Falls X -> csv
        ################

        voltAvg = X['Voltage'].mean()
        curAvg = X['Current'].mean()
        audioAvg = X['# Audio'].mean()
        time = X.shape[0] / 96000

        dfTransformer = pd.DataFrame({
            'AudioAvg': audioAvg,
            'VoltageAvg': voltAvg,
            'CurrentAvg': curAvg,
            'time': time
        }, index=[0])


        #################
        # Falls X -> Array (Arrays sind Columns)
        #################

        # if len(X) ==  3:
        #     dfFromArray = pd.DataFrame({
        #         '# Audio': X[:,0],
        #         'Voltage': X[:,1],
        #         'Current': X[:,2],
        #     })

        # else:
        #     dfFromArray = pd.DataFrame(
        #         X,columns=['# Audio', 'Voltage', 'Current']
        #     )            

        # voltAvg = dfFromArray['Voltage'].mean()
        # curAvg = dfFromArray['Current'].mean()
        # audioAvg = dfFromArray['# Audio'].mean()
        # time = dfFromArray.shape[0] / 96000

        # dfTransformer = pd.DataFrame({
        #     'AudioAvg': audioAvg,
        #     'VoltageAvg': voltAvg,
        #     'CurrentAvg': curAvg,
        #     'time': time
        # }, index=[0])
        #print(dfTransformer)
        return dfTransformer

# Transformer test
CsvRestructuring2().transform(test)

# scaler
scaler = CsvRestructuring2()

# column transformer
# columntrans = ColumnTransformer(('Csvreshape', scaler), remainder='passthrough')

# Classifier
clf = DecisionTreeClassifier()

# Pipeline
pipeline = Pipeline([#('csvScaler', columntrans),
                     ('classifier', clf)])

# Train und Testdata
X_train = dfTrain
y_train = dfmeasurements['material'][:70]

# X_test = dfTest
y_test = dfmeasurements['material'][70:]
# X_train, X_test, y_train, y_test = train_test_split(X,y, train_size=0.9, random_state=69)

# fit classifier
clf.fit(X_train, y_train)

# define model
model = Pipeline([('csvScaler', scaler),
                     ('classifier', clf)])



# predictions

y_pred = []

for toPredict in dfmeasurements['dataFile'][70:]:

    testdf = pd.read_csv(f'data/{toPredict}') # Pfad variiert je nach Pc -> damit funktioniert anpassen
    y_pred.append(model.predict(testdf)[0])


#print(model.predict(test))
with open('pipelinecdfneu.pkl','wb') as modelFile:
    pickle.dump(clf, modelFile, fix_imports=True)

with open('pipelinecdfneu2.pkl','wb') as modelFile:
    pickle.dump(clf, modelFile)