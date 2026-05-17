# AQI Prediction Project - Setup & Execution Guide

This guide explains how to set up and run the AQI Prediction project after extracting it from a zip file.

## Prerequisites

1.  **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
2.  **Node.js & npm**: [Download Node.js](https://nodejs.org/)

---

## Step 1: Set Up the Python Backend

The backend is a Flask API that handles Machine Learning predictions and data processing.

1.  Open a terminal (Command Prompt, PowerShell, or Bash).
2.  Navigate to the project root directory (where you extracted the zip).
3.  (Recommended) Create a virtual environment:
    ```bash
    python -m venv venv
    ```
4.  Activate the virtual environment:
    *   **Windows**: `venv\Scripts\activate`
    *   **Mac/Linux**: `source venv/bin/activate`
5.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
6.  Start the Flask server:
    ```bash
    python backend/app.py
    ```
    *The backend will run at `http://localhost:5000`.*

---

## Step 2: Set Up the React Frontend

The frontend is a React application built with Vite and Tailwind CSS.

1.  Open a **second** terminal window.
2.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
3.  Install the Node.js dependencies:
    ```bash
    npm install
    ```
4.  Start the development server:
    ```bash
    npm run dev
    ```
    *The frontend will run at `http://localhost:5173`.*

---

## How to Use the Dashboard

1.  Open your browser and go to `http://localhost:5173`.
2.  **Real-time Prediction**: Enter pollutant concentrations (PM2.5, PM10, etc.) and weather data to get an AQI category prediction from the trained models.
3.  **Model Comparison**: View performance metrics for different ML algorithms (Random Forest, SVM, LSTM, etc.).
4.  **Exploratory Data Analysis (EDA)**: View visualizations of historical air quality data across various Indian cities.

---

## Troubleshooting

- **Large CSV Files**: Ensure that `INDIA_AQI_CLEANED_FINAL.csv` is present in the root directory. This project relies on large datasets for visualization and model loading.
- **Port Conflicts**: If port 5000 or 5173 is already in use, you may need to stop other services or change the ports in `backend/app.py` or the frontend configuration.
- **Node Modules**: If the frontend fails to start, delete the `node_modules` folder inside `frontend` and run `npm install` again.
