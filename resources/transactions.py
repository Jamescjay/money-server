from flask import request
from flask_restful import Resource, reqparse, fields, marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Transaction, Users, Account

# Define response fields
transaction_fields = {
    'id': fields.Integer,
    'sender_name': fields.String,
    'receiver_name': fields.String,
    'amount': fields.Float,
    'status': fields.String,
    'transaction_type': fields.String,
    'created_at': fields.DateTime
}

# Request parser for transaction creation
transaction_parser = reqparse.RequestParser()
transaction_parser.add_argument('receiver_phone', type=str, required=True, help='Receiver phone number is required')
transaction_parser.add_argument('amount', type=float, required=True, help='Amount is required')
transaction_parser.add_argument('transaction_type', type=str, required=True, help='Transaction type is required')

class TransactionResource(Resource):
    @jwt_required()
    @marshal_with(transaction_fields)
    def get(self):
        """Retrieve transactions of the logged-in user."""
        user_id = get_jwt_identity()
        transactions = Transaction.query.filter(
            (Transaction.sender_id == user_id) | (Transaction.receiver_id == user_id)
        ).all()

        # Pre-fetch the users to avoid repeated database queries
        user_ids = {transaction.sender_id for transaction in transactions}.union(
            {transaction.receiver_id for transaction in transactions}
        )
        users = Users.query.filter(Users.id.in_(user_ids)).all()
        user_dict = {user.id: f"{user.first_name} {user.last_name}" for user in users}

        response = []
        for transaction in transactions:
            response.append({
                'id': transaction.id,
                'sender_name': user_dict.get(transaction.sender_id, None),
                'receiver_name': user_dict.get(transaction.receiver_id, None),
                'amount': transaction.amount,
                'status': transaction.status,
                'transaction_type': transaction.transaction_type,
                'created_at': transaction.created_at
            })
        return response, 200

    @jwt_required()
    def post(self):
        args = transaction_parser.parse_args()
        sender_id = get_jwt_identity()
        sender = Users.query.get(sender_id)

        if not sender:
            return {"message": "Sender not found"}, 404

        receiver = Users.query.filter_by(phone=args['receiver_phone']).first()
        if not receiver:
            return {"message": "Receiver not found"}, 404

        sender_account = Account.query.filter_by(user_id=sender_id).first()
        receiver_account = Account.query.filter_by(user_id=receiver.id).first()

        if not sender_account or not receiver_account:
            return {"message": "Accounts not found for sender or receiver"}, 404

        if sender_account.balance < args['amount']:
            return {"message": "Insufficient funds"}, 400

        try:
            # Perform the transaction
            sender_account.balance -= args['amount']
            receiver_account.balance += args['amount']

            # Create a new transaction record
            transaction = Transaction(
                sender_id=sender_id,
                receiver_id=receiver.id,
                amount=args['amount'],
                transaction_type=args['transaction_type'],
                status='completed'
            )
            db.session.add(transaction)
            db.session.commit()

            return {"message": "Transaction successful", "transaction_id": transaction.id}, 201
        except Exception as e:
            db.session.rollback()
            return {"message": "Transaction failed", "error": str(e)}, 500
