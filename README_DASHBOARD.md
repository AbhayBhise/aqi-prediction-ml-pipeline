# AQI ML Visualization Dashboard (Flask + React)

A complete end-to-end Machine Learning web dashboard architecture bridging a RESTful Python Flask API with a modern React.js SPA (Tailwind CSS, Recharts).

## Step 1: Start the Flask Backend

The backend exposes all ML metadata and executes live Random Forest predictions.

1. Open a new terminal.
2. Navigate to the project root:
   ```bash
   cd "f:\DOCUMENTS\B.TECH DOCS\Term II ABHAY BHISE\Predictive Analytics\PA LAB\PA LAB PROJECT\AQI PREDICTION VERSION 2"
   ```
3. Run the Flask server:
   ```bash
   python backend/app.py
   ```
*The API will boot linearly on `http://localhost:5000`.*

## Step 2: Start the React Frontend

The frontend pulls from the backend asynchronously without any rule-based logic fallback mapping.

1. Open a *second* new terminal.
2. Navigate into the frontend folder:
   ```bash
   cd "f:\DOCUMENTS\B.TECH DOCS\Term II ABHAY BHISE\Predictive Analytics\PA LAB\PA LAB PROJECT\AQI PREDICTION VERSION 2\frontend"
   ```
3. Start the Vite React development server:
   ```bash
   npm run dev
   ```
*The SPA will run exclusively on `http://localhost:5173`.*

## Data Flow Notes
- `backend/app.py` dynamically loads `.joblib` scalers and Random Forest classification weights.
- `frontend/src/services/api.js` automatically maps fetch requests to port `5000`.
- Offline static analysis visuals are linked into the component states conceptually.
