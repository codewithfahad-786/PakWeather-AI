from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cities data load karo - FIXED PATH FOR STREAMLIT CLOUD
CITIES_FILE = os.path.join(os.path.dirname(__file__), "pak_cities.json")

try:
    with open(CITIES_FILE, "r", encoding="utf-8") as f:
        PAK_CITIES = json.load(f)
except FileNotFoundError:
    # Backup agar file na mile
    PAK_CITIES = [
        {"name": "Karachi", "province": "Sindh", "country": "Pakistan", "lat": 24.8607, "lon": 67.0011},
        {"name": "Lahore", "province": "Punjab", "country": "Pakistan", "lat": 31.5497, "lon": 74.3436},
        {"name": "Islamabad", "province": "Islamabad", "country": "Pakistan", "lat": 33.6844, "lon": 73.0479},
        {"name": "Mirpur Khas", "province": "Sindh", "country": "Pakistan", "lat": 25.5251, "lon": 69.0159},
    ]

@app.get("/")
def root():
    return {"status": "PakWeather AI Backend Running"}

@app.get("/cities")
def search_cities(query: str):
    query = query.lower()
    result = [c for c in PAK_CITIES if query in c["name"].lower()][:10]
    return {"query": query, "count": len(result), "cities": result}

@app.get("/forecast")
def get_forecast(latitude: float, longitude: float, forecast_date: str, elevation: float = None):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=weathercode,temperature_2m_max,temperature_2m_min,temperature_2m_mean,apparent_temperature_max,apparent_temperature_min,precipitation_sum,rain_sum,precipitation_probability_max,windspeed_10m_max,windgusts_10m_max,winddirection_10m_dominant,sunrise,sunset&timezone=auto&forecast_days=1&start_date={forecast_date}&end_date={forecast_date}"
    r = requests.get(url)
    data = r.json()
    daily = data.get("daily", {})
    return {
        "status": "success",
        "date": forecast_date,
        "location": {"latitude": latitude, "longitude": longitude, "elevation": elevation},
        "weather_code": daily.get("weathercode", [0])[0] if daily.get("weathercode") else 0,
        "temperature": {"minimum": daily.get("temperature_2m_min", [0])[0], "average": daily.get("temperature_2m_mean", [0])[0], "maximum": daily.get("temperature_2m_max", [0])[0]},
        "apparent_temperature": {"minimum": daily.get("apparent_temperature_min", [0])[0], "maximum": daily.get("apparent_temperature_max", [0])[0]},
        "precipitation_mm": daily.get("precipitation_sum", [0])[0],
        "rain_mm": daily.get("rain_sum", [0])[0],
        "rain_probability": daily.get("precipitation_probability_max", [0])[0],
        "wind_speed_kmh": daily.get("windspeed_10m_max", [0])[0],
        "wind_gust_kmh": daily.get("windgusts_10m_max", [0])[0],
        "wind_direction": daily.get("winddirection_10m_dominant", [0])[0],
        "sunrise": daily.get("sunrise", [""])[0],
        "sunset": daily.get("sunset", [""])[0],
    }

@app.get("/hourly")
def get_hourly(latitude: float, longitude: float):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,apparent_temperature,relativehumidity_2m,precipitation,rain,precipitation_probability,weathercode,cloudcover,windspeed_10m,windgusts_10m,winddirection_10m&timezone=auto&forecast_days=1"
    r = requests.get(url)
    data = r.json()
    hourly = data.get("hourly", {})
    hours_list = []
    times = hourly.get("time", [])
    for i in range(len(times)):
        hours_list.append({
            "time": times[i],
            "temperature": hourly.get("temperature_2m", [])[i] if i < len(hourly.get("temperature_2m", [])) else 0,
            "feels_like": hourly.get("apparent_temperature", [])[i] if i < len(hourly.get("apparent_temperature", [])) else 0,
            "humidity": hourly.get("relativehumidity_2m", [])[i] if i < len(hourly.get("relativehumidity_2m", [])) else 0,
            "precipitation": hourly.get("precipitation", [])[i] if i < len(hourly.get("precipitation", [])) else 0,
            "rain": hourly.get("rain", [])[i] if i < len(hourly.get("rain", [])) else 0,
            "rain_probability": hourly.get("precipitation_probability", [])[i] if i < len(hourly.get("precipitation_probability", [])) else 0,
            "weather_code": hourly.get("weathercode", [])[i] if i < len(hourly.get("weathercode", [])) else 0,
            "cloud_cover": hourly.get("cloudcover", [])[i] if i < len(hourly.get("cloudcover", [])) else 0,
            "wind_speed": hourly.get("windspeed_10m", [])[i] if i < len(hourly.get("windspeed_10m", [])) else 0,
            "wind_gust": hourly.get("windgusts_10m", [])[i] if i < len(hourly.get("windgusts_10m", [])) else 0,
            "wind_direction": hourly.get("winddirection_10m", [])[i] if i < len(hourly.get("winddirection_10m", [])) else 0,
        })
    return {"status": "success", "location": {"latitude": latitude, "longitude": longitude}, "date": times[0][:10] if times else "", "hours": hours_list}

@app.get("/weather")
def get_16_day(latitude: float, longitude: float):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&daily=weathercode,temperature_2m_max,temperature_2m_min,temperature_2m_mean,apparent_temperature_max,apparent_temperature_min,precipitation_sum,rain_sum,precipitation_probability_max,windspeed_10m_max,windgusts_10m_max,winddirection_10m_dominant,sunrise,sunset&timezone=auto&forecast_days=16"
    r = requests.get(url)
    data = r.json()
    return {"status": "success", "location": {"latitude": latitude, "longitude": longitude}, "current_weather": data.get("current_weather", {}), "daily": data.get("daily", {})}
