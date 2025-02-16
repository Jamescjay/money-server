from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload
from models import db, Account, Users

class UserAccount(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        account = Account.query.options(joinedload(Account.user)).filter_by(user_id=user_id).first()

        if not account:
            return {"message": "Account not found", "status": "fail"}, 404
        
        # Debug print
        print("Account:", account)
        print("Account User:", account.user if account else "No account found")

        account_data = {
            "balance": account.balance,
            "user": {
                "first_name": account.user.first_name if account.user else None,
                "last_name": account.user.last_name if account.user else None
            },
            "id": account.id 
        }
        return {"message": "Account details retrieved", "status": "success", "account": account_data}, 200