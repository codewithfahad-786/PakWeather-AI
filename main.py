# ============================================================
# 🇵🇰 PakWeather AI - FastAPI Backend
# Version 5.0
# Features:
#   ✅ Pakistani city search
#   ✅ GPS reverse geocoding
#   ✅ Current weather
#   ✅ 24-hour hourly forecast
#   ✅ 16-day daily forecast
#   ✅ Sunrise / Sunset
#   ✅ Rain probability
#   ✅ Wind information
#   ✅ Feels-like temperature
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
    description=(
        "Pakistan weather API with city search, GPS location, "
        "current weather, 24-hour forecast and 16-day forecast."
    ),
    version="5.0.0"
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
# EXTERNAL APIs
# ============================================================

OPEN_METEO_GEOCODING = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

OPEN_METEO_FORECAST = (
    "https://api.open-meteo.com/v1/forecast"
)

REVERSE_GEOCODING = (
    "https://api.bigdatacloud.net/data/reverse-geocode-client"
)


# ============================================================
# COMMON WEATHER PARAMETERS
# ============================================================

DAILY_VARIABLES = ",".join([
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
])


HOURLY_VARIABLES = ",".join([
    "temperature_2m",
    "apparent_temperature",
    "relative_humidity_2m",
    "precipitation_probability",
    "precipitation",
    "rain",
    "weather_code",
    "cloud_cover",
    "wind_speed_10m",
    "wind_gusts_10m",
    "wind_direction_10m"
])


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "🇵🇰 PakWeather AI Backend is running!",
        "status": "online",
        "version": "5.0.0",
        "features": [
            "Pakistani city search",
            "GPS reverse geocoding",
            "Current weather",
            "24-hour forecast",
            "16-day forecast",
            "Rain probability",
            "Wind information",
            "Sunrise and sunset"
        ],
        "docs": "/docs"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "PakWeather AI Backend",
        "version": "5.0.0"
    }


# ============================================================
# SEARCH PAKISTANI CITIES
# ============================================================

@app.get("/cities")
def search_cities(
    query: str = Query(
        ...,
        min_length=1,
        description="Pakistani city name or partial city name"
    )
):

    params = {
        "name": query.strip(),
        "count": 20,
        "language": "en",
        "format": "json",
        "countryCode": "PK"
    }

    try:

        response = requests.get(
            OPEN_METEO_GEOCODING,
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

        if city.get("country_code", "").upper() != "PK":
            continue

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
                "elevation",
                0
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
# GPS REVERSE GEOCODING
# GPS COORDINATES → CITY
# ============================================================

@app.get("/reverse-geocode")
def reverse_geocode(

    latitude: float = Query(
        ...,
        ge=-90,
        le=90
    ),

    longitude: float = Query(
        ...,
        ge=-180,
        le=180
    )
):

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "localityLanguage": "en"
    }

    try:

        response = requests.get(
            REVERSE_GEOCODING,
            params=params,
            timeout=20,
            headers={
                "User-Agent": "PakWeatherAI/5.0"
            }
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as e:

        raise HTTPException(
            status_code=503,
            detail=f"Location service unavailable: {str(e)}"
        )

    country = data.get(
        "countryName",
        ""
    )

    country_code = data.get(
        "countryCode",
        ""
    )

    if (
        country_code.upper() != "PK"
        and country.lower() != "pakistan"
    ):

        raise HTTPException(
            status_code=400,
            detail="Current location is outside Pakistan."
        )

    city = (
        data.get("city")
        or data.get("locality")
        or data.get("principalSubdivision")
        or "Unknown"
    )

    province = (
        data.get("principalSubdivision")
        or ""
    )

    return {

        "status": "success",

        "location": {

            "latitude": latitude,

            "longitude": longitude,

            "city": city,

            "province": province,

            "country": "Pakistan",

            "country_code": "PK"
        }
    }


# ============================================================
# CURRENT WEATHER
# ============================================================

@app.get("/current")
def current_weather(

    latitude: float = Query(
        ...,
        description="Latitude"
    ),

    longitude: float = Query(
        ...,
        description="Longitude"
    )
):

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "is_day",
            "precipitation",
            "rain",
            "weather_code",
            "cloud_cover",
            "pressure_msl",
            "wind_speed_10m",
            "wind_gusts_10m",
            "wind_direction_10m"
        ]),

        "timezone": "auto",

        "temperature_unit": "celsius",

        "wind_speed_unit": "kmh",

        "precipitation_unit": "mm"
    }

    try:

        response = requests.get(
            OPEN_METEO_FORECAST,
            params=params,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as e:

        raise HTTPException(
            status_code=503,
            detail=f"Current weather service unavailable: {str(e)}"
        )

    return {

        "status": "success",

        "location": {

            "latitude": latitude,

            "longitude": longitude
        },

        "current": data.get(
            "current",
            {}
        )
    }


# ============================================================
# 24-HOUR WEATHER
# ============================================================

@app.get("/hourly")
def hourly_weather(

    latitude: float = Query(
        ...,
        description="Latitude"
    ),

    longitude: float = Query(
        ...,
        description="Longitude"
    )
):

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "hourly": HOURLY_VARIABLES,

        "forecast_hours": 24,

        "timezone": "auto",

        "temperature_unit": "celsius",

        "wind_speed_unit": "kmh",

        "precipitation_unit": "mm"
    }

    try:

        response = requests.get(
            OPEN_METEO_FORECAST,
            params=params,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as e:

        raise HTTPException(
            status_code=503,
            detail=f"Hourly weather service unavailable: {str(e)}"
        )

    return {

        "status": "success",

        "location": {

            "latitude": latitude,

            "longitude": longitude
        },

        "timezone": data.get(
            "timezone"
        ),

        "hourly": data.get(
            "hourly",
            {}
        )
    }


# ============================================================
# 16-DAY WEATHER
# ============================================================

@app.get("/weather")
def weather_forecast(

    latitude: float = Query(
        ...,
        description="Location latitude"
    ),

    longitude: float = Query(
        ...,
        description="Location longitude"
    )
):

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "daily": DAILY_VARIABLES,

        "timezone": "auto",

        "forecast_days": 16,

        "temperature_unit": "celsius",

        "wind_speed_unit": "kmh",

        "precipitation_unit": "mm"
    }

    try:

        response = requests.get(
            OPEN_METEO_FORECAST,
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

        "status": "success",

        "location": {

            "latitude": latitude,

            "longitude": longitude
        },

        "timezone": data.get(
            "timezone"
        ),

        "daily": data.get(
            "daily",
            {}
        )
    }


# ============================================================
# COMPLETE WEATHER
# CURRENT + 24 HOURS + 16 DAYS
# ============================================================

@app.get("/complete-weather")
def complete_weather(

    latitude: float = Query(
        ...,
        description="Location latitude"
    ),

    longitude: float = Query(
        ...,
        description="Location longitude"
    )
):

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "is_day",
            "precipitation",
            "rain",
            "weather_code",
            "cloud_cover",
            "pressure_msl",
            "wind_speed_10m",
            "wind_gusts_10m",
            "wind_direction_10m"
        ]),

        "hourly": HOURLY_VARIABLES,

        "daily": DAILY_VARIABLES,

        "forecast_hours": 24,

        "forecast_days": 16,

        "timezone": "auto",

        "temperature_unit": "celsius",

        "wind_speed_unit": "kmh",

        "precipitation_unit": "mm"
    }

    try:

        response = requests.get(
            OPEN_METEO_FORECAST,
            params=params,
            timeout=25
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as e:

        raise HTTPException(
            status_code=503,
            detail=f"Weather service unavailable: {str(e)}"
        )

    return {

        "status": "success",

        "location": {

            "latitude": latitude,

            "longitude": longitude
        },

        "timezone": data.get(
            "timezone"
        ),

        "current": data.get(
            "current",
            {}
        ),

        "hourly": data.get(
            "hourly",
            {}
        ),

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
        description="Location latitude"
    ),

    longitude: float = Query(
        ...,
        description="Location longitude"
    ),

    forecast_date: date | None = Query(
        None,
        description="Forecast date"
    ),

    elevation: float | None = Query(
        None,
        description="Location elevation"
    )
):

    today = date.today()

    maximum_date = (
        today + timedelta(days=15)
    )

    if forecast_date is None:

        forecast_date = today

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

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "daily": DAILY_VARIABLES,

        "timezone": "auto",

        "forecast_days": 16,

        "temperature_unit": "celsius",

        "wind_speed_unit": "kmh",

        "precipitation_unit": "mm"
    }

    try:

        response = requests.get(
            OPEN_METEO_FORECAST,
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

    def get_value(
        key,
        default=None
    ):

        values = daily.get(
            key,
            []
        )

        if index < len(values):

            return values[index]

        return default

    return {

        "status": "success",

        "date": target,

        "location": {

            "latitude": latitude,

            "longitude": longitude,

            "elevation": elevation
        },

        "weather_code": get_value(
            "weather_code"
        ),

        "temperature": {

            "minimum": get_value(
                "temperature_2m_min"
            ),

            "average": get_value(
                "temperature_2m_mean"
            ),

            "maximum": get_value(
                "temperature_2m_max"
            )
        },

        "apparent_temperature": {

            "minimum": get_value(
                "apparent_temperature_min"
            ),

            "maximum": get_value(
                "apparent_temperature_max"
            )
        },

        "precipitation_mm": get_value(
            "precipitation_sum",
            0
        ),

        "rain_mm": get_value(
            "rain_sum",
            0
        ),

        "rain_probability": get_value(
            "precipitation_probability_max",
            0
        ),

        "wind_speed_kmh": get_value(
            "wind_speed_10m_max",
            0
        ),

        "wind_gust_kmh": get_value(
            "wind_gusts_10m_max",
            0
        ),

        "wind_direction": get_value(
            "wind_direction_10m_dominant"
        ),

        "sunrise": get_value(
            "sunrise"
        ),

        "sunset": get_value(
            "sunset"
        )
    }


# ============================================================
# END
# ============================================================
