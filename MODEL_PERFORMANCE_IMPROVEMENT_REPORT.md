# AQI Model Performance Improvement Report

## Current Baseline

The project currently compares multiple AQI category classifiers, including Logistic Regression, Decision Tree, Random Forest, KNN, SGD/SVM, Naive Bayes, ANN, DNN, RNN, LSTM, and BiLSTM models.

The strongest existing tabular result is the research-feature DNN, with about 81.3% weighted accuracy/recall/F1. Random Forest is the strongest classical baseline at about 78.9% weighted accuracy.

The sequential comparison shows:

| Model | Accuracy | Macro F1 |
| --- | ---: | ---: |
| RNN | 57.96% | 25.24% |
| LSTM | 81.83% | 66.15% |
| BiLSTM | 82.92% | 66.90% |

## Main Issue

The target distribution is highly imbalanced:

| AQI Category | Share |
| --- | ---: |
| Moderate | 45.94% |
| Unhealthy Sensitive | 20.85% |
| Good | 16.25% |
| Unhealthy | 15.52% |
| Very Unhealthy | 1.23% |
| Hazardous | 0.20% |

This means weighted accuracy, weighted recall, and weighted F1 can look acceptable while the model still misses the most dangerous AQI classes. For an AQI system, recall for `Very_Unhealthy` and `Hazardous` matters more than small gains on the majority classes.

## Implemented Improvements

The training and dashboard pipeline now includes the following changes:

1. **Imbalance-aware classical models**
   - Logistic Regression now uses `class_weight='balanced'`.
   - Decision Tree now uses `class_weight='balanced'` and a minimum leaf size to reduce overfitting.
   - Random Forest now uses more trees, balanced subsampling, and a minimum leaf size.
   - SGD/SVM now uses `class_weight='balanced'`.
   - Hist Gradient Boosting uses balanced sample weights.
   - Naive Bayes uses balanced sample weights.

2. **Stronger tabular baseline**
   - Added `HistGradientBoostingClassifier`, a strong built-in scikit-learn model for structured tabular data.
   - This gives the project a modern boosted-tree baseline without adding new dependencies.

3. **Better evaluation metrics**
   - Added `Balanced_Accuracy`.
   - Added `Macro_Recall`.
   - Added `Macro_F1`.
   - Added `Very_Unhealthy_Recall`.
   - Added `Hazardous_Recall`.
   - Added `Severe_Class_Recall`, calculated as the average recall of `Very_Unhealthy` and `Hazardous`.

4. **Dashboard metric ranking**
   - The model comparison page now ranks models primarily by `SevereClassRecall`.
   - This prevents majority-class weighted F1 from hiding weak dangerous-class detection.

5. **Training efficiency correction**
   - Removed duplicate ANN and DNN fitting in the main evaluation script.

6. **Persisted model pipeline fix**
   - `persist_all_models.py` now reads from `data/processed` and writes model comparison artifacts to `backend/results`, matching the Flask API.

## Recommended Next Improvements

The following improvements should be implemented next if further performance gains are needed:

1. **Forecasting pipeline for real-time use**
   - Added `backend/training/forecast_model_training.py`.
   - The script creates future AQI category targets for 1h, 4h, 6h, 12h, and 24h horizons.
   - Targets are shifted forward per city, so a row at time `t` predicts the category at `t + horizon`.
   - This converts the project from same-row classification into genuine AQI forecasting.

2. **Temporal lag and rolling features**
   - The forecasting script adds 1-hour, 3-hour, 6-hour, 12-hour, and 24-hour pollutant lag features.
   - It also adds rolling mean and rolling max features using only observations before the prediction time.
   - This avoids leakage while giving models recent pollution trend context.

3. **Chronological validation**
   - The forecasting script uses a chronological 70/15/15 train/validation/test split.
   - This gives a more realistic estimate of future AQI prediction performance than random splitting.

4. **Ordinal AQI modeling**
   - AQI classes are ordered, but current classifiers treat all mistakes equally.
   - Consider predicting AQI score/regression first, then mapping to category.
   - Alternatively, use ordinal classification or custom penalty weighting.

5. **Hyperparameter search**
   - Use `RandomizedSearchCV` for Random Forest and Hist Gradient Boosting.
   - Optimize for `macro_f1`, `balanced_accuracy`, or severe-class recall instead of weighted F1.

6. **Sequential model upgrades**
   - Add weather and time features to LSTM/BiLSTM inputs.
   - Train across all cities with city encoding instead of Delhi only.
   - Tune sequence lengths such as 12, 24, 48, and 72.

7. **Prediction confidence**
   - Add calibrated probabilities using `CalibratedClassifierCV`.
   - Show low-confidence warnings in the dashboard.

## Real-Time Forecasting Standard

For real-time use, the trustworthy setup should separate two tasks:

1. **Current AQI nowcast**
   - Use pollutant readings and the official AQI formula.
   - This is a deterministic regulatory calculation, not a machine-learning forecast.

2. **Future AQI forecast**
   - Use ML models to predict future category at 1h, 4h, 6h, 12h, and 24h.
   - Use only data available at prediction time.
   - Use lag, rolling, weather, city, and time features.
   - Evaluate with chronological holdout data.

The project should not claim high forecasting accuracy from same-row classification, random splits, or AQI-derived columns. Those would overstate real-world performance.

## Practical Success Criteria

Future model improvements should be accepted only if they improve at least one of these without causing unacceptable regression:

- `Severe_Class_Recall`
- `Macro_Recall`
- `Macro_F1`
- `Balanced_Accuracy`
- per-class recall for `Very_Unhealthy`
- per-class recall for `Hazardous`

Accuracy alone should not be used as the primary success metric for this dataset.
