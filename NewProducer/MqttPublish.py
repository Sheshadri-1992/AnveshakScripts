from __future__ import print_function

import logging

import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s', )


class MqttPublish:
    broker_address = "10.24.24.2"
    tTransport = "websockets"
    tPort = 10001
    vehicle_topic = ""
    edge_topic = ""
    client_edge = None
    client_vertex = None

    def __init__(self):
        logging.debug("the constructor method is called")
        self.broker_address = "10.24.24.2"
        self.tTransport = "websockets"
        self.tPort = 10001
        self.vehicle_topic = "vechiclestats"
        self.edge_topic = "trafficstats"

    def print_variables(self):
        """
        utility message to print the values which are set during the constructor
        :return: Nothing
        """

        logging.debug(
            "The broker address " + str(
                self.broker_address) + "  transport " + self.tTransport + "  the port is  " + str(
                self.tPort))

    def on_publish_edge(self):
        """
        Asynchronous callback for edge client
        :return:
        """
        logging.debug("Edge data published")

    def on_publish_vertex(self):
        """
        Asynchronous callback for vertex client
        :return:
        """
        logging.debug("Vertex data published")

    def connect_to_broker(self):
        """
        Connect to the mqtt broker
        :return:
        """

        self.client_edge = mqtt.Client("P2", transport=self.tTransport)
        self.client_edge.username_pw_set(username="dreamlabanveshak", password="dream119")
        self.client_edge.on_publish = self.on_publish_edge
        self.client_edge.connect(self.broker_address, port=self.tPort, keepalive=60, bind_address="")

        # self.client_edge.loop_forever()

        self.client_vertex = mqtt.Client("P3", transport=self.tTransport)
        self.client_vertex.username_pw_set(username="dreamlabanveshak", password="dream119")
        self.client_vertex.on_publish = self.on_publish_vertex
        self.client_vertex.connect(self.broker_address, port=self.tPort, keepalive=60, bind_address="")
        # self.client_vertex.loop_start()

    def disconnect_broker(self):
        """
        disconnect the broker
        :return:
        """
        self.client_edge.disconnect()
        self.client_vertex.disconnect()

    def send_vertex_message(self, vertex_json):
        """
        the client publishes the message to the broker , the message is vehicle speed and position
        :param vertex_json: the json that has to be sent
        :return: nothing to return
        """
        logging.debug("Sending vehicle position and speed")
        ret = self.client_vertex.publish(self.vehicle_topic, vertex_json, qos=0)
        ret.wait_for_publish()
        logging.debug("The ret is " + str(ret))

    def send_edge_message(self, edge_json):
        """

        :param edge_json: the edge json which contains the edgeid and number of vehicles
        :return: nothing to return
        """

        logging.debug("Sending edge id and position " + edge_json + " topic is " + self.edge_topic)
        ret = self.client_edge.publish(self.edge_topic, edge_json, qos=0)
        ret.wait_for_publish()
        logging.debug("The ret is " + str(ret))
