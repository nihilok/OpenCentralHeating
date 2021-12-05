import re

from tortoise import Model, fields
from tortoise.exceptions import ValidationError
from tortoise.validators import RegexValidator

from api_v2.heating.systems_in_memory import systems_in_memory


def target_validator(value: int):
    if value > 30 or value < 5:
        raise ValidationError(f"Target must be between 30 and 5 ({value} is not)")


class HeatingSystemModel(Model):
    system_id = fields.IntField(pk=True, auto_increment=True)
    household = fields.ForeignKeyField(
        model_name="models.Household",
        related_name="heating_systems",
        on_delete=fields.CASCADE,
    )
    sensor_url = fields.CharField(100)
    raspberry_pi = fields.CharField(100, null=True, blank=True)
    gpio_pin = fields.IntField()
    activated = fields.BooleanField(default=False)

    @classmethod
    async def get_by_household_id(cls, household_id: int):
        return await cls.filter(household_id=household_id)

    @classmethod
    async def get_by_system_id(cls, system_id: int):
        return await cls.get(system_id=system_id)

    @property
    def is_running(self):
        return self.system_id in systems_in_memory.keys()

    class Meta:
        table = "heating_system"


class HeatingPeriod(Model):
    period_id = fields.IntField(pk=True, auto_increment=True)
    time_on = fields.CharField(
        5, validators=[RegexValidator("[0-2]?[0-9]:[0-5][0-9]", re.I)]
    )
    time_off = fields.CharField(
        5, validators=[RegexValidator("[0-2]?[0-9]:[0-5][0-9]", re.I)]
    )
    target = fields.IntField(validators=[target_validator])
    days = fields.JSONField()
    household = fields.ForeignKeyField(
        model_name="models.Household", related_name="periods", on_delete=fields.CASCADE
    )
    created = fields.DatetimeField(auto_now_add=True)
    created_by = fields.ForeignKeyField(
        model_name="models.HouseholdMember",
        related_name="periods",
        on_delete=fields.CASCADE,
    )
    heating_system = fields.ForeignKeyField(
        model_name="models.HeatingSystemModel",
        related_name="periods",
        on_delete=fields.CASCADE,
    )
    all_systems = fields.BooleanField(default=False)

    class Meta:
        table = "heating_period"
