# ============================================================
# 🇵🇰 PakWeather AI - FastAPI Backend
# ============================================================
# Features:
# 1. Pakistani city search
# 2. GPS coordinates → actual location
# 3. Current weather
# 4. 16-day weather forecast
# 5. Specific-date forecast
# 6. Sunrise / Sunset
# 7. Rain probability
# 8. Wind information
# 9. Temperature information
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
        "Weather search, GPS location, reverse geocoding "
        "and 16-day forecast API for Pakistan"
    ),
    version="4.0.0"
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
# API URLS
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

DAILY_PARAMETERS = [
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
    "sunset",
]


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "🇵🇰 PakWeather AI Backend is running!",
        "status": "online",
        "version": "4.0.0",
        "features": [
            "Pakistani city search",
            "GPS location",
            "Reverse geocoding",
            "Current weather",
            "16-day forecast",
            "Specific date forecast",
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
        "version": "4.0.0"
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

    search_query = query.strip()

    if not search_query:
        raise HTTPException(
            status_code=400,
            detail="City search query cannot be empty."
        )

    params = {
        "name": search_query,
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

        "status": "success",

        "query": search_query,

        "count": len(
            pakistan_cities
        ),

        "cities": pakistan_cities
    }


# ============================================================
# REVERSE GEOCODING
# GPS COORDINATES → CITY / DISTRICT / PROVINCE
# ============================================================

@app.get("/reverse-geocode")
def reverse_geocode(

    latitude: float = Query(
        ...,
        ge=-90,
        le=90,
        description="GPS latitude"
    ),

    longitude: float = Query(
        ...,
        ge=-180,
        le=180,
        description="GPS longitude"
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
                "User-Agent": "PakWeatherAI/4.0"
            }
        )

        response.raise_for_status()

        data = response.json()

    except requests.RequestException as e:

        raise HTTPException(
            status_code=503,
            detail=(
                "Location service unavailable: "
                f"{str(e)}"
            )
        )

    # --------------------------------------------------------
    # COUNTRY
    # --------------------------------------------------------

    country = data.get(
        "countryName",
        ""
    )

    country_code = data.get(
        "countryCode",
        ""
    )

    # --------------------------------------------------------
    # PAKISTAN CHECK
    # --------------------------------------------------------

    if (
        country_code.upper() != "PK"
        and country.lower() != "pakistan"
    ):

        raise HTTPException(
            status_code=400,
            detail="Current location is outside Pakistan."
        )

    # --------------------------------------------------------
    # CITY
    # --------------------------------------------------------

    city = (
        data.get("city")
        or data.get("locality")
        or data.get("principalSubdivision")
        or "Unknown"
    )

    # --------------------------------------------------------
    # PROVINCE
    # --------------------------------------------------------

    province = (
        data.get("principalSubdivision")
        or ""
    )

    # --------------------------------------------------------
    # DISTRICT
    # --------------------------------------------------------

    district_name = ""

    locality_info = data.get(
        "localityInfo",
        {}
    )

    administrative = locality_info.get(
        "administrative",
        []
    )

    if isinstance(administrative, list):

        for item in administrative:

            if not isinstance(item, dict):
                continue

            item_name = item.get(
                "name",
                ""
            )

            if (
                item_name
                and item_name != city
                and item_name != province
            ):

                district_name = item_name

                break

    # --------------------------------------------------------
    # FINAL LOCATION
    # --------------------------------------------------------

    return {

        "status": "success",

        "location": {

            "latitude": latitude,

            "longitude": longitude,

            "city": city,

            "district": district_name,

            "province": province,

            "country": "Pakistan",

            "country_code": "PK"
        }
    }


# ============================================================
# 16-DAY WEATHER FORECAST
# ============================================================

@app.get("/weather")
def weather_forecast(

    latitude: float = Query(
        ...,
        ge=-90,
        le=90,
        description="Location latitude"
    ),

    longitude: float = Query(
        ...,
        ge=-180,
        le=180,
        description="Location longitude"
    )
):

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "daily": ",".join(
            DAILY_PARAMETERS
        ),

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
            detail=(
                "Weather service unavailable: "
                f"{str(e)}"
            )
        )

    daily = data.get(
        "daily",
        {}
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

        "daily": daily
    }


# ============================================================
# SPECIFIC DATE FORECAST
# ============================================================

@app.get("/forecast")
def forecast_for_date(

    latitude: float = Query(
        ...,
        ge=-90,
        le=90,
        description="Location latitude"
    ),

    longitude: float = Query(
        ...,
        ge=-180,
        le=180,
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

    # --------------------------------------------------------
    # DEFAULT DATE
    # --------------------------------------------------------

    if forecast_date is None:

        forecast_date = today

    # --------------------------------------------------------
    # DATE VALIDATION
    # --------------------------------------------------------

    if forecast_date < today:

        raise HTTPException(
            status_code=400,
            detail="Past dates are not available."
        )

    if forecast_date > maximum_date:

        raise HTTPException(
            status_code=400,
            detail=(
                "Forecast is available "
                "for maximum 16 days."
            )
        )

    # --------------------------------------------------------
    # OPEN-METEO REQUEST
    # --------------------------------------------------------

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "daily": ",".join(
            DAILY_PARAMETERS
        ),

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
            detail=(
                "Weather service unavailable: "
                f"{str(e)}"
            )
        )

    # --------------------------------------------------------
    # DAILY DATA
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # SAFE VALUE HELPER
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------------

    return {

        "status": "success",

        "date": target,

        "location": {

            "latitude": latitude,

            "longitude": longitude,

            "elevation": elevation
        },

        "timezone": data.get(
            "timezone"
        ),

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
# 16-DAY FORECAST IN EASY FORMAT
# ============================================================

@app.get("/forecast-16-days")
def forecast_16_days(

    latitude: float = Query(
        ...,
        ge=-90,
        le=90,
        description="Location latitude"
    ),

    longitude: float = Query(
        ...,
        ge=-180,
        le=180,
        description="Location longitude"
    )
):

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "daily": ",".join(
            DAILY_PARAMETERS
        ),

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
            detail=(
                "Weather service unavailable: "
                f"{str(e)}"
            )
        )

    daily = data.get(
        "daily",
        {}
    )

    dates = daily.get(
        "time",
        []
    )

    forecast_list = []

    for index, forecast_date in enumerate(
        dates
    ):

        def value(
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

        forecast_list.append({

            "date": forecast_date,

            "weather_code": value(
                "weather_code"
            ),

            "temperature": {

                "minimum": value(
                    "temperature_2m_min"
                ),

                "average": value(
                    "temperature_2m_mean"
                ),

                "maximum": value(
                    "temperature_2m_max"
                )
            },

            "apparent_temperature": {

                "minimum": value(
                    "apparent_temperature_min"
                ),

                "maximum": value(
                    "apparent_temperature_max"
                )
            },

            "precipitation_mm": value(
                "precipitation_sum",
                0
            ),

            "rain_mm": value(
                "rain_sum",
                0
            ),

            "rain_probability": value(
                "precipitation_probability_max",
                0
            ),

            "wind_speed_kmh": value(
                "wind_speed_10m_max",
                0
            ),

            "wind_gust_kmh": value(
                "wind_gusts_10m_max",
                0
            ),

            "wind_direction": value(
                "wind_direction_10m_dominant"
            ),

            "sunrise": value(
                "sunrise"
            ),

            "sunset": value(
                "sunset"
            )
        })

    return {

        "status": "success",

        "location": {

            "latitude": latitude,

            "longitude": longitude
        },

        "timezone": data.get(
            "timezone"
        ),

        "forecast_days": len(
            forecast_list
        ),

        "forecast": forecast_list
    }


# ============================================================
# END
# ============================================================
