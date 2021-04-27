from models.base_model import BaseModel
from models.user import User
from models.ingredient import Ingredient
import peewee as pw


class Cart(BaseModel):
    quantity = pw.IntegerField(null=False)
    amount = pw.DecimalField(null=False, decimal_places=2)
    user = pw.ForeignKeyField(User, backref="carts", on_delete="CASCADE")
    ingredient = pw.ForeignKeyField(Ingredient)

    def validate(self):
        duplicate_ingredient = Cart.get_or_none(ingredient=self.ingredient)

        if duplicate_ingredient:
            self.errors.append("Ingredient duplicated!")