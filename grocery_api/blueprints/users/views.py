from types import MethodDescriptorType
from flask import Blueprint, jsonify, request
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash


users_api_blueprint = Blueprint('users_api', __name__)

@users_api_blueprint.route("/<user_id>", methods=["GET"])
def show(user_id):
    pass