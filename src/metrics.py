# Compute the numeric outputs (from a data frame)
    # Flight duration:  How long was the flight/data recorded 
    # Battery minimum:  What was the minimum battery voltage. We don't want it to drop too low 
    # GPS metrics:  How good was the GPS signal during the flight. We don't want it to drop too low 
    # Vibration maximum:    We don't want the vibration to be large --> flight will become unstable
    # Altitude error:   Want to check how far away drone is from ideal target altitude

def compute_metrics(df):
    flight_duration_s = df["timestamp_s"].max() - df["timestamp_s"].min()

    battery_min_v = df["battery_v"].min()

    gps_min_sats = df["gps_sats"].min()
    gps_avg_sats = df["gps_sats"].mean()

    vibe_max = df["vibe"].max()

    alt_error = df["altitude_m"] - df["target_altitude_m"]

    altitude_error_mean_abs = alt_error.abs().mean()
    altitude_error_std = alt_error.std()

    metrics = {
        "flight_duration_s": flight_duration_s,
        "battery_min_v": battery_min_v,
        "gps_min_sats": gps_min_sats,
        "gps_avg_sats": gps_avg_sats,
        "vibe_max": vibe_max,
        "altitude_error_mean_abs": altitude_error_mean_abs,
        "altitude_error_std": altitude_error_std
    }

    return metrics