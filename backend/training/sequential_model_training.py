import os
import json
import time
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, f1_score, accuracy_score
import joblib

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw', 'INDIA_AQI_CLEANED_FINAL.csv')
MODEL_DIR = os.path.join(PROJECT_ROOT, 'backend', 'models')
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'backend', 'results')
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Device Configuration (Automatic GPU detection)
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {DEVICE}")


# Constants
SEQUENCE_LENGTH = 12
HORIZONS = [1, 4, 6, 12, 24]
CATEGORY_ORDER = ["Good", "Moderate", "Unhealthy_Sensitive", "Unhealthy", "Very_Unhealthy", "Hazardous"]
CAT_TO_ID = {cat: i for i, cat in enumerate(CATEGORY_ORDER)}

# Features (14-channel input)
POLLUTANTS = ['PM2_5_ugm3', 'PM10_ugm3', 'NO2_ugm3', 'CO_ugm3', 'SO2_ugm3', 'O3_ugm3']
WEATHER = ['Temp_2m_C', 'Humidity_Percent']
TIME_CYC = ['hour_sin', 'hour_cos', 'month_sin', 'month_cos']
EVENTS = ['Festival_Period', 'Crop_Burning_Season']
FEATURES = POLLUTANTS + WEATHER + TIME_CYC + EVENTS

# 1. Models
class Attention(nn.Module):
    def __init__(self, hidden_dim):
        super(Attention, self).__init__()
        self.attn = nn.Linear(hidden_dim, 1)

    def forward(self, x):
        # x: (batch, seq, hidden)
        attn_weights = torch.softmax(self.attn(x), dim=1)
        # attn_weights: (batch, seq, 1)
        context = torch.sum(attn_weights * x, dim=1)
        # context: (batch, hidden)
        return context, attn_weights

class AQI_LSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim=128, num_layers=2, num_classes=6):
        super(AQI_LSTM, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True, dropout=0.3)
        self.attention = Attention(hidden_dim)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        out, _ = self.lstm(x)
        context, _ = self.attention(out)
        return self.fc(context)

class AQI_BiLSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim=128, num_layers=2, num_classes=6):
        super(AQI_BiLSTM, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True, dropout=0.3, bidirectional=True)
        self.attention = Attention(hidden_dim * 2)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * 2, 128),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        out, _ = self.lstm(x)
        context, _ = self.attention(out)
        return self.fc(context)

# 2. Data Processing
def load_and_preprocess():
    log("Loading dataset (drastic memory optimization mode)...")
    # ONLY load columns that actually exist in the CSV
    csv_cols = POLLUTANTS + WEATHER + EVENTS + ['City', 'Datetime', 'AQI_Category']
    df = pd.read_csv(DATA_PATH, usecols=csv_cols)
    
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df.sort_values(['City', 'Datetime'], inplace=True)
    
    # Fill gaps per city (optimized)
    for city, city_df in df.groupby('City'):
        df.loc[city_df.index, POLLUTANTS + WEATHER + EVENTS] = city_df[POLLUTANTS + WEATHER + EVENTS].ffill().bfill()

    # Cyclical Time (float32) - Create these AFTER loading
    df['hour_sin'] = np.sin(2 * np.pi * df['Datetime'].dt.hour / 24).astype(np.float32)
    df['hour_cos'] = np.cos(2 * np.pi * df['Datetime'].dt.hour / 24).astype(np.float32)
    df['month_sin'] = np.sin(2 * np.pi * (df['Datetime'].dt.month - 1) / 12).astype(np.float32)
    df['month_cos'] = np.cos(2 * np.pi * (df['Datetime'].dt.month - 1) / 12).astype(np.float32)

    # Convert all pollutant/weather features to float32
    float_cols = POLLUTANTS + WEATHER + EVENTS + TIME_CYC
    df[float_cols] = df[float_cols].astype(np.float32)
    
    gc.collect()
    return df

import sys
import gc

def log(msg):
    print(msg)
    sys.stdout.flush()

def create_sequential_data(df, horizon_hours):
    log(f"\n--- Processing {horizon_hours}h Horizon ---")
    
    # 1. Scale features on a copy
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df[FEATURES].astype(np.float32))
    
    # 2. Extract targets and city boundaries
    city_ids = df['City'].values
    target_values = df['AQI_Category'].map(CAT_TO_ID).values
    
    # Calculate total sequences first to pre-allocate
    total_sequences = 0
    city_indices = {}
    for city in np.unique(city_ids):
        mask = (city_ids == city)
        n_rows = np.sum(mask)
        n_seq = n_rows - (SEQUENCE_LENGTH + horizon_hours - 1)
        if n_seq > 0:
            total_sequences += n_seq
            city_indices[city] = np.where(mask)[0]
    
    log(f"  > Pre-allocating memory for {total_sequences} sequences...")
    X_final = np.zeros((total_sequences, SEQUENCE_LENGTH, len(FEATURES)), dtype=np.float32)
    y_final = np.zeros(total_sequences, dtype=np.int64)
    
    # 3. Fill arrays
    current_idx = 0
    for city, idxs in city_indices.items():
        city_feat = scaled_features[idxs]
        city_targ = target_values[idxs]
        
        n_seq = len(idxs) - (SEQUENCE_LENGTH + horizon_hours - 1)
        
        # Sliding window view
        feat_view = np.lib.stride_tricks.sliding_window_view(city_feat, (SEQUENCE_LENGTH, len(FEATURES))).squeeze()
        if feat_view.ndim == 2: feat_view = feat_view[np.newaxis, :, :]
        
        target_idxs = np.arange(SEQUENCE_LENGTH + horizon_hours - 1, len(idxs))
        
        X_final[current_idx : current_idx + n_seq] = feat_view[:n_seq]
        y_final[current_idx : current_idx + n_seq] = city_targ[target_idxs[:n_seq]]
        current_idx += n_seq
        
    log(f"  > Final shapes: X={X_final.shape}, y={y_final.shape}")
    return X_final, y_final, scaler

# 3. Training Function (optimized memory)
def train_model(model, train_loader, val_loader, class_weights, model_name, horizon):
    criterion = nn.CrossEntropyLoss(weight=class_weights.to(DEVICE))
    optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', patience=3, factor=0.5)
    
    best_f1 = 0
    patience = 8
    counter = 0
    
    log(f"\nTraining {model_name} ({horizon}h)...")
    for epoch in range(50):
        model.train()
        train_loss = 0
        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(DEVICE), batch_y.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            train_loss += loss.item()

        # Validation
        model.eval()
        val_preds, val_true = [], []
        with torch.no_grad():
            for batch_X, batch_y in val_loader:
                batch_X, batch_y = batch_X.to(DEVICE), batch_y.to(DEVICE)
                outputs = model(batch_X)
                preds = torch.argmax(outputs, dim=1)
                val_preds.extend(preds.cpu().numpy())
                val_true.extend(batch_y.cpu().numpy())
        
        curr_f1 = f1_score(val_true, val_preds, average='macro')
        curr_acc = accuracy_score(val_true, val_preds)
        
        log(f"Epoch {epoch+1:02d} | Loss: {train_loss/len(train_loader):.4f} | Val F1: {curr_f1:.4f} | Val Acc: {curr_acc:.4f}")
        
        scheduler.step(curr_f1)
        
        if curr_f1 > best_f1:
            best_f1 = curr_f1
            counter = 0
            torch.save(model.state_dict(), os.path.join(MODEL_DIR, f"{model_name.lower()}_{horizon}h.pt"))
        else:
            counter += 1
            if counter >= patience:
                log("Early stopping triggered.")
                break
    
    return best_f1

# 4. Main Loop
def run_full_training():
    all_results = []
    for horizon in HORIZONS:
        meta_path = os.path.join(MODEL_DIR, f"meta_{horizon}h.json")
        if os.path.exists(meta_path):
            log(f"Resuming: Found existing results for {horizon}h. Skipping...")
            with open(meta_path, 'r') as f:
                all_results.append(json.load(f))
            continue

        # Load and process fresh for each horizon to save memory during training
        df = load_and_preprocess()
        X, y, scaler = create_sequential_data(df, horizon)
        
        # We NO LONGER need df once X, y are created
        del df
        gc.collect()
        
        log(f"  > Dataset cleared. Training on {len(X)} sequences...")
        
        # Split
        train_idx = int(0.8 * len(X))
        X_train, X_val = X[:train_idx], X[train_idx:]
        y_train, y_val = y[:train_idx], y[train_idx:]
        
        # Clear large X, y to save memory
        del X, y
        gc.collect()
        
        # Weights
        class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
        class_weights = torch.tensor(class_weights, dtype=torch.float32)
        
        # Use as_tensor to avoid copies, pin_memory for faster GPU transfer
        pin = True if DEVICE.type == 'cuda' else False
        train_loader = DataLoader(TensorDataset(torch.as_tensor(X_train), torch.as_tensor(y_train)), batch_size=256, shuffle=True, pin_memory=pin)
        val_loader = DataLoader(TensorDataset(torch.as_tensor(X_val), torch.as_tensor(y_val)), batch_size=256, pin_memory=pin)

        
        # Train LSTM
        lstm_model_path = os.path.join(MODEL_DIR, f"lstm_{horizon}h.pt")
        lstm = AQI_LSTM(len(FEATURES)).to(DEVICE)
        if os.path.exists(lstm_model_path):
            log(f"  > LSTM model for {horizon}h already exists. Loading...")
            lstm.load_state_dict(torch.load(lstm_model_path, map_location=DEVICE))
            # We still need to calculate F1 for the meta dict
            lstm.eval()
            val_preds, val_true = [], []
            with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    batch_X, batch_y = batch_X.to(DEVICE), batch_y.to(DEVICE)
                    outputs = lstm(batch_X)
                    preds = torch.argmax(outputs, dim=1)
                    val_preds.extend(preds.cpu().numpy())
                    val_true.extend(batch_y.cpu().numpy())
            lstm_f1 = f1_score(val_true, val_preds, average='macro')
        else:
            lstm_f1 = train_model(lstm, train_loader, val_loader, class_weights, "LSTM", horizon)
            
        del lstm
        gc.collect()
        
        # Train BiLSTM
        bilstm_model_path = os.path.join(MODEL_DIR, f"bilstm_{horizon}h.pt")
        bilstm = AQI_BiLSTM(len(FEATURES)).to(DEVICE)
        if os.path.exists(bilstm_model_path):
             log(f"  > BiLSTM model for {horizon}h already exists. Loading...")
             bilstm.load_state_dict(torch.load(bilstm_model_path, map_location=DEVICE))
             bilstm.eval()
             val_preds, val_true = [], []
             with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    batch_X, batch_y = batch_X.to(DEVICE), batch_y.to(DEVICE)
                    outputs = bilstm(batch_X)
                    preds = torch.argmax(outputs, dim=1)
                    val_preds.extend(preds.cpu().numpy())
                    val_true.extend(batch_y.cpu().numpy())
             bilstm_f1 = f1_score(val_true, val_preds, average='macro')
        else:
            bilstm_f1 = train_model(bilstm, train_loader, val_loader, class_weights, "BiLSTM", horizon)
            
        del bilstm
        gc.collect()
        
        # Clear training data
        del X_train, X_val, y_train, y_val, train_loader, val_loader
        gc.collect()
        
        # Save Scaler and Metadata
        meta = {
            "features": FEATURES,
            "horizon": horizon,
            "lstm_f1": lstm_f1,
            "bilstm_f1": bilstm_f1,
            "classes": CATEGORY_ORDER
        }
        joblib.dump(scaler, os.path.join(MODEL_DIR, f"scaler_{horizon}h.joblib"))
        with open(meta_path, 'w') as f:
            json.dump(meta, f)
            
        all_results.append(meta)
        log(f"--- Completed {horizon}h Horizon ---")
        
    with open(os.path.join(RESULTS_DIR, 'sequential_results.json'), 'w') as f:
        json.dump(all_results, f, indent=4)


if __name__ == "__main__":
    run_full_training()
