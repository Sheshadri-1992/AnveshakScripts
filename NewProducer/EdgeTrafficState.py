import sys, os
import logging

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s', )


class EdgeStateInfo:

    def __init__(self):
        self.edge_list = []
        self.traffic_id_list = []
        self.traffic_phase_dict = {}  # store the previous edge phase
        self.traffic_id_lane_dict = {}  # traffic id to lanes
        self.traffic_id_index_dict = {}
        self.edge_lane_dict = {} # edge to number of lanes
        self.edge_traffic_dict = {} # edge to traffic light id
        self.set_list = []  # This is to set the traffic lights to green
        self.reset_list = []  # This is to reset the traffic lights to green
        self.index = 0

    def set_traffic_id_list(self, traffic_id_list):
        """

        :param traffic_id_list:
        :return:
        """
        self.traffic_id_list = traffic_id_list

    def get_traffic_id_list(self):
        """

        :return:
        """
        return self.traffic_id_list

    def set_traffic_id_index_dict(self, traffic_id_index_dict):
        """

        :return:
        """
        self.traffic_id_index_dict = traffic_id_index_dict

    def get_traffic_id_index_dict(self):
        """

        :return:
        """
        return self.traffic_id_index_dict

    def set_edge_traffic_dict(self, edge_traffic_dict):
        """

        :return:
        """
        self.edge_traffic_dict = edge_traffic_dict

    def get_edge_traffic_dict(self):
        """

        :return:
        """
        return self.edge_traffic_dict

    def set_edge_list(self, custom_edge_list):
        """

        :param custom_edge_list: the custom path of the new route added to the vehicle
        :return: nothing
        """

        if custom_edge_list is None:
            logging.debug("The custom edge sent is Null")
            return

        self.edge_list = custom_edge_list
        self.set_list = [0] * len(custom_edge_list)
        self.reset_list = [0] * len(custom_edge_list)

    def set_traffic_phase_dict(self, traffic_phase_dict):
        """

        :param traffic_phase_dict: In this dict, the key is traffic light id, value is phase
        :return: nothing
        """

        if traffic_phase_dict is None:
            logging.debug("Traffic phase dict is Null")
            return

        self.traffic_phase_dict = traffic_phase_dict

    def get_traffic_phase_dict(self):
        """

        :return:
        """
        return self.traffic_phase_dict

    def set_traffic_id_lane_dict(self, traffic_id_lane_dict):
        """

        :param traffic_id_lane_dict: key is traffic id, key is list of lanes
        :return: nothing
        """
        if traffic_id_lane_dict is None:
            logging.debug("traffic_id_lane_dict is Null")
            return

        self.traffic_id_lane_dict = traffic_id_lane_dict

    def get_traffic_id_lane_dict(self):
        """

        :return:
        """
        return self.traffic_id_lane_dict

    def set_edge_lane_dict(self, edge_lane_dict):
        """

        :param edge_lane_dict:
        :return:
        """
        if edge_lane_dict is None:
            logging.debug("edge_lane_dict is Null")
            return

        self.edge_lane_dict = edge_lane_dict

    def get_edge_lane_dict(self):
        """

        :return:
        """
        return self.edge_lane_dict

    def set_index(self, number):
        """

        :param number: the new index value
        :return:
        """
        self.index = number

    def get_index(self):
        """

        :return: index
        """
        return self.index
