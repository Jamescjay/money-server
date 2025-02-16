from flask import request
from flask_restful import Resource, reqparse, fields, marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Transaction, Users

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
        
        response = []
        for transaction in transactions:
            sender = Users.query.get(transaction.sender_id)
            receiver = Users.query.get(transaction.receiver_id)
            response.append({
                'id': transaction.id,
                'sender_name': f"{sender.first_name} {sender.last_name}" if sender else None,
                'receiver_name': f"{receiver.first_name} {receiver.last_name}" if receiver else None,
                'amount': transaction.amount,
                'status': transaction.status,
                'transaction_type': transaction.transaction_type,
                'created_at': transaction.created_at
            })
        return response, 200

    @jwt_required()
    def post(self):
        """Create a new transaction."""
        args = transaction_parser.parse_args()
        sender_id = get_jwt_identity()
        receiver_phone = args['receiver_phone']
        amount = args['amount']
        transaction_type = args['transaction_type']
        
        # Get receiver's ID using phone number
        receiver = Users.query.filter_by(phone=receiver_phone).first()
        if not receiver:
            return {'message': 'Receiver not found'}, 404
        
        new_transaction = Transaction(
            sender_id=sender_id,
            receiver_id=receiver.id,
            amount=amount,
            transaction_type=transaction_type,
            status='pending'
        )
        
        db.session.add(new_transaction)
        db.session.commit()
        
        return {'message': 'Transaction created successfully'}, 201
