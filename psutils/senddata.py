from __future__ import print_function
import paho.mqtt.client as mqtt
import psutil
import os
import socket
import json

broker_address="10.24.24.2" 

# Set the transport mode to WebSockets.
tTransport = "websockets"
tPort = 9001

client = mqtt.Client("P1", transport=tTransport)
client.connect(broker_address, port=tPort, keepalive=60, bind_address="")


# Create the topic string.
resourceTopic = "resource/"

af_map = {
    socket.AF_INET: 'IPv4',
    socket.AF_INET6: 'IPv6',
    psutil.AF_LINK: 'MAC',
}


def fetchIpAddr():

    ipAddr = ""

    stats = psutil.net_if_stats()
    io_counters = psutil.net_io_counters(pernic=True)
    for nic, addrs in psutil.net_if_addrs().items():
        # print("%s:" % (nic))

        if(nic=="eno1"):

            for addr in addrs:
                if(af_map.get(addr.family, addr.family)=="IPv4"):                    
                    # print("    %-4s" % af_map.get(addr.family, addr.family), end="")
                    # print(" address   : %s" % addr.address)

                    ipAddr=addr.address
                    
    return ipAddr

# A method to create payload
def createPayload():

	resourceId = fetchIpAddr()
	processId = os.getpid()
	cpuPercent = psutil.cpu_percent(interval=2)
	ramPercent = psutil.virtual_memory().percent
	ramTotalMB = (psutil.virtual_memory().total)/(1024.0*1024.0)
	ramAvailableMB = psutil.virtual_memory().available/(1024.0*1024.0)
	ramUsedMB = psutil.virtual_memory().used/(1024.0*1024.0)	
	cpuCores = psutil.cpu_count()

	# build the payload string.
	payload = "resourceid="+str(resourceId)+";"+"processid="+str(processId)+";"
	payload = payload + "cpupercent=" + str(cpuPercent)+";" +"cpucores=" + str(cpuCores) + ";" +"rampercent=" + str(round(ramPercent,2)) +";" +"ramtotalmb="+str(round(ramTotalMB,2))
	payload = payload+";"+"ramavailablemb="+str(round(ramAvailableMB,2))+";"+"ramusedmb="+str(round(ramUsedMB,2))

	myDict = {}
	myDict["containerid"] = str(resourceId)
	myDict["nodeid"]=str(processId)
	myDict["cpupercent"]=str(cpuCores)
	myDict["rampercent"]=str(round(ramPercent,2))
	myDict["ramtotalmb"]=str(round(ramTotalMB,2))
	myDict["ramavailablemb"]=str(round(ramAvailableMB,2))
	myDict["ramusedmb"]=str(round(ramUsedMB,2))

	return myDict


def sendPayload():

	while True:
		
		payloadDict = createPayload()
		payloadJson = json.dumps(str(payloadDict))

		print("The payload about to be sent "+str(payloadJson))

		# attempt to publish this data to the topic.
		try:
			print("publishing..")		
			client.publish(resourceTopic, payloadJson)	
			

		except (KeyboardInterrupt):
			break
		except:
			print ("There was an error while publishing the data.")


sendPayload()