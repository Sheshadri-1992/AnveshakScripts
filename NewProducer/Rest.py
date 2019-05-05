import json
import logging

from flask import Flask, current_app, Blueprint
from flask_cors import CORS
from flask import request

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s', )

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


@app.route('start_sumo', methods=['GET'])
def start_sumo():
    """
    This method will trigger the sumo simulation
    :return: nothing
    """
    logging.debug("In the start simulation method")
    my_state = current_app.config['state']
    my_state.start_simulation()

    return json.dumps({'message': 'Success'})


@app.route('start_global_viewport', methods=['GET'])
def start_global_viewport():
    """
    Return updates for all the edges in the viewport traffic
    :param p: The first diagonal point
    :param q: The second diagonal point
    :param graphid: 0 - low , 1 - medium , 2 - high
    :param resource_topic: specified by the user
    :return: nothing
    """
    logging.debug("In the start view port traffic method")
    lat = request.args.get('lat', default=0.0, type=float)
    lon = request.args.get('long', default=0.0, type=float)
    graphid = request.args.get('graphid', default=0, type=int)
    resource_topic = request.args.get('topic', default='medium', type=str)

    my_state = current_app.config['state']
    my_state.register_topic(lat, lon, resource_topic, graphid)

    logging.debug(
        "The parameters recevied are " + str(lat) + "  :  " + str(lon) + "  :  " + str(
            graphid) + "  :  " + resource_topic)

    return json.dumps({'message': 'Success'})


@app.route('update_view_port', methods=['GET'])
def update_view_port_traffic():
    """

    :param p: The first diagonal point
    :param q: The second diagonal point
    :param graphid: 0 - low , 1 - medium , 2 - high
    :return: nothing
    """
    logging.debug("In the update view port traffic method")

    p = request.args.get('p', default=0.0, type=float)
    q = request.args.get('q', default=0.0, type=float)
    graphid = request.args.get('graphid', default=0, type=int)

    logging.debug("The parameters received are " + str(p) + "  :  " + str(q) + "  :  " + str(graphid))
    return json.dumps({'message': 'Success'})


@app.route('start_ambulance', methods=['POST'])
def start_ambulance():
    """
    The request parameter has source and destination of the route map
    :return:
    """
    my_json =request.get_json()
    my_dict = json.loads(my_json)
    logging.debug("In the start ambulance method ")
    # src = request.args.get('src', default=0.0, type=float)
    # dest = request.args.get('dest', default=0.0, type=float)
    # batch_size = request.args.get('batchsize', default=0.0, type=float)
    # max_latency = request.args.get('maxlatency', default=0.0, type=float)
    # logging.debug("The parameters received are " + str(src) + "," + str(dest) + " , " + str(batch_size) + " , " + str(
    #     max_latency))

    logging.debug("The post request is "+str(my_dict))

    my_state = current_app.config['state']
    result = my_state.set_ambulance_co_ordinates(my_dict)  # 10 is the session id
    return json.dumps({'message': str(result)})


@app.route('reset', methods=['GET'])
def stop_sumo():
    """
    This method will stop the sumo simulation
    :return:
    """
    logging.debug("In the stop simulation method")

    my_state = current_app.config['state']
    result = my_state.stop_sumo()
    return json.dumps({'message': result})

# 308453207 3451683332
