def generate_daily_summary(forecast_sequence, profile):
    """
    Programmatically generates a headline daily summary.
    """
    if not forecast_sequence:
        return "No forecast data available to generate a summary."
        
    weights = {
        "Good": 0,
        "Moderate": 1,
        "Unhealthy_Sensitive": 2,
        "Unhealthy": 3,
        "Very_Unhealthy": 4,
        "Hazardous": 5
    }
    
    # Analyze morning (6 AM - 12 PM) vs afternoon (12 PM - 6 PM) vs evening (6 PM - 12 AM)
    # Since our sequence is 1, 4, 6, 12, 24 we approximate
    # 1-4h usually covers morning or afternoon depending on current time.
    # We will just evaluate based on horizons.
    
    # Find peak severity
    peak = max(forecast_sequence, key=lambda x: weights.get(x['category'], 0))
    peak_cat = peak['category']
    peak_time = peak['time']
    
    # Simple logic mapping
    sentences = []
    
    if weights.get(peak_cat, 0) <= 1:
        sentences.append("Today is suitable for all outdoor activities.")
    else:
        if weights.get(forecast_sequence[0]['category'], 0) <= 1:
            sentences.append("Conditions are currently acceptable for outdoor activities.")
            sentences.append(f"However, pollution is expected to rise, peaking at {peak_cat.replace('_', ' ')} around {peak_time}.")
        else:
            sentences.append(f"Air quality is poor today, with a peak of {peak_cat.replace('_', ' ')} expected around {peak_time}.")
            
    # Add profile specific advice
    if profile == "Asthma" or profile == "Children":
        if weights.get(peak_cat, 0) >= 2:
            sentences.append(f"Sensitive groups should strictly avoid outdoor exposure near {peak_time}.")
            
    elif profile == "Outdoor_Worker":
        if weights.get(peak_cat, 0) >= 3:
            sentences.append("Outdoor work schedules should be adjusted to avoid peak pollution hours.")
            
    return " ".join(sentences)
