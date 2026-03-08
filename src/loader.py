# ArduPilot DataFlash → internal field mapping
#
# Metrics:
#   max altitude      ← BARO.Alt, AHR2.Alt, POS.Alt, QTUN.Alt
#   min battery (V)   ← BAT.Volt, CURR.Volt
#   max vibration     ← VIBE.VibeX, VibeY, VibeZ (magnitude)
#   num satellites    ← GPS.NSats, GPS2.NSats
#   flight duration   ← timestamp range
#   mode changes      ← MODE.Mode (count transitions)
#
# Plots:
#   altitude vs time  ← altitude_m (BARO/AHR2/POS/QTUN.Alt)
#   battery vs time   ← battery_v (BAT/CURR.Volt)
#   roll/pitch vs time ← roll_deg, pitch_deg (ATT or AHR2)
#   vibration vs time ← vibe (VIBE magnitude)
#   GPS path          ← gps_lat, gps_lng (GPS or POS)

import sys
import pandas as pd
import numpy as np


def _get_attr(msg, *names, default=np.nan):
    """Get first available attribute from message."""
    for name in names:
        if hasattr(msg, name):
            return getattr(msg, name)
    # Fallback: try to_dict() for DFMessage (handles format quirks)
    try:
        d = msg.to_dict()
        for name in names:
            if name in d:
                return d[name]
            # Case-insensitive match
            for k, v in d.items():
                if k.lower() == name.lower():
                    return v
    except Exception:
        pass
    return default


def _safe_float(val, default=np.nan):
    """Coerce to float; return default if invalid."""
    if val is None:
        return default
    try:
        f = float(val)
        return f if np.isfinite(f) else default
    except (TypeError, ValueError):
        return default


def _log_contents_summary(log_types_and_fields):
    """Print a summary of message types and fields found in the log."""
    print("Log contains the following message types and fields:", file=sys.stderr)
    for msg_type in sorted(log_types_and_fields.keys()):
        fields = log_types_and_fields[msg_type]
        print(f"  {msg_type}: {', '.join(fields)}", file=sys.stderr)
    print(file=sys.stderr)


def load_flight_data(bin_path):
    """
    Load flight data from an ArduPilot DataFlash binary log (.bin).

    Uses pymavlink DFReader to parse the log and extract:
    - timestamp_s: seconds from log start (TimeUS -> seconds)
    - battery_v: from CURR.Volt or BAT.Volt
    - gps_sats: from GPS.NSats or GPS.GMSat
    - vibe: vibration magnitude from VIBE (VibeX, VibeY, VibeZ) or single axis
    - altitude_m: from CTUN.Alt, NTUN.Alt, or BARO.Alt
    - target_altitude_m: from NTUN.NavAlt or CTUN.AltT (or same as altitude if missing)

    Returns a DataFrame with the required columns. Missing data is forward-filled then
    back-filled so downstream metrics/plots get a consistent time series.
    """
    try:
        from pymavlink.DFReader import DFReader_binary
    except ImportError:
        raise ImportError(
            "pymavlink is required to read .bin logs. Install with: pip install pymavlink"
        )

    log = DFReader_binary(bin_path, zero_time_base=True)

    rows_battery = []
    rows_gps = []
    rows_alt = []
    rows_target_alt = []
    rows_vibe = []
    rows_roll = []
    rows_pitch = []
    rows_gps_lat = []
    rows_gps_lng = []
    mode_values = []  # (t_s, mode) for mode change count
    log_types_and_fields = {}  # message type -> list of field names

    try:
        while True:
            m = log.recv_msg()
            if m is None:
                break
            t = m.get_type()
            # Record message type and fields (once per type)
            if t not in log_types_and_fields:
                try:
                    names = m.get_fieldnames()
                    log_types_and_fields[t] = list(names) if names is not None else []
                except Exception:
                    log_types_and_fields[t] = [
                        a for a in dir(m)
                        if not a.startswith("_") and not callable(getattr(m, a, None))
                    ]

            # Time in seconds (DFReader sets _timestamp when zero_time_base=True)
            t_s = getattr(m, "_timestamp", None)
            if t_s is None and hasattr(m, "TimeUS"):
                t_s = m.TimeUS * 1e-6

            if t_s is None:
                continue

            # Battery: BAT.Volt, CURR.Volt, POWR.Vcc (Plane/some vehicles use POWR)
            if t in ("CURR", "BAT") or t.startswith("BAT"):
                v = _safe_float(_get_attr(m, "Volt", "Voltage", "VoltR"))
                if not np.isnan(v) and v >= 0:
                    rows_battery.append((t_s, v))
            elif t == "POWR":
                v = _safe_float(_get_attr(m, "Vcc"))
                if not np.isnan(v) and v >= 0:
                    rows_battery.append((t_s, v))

            # GPS satellites: GPS.NSats, GPS2.NSats
            if t in ("GPS", "GPS2") or t.startswith("GPS"):
                n = _get_attr(m, "NSats", "GMSat", "NumSat")
                try:
                    n_val = _safe_float(n)
                    if not np.isnan(n_val) and n_val >= 0:
                        rows_gps.append((t_s, int(n_val)))
                except (TypeError, ValueError):
                    pass
                lat = _get_attr(m, "Lat")
                lng = _get_attr(m, "Lng")
                lat = _safe_float(lat)
                lng = _safe_float(lng)
                if not np.isnan(lat) and not np.isnan(lng):
                    if abs(lat) > 360 or abs(lng) > 360:
                        lat, lng = lat / 1e7, lng / 1e7
                    rows_gps_lat.append((t_s, lat))
                    rows_gps_lng.append((t_s, lng))

            # Altitude: BARO.Alt, AHR2.Alt, POS.Alt, QTUN.Alt, CTUN.Alt, NTUN.Alt
            if t == "BARO":
                alt = _get_attr(m, "Alt")
                if np.isfinite(alt):
                    rows_alt.append((t_s, alt))
            elif t == "AHR2":
                alt = _get_attr(m, "Alt")
                if np.isfinite(alt):
                    rows_alt.append((t_s, alt))
                r = _get_attr(m, "Roll")
                p = _get_attr(m, "Pitch")
                if np.isfinite(r):
                    rows_roll.append((t_s, np.degrees(r)))
                if np.isfinite(p):
                    rows_pitch.append((t_s, np.degrees(p)))
            elif t == "POS":
                alt = _get_attr(m, "Alt")
                if np.isfinite(alt):
                    rows_alt.append((t_s, alt))
                lat = _get_attr(m, "Lat")
                lng = _get_attr(m, "Lng")
                if np.isfinite(lat) and np.isfinite(lng):
                    rows_gps_lat.append((t_s, lat))
                    rows_gps_lng.append((t_s, lng))
            elif t == "QTUN":
                alt = _get_attr(m, "Alt")
                if np.isfinite(alt):
                    rows_alt.append((t_s, alt))
            elif t == "CTUN":
                alt = _get_attr(m, "Alt")
                if np.isfinite(alt):
                    rows_alt.append((t_s, alt))
                alt_t = _get_attr(m, "AltT", "TAlt")
                if np.isfinite(alt_t):
                    rows_target_alt.append((t_s, alt_t))
            elif t == "NTUN":
                alt = _get_attr(m, "Alt")
                if np.isfinite(alt):
                    rows_alt.append((t_s, alt))
                alt_t = _get_attr(m, "TAlt", "NavAlt")
                if np.isfinite(alt_t):
                    rows_target_alt.append((t_s, alt_t))

            # Roll/Pitch: ATT.Roll, ATT.Pitch (degrees in some logs, rad in others)
            if t == "ATT":
                r = _get_attr(m, "Roll")
                p = _get_attr(m, "Pitch")
                if np.isfinite(r):
                    rows_roll.append((t_s, np.degrees(r) if abs(r) <= 4 else r))
                if np.isfinite(p):
                    rows_pitch.append((t_s, np.degrees(p) if abs(p) <= 4 else p))

            # Mode changes: MODE.Mode
            if t == "MODE":
                mode = _get_attr(m, "Mode", "ModeNum")
                if mode is not np.nan and mode is not None:
                    mode_values.append((t_s, str(mode)))

            # Vibration: VIBE.VibeX, VibeY, VibeZ -> magnitude
            if t == "VIBE":
                x = _get_attr(m, "VibeX", "VibeX")
                y = _get_attr(m, "VibeY", "VibeY")
                z = _get_attr(m, "VibeZ", "VibeZ")
                if np.isfinite(x) or np.isfinite(y) or np.isfinite(z):
                    x = x if np.isfinite(x) else 0
                    y = y if np.isfinite(y) else 0
                    z = z if np.isfinite(z) else 0
                    mag = np.sqrt(x * x + y * y + z * z)
                    rows_vibe.append((t_s, mag))
    finally:
        log.close()

    # Show exactly what the log contains
    _log_contents_summary(log_types_and_fields)

    required_columns = [
        "timestamp_s",
        "battery_v",
        "gps_sats",
        "vibe",
        "altitude_m",
        "target_altitude_m",
        "roll_deg",
        "pitch_deg",
        "gps_lat",
        "gps_lng",
    ]

    if not rows_alt and not rows_battery and not rows_gps:
        raise ValueError(
            f"No supported message types (CURR/BAT, GPS, CTUN/NTUN/BARO, VIBE) found in {bin_path}. "
            "Ensure the file is an ArduPilot DataFlash .bin log."
        )

    # Build per-channel DataFrames
    def to_series(rows, name):
        if not rows:
            return pd.Series(dtype=float)
        df = pd.DataFrame(rows, columns=["t", name])
        return df.drop_duplicates(subset=["t"], keep="last").set_index("t")[name]

    def _align_series_to_index(series, target_index):
        """Map series to target_index using last-value-at-or-before (avoids float-mismatch)."""
        if series.empty:
            return pd.Series(np.nan, index=target_index)
        idx = np.searchsorted(series.index.values, target_index, side="right") - 1
        mask_before = idx < 0
        idx = np.clip(idx, 0, len(series) - 1)
        vals = series.iloc[idx].astype(float).values.copy()
        vals[mask_before] = np.nan
        out = pd.Series(vals, index=target_index)
        return out.ffill().bfill()

    battery_s = to_series(rows_battery, "battery_v")
    gps_s = to_series(rows_gps, "gps_sats")
    alt_s = to_series(rows_alt, "altitude_m")
    target_alt_s = to_series(rows_target_alt, "target_altitude_m")
    vibe_s = to_series(rows_vibe, "vibe")
    roll_s = to_series(rows_roll, "roll_deg")
    pitch_s = to_series(rows_pitch, "pitch_deg")
    gps_lat_s = to_series(rows_gps_lat, "gps_lat")
    gps_lng_s = to_series(rows_gps_lng, "gps_lng")

    # Debug: time ranges per series (helps diagnose extraction gaps)
    def _time_range(s, name):
        if s.empty:
            return f"  {name}: (empty)"
        return f"  {name}: t=[{s.index.min():.1f}, {s.index.max():.1f}] n={len(s)}"

    print("Time ranges per series:", file=sys.stderr)
    for s, name in [
        (alt_s, "altitude_m"),
        (battery_s, "battery_v"),
        (gps_s, "gps_sats"),
        (vibe_s, "vibe"),
        (gps_lat_s, "gps_lat"),
        (gps_lng_s, "gps_lng"),
    ]:
        print(_time_range(s, name), file=sys.stderr)
    print(file=sys.stderr)

    # Mode changes: count transitions in MODE.Mode
    mode_changes = 0
    if len(mode_values) >= 2:
        prev = mode_values[0][1]
        for _, mode in mode_values[1:]:
            if mode != prev:
                mode_changes += 1
            prev = mode

    # Unified time index: from min to max at ~10 Hz (CTUN typical rate)
    all_t = []
    for s in (battery_s, gps_s, alt_s, target_alt_s, vibe_s, roll_s, pitch_s, gps_lat_s, gps_lng_s):
        if not s.empty:
            all_t.extend(s.index.tolist())
    if not all_t:
        raise ValueError(f"No timestamp data found in {bin_path}")
    t_min, t_max = min(all_t), max(all_t)
    time_index = np.unique(np.round(np.arange(t_min, t_max + 0.1, 0.1), 1))

    df = pd.DataFrame(index=time_index)
    df.index.name = "timestamp_s"
    df = df.reset_index()

    for series, col in [
        (battery_s, "battery_v"),
        (gps_s, "gps_sats"),
        (alt_s, "altitude_m"),
        (target_alt_s, "target_altitude_m"),
        (vibe_s, "vibe"),
        (roll_s, "roll_deg"),
        (pitch_s, "pitch_deg"),
        (gps_lat_s, "gps_lat"),
        (gps_lng_s, "gps_lng"),
    ]:
        if series.empty:
            df[col] = np.nan
        else:
            reindexed = _align_series_to_index(series, time_index)
            df[col] = reindexed.values

    # If target altitude was never set, use altitude (no offset)
    if df["target_altitude_m"].isna().all() and not df["altitude_m"].isna().all():
        df["target_altitude_m"] = df["altitude_m"]

    # Drop rows where we have no useful data (all NaN for key channels)
    key_cols = [
        "altitude_m", "battery_v", "gps_sats", "vibe",
        "roll_deg", "pitch_deg", "gps_lat", "gps_lng",
    ]
    key_cols = [c for c in key_cols if c in df.columns]
    has_any = df[key_cols].notna().any(axis=1) if key_cols else pd.Series([True] * len(df))
    df = df.loc[has_any].copy()

    # Forward/back fill to avoid NaNs where we have at least some data
    df = df.ffill().bfill()

    if df.empty:
        raise ValueError(f"No usable rows after merging time series in {bin_path}")

    # Warn only when log contains the message type but we got no valid data
    msg_has = set(log_types_and_fields.keys())
    warn_if = {
        "battery_v": msg_has & {"BAT", "BATT", "CURR", "POWR"},
        "gps_sats": msg_has & {"GPS", "GPS2"},
        "vibe": msg_has & {"VIBE"},
        "roll_deg": msg_has & {"ATT", "AHR2"},
        "pitch_deg": msg_has & {"ATT", "AHR2"},
        "gps_lat": msg_has & {"GPS", "GPS2", "POS"},
        "gps_lng": msg_has & {"GPS", "GPS2", "POS"},
    }
    for col in required_columns:
        if col == "timestamp_s":
            continue
        if col not in df.columns or not df[col].notna().any():
            if col in warn_if and warn_if[col]:
                print(
                    f"Warning: no valid data for '{col}' (log has {', '.join(sorted(warn_if[col]))} but extraction yielded nothing).",
                    file=sys.stderr,
                )
    # Ensure all required columns exist (fill with NaN if missing)
    for c in required_columns:
        if c not in df.columns:
            df[c] = np.nan

    # Mode changes: count transitions in MODE.Mode
    mode_changes = 0
    if len(mode_values) >= 2:
        prev = mode_values[0][1]
        for _, mode in mode_values[1:]:
            if mode != prev:
                mode_changes += 1
            prev = mode

    return df[required_columns], {"mode_changes": mode_changes}
