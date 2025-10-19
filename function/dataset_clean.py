import pandas as pd
from capstone_group4 import read_data_csv
from sklearn.preprocessing import LabelEncoder

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
    le = LabelEncoder()
    df['station_name_encoded'] = le.fit_transform(df['station_name'])


    if 'service_date' and 'time_period' in df.columns:
        df['time_period'] = df['time_period'].str.replace(r'[()]', '', regex=True)
        df['time'] = pd.to_datetime(df['service_date'] + ' ' + df['time_period'])

    return df