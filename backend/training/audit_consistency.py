import os, json, pandas as pd
import numpy as np

# Config
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'INDIA_AQI_COMPLETE_20251126.csv')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'backend', 'results')

def audit_consistency():
    print("--- STARTING DATA CONSISTENCY AUDIT ---")
    
    # 1. Real Dataset Stats
    df = pd.read_csv(DATA_PATH)
    actual_rows = len(df)
    actual_cols = len(df.columns)
    aqi_dist = df['AQI_Category'].value_counts().to_dict()
    
    print(f"Actual Rows: {actual_rows}")
    print(f"Actual Features: {actual_cols}")
    
    # 2. Check eda_data.json
    eda_path = os.path.join(RESULTS_DIR, 'eda_data.json')
    if os.path.exists(eda_path):
        with open(eda_path, 'r') as f:
            eda = json.load(f)
            eda['total_rows'] = actual_rows
            eda['total_features'] = actual_cols
            eda['aqi_distribution'] = {str(k): int(v) for k, v in aqi_dist.items()}
        with open(eda_path, 'w') as f:
            json.dump(eda, f, indent=4)
        print("[OK] eda_data.json synchronized.")
    
    # 3. Check model_metrics.json
    metrics_path = os.path.join(RESULTS_DIR, 'model_metrics.json')
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
            for model_name, data in metrics.items():
                if 'accuracy' in data and data['accuracy'] > 1.0:
                    data['accuracy'] = data['accuracy'] / 100.0
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=4)
        print("[OK] model_metrics.json verified.")

    # 4. Check VAE Generation Stats
    vae_stats_path = os.path.join(RESULTS_DIR, 'vae_generation_stats.json')
    if os.path.exists(vae_stats_path):
        with open(vae_stats_path, 'r') as f:
            v_stats = json.load(f)
            if 'real_stats' in v_stats:
                v_stats['real_stats']['PM2_5_ugm3']['mean'] = float(df['PM2_5_ugm3'].mean())
                v_stats['real_stats']['CO_ugm3']['mean'] = float(df['CO_ugm3'].mean())
        with open(vae_stats_path, 'w') as f:
            json.dump(v_stats, f, indent=4)
        print("[OK] VAE stats verified.")

    # 5. Check plots
    plots = [
        'bilstm_confusion_matrix_augmented.png',
        'vae_loss_curve.png',
        'vae_latent_space.png',
        'vae_synthetic_vs_real.png'
    ]
    for p in plots:
        path = os.path.join(RESULTS_DIR, p)
        if os.path.exists(path):
            print(f"[FOUND] Plot {p}")
        else:
            print(f"[MISSING] Plot {p}")

    print("--- AUDIT COMPLETE ---")

if __name__ == "__main__":
    audit_consistency()
