from flask import Flask
import os
from flask_restful import Api
from flask_migrate import Migrate
from models import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///money_transfer.db'
app.config['BUNDLE_ERRORS'] = True
app.config['SQLALCHEMY_ECHO'] = True

api = Api(app)
migrations = Migrate(app, db)
db.init_app(app)

@app.route('/')
def home():
    return "Hello, world!"

if __name__ == '__main__':
    app.run(debug=True, port=5000)