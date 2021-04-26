from logging import error
from models.user import User
from models.ingredient import Ingredient
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from decimal import Decimal
import boto3
import os


ingredients_api_blueprint = Blueprint('ingredients_api', __name__)

s3 = boto3.client(
    "s3",
    aws_access_key_id = os.getenv("AWS_KEY_ID"),
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
)


@ingredients_api_blueprint.route("/", methods=["GET"])
def show_ingredient():
    ingredient_all = Ingredient.select()

    results=[]
    for ingredient in ingredient_all:
        ingredient_data = {
            "name" : ingredient.name,
            "description": ingredient.description,
            "price": Decimal(ingredient.price),
            "stock": ingredient.stock,
            "image": ingredient.image,
            "ingredient_type": ingredient.ingredient_type
        }
        results.append(ingredient_data)
    return jsonify({"data":results})


@ingredients_api_blueprint.route("/new", methods=["POST"])
@jwt_required()
def new_ingredient():
    current_user = User.get_by_id(get_jwt_identity())

    if current_user.is_admin:
        name = request.form.get("name")
        description = request.form.get("description")
        ingredient_type = request.form.get("ingredient_type")
        price = request.form.get("price")
        stock = request.form.get("stock")
        file = request.files.get("image")
        bucket_name = os.getenv("AWS_S3_BUCKET")
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ACL":"public-read",
                "ContentType":file.content_type
            }
        )

        ingredient = Ingredient(name = name, description = description, ingredient_type = ingredient_type, price = price, stock = stock, image = f'https://kevinchan950-nextagram-flask.s3-ap-southeast-1.amazonaws.com/{file.filename}')

        if ingredient.save():
            return jsonify({ "successful": True, "message" : "Ingredient is added successfully!"})
    else:
        return jsonify({"errors":"Non-admin user detected. Request cannot be done."})


@ingredients_api_blueprint.route("/delete", methods=["POST"])
@jwt_required()
def delete_ingredient():
    current_user = User.get_by_id(get_jwt_identity())

    if current_user.is_admin:
        name = request.form.get("name")
        if name=="":
            return error
        delete = Ingredient.delete().where(Ingredient.name==name)
        delete.execute()
        return jsonify({"message":"ingredients has been successfully deleted!"})
    else:
        return jsonify({"errors":"Non-admin user detected. Request cannot be done."})


@ingredients_api_blueprint.route("/update", methods=["POST"])
@jwt_required()
def update_ingredient():
    current_user = User.get_by_id(get_jwt_identity())

    if current_user.is_admin:
        update_field = request.form.get("update_field")
        name = request.form.get("name")
        
        if name == "":
            return error

        if update_field == "image":
            file = request.files.get("update_content")
            bucket_name = os.getenv("AWS_S3_BUCKET")
            s3.upload_fileobj(
                file,
                bucket_name,
                file.filename,
                ExtraArgs={
                    "ACL":"public-read",
                    "ContentType":file.content_type
                }
            )
            update = Ingredient.update(image=f'https://kevinchan950-nextagram-flask.s3-ap-southeast-1.amazonaws.com/{file.filename}').where(Ingredient.name == name)
            update.execute()
            return jsonify ({"message":"ingredients has been successfully updated!"})

        if update_field == "new_name":
            new_name = request.form.get("update_content")
            update = Ingredient.update(name=new_name).where(Ingredient.name == name)
            update.execute()
            return jsonify ({"message":"ingredients has been successfully updated!"})
        
        if update_field == "description":
            description = request.form.get("update_content")
            update = Ingredient.update(description = description).where(Ingredient.name == name)
            update.execute()
            return jsonify ({"message":"ingredients has been successfully updated!"})
        
        if update_field == "price":
            price = request.form.get("update_content")
            update = Ingredient.update(price=price).where(Ingredient.name == name)
            update.execute()
            return jsonify ({"message":"ingredients has been successfully updated!"})
        
        if update_field == "stock":
            stock = request.form.get("update_content")
            update = Ingredient.update(stock=stock).where(Ingredient.name == name)
            update.execute()
            return jsonify ({"message":"ingredients has been successfully updated!"})
        
        if update_field == "ingredient_type":
            ingredient_type = request.form.get("update_content")
            update = Ingredient.update(ingredient_type=ingredient_type).where(Ingredient.name == name)
            update.execute()
            return jsonify ({"message":"ingredients has been successfully updated!"})
    else:
        return jsonify({"errors":"Non-admin user detected. Request cannot be done."})
