import zmq
import threading
import Queue


class MqttPubSub(threading.Thread):

    def __init__(self):
        self.current_edge_list = []
        self.my_queue = Queue.Queue()
        self.context = zmq.Context()
        self.ip = "tcp://10.244.17.8:9000"

    def run(self):

        try:
            receiver = self.context.socket(zmq.PULL)
            receiver.connect(self.ip)

            # Process any waiting tasks
            while True:
                try:
                    msg = receiver.recv()
                    print("The message is ", msg)
                    self.my_queue.put(msg)  # this message is a json
                except zmq.Again:
                    print("Caught Exception")
                    continue

        except Exception as e:

            print("The exception is caught in MqttPubSub", e)

    def get_object_from_queue(self):
        """
        Check if the queue is not empty and return the item
        :return:  the item is the json
        """

        if self.my_queue.empty() is False:
            return self.my_queue.get()

# my_obj = MqttPubSub()
# my_obj.get_object_from_queue()
# print("here")
