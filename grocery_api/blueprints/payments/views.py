from flask import Blueprint, jsonify, request
from models.user import User
from flask_jwt_extended import get_jwt_identity, jwt_required
import braintree
import os

payments_api_blueprint = Blueprint('payments_api', __name__)

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id= os.getenv("BRAINTREE_ID"),
        public_key= os.getenv("BRAINTREE_PUBLIC_KEY"),
        private_key= os.getenv("BRAINTREE_PRIVATE_KEY")
    )
)


@payments_api_blueprint.route("/client_token", methods=["GET"])
@jwt_required()
def client_token():
    current_user = User.get_by_id(get_jwt_identity())

    if current_user:
        client_token = gateway.client_token.generate()
        return jsonify({"client_token" : client_token})

@payments_api_blueprint.route("/pay", methods=["POST"])
@jwt_required()
def pay():
    current_user = User.get_by_id(get_jwt_identity())

    if current_user:
        total = request.form.get("total")
        nonce = request.form.get("nonce")

        result = gateway.transaction.sale({
            "amount": total,
            "payment_method_nonce" : nonce,
            "options" : {
                "submit_for_settlement" : True
            }
        })
        
        if result:
            return jsonify({"successful":True, "message": "Payment successful!"})
        else:
            return jsonify({"message":"Something wrong during the transaction!"})