"""
lecture 12: Dependency Injection — FastAPI-ის Depends()-ისთვის.
"""

from src.ingestion.currency_client import CurrencyClient
from src.ingestion.seismic_client import SeismicClient
from src.ingestion.weather_client import WeatherClient


def get_weather_client() -> WeatherClient:
    return WeatherClient()


def get_currency_client() -> CurrencyClient:
    return CurrencyClient()


def get_seismic_client() -> SeismicClient:
    return SeismicClient()