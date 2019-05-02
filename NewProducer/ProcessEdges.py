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
        self.flag = True
        self.consumer_thread = ConsumerThread(name='consumer')
        self.consumer_thread.update_sumo_object(self.sumo_obj)

    def start_simulation(self):
        """
        Starts the sumo simulation which increments simulation step every second
        :return:
        """
        # start simulation
        self.sumo_obj.start()

    def register_topic(self, lat, lon, topic, graphid):
        logging.debug("Entered register topic")
        self.consumer_thread.register_topic_and_produce(lat, lon, topic, graphid)

        if self.flag:
            self.flag = False
            logging.debug("Calling thread only once")
            self.consumer_thread.start()

    def start_producing_content(self):
        """

        :return:
        """
        self.consumer_thread.start_producers()
        if self.flag == True:
            self.flag = False
            self.consumer_thread.start()

    def load_json(self):
        """
        test/utility method to see file loading etc.,
        :return: nothing
        """

        logging.debug("Loading the low_ways json ")
        with open("./InputFiles/low_ways_p.json") as json_file:
            data_dict = json.load(json_file)

        low_edge_list = list(data_dict.keys())
        logging.debug("The number of edges are " + str(len(low_edge_list)))

        logging.debug("Loading the mid_ways json ")
        with open("./InputFiles/mid_ways_p.json") as json_file:
            data_dict = json.load(json_file)

        mid_edge_list = list(data_dict.keys())
        logging.debug("The number of edges are " + str(len(mid_edge_list)))

        logging.debug("Loading the high_ways json ")
        with open("./InputFiles/high_ways_p.json") as json_file:
            data_dict = json.load(json_file)

        high_edge_list = list(data_dict.keys())
        logging.debug("The number of edges are " + str(len(high_edge_list)))
