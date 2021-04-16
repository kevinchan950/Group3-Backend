from enum import unique
from models.base_model import BaseModel
import peewee as pw


class Cuisine(BaseModel):
    name = pw.CharField(unique=True)


    def validate(self):
        duplicate_name = Cuisine.get_or_none(Cuisine.name == self.name)

        if duplicate_name:
            self.errors.append("Duplicate cuisine name!")