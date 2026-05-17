import json
import os
import sys
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


TRAINING_DIR = os.path.abspath(os.path.dirname(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(TRAINING_DIR, ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, ".."))

DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "INDIA_AQI_CLEANED_FINAL.csv")
RESULTS_DIR = os.path.join(BACKEND_DIR, "results")
FORECAST_MODEL_DIR = os.path.join(PROJECT_ROOT, "data", "processed", "forecast_models")

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(FORECAST_MODEL_DIR, exist_ok=True)

HORIZONS_HOURS = [1, 4, 6, 12, 24]
CATEGORY_ORDER = [
    "Good",
    "Moderate",
    "Unhealthy_Sensitive",
    "Unhealthy",
    "Very_Unhealthy",
    "Hazardous",
]
CATEGORY_TO_ID = {name: idx for idx, name in enumerate(CATEGORY_ORDER)}
ID_TO_CATEGORY = {idx: name for name, idx in CATEGORY_TO_ID.items()}

POLLUTANT_FEATURES = ["PM2_5_ugm3", "PM10_ugm3", "NO2_ugm3", "CO_ugm3", "SO2_ugm3", "O3_ugm3"]
WEATHER_FEATURES = [
    "Temp_2m_C",
    "Humidity_Percent",
    "Wind_Speed_10m_kmh",
    "Wind_Dir_10m",
    "Wind_Gusts_kmh",
    "Wind_Stagnation",
    "Precipitation_mm",
    "Rain_mm",
    "Is_Raining",
    "Heavy_Rain",
    "Pressure_MSL_hPa",
    "Surface_Pressure_hPa",
    "Solar_Radiation_Wm2",
    "Direct_Radiation_Wm2",
    "Diffuse_Radiation_Wm2",
    "Cloud_Cover_Percent",
    "Cloud_Low_Percent",
    "Cloud_Mid_Percent",
    "Cloud_High_Percent",
    "Is_Daytime",
    "Sunshine_Seconds",
]
TIME_FEATURES = ["Year", "Month", "Day", "Hour", "Day_of_Week"]
EVENT_FEATURES = ["Festival_Period", "Crop_Burning_Season"]
LAG_HOURS = [1, 3, 6, 12, 24]
ROLLING_WINDOWS = [3, 6, 12, 24]


def add_cyclical_features(df):
    """Encodes Hour and Month as Sine/Cosine to preserve cyclical nature."""
    df["hour_sin"] = np.sin(2 * np.pi * df["Hour"] / 24).astype("float32")
    df["hour_cos"] = np.cos(2 * np.pi * df["Hour"] / 24).astype("float32")
    df["month_sin"] = np.sin(2 * np.pi * (df["Month"] - 1) / 12).astype("float32")
    df["month_cos"] = np.cos(2 * np.pi * (df["Month"] - 1) / 12).astype("float32")
    return df


def log(message):
    print(f"[FORECAST_TRAINING] {message}")
    sys.stdout.flush()


def add_past_only_features(df):
    df = df.sort_values(["City", "Datetime"]).copy()
    grouped = df.groupby("City", sort=False)

    for col in POLLUTANT_FEATURES:
        for lag in LAG_HOURS:
            df[f"{col}_lag_{lag}h"] = grouped[col].shift(lag)

        shifted = grouped[col].shift(1)
        for window in ROLLING_WINDOWS:
            df[f"{col}_roll_mean_{window}h"] = (
                shifted.groupby(df["City"], sort=False)
                .rolling(window=window, min_periods=max(2, window // 2))
                .mean()
                .reset_index(level=0, drop=True)
            )
            df[f"{col}_roll_max_{window}h"] = (
                shifted.groupby(df["City"], sort=False)
                .rolling(window=window, min_periods=max(2, window // 2))
                .max()
                .reset_index(level=0, drop=True)
            )

    # Convert all engineered columns to float32 to save memory
    engineered_cols = [c for c in df.columns if "_lag_" in c or "_roll_" in c]
    df[engineered_cols] = df[engineered_cols].astype("float32")
    return df


def build_forecast_frame(df, horizon_hours):
    df_h = df.copy()
    grouped = df_h.groupby("City", sort=False)
    future_time = grouped["Datetime"].shift(-horizon_hours)
    df_h["target_category"] = grouped["AQI_Category"].shift(-horizon_hours)
    df_h["target_encoded"] = df_h["target_category"].map(CATEGORY_TO_ID)

    expected_delta = pd.to_timedelta(horizon_hours, unit="h")
    valid_horizon = future_time.sub(df_h["Datetime"]).eq(expected_delta)
    df_h = df_h[valid_horizon].copy()
    df_h = df_h.dropna(subset=["target_encoded"])
    df_h["target_encoded"] = df_h["target_encoded"].astype(int)
    return df_h


def chronological_split(df):
    unique_times = np.array(sorted(df["Datetime"].dropna().unique()))
    train_cut = unique_times[int(len(unique_times) * 0.70)]
    val_cut = unique_times[int(len(unique_times) * 0.85)]

    train_df = df[df["Datetime"] < train_cut].copy()
    val_df = df[(df["Datetime"] >= train_cut) & (df["Datetime"] < val_cut)].copy()
    test_df = df[df["Datetime"] >= val_cut].copy()
    return train_df, val_df, test_df


def make_preprocessor(numeric_features):
    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("city", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["City"]),
        ]
    )


def make_models(numeric_features):
    return {
        "Logistic Regression": Pipeline(
            steps=[
                ("preprocess", make_preprocessor(numeric_features)),
                (
                    "model",
                    LogisticRegression(
                        max_iter=1000,
                        class_weight="balanced",
                        random_state=42,
                        n_jobs=1,
                    ),
                ),
            ]
        ),
        "Random Forest": Pipeline(
            steps=[
                ("preprocess", make_preprocessor(numeric_features)),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=120,
                        max_depth=18,
                        min_samples_leaf=5,
                        class_weight="balanced_subsample",
                        random_state=42,
                        n_jobs=1,
                    ),
                ),
            ]
        ),
        "Hist Gradient Boosting": Pipeline(
            steps=[
                ("preprocess", make_preprocessor(numeric_features)),
                (
                    "model",
                    HistGradientBoostingClassifier(
                        learning_rate=0.08,
                        max_iter=250,
                        l2_regularization=0.05,
                        random_state=42,
                    ),
                ),
            ]
        ),
        "XGBoost": Pipeline(
            steps=[
                ("preprocess", make_preprocessor(numeric_features)),
                (
                    "model",
                    XGBClassifier(
                        n_estimators=200,
                        learning_rate=0.05,
                        max_depth=8,
                        subsample=0.8,
                        colsample_bytree=0.8,
                        objective="multi:softprob",
                        random_state=42,
                        n_jobs=1,  # Set to 1 for Windows stability
                    ),
                ),
            ]
        ),
    }


def evaluate_predictions(y_true, y_pred):
    report = classification_report(
        y_true,
        y_pred,
        labels=list(ID_TO_CATEGORY.keys()),
        target_names=[ID_TO_CATEGORY[i] for i in range(len(ID_TO_CATEGORY))],
        output_dict=True,
        zero_division=0,
    )
    very_unhealthy_recall = report["Very_Unhealthy"]["recall"]
    hazardous_recall = report["Hazardous"]["recall"]

    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_weighted": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall_weighted": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        "f1_weighted": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "macro_recall": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "very_unhealthy_recall": float(very_unhealthy_recall),
        "hazardous_recall": float(hazardous_recall),
        "severe_class_recall": float((very_unhealthy_recall + hazardous_recall) / 2),
    }


def train_forecast_models():
    log("Loading cleaned AQI data...")
    df = pd.read_csv(DATA_PATH)
    df["Datetime"] = pd.to_datetime(df["Datetime"], errors="coerce")
    df = df.dropna(subset=["City", "Datetime", "AQI_Category"])
    df = df[df["AQI_Category"].isin(CATEGORY_ORDER)].copy()

    base_numeric = POLLUTANT_FEATURES + WEATHER_FEATURES + TIME_FEATURES + EVENT_FEATURES
    available_base_numeric = [col for col in base_numeric if col in df.columns]

    log("Creating lag and rolling features from past observations only...")
    df = add_past_only_features(df)
    
    log("Applying Cyclical Time Encoding...")
    df = add_cyclical_features(df)
    
    # Memory Optimization: Downsample to recent 1.5 years
    cutoff_date = df["Datetime"].max() - pd.DateOffset(months=18)
    log(f"Memory Optimization: Filtering data since {cutoff_date.date()}")
    df = df[df["Datetime"] >= cutoff_date].copy()

    engineered_features = [
        col
        for col in df.columns
        if col.endswith("h") and ("_lag_" in col or "_roll_mean_" in col or "_roll_max_" in col)
    ]
    cyclical_features = ["hour_sin", "hour_cos", "month_sin", "month_cos"]
    numeric_features = available_base_numeric + engineered_features + cyclical_features

    results = []
    for horizon in HORIZONS_HOURS:
        log(f"Preparing {horizon}h future target...")
        horizon_df = build_forecast_frame(df, horizon)
        model_df = horizon_df[["City", "Datetime", "target_encoded"] + numeric_features].dropna().copy()
        train_df, val_df, test_df = chronological_split(model_df)

        X_train = train_df[["City"] + numeric_features]
        y_train = train_df["target_encoded"]
        X_test = test_df[["City"] + numeric_features]
        y_test = test_df["target_encoded"]

        log(
            f"{horizon}h split sizes: train={len(train_df):,}, "
            f"validation={len(val_df):,}, test={len(test_df):,}"
        )

        horizon_dir = os.path.join(FORECAST_MODEL_DIR, f"{horizon}h")
        os.makedirs(horizon_dir, exist_ok=True)

        for model_name, model in make_models(numeric_features).items():
            log(f"Training {model_name} for {horizon}h horizon...")
            started = time.time()
            model.fit(X_train, y_train)
            train_time = time.time() - started

            y_pred = model.predict(X_test)
            metrics = evaluate_predictions(y_test, y_pred)
            metrics.update(
                {
                    "horizon_hours": horizon,
                    "model": model_name,
                    "train_rows": int(len(train_df)),
                    "validation_rows": int(len(val_df)),
                    "test_rows": int(len(test_df)),
                    "train_time_seconds": float(train_time),
                }
            )
            results.append(metrics)

            # Generate and save Confusion Matrix plot
            plt.figure(figsize=(10, 8))
            cm = confusion_matrix(y_test, y_pred, labels=list(ID_TO_CATEGORY.keys()))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                        xticklabels=list(CATEGORY_ORDER), 
                        yticklabels=list(CATEGORY_ORDER))
            plt.title(f"Confusion Matrix: {model_name} ({horizon}h Horizon)")
            plt.ylabel('Actual')
            plt.xlabel('Predicted')
            
            cm_filename = f"cm_forecast_{horizon}h_{model_name.lower().replace(' ', '_')}.png"
            cm_path = os.path.join(RESULTS_DIR, cm_filename)
            plt.savefig(cm_path, bbox_inches='tight', dpi=100)
            plt.close()

            model_path = os.path.join(horizon_dir, f"{model_name.lower().replace(' ', '_')}.joblib")
            joblib.dump(model, model_path)

    output = {
        "task": "future_aqi_category_forecasting",
        "target": "AQI_Category shifted forward by horizon per city",
        "horizons_hours": HORIZONS_HOURS,
        "category_mapping": CATEGORY_TO_ID,
        "feature_policy": "No AQI-derived columns. Lag and rolling features use past observations only.",
        "split_policy": "Chronological 70/15/15 split by timestamp.",
        "results": results,
    }
    output_path = os.path.join(RESULTS_DIR, "forecast_model_comparison.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)

    log(f"Forecast results saved to {output_path}")


if __name__ == "__main__":
    train_forecast_models()
