""" 
Scripts para pag 25 - Black Hat Python
"""


import socket
import datetime
target_host = "127.0.0.1"
target_port = 7070

datagramSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
datagramSocket.bind((target_host, target_port))

while(True):
  tempVal, sourceAddress = datagramSocket.recvfrom(128)

  print("Temperature at %s is %s"%(sourceAddress, tempVal.decode()))

  response = "Received at: %s"%datetime.datetime.now()

  datagramSocket.sendto(response.encode(), sourceAddress)
  
  
  