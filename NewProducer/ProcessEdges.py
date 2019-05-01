from __future__ import print_function

import json
import logging
import time
from random import randint
import Queue
from Consumer import ConsumerThread
import numpy as np
from Sumo import Sumo

# Global variables & constants
vehicle_queue = Queue.Queue()
my_dict = {}

# logging template
logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s', )


class ProducerConsumer:

    def __init__(self):
        logging.debug("Producer Consumer object has been initiated")
        self.sumo_obj = Sumo()
        self.consumer_thread = ConsumerThread(name='consumer')
        self.consumer_thread.update_sumo_object(self.sumo_obj)

    def start_simulation(self):
        """
        Starts the sumo simulation which increments simulation step every second
        :return:
        """
        # start simulation
        self.sumo_obj.start()
        self.start_producing_content()
        # self.start_publishing_data()

    def start_producing_content(self):
        """

        :return:
        """
        self.consumer_thread.start_producers()
        self.consumer_thread.start()

    def get_ambulance_path(self):
        """
        returns a dictionary with key value pairs where key is edgeID, value is vehicles

        Here we need to increment a simulation step only once,
        :return: dictionary containing the (key,value) => key is edgeID, value is num vehicles
        """
        print("The set of edge ids in the ambulance path ")

        edge_dict = {}

        # for i in range(0, len(edge_list)):
        #     edge = edge_list[i]
        #     edge_dict[edge] = randint(0, 2)

        payload = json.dumps(edge_dict)
        return payload

    def start_publishing_data(self):
        """
        starts all the threads which publish data at regular intervals to mqtt broker
        :return: Nothing
        """

        self.consumer_thread.start()

    def load_json(self):
        """
        load all the edgeid from the json file
        :return: nothing
        """

        logging.debug("Loading the low_ways json ")
        with open("./input/low_ways.json") as json_file:
            data_dict = json.load(json_file)

        low_edge_list = list(data_dict.keys())
        logging.debug("The number of edges are " + str(len(low_edge_list)))

        logging.debug("Loading the mid_ways json ")
        with open("./input/mid_ways.json") as json_file:
            data_dict = json.load(json_file)

        mid_edge_list = list(data_dict.keys())
        logging.debug("The number of edges are " + str(len(mid_edge_list)))

        logging.debug("Loading the high_ways json ")
        with open("./input/high_ways.json") as json_file:
            data_dict = json.load(json_file)

        high_edge_list = list(data_dict.keys())
        logging.debug("The number of edges are " + str(len(high_edge_list)))
