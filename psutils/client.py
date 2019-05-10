from __future__ import print_function
import paho.mqtt.client as mqtt
import psutil
import os
import socket
import json
import time

def on_connect(client, userdata, rc):
	print("Connected with result code "+str(rc))

def on_subscribe(client, userdata, message):

	print("here")

def on_message(client, userdata, message):
    
    print("received message =",str(message.payload.decode("utf-8")))


# Set the transport mode to WebSockets.
broker_address="10.24.24.2"
tTransport = "websockets"
tPort = 10001

print("I am here ")
client = mqtt.Client("P5",protocol=mqtt.MQTTv31, transport=tTransport)
client.username_pw_set(username="dreamlabanveshak", password="dream119")
client.on_message=on_message

client.connect(broker_address, port=tPort, keepalive=60, bind_address="")

client.subscribe("medium")
client.on_subscribe = on_subscribe
client.loop_forever()
