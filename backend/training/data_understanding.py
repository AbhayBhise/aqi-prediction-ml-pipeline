import pandas as pd
import numpy as np

# 1. Load the dataset
file_path = 'INDIA_AQI_COMPLETE_20251126.csv'
print(f"Loading dataset: {file_path}...")
df = pd.read_csv(file_path)

# 2. Display First and Last 5 rows
print("\n" + "="*50)
print("FIRST 5 ROWS")
print("="*50)
print(df.head())

print("\n" + "="*50)
print("LAST 5 ROWS")
print("="*50)
print(df.tail())

# 3. Print Shape and Column Names
print("\n" + "="*50)
print("DATASET OVERVIEW")
print("="*50)
print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
print("\nFull List of Columns:")
print(df.columns.tolist())

# 4. Group columns into categories
pollutant_cols = [
    'PM2_5_ugm3', 'PM10_ugm3', 'PM_Ratio', 'CO_ugm3', 'NO2_ugm3', 
    'SO2_ugm3', 'O3_ugm3', 'Dust_ugm3', 'NH3_ugm3', 'AOD'
]
weather_cols = [
    'Temp_2m_C', 'Temp_80m_C', 'Temp_120m_C', 'Temp_180m_C', 
    'Humidity_Percent', 'Dew_Point_C', 'Humidity_Category', 
    'Wind_Speed_10m_kmh', 'Wind_Speed_80m_kmh', 'Wind_Speed_120m_kmh', 
    'Wind_Dir_10m', 'Wind_Gusts_kmh', 'Wind_Category', 'Wind_Stagnation', 
    'Precipitation_mm', 'Rain_mm', 'Is_Raining', 'Heavy_Rain', 
    'Pressure_MSL_hPa', 'Surface_Pressure_hPa', 'Solar_Radiation_Wm2', 
    'Direct_Radiation_Wm2', 'Diffuse_Radiation_Wm2', 'UV_Index', 
    'Cloud_Cover_Percent', 'Cloud_Low_Percent', 'Cloud_Mid_Percent', 
    'Cloud_High_Percent', 'Is_Daytime', 'Sunshine_Seconds', 
    'Temp_Inversion', 'Inversion_Strength_C'
]
time_cols = [
    'Datetime', 'Year', 'Month', 'Day', 'Hour', 'Day_of_Week', 
    'Day_Name', 'Week_of_Year', 'Is_Weekend', 'Quarter', 'Season', 
    'Time_of_Day', 'Festival_Period', 'Crop_Burning_Season'
]
target_cols = ['AQI_Category']
aqi_derived_cols = [
    'US_AQI', 'US_AQI_PM25', 'US_AQI_PM10', 'US_AQI_NO2', 'US_AQI_O3', 
    'US_AQI_CO', 'EU_AQI', 'EU_AQI_PM25', 'EU_AQI_PM10', 'PM25_Category_India'
]
other_cols = [c for c in df.columns if c not in pollutant_cols + weather_cols + time_cols + target_cols + aqi_derived_cols]

print("\n" + "="*50)
print("COLUMN CATEGORIZATION")
print("="*50)
print(f"A. Pollutants ({len(pollutant_cols)}): {pollutant_cols}")
print(f"B. Weather ({len(weather_cols)}): {weather_cols}")
print(f"C. Time ({len(time_cols)}): {time_cols}")
print(f"D. Target ({len(target_cols)}): {target_cols}")
print(f"E. AQI-Derived ({len(aqi_derived_cols)}): {aqi_derived_cols}")
print(f"F. Others ({len(other_cols)}): {other_cols}")

# 5. Show Data types and Missing Values
print("\n" + "="*50)
print("DATA TYPES AND MISSING VALUES")
print("="*50)
info_df = pd.DataFrame({
    'Data Type': df.dtypes,
    'Missing Values': df.isnull().sum()
}).sort_values(by='Missing Values', ascending=False)
print(info_df)

# 6. Check for Duplicate Columns and Constant Columns
print("\n" + "="*50)
print("DATA QUALITY CHECKS")
print("="*50)

# Duplicate Columns
# Using a faster way to check for identical data in columns
duplicate_cols = []
cols = df.columns
for i in range(len(cols)):
    for j in range(i + 1, len(cols)):
        if df[cols[i]].equals(df[cols[j]]):
            duplicate_cols.append((cols[i], cols[j]))

print(f"Duplicate Columns (identical data): {duplicate_cols if duplicate_cols else 'None'}")

# Constant Columns
constant_cols = [c for c in df.columns if df[c].nunique() == 1]
print(f"Constant Columns (only one unique value): {constant_cols if constant_cols else 'None'}")

# 7. Summary
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

print("\n" + "="*50)
print("SUMMARY STATS")
print("="*50)
print(f"Number of Numerical Columns: {len(num_cols)}")
print(f"Number of Categorical Columns: {len(cat_cols)}")
