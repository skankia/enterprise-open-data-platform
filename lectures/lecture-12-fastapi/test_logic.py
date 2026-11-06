"""
lecture 12: logic.py-ის ტესტები mock client-ებით (FastAPI სერვერის გარეშე, ინტერნეტის გარეშე).
გაშვება პროექტის root-იდან:
    python lectures/lecture-12-fastapi/test_logic.py
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.api.logic import (  # noqa: E402
    CITY_COORDS,
    UnknownCityError,
    get_currency_rates,
    get_seismic_events,
    get_weather_for_city,
)
from src.ingestion.currency_client import CurrencyAPIError  # noqa: E402
from src.ingestion.seismic_client import SeismicAPIError  # noqa: E402
from src.ingestion.weather_client import WeatherAPIError  # noqa: E402


class TestWeatherLogic(unittest.TestCase):
    def test_success(self):
        client = MagicMock()
        client.fetch.return_value = {"current": {"temperature_2m": 24.3, "wind_speed_10m": 8.1}}

        result = get_weather_for_city(client, "Tbilisi")

        self.assertEqual(result, {"city": "Tbilisi", "temperature_c": 24.3, "wind_speed_kmh": 8.1})
        lat, lon = CITY_COORDS["Tbilisi"]
        client.fetch.assert_called_once_with(lat, lon, "Tbilisi")

    def test_unknown_city(self):
        client = MagicMock()

        with self.assertRaises(UnknownCityError):
            get_weather_for_city(client, "Moscow")

        client.fetch.assert_not_called()  # უცნობ ქალაქზე API-ს საერთოდ არ ვეძახით

    def test_client_error_propagates(self):
        client = MagicMock()
        client.fetch.side_effect = WeatherAPIError("API ჩავარდა")

        with self.assertRaises(WeatherAPIError):
            get_weather_for_city(client, "Batumi")


class TestCurrencyLogic(unittest.TestCase):
    def test_success_keeps_only_needed_fields(self):
        client = MagicMock()
        client.get_rates.return_value = {
            "date": "2026-08-27T00:00:00.000Z",
            "currencies": [
                {"code": "USD", "name": "აშშ დოლარი", "quantity": 1, "rate": 2.7, "diff": 0.01},
                {"code": "EUR", "name": "ევრო", "quantity": 1, "rate": 3.1, "diff": -0.02},
            ],
        }

        result = get_currency_rates(client)

        self.assertEqual(result["date"], "2026-08-27T00:00:00.000Z")
        self.assertEqual(len(result["rates"]), 2)
        self.assertEqual(
            result["rates"][0],
            {"code": "USD", "name": "აშშ დოლარი", "quantity": 1, "rate": 2.7},
        )

    def test_client_error_propagates(self):
        client = MagicMock()
        client.get_rates.side_effect = CurrencyAPIError("NBG ჩავარდა")

        with self.assertRaises(CurrencyAPIError):
            get_currency_rates(client)


class TestSeismicLogic(unittest.TestCase):
    def test_success_passes_arguments(self):
        client = MagicMock()
        events = [{"event_id": "us1", "magnitude": 2.4}]
        client.get_recent_events.return_value = events

        result = get_seismic_events(client, "2026-08-01", "2026-08-30", 2.0)

        self.assertEqual(result, events)
        client.get_recent_events.assert_called_once_with("2026-08-01", "2026-08-30", 2.0)

    def test_default_min_magnitude(self):
        client = MagicMock()
        client.get_recent_events.return_value = []

        get_seismic_events(client, "2026-08-01", "2026-08-30")

        client.get_recent_events.assert_called_once_with("2026-08-01", "2026-08-30", 1.5)

    def test_client_error_propagates(self):
        client = MagicMock()
        client.get_recent_events.side_effect = SeismicAPIError("USGS ჩავარდა")

        with self.assertRaises(SeismicAPIError):
            get_seismic_events(client, "2026-08-01", "2026-08-30")


if __name__ == "__main__":
    unittest.main(verbosity=2)