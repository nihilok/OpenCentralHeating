from typing import Optional

from pydantic import BaseModel


class Advance(BaseModel):
    on: bool = False
    start: Optional[int] = None
    relay: Optional[bool] = None


class HeatingConf(BaseModel):
    on_1: str
    off_1: str
    on_2: Optional[str] = None
    off_2: Optional[str] = None
    target: int = 20
    program_on: bool = True
    advance: Optional[Advance] = None


class SensorReadings(BaseModel):
    temperature: float
    pressure: float
    humidity: float


class HeatingInfo(BaseModel):
    indoor_temperature: float
    sensor_readings: SensorReadings
    relay_on: bool
    advance: Optional[Advance] = None
    conf: Optional[HeatingConf] = None


class ConfResponse(BaseModel):
    conf: HeatingConf


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
    visibility: int
    wind_speed: float
    wind_deg: int
    wind_gust: float
    weather: list[WeatherDetails]


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
    daily: list[WeatherDay]
