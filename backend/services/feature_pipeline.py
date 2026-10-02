import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.db.models import AirQualityLog, Location

# Constants matching original feature definitions
FORECAST_POLLUTANTS = ['pm25', 'pm10', 'no2', 'co', 'so2', 'o3', 'aqi']
FORECAST_LAGS = [1, 2, 3, 4, 6, 12, 24]
FORECAST_ROLLING_WINDOWS = [6, 12, 24]

class FeaturePipeline:
    def __init__(self, db_session: Session):
        self.db = db_session

    def _get_history_df(self, location_id: int, dt: datetime, hours_back: int = 48) -> pd.DataFrame:
        """
        Retrieves historical logs from the database and converts to a DataFrame.
        """
        start_time = dt - timedelta(hours=hours_back)
        logs = self.db.query(AirQualityLog).filter(
            AirQualityLog.location_id == location_id,
            AirQualityLog.timestamp >= start_time,
            AirQualityLog.timestamp <= dt
        ).order_by(AirQualityLog.timestamp.asc()).all()

        if not logs:
            return pd.DataFrame()

        # Convert to dictionary for pandas
        data = [{
            "timestamp": log.timestamp,
            "pm25": log.pm25,
            "pm10": log.pm10,
            "no2": log.no2,
            "co": log.co,
            "so2": log.so2,
            "o3": log.o3,
            "aqi": log.aqi,
            "temp": log.temp,
            "humidity": log.humidity,
            "wind_speed": log.wind_speed
        } for log in logs]

        df = pd.DataFrame(data)
        # Ensure it's sorted by time
        df = df.sort_values('timestamp')
        return df

    def compute_features(self, location: Location, target_dt: datetime) -> dict:
        """
        Calculates lag features and rolling windows for a given target datetime.
        """
        df = self._get_history_df(location.id, target_dt)
        
        if df.empty:
            raise ValueError(f"No historical data found for {location.city} to build features.")

        latest_row = df.iloc[-1].to_dict()
        feature_row = latest_row.copy()
        
        # Temporal features
        feature_row['Year'] = int(target_dt.year)
        feature_row['Month'] = int(target_dt.month)
        feature_row['Day'] = int(target_dt.day)
        feature_row['Hour'] = int(target_dt.hour)
        feature_row['Day_of_Week'] = int(target_dt.weekday())

        for col in FORECAST_POLLUTANTS:
            # Lags
            for lag in FORECAST_LAGS:
                # If we don't have enough history, fallback to the latest known value
                feature_row[f"{col}_lag_{lag}h"] = float(df[col].iloc[-lag]) if len(df) >= lag else float(latest_row[col])

            # Rolling stats
            for window in FORECAST_ROLLING_WINDOWS:
                values = df[col].tail(window)
                if values.empty:
                    feature_row[f"{col}_roll_mean_{window}h"] = float(latest_row[col])
                    feature_row[f"{col}_roll_max_{window}h"] = float(latest_row[col])
                else:
                    feature_row[f"{col}_roll_mean_{window}h"] = float(values.mean())
                    feature_row[f"{col}_roll_max_{window}h"] = float(values.max())

        return feature_row
