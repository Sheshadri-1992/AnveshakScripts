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

        self.large_thread = LargeProducer(name='large-producer')
        self.medium_thread = MediumProducer(name="medium-producer")
        self.small_thread = SmallProducer(name="small-producer")

        self.large_thread.start()
        self.medium_thread.start()
        self.small_thread.start()

        logging.debug("Started all the producers...")

    def update_edge_list(self, edge_list):
        """

        :param edge_list: sent by the Process Edges
        :return: nothing
        """
        self.edge_list = edge_list

    def get_edge_color(self, index):

        changed = False

        return changed

    def get_edge_color_buckets(self, candidate_edges):
        """
        Returns color bucket dictionary
        :param candidate_edges: The list of edges that are supposed to be sent to the mqtt broker
        :return: a dictionary where key is edge id and value is color bucket
        """
        edgeid_color_dict = {}

        return edgeid_color_dict 

    def run(self):
        mqtt_object = MqttPublish()
        mqtt_object.print_variables()

        while True:

            batch_count = 0
            candidate_edges = []
            currtime = datetime.now()

            # Run simulation step here

            while not self.small_thread.small_queue.empty():

                item = self.small_thread.get_element_from_queue()
                if (batch_count < MAX_BATCH) and (item.timestamp >= currtime):
                    candidate_edges.append(item.get_edge_id())
                    batch_count = batch_count + 1

            while not self.medium_thread.medium_queue.empty():

                item = self.medium_thread.get_element_from_queue()
                if batch_count < MAX_BATCH and (item.timestamp >= currtime):
                    candidate_edges.append(item.get_edge_id())
                    batch_count = batch_count + 1

            while not self.large_thread.large_queue.empty():

                item = self.large_thread.get_element_from_queue
                if batch_count < MAX_BATCH and (item.timestamp >= currtime):
                    candidate_edges.append(item.get_edge_id())
                    batch_count = batch_count + 1

            logging.debug("The number of edges are " + str(len(candidate_edges)))

            mqtt_object.connect_to_broker()
            mqtt_object.send_vertex_message(None)
            mqtt_object.send_edge_message(None)
            mqtt_object.disconnect_broker()

            time.sleep(1)
