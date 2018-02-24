import threading
import socket
from queue import Queue
from digi.xbee.devices import XBeeDevice

PRIVATE = '10.200.180.8' # TODO change to self ip
PORT = 5000
COM = 'COM8'
BAUD_RATE = 9600

packetQueue=Queue()
udp_socket = None
cord = None

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((PRIVATE,PORT))

cord = XBeeDevice(COM, BAUD_RATE)
try:
	cord.open()
except:
	pass

def initConnections():# open zigbee coordinator and open wifi socket. untested
	global udp_socket
	global cord
	udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	udp_socket.bind((PRIVATE,PORT))
	cord = XBeeDevice(COM, BAUD_RATE)
	try:
		cord.open()
	except:
		pass

def ProcessPacketQueue(): # get packet from queue
	while True:
		packet = packetQueue.get()
		parsePacket(packet) # send to parsing module
		packetQueue.task_done()

def WF_recPackets(): # get incomming wifi packets
	global udp_socket
	while True:
		data = udp_socket.recv(512) # might set to 84 to avoid bias
		packetQueue.put(data)

def ZB_recPackets(): # get incomming zigbee packets. maximum 84 bytes
	global cord
	try:
		while True:
			xbee_message = cord.read_data()
			if xbee_message is not None:

				packetQueue.put(bytes(xbee_message.data))
	except:
		pass

def parsePacket(data): #for demo 
	print(len(data)," ",data)


t1 = threading.Thread(target = ProcessPacketQueue)
t1.daemon = True
t1.start()

t2 = threading.Thread(target = ZB_recPackets)
t2.daemon = True
t2.start()

t3 = threading.Thread(target = WF_recPackets)
t3.daemon = True
t3.start()
