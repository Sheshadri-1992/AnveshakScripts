from __future__ import print_function

import logging
import json
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
    client_path_topic = None
    client_path_traffic_topic = None
    client_traffic_color_topic = None
    client_cam_feed = None
    client_cam_blend = None

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

    def on_publish_traffic_color_topic(self):
        """

        :return:
        """
        logging.debug("Traffic color topic got published")

    def on_publish_path_traffic_topic(self):
        """

        :return:
        """
        logging.debug("Path traffic topic got published")

    def on_publish_path_topic(self):
        """

        :return:
        """
        logging.debug("Path topic got published")


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

    def on_publish_cam_feed(self):
        """

        :return:
        """
        logging.debug("On publish cam feed")

    def on_publish_cam_blend(self):
        """

        :return:
        """
        logging.debug("On publish cam blend")

    def custom_connect_to_broker(self):
        """

        :return:
        """
        self.client_cam_feed = mqtt.Client("P52", transport=self.tTransport)
        self.client_cam_feed.username_pw_set(username="dreamlabanveshak", password="dream119")
        self.client_cam_feed.on_publish = self.on_publish_cam_feed
        self.client_cam_feed.connect(self.broker_address, port=self.tPort, keepalive=60, bind_address="")

        self.client_cam_blend = mqtt.Client("P53", transport=self.tTransport)
        self.client_cam_blend.username_pw_set(username="dreamlabanveshak", password="dream119")
        self.client_cam_blend.on_publish = self.on_publish_cam_blend
        self.client_cam_blend.connect(self.broker_address, port=self.tPort, keepalive=60, bind_address="")

    def connect_to_broker(self):
        """
        Connect to the mqtt broker
        :return:
        """

        self.client_edge = mqtt.Client("P2", transport=self.tTransport)
        self.client_edge.username_pw_set(username="dreamlabanveshak", password="dream119")
        self.client_edge.on_publish = self.on_publish_edge
        self.client_edge.connect(self.broker_address, port=self.tPort, keepalive=60, bind_address="")

        self.client_vertex = mqtt.Client("P3", transport=self.tTransport)
        self.client_vertex.username_pw_set(username="dreamlabanveshak", password="dream119")
        self.client_vertex.on_publish = self.on_publish_vertex
        self.client_vertex.connect(self.broker_address, port=self.tPort, keepalive=60, bind_address="")

        self.client_path_topic = mqtt.Client("P13", transport=self.tTransport)
        self.client_path_topic.username_pw_set(username="dreamlabanveshak", password="dream119")
        self.client_path_topic.on_publish = self.on_publish_path_topic
        self.client_path_topic.connect(self.broker_address, port=self.tPort, keepalive=60, bind_address="")

        self.client_path_traffic_topic = mqtt.Client("P14", transport=self.tTransport)
        self.client_path_traffic_topic.username_pw_set(username="dreamlabanveshak", password="dream119")
        self.client_path_traffic_topic.on_publish = self.on_publish_path_traffic_topic
        self.client_path_traffic_topic.connect(self.broker_address, port=self.tPort, keepalive=60, bind_address="")

        self.client_traffic_color_topic = mqtt.Client("P21", transport=self.tTransport)
        self.client_traffic_color_topic.username_pw_set(username="dreamlabanveshak", password="dream119")
        self.client_traffic_color_topic.on_publish = self.on_publish_path_traffic_topic
        self.client_traffic_color_topic.connect(self.broker_address, port=self.tPort, keepalive=60, bind_address="")

    def disconnect_broker(self):
        """
        disconnect the broker
        :return:
        """
        self.client_edge.disconnect()
        self.client_vertex.disconnect()
        self.client_path_topic.disconnect()
        self.client_path_traffic_topic.disconnect()
        self.client_traffic_color_topic.disconnect()

    def custom_disconnect_broker(self):
        """

        :return:
        """
        self.client_cam_feed.disconnect()
        self.client_cam_blend.disconnect()

    def send_vertex_message(self, vertex_json, topic):
        """
        the client publishes the message to the broker , the message is vehicle speed and position
        :param vertex_json: the json that has to be sent
        :param topic: the topic for vertex which is sent by consumer
        :return: nothing to return
        """
        logging.debug("Sending vehicle position and speed")
        ret = self.client_vertex.publish(topic, vertex_json, qos=0)
        ret.wait_for_publish()
        logging.debug("The ret is " + str(ret))

    def send_edge_message(self, edge_json, topic):
        """

        :param edge_json: the edge json which contains the edgeid and number of vehicles
        :param topic: the topic for edge which is sent by consumer
        :return: nothing to return
        """

        my_dict = json.loads(edge_json)
        logging.debug("Sending edge id " + str(len(edge_json)) + " topic is " + str(topic))
        ret = self.client_edge.publish(topic, edge_json, qos=0)
        ret.wait_for_publish()
        logging.debug("The keys sent are " + str(my_dict.keys()))
        logging.debug("The ret is " + str(ret))

    def send_path_topic_message(self, path_json, topic):
        """

        :param path_json: edgeid and lat long
        :param topic: path_topic
        :return: nothing
        """
        logging.debug("Sending path topic json")
        ret = self.client_path_topic.publish(topic, path_json, qos=0)
        ret.wait_for_publish()
        logging.debug("The ret is "+str(ret))

    def send_path_traffic_topic_message(self, path_traffic_json, topic):
        """

        :param path_traffic_json:  edge id and color
        :param topic: path_traffic topic
        :return: nothing
        """
        logging.debug("Sending path traffic topic json ")
        logging.debug("The path traffic ")
        ret = self.client_path_traffic_topic.publish(topic, path_traffic_json, qos=0)
        ret.wait_for_publish()
        logging.debug("The ret is "+str(ret))

    def send_traffic_color_topic_message(self, traffic_color_json, topic):
        """

        :param traffic_color_json:  contains traffic id and color
        :param topic: traffic color topic
        :return: nothing
        """
        print("Sending traffic color topic json ",traffic_color_json)
        ret = self.client_traffic_color_topic.publish(topic, traffic_color_json, qos=0)
        ret.wait_for_publish()
        logging.debug("The ret is " + str(ret))

    def send_camera_feed_topic_message(self, cam_feed_json, topic):
        """

        :param cam_feed_json:
        :param topic:
        :return:
        """
        print("Sending cam feed topic json ", cam_feed_json, "topic is ",topic)
        ret = self.client_cam_feed.publish(topic, cam_feed_json, qos=0)
        ret.wait_for_publish()
        logging.debug("The ret is "+str(ret))

    def send_camera_blend_topic_message(self, cam_blend_json, topic):
        """

        :param cam_blend_json:
        :param topic:
        :return:
        """
        print("Sending cam blend topic json ", cam_blend_json," topic is ", topic)
        ret = self.client_cam_blend.publish(topic, cam_blend_json)
        ret.wait_for_publish()
        logging.debug("The ret is "+str(ret))
