from typing import List, Optional

from pydantic.main import BaseModel


class WeatherDetails(BaseModel):
    id: int
    main: str
    description: str
    icon: str


class WeatherDaySingle(BaseModel):
    dt: int
    sunrise: int
    sunset: int
    temp: float
    feels_like: float
    pressure: int
    humidity: int
    dew_point: float
    uvi: float
    clouds: int
    visibility: Optional[int] = None
    wind_speed: float
    wind_deg: int
    wind_gust: Optional[float]
    weather: List[WeatherDetails]


class DayBreakDown(BaseModel):
    day: float
    min: Optional[float] = None
    max: Optional[float] = None
    night: float
    eve: float
    morn: float


class WeatherDay(WeatherDaySingle):
    temp: DayBreakDown
    feels_like: DayBreakDown
    pop: int


class WeatherReport(BaseModel):
    current: WeatherDaySingle
    daily: List[WeatherDay]
