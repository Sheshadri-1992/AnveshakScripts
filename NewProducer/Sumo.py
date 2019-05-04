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

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s', )


class Sumo(threading.Thread):
    # sumo_binary = "/home/dreamlab/sumo/bin/sumo"
    sumo_cmd = None
    lock = None
    edge_list = None
    ambulance_id = None

    def __init__(self):

        super(Sumo, self).__init__()
        logging.debug("Initialised sumo path")
        # self.sumo_binary = "/home/dreamlab/sumo/bin/sumo"
        self.sumo_binary = "/usr/bin/sumo/"  # local sumo path
        self.sumo_cmd = [self.sumo_binary, "-c", "testconfig.sumocfg"]
        self.lock = threading.Lock()
        self.edge_list = []
        self.ambulance_id = ""

        # start the simulation here
        traci.start(self.sumo_cmd)

        if 'SUMO_HOME' in os.environ:
            tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
            sys.path.append(tools)
        else:
            sys.exit("please declare environment variable 'SUMO_HOME'")

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
        Returns the ambulance Id, this may not be needed
        :return:
        """
        logging.debug("Got the ambulance id " + vehicle_id)
        self.ambulance_id = vehicle_id

        self.lock.acquire()
        vehicle_id_list = traci.vehicle.getIDList()
        self.lock.release()
        logging.debug("The number of vehicles are " + str(len(vehicle_id_list)))

        ambulance_id = ""
        if vehicle_id_list != None:
            ambulance_id = vehicle_id_list[0]
            self.ambulance_id = ambulance_id
            logging.debug("Set the ambulance id " + str(self.ambulance_id))

        return ambulance_id

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

            ambulance_dict["vehicleid"] = str(self.ambulance_id)
            ambulance_dict["speed"] = speed
            ambulance_dict["position"] = geo_co_ord

            logging.debug("The dictionary is " + str(ambulance_dict))

        except:

            logging.debug("Exception in vehicle stats method")

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

        # obtain the lanes which are controlled by a particular traffic ID
        self.lock.acquire()
        list_lanes = traci.trafficlight.getControlledLanes(traffic_lights_list[0])
        phase = traci.getPhase(traffic_lights_list[0])
        self.lock.release()
        print("The lanes which are controlled by traffic light ", traffic_lights_list[0], " are ", list_lanes)
        logging.debug("The phase is "+str(phase))

    def return_traffic_density(self, arg_edge_list):
        """
        makes traci call to each edge passed
        :param arg_edge_list: the edge list for which vehicle density is needed
        :return: a dictionary with key as vehicleid,
        """
        edge_dict = {}

        self.get_traffic_lights()

        if arg_edge_list is None:
            logging.debug("Empty list sent")
            return edge_dict

        try:

            for edge in arg_edge_list:
                self.lock.acquire()
                num_vehicles = traci.edge.getLastStepVehicleNumber(edge)
                self.lock.release()
                edge_dict[edge] = num_vehicles
        except:

            logging.debug("Exception in return traffic density method")

        return edge_dict

    def add_new_vehicle(self, vehicle_id, edge_id_list):
        """
        This method needs to add a vehicle and a set of routes it will follow
        The vehicle is an ambulance, the new route is the set of sumo edges
        :param vehicle_id: id of the ambulance
        :param edge_id: the road to which vehicle
        :return:
        """

        self.lock.acquire()
        all_routes = traci.route.getIDList()
        self.lock.release()

        logging.debug("There are " + str(len(all_routes)) + " number of routes")
        random_route_id = all_routes[0]
        logging.debug("The random route that we are going to assign is " + str(random_route_id))

        # adding a vehicle in the new route
        self.lock.acquire()
        traci.vehicle.add(vehicle_id, random_route_id)
        self.lock.release()

        logging.debug("Added a vehicle successfully")
        return "Added a vehicle successfully"

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
