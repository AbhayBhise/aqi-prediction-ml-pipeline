import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, f1_score
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import time
import os

print("1. Data Selection")
df = pd.read_csv('INDIA_AQI_CLEANED_FINAL.csv')
delhi_df = df[df['City'] == 'Delhi'].copy()
delhi_df['Datetime'] = pd.to_datetime(delhi_df['Datetime'])
delhi_df = delhi_df.sort_values('Datetime').reset_index(drop=True)
print(f"Total Delhi data rows: {len(delhi_df)}")

print("\n2. Feature Selection & Splits (70% Train, 10% Val, 20% Test)")
features = ['PM2_5_ugm3', 'PM10_ugm3', 'NO2_ugm3', 'CO_ugm3', 'SO2_ugm3', 'O3_ugm3']
target_mapping = {"Good": 0, "Moderate": 1, "Unhealthy_Sensitive": 2, "Unhealthy": 3, "Very_Unhealthy": 4, "Hazardous": 5}
delhi_df['Target'] = delhi_df['AQI_Category'].map(target_mapping)

split_train = int(0.70 * len(delhi_df))
split_val = int(0.80 * len(delhi_df))  # 70% + 10%

train_df = delhi_df[:split_train].copy()
val_df = delhi_df[split_train:split_val].copy()
test_df = delhi_df[split_val:].copy()
print(f"Raw Split Rows: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")

print("\n3. Preprocessing (No Leakage)")
scaler = StandardScaler()
# Fit scaler ONLY on train features
train_df[features] = scaler.fit_transform(train_df[features])
val_df[features] = scaler.transform(val_df[features])
test_df[features] = scaler.transform(test_df[features])

print("\n4. Create Sequences (length=24)")
sequence_length = 24

def create_sequences(data_df):
    X, y = [], []
    feats = data_df[features].values
    targs = data_df['Target'].values
    for i in range(len(feats) - sequence_length):
        X.append(feats[i : i + sequence_length])
        y.append(targs[i + sequence_length])
    return np.array(X), np.array(y)

X_train, y_train = create_sequences(train_df)
X_val, y_val = create_sequences(val_df)
X_test, y_test = create_sequences(test_df)

print(f"X_train shape: {X_train.shape}, y_train shape: {y_train.shape}")
print(f"X_val shape: {X_val.shape}, y_val shape: {y_val.shape}")
print(f"X_test shape: {X_test.shape}, y_test shape: {y_test.shape}")

print("\n5. Handle Class Imbalance")
# Compute class weights from train targets
classes = np.unique(y_train)
class_weights_arr = compute_class_weight('balanced', classes=classes, y=y_train)
# Some classes might be missing in train_y if it's very imbalanced, though highly unlikely for a large dataset.
weight_dict = {c: w for c, w in zip(classes, class_weights_arr)}
weights = [weight_dict.get(i, 1.0) for i in range(6)]
class_weights_t = torch.tensor(weights, dtype=torch.float32)
print("Class weights:", np.round(weights, 3))

print("\n6. Convert to PyTorch Tensors")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
class_weights_t = class_weights_t.to(device)

def get_dataloader(X, y):
    Xt = torch.tensor(X, dtype=torch.float32)
    yt = torch.tensor(y, dtype=torch.long)
    return DataLoader(TensorDataset(Xt, yt), batch_size=32, shuffle=False)

train_loader = get_dataloader(X_train, y_train)
val_loader = get_dataloader(X_val, y_val)
test_loader = get_dataloader(X_test, y_test)

print("\n7. Build Improved LSTM Model")
class ImprovedAQILSTM(nn.Module):
    def __init__(self, input_size=6, hidden_size=128, num_layers=2, num_classes=6):
        super(ImprovedAQILSTM, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                            batch_first=True, dropout=0.3, bidirectional=True)
        self.dropout = nn.Dropout(0.3)
        self.fc = nn.Linear(hidden_size * 2, num_classes) # *2 for bidirectional

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :] # Last time step
        out = self.dropout(out)
        out = self.fc(out)
        return out

model = ImprovedAQILSTM().to(device)
print(f"Using device: {device}")

print("\n8. Training (with Scheduler & Early Stopping)")
epochs = 30
criterion = nn.CrossEntropyLoss(weight=class_weights_t)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=3, factor=0.5)

train_losses, val_losses = [], []
best_val_loss = float('inf')
patience = 6
patience_counter = 0

start_time = time.time()
for epoch in range(epochs):
    model.train()
    running_loss = 0.0
    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        # Clip gradients to prevent exploding gradients in deeper LSTMs
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        running_loss += loss.item() * inputs.size(0)
    
    epoch_loss = running_loss / len(X_train)
    train_losses.append(epoch_loss)
    
    # Validation step
    model.eval()
    val_loss = 0.0
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            val_loss += loss.item() * inputs.size(0)
            
    epoch_val_loss = val_loss / len(X_val)
    val_losses.append(epoch_val_loss)
    
    print(f"Epoch [{epoch+1}/{epochs}] - Train Loss: {epoch_loss:.4f} - Val Loss: {epoch_val_loss:.4f} - LR: {optimizer.param_groups[0]['lr']:.6f}")
    
    scheduler.step(epoch_val_loss)
    
    # Early Stopping
    if epoch_val_loss < best_val_loss:
        best_val_loss = epoch_val_loss
        patience_counter = 0
        os.makedirs('processed_data', exist_ok=True)
        torch.save(model.state_dict(), 'processed_data/improved_lstm_model.pt')
    else:
        patience_counter += 1
        if patience_counter >= patience:
            print(f"Early stopping triggered at epoch {epoch+1}.")
            break

print(f"Training completed in {time.time() - start_time:.2f} seconds.")

# Load best model for evaluation
model.load_state_dict(torch.load('processed_data/improved_lstm_model.pt'))

print("\n9. Evaluation on Test Set")
model.eval()
all_preds = []
all_labels = []

with torch.no_grad():
    for inputs, labels in test_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        outputs = model(inputs)
        probs = torch.softmax(outputs, dim=1)
        _, preds = torch.max(probs, 1)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

accuracy = accuracy_score(all_labels, all_preds)
macro_f1 = f1_score(all_labels, all_preds, average='macro', zero_division=0)
print(f"\nFinal Test Accuracy: {accuracy:.4f}")
print(f"Final Test Macro F1: {macro_f1:.4f}")
print("\nClassification Report:")
print(classification_report(all_labels, all_preds, zero_division=0))

print("\n10. Visualization & Save")
os.makedirs('model_results', exist_ok=True)

plt.figure(figsize=(10, 6))
plt.plot(train_losses, label='Train Loss')
plt.plot(val_losses, label='Validation Loss')
plt.title('Improved LSTM Training & Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.tight_layout()
plt.savefig('model_results/improved_lstm_loss.png')
plt.close()

cm = confusion_matrix(all_labels, all_preds)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Oranges', 
            xticklabels=list(target_mapping.keys()), 
            yticklabels=list(target_mapping.keys()))
plt.title('Improved LSTM Confusion Matrix')
plt.ylabel('Actual')
plt.xlabel('Predicted')
plt.tight_layout()
plt.savefig('model_results/improved_lstm_cm.png')
plt.close()

torch.save(model, 'model_results/improved_lstm_full.pt')
joblib.dump(scaler, 'processed_data/improved_lstm_scaler.joblib')

print("\nOUTPUT COMPARISON:")
print("-" * 50)
print(f"{'Metric':<20} | {'Old LSTM':<10} | {'Improved LSTM':<10}")
print("-" * 50)
print(f"{'Test Accuracy':<20} | {'0.7440':<10} | {accuracy:.4f}")
print(f"{'Testing Seq Length':<20} | {'12':<10} | {sequence_length}")
print(f"{'Leakage Fixed':<20} | {'No':<10} | {'Yes'}")
print(f"{'Handles Imbalance':<20} | {'No':<10} | {'Yes'}")
print("-" * 50)
print("The improved model corrects methodological errors while applying class weights for minority class robustness.")
