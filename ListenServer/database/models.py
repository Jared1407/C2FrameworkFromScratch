from database.db import db

# Define models:

# Task model
class Task(db.DynamicDocument):
    task_id = db.StringField(required=True, unique=True)

class Result(db.DynamicDocument):
    result_id = db.StringField(required=True)

class TaskHistory(db.DynamicDocument):
    task_object = db.StringField()