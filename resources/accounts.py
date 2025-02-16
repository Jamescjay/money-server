
from flask_restful import Resource, fields, marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Account

class UserAccount(Resource):
    account_fields = {
        "balance": fields.Float(default=0.0),
        "user": fields.Nested({
            "first_name": fields.String,
            "last_name": fields.String
        })
    }

    @jwt_required()
    @marshal_with(account_fields)
    def get(self):
        user_id = get_jwt_identity()
        account = Account.query.filter_by(user_id=user_id).first()

        if not account:
            
         return {"message": "Account not found", "status": "fail"}, 404
        
        account_data = {
    "balance": account.balance,
    "first_name": account.user.first_name,  
    "last_name": account.user.last_name
}
        return {"message": "Account details retrieved", "status": "success", "account": account_data}, 200
