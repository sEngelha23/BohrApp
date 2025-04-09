# Automatically reload external modules (see https://ipython.org/ipython-doc/3/config/extensions/autoreload.html for more information).
#%load_ext autoreload
#%autoreload 2

# Set up system path to include our own "mldog" python package.
import sys
import os
import joblib
import dill
sys.path.append('.\\MLDOG-Framework\\src')
#print(sys.path)
current_file_path = os.path.abspath(__file__)
src_folder_path = os.path.dirname(os.path.dirname(current_file_path))  # Geht einen Ordner nach oben
if src_folder_path not in sys.path:
    sys.path.append(src_folder_path)

# general imports
import numpy as np
import pandas as pd
from tsfresh import extract_features
from tsfresh.feature_extraction import ComprehensiveFCParameters
from tsfresh.feature_extraction import MinimalFCParameters

# our own drill util library
import mldog.util.drill  as dog

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
from joblib import dump
import os
from model.task import Task
import pickle

# ----------------------------
# code für kompletten frame (dfAvg)
#-----------------------------

dfmeasurements = pd.read_csv('C:/Users/Muster/Desktop/Angewandte Künstliche Intelligenz/Semester 3/Projekt1/Projektrepository/team-9/MLDOG-Framework/data/measurements.csv')
dfmeasurements.head()

# Listen für Train/Testdaten
lisAudioTrain = []
lisVoltTrain = []
lisCurrentTrain = []
lisTimeTrain = []

lisVoltTest = []
lisCurrentTest = []
lisTimeTest = []

# Breakpoint für Trainingsdaten (70. DataFrame)
breakpoint1 = '2024_10_23_10_32_42_96000Hz.csv'

# Generierung von Trainingsdaten
for datafr in dfmeasurements['dataFile']:
    tempdf = pd.read_csv(f'C:/Users/Muster/Desktop/Angewandte Künstliche Intelligenz/Semester 3/Projekt1/Projektrepository/team-9/MLDOG-Framework/data/{datafr}')
    
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

# Testdaten (optional)
# Generierung von Testdaten erfolgt hier nach ähnlichem Prinzip wie bei Train

data_base_path = './data'
recording_path = 'gesamtdata'
data_file = '2024_10_23_09_58_52_96000Hz.csv'

test = pd.read_csv('C:/Users/Muster/Desktop/Angewandte Künstliche Intelligenz/Semester 3/Projekt1/Projektrepository/team-9/MLDOG-Framework/data/2024_10_23_09_58_52_96000Hz.csv')
test2 = dog.io.read_measurement_csv('C:/Users/Muster/Desktop/Angewandte Künstliche Intelligenz/Semester 3/Projekt1/Projektrepository/team-9/MLDOG-Framework/data/2024_10_23_09_58_52_96000Hz.csv', set_time_index=True)

# Generierung des Trainingsdataframes
dfTrain = pd.DataFrame({
    'AudioAvg': lisAudioTrain,
    'VoltageAvg': lisVoltTrain,
    'CurrentAvg': lisCurrentTrain,
    'time': lisTimeTrain
})

# Test-Dataframe (hier exemplarisch ohne 'AudioAvg', da in deinem Beispiel nicht verwendet)
dfTest = pd.DataFrame({
    'VoltageAvg': lisVoltTest,
    'CurrentAvg': lisCurrentTest,
    'time': lisTimeTest
})

# benutzerdefinierte Parameter für tsfresh
custom_params = {
    "mean": None,
    #"standard_deviation": None,
    #"maximum": None,
    #"minimum": None,
    #"sum_values": None
}

###########################
# Transformer-Definition
###########################

class CsvRestructuring(BaseEstimator, TransformerMixin):
    def __init__(self) -> None:
        self.task = None  # Kein Task-Objekt zu diesem Zeitpunkt

    def fit(self, X, y=None):
        # Task-Erstellung in den fit()-Methoden verschieben
        self.task = Task(name="CsvRestructuringTask")
        return self

    def transform(self, X):
        if self.task is None:
            raise ValueError("Task wurde noch nicht initialisiert. Bitte zuerst fit() aufrufen.")

        # Transformation durchführen
        voltAvg = X['Voltage'].mean()
        curAvg = X['Current'].mean()
        audioAvg = X['# Audio'].mean()
        time = X.shape[0] / 96000

        # Daten mit dem Task verarbeiten (aber den Task nicht in der Pipeline speichern)
        self.task.process(X.to_numpy())  # Beispielhafte Nutzung

        dfTransformer = pd.DataFrame({
            'AudioAvg': audioAvg,
            'VoltageAvg': voltAvg,
            'CurrentAvg': curAvg,
            'time': time
        }, index=[0])

        return dfTransformer


# Beispielhafter Aufruf des Transformers
scaler = CsvRestructuring()
scaler.fit(test)  # Initialisiere den Task
transformed_data = scaler.transform(test)  # Wende den Transformer an

###########################
# Modell und Pipeline
###########################

# Definiere den Klassifizierer
clf = DecisionTreeClassifier()

# Definiere die Pipeline
pipeline = Pipeline([
    ('csvScaler', scaler),  # Der Transformer wird hier angewendet
    ('classifier', clf)  # Der Klassifizierer wird hinzugefügt
])

# Trainingsdaten
X_train = dfTrain
y_train = dfmeasurements['material'][:70]  # Zielt auf den 'material' Spalte der ersten 70 Einträge

# Testdaten
y_test = dfmeasurements['material'][70:]  # Testdaten ab dem 70. Eintrag

# Trainiere den Klassifizierer
clf.fit(X_train, y_train)

# Speichere das Modell
model = Pipeline([('csvScaler', scaler),
                  ('classifier', clf)])

# Vorhersagen für das Testset
y_pred = []

for toPredict in dfmeasurements['dataFile'][70:]:
    testdf = pd.read_csv(f'C:/Users/Muster/Desktop/Angewandte Künstliche Intelligenz/Semester 3/Projekt1/Projektrepository/team-9/MLDOG-Framework/data/{toPredict}')
    y_pred += [model.predict(testdf)[0]]  # Vorhersage für jede Datei

# Berechne den Accuracy-Score
accuracy = accuracy_score(y_pred, y_test)
print(f"Accuracy: {accuracy}")


# Statt joblib.dump, dill verwenden
with open('pipeline_model.pkl', 'wb') as f:
    dill.dump(model, f)
