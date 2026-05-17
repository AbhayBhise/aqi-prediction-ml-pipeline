def calculate_sub_index(pollutant, value):
    """
    CPCB AQI Sub-index calculation based on Indian Standards.
    Source: CPCB AQI Calculation Table
    """
    breakpoints = {
        'PM2.5': {
            'conc': [0, 30, 60, 90, 120, 250],
            'aqi': [0, 50, 100, 200, 300, 400]
        },
        'PM10': {
            'conc': [0, 50, 100, 250, 350, 430],
            'aqi': [0, 50, 100, 200, 300, 400]
        },
        'NO2': {
            'conc': [0, 40, 80, 180, 280, 400],
            'aqi': [0, 50, 100, 200, 300, 400]
        },
        'SO2': {
            'conc': [0, 40, 80, 380, 800, 1600],
            'aqi': [0, 50, 100, 200, 300, 400]
        },
        'CO': {
            'conc': [0, 1, 2, 10, 17, 34],
            'aqi': [0, 50, 100, 200, 300, 400]
        },
        'O3': {
            'conc': [0, 50, 100, 168, 208, 748],
            'aqi': [0, 50, 100, 200, 300, 400]
        }
    }
    
    if pollutant not in breakpoints:
        return 0
    
    b = breakpoints[pollutant]
    c_list = b['conc']
    i_list = b['aqi']
    
    # piecewise linear interpolation
    for j in range(1, len(c_list)):
        if value <= c_list[j]:
            lo_c = c_list[j-1]
            hi_c = c_list[j]
            lo_i = i_list[j-1]
            hi_i = i_list[j]
            return ((hi_i - lo_i) / (hi_c - lo_c)) * (value - lo_c) + lo_i
            
    # If above max breakpoint
    if value > c_list[-1]:
        return i_list[-1] + (value - c_list[-1]) # Simple linear extension
        
    return 0

def get_aqi_category(aqi_val):
    if aqi_val <= 50: return "Good"
    if aqi_val <= 100: return "Satisfactory"
    if aqi_val <= 200: return "Moderate"
    if aqi_val <= 300: return "Poor"
    if aqi_val <= 400: return "Very Poor"
    return "Severe"

def calculate_cpcb_aqi(pollutant_data):
    """
    pollutant_data: dict with keys PM2.5, PM10, NO2, CO, SO2, O3
    Returns: { aqi, category, dominant_pollutant }
    """
    sub_indices = {}
    for p, val in pollutant_data.items():
        if p in ['PM2.5', 'PM10', 'NO2', 'CO', 'SO2', 'O3']:
            sub_indices[p] = calculate_sub_index(p, val)
    
    if not sub_indices:
        return {"aqi": 0, "category": "N/A", "dominant_pollutant": "None"}
        
    aqi = max(sub_indices.values())
    dominant = max(sub_indices, key=sub_indices.get)
    
    return {
        "aqi": round(aqi, 2),
        "category": get_aqi_category(aqi),
        "dominant_pollutant": dominant
    }
