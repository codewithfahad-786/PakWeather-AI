from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import date, timedelta
import time


# ============================================================
# 🇵🇰 PakWeather AI - FastAPI Backend
# ============================================================

app = FastAPI(
    title="PakWeather AI API",
    description="Weather search, GPS location, 24-hour and 16-day forecast API",
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
# WEATHER VARIABLES
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
    "precipitation",
    "rain",
    "precipitation_probability",
    "weather_code",
    "cloud_cover",
    "wind_speed_10m",
    "wind_gusts_10m",
    "wind_direction_10m"
])


# ============================================================
# HELPER - REQUEST WITH RETRY
# ============================================================

def make_request(
    url,
    params=None,
    headers=None,
    timeout=60,
    retries=2
):

    last_error = None

    for attempt in range(retries + 1):

        try:

            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout
            )

            response.raise_for_status()

            return response

        except requests.RequestException as error:

            last_error = error

            if attempt < retries:

                time.sleep(1)

            else:

                raise last_error


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
            "Pakistani City Search",
            "GPS Reverse Geocoding",
            "Current Location Weather",
            "24 Hour Forecast",
            "16 Day Forecast",
            "Specific Date Forecast"
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

        response = make_request(
            OPEN_METEO_GEOCODING,
            params=params,
            timeout=60
        )

        data = response.json()

    except requests.RequestException as error:

        raise HTTPException(
            status_code=503,
            detail=f"City search service unavailable: {str(error)}"
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

        response = make_request(
            REVERSE_GEOCODING,
            params=params,
            headers={
                "User-Agent": "PakWeatherAI/5.0"
            },
            timeout=60
        )

        data = response.json()

    except requests.RequestException as error:

        raise HTTPException(
            status_code=503,
            detail=f"Location service unavailable: {str(error)}"
        )

    country = data.get(
        "countryName",
        ""
    )

    country_code = data.get(
        "countryCode",
        ""
    )

    # --------------------------------------------------------
    # Pakistan check
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
    # City
    # --------------------------------------------------------

    city = (

        data.get("city")

        or data.get("locality")

        or data.get("principalSubdivision")

        or "Unknown"
    )

    # --------------------------------------------------------
    # Province
    # --------------------------------------------------------

    province = (

        data.get(
            "principalSubdivision"
        )

        or ""
    )

    # --------------------------------------------------------
    # District
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

    if isinstance(
        administrative,
        list
    ):

        for item in administrative:

            if not isinstance(
                item,
                dict
            ):
                continue

            name = item.get(
                "name",
                ""
            )

            if (
                name
                and name != city
            ):

                district_name = name

                break

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
# 24-HOUR FORECAST
# ============================================================

@app.get("/hourly")
def hourly_forecast(

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

        "hourly": HOURLY_VARIABLES,

        "timezone": "auto",

        "forecast_days": 2,

        "temperature_unit": "celsius",

        "wind_speed_unit": "kmh",

        "precipitation_unit": "mm"
    }

    try:

        response = make_request(
            OPEN_METEO_FORECAST,
            params=params,
            timeout=60
        )

        data = response.json()

    except requests.RequestException as error:

        raise HTTPException(
            status_code=503,
            detail=f"Hourly weather service unavailable: {str(error)}"
        )

    hourly = data.get(
        "hourly",
        {}
    )

    times = hourly.get(
        "time",
        []
    )

    if not times:

        raise HTTPException(
            status_code=404,
            detail="Hourly forecast data not found."
        )

    today = date.today().isoformat()

    selected_indices = [

        i

        for i, value in enumerate(times)

        if str(value).startswith(
            today
        )
    ]

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if not selected_indices:

        selected_indices = list(
            range(
                min(
                    24,
                    len(times)
                )
            )
        )

    # --------------------------------------------------------
    # Maximum 24 hours
    # --------------------------------------------------------

    selected_indices = selected_indices[:24]

    result = []

    for i in selected_indices:

        def value(
            key,
            default=None
        ):

            values = hourly.get(
                key,
                []
            )

            if i < len(values):

                return values[i]

            return default

        result.append({

            "time": value(
                "time"
            ),

            "temperature": value(
                "temperature_2m"
            ),

            "feels_like": value(
                "apparent_temperature"
            ),

            "humidity": value(
                "relative_humidity_2m"
            ),

            "precipitation": value(
                "precipitation",
                0
            ),

            "rain": value(
                "rain",
                0
            ),

            "rain_probability": value(
                "precipitation_probability",
                0
            ),

            "weather_code": value(
                "weather_code"
            ),

            "cloud_cover": value(
                "cloud_cover"
            ),

            "wind_speed": value(
                "wind_speed_10m",
                0
            ),

            "wind_gust": value(
                "wind_gusts_10m",
                0
            ),

            "wind_direction": value(
                "wind_direction_10m"
            )
        })

    return {

        "status": "success",

        "location": {

            "latitude": latitude,

            "longitude": longitude
        },

        "date": today,

        "hours": result
    }


# ============================================================
# 16-DAY FORECAST
# ============================================================

@app.get("/weather")
def weather_forecast(

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

        "daily": DAILY_VARIABLES,

        "timezone": "auto",

        "forecast_days": 16,

        "temperature_unit": "celsius",

        "wind_speed_unit": "kmh",

        "precipitation_unit": "mm"
    }

    try:

        response = make_request(
            OPEN_METEO_FORECAST,
            params=params,
            timeout=60
        )

        data = response.json()

    except requests.RequestException as error:

        raise HTTPException(
            status_code=503,
            detail=f"Weather service unavailable: {str(error)}"
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
# SPECIFIC DATE FORECAST
# ============================================================

@app.get("/forecast")
def forecast_for_date(

    latitude: float = Query(
        ...,
        ge=-90,
        le=90
    ),

    longitude: float = Query(
        ...,
        ge=-180,
        le=180
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
        today + timedelta(
            days=15
        )
    )

    # --------------------------------------------------------
    # Default date
    # --------------------------------------------------------

    if forecast_date is None:

        forecast_date = today

    # --------------------------------------------------------
    # Date validation
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

        response = make_request(
            OPEN_METEO_FORECAST,
            params=params,
            timeout=60
        )

        data = response.json()

    except requests.RequestException as error:

        raise HTTPException(
            status_code=503,
            detail=f"Weather service unavailable: {str(error)}"
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

    # --------------------------------------------------------
    # Safe value helper
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
    # Response
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
