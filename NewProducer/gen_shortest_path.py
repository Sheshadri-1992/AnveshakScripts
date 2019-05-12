from collections import OrderedDict
import networkx as nx
import types
from networkx.readwrite import json_graph
import json
import pickle
import xmltodict
import random
import sumolib


def compute_shortest_path(origin, dest, graph):
    """

    :param origin: Ambulance source position
    :param dest: Hospital destination position
    :param graph: The network graph
    :return: the shortest path (set of edges) and locations dict which has lat long for the shortest path
    """
    # origin = '3756191723'
    # dest = '3370075981'

    print("The origin is ", origin, " destination is ", dest)
    path = nx.shortest_path(graph, origin, dest, weight='weight')  # LIST OF NODES

    # get edges

    edges = [-1]
    edge_node_map = {}

    locations = {}

    for i in range(len(path) - 1):
        e = graph[path[i]][path[i + 1]]
        if type(e) is list:
            for j in e:
                id = j.keys()[0]
                edge_node_map[id] = (path[i], path[i + 1])  # newly added
                if edges[-1] != id:
                    edges.append(id)
                    locations[id] = j[id]['lanes'][0]['shape']
        else:
            id = e.keys()[0]
            edge_node_map[id] = (path[i], path[i + 1]) # newly added
            if edges[-1] != id:
                edges.append(id)
                locations[id] = e[id]['lanes'][0]['shape']

    edges = edges[1:]

    return edges, locations, edge_node_map, path


def get_shortest_path_traffic(graph, traffic_lights, source, destination, foresight):
    """

    :return:
    """

    # source = '3756191723'
    # destination = '3370075981'
    path = nx.shortest_path(graph, source, destination, weight='weight')
    lights = []
    if set(path) & set(traffic_lights):
        s = set(path) & set(traffic_lights)
        for node in path:
            if node in s:
                lights.append(node)

    if foresight == -1:
        return lights

    print("total number of traffic lights are ",len(lights))

    return set(lights[:foresight])
