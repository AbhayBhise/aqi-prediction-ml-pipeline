import pandas as pd
import numpy as np
import joblib
import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report, silhouette_score, balanced_accuracy_score
from sklearn.utils.class_weight import compute_sample_weight
import time

# Use non-interactive backend
import matplotlib
matplotlib.use('Agg')

def log(msg):
    print(msg)
    sys.stdout.flush()

TRAINING_DIR = os.path.abspath(os.path.dirname(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(TRAINING_DIR, '..'))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, '..'))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, 'data', 'processed')
output_dir = os.path.join(BACKEND_DIR, 'results')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 1. Load Preprocessed Data
log("Loading preprocessed data...")
X_train_ui = joblib.load(os.path.join(PROCESSED_DIR, 'X_train_UI.joblib'))
X_test_ui = joblib.load(os.path.join(PROCESSED_DIR, 'X_test_UI.joblib'))
y_train_ui = joblib.load(os.path.join(PROCESSED_DIR, 'y_train_UI.joblib'))
y_test_ui = joblib.load(os.path.join(PROCESSED_DIR, 'y_test_UI.joblib'))

X_train_res = joblib.load(os.path.join(PROCESSED_DIR, 'X_train_Research.joblib'))
X_test_res = joblib.load(os.path.join(PROCESSED_DIR, 'X_test_Research.joblib'))
y_train_res = joblib.load(os.path.join(PROCESSED_DIR, 'y_train_Research.joblib'))
y_test_res = joblib.load(os.path.join(PROCESSED_DIR, 'y_test_Research.joblib'))

X_clustering = joblib.load(os.path.join(PROCESSED_DIR, 'X_clustering_scaled.joblib'))
target_mapping = joblib.load(os.path.join(PROCESSED_DIR, 'target_mapping.joblib'))
reverse_mapping = {v: k for k, v in target_mapping.items()}

# 2. & 3. Classification Models (UI Dataset)
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42),
    "Decision Tree": DecisionTreeClassifier(random_state=42, class_weight='balanced', min_samples_leaf=5),
    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        max_depth=18,
        min_samples_leaf=5,
        class_weight='balanced_subsample',
        random_state=42,
        n_jobs=-1
    ),
    "Hist Gradient Boosting": HistGradientBoostingClassifier(
        learning_rate=0.08,
        max_iter=250,
        l2_regularization=0.05,
        random_state=42
    ),
    "KNN (Sampled)": KNeighborsClassifier(n_neighbors=5, n_jobs=-1),
    "SGDClassifier (SVM)": SGDClassifier(loss='hinge', class_weight='balanced', random_state=42),
    "Naive Bayes": GaussianNB()
}

results = []

def evaluate_model(name, model, X_train, X_test, y_train, y_test):
    log(f"Training {name}...")
    start_time = time.time()
    sample_weight = compute_sample_weight(class_weight='balanced', y=y_train)
    
    # Check if model is KNN to sample
    if "KNN" in name:
        X_tr_sub, _, y_tr_sub, _ = train_test_split(X_train, y_train, train_size=50000, stratify=y_train, random_state=42)
        model.fit(X_tr_sub, y_tr_sub)
    elif name in {"Hist Gradient Boosting", "Naive Bayes"}:
        model.fit(X_train, y_train, sample_weight=sample_weight)
    else:
        model.fit(X_train, y_train)
        
    train_time = time.time() - start_time
    log(f"Evaluating {name}...")
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='weighted')
    rec = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    macro_rec = recall_score(y_test, y_pred, average='macro', zero_division=0)
    macro_f1 = f1_score(y_test, y_pred, average='macro', zero_division=0)
    balanced_acc = balanced_accuracy_score(y_test, y_pred)
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=reverse_mapping.values(), yticklabels=reverse_mapping.values())
    plt.title(f'Confusion Matrix: {name}')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/cm_{name.replace(" ", "_")}.png')
    plt.close()
    
    # Classification Report (Targeting minority classes 1 and 5)
    report = classification_report(
        y_test,
        y_pred,
        target_names=[reverse_mapping[i] for i in range(len(reverse_mapping))],
        output_dict=True,
        zero_division=0
    )
    very_unhealthy_recall = report.get('Very_Unhealthy', {}).get('recall', 0)
    hazardous_recall = report.get('Hazardous', {}).get('recall', 0)
    
    results.append({
        "Model": name,
        "Accuracy": acc,
        "Precision": prec,
        "Recall": rec,
        "F1-Score": f1,
        "Balanced_Accuracy": balanced_acc,
        "Macro_Recall": macro_rec,
        "Macro_F1": macro_f1,
        "Hazardous_F1": report.get('Hazardous', {}).get('f1-score', 0),
        "Hazardous_Recall": hazardous_recall,
        "Very_Unhealthy_F1": report.get('Very_Unhealthy', {}).get('f1-score', 0),
        "Very_Unhealthy_Recall": very_unhealthy_recall,
        "Severe_Class_Recall": (very_unhealthy_recall + hazardous_recall) / 2,
        "Time (s)": train_time
    })

# Special import for sampling in evaluate function
from sklearn.model_selection import train_test_split

for name, model in models.items():
    evaluate_model(name, model, X_train_ui, X_test_ui, y_train_ui, y_test_ui)

# 4. ANN Model (UI Dataset)
log("Training ANN model...")
ann = MLPClassifier(hidden_layer_sizes=(64, 32), activation='relu', solver='adam', 
                    early_stopping=True, random_state=42, max_iter=200)
evaluate_model("ANN (UI Dataset)", ann, X_train_ui, X_test_ui, y_train_ui, y_test_ui)

# Plot Loss Curve for ANN
plt.figure()
plt.plot(ann.loss_curve_)
plt.title('Loss Curve: ANN (UI Dataset)')
plt.xlabel('Iterations')
plt.ylabel('Loss')
plt.savefig(f'{output_dir}/loss_ann.png')
plt.close()

# 5. DNN Model (Research Dataset)
log("Training DNN model...")
dnn = MLPClassifier(hidden_layer_sizes=(128, 64, 32), activation='relu', solver='adam', 
                    early_stopping=True, random_state=42, max_iter=200)
evaluate_model("DNN (Research Dataset)", dnn, X_train_res, X_test_res, y_train_res, y_test_res)

# Plot Loss Curve for DNN
plt.figure()
plt.plot(dnn.loss_curve_)
plt.title('Loss Curve: DNN (Research Dataset)')
plt.xlabel('Iterations')
plt.ylabel('Loss')
plt.savefig(f'{output_dir}/loss_dnn.png')
plt.close()

# 6. Clustering
log("Performing clustering on sampled data (20,000 rows)...")
X_sample, _, _, _ = train_test_split(X_clustering, np.zeros(len(X_clustering)), train_size=20000, random_state=42)

# KMeans
kmeans = KMeans(n_clusters=6, random_state=42, n_init=10)
kmeans_labels = kmeans.fit_predict(X_sample)
kmeans_sil = silhouette_score(X_sample, kmeans_labels)

# Hierarchical
hier = AgglomerativeClustering(n_clusters=6)
hier_labels = hier.fit_predict(X_sample)
hier_sil = silhouette_score(X_sample, hier_labels)

# DBSCAN
dbscan = DBSCAN(eps=1.5, min_samples=10).fit(X_sample)
dbscan_labels = dbscan.labels_
# DBSCAN might result in only one cluster or all noise; only compute silhouette if > 1 cluster
if len(set(dbscan_labels)) > 1:
    dbscan_sil = silhouette_score(X_sample, dbscan_labels)
else:
    dbscan_sil = -1

clustering_results = {
    "KMeans": kmeans_sil,
    "Hierarchical": hier_sil,
    "DBSCAN": dbscan_sil
}
log(f"Clustering Silhouettes: {clustering_results}")

# PCA Visualization
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_sample)

plt.figure(figsize=(10, 8))
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=kmeans_labels, cmap='viridis', s=5, alpha=0.5)
plt.title('PCA Visualization: KMeans Clusters')
plt.colorbar()
plt.savefig(f'{output_dir}/pca_clusters.png')
plt.close()

# 7. Final Summary
log("\nComparison Table:")
results_df = pd.DataFrame(results)
print(results_df.to_string(index=False))
results_df.to_csv(f'{output_dir}/model_comparison.csv', index=False)

log("\nClustering Summary:")
print(clustering_results)

log("\nModel training and evaluation complete.")
