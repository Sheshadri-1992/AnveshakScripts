import os, sys
import traci
import time

sumoBinary = "/home/dreamlab/sumo/bin/sumo"
sumoCmd = [sumoBinary, "-c", "testconfig.sumocfg"]


if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
else:
        sys.exit("please declare environment variable 'SUMO_HOME'")

def sendJson():
        vehicleIdList = traci.vehicle.getIDList()

        randVehicleId = ""
        if(vehicleIdList!=None):
                randVehicleId = vehicleIdList[0]

        maxSpeed = traci.vehicle.getSpeed(randVehicleId)
        position = traci.vehicle.getPosition(randVehicleId)

        print "The (vehId, maxSpeed, position) = ",randVehicleId," , ",maxSpeed," , ",position

        edgeList = traci.edge.getIDList() #returns a list of strings
        for edge in edgeList:
                numVehicles = traci.edge.getLastStepVehicleNumber(edge)

                print "(EdgeId, numVehciles) = ",edge,numVehicles


traci.start(sumoCmd)
step = 0

while step<1000:
        
        traci.simulationStep() # this is an important step
        print "Sending statistics..."
        sendJson()
        time.sleep(1)
        step = step + 1