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
    sumo_binary = "/home/dreamlab/sumo/bin/sumo"
    sumo_cmd = None
    lock = None
    edge_list = None
    ambulance_id = None

    def __init__(self):

        super(Sumo, self).__init__()
        logging.debug("Initialised sumo path")
        self.sumo_binary = "/home/dreamlab/sumo/bin/sumo"
        self.sumo_cmd = [self.sumo_binary, "-c", "testconfig.sumocfg"]
        self.lock = threading.Lock()

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

    def return_ambulance_id(self, vehicle_id):
        """
        Returns the ambulance Id, this may not be needed
        :return:
        """

        self.ambulance_id = vehicle_id

        self.lock.acquire()
        vehicle_id_list = traci.vehicle.getIDList()
        self.lock.release()

        ambulance_id = ""
        if vehicle_id_list is not None:
            ambulance_id = vehicle_id_list[0]

        return ambulance_id

    def get_vehicle_stats(self):
        """
        Make a traci call and return the ambulance speed and position
        :return: the ambulance speed and position
        """
        ambulance_dict = {}

        try:

            self.lock.acquire()
            speed = traci.vehicle.getSpeed(self.ambulance_id)
            self.lock.release()

            self.lock.acquire()
            position = traci.vehicle.getPosition(self.ambulance_id)
            self.lock.release()

            ambulance_dict["vehicleid"] = str(self.ambulance_id)
            ambulance_dict["speed"] = speed
            ambulance_dict["position"] = position

            logging.debug("The dictionary is " + str(ambulance_dict))

        except:

            logging.debug("Exception in vehicle stats method")

        return ambulance_dict

    def return_traffic_density(self, arg_edge_list):
        """
        makes traci call to each edge passed
        :param arg_edge_list: the edge list for which vehicle density is needed
        :return: a dictionary with key as vehicleid,
        """
        edge_dict = {}

        try:

            for edge in arg_edge_list:
                self.lock.acquire()
                num_vehicles = traci.edge.getLastStepVehicleNumber(edge)
                self.lock.release()
                edge_dict[edge] = num_vehicles
        except:

            logging.debug("Exception in return traffic density method")

        return edge_dict

    def run(self):
        """
        This should be run on a separate thread
        :return:
        """

        try:
            step = 0
            while step < 1000:
                self.lock.acquire()
                traci.simulationStep()  # this is an important step
                self.lock.release()

                step = step + 1 # this is an important step
                time.sleep(1)
        except:

            logging.debug("Exception in start simulation method")
