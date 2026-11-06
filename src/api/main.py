"""
lecture 12: "Georgia Open Data Gateway" — FastAPI wrapper 3 მონაცემთა წყაროსთვის.
გაშვება პროექტის root-იდან:
    uvicorn "src.api.main:app" --reload
შემდეგ გახსენი: http://127.0.0.1:8000/docs (ავტომატური Swagger UI)
"""

import logging
import time
from datetime import date, timedelta

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request

from src.api.dependencies import get_currency_client, get_seismic_client, get_weather_client
from src.api.logic import (
    UnknownCityError,
    get_currency_rates,
    get_seismic_events,
    get_weather_for_city,
)
from src.api.schemas import CurrencyResponse, HealthResponse, SeismicEvent, WeatherResponse
from src.ingestion.currency_client import CurrencyAPIError
from src.ingestion.logging_config import setup_logging
from src.ingestion.seismic_client import SeismicAPIError
from src.ingestion.weather_client import WeatherAPIError

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Georgia Open Data Gateway",
    description="ერთიანი REST API სამი ღია მონაცემთა წყაროსთვის — ამინდი, ვალუტა, მიწისძვრები.",
    version="1.0.0",
)


# ---------- Middleware: ყველა request-ის ლოგირება ----------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    logger.info("%s %s -> %s (%.3fs)", request.method, request.url.path, response.status_code, duration)
    return response


# ---------- Background Task helper ----------
def _append_request_log(line: str) -> None:
    with open("request_log.txt", "a", encoding="utf-8") as f:
        f.write(line + "\n")


@app.get("/health", response_model=HealthResponse)
def health() -> dict:
    return {"status": "ok"}


@app.get("/weather/current", response_model=WeatherResponse)
def read_current_weather(
    background_tasks: BackgroundTasks,
    city: str = "Tbilisi",
    client=Depends(get_weather_client),
) -> dict:
    try:
        result = get_weather_for_city(client, city)
    except UnknownCityError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except WeatherAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    background_tasks.add_task(_append_request_log, f"weather query: {city}")
    return result


@app.get("/currency/rates", response_model=CurrencyResponse)
def read_currency_rates(client=Depends(get_currency_client)) -> dict:
    try:
        return get_currency_rates(client)
    except CurrencyAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/seismic/events", response_model=list[SeismicEvent])
def read_seismic_events(
    start_date: str = None,
    end_date: str = None,
    min_magnitude: float = 1.5,
    client=Depends(get_seismic_client),
) -> list:
    # თარიღებს function body-ში ვითვლით და არა signature-ში,
    # თორემ server startup-ზე "გაიყინებოდა"
    if end_date is None:
        end_date = str(date.today())
    if start_date is None:
        start_date = str(date.today() - timedelta(days=30))
    try:
        return get_seismic_events(client, start_date, end_date, min_magnitude)
    except SeismicAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc