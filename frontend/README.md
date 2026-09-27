# 🌫️ AQI Prediction & Decision Support Dashboard

> **Live Demo →** [aqi-frontend.vercel.app](https://aqi-frontend.vercel.app) &nbsp;|&nbsp; **Backend API →** [Hugging Face Spaces](https://huggingface.co/spaces/CBABHI/aqi-prediction-ml-pipeline)

An end-to-end **AI-powered Air Quality forecasting web app** that turns raw ML predictions into personalized, human-readable health decisions. Built as a B.Tech academic capstone project in Predictive Analytics.

![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-8-646CFF?style=flat&logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-4-38BDF8?style=flat&logo=tailwindcss&logoColor=white)
![Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-000000?style=flat&logo=vercel&logoColor=white)

---

## 🚀 What This Project Does

Most AQI apps show you a number. This one answers the real questions:

- *"Is it safe to go running right now?"*
- *"What's the safest 2-hour window for outdoor activity today?"*
- *"How much pollution exposure am I accumulating?"*

The dashboard connects to a **Flask + ML backend** that runs XGBoost and BiLSTM models to forecast AQI up to **24 hours ahead**, then applies a decision-support engine to generate actionable guidance.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 📊 **Live AQI Dashboard** | Real-time forecast charts for 1h, 4h, 6h, 12h, 24h horizons with Recharts |
| 🏃 **Activity Advisor** | Sliding-window optimizer finds the safest time window for outdoor activity |
| 💨 **Exposure Score** | Cumulative pollution risk score weighted by AQI severity over 24h |
| 👤 **Risk Profiles** | Personalized recommendations for General / Asthma / Outdoor Worker profiles |
| 🔬 **EDA Explorer** | Interactive exploratory data analysis results with visual plots |
| 🤖 **Model Comparison** | Side-by-side performance metrics for all trained ML models |
| 🧠 **Generative AI** | AI-powered natural language summaries of air quality outlook |
| 🌙 **Dark / Light Mode** | Persistent theme toggle with smooth transitions |
| 📱 **Responsive Design** | Works on desktop, tablet, and mobile |

---

## 🛠️ Tech Stack

**Frontend**
- **React 19** + **React Router v7** — SPA with client-side routing
- **Vite 8** — blazing fast dev server & build tool
- **TailwindCSS v4** — utility-first styling
- **Recharts** — forecast & analytics visualizations
- **Framer Motion** — page transitions and micro-animations
- **Zustand** — lightweight global state management
- **Axios** — REST API communication

**Backend** *(separate repo)*
- Python, Flask, Blueprint routing, Pydantic validation
- XGBoost, HistGradientBoosting, PyTorch BiLSTM
- Deployed on Hugging Face Spaces

---

## 📁 Project Structure

```
src/
├── pages/
│   ├── Dashboard.jsx        # Main forecast + decision support UI
│   ├── Prediction.jsx       # AQI prediction interface
│   ├── EDA.jsx              # Exploratory Data Analysis results
│   ├── ModelComparison.jsx  # ML model benchmarks
│   ├── LSTMPage.jsx         # LSTM sequential forecast details
│   ├── Clustering.jsx       # K-Means clustering analysis
│   ├── FinalInsights.jsx    # Summary insights
│   ├── GenerativeAI.jsx     # LLM-powered air quality summaries
│   └── AgenticAI.jsx        # Agentic AI interactions
├── components/
│   ├── SidePanel.jsx        # Navigation sidebar
│   ├── AIChatbot.jsx        # Embedded AI assistant
│   ├── ImageModal.jsx       # Chart zoom modal
│   ├── LoadingOverlay.jsx   # Loading state UI
│   └── BuyMeACoffeeModal.jsx
├── store/
│   ├── useThemeStore.js     # Dark/light mode state
│   └── useDashboardStore.js # Dashboard data state
└── services/
    └── api.js               # Axios API client
```

---

## ⚡ Getting Started

```bash
# Clone the repo
git clone https://github.com/AbhayBhise/AQI-Frontend.git
cd AQI-Frontend

# Install dependencies
npm install

# Set up environment variable
echo "VITE_API_BASE_URL=https://your-backend-url.com" > .env.development

# Start dev server
npm run dev
```

> **Note:** The app expects a running instance of the [AQI backend](https://huggingface.co/spaces/CBABHI/aqi-prediction-ml-pipeline). Set `VITE_API_BASE_URL` to point to it.

---

## 🏗️ Build & Deploy

```bash
npm run build    # outputs to dist/
npm run preview  # preview production build locally
```

The app is deployed on **Vercel** with automatic deployments on every push to `main`. The `vercel.json` handles SPA routing so direct URL access works correctly.

---

## 📈 ML Models Behind the Dashboard

| Model | Purpose | Key Metric |
|---|---|---|
| XGBoost | Short-term AQI forecast | MAE ~8.2 |
| HistGradientBoosting | Robust baseline | MAE ~9.1 |
| PyTorch BiLSTM | Sequential 24h forecast | RMSE ~11.4 |
| K-Means Clustering | AQI pattern segmentation | Silhouette ~0.61 |

---

## 💼 Engineering Highlights

- **Built a multi-page React SPA** with React Router v7, persistent theme management via Zustand, and smooth Framer Motion page transitions
- **Integrated a 24-hour AQI forecast dashboard** consuming a Flask REST API that runs XGBoost and BiLSTM models, rendering results as interactive Recharts visualizations
- **Implemented a sliding-window activity optimizer** on the frontend that highlights the safest outdoor activity windows from forecast data
- **Designed a responsive, dark/light themed UI** using TailwindCSS v4 with a custom side-panel navigation system
- **Deployed to Vercel** with CI/CD via GitHub integration; configured SPA routing to prevent 404s on direct URL access

---

## 👨‍💻 Author

**Abhay Bhise** — B.Tech, Predictive Analytics  
[![GitHub](https://img.shields.io/badge/GitHub-AbhayBhise-181717?style=flat&logo=github)](https://github.com/AbhayBhise)

---

*Built as a capstone project for Predictive Analytics Lab, Term II.*
