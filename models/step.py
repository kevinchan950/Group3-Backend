from models.base_model import BaseModel
from models.recipe import Recipe 
import peewee as pw

class Step(BaseModel):
    number = pw.IntegerField(null=False)
    description = pw.TextField(null=False)
    recipe = pw.ForeignKeyField(Recipe, backref='steps', on_delete="CASCADE")