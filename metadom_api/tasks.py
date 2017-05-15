#!flask/bin/python
from flask import Flask, jsonify, abort, make_response
import metadom_api.application

from flask import current_app as flask_app

_tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]

@flask_app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': _tasks})


@flask_app.route('/metadom/api/v1.0/chr/<int:chr>/<int:position>', methods=['GET'])
def get_chr_pos(chr,position):
    task = [task for task in _tasks if task['id'] == position]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})

@flask_app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    
    flask_app.run(debug=True)
    