# 📑 AQI Project: VIVA TECHNICAL MASTER GUIDE

This document provides industry-level technical justifications for every major component of your project. Use these points to answer examiner questions during your Viva.

---

## 1. Project Overview & Objective
**What is this project?**
It is an **Agentic Air Quality Forecasting & Analysis System**. Unlike simple prediction models, this system integrates:
1.  **Real-time Data Integration**: Live polling of OpenWeatherMap API.
2.  **Predictive Modeling**: Multi-horizon forecasting (1h to 24h).
3.  **Agentic AI**: A reasoning chatbot that explains pollution trends using project data.
4.  **Advanced Research**: Deep learning (LSTMs) and Generative models (GANs) for data augmentation.

---

## 2. Dataset & Transformation (842,160 Rows)
**What was wrong with the raw dataset?**
-   **Missing Values**: Sensor failures caused gaps in PM2.5 and PM10 readings.
-   **No Ground Truth**: Raw pollutants don't tell you if the air is "Poor" or "Moderate" without calculation.
-   **Outliers**: Sensor noise produced impossible spikes.

**How we transformed it:**
1.  **CPCB Logic**: We implemented the official Indian **Central Pollution Control Board (CPCB)** AQI formula to calculate the "Target Class."
2.  **Imputation**: We used **Linear Interpolation** for time-series gaps and **Median Imputation** for larger city-wide gaps.
3.  **Cyclical Encoding**: We converted `Hour` (0-23) into `hour_sin` and `hour_cos`.
    -   *Why?* To ensure the model knows that Hour 23 (11 PM) is mathematically adjacent to Hour 0 (12 AM).

---

## 3. Classification & Forecasting Models (Unit I & III)

### A. HistGradientBoosting (HGB)
-   **Structure**: A tree-based ensemble using histogram binning.
-   **Why this?**: It is significantly faster than standard Random Forest for 800k+ rows and natively handles missing values.
-   **Input**: 12-15 features (Pollutants + Weather + Temporal).
-   **Output**: One of 6 AQI Categories.

### B. Random Forest
-   **Structure**: 120 estimators (trees) with a max depth of 18.
-   **Why this structure?**: We used `class_weight="balanced_subsample"` to prevent the model from ignoring rare "Severe" pollution days.

---

## 4. Sequential Deep Learning (Unit IV)

### BiLSTM with Multi-Head Attention (State-of-the-Art)
-   **Architecture**:
    -   `Input Layer`: 14 features (Pollutants, Weather, Cyclical Time, Event Flags).
    -   `Sequential Layer`: 2-layer **Bidirectional LSTM** (128 units).
    -   `Attention Layer`: **Self-Attention Mechanism** (captures critical time steps).
    -   `Optimization`: **Weighted Cross-Entropy Loss**.
-   **Why this architecture?**: 
    -   **Bidirectional**: Unlike a standard LSTM, it reads the 24-hour sequence forwards and backwards simultaneously to capture complex lead-lag relationships.
    -   **Attention**: It doesn't just look at the last hour; it learns *which* specific hours in the day (e.g., peak traffic at 6 PM) contribute most to the forecast.
    -   **Class Weighting**: We penalize the model 500x more for missing a "Hazardous" event. This is an industry-standard way to handle extreme imbalance.

---

## 5. Unsupervised Clustering (Unit II)
-   **Algorithm**: PCA + K-Means ($k=3$).
-   **Logic**: We used PCA to reduce 12 pollutant dimensions to 2, then clustered cities.
-   **Finding**: Cities are grouped into "Regimes" (e.g., Industrial Metro, Coastal, and Residential). This proves that geography affects pollution behavior.

---

## 6. Advanced Research: GANs (Unit VI)
-   **Why VAE?**: We used a **Variational Autoencoder (VAE)** for high-fidelity data augmentation. 
-   **Structure**: Encoder compresses pollutant features into a 2D Latent Space; Decoder reconstructs them.
-   **Impact**: We generated 50,000 synthetic "Hazardous" and "Severe" samples to balance the training set. This improved our **Hazardous Recall from 0% to ~28%**, solving the "Minority Class Problem" in environmental data.

---

## 7. Performance Comparison
-   **Classical vs. Deep Learning**: Classical models (HGB) are great for general categorization, but LSTMs are superior for "Spike Detection" because they understand the time-series momentum.
-   **Evaluation Metrics**: We prioritize **Macro F1-Score** and **Recall for Severe Class**, as missing a "Severe" prediction is a greater public health risk than a slight error in a "Moderate" prediction.

---
**Prepared for:** Abhay Bhise | Predictive Analytics Viva 2026
