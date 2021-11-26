import asyncio

from pydantic import BaseModel, root_validator
from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator


class HeatingPeriod(Model):
    period_id = fields.IntField(pk=True, auto_increment=True)
    time_on = fields.IntField()
    time_off = fields.IntField()
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
    time_on: int
    time_off: int
    days: Days
    household_id: int

    @root_validator
    def check_order(cls, v):
        if v.get('time_on') >= v.get('time_off'):
            raise ValueError('On-time cannot be after off-time')
        return v

    async def query(cls):
        return await HeatingPeriodModelCreator.from_queryset(HeatingPeriod.filter(household_id=cls.household_id))

    @root_validator
    def check_db(cls, v):
        loop = asyncio.get_running_loop()
        result = loop.run_until_complete(cls.query())
        for p in result:
            if p.time_on == v.get('time_on'):
                pass
        return v




HeatingPeriodModelCreator = pydantic_model_creator(HeatingPeriod, name='HeatingPeriod')
