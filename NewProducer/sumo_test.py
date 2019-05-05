import traci
import random

sumo_binary = "/usr/local/bin/sumo"
sumo_cmd = [sumo_binary, "-c", "/home/dreamlab/sheshadri/SumoProducer/testconfig.sumocfg"]

traci.start(sumo_cmd)

print("SUMO Started!")

# Add vehicle

vehicle_id = str(random.randint(50000, 100000))
route_id = str(random.randint(50000, 100000))
custom_edge_list = ["45250008#7", "-45250008#7", "-45250008#6", "-45250008#5", "-45250008#4", "-45250008#3",
                       "-45250008#2", "-45250008#1", "-45250008#0", "45250014#0", "45250533#0", "45250533#1",
                       "45250533#2", "45250533#3", "-46951252#1", "-46951252#0", "-35901381#10", "-35901381#9",
                       "-35901381#8", "-35901381#7", "-35901381#6", "-35901381#5", "-35901381#4", "-35901381#3",
                       "-35901381#2", "-35901381#1", "40151526#2", "-215412812", "-345411282#1", "-345411282#0",
                       "-404335353", "383028788#12", "383028788#13", "379878516#0", "379878516#1", "383029332",
                       "392213813", "383031432#0", "383031432#1", "-470223620", "470223615#0", "470223615#1",
                       "470223615#2", "470223615#3", "236578402", "-452366265#19", "-452366265#18", "-452366265#17",
                       "-452366265#16", "-236531497#1", "-236531497#0", "46918817", "-42013627#7", "-42013627#6",
                       "-42013627#5", "46918821"]

traci.route.add(route_id, custom_edge_list)
print("Route Added: " + route_id)
traci.vehicle.add(vehicle_id, route_id)
print("Vehicle Added: " + vehicle_id)
traci.vehicle.moveTo(vehicle_id, "45250008#7_0", pos=1.0)
print("Vehicle Moved: " + vehicle_id)

# Get vehicle position

position = traci.vehicle.getPosition(vehicle_id)

print("Position: ", position)

# Convert Geo

print(traci.simulation.convertGeo(position[0], position[1]))

print(traci.simulation.convertGeo(x=50450.7527098387, y=22602.868908196364))

# Exit

traci.close()

