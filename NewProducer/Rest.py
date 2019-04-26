import json

from flask import Flask, current_app, Blueprint
from flask_cors import CORS

app = Blueprint('scale_app', 'scale_api', url_prefix='/')


def create_rest_app(state_obj):

    print("Starting the REST server...")

    rest_app = Flask('scale_api')
    rest_app.config['state'] = state_obj
    CORS(rest_app)
    rest_app.register_blueprint(app)
    return rest_app


@app.route('test', methods=['GET'])
def test():
    """
    Test
    """
    my_state = current_app.config['state']

    # my_state.load_json()

    return json.dumps({'message': 'Success'})


@app.route('start', methods=['GET'])
def start():
    """

    :return: jsonArray containing (key,value) pair, where key is edgeid, value is num vehicles
    """
    my_state = current_app.config['state']

    # get the ambulance path (which is a set of edges )
    edge_list = my_state.get_ambulance_path()

    my_state.start_publishing_data()
    return json.dumps({'ambulancepath': edge_list})