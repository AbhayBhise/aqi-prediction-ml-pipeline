import pandas as pd
import numpy as np
import json
import joblib
import sys
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

def log(msg):
    print(msg)
    sys.stdout.flush()

# 1. Load feature_groups.json
log("Loading feature_groups.json...")
with open('feature_groups.json', 'r') as f:
    feature_config = json.load(f)

ui_features = feature_config['UI_Features']
research_features = feature_config['Research_Features']
# User requested to REMOVE specific columns from research features
removal_list = ['PM_Ratio', 'Dust_ugm3', 'AOD']
research_features = [f for f in research_features if f not in removal_list]

# Clustering features (ONLY these 9)
clustering_features_manual = [
    'PM2_5_ugm3', 'PM10_ugm3', 'NO2_ugm3', 'CO_ugm3', 'SO2_ugm3', 'O3_ugm3', 
    'Temp_2m_C', 'Humidity_Percent', 'Wind_Speed_10m_kmh'
]

target_col = 'AQI_Category'

# Load the dataset
log("Loading INDIA_AQI_CLEANED_FINAL.csv...")
df = pd.read_csv('INDIA_AQI_CLEANED_FINAL.csv')

# 2. Fix Target Encoding (Manual Ordinal Mapping)
log("Applying manual ordinal mapping to target...")
target_mapping = {
    "Good": 0,
    "Moderate": 1,
    "Unhealthy_Sensitive": 2,
    "Unhealthy": 3,
    "Very_Unhealthy": 4,
    "Hazardous": 5
}
df['target_encoded'] = df[target_col].map(target_mapping)
joblib.dump(target_mapping, 'processed_data/target_mapping.joblib')

# 3. Create Datasets
y = df['target_encoded']

# UI Model Dataset
X_ui = df[ui_features]

# Research Dataset
X_research = df[research_features]

# Clustering Dataset
X_clustering = df[clustering_features_manual]

# 4. Train-Test Split (80/20, Stratified)
log("Splitting UI dataset...")
X_train_ui_raw, X_test_ui_raw, y_train_ui, y_test_ui = train_test_split(
    X_ui, y, test_size=0.2, random_state=42, stratify=y
)

log("Splitting Research dataset...")
X_train_research_raw, X_test_research_raw, y_train_research, y_test_research = train_test_split(
    X_research, y, test_size=0.2, random_state=42, stratify=y
)

# 5. Scaling
log("Scaling datasets...")

# UI Scaler
scaler_ui = StandardScaler()
X_train_ui_scaled = scaler_ui.fit_transform(X_train_ui_raw)
X_test_ui_scaled = scaler_ui.transform(X_test_ui_raw)

# Research Scaler
scaler_research = StandardScaler()
X_train_research_scaled = scaler_research.fit_transform(X_train_research_raw)
X_test_research_scaled = scaler_research.transform(X_test_research_raw)

# Clustering Scaler (Apply to whole dataset separately)
scaler_clustering = StandardScaler()
X_clustering_scaled = scaler_clustering.fit_transform(X_clustering)

# 6. Save Artifacts
log("Saving artifacts to processed_data/...")
joblib.dump(X_train_ui_scaled, 'processed_data/X_train_UI.joblib')
joblib.dump(X_test_ui_scaled, 'processed_data/X_test_UI.joblib')
joblib.dump(y_train_ui, 'processed_data/y_train_UI.joblib')
joblib.dump(y_test_ui, 'processed_data/y_test_UI.joblib')
joblib.dump(scaler_ui, 'processed_data/scaler_UI.joblib')

joblib.dump(X_train_research_scaled, 'processed_data/X_train_Research.joblib')
joblib.dump(X_test_research_scaled, 'processed_data/X_test_Research.joblib')
joblib.dump(y_train_research, 'processed_data/y_train_Research.joblib')
joblib.dump(y_test_research, 'processed_data/y_test_Research.joblib')
joblib.dump(scaler_research, 'processed_data/scaler_Research.joblib')

joblib.dump(X_clustering_scaled, 'processed_data/X_clustering_scaled.joblib')
joblib.dump(scaler_clustering, 'processed_data/scaler_clustering.joblib')

# 7. Output Summary
log("\n" + "="*50)
log("PREPROCESSING COMPLETE - SUMMARY")
log("="*50)
log(f"UI Dataset - X_train: {X_train_ui_scaled.shape}, X_test: {X_test_ui_scaled.shape}")
log(f"Research Dataset - X_train: {X_train_research_scaled.shape}, X_test: {X_test_research_scaled.shape}")
log(f"Clustering Dataset: {X_clustering_scaled.shape}")
log("\nScaling Confirmation:")
log(f"UI Train Mean: {np.mean(X_train_ui_scaled):.5f} (should be ~0)")
log(f"UI Train Std: {np.std(X_train_ui_scaled):.5f} (should be ~1)")
log("\nAll requested datasets for UI, Research, and Clustering have been correctly produced.")
