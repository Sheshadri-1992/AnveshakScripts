from __future__ import print_function
import json
import logging
import threading
import time
import Queue
import numpy as np
from MqttPublish import MqttPublish
from Query import QueryStruct

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s', )
low_ways = "./input/low_ways.json"
mid_ways = "./input/mid_ways.json"
high_ways = "./input/low_ways.json"


class LargeProducer(threading.Thread):

    def __init__(self, edge_dict, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):

        super(LargeProducer, self).__init__()
        self.target = target
        self.name = name
        self.large_queue = Queue.Queue()
        self.large_edge_list = []
        self.global_edge_dict = edge_dict

        logging.debug("Loading the high_ways json ")
        with open("./InputFiles/high_ways_p.json") as json_file:
            data_dict = json.load(json_file)

        self.large_edge_list = list(data_dict.keys())
        logging.debug("The number of edges are " + str(len(self.large_edge_list)))

    def run(self):

        # print("I am  here in large producer ")
        length = len(self.large_edge_list)
        index = 0
        while True:
            if not self.large_queue.full():

                while index < length:

                    edge_id = self.large_edge_list[index % length]

                    for lane in self.global_edge_dict[edge_id]:
                        item = QueryStruct(1, lane)
                        self.large_queue.put(item)
#                        logging.debug("Putting item : edge " + item.get_edge_id() + " : qsize " + str(
#                            self.large_queue.qsize()) + " items in large queue")

                    index = index + 1
		logging.debug("index id is "+str(index))
		index = 0
                time.sleep(10)

            else:
                logging.debug("queue is full ")
                time.sleep(10)

    def get_element_from_queue(self):
        """

        :return: return an object if exists else return None
        """

        # check for queue not being empty
        if not self.large_queue.empty():
            item = self.large_queue.get()
            return item

        return None


class MediumProducer(threading.Thread):

    def __init__(self, edge_dict, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):

        super(MediumProducer, self).__init__()
        self.target = target
        self.name = name
        self.medium_queue = Queue.Queue()
        self.medium_edge_list = []
        self.global_edge_dict = edge_dict

        logging.debug("Loading the mid_ways json ")
        with open("./InputFiles/mid_ways_p.json") as json_file:
            data_dict = json.load(json_file)

        self.medium_edge_list = list(data_dict.keys())
        logging.debug("The number of edges are " + str(len(self.medium_edge_list)))

    def run(self):

        index = 0
        length = len(self.medium_edge_list)
        # print("I am  here in medium producer ")
        while True:
            if not self.medium_queue.full():

                while index < length:

                    edge_id = self.medium_edge_list[index % length]

                    for lane in self.global_edge_dict[edge_id]:
                        item = QueryStruct(2, lane)
                        self.medium_queue.put(item)
 #                       logging.debug("Putting item : edge " + item.get_edge_id() + " : qsize " + str(
 #                           self.medium_queue.qsize()) + " items in medium queue")

                    index = index + 1

		index = 0
                time.sleep(5)

            else:
                logging.debug("queue is full ")
                time.sleep(5)

    def get_element_from_queue(self):
        """

        :return: return an object if exists else return None
        """

        # check for queue not being empty
        if not self.medium_queue.empty():
            item = self.medium_queue.get()
            return item

        return None


class SmallProducer(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):

        super(SmallProducer, self).__init__()
        self.target = target
        self.name = name
        self.small_queue = Queue.Queue()
        self.small_edge_list = []

        logging.debug("Loading the low_ways json ")
        with open("./InputFiles/low_ways_p.json") as json_file:
            data_dict = json.load(json_file)

        self.small_edge_list = list(data_dict.keys())
        logging.debug("The number of edges are " + str(len(self.small_edge_list)))

    def run(self):

        index = 0
        length = len(self.small_edge_list)
        # print("I am  here in small producer ")
        while True:
            if not self.small_queue.full():
                item = QueryStruct(3, self.small_edge_list[index % length])
                self.small_queue.put(item)
                logging.debug("Putting item : edge " + item.get_edge_id() + " : qsize " + str(
                    self.small_queue.qsize()) + " items in small queue")
                index = index + 1
                time.sleep(0.1)
                # break
            else:
                logging.debug("queue is full ")
                time.sleep(1)

    def get_element_from_queue(self):
        """

        :return: return a object if exists else return None
        """

        # check for queue not being empty
        if not self.small_queue.empty():
            logging.debug("Size before " + str(self.small_queue.qsize()))
            item = self.small_queue.get()
            logging.debug("The item is " + str(item.timestamp) + " The edge id is " + str(item.edgeid))
            logging.debug("Size after " + str(self.small_queue.qsize()))
            return item

        return None
