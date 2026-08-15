# ============================================================
# 🇵🇰 PakWeather AI - FastAPI Backend
# ============================================================

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import date, timedelta


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="PakWeather AI API",
    description="Weather search and forecast API for Pakistani cities",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "🇵🇰 PakWeather AI Backend is running!",
        "status": "online",
        "docs": "/docs"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "PakWeather AI Backend"
    }


# ============================================================
# SEARCH PAKISTANI CITIES
# ============================================================

@app.get("/cities")
def search_cities(
    query: str = Query(
        ...,
        min_length=2,
        description="City name or partial city name"
    )
):

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": query,
        "count": 20,
        "language": "en",
        "format": "json"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as e:

        raise HTTPException(
            status_code=503,
            detail=f"City search service unavailable: {str(e)}"
        )


    results = data.get("results", [])

    pakistan_cities = []


    for city in results:

        country_code = city.get(
            "country_code",
            ""
        )

        country = city.get(
            "country",
            ""
        )


        # Only Pakistan
        if (
            country_code.upper() == "PK"
            or country.lower() == "pakistan"
        ):

            pakistan_cities.append({

                "name": city.get(
                    "name",
                    "Unknown"
                ),

                "province": city.get(
                    "admin1",
                    ""
                ),

                "country": "Pakistan",

                "latitude": city.get(
                    "latitude"
                ),

                "longitude": city.get(
                    "longitude"
                ),

                "elevation": city.get(
                    "elevation"
                ),

                "timezone": city.get(
                    "timezone",
                    "auto"
                )
            })


    return {

        "query": query,

        "count": len(
            pakistan_cities
        ),

        "cities": pakistan_cities
    }


# ============================================================
# WEATHER FORECAST
# ============================================================

@app.get("/weather")
def weather_forecast(

    latitude: float = Query(
        ...,
        description="City latitude"
    ),

    longitude: float = Query(
        ...,
        description="City longitude"
    )
):

    today = date.today()

    end_date = (
        today + timedelta(days=15)
    )


    url = "https://api.open-meteo.com/v1/forecast"


    params = {

        "latitude": latitude,

        "longitude": longitude,

        "daily": ",".join([

            "weather_code",

            "temperature_2m_max",

            "temperature_2m_min",

            "temperature_2m_mean",

            "apparent_temperature_max",

            "apparent_temperature_min",

            "precipitation_sum",

            "rain_sum",

            "precipitation_probability_max",

            "wind_speed_10m_max",

            "wind_gusts_10m_max",

            "wind_direction_10m_dominant",

            "sunrise",

            "sunset"
        ]),

        "timezone": "auto",

        "forecast_days": 16,

        "temperature_unit": "celsius",

        "wind_speed_unit": "kmh",

        "precipitation_unit": "mm"
    }


    try:

        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as e:

        raise HTTPException(
            status_code=503,
            detail=f"Weather service unavailable: {str(e)}"
        )


    return {

        "location": {

            "latitude": latitude,

            "longitude": longitude
        },

        "forecast_period": {

            "start": str(today),

            "end": str(end_date)
        },

        "daily": data.get(
            "daily",
            {}
        )
    }


# ============================================================
# SPECIFIC DATE FORECAST
# ============================================================

@app.get("/forecast")
def forecast_for_date(

    latitude: float = Query(
        ...,
        description="City latitude"
    ),

    longitude: float = Query(
        ...,
        description="City longitude"
    ),

    forecast_date: date = Query(
        ...,
        description="Date between today and next 15 days"
    )
):

    today = date.today()

    maximum_date = (
        today + timedelta(days=15)
    )


    # Date validation

    if forecast_date < today:

        raise HTTPException(

            status_code=400,

            detail="Past dates are not available."
        )


    if forecast_date > maximum_date:

        raise HTTPException(

            status_code=400,

            detail="Forecast is available for maximum 16 days."
        )


    url = "https://api.open-meteo.com/v1/forecast"


    params = {

        "latitude": latitude,

        "longitude": longitude,

        "daily": ",".join([

            "weather_code",

            "temperature_2m_max",

            "temperature_2m_min",

            "temperature_2m_mean",

            "apparent_temperature_max",

            "apparent_temperature_min",

            "precipitation_sum",

            "rain_sum",

            "precipitation_probability_max",

            "wind_speed_10m_max",

            "wind_gusts_10m_max"
        ]),

        "timezone": "auto",

        "forecast_days": 16,

        "temperature_unit": "celsius",

        "wind_speed_unit": "kmh",

        "precipitation_unit": "mm"
    }


    try:

        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as e:

        raise HTTPException(

            status_code=503,

            detail=f"Weather service unavailable: {str(e)}"
        )


    daily = data.get(
        "daily",
        {}
    )


    dates = daily.get(
        "time",
        []
    )


    target = str(
        forecast_date
    )


    if target not in dates:

        raise HTTPException(

            status_code=404,

            detail="Forecast data not found."
        )


    index = dates.index(
        target
    )


    return {

        "date": target,

        "weather_code": daily[
            "weather_code"
        ][index],

        "temperature": {

            "minimum": daily[
                "temperature_2m_min"
            ][index],

            "average": daily[
                "temperature_2m_mean"
            ][index],

            "maximum": daily[
                "temperature_2m_max"
            ][index]
        },

        "apparent_temperature_max": daily[
            "apparent_temperature_max"
        ][index],

        "apparent_temperature_min": daily[
            "apparent_temperature_min"
        ][index],

        "precipitation_mm": daily[
            "precipitation_sum"
        ][index],

        "rain_mm": daily[
            "rain_sum"
        ][index],

        "rain_probability": daily[
            "precipitation_probability_max"
        ][index],

        "wind_speed_kmh": daily[
            "wind_speed_10m_max"
        ][index],

        "wind_gust_kmh": daily[
            "wind_gusts_10m_max"
        ][index]
    }