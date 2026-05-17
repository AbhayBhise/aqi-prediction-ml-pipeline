import pandas as pd
import sys

def log(msg):
    print(msg)
    sys.stdout.flush()

# Load the final cleaned dataset
file_path = 'INDIA_AQI_CLEANED_FINAL.csv'
log(f"Loading dataset: {file_path}...")
df = pd.read_csv(file_path)
log(f"Dataset loaded. Initial columns: {len(df.columns)}")

# Define pollutant and weather lists for easier selection
core_pollutants = ['PM2_5_ugm3', 'PM10_ugm3', 'NO2_ugm3', 'CO_ugm3', 'SO2_ugm3', 'O3_ugm3']
other_pollutants = ['PM_Ratio', 'Dust_ugm3', 'AOD']
weather_features = [
    'Temp_2m_C', 'Humidity_Percent', 'Wind_Speed_10m_kmh', 'Wind_Dir_10m', 
    'Wind_Gusts_kmh', 'Wind_Stagnation', 'Precipitation_mm', 'Rain_mm', 
    'Is_Raining', 'Heavy_Rain', 'Pressure_MSL_hPa', 'Surface_Pressure_hPa', 
    'Solar_Radiation_Wm2', 'Direct_Radiation_Wm2', 'Diffuse_Radiation_Wm2', 
    'Cloud_Cover_Percent', 'Cloud_Low_Percent', 'Cloud_Mid_Percent', 
    'Cloud_High_Percent', 'Is_Daytime', 'Sunshine_Seconds'
]
time_features = ['Year', 'Month', 'Day', 'Hour', 'Day_of_Week']
event_features = ['Festival_Period', 'Crop_Burning_Season']
target = ['AQI_Category']

# 1. Define Feature Groups

# A. UI Model Features (~12 features)
ui_features = core_pollutants + [
    'Temp_2m_C', 'Humidity_Percent', 'Wind_Speed_10m_kmh',
    'Hour', 'Month', 'Day_of_Week'
]

# B. Research Model Features (Comprehensive)
research_features = core_pollutants + other_pollutants + weather_features + time_features + event_features

# C. Clustering Features (Pollutants + Weather ONLY)
clustering_features = core_pollutants + other_pollutants + weather_features

# 2. Filtering and redundant removal is handled by the explicit definitions above.
# The user asked to remove specific ones: Day_Name, Week_of_Year, Quarter, Time_of_Day, Humidity_Category, Wind_Category.
# Since I only included specific ones in my lists above, these are effectively removed.

log("\n" + "="*50)
log("FEATURE SELECTION RESULTS")
log("="*50)

log(f"\nGroup A: UI Model Features ({len(ui_features)})")
log(f"Features: {ui_features}")

log(f"\nGroup B: Research Model Features ({len(research_features)})")
log(f"Features: {research_features}")

log(f"\nGroup C: Clustering Features ({len(clustering_features)})")
log(f"Features: {clustering_features}")

# 3. Output Count Comparison
log("\n" + "="*50)
log("SUMMARY COUNTS")
log("="*50)
log(f"Total Columns in Cleaned Dataset: {len(df.columns)}")
log(f"UI Model Feature Count: {len(ui_features)}")
log(f"Research Model Feature Count: {len(research_features)}")
log(f"Clustering Feature Count: {len(clustering_features)}")

# We can save these feature lists for the next phase
import json
feature_config = {
    'UI_Features': ui_features,
    'Research_Features': research_features,
    'Clustering_Features': clustering_features,
    'Target': target
}

with open('feature_groups.json', 'w') as f:
    json.dump(feature_config, f, indent=4)
log("\nFeature lists saved to 'feature_groups.json'.")
