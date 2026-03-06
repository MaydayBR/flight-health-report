# Turn metrics into judgments
    # Is the battery okay?
    # Was GPS quality good enough?
    # Was vibration too high?
    # Was altitude control stable?
    # Overall, was this a healthy flight?

def evaluate_battery(battery_min_v):
    if battery_min_v >= 15.2:
        return "pass", 25
    elif battery_min_v >= 14.8:
        return "warn", 15
    else:
        return "fail", 0


def evaluate_gps(gps_min_sats):
    if gps_min_sats >= 10:
        return "pass", 25
    elif gps_min_sats >= 8:
        return "warn", 15
    else:
        return "fail", 0


def evaluate_vibration(vibe_max):
    if vibe_max < 20:
        return "pass", 25
    elif vibe_max < 30:
        return "warn", 15
    else:
        return "fail", 0


def evaluate_altitude(altitude_error_std):
    if altitude_error_std < 0.3:
        return "pass", 25
    elif altitude_error_std < 0.7:
        return "warn", 15
    else:
        return "fail", 0


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