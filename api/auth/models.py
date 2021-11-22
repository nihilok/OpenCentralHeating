from passlib.context import CryptContext
from pydantic import BaseModel
from tortoise import Tortoise
from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Household(Model):
    id = fields.IntField(pk=True, auto_increment=True)
    week = fields.BinaryField(null=True)


class HouseholdMember(Model):
    id = fields.IntField(pk=True, auto_increment=True)
    name = fields.CharField(100, unique=True)
    password_hash = fields.CharField(128)
    household = fields.ForeignKeyField("models.Household", related_name="members")

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


Tortoise.init_models(["api.auth.models"], "models")

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
