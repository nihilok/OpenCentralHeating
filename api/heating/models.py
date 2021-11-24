from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, root_validator


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

    @staticmethod
    def parse_time(time_: Optional[str] = None) -> Optional[datetime.time]:
        if time_ is not None:
            return datetime.strptime(time_, "%H:%M").time()

    @root_validator(pre=True)
    def check_pairs(cls, values):
        if not values.get('on_1') and values.get('off_1'):
            raise ValueError('on_1 missing')
        if values.get('on_1') and not values.get('off_1'):
            raise ValueError('off_1 missing')
        if not values.get('on_2') and values.get('off_2'):
            raise ValueError('on_2 missing')
        if values.get('on_2') and not values.get('off_2'):
            raise ValueError('off_2 missing')

    @root_validator(pre=True)
    def order_of_times(cls, values):
        if cls.parse_time(values.get('on_1')) >= cls.parse_time(values.get('off_1')):
            raise ValueError('on_1 cannot be after off_1')
        elif values.get('on_2'):
            if cls.parse_time(values.get('on_1')) >= cls.parse_time(values.get('on_2')):
                raise ValueError('on_1 cannot be after on_2')


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
