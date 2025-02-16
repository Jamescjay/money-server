from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Transaction, Account, Users


class TransactionResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('receiver_phone', type=str, required=True, help='Receiver phone number is required')
    parser.add_argument('amount', type=float, required=True, help='Amount is required')

    @jwt_required()
    def post(self):
        data = TransactionResource.parser.parse_args()
        sender_id = get_jwt_identity()
        receiver_phone = data['receiver_phone']
        amount = data['amount']

        if not receiver_phone:
            return {"message": "Receiver phone number is required.", "status": "fail"}, 400

        receiver = Users.query.filter_by(phone=receiver_phone).first()
        if not receiver:
            return {"message": "Receiver not found.", "status": "fail"}, 404

        if sender_id == receiver.id:
            return {"message": "You cannot send money to yourself.", "status": "fail"}, 400

        sender_account = Account.query.filter_by(user_id=sender_id).first()
        receiver_account = Account.query.filter_by(user_id=receiver.id).first()

        if not sender_account or not receiver_account:
            return {"message": "Invalid sender or receiver account.", "status": "fail"}, 400

        if sender_account.balance < amount:
            return {"message": "Insufficient funds.", "status": "fail"}, 400

        try:
            sender_account.balance -= amount
            receiver_account.balance += amount

            transaction = Transaction(sender_id=sender_id, receiver_id=receiver.id, amount=amount)
            db.session.add(transaction)
            db.session.commit()

            return {"message": "Transaction successful.", "status": "success"}, 201
        except Exception as e:
            db.session.rollback()
            return {"message": "Transaction failed.", "status": "fail", "error": str(e)}, 500

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        transactions = Transaction.query.filter((Transaction.sender_id == user_id) | (Transaction.receiver_id == user_id)).all()
        
        return {
            "message": "Transactions retrieved successfully.",
            "status": "success",
            "transactions": [
                {
                    "id": t.id,
                    "sender_id": t.sender_id,
                    "receiver_id": t.receiver_id,
                    "amount": t.amount,
                    "created_at": t.created_at.isoformat()
                }
                for t in transactions
            ]
        }, 200
