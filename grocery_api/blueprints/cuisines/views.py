from types import MethodDescriptorType
from flask import Blueprint, jsonify, request
from models.cuisine import Cuisine
from models.recipe import Recipe
from models.step import Step
from models.recipe_ingredient import RecipeIngredient
from models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity

cuisines_api_blueprint = Blueprint('cuisines_api', __name__)

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
        cuisine = Cuisine(name=name)
        if cuisine.save():
            return jsonify({"successful" : True, "message" : name + " cuisine is created successfully"})
        else:
            return jsonify({ "errors" : cuisine.errors })
    else:
        return jsonify({ "errors" : "Non-admin user detected. Request cannot be done." })


@cuisines_api_blueprint.route("/delete", methods=["POST"])
@jwt_required()
def delete_cuisine():
    user = User.get_by_id(get_jwt_identity())
    if user.is_admin:
        id = request.json.get("id")
        cuisine = Cuisine.get_by_id(id)
        cuisine.delete_instance()
        return jsonify({ "message" : cuisine.name + " cuisine has been successfully deleted!"})
    else:
        return jsonify({ "errors" : "Non-admin user detected. Request cannot be done." })    
# --------------------------------------------------------------------------------------------------------

# API for recipes of each cuisine
# --------------------------------------------------------------------------------------------------------
@cuisines_api_blueprint.route("/<cuisine_name>/recipes", methods=["GET"])
def show_cuisine_recipe(cuisine_name):
    cuisine = Cuisine.get_or_none(name=cuisine_name)

    if cuisine:
        recipe_all = Recipe.select().where(Recipe.cuisine_id == cuisine.id)
        results = []
        for recipe in recipe_all:
            recipe_data = {
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
            name = request.json.get("recipe_name")
            image = request.json.get("recipe_image")
            difficulty = request.json.get("recipe_difficulty")
            recipe = Recipe(name=name, image=image, difficulty=difficulty, cuisine_id=cuisine.id)
        
            if recipe.save():
                return jsonify({ "successful" : True , "message" : name + " has been successfully created for " + cuisine_name + " cuisine."})
            else:
                return jsonify({ "errors" : recipe.errors })
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
            id = request.json.get("recipe_id")
            recipe = Recipe.get_by_id(id)

            if recipe.cuisine_id == cuisine.id:
                recipe.delete_instance()
                return jsonify({ "message" : recipe.name + " has been successfully deleted from " + cuisine_name + " cuisine." })
            else:
                return jsonify({ "errors" : recipe.name + " is not found in " + cuisine_name + " cuisine."})
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
@cuisines_api_blueprint.route("/<cuisine_name>/recipes/<recipe_name>/<step_number>", methods=["GET"])
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