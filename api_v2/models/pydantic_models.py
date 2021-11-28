from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic.class_validators import root_validator

from . import Household, HouseholdMember, HeatingPeriod
from tortoise.contrib.pydantic import pydantic_model_creator


HouseholdPydantic = pydantic_model_creator(Household, name="Household")
HouseholdPydanticIn = pydantic_model_creator(
    Household, name="HouseholdIn", exclude_readonly=True
)
HouseholdMemberPydantic = pydantic_model_creator(
    HouseholdMember, name="HouseholdMember"
)
HouseholdMemberPydanticIn = pydantic_model_creator(
    HouseholdMember, name="HouseholdMemberIn", exclude_readonly=True
)


class PasswordChange(BaseModel):
    current_password: str
    password_check: str
    new_password: str


class Days(BaseModel):
    monday: bool = False
    tuesday: bool = False
    wednesday: bool = False
    thursday: bool = False
    friday: bool = False
    saturday: bool = False
    sunday: bool = False


class HeatingPeriodModel(BaseModel):
    time_on: str
    time_off: str
    days: Days
    target: int

    @root_validator
    def check_order(cls, v):
        time_on = datetime.strptime(v.get('time_on'), '%H:%M')
        time_off = datetime.strptime(v.get('time_off'), '%H:%M')
        if time_on >= time_off:
            raise ValueError('On-time cannot be after off-time')
        return v


HeatingPeriodModelCreator = pydantic_model_creator(HeatingPeriod, name='HeatingPeriod')


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