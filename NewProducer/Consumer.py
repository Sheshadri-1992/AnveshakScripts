from __future__ import print_function

import json
import logging
import threading
import time
from datetime import datetime
from random import randint
from MqttPublish import MqttPublish
from Producer import LargeProducer, MediumProducer, SmallProducer
from Query import QueryStruct

from Sumo import Sumo

MAX_BATCH = 4000

# logging template
logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s', )


class ConsumerThread(threading.Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(ConsumerThread, self).__init__()
        self.target = target
        self.name = name
        self.edge_list = []
        self.sumo_obj = None

        self.large_thread = LargeProducer(name='large-producer')
        self.medium_thread = MediumProducer(name="medium-producer")
        # self.small_thread = SmallProducer(name="small-producer")
        self.large_topic = "large"
        self.medium_topic = "medium"
        self.small_topic = "small"
        self.vehicle_topic = "ambulance"

        logging.debug("Started all the producers...")

    def start_producers(self):
        """
        start producing items from all queues
        :return:
        """
        logging.debug("Started producing...")
        self.large_thread.start()
        self.medium_thread.start()
        # self.small_thread.start()

    def update_sumo_object(self, sumo_obj):
        """
        Assign the sumo object so that it can retrieve traffic density
        :return: nothing
        """
        logging.debug("updated sumo object")
        self.sumo_obj = sumo_obj

    def register_topic(self, p, q , topic, graphid):

        if(int(graphid)==0):
            self.large_topic = topic
            self.large_thread.start()
        elif(int(graphid)==1):
            self.medium_topic = topic
            self.medium_thread.start()
        elif(int(graphid)==2):
            self.small_topic = topic
        else:
            self.vehicle_topic = topic


    def update_edge_list(self, edge_list):
        """

        :param edge_list: sent by the Process Edges
        :return: nothing
        """
        self.edge_list = edge_list

    @staticmethod
    def get_edge_color(edge_traffic_dict):

        edgeid_color_dict = {}

        for edge in edge_traffic_dict:

            num_vehicles = edge_traffic_dict[edge]

            # color bucker logic
            if num_vehicles < 5:
                edgeid_color_dict[edge] = 0
            elif 5 < num_vehicles <= 10:
                edgeid_color_dict[edge] = 1
            else:
                edgeid_color_dict[edge] = 2

        return edgeid_color_dict

    def run(self):
        mqtt_object = MqttPublish()
        mqtt_object.print_variables()

        while True:

            batch_count = 0
            small_candidate_edges = []
            medium_candidate_edges = []
            large_candidate_edges = []
            curr_time = datetime.now()

            # Run simulation step here

            # while not self.small_thread.small_queue.empty():
            #
            #     item = self.small_thread.get_element_from_queue()
            #     print(type(item))
            #     if (batch_count < MAX_BATCH) and (item.timestamp >= curr_time):
            #         small_candidate_edges.append(item.get_edge_id())
            #         batch_count = batch_count + 1

            while not self.medium_thread.medium_queue.empty():

                item = self.medium_thread.get_element_from_queue()
                if batch_count < MAX_BATCH and (item.timestamp >= curr_time):
                    medium_candidate_edges.append(item.get_edge_id())
                    batch_count = batch_count + 1

            while not self.large_thread.large_queue.empty():

                item = self.large_thread.get_element_from_queue()
                if batch_count < MAX_BATCH and (item.timestamp >= curr_time):
                    large_candidate_edges.append(item.get_edge_id())
                    batch_count = batch_count + 1

            # logging.debug("The small candidate edges are " + str(len(small_candidate_edges)) + "Edges are " + str(
            #     small_candidate_edges[0]))
            logging.debug("The medium candidate edges are " + str(len(medium_candidate_edges)))
            logging.debug("The large candidate edges are" + str(len(large_candidate_edges)))

            # small_dict = self.sumo_obj.return_traffic_density(small_candidate_edges)
            medium_dict = self.sumo_obj.return_traffic_density(medium_candidate_edges)
            large_dict = self.sumo_obj.return_traffic_density(large_candidate_edges)

            # aggregate stuff needed here

            self.sumo_obj.set_ambulance_id("dummy_ambulance_id")
            vehicle_stat_dict = self.sumo_obj.get_vehicle_stats()

            # color_small = self.get_edge_color(small_dict)
            color_medium = self.get_edge_color(medium_dict)
            color_large = self.get_edge_color(large_dict)

            logging.debug("The vehicle payload is ")

            mqtt_object.connect_to_broker()
            mqtt_object.send_vertex_message(json.dumps(vehicle_stat_dict))
            # mqtt_object.send_edge_message(json.dumps(color_small))
            mqtt_object.send_edge_message(json.dumps(color_medium))
            mqtt_object.send_edge_message(json.dumps(color_large))
            mqtt_object.disconnect_broker()
