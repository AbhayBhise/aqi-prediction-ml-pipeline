import os
import requests
from datetime import datetime
from typing import Dict, Any, List
from backend.services.data_providers.base import AQIDataProvider

class WAQIProvider(AQIDataProvider):
    def __init__(self):
        self.api_key = os.environ.get("WAQI_API_KEY")
        self.base_url = "https://api.waqi.info/feed/geo"

    @property
    def provider_name(self) -> str:
        return "waqi"

    def get_current_aqi(self, lat: float, lon: float) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("WAQI_API_KEY is missing")
            
        url = f"{self.base_url}:{lat};{lon}/?token={self.api_key}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "ok":
            raise ValueError(f"WAQI API Error: {data.get('data')}")
            
        d = data["data"]
        iaqi = d.get("iaqi", {})
        
        # WAQI gives individual sub-indices. We extract what is available.
        pollutants = {
            "pm2_5": iaqi.get("pm25", {}).get("v"),
            "pm10": iaqi.get("pm10", {}).get("v"),
            "no2": iaqi.get("no2", {}).get("v"),
            "co": iaqi.get("co", {}).get("v"),
            "so2": iaqi.get("so2", {}).get("v"),
            "o3": iaqi.get("o3", {}).get("v"),
            "aqi": d.get("aqi")
        }
        
        weather = {
            "temp": iaqi.get("t", {}).get("v"),
            "humidity": iaqi.get("h", {}).get("v"),
            "wind_speed": iaqi.get("w", {}).get("v")
        }
        
        # Parse timestamp from "2026-07-13 18:00:00" string or similar
        time_str = d.get("time", {}).get("s")
        if time_str:
            timestamp = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        else:
            timestamp = datetime.utcnow()
            
        return self.standardize_response(timestamp, pollutants, weather)

    def get_historical_aqi(self, lat: float, lon: float, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        # WAQI historical data is typically only available via enterprise plans or specific 
        # station queries, not purely by geo coordinates.
        # For MVP, we will rely on OpenWeather for historical ingestion.
        raise NotImplementedError("WAQI Historical API requires station IDs and enterprise tokens. Use OpenWeather for history.")
