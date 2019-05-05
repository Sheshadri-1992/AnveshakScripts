import numpy as np
import random as rand
import time
import json
import logging

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s', )
camera_lat_long = []

with open("./InputFiles/cameras.json") as json_file:
    cameras = json.load(json_file)


def calculate_within_radius(vehicle_pos_x, vehicle_pos_y):
    logging.debug("received positions are " + str(vehicle_pos_x) + " , " + str(vehicle_pos_y))

    camera_id_list = []
    node_id_list = []
    lat_list = []
    long_list = []

    for item in cameras:
        camera_id_list.append(item[0])
        node_id_list.append(item[1])
        lat_list.append(float(item[2]))
        long_list.append(float(item[3]))
        # print(item[2], item[3])

    vehicle_pos = np.array((float(vehicle_pos_x), float(vehicle_pos_y)))
    # generate random lat long for cameras
    for i in range(0, 4000):
        camera_lat_long.append(np.array((lat_list[i], long_list[i])))

    diameter = 0.0015  # Not sure what this value should be. This will have to be experimentally inferred.
    # Calculate Euclidean Distance

    num_cameras = 0
    start_time = time.time()
    for camera_pos in camera_lat_long:
        # print("camera position ", camera_pos, vehicle_pos)
        dist = np.linalg.norm(vehicle_pos - camera_pos)
        # print dist
        if dist < diameter:
            num_cameras = num_cameras + 1
            print("the vehicle is coming close ", num_cameras)  # print(dist)

    print('Total time', time.time() - start_time," num cameras ",num_cameras)

# calculate_within_radius(0.0,0.0)
