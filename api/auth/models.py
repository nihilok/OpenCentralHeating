from passlib.context import CryptContext
from tortoise import Tortoise
from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Household(Model):
    id = fields.IntField(pk=True)
    week = fields.BinaryField(null=True)


HouseholdPydantic = pydantic_model_creator(Household, name='Household')
HouseholdPydanticIn = pydantic_model_creator(Household, name='HouseholdIn', exclude_readonly=True)


class HouseholdMember(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(100, unique=True)
    password_hash = fields.CharField(128)
    household = fields.ForeignKeyField('models.Household', related_name='members')

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


HouseholdMemberPydantic = pydantic_model_creator(HouseholdMember, name='HouseholdMember')
HouseholdMemberPydanticIn = pydantic_model_creator(HouseholdMember, name='HouseholdMemberIn', exclude_readonly=True)

# Tortoise.init_models(["api.auth.models"], "models")
