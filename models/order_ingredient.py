from models.base_model import BaseModel
from models.user import User
from models.order import Order
import peewee as pw

class OrderIngredient(BaseModel):
    name = pw.CharField(unique=True, null=False)
    quantity = pw.IntegerField(null=False)
    amount = pw.DecimalField(null=False, decimal_places=2)
    user = pw.ForeignKeyField(User, backref="order_ingredients", on_delete="CASCADE")
    order = pw.ForeignKeyField(Order, backref="order_ingredients", on_delete="CASCADE")

    def validate(self):
        duplicate_name = OrderIngredient.get_or_none(name=self.name)

        if duplicate_name:
            self.errors.append("Ingredient duplicated!")