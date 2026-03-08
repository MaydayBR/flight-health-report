# Turn metrics into judgments
    # Is the battery okay?
    # Was GPS quality good enough?
    # Was vibration too high?
    # Was altitude control stable?
    # Overall, was this a healthy flight?

import math


def _nan_safe(fn, value, default_status="n/a", default_score=0):
    """If value is NaN, return (default_status, default_score); else call fn(value)."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return default_status, default_score
    return fn(value)


def evaluate_battery(battery_min_v):
    def _eval(v):
        if v >= 15.2:
            return "pass", 25
        elif v >= 14.8:
            return "warn", 15
        return "fail", 0

    return _nan_safe(_eval, battery_min_v)


def evaluate_gps(gps_min_sats):
    def _eval(v):
        if v >= 10:
            return "pass", 25
        elif v >= 8:
            return "warn", 15
        return "fail", 0

    return _nan_safe(_eval, gps_min_sats)


def evaluate_vibration(vibe_max):
    def _eval(v):
        if v < 20:
            return "pass", 25
        elif v < 30:
            return "warn", 15
        return "fail", 0

    return _nan_safe(_eval, vibe_max)


def evaluate_altitude(altitude_error_std):
    def _eval(v):
        if v < 0.3:
            return "pass", 25
        elif v < 0.7:
            return "warn", 15
        return "fail", 0

    return _nan_safe(_eval, altitude_error_std)


def get_overall_status(score):
    if score >= 85:
        return "Healthy"
    elif score >= 60:
        return "Warning"
    else:
        return "Poor"


def evaluate_health(metrics):
    battery_status, battery_score = evaluate_battery(metrics["battery_min_v"])
    gps_status, gps_score = evaluate_gps(metrics["gps_min_sats"])
    vibe_status, vibe_score = evaluate_vibration(metrics["vibe_max"])
    altitude_status, altitude_score = evaluate_altitude(metrics["altitude_error_std"])

    overall_score = battery_score + gps_score + vibe_score + altitude_score
    overall_status = get_overall_status(overall_score)

    results = {
        "battery_status": battery_status,
        "gps_status": gps_status,
        "vibe_status": vibe_status,
        "altitude_status": altitude_status,
        "overall_score": overall_score,
        "overall_status": overall_status
    }

    return results