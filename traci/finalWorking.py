from __future__ import print_function
import paho.mqtt.client as mqtt
import socket
import json
import os, sys
import traci
import time

############################ SUMO INIT COMMANDS & PATH ############################
sumoBinary = "/home/dreamlab/sumo/bin/sumo"
sumoCmd = [sumoBinary, "-c", "testconfig.sumocfg"]
####################################################################################

############################ SET SUMO HOME ENVIRONMENT ############################
if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
else:
        sys.exit("please declare environment variable 'SUMO_HOME'")

####################################################################################        

############################ SET THE BROKER ADDRESS & PORT ############################
broker_address="10.24.24.2" 
tTransport = "websockets"
tPort = 10001        
####################################################################################

############################## ON PUBLISH CALLBACK #################################
def on_publish_edge(client,userdata,result):
        print("Edge Data Published..")

####################################################################################

############################## ON PUBLISH CALLBACK #################################
def on_publish_vertex(client,userdata,result):
        print("Vertex Data Published..")

####################################################################################

############################ MQTT CLIENT AND TOPIC ############################
clientEdge = mqtt.Client("P2", transport=tTransport)
clientEdge.on_publish = on_publish_edge
clientEdge.connect(broker_address, port=tPort, keepalive=60, bind_address="")

clientVertex = mqtt.Client("P3", transport=tTransport)
clientVertex.on_publish = on_publish_vertex
clientVertex.connect(broker_address, port=tPort, keepalive=60, bind_address="")

edgeTopic = "trafficstats/"
vehicleTopic = "vechiclestats/"
####################################################################################

############################ SEND VECHICLE PAYLOAD ############################
def sendVehiclePayload(payload):
        print("the vehicle payload is ",payload)
####################################################################################

############################ PREPARE VEHICLE PAYLOAD ############################
def prepareVehiclePayload():
        myDict = {}

        vehicleIdList = traci.vehicle.getIDList()

        randVehicleId = ""
        if(vehicleIdList!=None):
                randVehicleId = vehicleIdList[0] #random vehicle Id

        speed = traci.vehicle.getSpeed(randVehicleId)
        position = traci.vehicle.getPosition(randVehicleId)

        myDict["vehicleid"] = str(randVehicleId)
        myDict["speed"] = speed
        myDict["position"] = position

        payloadJson = json.dumps(myDict)

        return payloadJson

####################################################################################

############################ SEND EDGE PAYLOAD ############################
def sendEdgePayload(payload):
        print("the edge payload is ",payload)
####################################################################################

############################ PREPARE EDGE PAYLOAD ############################
def prepareEdgePayload(edgeList):

	myDict = {}

        numVehiclesList = []
        for edge in edgeList:
                numVehicles = traci.edge.getLastStepVehicleNumber(edge)
                numVehiclesList.append(numVehicles)

        myDict["edges"] = numVehiclesList

        #This can be a point of concern
        payloadJson = json.dumps(myDict)

        return payloadJson
####################################################################################



############################## SUMO INIT ###################################
traci.start(sumoCmd)
step = 0

edgeList = traci.edge.getIDList() #returns a list of edgeId as strings
print("The number of edges are ",len(edgeList))

while step<12:

        traci.simulationStep() # this is an important step
        print("Sending statistics...")

        if(step%5==0):
                print("Edge case : Step Number ",step)
                payload = prepareEdgePayload(edgeList)
                #sendEdgePayload(payload)
                clientEdge.publish(edgeTopic,payload)
                #print("Going to sleep..5s")

        if(step%2==0):
                print("Vehicle case : Step Number ",step)
                payload = prepareVehiclePayload()
                #sendVehiclePayload(payload)
                clientVertex.publish(vehicleTopic,payload)
                #print("Going to sleep..1s")

        time.sleep(1)
        step = step + 1
#################################################################################### 