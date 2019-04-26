from __future__ import print_function

import json
import logging
# import paho.mqtt.client as mqtt
import threading
# import traci
import time
from datetime import datetime
from random import randint
import Queue
import numpy as np
from MqttPublish import MqttPublish
from Query import QueryStruct

############################################ QUEUES ############################################
large_queue = Queue.Queue()
medium_queue = Queue.Queue()
small_queue = Queue.Queue()
vehicle_queue = Queue.Queue()
edge_list = []
my_dict = {}
################################################################################################

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s', )
MAX_BATCH = 4000


############################################ LARGE PRODUCER ####################################

class LargeProducer(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):

        super(LargeProducer, self).__init__()
        self.target = target
        self.name = name

    def run(self):

        # print("I am  here in large producer ")
        while True:
            if not large_queue.full():

                item = QueryStruct(1, "edgeid")
                large_queue.put(item)
                logging.debug('Putting item : ' + str(large_queue.qsize()) + ' items in large queue')
                time.sleep(10)
                # break
            else:
                logging.debug("queue is full ")
                time.sleep(10)


################################################################################################

############################################ MEDIUM PRODUCER ####################################

class MediumProducer(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):

        super(MediumProducer, self).__init__()
        self.target = target
        self.name = name

    def run(self):

        # print("I am  here in medium producer ")
        while True:
            if not medium_queue.full():
                item = QueryStruct(2, "edgeid")
                medium_queue.put(item)
                logging.debug('Putting ' + ' : ' + str(medium_queue.qsize()) + ' items in medium queue')
                time.sleep(5)
                # break
            else:
                logging.debug("queue is full ")
                time.sleep(5)


################################################################################################

############################################ LARGE PRODUCER ####################################

class SmallProducer(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):

        super(SmallProducer, self).__init__()
        self.target = target
        self.name = name

    def run(self):

        # print("I am  here in small producer ")
        while True:
            if not small_queue.full():
                item = QueryStruct(3, "edgeid")
                small_queue.put(item)
                logging.debug('Putting item : ' + str(small_queue.qsize()) + ' items in small queue')
                time.sleep(0.01)
                # break
            else:
                logging.debug("queue is full ")
                time.sleep(1)


################################################################################################

############################################ CONSUMER THREAD ####################################

class ConsumerThread(threading.Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(ConsumerThread, self).__init__()
        self.target = target
        self.name = name
        return

    def generate_rand_prob(self):

        number = np.random.choice([0, 1], 1, p=[0.5, 0.5])
        choice = list(number)[0]

        print("choice ", int(choice))

        if choice == 0:
            logging.debug(" choice is don't change")
        else:
            logging.debug(" choice is change")

        return choice

    def get_edge_color(self, index):

        choice = self.generate_rand_prob()
        changed = False
        edge = edge_list[index]

        if edge not in my_dict:
            my_dict[edge] = randint(0, 2)
            changed = True

        elif choice == 1:

            color = randint(0, 2)
            if my_dict[edge] != color:
                my_dict[edge] = color
                changed = True

        return changed

    def run(self):
        mqtt_object = MqttPublish()
        mqtt_object.print_variables()

        num_edges = len(edge_list)
        index = 0

        my_file_handler = open("edge_count.txt", 'a')

        while True:

            edge_dict = {}
            batch_count = 0
            currtime = datetime.now()

            # Run simulation step here

            # while not small_queue.empty():
            #
            #     item = small_queue.get()
            #     if (batch_count < MAX_BATCH) and (item.timestamp >= currtime):
            #         # item.print_members()
            #         my_dict[str(edge_list[batch_count % 4000])] = randint(0, 2)
            #         batch_count = batch_count + 1
            #
            # while not medium_queue.empty():
            #
            #     item = medium_queue.get()
            #     if batch_count < MAX_BATCH and (item.timestamp >= currtime):
            #         # item.print_members()
            #         my_dict[str(edge_list[batch_count % 4000])] = randint(0, 2)
            #         batch_count = batch_count + 1
            #
            # while not large_queue.empty():
            #
            #     item = large_queue.get()
            #     if batch_count < MAX_BATCH and (item.timestamp >= currtime):
            #         # item.print_members()
            #         my_dict[str(edge_list[batch_count % 4000])] = randint(0, 2)
            #         batch_count = batch_count + 1

            # Need to call the broker here

            for i in range(0, 1500):
                if index == num_edges:
                    index = 0

                logging.debug("The index is " + str(index))
                changed = self.get_edge_color(index)

                edge = edge_list[index]
                if changed:
                    edge_dict[edge] = my_dict[edge]

                index = index + 1

            logging.debug("The number of edges are " + str(len(edge_list)))
            logging.debug("The number of keys are " + str(len(edge_dict.keys())))

            my_file_handler.write(str(len(edge_dict.keys()))+"\n")

            mqtt_object.connect_to_broker()
            mqtt_object.send_vertex_message(None)
            mqtt_object.send_edge_message(json.dumps(edge_dict))

            mqtt_object.disconnect_broker()

            time.sleep(1)


################################################################################################


class ProducerConsumer:

    def __init__(self):
        logging.debug("Producer Consumer object has been initiated")

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
        # large_thread = LargeProducer(name='large-producer')
        # large_thread.start()
        #
        # medium_thread = MediumProducer(name="medium-producer")
        # medium_thread.start()
        #
        # small_thread = SmallProducer(name="small-producer")
        # small_thread.start()

        consumer_thread = ConsumerThread(name='consumer')
        consumer_thread.start()

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
