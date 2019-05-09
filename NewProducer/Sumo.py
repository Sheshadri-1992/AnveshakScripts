from __future__ import print_function
import paho.mqtt.client as mqtt
import traceback
import threading
import traceback
import socket
import json
import os, sys
import traci
import time
import logging
import TestCameraPosistion
import pickle
import xmltodict
import random
import sumolib
from collections import OrderedDict
import networkx as nx
import types
from networkx.readwrite import json_graph
import gen_shortest_path
from EdgeTrafficState import EdgeStateInfo

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s', )


class Sumo(threading.Thread):
    sumo_cmd = None
    lock = None
    edge_list = None
    ambulance_id = None

    def __init__(self):

        super(Sumo, self).__init__()
        logging.debug("Initialised sumo path")
        self.sumo_binary = "/usr/local/bin/sumo"
        self.sumo_cmd = [self.sumo_binary, "--collision.action", "none", "-c", "testconfig.sumocfg"]
        self.lock = threading.Lock()
        self.edge_list = []  # not used, remove after review
        self.ambulance_id = "-1"
        self.amb_src = ""
        self.amb_dest = ""
        self.edge_node_map = {}
        self.custom_edge_list = []
        self.custom_locations = {}
        self.edge_traffic_state = EdgeStateInfo()

        # start the simulation here
        traci.start(self.sumo_cmd)

        if 'SUMO_HOME' in os.environ:
            tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
            sys.path.append(tools)
        else:
            sys.exit("please declare environment variable 'SUMO_HOME'")

        with open("./InputFiles/sumo_mid_graph.json", 'rb') as f:
            data = f.read()
            data = json.loads(data)

        self.graph = json_graph.node_link_graph(data)  # this is the graph

        with open('./InputFiles/traffic_lights_anveshak.json', 'rb') as traffic_file:
            json_string = traffic_file.read()
            self.traffic_lights_set = json.loads(json_string)

        with open("./InputFiles/cameras_anveshak.json", 'rb') as camera_file:
            json_string = camera_file.read()
            self.camera_list = json.loads(json_string)

        with open("./InputFiles/nodes_coord.json", 'rb') as json_file:
            node_to_xy_json = json.load(json_file)
            self.node_to_xy_json = node_to_xy_json

        with open("./InputFiles/nodes_lat_lon_coord.json", 'rb') as json_file:
            node_to_lat_long_json = json.load(json_file)
            self.node_to_lat_long_json = node_to_lat_long_json

        logging.debug("All settings successfully initialized")

    def retrieve_edge_list(self):
        """
        retrieves all the edges in the given map from traci and it is set in the edge_list
        :return:
        """

        self.lock.acquire()
        self.edge_list = traci.edge.getIDList()
        self.lock.release()

        logging.debug("The number of edges in traci is " + str(len(self.edge_list)))

    def set_ambulance_id(self, vehicle_id):
        """
        Sets the ambulance Id, this may not be needed
        :return:
        """
        logging.debug("Got the ambulance id " + vehicle_id)
        self.ambulance_id = vehicle_id

    def get_ambulance_id(self):
        """

        :return: the ambulance id
        """
        return self.ambulance_id

    def get_vehicle_stats(self):
        """
        Make a traci call and return the ambulance speed and position
        :return: the ambulance speed and position
        """
        logging.debug("Sending the stats for the ambulance " + self.ambulance_id)
        ambulance_dict = {}

        try:

            self.lock.acquire()
            speed = traci.vehicle.getSpeed(self.ambulance_id)
            self.lock.release()

            self.lock.acquire()
            position = traci.vehicle.getPosition(self.ambulance_id)
            self.lock.release()

            pos_x = position[0]
            pos_y = position[1]

            self.lock.acquire()
            geo_co_ord = traci.simulation.convertGeo(pos_x, pos_y, fromGeo=False)
            self.lock.release()

            rev_co_ord = (geo_co_ord[1], geo_co_ord[0])

            ambulance_dict["vehicleid"] = str(self.ambulance_id)
            ambulance_dict["speed"] = speed
            ambulance_dict["position"] = rev_co_ord

            TestCameraPosistion.calculate_within_radius(geo_co_ord[1], geo_co_ord[0])  # lat, long in reverse order

            logging.debug("The dictionary is " + str(ambulance_dict))

        except Exception as e:

            logging.debug("Exception in vehicle stats method " + str(e))

        return ambulance_dict

    def get_traffic_lights_between_src_dest(self):
        """

        :param src: The starting point of ambulance route
        :param dest: The end point of the ambulance route
        :return:
        """
        logging.debug("The new traffic lights method got called")
        traffic_lights = gen_shortest_path.get_shortest_path_traffic(self.graph, self.traffic_lights_set, self.amb_src,
                                                                     self.amb_dest, -1)
        return traffic_lights

    def get_traffic_lights_for_vehicle(self, vehicle_id):
        """
        Returns all the traffic signals in the route
        :return: Returns all the traffic signals in the route
        """

        self.lock.acquire()
        all_traffic_routes = traci.vehicle.getNextTLS(vehicle_id)
        self.lock.release()

        traffic_id_list = []

        for item in all_traffic_routes:
            traffic_id_list.append(str(item[0]))

        return traffic_id_list

    def return_traffic_density(self, arg_edge_list):
        """
        makes traci call to each edge passed
        :param arg_edge_list: the edge list for which vehicle density is needed
        :return: a dictionary with key as vehicleid,
        """
        edge_dict = {}

        # self.get_traffic_lights()

        if arg_edge_list is None:
            logging.debug("Empty list sent")
            return edge_dict

        try:

            for edge in arg_edge_list:
                self.lock.acquire()
                num_vehicles = traci.edge.getLastStepVehicleNumber(edge)
                self.lock.release()
                edge_dict[edge] = num_vehicles
        except Exception as e:

            logging.debug("Exception in return traffic density method " + str(e))

        return edge_dict

    def get_shortest_path(self, src, dest):
        """

        :param src: The source id
        :param dest: The destination id
        :return: A set of edges which constitute shortest path
        """
        return None

    def send_message_to_everyone(self):
        """
        A place holder to call anveshak module
        :return:
        """
        logging.debug("Got the message")

    def init_green_wave(self):
        """
        Starts by turning at least 4 signals green
        :return:

        """
        print("In green wave ")
        traffic_id_list = self.edge_traffic_state.get_traffic_id_list()
        traffic_id_index_dict = self.edge_traffic_state.get_traffic_id_index_dict()
        num_traffic_signals = len(traffic_id_list)
        logging.debug("The number of traffic signals are " + str(num_traffic_signals))

        try:

            completed_edges = 0
            for i in range(0, num_traffic_signals):

                if i >= 1:  # turn only one camera green
                    break

                traffic_signal_id = traffic_id_list[i]
                lane_index = traffic_id_index_dict[traffic_signal_id]

                self.lock.acquire()
                curr_state = traci.trafficlight.getRedYellowGreenState(traffic_signal_id)
                state_length = len(curr_state)

                new_state = ""
                for j in range(0, state_length):
                    if j == int(lane_index):
                        new_state = new_state + 'G'
                    else:
                        new_state = new_state + 'r'

                traci.trafficlight.setRedYellowGreenState(traffic_signal_id, new_state)
                new_state = traci.trafficlight.getRedYellowGreenState(traffic_signal_id)
                logging.debug("Prev state " + str(curr_state) + " set state " + str(new_state))

                self.lock.release()
                completed_edges = completed_edges + 1

            completed_edges = completed_edges - 1
            print("Processed ", completed_edges, " setting ", completed_edges)
            self.edge_traffic_state.set_index(completed_edges)

        except Exception as e:

            print("Excpetion in initi green wave " + e)

    def add_new_vehicle(self, vehicle_id, new_route_id, custom_edge_list, source, dest):
        """
        This method needs to add a vehicle and a set of routes it will follow
        The vehicle is an ambulance, the new route is the set of sumo edges
        :param vehicle_id: id of the ambulance
        :param new_route_id for adding new route
        :param custom_edge_list: the custom edge list for the new route
        :return:
        """

        custom_edge_list = ["45250008#7", "-45250008#7", "-45250008#6", "-45250008#5", "-45250008#4", "-45250008#3",
                            "-45250008#2", "-45250008#1", "-45250008#0", "45250014#0", "45250533#0", "45250533#1",
                            "45250533#2", "45250533#3", "-46951252#1", "-46951252#0", "-35901381#10", "-35901381#9",
                            "-35901381#8", "-35901381#7", "-35901381#6", "-35901381#5", "-35901381#4", "-35901381#3",
                            "-35901381#2", "-35901381#1", "40151526#2", "-215412812", "-345411282#1", "-345411282#0",
                            "-404335353", "383028788#12", "383028788#13", "379878516#0", "379878516#1", "383029332",
                            "392213813", "383031432#0", "383031432#1", "-470223620", "470223615#0", "470223615#1",
                            "470223615#2", "470223615#3", "236578402", "-452366265#19", "-452366265#18",
                            "-452366265#17", "-452366265#16", "-236531497#1", "-236531497#0", "46918817", "-42013627#7",
                            "-42013627#6", "-42013627#5", "46918821"]

        # important , ambulance source, hospital dest is set
        self.amb_src = source
        self.amb_dest = dest

        custom_edge_list, locations, edge_node_map = gen_shortest_path.compute_shortest_path(source, dest, self.graph)
        self.custom_edge_list = custom_edge_list
        self.custom_locations = locations
        self.edge_node_map = edge_node_map

        self.edge_traffic_state.set_edge_list(self.custom_edge_list)  # set the edge list

        print("The custom edge locations are ", custom_edge_list)
        logging.debug("The first lane " + str(custom_edge_list[0] + "_0"))

        self.lock.acquire()
        traci.route.add(new_route_id, custom_edge_list)
        traci.vehicle.add(vehicle_id, new_route_id)
        traci.vehicle.moveTo(vehicle_id, custom_edge_list[0] + "_0", pos=1)  # lane 0 of first edge
        self.lock.release()

        # store all the traffic light ids
        self.lock.acquire()
        traffic_light_sequence = traci.vehicle.getNextTLS(vehicle_id)  # THIS API HAS TO BE REPLACED
        # traffic_light_sequence = self.get_traffic_lights_between_src_dest()
        self.lock.release()

        # all the upcoming traffic lights for the given vehicle
        traffic_id_index_dict = {}
        traffic_light_list = []
        for item in traffic_light_sequence:
            traffic_light_id = item[0]
            traffic_id_index_dict[item[0]] = item[1]  # this is the lane index
            traffic_light_list.append(traffic_light_id)

        traffic_id_phase_dict = {}
        traffic_id_state_dict = {}
        for traffic_id in traffic_light_list:
            self.lock.acquire()
            traffic_phase = traci.trafficlight.getPhase(traffic_id)
            traffic_id_phase_dict[traffic_id] = traffic_phase

            traffic_state = traci.trafficlight.getRedYellowGreenState(traffic_id)
            traffic_id_state_dict[traffic_id] = traffic_state
            self.lock.release()

        traffic_id_lanes_dict = {}
        for traffic_id in traffic_light_list:
            self.lock.acquire()
            lanes = traci.trafficlight.getControlledLanes(traffic_id)
            traffic_id_lanes_dict[traffic_id] = lanes
            self.lock.release()

        edge_lane_dict = {}
        for edge_id in custom_edge_list:
            self.lock.acquire()
            number = traci.edge.getLaneNumber(edge_id)
            lane_list = []

            for i in range(0, number):
                lane_id = edge_id + "_" + str(i)
                lane_list.append(lane_id)

            edge_lane_dict[edge_id] = lane_list
            self.lock.release()

        # structures which will be referred to later
        self.edge_traffic_state.set_traffic_id_list(traffic_light_list)
        self.edge_traffic_state.set_traffic_phase_dict(traffic_id_phase_dict)
        self.edge_traffic_state.set_traffic_id_lane_dict(traffic_id_lanes_dict)
        self.edge_traffic_state.set_edge_lane_dict(edge_lane_dict)
        self.edge_traffic_state.set_traffic_id_index_dict(traffic_id_index_dict)
        self.edge_traffic_state.set_traffic_id_state_dict(traffic_id_state_dict)

        logging.debug("Added a vehicle successfully")

        print("Traffic lanes are ", self.edge_traffic_state.get_traffic_id_list())
        print("Lanes controlled by traffic lights ", self.edge_traffic_state.get_traffic_id_lane_dict())

        return "Added a vehicle successfully"

    def get_custom_locations(self):
        """
        This method returns the custom locations, which contain lat lon pair for each edges
        :return: This method returns the custom locations
        """
        return self.custom_locations

    def get_custom_route_list(self):
        """
        This method returns the route followed in between source and destination
        :return: Returns the custom route list
        """
        return self.custom_edge_list

    def prepare_traffic_color_payload(self):
        """
        prepare a payload and send every second
        :return:
        """

        custom_edge_list = self.custom_edge_list  # this will give me the edge list
        custom_traffic_lights = self.get_traffic_lights_for_vehicle(self.ambulance_id)  # THIS API HAS TO BE REPLACED
        # custom_traffic_lights = self.get_traffic_lights_between_src_dest()
        traffic_id_color_dict = {}

        for traffic_signal_id in custom_traffic_lights:

            self.lock.acquire()
            traffic_lanes = traci.trafficlight.getControlledLanes(traffic_signal_id)
            self.lock.release()

            for edge in custom_edge_list:

                index = 0
                matches = 0
                for lane in traffic_lanes:

                    lane_to_edge_id = lane[:-2]
                    if lane_to_edge_id == edge:
                        self.lock.acquire()
                        color_state = traci.trafficlight.getRedYellowGreenState(traffic_signal_id)
                        all_edge_lanes = traci.edge.getLaneNumber(edge)
                        vehicle_lane_id = traci.vehicle.getLaneID(self.ambulance_id)
                        self.lock.release()
                        color = color_state[index]
                        traffic_id_color_dict[traffic_signal_id] = color

                        print("*************************************************************")
                        print("MATCH FOUND ", edge, lane_to_edge_id, " match count ", matches, " traffic signal",
                              traffic_signal_id)
                        print("MATCH FOUND ", all_edge_lanes, " match count ", matches, " traffic signal",
                              traffic_signal_id)
                        print("MATCH FOUND ", vehicle_lane_id, " match count ", matches, " traffic signal",
                              traffic_signal_id)
                        print("*************************************************************")
                        matches = matches + 1

                    index = index + 1

                if matches > 1:
                    print("WARNING MORE THAN ONE LANE MATCHES EDGE ID!!", matches)

        print("The traffic id color dict is ", traffic_id_color_dict)
        return traffic_id_color_dict

    def get_vehicle_speed(self, vehicle_id):
        """

        :param vehicle_id: the id of the ambulance
        :return: the speed of the vehicle (speed in m/s)
        """
        self.lock.acquire()
        speed = traci.vehicle.getSpeed(vehicle_id)
        self.lock.release()

        return speed

    def set_vehicle_speed(self, vehicle_id, speed):
        """

        :param vehicle_id: the id of the ambulance
        :param speed: the speed that is set to the vehicle (speed in m/s)
        :return: nothing
        """
        self.lock.acquire()
        traci.vehicle.setSpeed(vehicle_id, speed)
        traci.vehicle.setSpeedMode(vehicle_id, 0)  # 0 is rouge mode
        traci.vehicle.setLaneChangeMode(vehicle_id, 2218)  # 2218 is rouge mode
        self.lock.release()

    def perform_reset_traffic_lights(self, reset_id_list):
        """

        :param reset_id_list:
        :return:
        """

        for traffic_signal_id in reset_id_list:
            traffic_id_state_dict = self.edge_traffic_state.get_traffic_id_state_dict()
            old_state = ""

            if traffic_signal_id in traffic_id_state_dict:
                old_state = traffic_id_state_dict[traffic_signal_id]
            else:
                self.lock.acquire()
                old_state = traci.trafficlight.getRedYellowGreenState(traffic_signal_id)
                self.lock.release()

            self.lock.acquire()
            traci.trafficlight.setRedYellowGreenState(traffic_signal_id, old_state)
            traci.trafficlight.setPhaseDuration(traffic_signal_id, 120)  # 120 seconds of prev state
            self.lock.release()

            print("Reset the traffic lights to old state ", old_state)

    def return_lane_id_given_edge_id_and_traffic_id(self, edge_id, traffic_id):
        """
        Returns the lane id in the set of all lanes in the traffic id
        :param edge_id The current edge id of the vehicle
        :param traffic_id The current traffic id
        :return:
        """

    def perform_set_traffic_lights(self, set_id_list):
        """

        :param set_id_list: the traffic id which i need to turn green
        :return: nothing
        """

        for traffic_signal_id in set_id_list:
            self.lock.acquire()
            curr_state = traci.trafficlight.getRedYellowGreenState(traffic_signal_id)
            self.lock.release()

            traffic_id_state_dict = self.edge_traffic_state.get_traffic_id_state_dict()
            traffic_id_state_dict[traffic_signal_id] = curr_state

            state_length = len(curr_state)  # set everything to Green for now
            new_state = 'G' * state_length

            self.lock.acquire()
            traci.trafficlight.setRedYellowGreenState(traffic_signal_id, new_state)
            self.lock.release()

            print("In the perform set traffic lights state set ", new_state)

    def perform_set_reset_traffic_lights(self, json_string):
        """

        :param json_string: received by the zmqq messaage
        :return:
        """
        set_reset_dict = json.loads(json_string)
        set_id_list = []
        reset_id_list = []

        if 'set' in set_reset_dict:
            print("Setting the following json ", set_id_list)
            set_id_list = set_reset_dict['set']
            self.perform_set_traffic_lights(set_id_list)
        else:
            print("Resetting the following json ", reset_id_list)
            reset_id_list = set_reset_dict['reset']
            self.perform_reset_traffic_lights(reset_id_list)

    def get_next_camera(self):
        """
        returns the id of the next camera id, in which a vehicle will feature or skip
        but never takes a wrong decision
        :return: return camera id
        """
        if self.ambulance_id == "-1":
            logging.debug("Ambulance id not yet set")
            return

        self.lock.acquire()
        curr_edge_id = traci.vehicle.getRoadID(self.ambulance_id)
        self.lock.release()

        if curr_edge_id[0] == ":":
            print("Returning Internal Edge ", curr_edge_id)
            return

        custom_node_id_list = []
        first_edge = self.custom_edge_list[0]
        node_tuple = self.edge_node_map[first_edge]
        custom_node_id_list.append(str(node_tuple[0]))
        custom_node_id_list.append(str(node_tuple[1]))

        for edge_id in self.custom_edge_list[1:]:
            node_tuple = self.edge_node_map[edge_id]
            custom_node_id_list.append(str(node_tuple[1]))

        custom_node_id_set = set(custom_node_id_list)

        print("The camera list is ", self.camera_list)
        camera_set = set(self.camera_list)
        cameras_in_path = camera_set.intersection(custom_node_id_set)

        # print("Custom node id set ", custom_node_id_set)
        print("************ Cameras path ", cameras_in_path)

        print("The current edge the vehicle is in ", curr_edge_id)
        node_1 = self.edge_node_map.get(curr_edge_id)[1]  # the ending node
        print("The node 1 is ", node_1)

        cameras_in_path_list = []
        for custom_node_id in custom_node_id_list:
            if custom_node_id in cameras_in_path:
                cameras_in_path_list.append(custom_node_id)

        # convert set to list
        # cameras_in_path_list = list(cameras_in_path)

        print("The custom node id list is ", custom_node_id_list)
        print("************************* Camera in path list is ", cameras_in_path_list)

        node1_index = 0
        for ele in custom_node_id_list:
            if node_1 == ele:
                print("Element is found ", ele)
                break

            node1_index = node1_index + 1
        end_index = node1_index + 3

        print("start index is ", node1_index, " end_index ", end_index)

        if end_index > (len(custom_node_id_list) - 1):
            end_index = (len(custom_node_id_list) - 1)

        candidate_list = custom_node_id_list[node1_index:end_index]
        print("start index ", node1_index, " end index ", end_index)
        print("Candidate list ", candidate_list)

        current_node_id = self.edge_node_map[curr_edge_id]

        # for node_id in candidate_list:
        for camera in cameras_in_path_list:

            node_id_lat_long = self.node_to_lat_long_json[current_node_id[1]]
            camera_lat_long_pair = self.node_to_lat_long_json[camera]
            distance = TestCameraPosistion.distance_in_meters(node_id_lat_long, camera_lat_long_pair)
            if distance < (2 * 28):

                node_id_index = custom_node_id_list.index(current_node_id[0])
                camera_index = custom_node_id_list.index(camera)

                if node_id_index <= camera_index:
                    print("Sending message to traffic signal ", str(camera), " the distance is ", distance)
                    break
                else:
                    print(
                        "******************though distance is less, vehicle has already passed the signal******************")

    def reset_traffic_lights(self, end_index):
        """

        :param end_index:
        :return:
        """
        print("reset_traffic_lights Start index 0, end index ", end_index)

        if end_index == -1:
            logging.debug("reset_traffic_lights Nothing to reset")
            return

        start_index = end_index - 4
        if start_index < 0:
            start_index = 0

        candidate_edge_list = self.custom_edge_list[start_index:end_index]
        nodes_to_be_checked = []

        for edge in candidate_edge_list:
            node_tuple = self.edge_node_map[edge]
            nodes_to_be_checked.append(node_tuple[0])
            nodes_to_be_checked.append(node_tuple[1])

        traffic_light_to_be_reset = []

        all_traffic_id_list = self.get_traffic_lights_between_src_dest()

        for node_id in nodes_to_be_checked:
            for traffic_id in all_traffic_id_list:
                if node_id == traffic_id:
                    traffic_light_to_be_reset.append(traffic_id)

        for traffic_id in traffic_light_to_be_reset:
            self.lock.acquire()
            curr_state = traci.trafficlight.getRedYellowGreenState(traffic_id)
            logging.debug("Current state is " + str(curr_state))
            traci.trafficlight.setPhaseDuration(traffic_id, 100)
            self.lock.release()

    def set_traffic_lights(self, start_index, end_index):
        """

        :param start_index: current edge id index
        :param end_index: the edge id upto which traffic lights should be turned on
        :return:
        """

        print("set_traffic_lights Start index ", start_index, " end index ", end_index)

        if end_index >= len(self.custom_edge_list):
            logging.debug("set_traffic_lights The end index is more than the edges")
            end_index = len(self.custom_edge_list) - 1

        candidate_edge_list = self.custom_edge_list[start_index:end_index]

        if len(candidate_edge_list) == 0:
            logging.debug("set_traffic_lights nothing to set")
            return

        nodes_to_be_checked = []

        for edge_id in candidate_edge_list:
            node_tuple = self.edge_node_map[edge_id]
            nodes_to_be_checked.append(node_tuple[0])
            nodes_to_be_checked.append(node_tuple[1])

        traffic_light_to_be_set = []

        all_traffic_id_list = self.get_traffic_lights_between_src_dest()

        for node_id in nodes_to_be_checked:
            for traffic_id in all_traffic_id_list:
                if node_id == traffic_id:
                    traffic_light_to_be_set.append(traffic_id)

        for traffic_id in traffic_light_to_be_set:
            self.lock.acquire()
            curr_state = traci.trafficlight.getRedYellowGreenState(traffic_id)
            state_length = len(curr_state)
            new_state = 'G' * state_length
            traci.trafficlight.setRedYellowGreenState(traffic_id, new_state)
            self.lock.release()

    def set_reset_traffic_lights(self):
        """

        :return:
        """
        logging.debug("In set reset traffic lights ")
        if self.ambulance_id == "-1":
            return

        try:
            self.lock.acquire()
            logging.debug("The vehicle id is " + self.ambulance_id)
            edge_id = traci.vehicle.getRoadID(self.ambulance_id)

            traffic_id_seq = traci.vehicle.getNextTLS(self.ambulance_id)
            logging.debug("The edge/road id is " + str(edge_id))
            print("(Stats for fun) The traffic light sequence is ", traffic_id_seq)
            self.lock.release()

            edge_index = -1
            count = 0
            for custom_edge_id in self.custom_edge_list:

                if custom_edge_id == edge_id:
                    edge_index = count
                    break
                count = count + 1

            if edge_index == -1:
                print("Edge " + str(edge_id) + " not found in custom edge list ")
                return

            self.set_traffic_lights(edge_index, edge_index + 4)
            self.reset_traffic_lights(edge_index - 1)

        except Exception as e:

            print("The exception is ", e)

    def run(self):
        """
        This should be run on a separate thread
        :return:
        """
        logging.debug("Starting the simulation..")
        try:
            step = 0
            while True:
                self.lock.acquire()
                traci.simulationStep()  # this is an important step
                self.lock.release()

                logging.debug("simulation step " + str(step))

                # self.set_reset_traffic_lights()
                self.get_next_camera()

                step = step + 1  # this is an important step

                time.sleep(1)
        except Exception as e:

            logging.debug("Exception in start simulation method " + str(e))

    def stop(self):
        """
        stop the simulation
        :return:
        """
        logging.debug("Request to stop simulation")
        traci.close(False)  # important
        return "Sumo stopped"
