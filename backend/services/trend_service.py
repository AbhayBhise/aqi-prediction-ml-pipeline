def analyze_trend(current_aqi, current_category, forecast_sequence):
    """
    Analyzes the quantitative trend in AQI based on the forecast.
    Note: For a fully accurate trend, the models would need to output numerical AQI values.
    Since models output categories, we approximate the "AQI value" using the category midpoints.
    
    Category Midpoints:
    Good: 25
    Moderate: 75
    Unhealthy_Sensitive: 125
    Unhealthy: 175
    Very_Unhealthy: 250
    Hazardous: 400
    """
    midpoints = {
        "Good": 25,
        "Moderate": 75,
        "Unhealthy_Sensitive": 125,
        "Unhealthy": 175,
        "Very_Unhealthy": 250,
        "Hazardous": 400
    }
    
    current_val = current_aqi if current_aqi else midpoints.get(current_category, 75)
    
    if not forecast_sequence:
        return None
        
    peak_val = -1
    peak_time = None
    
    for f in forecast_sequence:
        f_val = midpoints.get(f['category'], 75)
        if f_val > peak_val:
            peak_val = f_val
            peak_time = f['time']
            
    increase = peak_val - current_val
    
    trend = "Stable"
    if increase > 20:
        trend = "Increasing"
    elif increase < -20:
        trend = "Decreasing"
        
    return {
        "current_approx": current_val,
        "predicted_peak": peak_val,
        "increase": increase,
        "peak_time": peak_time,
        "trend_direction": trend
    }
