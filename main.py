# ============================================================
# 🇵🇰 PakWeather AI - FastAPI Backend
# Version 4.0.0
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
        "Weather search, GPS location, reverse geocoding, "
        "16-day forecast and 24-hour hourly forecast API"
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

DAILY_PARAMETERS = ",".join([
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


HOURLY_PARAMETERS = ",".join([
    "temperature_2m",
    "apparent_temperature",
    "precipitation_probability",
    "precipitation",
    "rain",
    "weather_code",
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
        "version": "4.0.0",
        "features": [
            "Pakistan city search",
            "GPS reverse geocoding",
            "Current weather",
            "24-hour hourly forecast",
            "16-day forecast"
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
            detail=f"Location service unavailable: {str(e)}"
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
        or data.get("principalSubdivisionCode")
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

            name = item.get(
                "name",
                ""
            )

            if name and name != city:

                district_name = name
                break

    # --------------------------------------------------------
    # RESPONSE
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

        "daily": DAILY_PARAMETERS,

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

        "daily": data.get(
            "daily",
            {}
        )
    }


# ============================================================
# 24-HOUR / HOURLY WEATHER FORECAST
# ============================================================

@app.get("/hourly")
def hourly_forecast(

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

        "hourly": HOURLY_PARAMETERS,

        "timezone": "auto",

        "forecast_days": 2,

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

    hourly = data.get(
        "hourly",
        {}
    )

    times = hourly.get(
        "time",
        []
    )

    temperatures = hourly.get(
        "temperature_2m",
        []
    )

    apparent_temperatures = hourly.get(
        "apparent_temperature",
        []
    )

    rain_probabilities = hourly.get(
        "precipitation_probability",
        []
    )

    precipitations = hourly.get(
        "precipitation",
        []
    )

    rains = hourly.get(
        "rain",
        []
    )

    weather_codes = hourly.get(
        "weather_code",
        []
    )

    wind_speeds = hourly.get(
        "wind_speed_10m",
        []
    )

    wind_gusts = hourly.get(
        "wind_gusts_10m",
        []
    )

    wind_directions = hourly.get(
        "wind_direction_10m",
        []
    )

    # --------------------------------------------------------
    # Build hourly records
    # --------------------------------------------------------

    records = []

    for i in range(len(times)):

        records.append({

            "time": times[i],

            "temperature": (
                temperatures[i]
                if i < len(temperatures)
                else None
            ),

            "feels_like": (
                apparent_temperatures[i]
                if i < len(apparent_temperatures)
                else None
            ),

            "rain_probability": (
                rain_probabilities[i]
                if i < len(rain_probabilities)
                else 0
            ),

            "precipitation_mm": (
                precipitations[i]
                if i < len(precipitations)
                else 0
            ),

            "rain_mm": (
                rains[i]
                if i < len(rains)
                else 0
            ),

            "weather_code": (
                weather_codes[i]
                if i < len(weather_codes)
                else None
            ),

            "wind_speed_kmh": (
                wind_speeds[i]
                if i < len(wind_speeds)
                else 0
            ),

            "wind_gust_kmh": (
                wind_gusts[i]
                if i < len(wind_gusts)
                else 0
            ),

            "wind_direction": (
                wind_directions[i]
                if i < len(wind_directions)
                else None
            )
        })

    # --------------------------------------------------------
    # Current local date
    # --------------------------------------------------------

    today_string = date.today().isoformat()

    today_records = [
        item
        for item in records
        if item["time"].startswith(
            today_string
        )
    ]

    # --------------------------------------------------------
    # If timezone/date mismatch occurs,
    # return first 24 records
    # --------------------------------------------------------

    if len(today_records) == 0:

        today_records = records[:24]

    else:

        today_records = today_records[:24]

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {

        "status": "success",

        "location": {

            "latitude": latitude,

            "longitude": longitude
        },

        "date": today_string,

        "count": len(today_records),

        "hourly": today_records
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

    # --------------------------------------------------------
    # DEFAULT DATE
    # --------------------------------------------------------

    if forecast_date is None:

        forecast_date = today

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # OPEN-METEO
    # --------------------------------------------------------

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "daily": DAILY_PARAMETERS,

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
    # SAFE VALUE
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
    # RESPONSE
    # --------------------------------------------------------

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
