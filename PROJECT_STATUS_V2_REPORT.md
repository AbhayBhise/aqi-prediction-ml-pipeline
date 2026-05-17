# Project Status Report: AQI Prediction Pipeline V2.0

## 1. Current Status
The project is currently in a **Live-Enabled Functional State**. We have successfully transitioned to a stable Python 3.10 environment and integrated real-time data ingestion.

- **Backend:** Flask API with endpoints for Nowcasting (`/predict`), Forecasting (`/forecast`), and Live Data (`/live_data`).
- **Frontend:** React + Vite Dashboard with Glassmorphic UI.
- **Data:** Historical dataset covers **Aug 2022 to Nov 2025**.
- **Live Sync:** Connected to OpenWeatherMap (OWM) for current pollutant and weather readings.

## 2. Key Features & Capabilities
- **Real-Time Nowcasting:** Users can fetch live data for 100+ cities and get instant AQI category predictions.
- **Multi-Horizon Forecasting:** Predicts AQI categories for 1h, 4h, 6h, 12h, and 24h into the future.
- **Interpretability:** Provides class probabilities (e.g., "38.4% Very Unhealthy") and confidence scores.
- **Professional Validation:** Displays advanced metrics like Macro F1 and Severe Class Recall to ensure safety in hazardous categories.
- **Modern UI:** Responsive dashboard with dark mode, interactive charts, and real-time loading states.

## 3. Current Flaws & Limitations
- **Memory Bottleneck:** The current feature engineering pipeline (Lags/Rolling windows) requires significant RAM (>1GB) for large-scale training, leading to memory errors on standard hardware.
- **Spatial Awareness:** The model predicts for a city in isolation; it doesn't yet account for "Pollution Plumes" moving from neighboring cities.
- **Seasonality Handling:** While the model uses "Month" and "Hour", it treats them as linear values rather than cyclical (e.g., it doesn't know 11 PM is next to 12 AM).
- **Inference Latency:** Loading multiple `joblib` models on the fly for each forecast horizon adds a small overhead (approx. 500ms-1s).

## 4. Risks
- **API Dependency:** Reliability is tied to the OpenWeatherMap free tier limits.
- **Version Sensitivity:** Pickled models are highly dependent on the `scikit-learn` version; moving between Python versions requires a full re-train.
- **Severe Class Accuracy:** Due to data imbalance, there is a risk of under-predicting rare "Hazardous" events if not continuously monitored.

## 5. Planned Improvements (Next Phase)
1. **Memory Optimization:** Optimize feature engineering to run on lower-RAM systems (downsampling/float32).
2. **Cyclical Feature Encoding:** Implement Sine/Cosine transforms for Time/Seasonality.
3. **Imbalance Correction:** Apply SMOTE or cost-sensitive weight adjustments.
4. **Algorithm Upgrade:** Integrate XGBoost or LightGBM for superior performance over standard HistGradientBoosting.
