import logging
from datetime import datetime
from sqlalchemy.orm import Session
from backend.db.database import SessionLocal
from backend.db.models import Location, AirQualityLog
from backend.services.data_providers.openweather import OpenWeatherProvider
from backend.services.data_providers.waqi import WAQIProvider

logger = logging.getLogger(__name__)

class IngestionService:
    def __init__(self):
        self.primary_provider = OpenWeatherProvider()
        # Fallback provider initialized if primary fails
        self.fallback_provider = WAQIProvider()

    def _get_provider_data(self, lat: float, lon: float) -> dict:
        try:
            return self.primary_provider.get_current_aqi(lat, lon)
        except Exception as e:
            logger.warning(f"Primary provider failed for {lat},{lon}: {e}. Trying fallback.")
            try:
                return self.fallback_provider.get_current_aqi(lat, lon)
            except Exception as fallback_e:
                logger.error(f"Fallback provider also failed: {fallback_e}")
                raise

    def ingest_current_data(self):
        """
        Polls the current active locations and inserts the latest data into the database.
        Intended to be run via an hourly APScheduler job.
        """
        db: Session = SessionLocal()
        try:
            locations = db.query(Location).all()
            if not locations:
                logger.info("No active locations to ingest.")
                return

            for loc in locations:
                logger.info(f"Ingesting data for {loc.city} ({loc.lat}, {loc.lon})...")
                try:
                    data = self._get_provider_data(loc.lat, loc.lon)
                    
                    log_entry = AirQualityLog(
                        location_id=loc.id,
                        timestamp=data["timestamp"],
                        pm25=data["pm25"],
                        pm10=data["pm10"],
                        no2=data["no2"],
                        co=data["co"],
                        so2=data["so2"],
                        o3=data["o3"],
                        aqi=data["aqi"],
                        temp=data["temp"],
                        humidity=data["humidity"],
                        wind_speed=data["wind_speed"],
                        source=data["source"]
                    )
                    
                    db.add(log_entry)
                    db.commit()
                    logger.info(f"Successfully ingested log for {loc.city}.")
                    
                except Exception as e:
                    logger.error(f"Failed to ingest for {loc.city}: {e}")
                    db.rollback()
        finally:
            db.close()
