import pandas as pd
import sys

def log(msg):
    print(msg)
    sys.stdout.flush()

# Load the cleaned dataset
file_path = 'INDIA_AQI_CLEANED.csv'
log(f"Loading cleaned dataset: {file_path}...")
df = pd.read_csv(file_path)
log(f"Dataset loaded. Current shape: {df.shape}")

# 1. Handle Missing Target Values (MANDATORY)
initial_rows = len(df)
df = df.dropna(subset=['AQI_Category'])
dropped_rows = initial_rows - len(df)
log(f"Removed {dropped_rows} rows where 'AQI_Category' was missing.")

# 2. Verify Target Integrity
log("\n" + "="*50)
log("TARGET INTEGRITY CHECK")
log("="*50)
log(f"Unique Categories: {df['AQI_Category'].unique()}")
log("Category Counts:")
log(str(df['AQI_Category'].value_counts()))

# 3. Convert Datetime Column
log("\nConverting 'Datetime' to datetime format...")
df['Datetime'] = pd.to_datetime(df['Datetime'])
log("'Datetime' conversion complete.")

# 4. Save Updated Dataset
final_path = 'INDIA_AQI_CLEANED_FINAL.csv'
log(f"Saving final cleaned dataset to: {final_path}...")
df.to_csv(final_path, index=False)
log("Save complete.")

# 5. Output Summary
log("\n" + "="*50)
log("FINAL ADJUSTMENTS - SUMMARY")
log("="*50)
log(f"Final Dataset Shape: {df.shape}")
log("\nTop 10 Remaining Missing Values:")
log(str(df.isnull().sum().sort_values(ascending=False).head(10)))
