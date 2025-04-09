# .csv data io functions
import pandas as pd
import os


__all__ = ['read_measurement_csv']


def read_measurement_csv(csv_file: str, set_time_index: bool = False):
    """Method to read sensor time series data from a .csv file.
    
    Parameters
    ----------
    csv_file : string
        The path to the .csv file to read.

    set_time_index : bool
        If True, set the (generated) time information as index for the measurement data.
    
    Returns
    ----------
    df : pandas.DataFrame
        A pandas DataFrame with the sensor data.
    """

    # split file name by underscore '_'
    name_split = os.path.basename(csv_file)[:-4].split('_') 

    # extract frequency information
    frequency = int(name_split[-1][:-2])
    # print(frequency)

    # Determine start time of measurement
    start_time = pd.to_datetime('_'.join(name_split[:-1]), format = '%Y_%m_%d_%H-%M-%S')
    # print(start_time)

    # read raw csv data
    df = pd.read_csv(csv_file)

    # construct date time information based on start time and sample rate
    time_idx = pd.date_range(start = start_time, periods = len(df), freq = pd.Timedelta(seconds = 1.0 / frequency))
    if set_time_index:
        # override sequential index with timestamp based index
        df.set_index(time_idx, inplace=True)
    else:
        df['Time'] = time_idx

    return df


