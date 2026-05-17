import pandas as pd
import numpy as np
import sys

def log(msg):
    print(msg)
    sys.stdout.flush()

# Load the dataset
file_path = 'INDIA_AQI_COMPLETE_20251126.csv'
log(f"Loading dataset: {file_path}...")
df = pd.read_csv(file_path)
log(f"Dataset loaded. Initial shape: {df.shape}")

# 1. Drop Completely Useless Columns (100% missing)
useless_cols = [
    'NH3_ugm3', 'Temp_80m_C', 'Temp_120m_C', 'Temp_180m_C', 
    'Wind_Speed_80m_kmh', 'Wind_Speed_120m_kmh', 'UV_Index', 'Inversion_Strength_C'
]
cols_to_drop = [col for col in useless_cols if col in df.columns]
df.drop(columns=cols_to_drop, inplace=True)
log(f"Dropped useless columns: {cols_to_drop}")

# 2. Drop Duplicate Columns (Identical data)
log("Searching for duplicate columns...")
# A more efficient way to find duplicate columns
# We can sample rows to quickly eliminate non-duplicates
# For speed, we'll check columns with identical hashes or just use the subset approach
def find_duplicate_columns(df):
    duplicates = []
    columns = df.columns
    # Basic check using sampling
    potential_dupes = {}
    sample = df.sample(min(100, len(df)))
    
    for col in columns:
        sample_val = tuple(sample[col].values)
        if sample_val not in potential_dupes:
            potential_dupes[sample_val] = []
        potential_dupes[sample_val].append(col)
    
    for group in potential_dupes.values():
        if len(group) > 1:
            # Thorough check for the group
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    if df[group[i]].equals(df[group[j]]):
                        if group[j] not in duplicates:
                            duplicates.append(group[j])
    return duplicates

dup_cols = find_duplicate_columns(df)
if dup_cols:
    df.drop(columns=dup_cols, inplace=True)
    log(f"Dropped duplicate columns: {dup_cols}")
else:
    log("No additional duplicate columns found.")

# 3. Drop Constant Columns
constant_cols = ['Temp_Inversion']
cols_to_drop_const = [col for col in constant_cols if col in df.columns]
df.drop(columns=cols_to_drop_const, inplace=True)
log(f"Dropped constant columns: {cols_to_drop_const}")

# 4. Remove AQI-Derived Columns (Data Leakage)
derived_cols = [
    'US_AQI', 'US_AQI_PM25', 'US_AQI_PM10', 'US_AQI_NO2', 'US_AQI_O3', 
    'US_AQI_CO', 'EU_AQI', 'EU_AQI_PM25', 'EU_AQI_PM10', 'PM25_Category_India'
]
cols_to_drop_derived = [col for col in derived_cols if col in df.columns]
df.drop(columns=cols_to_drop_derived, inplace=True)
log(f"Dropped derived columns: {cols_to_drop_derived}")

# Save the cleaned dataset
cleaned_path = 'INDIA_AQI_CLEANED.csv'
log(f"Saving cleaned dataset to: {cleaned_path}...")
df.to_csv(cleaned_path, index=False)
log("Save complete.")

# 6. Output After Cleaning
log("\n" + "="*50)
log("CLEANING COMPLETE - SUMMARY")
log("="*50)
log(f"New Shape: {df.shape}")
log(f"Remaining Columns ({len(df.columns)}):\n{df.columns.tolist()}")

log("\nTop 10 Columns with Missing Values:")
log(str(df.isnull().sum().sort_values(ascending=False).head(10)))
