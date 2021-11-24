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

    @root_validator
    def check_pairs(cls, values):
        if not values.get('on_1') and values.get('off_1'):
            raise ValueError('On 1 missing')
        if values.get('on_1') and not values.get('off_1'):
            raise ValueError('Off 1 missing')
        if not values.get('on_2') and values.get('off_2'):
            raise ValueError('On 2 missing')
        if values.get('on_2') and not values.get('off_2'):
            raise ValueError('Off 2 missing')
        return values

    @root_validator
    def order_of_times(cls, values):
        on_1, off_1, on_2, off_2 = (
            values.get("on_1"),
            values.get("off_1"),
            values.get("on_2"),
            values.get("off_2"),
        )
        if cls.parse_time(on_1) >= cls.parse_time(off_1):
            raise ValueError("On 1 cannot be after Off 1")
        elif on_2:
            if cls.parse_time(on_1) >= cls.parse_time(on_2):
                raise ValueError("On 1 cannot be after On 2")
            if cls.parse_time(off_1) > cls.parse_time(on_2):
                raise ValueError("Off 1 cannot be after On 2")
            if cls.parse_time(on_2) >= cls.parse_time(off_2):
                raise ValueError("On 2 cannot be after Off 2")
        return values


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
