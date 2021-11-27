import asyncio
from datetime import datetime

from pydantic import BaseModel, root_validator
from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator


class HeatingPeriod(Model):
    period_id = fields.IntField(pk=True, auto_increment=True)
    time_on = fields.CharField(5)
    time_off = fields.CharField(5)
    days = fields.JSONField()
    household = fields.ForeignKeyField(model_name='models.Household', related_name='periods', on_delete=fields.CASCADE)


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

    @root_validator
    def check_order(cls, v):
        time_on = datetime.strptime(v.get('time_on'), '%H:%M')
        time_off = datetime.strptime(v.get('time_off'), '%H:%M')
        if time_on >= time_off:
            raise ValueError('On-time cannot be after off-time')
        return v


HeatingPeriodModelCreator = pydantic_model_creator(HeatingPeriod, name='HeatingPeriod')
