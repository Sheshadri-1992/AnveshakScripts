from __future__ import print_function

import json
import logging
import threading
import time
from datetime import datetime
from MqttPublish import MqttPublish
from Producer import LargeProducer, MediumProducer, SmallProducer
from Query import QueryStruct
import pickle
from networkx.readwrite import json_graph

MAX_BATCH = 1500

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
        self.edge_dist_dict = {}
        self.edge_node_map = {}

        # mandatory file loads
        logging.debug("Loading the low_ways json ")
        with open("./InputFiles/osm_sumo.json") as json_file:
            osm_sumo = json.load(json_file)

        self.edge_lane_dict = osm_sumo

        logging.debug("Loading the low_ways json ")
        with open("./InputFiles/sumo_osm.json") as json_file:
            sumo_osm = json.load(json_file)
        self.lane_edge_dict = sumo_osm

        logging.debug("Loading the Edge distance json ")
        with open("./InputFiles/sumo_distance.json") as json_file:
            self.edge_dist_dict = json.load(json_file)

        logging.debug("Loading the Node lat long json")
        with open("./InputFiles/nodes_lat_lon_coord.json") as json_file:
            self.edge_lat_long_dict = json.load(json_file)

        # threads
        self.large_thread = LargeProducer(self.edge_lane_dict, name='large-producer')
        self.medium_thread = MediumProducer(self.edge_lane_dict, name="medium-producer")

        # default registration topic
        self.large_topic = "large"
        self.medium_topic = "medium-live-traffic"
        self.small_topic = "small"
        self.ambulance_topic = "ambulance"
        self.path_topic = ""  # this has to sent first
        self.path_traffic_topic = ""  # this has to be be sent next
        self.traffic_color_topic = ""

        # registration dictionary
        self.register_dict = {}
        self.medium_edges_dict = {}
        self.large_edges_dict = {}

        # vehicle id for new additions
        self.vehicle_id = 50000

        # route id for new routes
        self.route_id = 60000

        # source and destination for ambulance
        self.amb_source = "-1"
        self.amb_dest = "-1"

        # reset flag
        self.stop_thread = False

        logging.debug("Started all the producers...")

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

    def ambulance_topic_and_produce(self, ambulance_id, position_topic, path_topic, path_traffic_topic, source, dest):
        """

        :param ambulance_id: The id of the vehicle to be inserted
        :param position_topic: The topic to which we need to publish ambulance updates
        :param path_topic: This is where the lat long of custom edges should be published
        :param path_traffic_topic: This is where the raw traffic updates have to be updated, lane level no aggregation
        :param source: The location of ambulance
        :param dest: The location of hospital
        :return: nothing
        """

        logging.debug(
            "The parameters received are " + str(ambulance_id) + str(position_topic) + str(source) + str(dest))

        # add new vehicle
        self.sumo_obj.add_new_vehicle(str(self.vehicle_id), str(self.route_id), [], source,
                                      dest)  # ambulance id and list of edges

        # set source and destination for ambulance
        self.amb_source = source  # VERY IMPORTANT
        self.amb_dest = dest  # VERY IMPORTANT

        # topic is set for the ambulance
        self.ambulance_topic = position_topic
        self.register_dict[self.ambulance_topic] = True
        self.sumo_obj.set_ambulance_id(str(self.vehicle_id))

        # Set a high speed for ambulance
        speed = self.sumo_obj.get_vehicle_speed(str(self.vehicle_id))
        self.sumo_obj.set_vehicle_speed(str(self.vehicle_id), 28.0)  # Setting the vehicle speed here

        # this is for the focus path
        self.path_topic = path_topic
        self.register_dict[self.path_topic] = True

        # this is for the raw traffic color updates
        self.path_traffic_topic = path_traffic_topic
        self.register_dict[self.path_traffic_topic] = True

        # this topic is for the traffic color updates
        self.traffic_color_topic = "traffic_color"
        self.register_dict[self.traffic_color_topic] = True

        # increment vehicle id
        self.vehicle_id = self.vehicle_id + 1
        self.route_id = self.route_id + 1

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

    def get_edge_color(self, edge_traffic_dict, producer_type):
        """
        This method optimizes the number of edge ids to sned
        :param edge_traffic_dict: the aggregated traffic density for each edges
        :param producer_type: 0- large, 1- medium , 2- small
        :return: the dictionary which contains edge id and color code for traffic density
        """

        new_insertions = 0
        edgeid_color_dict = {}

        for edge in edge_traffic_dict:

            try:

                num_vehicles = edge_traffic_dict[edge]
                total_distance = self.edge_dist_dict[edge]

                vehicles_per_meter = float(num_vehicles * 1.0) / float(total_distance * 1.0)
                cat_1 = vehicles_per_meter / 3.0
                cat_2 = (2.0 * vehicles_per_meter) / 3.0

                # color bucket logic
                if vehicles_per_meter <= cat_1:
                    edgeid_color_dict[edge] = 0
                elif cat_1 < vehicles_per_meter <= cat_2:
                    edgeid_color_dict[edge] = 1
                else:
                    edgeid_color_dict[edge] = 2

            except Exception as e:
                #print("Exception in get color ", e, " the edge is ", edge)
                edgeid_color_dict[edge] = 0

        local_dict = {}
        if producer_type == 0:
            local_dict = self.large_edges_dict
        elif producer_type == 1:
            local_dict = self.medium_edges_dict

        final_return_dict = {}

        for edge in edgeid_color_dict:

            if edge not in local_dict:
                local_dict[edge] = edgeid_color_dict[edge]  # this will give the color
                final_return_dict[edge] = edgeid_color_dict[edge]
                new_insertions = new_insertions + 1

            elif edge in local_dict:

                prev_color = local_dict[edge]
                curr_color = edgeid_color_dict[edge]

                if prev_color != curr_color:  # this is to check whether color has changed or not
                    final_return_dict[edge] = edgeid_color_dict[edge]

        if producer_type == 0:

            self.large_edges_dict = local_dict
            large_edges_count = self.large_thread.get_large_edge_list_length()
            if len(self.large_edges_dict.keys()) == large_edges_count:
                logging.debug(
                    "Colors to all the large edges have been sent at least once " + str(large_edges_count))

        elif producer_type == 1:

            self.medium_edges_dict = local_dict
            medium_edges_count = self.medium_thread.get_medium_edge_list_length()
            if len(self.medium_edges_dict.keys()) == medium_edges_count:
                logging.debug("Colors to all the medium edges have be sent at least once " + str(medium_edges_count))

        logging.debug("new insertions are " + str(new_insertions))

        return final_return_dict

    def get_edge_color_simple(self, edge_traffic_dict):
        """

        :param edge_traffic_dict: The key is edge id , value is traffic density
        :return: A dictionary where edgeid is key and value is color
        """
        edgeid_color_dict = {}

        for edge in edge_traffic_dict:

            try:

                num_vehicles = edge_traffic_dict[edge]

                total_distance = self.edge_dist_dict[edge]

                vehicles_per_meter = float(num_vehicles * 1.0) / float(total_distance * 1.0)
                cat_1 = vehicles_per_meter / 3.0
                cat_2 = (2.0 * vehicles_per_meter) / 3.0

                # color bucket logic
                if vehicles_per_meter <= cat_1:
                    edgeid_color_dict[edge] = 0
                elif cat_1 < vehicles_per_meter <= cat_2:
                    edgeid_color_dict[edge] = 1
                else:
                    edgeid_color_dict[edge] = 2

            except Exception as e:
                # print("Exception in get color ", e, " the edge is ",edge)
                edgeid_color_dict[edge] = 0

        return edgeid_color_dict

    def stop_producers(self):
        """
        Clears out all state
        :return:
        """

        try:

            self.medium_thread.kill_thread()
            self.large_thread.kill_thread()

            self.medium_thread.join()
            logging.debug("Medium thread has stopped")
            self.large_thread.join()
            logging.debug("Large Thread has been stopped")

            self.stop_thread = True
            logging.debug("All producer threads are stopped")

        except Exception as e:
            print("The exception is ", e)

    def get_traffic_id_lat_long_list(self, traffic_signal_list):
        """

        :param traffic_signal_list: the list of traffic light id
        :return: a list of tuple where each tuple is a lat long entry
        """

        traffic_id_lat_long_list = []

        for traffic_signal_id in traffic_signal_list:
            lat_long = self.edge_lat_long_dict[traffic_signal_id]  # new one
            lat = lat_long[0]
            lon = lat_long[1]
            pos_item = (lat, lon)
            traffic_id_lat_long_list.append(pos_item)

        return traffic_id_lat_long_list

    def get_total_edge_weight(self, edge_list):
        """

        :param edge_list: the edges whose wait has to be aggregated
        :return:sum total of distances of all the edges
        """
        total = 0
        for edge in edge_list:
            try:
                total = total + float(self.edge_dist_dict[edge])
            except Exception as e:
                total = total + 0
                print("Excpetion is ", e)

        logging.debug("The total weight is " + str(total))
        return total

    def set_resources(self):
        """
        Resets the reset flag
        :return:
        """
        self.stop_thread = False

    def run(self):
        mqtt_object = MqttPublish()
        mqtt_object.print_variables()
        self.stop_thread = False
        running_counter = 0

        while True:

            logging.debug("Entered the consumer..")

            if self.stop_thread:
                logging.debug("The reset flag has been called ")
                break

            batch_count = 0
            medium_candidate_edges = []
            large_candidate_edges = []
            curr_time = datetime.now()

            # Medium queue edges
            while batch_count < MAX_BATCH:  # and (item.timestamp >= curr_time):
                if not self.medium_thread.medium_queue.empty():
                    item = self.medium_thread.get_element_from_queue()
                    medium_candidate_edges.append(item.get_edge_id())
                    batch_count = batch_count + 1

            logging.debug("message medium producer " + str(batch_count) + " ,running counter " + str(running_counter))

            # Large queue edges
            while batch_count < MAX_BATCH:

                if not self.large_thread.large_queue.empty():  # and (item.timestamp >= curr_time):
                    item = self.large_thread.get_element_from_queue()
                    large_candidate_edges.append(item.get_edge_id())
                    batch_count = batch_count + 1

            # The original candidate id do not contain lane id
            medium_candidate_edges = self.prepare_candidate_edges(medium_candidate_edges)
            large_candidate_edges = self.prepare_candidate_edges(large_candidate_edges)

            logging.debug("The medium candidate edges are " + str(len(medium_candidate_edges)))
            logging.debug("The large candidate edges are" + str(len(large_candidate_edges)))

            # small_dict = self.sumo_obj.return_traffic_density(small_candidate_edges)
            medium_dict = self.sumo_obj.return_traffic_density(medium_candidate_edges)
            large_dict = self.sumo_obj.return_traffic_density(large_candidate_edges)

            # aggregate stuff needed here
            medium_dict = self.aggregate_edge_id_traffic(medium_dict)
            large_dict = self.aggregate_edge_id_traffic(large_dict)

            # self.sumo_obj.set_ambulance_id("dummy_ambulance_id")

            # color_small = self.get_edge_color(small_dict)
            color_medium = self.get_edge_color(medium_dict, 1)  # 1 is medium
            color_large = self.get_edge_color(large_dict, 0)  # 0 is small

            mqtt_object.connect_to_broker()

            if self.medium_topic in self.register_dict:
                logging.debug("Medium topic set..sending message, the label is " + str(running_counter) + " " + str(
                    len(color_medium.keys())))
                # key = "id:" +
                color_medium['id'] = str(running_counter)
                # final_message[str(running_counter)] = color_medium
                mqtt_object.send_edge_message(json.dumps(color_medium), self.medium_topic)

            if self.large_topic in self.register_dict:
                logging.debug("Large topic set..sending message")
                mqtt_object.send_edge_message(json.dumps(color_large), self.large_topic)

            if self.ambulance_topic != "" and self.ambulance_topic in self.register_dict:
                logging.debug("Ambulance topic set..sending message")
                vehicle_stat_dict = self.sumo_obj.get_vehicle_stats()
                mqtt_object.send_vertex_message(json.dumps(vehicle_stat_dict), self.ambulance_topic)

            if self.path_topic != "" and self.path_topic in self.register_dict:
                if self.register_dict[self.path_topic]:
                    logging.debug("path topic set..sending message..only once")
                    locations_dict = self.sumo_obj.get_custom_locations()
                    locations_list = list(locations_dict.keys())
                    traffic_id_list = self.sumo_obj.get_traffic_lights_for_vehicle(self.sumo_obj.get_ambulance_id())
                    traffic_id_lat_long_list = self.get_traffic_id_lat_long_list(traffic_id_list)

                    traffic_id_lat_long_dict = {}
                    for i in range(0, len(traffic_id_list)):
                        traffic_id_lat_long_dict[traffic_id_list[i]] = traffic_id_lat_long_list[i]

                    payload_dict = {}
                    payload_dict['traffic_signals'] = traffic_id_lat_long_dict
                    payload_dict['distance'] = self.get_total_edge_weight(locations_list)
                    payload_dict['path'] = locations_dict

                    mqtt_object.send_path_topic_message(json.dumps(payload_dict), self.path_topic)
                    # this is important to send it only once
                    # need to set it to True again when there is a custom edge list which gets updated
                    self.register_dict[self.path_topic] = False

            if self.path_traffic_topic != "" and self.path_traffic_topic in self.register_dict:
                logging.debug("path traffic topic set.. sending message")
                locations_dict = self.sumo_obj.get_custom_locations()
                candidate_edges = list(locations_dict.keys())
                lane_traffic_dict = self.sumo_obj.return_traffic_density(candidate_edges)
                lane_traffic_dict = self.get_edge_color_simple(lane_traffic_dict)
                mqtt_object.send_path_traffic_topic_message(json.dumps(lane_traffic_dict), self.path_traffic_topic)

            if self.traffic_color_topic != "" and self.traffic_color_topic in self.register_dict:
                traffic_color_dict = self.sumo_obj.prepare_traffic_color_payload()
                print("Getting the traffic color payload ", traffic_color_dict)

            mqtt_object.disconnect_broker()

            logging.debug("Consumer sleeping...")
            running_counter = running_counter + 1
            time.sleep(1)
