from typing import Optional

from fastapi import APIRouter, HTTPException

from ..cache import get_weather, set_weather
from ..heating.constants import WEATHER_URL
from ..models import WeatherReport
from ..utils import get_json

router = APIRouter()


@router.get("/weather/", response_model=Optional[WeatherReport])
async def weather():
    """Gets weather info from OpenWeatherMap API or from local cache"""
    weather_dict = await get_weather()
    try:
        if not weather_dict:
            r = await get_json(WEATHER_URL)
            weather_dict = {"current": r["current"], "daily": r["daily"]}
            await set_weather(weather_dict)
        weather_report = WeatherReport(**weather_dict)
        return weather_report
    except KeyError:
        raise HTTPException(
            status_code=500, detail="OpenWeatherMap API not setup or not responding"
        )
