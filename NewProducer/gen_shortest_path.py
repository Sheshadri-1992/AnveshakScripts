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
    origin = '249072983'
    dest = '448116544'

    print("The origin is ", origin, " destination is ", dest)
    path = nx.shortest_path(graph, origin, dest, weight='weight')

    # get edges

    edges = [-1]

    locations = {}

    for i in range(len(path) - 1):
        e = graph[path[i]][path[i + 1]]
        if type(e) is list:
            for j in e:
                id = j.keys()[0]
                if edges[-1] != id:
                    edges.append(id)
                    locations[id] = j[id]['lanes'][0]['shape']
        else:
            id = e.keys()[0]
            if edges[-1] != id:
                edges.append(id)
                locations[id] = e[id]['lanes'][0]['shape']

    edges = edges[1:]

    return edges, locations
