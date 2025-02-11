from flask import Flask
import os
from flask_restful import Api
from flask_migrate import Migrate
from flask_cors import CORS  # Enable CORS
from models import db
from flask_jwt_extended import JWTManager
from resources.user import UserResource, LoginResource
from resources.user import user_blueprint

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///money_transfer.db'
app.config['BUNDLE_ERRORS'] = True
app.config['SQLALCHEMY_ECHO'] = True
app.config['JWT_SECRET_KEY'] = 'your_secret_key'

# Enable CORS (for frontend communication)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Initialize extensions
api = Api(app)
migrations = Migrate(app, db)
db.init_app(app)
jwt = JWTManager(app)

# Register API Resources
api.add_resource(UserResource, '/users', '/users/<int:id>')
api.add_resource(LoginResource, '/login')

# Register Blueprint AFTER initializing extensions
app.register_blueprint(user_blueprint)

if __name__ == '__main__':
    app.run(debug=True, port=5000)