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
        self.sumo_flag = True
        self.consumer_thread = ConsumerThread(name='consumer')
        self.consumer_thread.update_sumo_object(self.sumo_obj)

    def start_simulation(self):
        """
        Starts the sumo simulation which increments simulation step every second
        :return:
        """
        # start simulation
        self.sumo_obj.start()
        return "success"

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
        if self.flag:
            self.flag = False
            self.consumer_thread.start()

    def set_ambulance_co_ordinates(self, ambulance_dict):
        """

        :param ambulance_dict: The json received which contains src, dest, lat, batch_size, topic
        :return:nothing
        """

        logging.debug("The ambulance dict is "+str(ambulance_dict))
        ambulance = ambulance_dict['ambulance']
        hospital = ambulance_dict['hospital']
        sessionid = ambulance_dict['session']
        topic = ambulance_dict['topic']
        latency = ambulance_dict['latency']
        batch_size = ambulance_dict['batch_size']

        logging.debug(
            "Ambulance co-ordinates received " + str(ambulance) + " , " + str(hospital) + " , " + str(
                sessionid) + " , latency " + str(latency) + " , batchsize " + str(batch_size) + " , topic " + str(
                topic))

        self.consumer_thread.ambulance_topic_and_produce("newid", topic, ambulance, hospital)
        # message = self.sumo_obj.add_new_vehicle(50000, [])  # the second argument is a list of short edges

        return "New vehicle will be added"

    def stop_sumo(self):
        """
        close the simulation
        :return:
        """
        result = self.sumo_obj.stop()
        return result

    def load_json(self):
        """
        test/utility method to see file loading etc.,
        :return: nothing
        """
        return "Test Success"

    # logging.debug("Loading the low_ways json ")
    # with open("./InputFiles/low_ways_p.json") as json_file:
    #     data_dict = json.load(json_file)
    #
    # low_edge_list = list(data_dict.keys())
    # logging.debug("The number of edges are " + str(len(low_edge_list)))
    #
    # logging.debug("Loading the mid_ways json ")
    # with open("./InputFiles/mid_ways_p.json") as json_file:
    #     data_dict = json.load(json_file)
    #
    # mid_edge_list = list(data_dict.keys())
    # logging.debug("The number of edges are " + str(len(mid_edge_list)))
    #
    # logging.debug("Loading the high_ways json ")
    # with open("./InputFiles/high_ways_p.json") as json_file:
    #     data_dict = json.load(json_file)
    #
    # high_edge_list = list(data_dict.keys())
    # logging.debug("The number of edges are " + str(len(high_edge_list)))
