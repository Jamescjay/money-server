from flask_restful import Resource, fields, marshal_with, reqparse
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models import db, Transaction, Account
from datetime import datetime

transaction_fields = {
    "id": fields.Integer,
    "sender_id": fields.Integer,
    "receiver_id": fields.Integer,
    "amount": fields.Float,
    "status": fields.String,  
    "transaction_type": fields.String, 
    "created_at": fields.DateTime
}

class UserTransactions(Resource):
    @jwt_required()
    @marshal_with(transaction_fields)
    def get(self):
        """Fetch transactions for the logged-in user (both sent & received)."""
        user_id = get_jwt_identity()

        transactions = Transaction.query.filter(
            (Transaction.sender_id == user_id) | (Transaction.receiver_id == user_id)
        ).order_by(Transaction.created_at.desc()).all()

        return transactions, 200
    
class SendMoney(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("receiver_phone_number", type=int, required=True, help="Receiver's number is required.")
    parser.add_argument("amount", type=float, required=True, help="Amount is required.")

    @jwt_required()
    def post(self):
        """Handle sending money from the logged-in user to another user."""
        data = SendMoney.parser.parse_args()
        sender_id = get_jwt_identity()
        receiver_id = data["receiver_id"]
        amount = data["amount"]

        if sender_id == receiver_id:
            return {"message": "You cannot send money to yourself."}, 400

        sender_account = Account.query.filter_by(user_id=sender_id).first()
        receiver_account = Account.query.filter_by(user_id=receiver_id).first()

        if not sender_account or not receiver_account:
            return {"message": "Invalid sender or receiver account."}, 404

        if sender_account.balance < amount:
            return {"message": "Insufficient balance."}, 400

        sender_account.balance -= amount
        receiver_account.balance += amount

        transaction = Transaction(
            sender_id=sender_id,
            receiver_id=receiver_id,
            amount=amount,
            status="Success",
            transaction_type="Transfer",
            created_at=datetime.utcnow(),
        )

        db.session.add(transaction)
        db.session.commit()

        return {"message": "Transaction successful!", "transaction_id": transaction.id}, 201
