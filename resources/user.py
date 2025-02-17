from flask import Blueprint
from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import Users, Account, db
from datetime import datetime

# Define Blueprint
user_blueprint = Blueprint('user', __name__)
api = Api(user_blueprint)

# Request Parsers
user_parser = reqparse.RequestParser()
user_parser.add_argument('first_name', required=True, help='First name is required')
user_parser.add_argument('last_name', required=True, help='Last name is required')
user_parser.add_argument('email', required=True, help='Email is required')
user_parser.add_argument('password', required=True, help='Password is required')
user_parser.add_argument('phone', required=True, help='Phone number is required')

login_parser = reqparse.RequestParser()
login_parser.add_argument('email', required=True, help='Email is required')
login_parser.add_argument('password', required=True, help='Password is required')

# Custom serialization function for datetime
def format_datetime(value):
    return value.strftime('%Y-%m-%d %H:%M:%S') if value else None

class UserResource(Resource):
    def post(self):
        data = user_parser.parse_args()
        data['password'] = generate_password_hash(data['password'])

        # Check if user already exists based on email or phone number
        if Users.query.filter_by(email=data['email']).first():
            return {"message": "Email already taken", "status": "fail"}, 400

        if Users.query.filter_by(phone=data['phone']).first():
            return {"message": "Phone number already exists", "status": "fail"}, 400

        try:
            # Create new user
            user = Users(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone=data['phone'],
                password=data['password'],
                created_at=datetime.utcnow()  # Store as a datetime object
            )
            db.session.add(user)
            db.session.flush()  # Temporarily commit to get user id

            # Create new account with initial balance of 10,000
            account = Account(user_id=user.id, balance=10000)
            db.session.add(account)
            db.session.commit()

            # Generate tokens
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))

            return {
                "message": "Account created successfully",
                "status": "success",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "phone": user.phone,
                    "created_at": format_datetime(user.created_at)
                }
            }, 201
        except Exception as e:
            db.session.rollback()
            return {"message": "Unable to create account", "status": "fail", "error": str(e)}, 400

    @jwt_required()
    def get(self, id=None):
        if id:
            user = Users.query.get(id)
            if user:
                return {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "phone": user.phone,
                    "created_at": format_datetime(user.created_at)
                }, 200
            return {"message": "User not found", "status": "fail"}, 404
        return self.get_all_users()

    @jwt_required()
    def get_all_users(self):
        users = Users.query.all()
        return {
            "message": "Users retrieved",
            "status": "success",
            "users": [
                {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "phone": user.phone,
                    "created_at": format_datetime(user.created_at)
                }
                for user in users
            ]
        }, 200

class LoginResource(Resource):
    def post(self):
        data = login_parser.parse_args()
        user = Users.query.filter_by(email=data['email']).first()

        if user and check_password_hash(user.password, data['password']):
            # Generate tokens
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))

            return {
                "message": "Login successful",
                "status": "success",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "phone": user.phone,
                    "created_at": format_datetime(user.created_at)
                }
            }, 200
        return {"message": "Invalid email/password", "status": "fail"}, 400
