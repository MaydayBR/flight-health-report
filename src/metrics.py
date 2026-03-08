# Compute the numeric outputs (from a data frame)
    # Flight duration:  How long was the flight/data recorded 
    # Battery minimum:  What was the minimum battery voltage. We don't want it to drop too low 
    # GPS metrics:  How good was the GPS signal during the flight. We don't want it to drop too low 
    # Vibration maximum:    We don't want the vibration to be large --> flight will become unstable
    # Altitude error:   Want to check how far away drone is from ideal target altitude

import numpy as np
import pandas as pd


def _safe_min(series, default=np.nan):
    """Min of series; return default if empty or all-NaN."""
    if series is None or series.empty or series.isna().all():
        return default
    return series.min()


def _safe_max(series, default=np.nan):
    """Max of series; return default if empty or all-NaN."""
    if series is None or series.empty or series.isna().all():
        return default
    return series.max()


def _safe_mean(series, default=np.nan):
    """Mean of series; return default if empty or all-NaN."""
    if series is None or series.empty or series.isna().all():
        return default
    return series.mean()


def _safe_std(series, default=np.nan):
    """Std of series; return default if empty or all-NaN."""
    if series is None or series.empty or series.isna().all():
        return default
    return series.std()


def compute_metrics(df, extras=None):
    extras = extras or {}
    flight_duration_s = np.nan
    if "timestamp_s" in df.columns and df["timestamp_s"].notna().any():
        flight_duration_s = df["timestamp_s"].max() - df["timestamp_s"].min()

    battery_min_v = _safe_min(df["battery_v"] if "battery_v" in df.columns else pd.Series(dtype=float))
    gps_min_sats = _safe_min(df["gps_sats"] if "gps_sats" in df.columns else pd.Series(dtype=float))
    gps_avg_sats = _safe_mean(df["gps_sats"] if "gps_sats" in df.columns else pd.Series(dtype=float))
    vibe_max = _safe_max(df["vibe"] if "vibe" in df.columns else pd.Series(dtype=float))
    altitude_max_m = _safe_max(df["altitude_m"] if "altitude_m" in df.columns else pd.Series(dtype=float))
    mode_changes = extras.get("mode_changes", np.nan)

    alt_error = np.nan
    altitude_error_mean_abs = np.nan
    altitude_error_std = np.nan
    if "altitude_m" in df.columns and "target_altitude_m" in df.columns:
        a = df["altitude_m"]
        b = df["target_altitude_m"]
        if a.notna().any() and b.notna().any():
            alt_error = a - b
            altitude_error_mean_abs = alt_error.abs().mean()
            altitude_error_std = _safe_std(alt_error)

    metrics = {
        "flight_duration_s": flight_duration_s,
        "altitude_max_m": altitude_max_m,
        "battery_min_v": battery_min_v,
        "vibe_max": vibe_max,
        "gps_min_sats": gps_min_sats,
        "gps_avg_sats": gps_avg_sats,
        "mode_changes": mode_changes,
        "altitude_error_mean_abs": altitude_error_mean_abs,
        "altitude_error_std": altitude_error_std,
    }

    return metrics