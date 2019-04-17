from __future__ import print_function
import paho.mqtt.client as mqtt
import psutil
import os
import socket
import json
import time

def on_message(client, userdata, message):
    time.sleep(1)
    print("received message =",str(message.payload.decode("utf-8")))

broker_address="10.24.24.2" 

# Set the transport mode to WebSockets.
tTransport = "websockets"
tPort = 9001

client = mqtt.Client("P2", transport=tTransport)
client.on_message=on_message

client.connect(broker_address, port=tPort, keepalive=60, bind_address="")
client.loop_start()
client.subscribe("resource/")
time.sleep(4)
# client.disconnect()
# client.loop_stop()