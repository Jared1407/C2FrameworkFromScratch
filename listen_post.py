import json
import resources

from flask import Flask
from flask_restful import Api
from database.db import initialize_db

# Init flask app
app = Flask(__name__)

# Mango Config: Localhost
app.config['MONGO_URI'] = 'mongodb://localhost:27017/c2framework2'

# init db
initialize_db(app)

# Init API
api = Api(app)

# Define routes for resources:
# Currently only /tasks 
api.add_resource(resources.Tasks, '/tasks', endpoint='tasks')
api.add_resource(resources.Results, '/results')

# Start app in debug
if __name__ == '__main__':
    app.run(debug=True)