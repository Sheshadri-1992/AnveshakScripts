from __future__ import print_function

import json
import logging
import time
from random import randint
import Queue
from Consumer import ConsumerThread
import numpy as np
from MqttPublish import MqttPublish
from Producer import LargeProducer, MediumProducer, SmallProducer
from Query import QueryStruct
from Sumo import Sumo

# Global variables & constants
vehicle_queue = Queue.Queue()
edge_list = []
my_dict = {}


# logging template
logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s', )


class ProducerConsumer:

    def __init__(self):
        logging.debug("Producer Consumer object has been initiated")
        self.sumo_obj = Sumo()
        self.consumer_thread = ConsumerThread(name='consumer')

    def start_simulation(self):
        """
        Starts the sumo simulation which increments simulation step every second
        :return:
        """
        # start simulation
        self.sumo_obj.start()

    def get_ambulance_path(self):
        """
        returns a dictionary with key value pairs where key is edgeID, value is vehicles

        Here we need to increment a simulation step only once,
        :return: dictionary containing the (key,value) => key is edgeID, value is num vehicles
        """
        print("The set of edge ids in the ambulance path ")

        edge_dict = {}

        for i in range(0, len(edge_list)):
            edge = edge_list[i]
            edge_dict[edge] = randint(0, 2)

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

        logging.debug("Loading the json")
        with open("low_ways.json") as json_file:
            data_dict = json.load(json_file)

        global edge_list
        edge_list = list(data_dict.keys())
        logging.debug("The number of edges are " + str(len(edge_list)))
