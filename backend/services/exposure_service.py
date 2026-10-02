def calculate_exposure_score(forecast_sequence):
    """
    Calculates a 0-100 exposure score based on a sequence of predicted AQI categories.
    Higher scores indicate greater cumulative health risk.
    
    Weights (per hour of exposure):
    Good = 0
    Moderate = 15
    Unhealthy_Sensitive = 35
    Unhealthy = 60
    Very_Unhealthy = 85
    Hazardous = 100
    
    Args:
        forecast_sequence (list of dict): List of forecasts with 'horizon' and 'category'.
            e.g., [{'horizon': 1, 'category': 'Moderate'}, {'horizon': 4, 'category': 'Unhealthy'}, ...]
            We assume these represent blocks of time up to the horizon.
    """
    weights = {
        "Good": 0,
        "Moderate": 15,
        "Unhealthy_Sensitive": 35,
        "Unhealthy": 60,
        "Very_Unhealthy": 85,
        "Hazardous": 100
    }
    
    # We will interpolate the durations. 
    # e.g. 1h prediction applies to hour 1. 4h applies to hours 2,3,4. 
    # 6h applies to 5,6. 12h applies to 7..12. 24h applies to 13..24.
    
    horizons = sorted(forecast_sequence, key=lambda x: x['horizon'])
    
    total_score = 0
    total_hours = 0
    last_h = 0
    
    for f in horizons:
        h = f['horizon']
        cat = f['category']
        duration = h - last_h
        
        if duration > 0:
            weight = weights.get(cat, 0)
            total_score += weight * duration
            total_hours += duration
            
        last_h = h
        
    if total_hours == 0:
        return 0
        
    normalized_score = int(total_score / total_hours)
    return min(100, max(0, normalized_score))

def compute_exposure_scores(forecasts_today, forecasts_tomorrow):
    """
    Computes and compares exposure scores for today (next 24h) and tomorrow.
    """
    today_score = calculate_exposure_score(forecasts_today)
    tomorrow_score = calculate_exposure_score(forecasts_tomorrow) if forecasts_tomorrow else None
    
    improvement = None
    if tomorrow_score is not None:
        if today_score > 0:
            improvement = int(((today_score - tomorrow_score) / today_score) * 100)
        else:
            improvement = 0
            
    return {
        "today": today_score,
        "tomorrow": tomorrow_score,
        "improvement_percent": improvement
    }
