from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Location(Base):
    __tablename__ = 'locations'
    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String, nullable=False, unique=True)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    
    logs = relationship("AirQualityLog", back_populates="location")

class AirQualityLog(Base):
    __tablename__ = 'air_quality_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(Integer, ForeignKey('locations.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    # Pollutants
    pm25 = Column(Float)
    pm10 = Column(Float)
    no2 = Column(Float)
    co = Column(Float)
    so2 = Column(Float)
    o3 = Column(Float)
    aqi = Column(Float)
    
    # Meteorology
    temp = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    
    # Metadata
    source = Column(String)  # 'openweather', 'cpcb', 'waqi'
    provider_version = Column(String)
    ingestion_time = Column(DateTime, default=datetime.utcnow)
    quality_score = Column(Float)
    
    location = relationship("Location", back_populates="logs")

# Indexes for fast time-series queries
Index('idx_location_timestamp', AirQualityLog.location_id, AirQualityLog.timestamp)
