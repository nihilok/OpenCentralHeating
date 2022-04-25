from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel
from pydantic.class_validators import root_validator
from tortoise.contrib.pydantic import pydantic_model_creator

from .authentication import Household, HouseholdMember
from .heating import HeatingPeriod, HeatingSystemModel

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
    monday: bool = True
    tuesday: bool = True
    wednesday: bool = True
    thursday: bool = True
    friday: bool = True
    saturday: bool = True
    sunday: bool = True


class PHeatingPeriod(BaseModel):
    time_on: str
    time_off: str
    days: Days
    target: int
    heating_system_id: int
    period_id: Optional[int] = None

    @root_validator
    def check_order(cls, v):
        time_on = datetime.strptime(v.get("time_on"), "%H:%M")
        time_off = datetime.strptime(v.get("time_off"), "%H:%M")
        if time_on >= time_off:
            raise ValueError("On-time cannot be after off-time")
        return v


HeatingPeriodModelCreator = pydantic_model_creator(HeatingPeriod, name="HeatingPeriod")
HeatingSystemModelCreator = pydantic_model_creator(
    HeatingSystemModel, name="HeatingSystem"
)


class PHeatingSystemIn(BaseModel):
    sensor_url: str
    raspberry_pi: Optional[str] = None
    gpio_pin: int


class Advance(BaseModel):
    on: bool = False
    start: Optional[int] = None
    relay: Optional[bool] = None


class HeatingConf(BaseModel):
    target: Optional[int] = None
    program_on: bool = True
    advance: Optional[Advance] = None


class SensorReadings(BaseModel):
    temperature: float
    pressure: float
    humidity: float


class HeatingInfo(BaseModel):
    sensor_readings: SensorReadings
    relay_on: bool
    advance: Optional[Advance] = None
    conf: Optional[HeatingConf] = None


class ConfResponse(BaseModel):
    conf: HeatingConf


class SystemInfo(BaseModel):
    sensor_readings: SensorReadings
    relay_on: bool
    program_on: bool
    target: float


class ProgramOnlyResponse(BaseModel):
    program_on: bool
    relay_on: bool


class HeatingV2Response(BaseModel):
    systems: List[SystemInfo] = []


class TimesResponse(BaseModel):
    periods: List[PHeatingPeriod]
