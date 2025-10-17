import pandas as pd
from dataset_get import read_data_csv

def clean_data(df):
    """
    Clean the dataset by handling missing values and duplicates.

    Parameters:
    df (pd.DataFrame): The input DataFrame to be cleaned.

    Returns:
    pd.DataFrame: The cleaned DataFrame.
    """
    # Drop duplicates
    df = df.drop_duplicates()

    df = df.dropna(subset=['route_id'])


    df['route_color'] = '#' + df['route_color'].astype(str)



    if 'service_date' and 'time_period' in df.columns:
        df['time_period'] = df['time_period'].str.replace('()', '', regex=True)
        df['time'] = pd.to_datetime(df['service_date'] + ' ' + df['time_period'], format='%m/%d/%Y (%H:%M:%S)')
        print("time:", df['time'])

    return df