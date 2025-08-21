from flask_mongoengine import MongoEngine

# Init MongoEnginbge and DB
db = MongoEngine()

def initialize_db(app):
    db.init_app(app)