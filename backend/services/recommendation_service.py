def get_health_recommendations(current_aqi_category, profile):
    """
    Returns personalized contextual health recommendations based on AQI category and risk profile.
    
    Args:
        current_aqi_category (str): AQI category (e.g., 'Unhealthy', 'Good').
        profile (str): User risk profile ('General', 'Asthma', 'Children', 'Outdoor_Worker').
    """
    
    advice = []
    
    if current_aqi_category == "Good":
        advice.append("Great day for outdoor activities.")
        if profile == "Outdoor_Worker":
            advice.append("Proceed with normal outdoor work.")
            
    elif current_aqi_category == "Moderate":
        advice.append("Air quality is acceptable.")
        if profile == "Asthma" or profile == "Children":
            advice.append("Unusually sensitive individuals should consider limiting prolonged outdoor exertion.")
        elif profile == "Outdoor_Worker":
            advice.append("Normal work conditions.")
            
    elif current_aqi_category == "Unhealthy_Sensitive":
        if profile in ["Asthma", "Children"]:
            advice.append("Avoid prolonged outdoor exposure.")
            advice.append("Keep windows closed.")
        else:
            advice.append("General public is not likely to be affected.")
        if profile == "Outdoor_Worker":
            advice.append("Take more frequent breaks during heavy outdoor exertion.")
            
    elif current_aqi_category == "Unhealthy":
        advice.append("Everyone may begin to experience health effects.")
        if profile in ["Asthma", "Children"]:
            advice.append("Avoid all outdoor activities.")
            advice.append("Run air purifier if available.")
        elif profile == "Outdoor_Worker":
            advice.append("Wear an N95 mask.")
            advice.append("Reschedule physically demanding tasks.")
        else:
            advice.append("Reduce prolonged or heavy outdoor exertion.")
            
    elif current_aqi_category == "Very_Unhealthy":
        advice.append("Health warnings of emergency conditions.")
        if profile in ["Asthma", "Children"]:
            advice.append("STAY INDOORS.")
        elif profile == "Outdoor_Worker":
            advice.append("Halt non-essential outdoor work. N95 respirator mandatory.")
        else:
            advice.append("Avoid all outdoor exertion.")
            
    elif current_aqi_category == "Hazardous":
        advice.append("Health alert: everyone may experience more serious health effects.")
        advice.append("Remain indoors and keep activity levels low.")
        if profile == "Outdoor_Worker":
            advice.append("All outdoor work should be suspended.")
            
    return advice
