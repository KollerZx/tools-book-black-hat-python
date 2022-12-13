""" 
Scripts para pag 25 - Black Hat Python
"""

import socket

import random


def getTemp():
    temp = random.uniform(60.0, 62.0)
    return temp

serverAddress = ("127.0.0.1", 7070)


tempSensorSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

temperature = getTemp()

tempString  = "%.2f"%temperature

tempSensorSocket.sendto(tempString.encode(), ("127.0.0.1",7070))

response = tempSensorSocket.recv(1024)

print(response)