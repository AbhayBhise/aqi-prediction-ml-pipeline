from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime

class AQIDataProvider(ABC):
    """
    Abstract base class for Environmental Data Providers (OpenWeather, CPCB, WAQI, etc.)
    """
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the data provider"""
        pass

    @abstractmethod
    def get_current_aqi(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Fetch current AQI and meteorology for the given coordinates.
        Returns a standardized dictionary.
        """
        pass
        
    @abstractmethod
    def get_historical_aqi(self, lat: float, lon: float, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        """
        Fetch historical AQI for the given coordinates and time range.
        Returns a list of standardized dictionaries.
        """
        pass

    def standardize_response(self, timestamp: datetime, pollutants: dict, weather: dict) -> dict:
        """
        Helper method to format the response into the unified schema expected by the database.
        """
        return {
            "timestamp": timestamp,
            "pm25": pollutants.get("pm2_5"),
            "pm10": pollutants.get("pm10"),
            "no2": pollutants.get("no2"),
            "co": pollutants.get("co"),
            "so2": pollutants.get("so2"),
            "o3": pollutants.get("o3"),
            "aqi": pollutants.get("aqi"),
            "temp": weather.get("temp"),
            "humidity": weather.get("humidity"),
            "wind_speed": weather.get("wind_speed"),
            "source": self.provider_name
        }
