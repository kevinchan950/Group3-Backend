from types import MethodDescriptorType
from flask import Blueprint, jsonify, request
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity
import boto3
import os


users_api_blueprint = Blueprint('users_api', __name__)


s3 = boto3.client(
    "s3",
    aws_access_key_id = os.getenv('AWS_KEY_ID'),
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
)

@users_api_blueprint.route("/<user_id>", methods=["GET"])
def show(user_id):
    pass


@users_api_blueprint.route("/me", methods=["GET"])
@jwt_required()
def show_myprofile():
    current_user = User.get_by_id(get_jwt_identity())
    return jsonify({
        "id" : current_user.id,
        "username" : current_user.username,
        "email" : current_user.email,
        "profile_picture" : current_user.profile_picture,
        "phone_number" : current_user.phone_number,
        "is_admin" : current_user.is_admin
    })


@users_api_blueprint.route("/uploadImage", methods=['POST'])
@jwt_required()
def create_profile_picture():
    current_user = User.get_by_id(get_jwt_identity())
    file = request.files.get('image')
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

    update = User.update(profile_picture=f'https://kevinchan950-nextagram-flask.s3-ap-southeast-1.amazonaws.com/{file.filename}').where(User.id==current_user.id)
    if update.execute():
        return jsonify({
            "successful" : True,
            "message" : "Profile picture has been successfully uploaded!"
        })
    else:
        return jsonify({
            "Errors" : "errors"
        })