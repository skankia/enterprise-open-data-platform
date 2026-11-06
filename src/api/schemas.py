"""
lecture 12: Pydantic request/response models.
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class WeatherResponse(BaseModel):
    city: str
    temperature_c: float = Field(..., description="ტემპერატურა °C-ში")
    wind_speed_kmh: float = Field(..., description="ქარის სიჩქარე კმ/სთ-ში")


class CurrencyRate(BaseModel):
    code: str
    name: str
    quantity: int
    rate: float


class CurrencyResponse(BaseModel):
    date: str
    rates: List[CurrencyRate]


class SeismicEvent(BaseModel):
    event_id: str
    magnitude: float = Field(..., description="მაგნიტუდა")
    place: str
    event_time: datetime = Field(..., description="მოვლენის დრო (UTC)")
    latitude: float
    longitude: float
    depth_km: float = Field(..., description="სიღრმე კილომეტრებში")


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"