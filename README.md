<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f172a,100:059669&height=200&section=header&text=AQI%20Prediction%20ML%20Pipeline&fontSize=42&fontColor=ffffff&fontAlignY=38&desc=Multi-Horizon%20Air%20Quality%20Forecasting%20for%20Indian%20Cities&descAlignY=58&descSize=16&animation=fadeIn" width="100%"/>

<br/>

![Backend](https://img.shields.io/badge/backend-live-brightgreen?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![React](https://img.shields.io/badge/React_19-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**[Live Dashboard](#)** https://frontend-sigma-six-81.vercel.app/ · **[Research Paper](./IEEE_AQI_Research_Paper.zip)**

</div>

---

## 🌍 Overview

A full-stack air quality forecasting system built on real Indian AQI data (265,000+ chronologically-ordered records across multiple cities). It doesn't just classify current air quality — it **forecasts AQI category 1, 4, 6, 12, and 24 hours ahead**, using lag and rolling pollutant features so predictions are made only from information that would genuinely be available at inference time.

The backend is a Flask API serving trained models, deployed as a Docker container. The frontend is a React dashboard for real-time predictions, model comparison, EDA, and clustering.

## 🚀 Live Deployment

| Service | Stack | Status |
|---|---|---|
| **Backend API** | Flask + Gunicorn, Dockerized, hosted on Hugging Face Spaces | 🟢 [Live](https://cbabhi-aqi-prediction-ml-pipeline.hf.space) |
| **Frontend Dashboard** | React 19 + Vite + Tailwind, deployed on Vercel | (https://frontend-sigma-six-81.vercel.app/) |

---

## 🧠 What It Actually Does

- **Multi-horizon forecasting** — predicts future AQI category (not just current), at 1h/4h/6h/12h/24h, using per-city lag and rolling-window pollutant features computed only from past observations.
- **9-model classification benchmark** — Logistic Regression, Decision Tree, Random Forest, KNN, SGD/SVM, Naive Bayes, HistGradientBoosting, ANN, DNN — plus sequential models (RNN, LSTM, BiLSTM) and a custom 1D-CNN forecast engine, all compared on the same dashboard.
- **VAE-based data augmentation** — a Variational Autoencoder generates synthetic samples for the rare, dangerous AQI classes (`Very_Unhealthy`, `Hazardous`) that make up under 1.5% of the raw data, so the models aren't blind to the cases that matter most.
- **Agentic AI chatbot** — a ReAct-style (reasoning + action) assistant powered by Gemini, grounded on the project's own live metrics and current AQI data rather than answering from general knowledge.
- **News sentiment analysis** — NLTK + TextBlob pipeline for tokenizing and scoring air-quality-related news headlines.
- **EDA & clustering dashboard** — hierarchical clustering, PCA visualization, correlation heatmaps, and pollutant distribution analysis, all served dynamically from the API.

## 🔬 Why the Numbers Are Trustworthy

Most student ML projects inflate their accuracy through shortcuts. This pipeline was built to specifically avoid the common ones:

- **Chronological split, not random** — training, validation, and test sets are split strictly by timestamp (70/15/15) per city, so the model is always evaluated on a genuinely future, unseen period.
- **No leakage in scaling** — the `StandardScaler` is fit only on the training split; validation and test data are transformed using those parameters, never their own.
- **No AQI-derived features** — forecasting features are limited to lagged/rolling pollutant and weather readings available *before* the prediction time.
- **Imbalance-aware evaluation** — since `Moderate` alone makes up ~46% of the data and `Hazardous` under 0.2%, weighted accuracy is misleading here. The project tracks **Macro F1, Balanced Accuracy, and Severe-Class Recall** (average recall on `Very_Unhealthy` + `Hazardous`) as the real success metrics, and is explicit where those numbers still need work.

## 📊 Forecasting Performance

Accuracy naturally decays as the horizon extends — which is itself evidence the models aren't leaking future information:

| Horizon | Logistic Regression | Random Forest | XGBoost | BiLSTM |
|---|---:|---:|---:|---:|
| 1h  | 90.6% | 98.3% | **99.3%** | 88.1% |
| 4h  | 90.5% | 95.3% | **97.3%** | 88.4% |
| 6h  | 89.9% | 93.2% | **95.2%** | 89.4% |
| 12h | 84.1% | 87.5% | **89.2%** | 84.7% |
| 24h | 69.8% | 76.6% | **78.7%** | 74.1% |

> ⚠️ Honest caveat, tracked directly in the repo: raw accuracy looks strong across the board, but **severe-class recall** (correctly catching `Very_Unhealthy`/`Hazardous` readings) is meaningfully lower and drops further at longer horizons — the known next problem to solve, not a hidden one.

---

## 🛠️ Tech Stack

**Backend & Serving**

![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)
![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=flat-square&logo=gunicorn&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HF_Spaces-FFD21E?style=flat-square&logo=huggingface&logoColor=black)

**Machine Learning / Deep Learning**

![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-005A9C?style=flat-square)
![LightGBM](https://img.shields.io/badge/LightGBM-02569B?style=flat-square)
![NLTK](https://img.shields.io/badge/NLTK-3776AB?style=flat-square)

**Frontend**

![React](https://img.shields.io/badge/React_19-61DAFB?style=flat-square&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![Recharts](https://img.shields.io/badge/Recharts-22B5BF?style=flat-square)

**AI / APIs**

![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-4285F4?style=flat-square&logo=googlegemini&logoColor=white)
![OpenWeather](https://img.shields.io/badge/OpenWeather_API-EB6E4B?style=flat-square)

---

## 🏗️ Architecture

```
Raw AQI + weather data (multi-city, timestamped)
        ↓
Cleaning → feature selection → lag/rolling feature engineering
        ↓
Chronological train/val/test split (per city)
        ↓
┌─────────────────────────┬──────────────────────────┐
│  Classical ML ensemble   │  Sequential DL (LSTM/    │
│  (RF, XGBoost, HGB...)   │  BiLSTM/CNN forecast)     │
└─────────────────────────┴──────────────────────────┘
        ↓
VAE augmentation for rare severe classes
        ↓
Flask API (predict / forecast / model_metrics / eda_data / chatbot)
        ↓
React dashboard (Prediction, Model Comparison, EDA, Clustering, Agentic AI)
```

## 📡 API Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /predict` | Real-time AQI category from current pollutant/weather input |
| `POST /forecast` | Future AQI category at a chosen horizon (1h–24h) |
| `GET /model_metrics` / `/forecast_metrics` | Model comparison data for the dashboard |
| `GET /sequential_comparison` | RNN vs LSTM vs BiLSTM comparison |
| `GET /eda_filters` / `/eda_data` | Dynamic exploratory data analysis |
| `GET /clustering_data` / `/generate_dendrogram` | Hierarchical clustering & PCA |
| `GET /vae_results` | Synthetic data augmentation results |
| `GET /live_data` | Live current AQI from OpenWeather |
| `POST /api/chatbot` | Agentic AI assistant grounded on live project data |

---

## 📁 Project Structure

```
├── backend/
│   ├── api/            # Flask app + agentic chatbot
│   ├── analytics/      # CNN forecast engine, GAN, news sentiment
│   ├── models/         # Trained LSTM/BiLSTM/VAE weights & scalers
│   ├── training/        # Training, augmentation, evaluation scripts
│   └── utils/           # CPCB AQI calculator, preprocessing
├── frontend/
│   └── src/pages/       # Dashboard, Prediction, EDA, ModelComparison,
│                         # Clustering, GenerativeAI, LSTM, AgenticAI
├── data/                # Raw + processed datasets, saved models
├── experiments/eda/     # Exploratory data analysis outputs
├── Dockerfile
└── paper.tex            # IEEE-format research paper
```

## ⚙️ Run It Locally

```bash
# Backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python backend/api/app.py   # → http://localhost:5000

# Frontend (new terminal)
cd frontend
npm install
npm run dev                 # → http://localhost:5173
```

---

<div align="center">

📄 Methodology write-up in [`MODEL_PERFORMANCE_IMPROVEMENT_REPORT.md`](./MODEL_PERFORMANCE_IMPROVEMENT_REPORT.md) · Research paper in [`IEEE_AQI_Research_Paper.zip`](./IEEE_AQI_Research_Paper.zip)

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:059669,100:0f172a&height=90&section=footer" width="100%"/>

</div>
