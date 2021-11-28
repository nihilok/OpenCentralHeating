import re
from datetime import datetime

from pydantic import BaseModel, root_validator
from tortoise import Model, fields, Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.validators import RegexValidator
from tortoise.exceptions import ValidationError


def target_validator(value: int):
    if value > 30 or value < 5:
        raise ValidationError(f'Target must be between 30 and 5 ({value} is not)')


class HeatingPeriod(Model):
    period_id = fields.IntField(pk=True, auto_increment=True)
    time_on = fields.CharField(5, validators=[RegexValidator('[0-1]?[0-9]:[0-5][0-9]', re.I)])
    time_off = fields.CharField(5, validators=[RegexValidator('[0-1]?[0-9]:[0-5][0-9]', re.I)])
    target = fields.IntField(validators=[target_validator])
    days = fields.JSONField()
    household = fields.ForeignKeyField(model_name='models.Household', related_name='periods', on_delete=fields.CASCADE)
    created = fields.DatetimeField(auto_now_add=True)
    created_by = fields.ForeignKeyField(model_name='models.HouseholdMember', related_name='periods', on_delete=fields.CASCADE)


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


Tortoise.init_models(["api.auth.models", "api.heating.times.models"], "models")

HeatingPeriodModelCreator = pydantic_model_creator(HeatingPeriod, name='HeatingPeriod')
