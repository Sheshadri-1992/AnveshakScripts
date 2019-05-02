import json

def create_set():

    with open("./InputFiles/osm_sumo.json") as json_file:
            data_dict = json.load(json_file)

    edge_set = set([])
    counter = 0
    for edge in data_dict:

        lanes = data_dict[edge]
        for lane in lanes:
            counter = counter + 1
            edge_set.add(str(lane))

    print("done..",len(edge_set))
    print("Count is ",counter)

create_set()