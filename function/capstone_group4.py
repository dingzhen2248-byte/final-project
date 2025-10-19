import pandas as pd
from api import get_request
import pandas as pd, numpy as np, re
from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import pandas as pd


def read_data_api(base_url, params):
    df = pd.DataFrame()
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


    

def parse_service_date(series: pd.Series) -> pd.Series:
    """兼容 45199、'45199 (00:00:00)'、正常日期字符串"""
    num1 = pd.to_numeric(series, errors="coerce")
    digits = series.astype(str).str.extract(r"(\d{5,})")[0]
    num2 = pd.to_numeric(digits, errors="coerce")
    excel_serial = num1.fillna(num2)
    dt_from_serial = pd.to_datetime("1899-12-30") + pd.to_timedelta(excel_serial, unit="D")
    dt_generic = pd.to_datetime(series, errors="coerce")
    return dt_from_serial.fillna(dt_generic)

def parse_hour(tp):
    if pd.isna(tp): return np.nan
    s = str(tp).strip().strip("()")
    try: return int(s.split(":")[0])
    except: return np.nan

def assign_route_group(name: str) -> str:
    x = str(name).lower()
    if "red" in x: return "Red"
    if "orange" in x: return "Orange"
    if "blue" in x: return "Blue"
    if "green" in x: return "Green"
    if "silver" in x: return "Silver"
    if "commuter" in x or "rail" in x: return "Commuter Rail"
    if "bus" in x: return "Bus"
    if "ferry" in x: return "Ferry"
    return "Other/Unknown"

def holidays_for(year: int):
    # US Federal Holidays
    if year == 2024:
        return pd.to_datetime([
            "2024-01-01","2024-01-15","2024-02-19","2024-04-15",
            "2024-05-27","2024-06-19","2024-07-04","2024-09-02",
            "2024-10-14","2024-11-11","2024-11-28","2024-12-25",
        ])
    if year == 2023:
        return pd.to_datetime([
            "2023-01-02","2023-01-16","2023-02-20","2023-04-17",
            "2023-05-29","2023-06-19","2023-07-04","2023-09-04",
            "2023-10-09","2023-11-10","2023-11-23","2023-12-25",
        ])
    return pd.to_datetime([])

def build_month_dataset(gse_path, routes_path, stops_path, year: int, month: int, out_path):
    # Read data
    gse = pd.read_csv(gse_path) if str(gse_path).endswith(".csv") else pd.read_excel(gse_path)
    routes = pd.read_csv(routes_path)
    stops  = pd.read_csv(stops_path)

    # Feature engineering
    gse["service_date"] = parse_service_date(gse["service_date"])
    gse["hour_of_day"]  = gse["time_period"].map(parse_hour)
    gse["day_of_week"]  = gse["service_date"].dt.dayofweek
    gse["is_weekend"]   = (gse["day_of_week"] >= 5).astype(int)
    gse["month"]        = gse["service_date"].dt.month
    gse["rush_hour_flag"] = gse["hour_of_day"].isin([7,8,16,17,18]).astype(int)
    gse["is_holiday"]   = gse["service_date"].isin(holidays_for(year)).astype(int)

    # combine route info
    rsel = routes[["route_id","route_short_name","route_long_name","route_type",
                   "route_color","route_sort_order","route_fare_class","line_id","network_id"]].copy()
    rsel["route_long_name_norm"] = rsel["route_long_name"].str.lower().str.strip()
    gse["route_or_line_norm"]    = gse["route_or_line"].str.lower().str.strip()
    gse = gse.merge(rsel, left_on="route_or_line_norm", right_on="route_long_name_norm", how="left")

    # combine stop info
    ssel = stops[["stop_id","municipality","parent_station"]]
    gse  = gse.merge(ssel, on="stop_id", how="left")
    gse["neighborhood"] = gse["municipality"]

    # compute transfer features
    route_key = np.where(gse["route_id"].notna(), gse["route_id"], gse["route_or_line_norm"])
    gse["_route_key"] = route_key
    per_stop = gse.dropna(subset=["stop_id","_route_key"]).groupby("stop_id")["_route_key"] \
                  .nunique().rename("n_routes_at_station").reset_index()
    list_stop = gse.dropna(subset=["stop_id","route_long_name"]).groupby("stop_id")["route_long_name"] \
                  .agg(lambda s: ",".join(sorted(pd.Series(s).dropna().unique()))) \
                  .rename("routes_at_station").reset_index()
    gse = gse.merge(per_stop, on="stop_id", how="left").merge(list_stop, on="stop_id", how="left")
    gse["transfer_degree"]   = np.clip((gse["n_routes_at_station"].fillna(1)-1).astype(int),0,None)
    gse["is_multi_route_hub"]= (gse["n_routes_at_station"]>=2).astype(int)

    # transfer station flag
    transfer_stations = {"Downtown Crossing","Park Street","Government Center","State","Haymarket",
                         "North Station","South Station","Back Bay","JFK/UMass","Kenmore","Copley",
                         "Airport","Harvard","Alewife","Forest Hills","Oak Grove","Sullivan Square",
                         "Wellington","Boylston","Arlington","Orient Heights"}
    gse["is_transfer_station"] = gse["station_name"].isin(transfer_stations).astype(int)

    gse["route_group"] = gse["route_or_line"].map(assign_route_group)
    gse.loc[gse["route_group"].isin(["Green","Silver"]), "route_id"] = pd.NA

    mask = (gse["service_date"].dt.year == year) & (gse["service_date"].dt.month == month)
    out  = gse.loc[mask].dropna(subset=["service_date","station_name","gated_entries"])

    # save output
    out_cols = ["service_date","time_period","station_name","route_or_line","gated_entries","stop_id",
                "hour_of_day","day_of_week","is_weekend","month","rush_hour_flag","is_holiday",
                "route_id","route_short_name","route_long_name","route_type","route_color",
                "route_sort_order","route_fare_class","line_id","network_id",
                "municipality","parent_station","is_transfer_station","n_routes_at_station",
                "transfer_degree","is_multi_route_hub","routes_at_station","neighborhood","route_group"]
    out[out_cols].to_csv(out_path, index=False)
    print(f"Saved: {out_path}  Shape: {out.shape}")


def pred_data_randomForest(train_data, pred_data):

    #train data
    x = train_data[['station_name_encoded', 'hour_of_day', 'day_of_week', 'month', 'is_weekend', 'is_holiday','is_transfer_station','n_routes_at_station','is_multi_route_hub']]
    y = train_data['gated_entries']

    # split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    # train model using RandomForestRegressor
    model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    
    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    # Print evaluation metrics
    print(f"R²: {r2:.3f} - MSE: {mse:.3f}")

    
    
    # plot actual vs predicted values
    fig1 = plt.figure(figsize=(10, 6))
    plt.scatter(x=y_test, y=y_pred)
    plt.xlabel("Actual Gated Entries")
    plt.ylabel("Predicted Gated Entries")
    plt.show()


    px = pred_data[['station_name_encoded', 'hour_of_day', 'day_of_week', 'month', 'is_weekend', 'is_holiday','is_transfer_station','n_routes_at_station','is_multi_route_hub']]

    # combine origanl data and pred data
    y_pred_all = model.predict(px)
    pre_data_with_pred = pred_data.copy()
    pre_data_with_pred["predicted_gated_entries"] = y_pred_all


    return pre_data_with_pred, model

