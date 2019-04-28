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

############################ GLOBAL VARIABLE ######################################
lock = threading.Lock()
clientEdge=None
clientVertex=None
###################################################################################

############################ SET THE BROKER ADDRESS & PORT ############################
broker_address="10.24.24.2" 
tTransport = "websockets"
tPort = 10001        
edgeTopic = "trafficstats/"
vehicleTopic = "vechiclestats/"
####################################################################################

############################ SUMO INIT COMMANDS & PATH ############################
sumoBinary = "/home/dreamlab/sumo/bin/sumo"
sumoCmd = [sumoBinary, "-c", "testconfig.sumocfg"]
####################################################################################

############################ SET SUMO HOME ENVIRONMENT ############################
try:

	if 'SUMO_HOME' in os.environ:
		tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
		sys.path.append(tools)
	else:
		sys.exit("please declare environment variable 'SUMO_HOME'")
except:

	print("Excpetion caught in setting environment variable")

####################################################################################        


############################## ON PUBLISH CALLBACK #################################
def on_publish_edge(client,userdata,result):
	edgeFile = open("edgefile.txt", "a+")
	edgeFile.write("edge data recevied\n")
	edgeFile.close()
	client.loop_stop()
        print("Edge Data Published..")

####################################################################################

############################## ON PUBLISH CALLBACK #################################
def on_publish_vertex(client,userdata,result):
	vertexFile = open("vertexfile.txt","a+")
	vertexFile.write("vertex data received\n")
	vertexFile.close()
	client.loop_stop()
        print("Vertex Data Published..")

####################################################################################


############################ PRINT VECHICLE PAYLOAD ############################
def printVehiclePayload(payload):
        print("the vehicle payload is ",payload)
####################################################################################


############################ PRINT EDGE PAYLOAD ############################
def printEdgePayload(payload):
        print("the edge payload is ",payload)
####################################################################################

############################ PREPARE VEHICLE PAYLOAD ############################
def prepareVehiclePayload():

	try:

		myDict = {}

		################### CRITICAL SECTION #####################
		lock.acquire()
		vehicleIdList = traci.vehicle.getIDList()
		lock.release()
		##########################################################

		randVehicleId = ""
		if(vehicleIdList!=None):
			randVehicleId = vehicleIdList[0] #random vehicle Id

		################### CRITICAL SECTION #####################
		lock.acquire()
		speed = traci.vehicle.getSpeed(randVehicleId)
		lock.release()
		##########################################################
	
		################### CRITICAL SECTION #####################
		lock.acquire()
		position = traci.vehicle.getPosition(randVehicleId)
		lock.release()
		##########################################################

		myDict["vehicleid"] = str(randVehicleId)
		myDict["speed"] = speed
		myDict["position"] = position

		payloadJson = json.dumps(myDict)

		return payloadJson

	except:
		print(traceback.format_exc())
		print("Exception caught in vehicle payload")

####################################################################################


############################ PREPARE EDGE PAYLOAD ############################
def prepareEdgePayload(edgeList):

	try:

		myDict = {}
		numVehiclesList = []

		for edge in edgeList:			
			
		################### CRITICAL SECTION #####################
			lock.acquire()
			numVehicles = traci.edge.getLastStepVehicleNumber(edge)
			lock.release()
		##########################################################
			numVehiclesList.append(numVehicles)

		myDict["edges"] = numVehiclesList

		#This can be a point of concern
		payloadJson = json.dumps(myDict)

	        return payloadJson
	except:
		print(traceback.format_exc())
		print("Exception caught in prepare edge payload")

####################################################################################

############################### SEND MESSAGE THREAD  ####################################
def sendEdgeMessage(step):

	try:
		print("Edge case : Step Number ",step)
		
		start = time.time()
		payload = prepareEdgePayload(edgeList)	
		print("Edge payload..")
		end = time.time()

		print("The time taken for edge payload ",(end-start))
		ret=clientEdge.publish(edgeTopic,payload)
		clientEdge.loop_start()

		print("The result is ",str(ret))

	except:
		print(traceback.format_exc())
		print("Exception caught in send Edge message")

	finally:
		print("finally..")

def sendVertexMessage(step):

	try :

		print("Vehicle case : Step Number ",step)

		start = time.time()
		payload = prepareVehiclePayload()
		print("Payload is ",payload)
		end = time.time()
		
		print("The time taken for vertex payload ",(end-start))
		ret = clientVertex.publish(vehicleTopic,payload)
		clientVertex.loop_start()
		
		print("The result is ",str(ret))

	except:
		print(traceback.format_exc())
		print("Excpetion caught in send vertex message")

	finally:
		print("finally..")


####################################################################################


############################## SUMO INIT ###################################
traci.start(sumoCmd)
step = 0

start = time.time()
edgeList = traci.edge.getIDList() #returns a list of edgeId as strings
end = time.time()

print("The number of edges are ",len(edgeList)," The time taken is ",(end-start))

try:

	while step<1003:

		print("Creating client connections ")

		############################ CLIENT CONNECTIONS ###############################
		clientEdge = mqtt.Client("Edge", protocol=mqtt.MQTTv31,transport=tTransport)
		clientEdge.on_publish = on_publish_edge
		clientEdge.connect(broker_address, port=tPort, keepalive=60, bind_address="")

		clientVertex = mqtt.Client("Vertex", protocol=mqtt.MQTTv31,transport=tTransport)
		clientVertex.on_publish = on_publish_vertex
		clientVertex.connect(broker_address, port=tPort, keepalive=60, bind_address="")
		###############################################################################


		############################ CRITICAL SECTION #################################
		lock.acquire()
		traci.simulationStep() # this is an important step
		lock.release()
		###############################################################################

		if(step%2==0):		
			t1 = threading.Thread(target=sendVertexMessage, args=(step,))
			t1.start()

		if(step%5==0):	                
			t2 = threading.Thread(target=sendEdgeMessage, args=(step,))
			t2.start()

		
				
		########################### INCR STEP & SLEEP #################################
		step = step + 1
		time.sleep(0.1)
		###############################################################################
		
		clientEdge.disconnect()
		clientVertex.disconnect()

		print("Disconnecting connections...")

except:

	print("Excpetion in while loop")
#################################################################################### 
