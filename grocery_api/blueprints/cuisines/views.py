from logging import error
from types import MethodDescriptorType
from flask import Blueprint, jsonify, request
from models.cuisine import Cuisine
from models.recipe import Recipe
from models.step import Step
from models.recipe_ingredient import RecipeIngredient
from models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
import boto3
import os

cuisines_api_blueprint = Blueprint('cuisines_api', __name__)

s3 = boto3.client(
    "s3",
    aws_access_key_id = os.getenv('AWS_KEY_ID'),
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
)
# API for Cuisine Section
# --------------------------------------------------------------------------------------------------------
@cuisines_api_blueprint.route("/", methods=["GET"])
def show_cuisine():
    cuisine_all = Cuisine.select()

    results = [] 
    for cuisine in cuisine_all:
        cuisine_data = {
            "name" : cuisine.name
        }
        results.append(cuisine_data)
    return jsonify({ "data" : results })


@cuisines_api_blueprint.route("/new", methods=["POST"])
@jwt_required()
def create_cuisine():
    user = User.get_by_id(get_jwt_identity())
    if user.is_admin: 
        name = request.json.get("name")
        if name=="":
            return error
        cuisine = Cuisine(name=name)
        if cuisine.save():
            return jsonify({"successful" : True, "message" : name + " cuisine is created successfully"})
        
    else:
        return jsonify({ "errors" : "Non-admin user detected. Request cannot be done." })


@cuisines_api_blueprint.route("/delete", methods=["POST"])
@jwt_required()
def delete_cuisine():
    user = User.get_by_id(get_jwt_identity())
    if user.is_admin:
        name = request.json.get("name")
        cuisine = Cuisine.get(name=name)
        cuisine.delete_instance()
        return jsonify({ "message" : cuisine.name + " cuisine has been successfully deleted!"})
    else:
        return jsonify({ "errors" : "Non-admin user detected. Request cannot be done." })


@cuisines_api_blueprint.route("/update", methods=["POST"])
@jwt_required()
def update_cuisine():
    user = User.get_by_id(get_jwt_identity())
    if user.is_admin:
        name = request.json.get("name")
        new_name = request.json.get("new_name")
        print(name)
        print(new_name)
        update = Cuisine.update(name=new_name).where(Cuisine.name==name)
        update.execute()
        return jsonify({ "message" : "Name has been successfully updated!"})
    else:
        return jsonify({ "errors" : "Non-admin user detected. Request cannot be done." })    
# --------------------------------------------------------------------------------------------------------

# API for recipes of each cuisine
# --------------------------------------------------------------------------------------------------------
@cuisines_api_blueprint.route("/recipes/<id>", methods=["GET"])
def show_single_recipe(id):
    recipe = Recipe.get_by_id(id)
    step = Step.select().where(Step.recipe_id==id)
    recipe_ingredient = RecipeIngredient.select().where(RecipeIngredient.recipe_id == id)
    if recipe: 
        
        step_data = []
        for s in step:
            data = {
                "number": s.number,
                "description": s.description
            }
            step_data.append(data)

        ingredient_data = []
        for i in recipe_ingredient:
            data = {
                "name": i.name
            }
            ingredient_data.append(data)
        
        results = {
            "id" : recipe.id,
            "name" : recipe. name,
            "image" : recipe.image,
            "step" : step_data,
            "ingredient": ingredient_data
        }
        return jsonify({ "data" : results})


@cuisines_api_blueprint.route("/<cuisine_name>/recipes", methods=["GET"])
def show_cuisine_recipe(cuisine_name):
    cuisine = Cuisine.get_or_none(name=cuisine_name)

    if cuisine:
        recipe_all = Recipe.select().where(Recipe.cuisine_id == cuisine.id)
        results=[]
        for recipe in recipe_all:
            recipe_data = {
                "name": recipe.name,
                "image": recipe.image,
                "difficulty": recipe.difficulty
            }
            results.append(recipe_data)
        return jsonify({ "data" : results})
    else:
        return jsonify({ "errors" : cuisine_name + " cuisine is not exist"})


@cuisines_api_blueprint.route("/<cuisine_name>/recipes/<difficulty>", methods=["GET"])
def show_cuisine_recipe_difficulty(cuisine_name,difficulty):
    cuisine = Cuisine.get_or_none(name=cuisine_name)

    if cuisine:
        recipe_difficulty = difficulty
        recipe_all = Recipe.select().where(Recipe.cuisine_id == cuisine.id, Recipe.difficulty==recipe_difficulty)
        results = []
        for recipe in recipe_all:
            recipe_data = {
                "id" : recipe.id,
                "name" : recipe.name,
                "image" : recipe.image,
                "difficulty" : recipe.difficulty
            }
            results.append(recipe_data)
        return jsonify({ "data" : results })
    else:
        return jsonify({ "errors" : cuisine_name + " cuisine is not exist"})



@cuisines_api_blueprint.route("/<cuisine_name>/recipes/new", methods=["POST"])
@jwt_required()
def create_cuisine_recipe(cuisine_name):
    user = User.get_by_id(get_jwt_identity())
 
    if user.is_admin:
        cuisine = Cuisine.get_or_none(name=cuisine_name)
        
        if cuisine:
            file = request.files.get('image')
            name = request.form.get("recipe_name")
            bucket_name = os.getenv('AWS_S3_BUCKET')
            s3.upload_fileobj(
                file,
                bucket_name,
                file.filename,
                ExtraArgs={
                    "ACL":"public-read",
                    "ContentType":file.content_type
                }
            )
            difficulty = request.form.get("recipe_difficulty")
            recipe = Recipe(name=name, image=f'https://kevinchan950-nextagram-flask.s3-ap-southeast-1.amazonaws.com/{file.filename}', difficulty=difficulty, cuisine_id=cuisine.id)
        
            if recipe.save():
                return jsonify({ "successful" : True , "message" : name + " has been successfully created for " + cuisine_name + " cuisine."})
        else:
            return jsonify({ "errors" : cuisine_name + " cuisine is not exist" })      
    else:
        return jsonify({ "errors" : "Non-admin user detected. Request cannot be done." }) 
    


@cuisines_api_blueprint.route("/<cuisine_name>/recipes/delete", methods=["POST"])
@jwt_required()
def delete_cuisine_recipe(cuisine_name):
    user = User.get_by_id(get_jwt_identity())

    if user.is_admin:
        cuisine = Cuisine.get_or_none(name=cuisine_name)
        
        if cuisine:
            name = request.json.get("recipe_name")
            recipe = Recipe.get(name=name)

            if recipe.cuisine_id == cuisine.id:
                recipe.delete_instance()
                return jsonify({ "message" : recipe.name + " has been successfully deleted from " + cuisine_name + " cuisine." })
            else:
                return jsonify({ "errors" : recipe.name + " is not found in " + cuisine_name + " cuisine."})
        else:
            return jsonify({ "errors" : cuisine_name + " cuisine is not exist" }) 
    else:
        return jsonify({ "errors" : "Non-admin user deteced. Request cannot be done." })


@cuisines_api_blueprint.route("/<cuisine_name>/recipes/update", methods=["POST"])
@jwt_required()
def update_cuisine_recipe(cuisine_name):
    user = User.get_by_id(get_jwt_identity())

    if user.is_admin:
        cuisine = Cuisine.get_or_none(name=cuisine_name)

        if cuisine: 
            update_field = request.form.get("update_field")

            if update_field == "name":
                name = request.form.get("recipe_name")
                recipe = Recipe.get(name=name)
                update_content = request.form.get("update_content")
                update = Recipe.update(name=update_content).where(Recipe.id == recipe.id)
                update.execute()
                return jsonify({ "message" : "Name has been successfully updated" })
            elif update_field == "difficulty":
                name = request.form.get("recipe_name")
                recipe = Recipe.get(name=name)
                update_content = request.form.get("update_content")
                update = Recipe.update(difficulty=update_content).where(Recipe.id == recipe.id)
                update.execute()
                return jsonify({ "message" : "Difficulty has been successfully updated" })
            elif update_field == "image":
                name = request.form.get("recipe_name")
                recipe = Recipe.get(name=name)
                file = request.files.get("image")
                bucket_name = os.getenv('AWS_S3_BUCKET')
                s3.upload_fileobj(
                    file,
                    bucket_name,
                    file.filename,
                    ExtraArgs={
                        "ACL":"public-read",
                        "ContentType":file.content_type
                    }
                )
                update = Recipe.update(image=f'https://kevinchan950-nextagram-flask.s3-ap-southeast-1.amazonaws.com/{file.filename}').where(Recipe.id == recipe.id)
                update.execute()
                return jsonify({ "message" : "Image has been successfully updated" })
            else:
                return error
        else:
            return jsonify({ "errors" : cuisine_name + " cuisine is not exist" })
    else:
        return jsonify({ "errors" : "Non-admin user deteced. Request cannot be done." })


@cuisines_api_blueprint.route("/<cuisine_name>/recipes/<recipe_name>", methods=["GET"])
def show_cuisine_single_recipe(cuisine_name, recipe_name):
    cuisine = Cuisine.get_or_none(name=cuisine_name)

    if cuisine:
        is_recipe = Recipe.get_or_none(name=recipe_name)

        if is_recipe:
            recipe = Recipe.select().where(Recipe.cuisine_id == cuisine.id, Recipe.name == recipe_name)
            if recipe:
                for r in recipe:
                    result = {
                        "name" : r.name,
                        "image" : r.image,
                        "difficulty" : r.difficulty
                    }
                return jsonify({ "data": result })
            else:
                return jsonify({ "erros" : recipe_name + " is not found in " + cuisine_name + " cuisine." })
        else:
            return jsonify({ "errors" : "Recipe not exists" })
    else:
        return jsonify({ "errors" : cuisine_name + " cuisine is not exist"})
# --------------------------------------------------------------------------------------------------------

# API for step of each recipe
# --------------------------------------------------------------------------------------------------------
@cuisines_api_blueprint.route("/<cuisine_name>/recipes/<recipe_name>/steps/<step_number>", methods=["GET"])
def show_recipe_step(cuisine_name, recipe_name, step_number):
    cuisine = Cuisine.get_or_none(name=cuisine_name)

    if cuisine:
        recipe = Recipe.get_or_none(name=recipe_name)
        if recipe:
            if recipe.cuisine_id == cuisine.id:
                step = Step.select().where(Step.recipe_id == recipe.id, Step.number == step_number)
                for s in step:
                    result = {
                        "step_number" : s.number,
                        "description" : s.description
                    }
                return jsonify({ "data" : result })
            else:
                return jsonify({ "errors" : recipe_name + " is not found in " + cuisine_name + " cuisine." })
        else:
            return jsonify({ "errors" : "Recipe not exists" })
    else:
        return jsonify({ "errors" : cuisine_name + " cusine is not exist" })


@cuisines_api_blueprint.route("/<cuisine_name>/recipes/<recipe_name>/steps", methods=["GET"])
def show_recipe_all_step(cuisine_name, recipe_name):
    cuisine = Cuisine.get_or_none(name=cuisine_name)
    if cuisine:
        recipe = Recipe.get_or_none(name=recipe_name)
        if recipe:
            step_all = Step.select().where(Step.recipe_id == recipe.id)
            results = []
            for step in step_all:
                step_data = {
                    "step_number" : step.number,
                    "step_description" : step.description
                }
                results.append(step_data)
            return jsonify({
                "data" : results
            })
        else:
            return jsonify({ "errors" : recipe_name + " is not found in " + cuisine_name + " cuisine." })      
    else:        
        return jsonify({ "errors" : cuisine_name + " cusine is not exist" })

@cuisines_api_blueprint.route("/<cuisine_name>/recipes/<recipe_name>/steps/new", methods=["POST"])
@jwt_required()
def new_recipe_step(cuisine_name, recipe_name):
    user = User.get_by_id(get_jwt_identity())
    cuisine = Cuisine.get_or_none(name=cuisine_name)
    if user.is_admin:
        if cuisine:
            recipe = Recipe.get_or_none(name=recipe_name)
            if recipe:
                step_number = request.form.get("step_number")
                step_description = request.form.get("step_description")
                new_step = Step(number=step_number, description=step_description, recipe_id=recipe.id)
                new_step.save()
                return jsonify({"message" : "Step successfully created!"})
            else:
                return jsonify({ "errors" : "Recipe not exists" })
        else:
            return jsonify({ "errors" : cuisine_name + " cusine is not exist" })
    else:
        return 0


@cuisines_api_blueprint.route("/<cuisine_name>/recipes/<recipe_name>/steps/delete", methods=["POST"])
@jwt_required()
def delete_recipe_step(cuisine_name, recipe_name):
    user = User.get_by_id(get_jwt_identity())
    cuisine = Cuisine.get_or_none(name=cuisine_name)
    if user.is_admin:
        if cuisine:
            recipe = Recipe.get_or_none(name=recipe_name)
            if recipe:
                step_number = request.form.get("step_number")
                delete = Step.delete().where(Step.number==step_number, Step.recipe_id == recipe.id)
                delete.execute()
                return jsonify({ "message" : "Step has been successfully deleted." })
            else:
                return jsonify({ "errors" : "Recipe not exists" })
        else:
            return jsonify({ "errors" : cuisine_name + " cusine is not exist" })
    else:
        return 0



@cuisines_api_blueprint.route("/<cuisine_name>/recipes/<recipe_name>/steps/update", methods=["POST"])
@jwt_required()
def update_recipe_step(cuisine_name, recipe_name):
    user = User.get_by_id(get_jwt_identity())
    cuisine = Cuisine.get_or_none(name=cuisine_name)
    if user.is_admin:
        if cuisine:
            recipe = Recipe.get_or_none(name=recipe_name)
            if recipe:
                step_number = request.form.get("step_number")
                new_description = request.form.get("new_description")
                update = Step.update(description=new_description).where(Step.recipe_id==recipe.id, Step.number == step_number)
                update.execute()            
                return jsonify({ "message" : "Step has been successfully updated." })
            else:
                return jsonify({ "errors" : "Recipe not exists" })
        else:
            return jsonify({ "errors" : cuisine_name + " cusine is not exist" })
    else:
       return 0 
# --------------------------------------------------------------------------------------------------------

# API for ingredient of each recipe
# --------------------------------------------------------------------------------------------------------
@cuisines_api_blueprint.route("/<cuisine_name>/recipes/<recipe_name>/ingredients", methods=["GET"])
def show_recipe_ingredient(cuisine_name, recipe_name):
    cuisine = Cuisine.get_or_none(name=cuisine_name)

    if cuisine:
        recipe = Recipe.get_or_none(name=recipe_name)
        if recipe:
            if recipe.cuisine_id == cuisine.id:
                ingredient = RecipeIngredient.select().where(RecipeIngredient.recipe_id == recipe.id)
                results = []
                for i in ingredient:
                    ingredient_data = {
                        "name" : i.name,
                        "quantity": i.quantity
                    }
                    results.append(ingredient_data)
                return jsonify({ "data" : results })
            else:
                return jsonify({ "errors" : recipe_name + " is not found in " + cuisine_name + " cuisine." })
        else:
            return jsonify({ "errors" : "Recipe not exists" })
    else:
        return jsonify({ "errors" : cuisine_name + " cusine is not exist" })


@cuisines_api_blueprint.route("/<cuisine_name>/recipes/<recipe_name>/ingredients/new", methods=["POST"])
@jwt_required()
def add_recipe_ingredient(cuisine_name, recipe_name):
    current_user = User.get_by_id(get_jwt_identity())

    if current_user.is_admin:
        cuisine = Cuisine.get_or_none(name=cuisine_name)
        if cuisine:
            recipe = Recipe.get_or_none(name=recipe_name)
            if recipe:
                if recipe.cuisine_id == cuisine.id:
                    quantity = request.form.get("quantity")
                    name = request.form.get("name")
                    recipe_ingredient = RecipeIngredient(name= name, quantity= quantity, recipe_id=recipe.id)
                    recipe_ingredient.save()
                    return jsonify({ "message" : "Ingredient has been successfully created!"})
                else:
                    return jsonify({ "errors" : recipe_name + " is not found in " + cuisine_name + " cuisine." })
            else:
                return jsonify({ "errors" : "Recipe not exists" })
        else:
            return jsonify({ "errors" : cuisine_name + " cusine is not exist" })
    else:
        return 0    


@cuisines_api_blueprint.route("/<cuisine_name>/recipes/<recipe_name>/ingredients/delete", methods=["POST"])
@jwt_required()
def delete_recipe_ingredient(cuisine_name, recipe_name):
    current_user = User.get_by_id(get_jwt_identity())

    if current_user.is_admin:
        cuisine = Cuisine.get_or_none(name=cuisine_name)
        if cuisine:
            recipe = Recipe.get_or_none(name=recipe_name)
            if recipe:
                if recipe.cuisine_id == cuisine.id:
                    name = request.form.get("name")
                    delete = RecipeIngredient.delete().where(RecipeIngredient.name == name, RecipeIngredient.recipe_id == recipe.id)
                    delete.execute()
                    return jsonify({ "message" : "Ingredient has been successfully deleted!"})
                else:
                    return jsonify({ "errors" : recipe_name + " is not found in " + cuisine_name + " cuisine." })
            else:
                return jsonify({ "errors" : "Recipe not exists" })
        else:
            return jsonify({ "errors" : cuisine_name + " cusine is not exist" })
    else:
        return 0
