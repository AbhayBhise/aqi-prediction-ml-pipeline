import pandas as pd
import numpy as np
import joblib
import os
import time
import sys
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, balanced_accuracy_score, classification_report
from sklearn.utils.class_weight import compute_sample_weight

# Non-interactive matplotlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

def log(msg):
    print(f"[MODEL_TRAINING] {msg}")
    sys.stdout.flush()

# Path resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
PROCESSED_DIR = os.path.join(PROJECT_ROOT, 'data', 'processed')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
MODELS_DIR = os.path.join(PROCESSED_DIR, 'all_models')

if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR)

def train_and_persist():
    log("Loading UI dataset...")
    x_path = os.path.join(PROCESSED_DIR, 'X_train_UI.joblib')
    y_path = os.path.join(PROCESSED_DIR, 'y_train_UI.joblib')
    
    if not os.path.exists(x_path):
        log(f"ERROR: Could not find {x_path}")
        return

    X = joblib.load(x_path)
    y = joblib.load(y_path)
    
    # Force to numpy for robust positional indexing
    if hasattr(X, "values"): X = X.values
    if hasattr(y, "values"): y = y.values
    
    log(f"Original dataset size: {X.shape}")

    # We use a 100k sample for fast demo training while maintaining research validity
    if len(X) > 100000:
        log("Sampling 100,000 rows for training...")
        np.random.seed(42)
        indices = np.random.choice(len(X), 100000, replace=False)
        X_train = X[indices]
        y_train = y[indices]
    else:
        X_train = X
        y_train = y

    log(f"Training set ready: {X_train.shape}")

    # Test set
    X_test = joblib.load(os.path.join(PROCESSED_DIR, 'X_test_UI.joblib'))
    y_test = joblib.load(os.path.join(PROCESSED_DIR, 'y_test_UI.joblib'))
    if hasattr(X_test, "values"): X_test = X_test.values
    if hasattr(y_test, "values"): y_test = y_test.values

    target_mapping = joblib.load(os.path.join(PROCESSED_DIR, 'target_mapping.joblib'))
    reverse_mapping = {v: k for k, v in target_mapping.items()}
    class_names = [reverse_mapping[i] for i in range(len(reverse_mapping))]

    models_to_train = {
        "Logistic_Regression": LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42),
        "Decision_Tree": DecisionTreeClassifier(random_state=42, class_weight='balanced', min_samples_leaf=5),
        "Random_Forest": RandomForestClassifier(
            n_estimators=100,
            max_depth=18,
            min_samples_leaf=5,
            class_weight='balanced_subsample',
            random_state=42,
            n_jobs=1
        ),
        "Hist_Gradient_Boosting": HistGradientBoostingClassifier(
            learning_rate=0.08,
            max_iter=250,
            l2_regularization=0.05,
            random_state=42
        ),
        "KNN": KNeighborsClassifier(n_neighbors=5, n_jobs=1),
        "SVM_SGD": SGDClassifier(loss='hinge', class_weight='balanced', random_state=42),
        "Naive_Bayes": GaussianNB(),
        "ANN": MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=100, random_state=42, early_stopping=True),
        "DNN": MLPClassifier(hidden_layer_sizes=(128, 64, 32), max_iter=100, random_state=42, early_stopping=True)
    }

    comparison_results = []

    for name, model in models_to_train.items():
        log(f"--- Processing {name} ---")
        t0 = time.time()
        sample_weight = compute_sample_weight(class_weight='balanced', y=y_train)
        if name in {"Hist_Gradient_Boosting", "Naive_Bayes"}:
            model.fit(X_train, y_train, sample_weight=sample_weight)
        else:
            model.fit(X_train, y_train)
        train_time = time.time() - t0
        
        log(f"Evaluating {name}...")
        y_pred = model.predict(X_test)
        
        report = classification_report(
            y_test,
            y_pred,
            target_names=class_names,
            output_dict=True,
            zero_division=0
        )
        very_unhealthy_recall = report.get('Very_Unhealthy', {}).get('recall', 0.0)
        hazardous_recall = report.get('Hazardous', {}).get('recall', 0.0)

        metrics = {
            "Model": name.replace("_", " "),
            "Accuracy": float(accuracy_score(y_test, y_pred)),
            "Precision": float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
            "Recall": float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
            "F1Score": float(f1_score(y_test, y_pred, average='weighted', zero_division=0)),
            "BalancedAccuracy": float(balanced_accuracy_score(y_test, y_pred)),
            "MacroRecall": float(recall_score(y_test, y_pred, average='macro', zero_division=0)),
            "MacroF1": float(f1_score(y_test, y_pred, average='macro', zero_division=0)),
            "VeryUnhealthyRecall": float(very_unhealthy_recall),
            "HazardousRecall": float(hazardous_recall),
            "SevereClassRecall": float((very_unhealthy_recall + hazardous_recall) / 2),
            "Time": float(train_time)
        }
        comparison_results.append(metrics)
        
        # Save model
        model_path = os.path.join(MODELS_DIR, f"{name.lower()}.joblib")
        joblib.dump(model, model_path)
        log(f"Saved {name} model.")

        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=class_names, yticklabels=class_names)
        plt.title(f'CM: {name.replace("_", " ")}')
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        plt.tight_layout()
        cm_path = os.path.join(RESULTS_DIR, f"cm_{name.lower()}.png")
        plt.savefig(cm_path)
        plt.close()

    # Save comparison report as JSON
    import json
    report_path = os.path.join(RESULTS_DIR, 'ui_model_comparison.json')
    with open(report_path, 'w') as f:
        json.dump(comparison_results, f, indent=4)
    
    log(f"All {len(models_to_train)} models persisted successfully. Report saved to {report_path}")

if __name__ == "__main__":
    train_and_persist()
