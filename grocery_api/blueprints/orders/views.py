from flask import Blueprint, request, jsonify
from peewee import Ordering
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.order import Order
from models.order_ingredient import OrderIngredient

orders_api_blueprint = Blueprint('orders_api', __name__)

@orders_api_blueprint.route("/me", methods=["GET"])
@jwt_required()
def show_order():
    current_user = User.get_by_id(get_jwt_identity())

    if current_user:
        order = Order.select().where(Order.user_id==current_user.id)

        result = []

        for o in order:
            data = {
                "id" : o.id,
                "amount" : o.total_amount
            }
            result.append(data)
        
        return jsonify({"data" : result})


@orders_api_blueprint.route("/new", methods=["POST"])
@jwt_required()
def new_order():
    current_user = User.get_by_id(get_jwt_identity())

    if current_user:
        total_amount = request.form.get("total_amount")

        order = Order(total_amount = total_amount, user_id = current_user.id)

        if order.save():
            return jsonify({"message" : "Order created successfully!", "order_id" : order.id })  


@orders_api_blueprint.route("/new/order_ingredients", methods=["POST"])
@jwt_required()
def new_order_ingredients():
    current_user = User.get_by_id(get_jwt_identity())

    if current_user:
        quantity = request.form.get("quantity")
        amount = request.form.get("amount")
        name = request.form.get("name")
        order_id = request.form.get("order_id")
        order_ingredient = OrderIngredient(quantity = quantity, amount = amount, user_id = current_user.id, order_id = order_id, name = name )

        if order_ingredient.save():
            return jsonify({"message" : "Order has been added successfully!"})


@orders_api_blueprint.route("/<id>", methods=["GET"])
@jwt_required()
def show_order_ingredients(id):
    current_user = User.get_by_id(get_jwt_identity())

    if current_user:
        order_ingredient = OrderIngredient.select().where(OrderIngredient.user_id == current_user.id, OrderIngredient.order_id == id)

        result = [] 

        for o in order_ingredient:
            data = {
                "name": o.name,
                "quantity" : o.quantity,
                "amount" : o.amount
            }
            result.append(data)
        
        return jsonify({ "data" : result})
        