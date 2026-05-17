import os
import json
import gc
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
import matplotlib.pyplot as plt
import seaborn as sns

# Import necessary parts from sequential_model_training
from sequential_model_training import (
    load_and_preprocess, create_sequential_data, 
    AQI_LSTM, AQI_BiLSTM, FEATURES, CATEGORY_ORDER
)

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
TRAINING_DIR = os.path.abspath(os.path.dirname(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(TRAINING_DIR, '..'))
RESULTS_DIR = os.path.join(BACKEND_DIR, 'results')
MODEL_DIR = os.path.join(BACKEND_DIR, 'models')

HORIZONS = [1, 4, 6, 12, 24]

def evaluate_predictions(y_true, y_pred):
    report = classification_report(
        y_true, y_pred, 
        labels=range(len(CATEGORY_ORDER)), 
        target_names=CATEGORY_ORDER, 
        output_dict=True, zero_division=0
    )
    very_unhealthy_recall = report.get("Very_Unhealthy", {}).get("recall", 0.0)
    hazardous_recall = report.get("Hazardous", {}).get("recall", 0.0)
    
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_weighted": float(precision_score(y_true, y_pred, average='weighted', zero_division=0)),
        "recall_weighted": float(recall_score(y_true, y_pred, average='weighted', zero_division=0)),
        "f1_weighted": float(f1_score(y_true, y_pred, average='weighted', zero_division=0)),
        "balanced_accuracy": float(recall_score(y_true, y_pred, average='macro', zero_division=0)), # often macro recall is used as balanced acc
        "macro_recall": float(recall_score(y_true, y_pred, average='macro', zero_division=0)),
        "macro_f1": float(f1_score(y_true, y_pred, average='macro', zero_division=0)),
        "very_unhealthy_recall": float(very_unhealthy_recall),
        "hazardous_recall": float(hazardous_recall),
        "severe_class_recall": float((very_unhealthy_recall + hazardous_recall) / 2)
    }

def main():
    print("Loading data for evaluation...")
    df = load_and_preprocess()
    
    new_metrics = []
    
    for horizon in HORIZONS:
        print(f"\nEvaluating horizon {horizon}h")
        X, y, scaler = create_sequential_data(df.copy(), horizon)
        
        train_idx = int(0.8 * len(X))
        X_val, y_val = X[train_idx:], y[train_idx:]
        train_rows = train_idx
        
        val_loader = DataLoader(TensorDataset(torch.as_tensor(X_val), torch.as_tensor(y_val)), batch_size=256, pin_memory=True if DEVICE.type=='cuda' else False)
        
        del X, y, X_val, y_val
        gc.collect()
        
        for model_class, model_name in [(AQI_LSTM, 'LSTM'), (AQI_BiLSTM, 'BiLSTM')]:
            model_path = os.path.join(MODEL_DIR, f"{model_name.lower()}_{horizon}h.pt")
            if not os.path.exists(model_path):
                print(f"Skipping {model_name} for {horizon}h (model not found)")
                continue
                
            model = model_class(len(FEATURES)).to(DEVICE)
            model.load_state_dict(torch.load(model_path, map_location=DEVICE))
            model.eval()
            
            val_preds, val_true = [], []
            with torch.no_grad():
                for batch_X, batch_y in val_loader:
                    batch_X = batch_X.to(DEVICE)
                    outputs = model(batch_X)
                    preds = torch.argmax(outputs, dim=1)
                    val_preds.extend(preds.cpu().numpy())
                    val_true.extend(batch_y.numpy())
            
            metrics = evaluate_predictions(val_true, val_preds)
            metrics['horizon_hours'] = horizon
            metrics['model'] = model_name
            metrics['train_rows'] = train_rows
            
            new_metrics.append(metrics)
            
            # Generate Confusion Matrix
            cm = confusion_matrix(val_true, val_preds, labels=range(len(CATEGORY_ORDER)))
            plt.figure(figsize=(10, 8))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                        xticklabels=CATEGORY_ORDER, yticklabels=CATEGORY_ORDER)
            plt.title(f"Confusion Matrix: {model_name} ({horizon}h Horizon)")
            plt.ylabel('Actual')
            plt.xlabel('Predicted')
            
            cm_filename = f"cm_forecast_{horizon}h_{model_name.lower()}.png"
            plt.savefig(os.path.join(RESULTS_DIR, cm_filename), bbox_inches='tight', dpi=100)
            plt.close()
            
            # Also save base CM for 1h horizon (used in ui_model_comparison tab)
            if horizon == 1:
                base_cm_filename = f"cm_{model_name.lower()}.png"
                plt.figure(figsize=(10, 8))
                sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                            xticklabels=CATEGORY_ORDER, yticklabels=CATEGORY_ORDER)
                plt.title(f"Confusion Matrix: {model_name}")
                plt.ylabel('Actual')
                plt.xlabel('Predicted')
                plt.savefig(os.path.join(RESULTS_DIR, base_cm_filename), bbox_inches='tight', dpi=100)
                plt.close()
                
        del val_loader
        gc.collect()

    print("\nUpdating JSON files...")
    
    # 1. Update forecast_model_comparison.json
    forecast_json_path = os.path.join(RESULTS_DIR, 'forecast_model_comparison.json')
    if os.path.exists(forecast_json_path):
        with open(forecast_json_path, 'r') as f:
            forecast_data = json.load(f)
            
        old_results = forecast_data.get('results', [])
        # Remove old LSTM and BiLSTM
        filtered_results = [r for r in old_results if r['model'] not in ['LSTM', 'BiLSTM']]
        # Add new metrics
        filtered_results.extend(new_metrics)
        forecast_data['results'] = filtered_results
        
        with open(forecast_json_path, 'w') as f:
            json.dump(forecast_data, f, indent=4)
            
    # 2. Update ui_model_comparison.json (only 1h horizon)
    ui_json_path = os.path.join(RESULTS_DIR, 'ui_model_comparison.json')
    if os.path.exists(ui_json_path):
        with open(ui_json_path, 'r') as f:
            ui_data = json.load(f)
            
        new_ui_data = []
        for row in ui_data:
            model_name = row['Model']
            if model_name in ['LSTM', 'BiLSTM']:
                # Find matching metric from new_metrics (horizon 1)
                match = next((m for m in new_metrics if m['model'] == model_name and m['horizon_hours'] == 1), None)
                if match:
                    new_row = {
                        "Model": model_name,
                        "Accuracy": match['accuracy'],
                        "Precision": match['precision_weighted'],
                        "Recall": match['recall_weighted'],
                        "F1Score": match['f1_weighted'],
                        "BalancedAccuracy": match['balanced_accuracy'],
                        "MacroRecall": match['macro_recall'],
                        "MacroF1": match['macro_f1'],
                        "VeryUnhealthyRecall": match['very_unhealthy_recall'],
                        "HazardousRecall": match['hazardous_recall'],
                        "SevereClassRecall": match['severe_class_recall'],
                        "Time": row.get('Time', 0.0) # Keep original time since inference time isn't measured here
                    }
                    new_ui_data.append(new_row)
                else:
                    new_ui_data.append(row)
            else:
                new_ui_data.append(row)
                
        with open(ui_json_path, 'w') as f:
            json.dump(new_ui_data, f, indent=4)
            
    print("Done! Metrics synchronized.")

if __name__ == '__main__':
    main()
