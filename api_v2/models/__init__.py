from tortoise import Tortoise

from .authentication import Household, HouseholdMember
from .heating import HeatingSystemModel, HeatingPeriod
from .. import settings

Tortoise.init_models(settings.TORTOISE_MODELS_LIST, "models")

from .pydantic_models import (
    HouseholdPydantic,
    HouseholdPydanticIn,
    HouseholdMemberPydantic,
    HouseholdMemberPydanticIn,
    PasswordChange,
    Days,
    PHeatingPeriod,
    HeatingPeriodModelCreator,
    Advance,
    HeatingConf,
    SensorReadings,
    HeatingInfo,
    ConfResponse,
    PHeatingSystemIn,
    HeatingSystemModelCreator,
    TimesResponse,
    HeatingV2Response,
    SystemInfo,
    ProgramOnlyResponse,
)
from .weather import (
    WeatherDay,
    WeatherDaySingle,
    WeatherReport,
    WeatherDetails,
    DayBreakDown,
)
