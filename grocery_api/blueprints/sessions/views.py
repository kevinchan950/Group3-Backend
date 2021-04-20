from flask import Blueprint, jsonify, request, url_for
from flask.helpers import url_for
from flask_jwt_extended import create_access_token
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.requests_client import OAuth2Session
import os


sessions_api_blueprint = Blueprint('sessions_api', __name__)

@sessions_api_blueprint.route("/signup", methods=["POST"])
def signup():
    username = request.json.get("username")
    email = request.json.get("email")
    password = request.json.get("password")
    hashed_password = generate_password_hash(password)
    user = User(username=username, email=email, password=password, hashed_password=hashed_password)
    if user.save():
        token = create_access_token(identity=user.id)
        return jsonify({"success": True, "token" : token})
    else:
        return jsonify({
            "errors": user.errors
        })


@sessions_api_blueprint.route("/signup/checkemail=<email>", methods=["GET"])
def check_email(email):

    check_email = User.get_or_none(email = email)
    
    if check_email:
        return jsonify({
            "exist" : True
        })
    else: 
        return jsonify({
            "exist" : False 
        })


@sessions_api_blueprint.route("/signup/checkusername=<username>", methods=["GET"])
def check_username(username):

    check_username = User.get_or_none(username = username)

    if check_username: 
        return jsonify({
            "exist" : True
        })
    else: 
        return jsonify({
            "exist" : False 
        })


@sessions_api_blueprint.route("/admin/signup", methods=["POST"])
def admin_signup():
    username = request.json.get("username")
    email = request.json.get("email")
    password = request.json.get("password")
    hashed_password = generate_password_hash(password)
    admin = User(username=username, email=email, password=password, hashed_password=hashed_password, is_admin=True)
    if admin.save():
        token = create_access_token(identity=admin.id)
        return jsonify({"success": True, "token": token})
    else:
        return jsonify({
            "errors" : admin.errors
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



@sessions_api_blueprint.route("/authorize/google", methods=["POST"])
def authorize():
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    token = request.json.get("token")
    client = OAuth2Session(client_id, client_secret, token=token)
    account_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
    client = OAuth2Session(client_id, client_secret, token=token)
    resp = client.get(account_url)
    username = resp.json()['name']
    email = resp.json()['email']
    user = User.get_or_none(User.email == email)
    
    if user:
        token = create_access_token(identity=user.id)
        return jsonify({ "token" : token })
    else:
        password = os.urandom(8)
        hashed_password = generate_password_hash(password)
        create_user = User(username=username, email = email, hashed_password=hashed_password)
        create_user.save()
        token = create_access_token(identity=create_user.id)
        return jsonify({ "token" : token })