from flask import request
from flask_restful import Resource, fields, marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Account, Users

# Define response fields
account_fields = {
    'id': fields.Integer,
    'user_id': fields.Integer,
    'balance': fields.Float,
    'created_at': fields.DateTime,
    'username': fields.String,  # Remove the concatenation here
}

class AccountResource(Resource):
    @jwt_required()
    @marshal_with(account_fields)
    def get(self):
        """Retrieve account details of the logged-in user."""
        user_id = get_jwt_identity()  # Get the current user ID from the JWT token
        account = Account.query.filter_by(user_id=user_id).first()

        if not account:
            return {"message": "Account not found"}, 404
        
        # Retrieve the user's first and last name from Users table
        user = Users.query.get(user_id)
        if user:
            account.username = f"{user.first_name} {user.last_name}"
        
        return account, 200
