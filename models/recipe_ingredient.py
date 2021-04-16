from enum import unique
from models.base_model import BaseModel
from models.recipe import Recipe 
import peewee as pw

class RecipeIngredient(BaseModel):
    name = pw.CharField(unique=True, null=False)
    quantity = pw.IntegerField(null=False)
    recipe = pw.ForeignKeyField(Recipe, backref='recipeingredients', on_delete="CASCADE")
