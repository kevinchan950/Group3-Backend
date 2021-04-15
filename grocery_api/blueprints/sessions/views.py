from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash



sessions_api_blueprint = Blueprint('sessions_api', __name__)

@sessions_api_blueprint.route("/signup", methods=["POST"])
def signup():
    username = request.json.get("username")
    email = request.json.get("email")
    password = request.json.get("password")
    hashed_password = generate_password_hash(password)
    user = User(username=username, email=email, password=password, hashed_password=hashed_password)
    if user.save():
        return jsonify({"success": True})
    else:
        return jsonify({
            "errors": user.errors
        })

@sessions_api_blueprint.route("/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    user = User.get_or_none(username=username)
    if user:
        if check_password_hash(user.hashed_password, password):
            token = create_access_token(identity=user.id)
            return jsonify({ "token" : token })
        else:
            return jsonify({
                "errors" : "Username or password is incorrect!"
            })
    else:
        return jsonify({
            "errors" : "Username or password is incorrect!"
        })