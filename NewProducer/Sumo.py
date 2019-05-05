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
        self.sumo_cmd = [self.sumo_binary, "-c", "testconfig.sumocfg"]
        self.lock = threading.Lock()
        self.edge_list = []  # not used, remove after review
        self.ambulance_id = ""
        self.custom_edge_list = []
        self.custom_locations = {}

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

        # self.lock.acquire()
        # vehicle_id_list = traci.vehicle.getIDList()
        # self.lock.release()
        # logging.debug("The number of vehicles are " + str(len(vehicle_id_list)))
        #
        # if vehicle_id_list is not None:
        #     ambulance_id = vehicle_id_list[0]  # this I will have to remove
        #     self.ambulance_id = ambulance_id
        #     logging.debug("Set the ambulance id " + str(self.ambulance_id))

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

    def get_traffic_lights(self):
        """

        :return:
        """

        # obtain all traffic lights' ids
        self.lock.acquire()
        traffic_lights_list = traci.trafficlight.getIDList()
        traffic_lights_count = traci.trafficlight.getIDCount()
        self.lock.release()

        # for tl in traffic_lights_list:
        tl = "343594553"
        # obtain the lanes which are controlled by a particular traffic ID
        self.lock.acquire()
        list_lanes = traci.trafficlight.getControlledLanes(tl)
        color = traci.trafficlight.getRedYellowGreenState(tl)
        phase = traci.trafficlight.getPhase(tl)
        phase_duration = traci.trafficlight.getPhaseDuration(tl)
        phase_name = traci.trafficlight.getPhaseName(tl)
        next_switch = traci.trafficlight.getNextSwitch(tl)
        self.lock.release()

        print("The lanes which are controlled by traffic light ", tl, " are ", list_lanes)
        logging.debug("The light color is " + str(color) + " the next switch is " + str(next_switch))
        logging.debug("The phase is " + str(phase) + " the phase name is " + str(
            phase_name) + " the phase duration is " + str(phase_duration))

        print("Before setting traffic light ", color)
        traci.trafficlight.setRedYellowGreenState(tl, 'GgGg')
        color = traci.trafficlight.getRedYellowGreenState(tl)
        print("After setting traffic light ", color)

        print("The counts are ", traffic_lights_count, " the actual count ", len(traffic_lights_list))

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

        custom_edge_list, locations = gen_shortest_path.compute_shortest_path(source, dest, self.graph)
        self.custom_edge_list = custom_edge_list
        self.custom_locations = locations

        logging.debug("The first lane " + str(custom_edge_list[0] + "_0"))

        self.lock.acquire()
        traci.route.add(new_route_id, custom_edge_list)
        traci.vehicle.add(vehicle_id, new_route_id)
        traci.vehicle.moveTo(vehicle_id, custom_edge_list[0] + "_0", pos=1)  # lane 0 of first edge
        self.lock.release()

        logging.debug("Added a vehicle successfully")
        return "Added a vehicle successfully"

    def get_custom_locations(self):
        """
        This method returns the custom locations, which contain lat lon pair for each edges
        :return: This method returns the custom locations
        """
        return self.custom_locations

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
        self.lock.release()

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

                step = step + 1  # this is an important step

                # if step > 20000:
                time.sleep(1)
        except:

            logging.debug("Exception in start simulation method")

    def stop(self):
        """
        stop the simulation
        :return:
        """
        logging.debug("Request to stop simulation")
        traci.close()
        return "Sumo stopped"
