from tortoise import Model, fields
from passlib.context import CryptContext


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

    class Meta:
        table = 'household_member'
