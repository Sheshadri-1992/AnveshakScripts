import messageSchema_pb2
import time
import traceback
import zmq
import pickle


def __make_message(module_id, key, value, query_id, data=None):
    """
    This method is run only on the source and is used to make messages of messageSchema format. It also
    assigns the startTimeStamp which will be used for all future drops and batching.

    :param module_id: Module id of the source. eg: Filter_1
    :param key: key sent in the kafka message
    :param value: Generally the image to be sent
    :param query_id: Unique id of the query specified in the JSON
    :return:
    """
    message = messageSchema_pb2.msg()
    try:
        message.startTimeStamp = int(time.time()*1000)  # timestamp in milliseconds
        message.bitMask = query_id
        message.boundOverride = False
        message.type = messageSchema_pb2.msg.START
        message.id = module_id
        message.sender = ''
        message.receiver = module_id
        message.key = key
        message.value = value
        if data is not None:
            message.upper_limit_bs = data['upper_limit_bs']
            message.max_tol_lat = data['max_tol_lat']
        return message
    except Exception:
        print(traceback.format_exc())


def __send_message(msg, ip):
    """
    This method accepts a protobuf object, serializes it sends it over to the sender specified in the message using
    the _instance_to_endpoint_map.

    :param msg: Protobuf message
    :return: Nothing
    """
    try:
        buffer = msg.SerializeToString()
        zmq_context = zmq.Context()
        zmq_socket = zmq_context.socket(zmq.PUSH)
        zmq_socket.connect(ip)
        zmq_socket.send(buffer)
    except Exception:
        print(traceback.format_exc())


def start_anveshak(session_id, max_tol_lat, upper_limit_bs, source, destination, ip):
    """
    This method should be called from the Python server that runs Anveshak

    :param session_id: Session ID from the UI
    :param max_tol_lat: Maximum Latency from the UI
    :param upper_limit_bs: Maximum Batch Size from the UI
    :param source: Source from the UI
    :param destination: Destination from the UI
    :param ip: IP address of the DU module (must be a part of the Python Server module)
    :return:
    """
    data = {'max_tol_lat': max_tol_lat, 'upper_limit_bs': upper_limit_bs, 'new_query_id': session_id,
            'source': source, 'destination': destination, 'last_seen_ts': int(time.time() * 1000), 'request': 'start'}
    msg = __make_message('DU_0', 'start', pickle.dumps(data), session_id, data=data)
    __send_message(msg, ip)


def vehicle_enters_fov(session_id, camera_id):
    camera_id = 'C_' + str(camera_id)
    ip = 'tcp://'+cam_id_to_filter_map[camera_id]
    msg = __make_message(camera_id, camera_id, pickle.dumps(True), session_id)
    __send_message(msg, ip)


"""
***deprecated***

def vehicle_exits_fov(session_id, camera_id):
    ip = ''
    camera_id = 'C_' + str(camera_id)
    msg = __make_message(camera_id, camera_id, pickle.dumps(False), session_id)
    __send_message(msg, ip)
"""

f = open('./InputFiles/cam_id_to_filter.pkl', 'rb')
cam_id_to_filter_map = pickle.load(f)
