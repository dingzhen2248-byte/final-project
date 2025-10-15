import pandas as pd
from api import get_request

def read_data_api():
    df = pd.DataFrame(base_url,params)
    try:
        df = get_request(base_url,params)
        if df.empty:
            print("No data retrieved!")
    except Exception as e:
        print("Error reading API data:", e)
    df = pd.DataFrame(df[1:], columns=df[0])
    print("API data:\n", df.head())
    return df

def read_data_csv(file_path):
    df = pd.DataFrame()
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            print("No data retrieved!")
    except Exception as e:
        print("Error reading CSV file:", e)
    print("CSV data:\n", df.head())
    return df

