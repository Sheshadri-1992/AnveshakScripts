import zmq

# ZeroMQ Context
context = zmq.Context()

# Define the socket using the "Context"
sock = context.socket(zmq.REP)
sock.bind("tcp://0.0.0.0:8000")

# Run a simple "Echo" server
while True:
    message = sock.recv()
    sock.send("Echo: " + message)
    print "Echo: " + message