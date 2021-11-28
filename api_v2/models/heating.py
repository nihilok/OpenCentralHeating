import re
from tortoise import Model, fields
from tortoise.validators import RegexValidator
from tortoise.exceptions import ValidationError


def target_validator(value: int):
    if value > 30 or value < 5:
        raise ValidationError(f'Target must be between 30 and 5 ({value} is not)')


class HeatingPeriod(Model):
    period_id = fields.IntField(pk=True, auto_increment=True)
    time_on = fields.CharField(5, validators=[RegexValidator('[0-2]?[0-9]:[0-5][0-9]', re.I)])
    time_off = fields.CharField(5, validators=[RegexValidator('[0-2]?[0-9]:[0-5][0-9]', re.I)])
    target = fields.IntField(validators=[target_validator])
    days = fields.JSONField()
    household = fields.ForeignKeyField(model_name='models.Household', related_name='periods', on_delete=fields.CASCADE)
    created = fields.DatetimeField(auto_now_add=True)
    created_by = fields.ForeignKeyField(model_name='models.HouseholdMember', related_name='periods', on_delete=fields.CASCADE)
