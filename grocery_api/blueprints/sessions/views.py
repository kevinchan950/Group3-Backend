from flask import Blueprint, jsonify, request, url_for
from flask.helpers import url_for
from flask_jwt_extended import create_access_token
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from grocery_api.utils.google_oauth import oauth


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


@sessions_api_blueprint.route("/signup/checkemail", methods=["GET"])
def check_email():
    check_email = request.json.get("email")
    email = User.get_or_none(email = check_email)
    
    if email:
        return jsonify({
            "exist" : True
        })
    else: 
        return jsonify({
            "exist" : False 
        })


@sessions_api_blueprint.route("/signup/checkusername", methods=["GET"])
def check_username():
    check_username = request.json.get("username")
    username = User.get_or_none(username = check_username)

    if username: 
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


@sessions_api_blueprint.route("/google_login")
def google_login():
    redirect_url = url_for('sessions_api.authorize', _external = True)
    return oauth.google.authorize_redirect(redirect_url)


@sessions_api_blueprint.route("/authorize/google")
def authorize():
    oauth.google.authorize_access_token()
    name = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo').json()['name']
    email = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo').json()['email']
    user = User.get_or_none(User.email == email)
    if user:
        token = create_access_token(identity=user.id)
        return jsonify({ "token" : token })
    else:
        password = os.urandom(8)
        hashed_password = generate_password_hash(password)
        create_user = User(name=name, email = email, hashed_password=hashed_password)
        create_user.save()
        token = create_access_token(identity=create_user.id)
        return jsonify({ "token" : token })
