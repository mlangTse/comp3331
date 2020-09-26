#coding: utf-8
from socket import *
#using the socket module

#Define connection (socket) parameters
#Address + Port no
#Server would be running on the same host as Client
# change this port number if required
serverPort = 12000 

serverSocket = socket(AF_INET, SOCK_DGRAM)
#This line creates the server’s socket, called serverSocket. The first parameter indicates the address family; in particular,AF_INET indicates that the underlying network is using IPv4.The second parameter indicates that the socket is of type SOCK_DGRAM,which means it is a UDP socket (rather than a TCP socket, where we use SOCK_STREAM).

serverSocket.bind(('localhost', serverPort))
#The above line binds (that is, assigns) the port number 12000 to the server’s socket. In this manner, when anyone sends a packet to port 12000 at the IP address of the server (localhost in this case), that packet will be directed to this socket.
print('The server is ready to receive')
while 1:
    message, clientAddress = serverSocket.recvfrom(2048)
    #receive data from the client, now we know who we are talking with
    
    modifiedMessage = message.upper()
    #change the case of the message received from client

    serverSocket.sendto(modifiedMessage, clientAddress)
    #send it back to client, need to specify the client address in sendto

