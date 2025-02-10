from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import Users, db

class User(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('first_name', required=True, help='first_name is required')
    parser.add_argument('last_name', required=True, help='last_name is required')
    parser.add_argument('email', required=True, help='email is required')
    parser.add_argument('password', required=True, help='password is required')
    parser.add_argument('phone', required=True, help='phone is required')

    def post(self):
        data = User.parser.parse_args()
        data['password'] = generate_password_hash(data['password'])

        if Users.query.filter_by(email=data['email']).first():
            return {"message": "Email already taken", "status": "fail"}, 400

        if Users.query.filter_by(phone=data['phone']).first():
            return {"message": "Phone number already exists", "status": "fail"}, 400

        try:
            user = Users(**data)
            db.session.add(user)
            db.session.commit()

            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            return {
                "message": "Account created successfully.",
                "status": "success",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user_schema(user)  # Use helper function
            }, 201
        except Exception as e:
            return {"message": "Unable to create account", "status": "fail", "error": str(e)}, 400

    @jwt_required()
    def get(self, id=None):
        if id:
            user = Users.query.get(id)
            if user:
                return {
                    "message": "User found",
                    "status": "success",
                    "user": user_schema(user)
                }, 200
            return {"message": "User not found", "status": "fail"}, 404
        return self.get_all_users()

    @jwt_required()
    def get_all_users(self):
        users = Users.query.all()
        return {
            "message": "Users retrieved",
            "status": "success",
            "users": [user_schema(user) for user in users]
        }, 200


class Login(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email', required=True, help='email is required')
    parser.add_argument('password', required=True, help='password is required')

    def post(self):
        data = Login.parser.parse_args()
        user = Users.query.filter_by(email=data['email']).first()

        if user and check_password_hash(user.password, data['password']):
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            return {
                "message": "Login successful",
                "status": "success",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user_schema(user)
            }, 200
        return {"message": "Invalid email/password", "status": "fail"}, 400

def user_schema(user):
    """Helper function to convert SQLAlchemy object to JSON-serializable dictionary"""
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "phone": user.phone,
        "password": user.password,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }
