from logging import error
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.cart import Cart
from models.ingredient import Ingredient

carts_api_blueprint = Blueprint('carts_api', __name__)


@carts_api_blueprint.route("/me", methods=["GET"])
@jwt_required()
def show_cart():
    current_user = User.get_by_id(get_jwt_identity())

    if current_user:
        cart = Cart.select().where(Cart.user_id==current_user.id)
        results = []
        for c in cart:
            c_data = {
                "ingredient": c.ingredient.name,
                "quantity": c.quantity,
                "amount" : c.amount
            }
            results.append(c_data)
        return jsonify({ "data" : results})
    else:
        return error

@carts_api_blueprint.route("/single/delete", methods=["POST"])
@jwt_required()
def remove_single_cart():
    current_user = User.get_by_id(get_jwt_identity())

    if current_user:
        name = request.form.get("name")
        ingredient = Ingredient.get(name=name)
        delete = Cart.delete().where(Cart.ingredient_id==ingredient.id, Cart.user_id == current_user.id)
        delete.execute()
        return jsonify({"data":"Ingredient has been removed from cart!"})
    else:
        return error


@carts_api_blueprint.route("/delete", methods=["POST"])
@jwt_required()
def delete_cart():
    current_user = User.get_by_id(get_jwt_identity())

    if current_user:
        delete = Cart.delete().where(Cart.user_id==current_user.id)
        delete.execute()
        return jsonify({"data":"Ingredient has been removed from cart!"})
    else:
        return error


@carts_api_blueprint.route("/new", methods=["POST"])
@jwt_required()
def new_cart():
    current_user = User.get_by_id(get_jwt_identity())
    if current_user:
        name = request.form.get("name")
        ingredient = Ingredient.get(name=name)
        quantity = request.form.get("quantity")
        amount = int(quantity)*ingredient.price
        cart = Cart(quantity=quantity, amount=amount, user_id = current_user.id, ingredient_id = ingredient.id)
        if cart.save():
            return jsonify({"message" : "Ingredient has been successfully added into cart!"})
        else:
            return jsonify({"message": "Ingredient exists in cart already!"})
    else:
        return error