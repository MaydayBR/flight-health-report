# GOALS
#1) read CSV
#2) validate required columns
#3) return a DataFrame

# STEPS
#1) Read the CSV
#2) Check that all required columns exist
#3) Raise an error if something is missing
#4) Return the data

import pandas as pd

def load_flight_data(csv_file):
    required_columns = [
        "timestamp_s",
        "battery_v",
        "gps_sats",
        "vibe",
        "altitude_m",
        "target_altitude_m"
    ]
    data_frame = pd.read_csv(csv_file)
    missing_columns = [col for col in required_columns if col not in data_frame.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    return data_frame

