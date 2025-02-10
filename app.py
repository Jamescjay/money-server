from flask import Flask
import os
from flask_restful import Api
from flask_migrate import Migrate
from models import db
from flask_jwt_extended import JWTManager
from resources.user import User, Login

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///money_transfer.db'
app.config['BUNDLE_ERRORS'] = True
app.config['SQLALCHEMY_ECHO'] = True
app.config['JWT_SECRET_KEY'] = 'your_secret_key'

api = Api(app)
migrations = Migrate(app, db)
db.init_app(app)
jwt = JWTManager(app)


api.add_resource(User, '/user', '/user/<int:id>')
api.add_resource(Login, '/login')

if __name__ == '__main__':
    app.run(debug=True, port=5000)