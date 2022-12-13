""" 
Script pag 24/27 - Black Hat Python
"""

import socket

target_host = "0.0.0.0"
target_port = 9999

# AF_INET -> Address IPV4 | SOCK_STREAM - > TCP Client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((target_host, target_port))

request = "ACBDEF"

client.send(request.encode())

response = client.recv(4096)

print(response.decode())