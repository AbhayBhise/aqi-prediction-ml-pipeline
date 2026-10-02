import os
import requests
from datetime import datetime
from typing import Dict, Any, List
from backend.services.data_providers.base import AQIDataProvider

class OpenWeatherProvider(AQIDataProvider):
    def __init__(self):
        self.api_key = os.environ.get("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENWEATHER_API_KEY is missing from environment variables.")
        self.base_url_aqi = "http://api.openweathermap.org/data/2.5/air_pollution"
        self.base_url_weather = "http://api.openweathermap.org/data/2.5/weather"

    @property
    def provider_name(self) -> str:
        return "openweather"

    def _fetch_weather(self, lat: float, lon: float) -> dict:
        url = f"{self.base_url_weather}?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {
            "temp": data.get("main", {}).get("temp"),
            "humidity": data.get("main", {}).get("humidity"),
            "wind_speed": data.get("wind", {}).get("speed")
        }

    def get_current_aqi(self, lat: float, lon: float) -> Dict[str, Any]:
        weather = self._fetch_weather(lat, lon)
        
        url = f"{self.base_url_aqi}?lat={lat}&lon={lon}&appid={self.api_key}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        item = data["list"][0]
        components = item["components"]
        timestamp = datetime.utcfromtimestamp(item["dt"])
        
        # OpenWeather returns an AQI index from 1-5. For our system, we might log it as is or recalculate.
        components["aqi"] = item.get("main", {}).get("aqi")
        
        return self.standardize_response(timestamp, components, weather)

    def get_historical_aqi(self, lat: float, lon: float, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        # OpenWeather Air Pollution History API
        start_unix = int(start.timestamp())
        end_unix = int(end.timestamp())
        
        url = f"{self.base_url_aqi}/history?lat={lat}&lon={lon}&start={start_unix}&end={end_unix}&appid={self.api_key}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # NOTE: OpenWeather doesn't provide historical weather on the free tier,
        # so for historical pollution ingestion, we leave weather fields as None 
        # or implement a fallback logic. For MVP data collection, we collect what we have.
        results = []
        for item in data.get("list", []):
            components = item["components"]
            timestamp = datetime.utcfromtimestamp(item["dt"])
            components["aqi"] = item.get("main", {}).get("aqi")
            results.append(self.standardize_response(timestamp, components, {}))
            
        return results
