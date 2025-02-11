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
            
            return {"balance": 0.0, "user": {"first_name": "", "last_name": ""}}, 200
        
        if account.balance is None:
            account.balance = 0.0
            db.session.commit()  
        
        return account