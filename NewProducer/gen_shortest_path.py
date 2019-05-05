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

    :param origin:
    :param dest:
    :param graph:
    :return:
    """
    # origin = '249072983'
    # dest = '448116544'

    print("The origin is ",origin," destination is ",dest)
    path = nx.shortest_path(graph, origin, dest, weight='weight')

    # get edges

    edges = [-1]

    for i in range(len(path) - 1):
        e = graph[path[i]][path[i + 1]]
        if type(e) is list:
            for j in e:
                if edges[-1] != j.keys()[0]:
                    edges.append(j.keys()[0])
        else:
            if edges[-1] != e.keys()[0]:
                edges.append(e.keys()[0])

    edges = edges[1:]

    print("The edge in the shortest path ", edges)
    return edges
