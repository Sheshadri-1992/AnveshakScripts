	#!/usr/bin/python
import sys
import yaml

#for edge and fog yamls use "sample.yaml"
#for services use service.yaml
fileName = "service.yaml"
COMMAND = "while true; do sleep 30; done;"
NUM_EDGE = 100
NUM_EDGE_PER_NODE = 10
EDGE="edge"
FOG="fog"
NODE="node"
SERVICE="service"

# THIS IS FOR EDGE FOG YAML FILES #
def returnYamlMap(dataMap,devFileName,nodeFileName):

	dataMap["metadata"]["name"] = devFileName
	dataMap["spec"]["selector"]["matchLabels"]["k8s-app"] = devFileName
	dataMap["spec"]["template"]["metadata"]["labels"]["k8s-app"] = devFileName
	dataMap["spec"]["template"]["spec"]["hostname"]=devFileName
	dataMap["spec"]["template"]["spec"]["nodeSelector"]["name"] = nodeFileName	

	return dataMap

def generate_yaml_files():

	with open(fileName) as f:
	    dataMap = yaml.safe_load(f)

	modCounter =0
	nodeIndex = 0

	for i in range(0,101):	

		if(modCounter==NUM_EDGE_PER_NODE):
			modCounter = 0
			nodeIndex = nodeIndex + 1

			fogFileName = FOG+str(nodeIndex)
			nodeFileName = NODE+str(nodeIndex)

			dataMap = returnYamlMap(dataMap,fogFileName,nodeFileName)
			with open('EdgeFogYamlFiles/'+fogFileName+'.yaml', "w") as f:
				yaml.dump(dataMap, f,default_flow_style=False)


		edgeFileName = EDGE+str(i+1)
		nodeFileName = NODE+str(nodeIndex+1)

		dataMap = returnYamlMap(dataMap,edgeFileName,nodeFileName)
		with open('EdgeFogYamlFiles/'+edgeFileName+'.yaml', "w") as f:
			yaml.dump(dataMap, f,default_flow_style=False)

		modCounter = modCounter + 1

	print dataMap   

# THIS IS FOR SERVICE YAML FILES #
def returnYamlServiceMap(dataMap,deviceName):

	dataMap["metadata"]["name"] = deviceName
	dataMap["spec"]["selector"]["k8s-app"] = deviceName

	return dataMap

def generate_service_yaml_files():
	print "service yaml"
	with open(fileName) as f:
	    dataMap = yaml.safe_load(f)

	modCounter =0
	nodeIndex = 0

	for i in range(0,101):	

		if(modCounter==NUM_EDGE_PER_NODE):
			modCounter = 0
			nodeIndex = nodeIndex + 1

			fogFileName = SERVICE+"_"+FOG+str(nodeIndex)
			nodeFileName = SERVICE+"_"+NODE+str(nodeIndex)

			dataMap = returnYamlServiceMap(dataMap,FOG+str(nodeIndex))
			with open('ServiceYamlFiles/'+fogFileName+'.yaml', "w") as f:
				yaml.dump(dataMap, f,default_flow_style=False)


		edgeFileName = SERVICE+"_"+EDGE+str(i+1)
		nodeFileName = SERVICE+"_"+NODE+str(nodeIndex+1)

		dataMap = returnYamlServiceMap(dataMap,EDGE+str(i+1))
		with open('ServiceYamlFiles/'+edgeFileName+'.yaml', "w") as f:
			yaml.dump(dataMap, f,default_flow_style=False)

		modCounter = modCounter + 1

	print dataMap	

# generate_yaml_files()
generate_service_yaml_files()