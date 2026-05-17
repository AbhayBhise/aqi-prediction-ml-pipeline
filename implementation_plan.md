# Implementation Plan — Research-Grade ML Analysis System

Transform the AQI dashboard into a comprehensive ML research pipeline by implementing deep visualizations, comparative analysis, and consensus-driven inference across 8 distinct architectures.

## User Review Required

> [!IMPORTANT]
> **Visualization Accuracy**: I will use the pre-calculated metrics from `ui_model_comparison.json` and existing confusion matrix images in `model_results`. I will ensure all 8 models (LR, DT, RF, KNN, SVM, NB, ANN, DNN) are represented throughout the application.

- **Confusion Matrices**: These will be displayed in a strictly managed 2x4 grid on desktop to ensure scientific comparability.
- **Consensus Logic**: The backend already provides consensus and agreement scores; I will focus on the UI presentation of this "dissent vs agreement" logic.

## Proposed Changes

### 1. Model Visualization (Prediction Page)
#### [MODIFY] [Prediction.jsx](file:///f:/DOCUMENTS/B.TECH DOCS/Term II ABHAY BHISE/Predictive Analytics/PA LAB/PA LAB PROJECT/AQI PREDICTION VERSION 2/frontend/src/pages/Prediction.jsx)
- Update the "Architectural Dissent & Agreement" grid to show all 8 models clearly.
- Enhance the Consensus Hero card to highlight the mode-based agreement score (e.g., "6/8 models agree").

### 2. Comparative Benchmarking (Comparison Page)
#### [MODIFY] [ModelComparison.jsx](file:///f:/DOCUMENTS/B.TECH DOCS/Term II ABHAY BHISE/Predictive Analytics/PA LAB/PA LAB PROJECT/AQI PREDICTION VERSION 2/frontend/src/pages/ModelComparison.jsx)
- **Table**: Expand leaderboard to show [Architecture | Accuracy | Precision | Recall | F1-Score].
- **Comparison Chart**: Bar chart focused on F1-Score across all 8 models.
- **Confusion Matrix Grid**: Implement a strictly structured 2x4 grid of images for the 8 core models.
- **Badging**: Add explicit "Best Performer" and "Underperformer" badges.

### 3. Structural/Pattern Analysis (Clustering Page)
#### [MODIFY] [Clustering.jsx](file:///f:/DOCUMENTS/B.TECH DOCS/Term II ABHAY BHISE/Predictive Analytics/PA LAB/PA LAB PROJECT/AQI PREDICTION VERSION 2/frontend/src/pages/Clustering.jsx)
- Integrate the **Dendrogram** (Hierarchical clustering evidence) via the `/generate_dendrogram` API.
- Add descriptive text explaining that clusters represent different pollutant "regimes" (e.g., Industrial High-SO2 vs Urban High-NO2).

### 4. Temporal Depth (LSTM Page)
#### [MODIFY] [LSTMPage.jsx](file:///f:/DOCUMENTS/B.TECH DOCS/Term II ABHAY BHISE/Predictive Analytics/PA LAB/PA LAB PROJECT/AQI PREDICTION VERSION 2/frontend/src/pages/LSTMPage.jsx)
- Display the LSTM Loss Curve and Confusion Matrix.
- Add a comparison panel benchmarking LSTM vs Random Forest and DNN.

### 5. Research Synthesis (Final Insights Page)
#### [MODIFY] [FinalInsights.jsx](file:///f:/DOCUMENTS/B.TECH DOCS/Term II ABHAY BHISE/Predictive Analytics/PA LAB/PA LAB PROJECT/AQI PREDICTION VERSION 2/frontend/src/pages/FinalInsights.jsx)
- Programmatically summarize the Best vs Worst models based on telemetry.
- Highlight the **PM2.5 Dominance** in feature importance and the rationale behind the DNN's superior performance in capturing complex chemical interactions.

## Open Questions

1. **Confusion Matrix Source**: I see multiple versions of CM images (e.g., `cm_ann.png` vs `cm_ANN_(UI_Dataset).png`). I will use the simpler `cm_{model}.png` naming convention for consistency unless you prefer otherwise.
2. **Dendrogram Generation**: Hierarchical clustering on the full dataset is slow. I will use the backend's provided sampling logic (200-500 samples) for the live dendrogram.

## Verification Plan

### Automated Tests
- Verify all `/images` endpoints return valid PNGs for the model grid.
- Check `/predict` output structure to ensure agreement scores are strings.

### Manual Verification
- Visual check of the 2x4 CM grid for alignment.
- Interaction check: ensure the Consensus highlights properly update on new predictions.
