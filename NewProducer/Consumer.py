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

MAX_BATCH = 3400

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

        logging.debug("Loading the low_ways json ")
        with open("./InputFiles/osm_sumo.json") as json_file:
            osm_sumo = json.load(json_file)

        self.edge_lane_dict = osm_sumo

        logging.debug("Loading the low_ways json ")
        with open("./InputFiles/sumo_osm.json") as json_file:
            sumo_osm = json.load(json_file)
        self.lane_edge_dict = sumo_osm

        self.large_thread = LargeProducer(self.edge_lane_dict, name='large-producer')
        self.medium_thread = MediumProducer(self.edge_lane_dict, name="medium-producer")

        # default registration topic
        self.large_topic = "large"
        self.medium_topic = "medium-live-traffic"
        self.small_topic = "small"
        self.ambulance_topic = "ambulance"

        # registration dictionary
        self.register_dict = {}

        logging.debug("Started all the producers...")

    def start_producers(self):
        """
        start producing items from all queues
        :return:
        """
        logging.debug("Started producing...")
        self.large_thread.start()
        self.medium_thread.start()


    def update_sumo_object(self, sumo_obj):
        """
        Assign the sumo object so that it can retrieve traffic density
        :return: nothing
        """
        logging.debug("updated sumo object")
        self.sumo_obj = sumo_obj

    def register_topic_and_produce(self, p, q, topic, graphid):

        logging.debug("The graph id is " + str(graphid) + " the topic is " + topic)

        if int(graphid) == 0:

            self.large_topic = topic
            self.register_dict[self.large_topic] = True
            self.large_thread.start()

        elif int(graphid) == 1:

            self.medium_topic = topic
            self.register_dict[self.medium_topic] = True
            self.medium_thread.start()

        elif int(graphid) == 2:

            self.register_dict[topic] = True
            self.small_topic = topic

    def ambulance_topic_and_produce(self, ambulance_id, topic, source, dest):
        """

        :param ambulance_id: The id of the vehicle to be inserted
        :param topic: The topic to which we need to publish ambulance updates
        :param source: The location of ambulance
        :param dest: The location of hospital
        :return: nothing
        """

        logging.debug("The parameters received are "+str(ambulance_id)+str(topic)+str(source)+ str(dest))

        # here the proper shortest route will be given to me
        self.sumo_obj.add_new_vehicle(str(50000), "25000",[]) #ambulance id and list of edges
        self.ambulance_topic = topic
        self.sumo_obj.set_ambulance_id(str(50000))
        self.register_dict[self.ambulance_topic] = True

        # a call to compute shortest path, I will get ambulance id and a list of edges as route
        # it takes source and destination node id

    def update_edge_list(self, edge_list):
        """

        :param edge_list: sent by the Process Edges
        :return: nothing
        """
        self.edge_list = edge_list

    def prepare_candidate_edges(self, candidate_edge_list):
        """
        Method to prepare candidate edges which will be sent to sumo for traci calls
        :param candidate_edge_list: the edges will be just plain osm id, we need to convert into sumo id and
               then make traci calls
        :return: return traci complaint edge id
        """
        candidate_list = []

        for edge_id in candidate_edge_list:

            if edge_id in self.edge_lane_dict:
                lane_list = self.edge_lane_dict[edge_id]
                candidate_list = candidate_list + lane_list  # this is where things are aggregated

        logging.debug("Number of edges in candidate list " + str(len(candidate_list)))
        return candidate_list

    def aggregate_edge_id_traffic(self, road_dict):
        """
        Method to aggregate traffic density from lane id to edge id
        :param road_dict: contains lane id , these needs to be remapped to their respective edge id
        :return: An edge id dictionary where key is edge id and value is number of vehicles
        """
        new_dict = {}
        if road_dict is None:
            return None

        for lane in road_dict:

            edge_id = self.lane_edge_dict[lane]

            if edge_id not in new_dict:
                new_dict[edge_id] = int(road_dict[lane])
            else:
                new_dict[edge_id] = int(new_dict[edge_id]) + int(road_dict[lane])

        return new_dict

    @staticmethod
    def get_edge_color(edge_traffic_dict):

        edgeid_color_dict = {}

        for edge in edge_traffic_dict:

            num_vehicles = edge_traffic_dict[edge]

            # color bucket logic
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

            logging.debug("Entered the consumer..")

            batch_count = 0
            medium_candidate_edges = []
            large_candidate_edges = []
            curr_time = datetime.now()

            # Medium queue edges
            while not self.medium_thread.medium_queue.empty():

                item = self.medium_thread.get_element_from_queue()

                if batch_count < MAX_BATCH and (item.timestamp >= curr_time):
                    medium_candidate_edges.append(item.get_edge_id())
                    batch_count = batch_count + 1
                else:
                    logging.debug("dropping the message medium producer")

            # Large queue edges
            while not self.large_thread.large_queue.empty():

                item = self.large_thread.get_element_from_queue()
                if batch_count < MAX_BATCH and (item.timestamp >= curr_time):
                    large_candidate_edges.append(item.get_edge_id())
                    batch_count = batch_count + 1
                else:
                    logging.debug("dropping the message large producer")

            logging.debug("The medium candidate edges are " + str(len(medium_candidate_edges)))
            logging.debug("The large candidate edges are" + str(len(large_candidate_edges)))

            # The original candidate id do not contain lane id
            medium_candidate_edges = self.prepare_candidate_edges(medium_candidate_edges)
            large_candidate_edges = self.prepare_candidate_edges(large_candidate_edges)

            # small_dict = self.sumo_obj.return_traffic_density(small_candidate_edges)
            medium_dict = self.sumo_obj.return_traffic_density(medium_candidate_edges)
            large_dict = self.sumo_obj.return_traffic_density(large_candidate_edges)

            # aggregate stuff needed here
            medium_dict = self.aggregate_edge_id_traffic(medium_dict)
            large_dict = self.aggregate_edge_id_traffic(large_dict)

            # self.sumo_obj.set_ambulance_id("dummy_ambulance_id")

            # color_small = self.get_edge_color(small_dict)
            color_medium = self.get_edge_color(medium_dict)
            color_large = self.get_edge_color(large_dict)

            mqtt_object.connect_to_broker()

            if self.medium_topic in self.register_dict:
                logging.debug("Medium topic set..sending message "+str(len(color_medium.keys())))
                mqtt_object.send_edge_message(json.dumps(color_medium), self.medium_topic)

            if self.large_topic in self.register_dict:
                logging.debug("Large topic set..sending message")
                mqtt_object.send_edge_message(json.dumps(color_large), self.large_topic)

            if self.ambulance_topic != "" and self.ambulance_topic in self.register_dict:
                vehicle_stat_dict = self.sumo_obj.get_vehicle_stats()
                logging.debug("Ambulance topic set..sending message")
                mqtt_object.send_vertex_message(json.dumps(vehicle_stat_dict), self.ambulance_topic)

            mqtt_object.disconnect_broker()

            logging.debug("Consumer sleeping...")
            time.sleep(1)
