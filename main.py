from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import date, timedelta


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="PakWeather AI API",
    description="Weather search, GPS location, 24-hour and 16-day forecast API",
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
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "🇵🇰 PakWeather AI Backend is running!",
        "status": "online",
        "version": "4.0.0",
        "features": [
            "City Search",
            "GPS Reverse Geocoding",
            "24 Hour Forecast",
            "16 Day Forecast"
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
        "service": "PakWeather AI Backend"
    }


# ============================================================
# SEARCH PAKISTANI CITIES
# ============================================================

@app.get("/cities")
def search_cities(
    query: str = Query(
        ...,
        min_length=1,
        description="Pakistani city name"
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
# WEATHER - 16 DAYS
# ============================================================

@app.get("/weather")
def weather_forecast(

    latitude: float = Query(...),

    longitude: float = Query(...)
):

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
# 24 HOUR HOURLY FORECAST
# ============================================================

@app.get("/hourly")
def hourly_forecast(

    latitude: float = Query(...),

    longitude: float = Query(...)
):

    params = {

        "latitude": latitude,

        "longitude": longitude,

        "hourly": ",".join([

            "temperature_2m",

            "apparent_temperature",

            "precipitation_probability",

            "precipitation",

            "rain",

            "weather_code",

            "cloud_cover",

            "relative_humidity_2m",

            "wind_speed_10m",

            "wind_gusts_10m",

            "wind_direction_10m"
        ]),

        "daily": ",".join([

            "sunrise",

            "sunset"
        ]),

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

    # --------------------------------------------------------
    # First 24 hours only
    # --------------------------------------------------------

    result = {

        "time": times[:24],

        "temperature": hourly.get(
            "temperature_2m",
            []
        )[:24],

        "apparent_temperature": hourly.get(
            "apparent_temperature",
            []
        )[:24],

        "rain_probability": hourly.get(
            "precipitation_probability",
            []
        )[:24],

        "precipitation": hourly.get(
            "precipitation",
            []
        )[:24],

        "rain": hourly.get(
            "rain",
            []
        )[:24],

        "weather_code": hourly.get(
            "weather_code",
            []
        )[:24],

        "cloud_cover": hourly.get(
            "cloud_cover",
            []
        )[:24],

        "humidity": hourly.get(
            "relative_humidity_2m",
            []
        )[:24],

        "wind_speed": hourly.get(
            "wind_speed_10m",
            []
        )[:24],

        "wind_gust": hourly.get(
            "wind_gusts_10m",
            []
        )[:24],

        "wind_direction": hourly.get(
            "wind_direction_10m",
            []
        )[:24]
    }

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

        "hourly": result,

        "sunrise": (
            daily.get(
                "sunrise",
                [None]
            )[0]
        ),

        "sunset": (
            daily.get(
                "sunset",
                [None]
            )[0]
        )
    }


# ============================================================
# SPECIFIC DATE FORECAST
# ============================================================

@app.get("/forecast")
def forecast_for_date(

    latitude: float = Query(...),

    longitude: float = Query(...),

    forecast_date: date | None = Query(
        None
    ),

    elevation: float | None = Query(
        None
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
