import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
import os

print("Creating models directory...")
import time

start_time = time.time()
print("Loading data...")
X_train_ui = joblib.load('processed_data/X_train_UI.joblib')
y_train_ui = joblib.load('processed_data/y_train_UI.joblib')

X_train_res = joblib.load('processed_data/X_train_Research.joblib')
y_train_res = joblib.load('processed_data/y_train_Research.joblib')

print("Training Random Forest...")
rf = RandomForestClassifier(n_estimators=50, max_depth=15, random_state=42, n_jobs=-1)
rf.fit(X_train_ui, y_train_ui)
joblib.dump(rf, 'processed_data/rf_model.joblib')
print("Random Forest saved.")

print("Training DNN...")
dnn = MLPClassifier(hidden_layer_sizes=(128, 64, 32), activation='relu', solver='adam', early_stopping=True, random_state=42, max_iter=200)
dnn.fit(X_train_res, y_train_res)
joblib.dump(dnn, 'processed_data/dnn_model.joblib')
print("DNN saved.")

print(f"Done in {time.time() - start_time:.2f} seconds.")
