from models.base_model import BaseModel
from models.user import User
import peewee as pw


class Order(BaseModel):
    total_amount = pw.DecimalField(null=False,decimal_places=2)
    user = pw.ForeignKeyField(User, backref='orders', on_delete="CASCADE")
