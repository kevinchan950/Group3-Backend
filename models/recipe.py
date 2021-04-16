from enum import unique
from models.base_model import BaseModel
from models.cuisine import Cuisine
import peewee as pw

class Recipe(BaseModel):
    name = pw.CharField(unique=True, null=False)
    image = pw.TextField(null=False)
    difficulty = pw.CharField(null=False)
    cuisine = pw.ForeignKeyField(Cuisine, backref='recipes', on_delete="CASCADE")

    def validate(self):
        duplicate_name = Recipe.get_or_none(name=self.name)

        if duplicate_name:
            self.errors.append("Recipe has existed!") 