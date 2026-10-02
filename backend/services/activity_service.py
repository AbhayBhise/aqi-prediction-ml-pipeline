import pandas as pd

def plan_outdoor_activity(forecasts, duration_minutes):
    """
    Finds the optimal time window for an outdoor activity based on sliding window exposure.
    
    Args:
        forecasts (list of dict): e.g., [{'hour_offset': 1, 'category': 'Moderate', 'time': '7 AM'}, ...]
            Must be expanded to an hourly sequence (e.g. 24 items for 24 hours).
        duration_minutes (int): Duration of the activity.
        
    Returns:
        dict: Best time window, worst time window, and reason.
    """
    weights = {
        "Good": 0,
        "Moderate": 15,
        "Unhealthy_Sensitive": 35,
        "Unhealthy": 60,
        "Very_Unhealthy": 85,
        "Hazardous": 100
    }
    
    if not forecasts or len(forecasts) < 2:
        return None
        
    # Ensure forecasts are sorted by hour offset
    hourly_data = sorted(forecasts, key=lambda x: x['hour_offset'])
    
    duration_hours = max(1, round(duration_minutes / 60.0))
    
    best_window = None
    min_exposure = float('inf')
    
    worst_window = None
    max_exposure = -1
    
    # Slide window
    for i in range(len(hourly_data) - duration_hours + 1):
        window = hourly_data[i:i + duration_hours]
        exposure = sum(weights.get(hour['category'], 100) for hour in window)
        
        start_time = window[0]['time']
        end_time_offset = i + duration_hours
        
        # approximate end time string
        # for a real app, use actual datetime parsing, but keeping it simple for the demo
        if end_time_offset < len(hourly_data):
            end_time = hourly_data[end_time_offset]['time']
        else:
            end_time = "Late"
            
        if exposure < min_exposure:
            min_exposure = exposure
            best_window = {"start": start_time, "end": end_time, "exposure": exposure, "categories": [h['category'] for h in window]}
            
        if exposure > max_exposure:
            max_exposure = exposure
            worst_window = {"start": start_time, "end": end_time, "exposure": exposure, "categories": [h['category'] for h in window]}
            
    reason = "Minimizes cumulative exposure and avoids hazardous peaks."
    if best_window and all(c in ["Good", "Moderate"] for c in best_window['categories']):
        reason = "Air quality remains within safe limits for the entire duration."
        
    return {
        "best_time": f"{best_window['start']} to {best_window['end']}" if best_window else "N/A",
        "avoid_time": f"{worst_window['start']} to {worst_window['end']}" if worst_window else "N/A",
        "reason": reason
    }
