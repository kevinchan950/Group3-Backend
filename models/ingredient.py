from models.base_model import BaseModel
import peewee as pw

class Ingredient(BaseModel):
    name = pw.CharField(unique=True, null=False)
    description = pw.CharField(null=True)
    ingredient_type = pw.CharField(null=False)
    image = pw.TextField(null=False)
    price = pw.DecimalField(null=False, decimal_places=2)
    stock = pw.IntegerField(null=False)

    def validate(self):
        duplicate_name = Ingredient.get_or_none(name=self.name)

        if duplicate_name:
            self.errors.append("Ingredient name exist!")
        
        if len(self.name.strip())==0:
            self.erros.append("Ingredient name cannot be blank!")

        if len(self.description.strip())==0:
            self.errors.append("Description cannot be blank!")
        
        if len(self.price.strip())==0:
            self.erros.append("Price cannot be blank!")
        
        if len(self.ingredient_type.strip())==0:
            self.errors.append("Ingredient type canot be blank!")

        if len(self.stock.strip())==0:
            self.errors.append("Stock cannot be blank!")
