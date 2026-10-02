import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import pandas as pd
import numpy as np

def train_and_log_model(X_train, y_train, X_test, y_test):
    """
    Example function demonstrating how to train a model and log it with MLflow.
    Run this script with the MLFLOW_TRACKING_URI set to your local server.
    e.g., export MLFLOW_TRACKING_URI=http://localhost:5000
    """
    # 1. Start an MLflow experiment run
    mlflow.set_experiment("AQI_Prediction_Models")
    
    with mlflow.start_run(run_name="RandomForest_Baseline"):
        # 2. Log hyperparameters
        params = {
            "n_estimators": 100,
            "max_depth": 10,
            "random_state": 42
        }
        mlflow.log_params(params)
        
        # 3. Train the model
        model = RandomForestRegressor(**params)
        model.fit(X_train, y_train)
        
        # 4. Evaluate the model
        predictions = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        
        # 5. Log metrics
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("r2", r2)
        
        # 6. Log the model to the MLflow Registry
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="random_forest_model",
            registered_model_name="AQI_RandomForest_Regressor"
        )
        
        print(f"Model logged to MLflow with RMSE: {rmse:.2f}")

if __name__ == "__main__":
    # Generate some dummy data to demonstrate
    print("Running MLflow training example...")
    np.random.seed(42)
    X_train = pd.DataFrame(np.random.rand(100, 5), columns=[f"feature_{i}" for i in range(5)])
    y_train = pd.Series(np.random.rand(100))
    X_test = pd.DataFrame(np.random.rand(20, 5), columns=[f"feature_{i}" for i in range(5)])
    y_test = pd.Series(np.random.rand(20))
    
    # In a real environment, you'd ensure MLFLOW_TRACKING_URI is set.
    # We set it here manually to point to the local docker-compose service if running outside container
    mlflow.set_tracking_uri("http://localhost:5000")
    
    train_and_log_model(X_train, y_train, X_test, y_test)
