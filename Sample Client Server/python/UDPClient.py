#coding: utf-8
from socket import *

#Define connection (socket) parameters
#Address + Port no
#Server would be running on the same host as Client
serverName = 'localhost'

#change this port number if required
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_DGRAM)
#This line creates the client’s socket. The first parameter indicates the address family; in particular,AF_INET indicates that the underlying network is using IPv4.The second parameter indicates that the socket is of type SOCK_DGRAM,which means it is a UDP socket (rather than a TCP socket, where we use SOCK_STREAM).

message = input("Input lowercase sentence:")
#input() is a built-in function in Python. When this command is executed, the user at the client is prompted with the words “Input lowercase sentence:” The user then uses the keyboard to input a line, which is put into the variable sentence. Now that we have a socket and a message, we will want to send the message through the socket to the destination host.

clientSocket.sendto(message.encode('utf-8'),(serverName, serverPort))
# Note the difference between UDP sendto() and TCP send() calls. In TCP we do not need to attach the destination address to the packet, while in UDP we explicilty specify the destination address + Port No for each message

modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
# Note the difference between UDP recvfrom() and TCP recv() calls.

print(modifiedMessage.decode('utf-8'))
# print the received message

clientSocket.close()
# Close the socket
