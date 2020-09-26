#coding: utf-8
from socket import *

#Define connection (socket) parameters
#Address + Port no
#Server would be running on the same host as Client
serverName = 'localhost'

#change this port number if required
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_STREAM)
#This line creates the client’s socket. The first parameter indicates the address family; in particular,AF_INET indicates that the underlying network is using IPv4. The second parameter indicates that the socket is of type SOCK_STREAM,which means it is a TCP socket (rather than a UDP socket, where we use SOCK_DGRAM). 

clientSocket.connect((serverName, serverPort))
#Before the client can send data to the server (or vice versa) using a TCP socket, a TCP connection must first be established between the client and server. The above line initiates the TCP connection between the client and server. The parameter of the connect( ) method is the address of the server side of the connection. After this line of code is executed, the three-way handshake is performed and a TCP connection is established between the client and server.

sentence = input('Input lowercase sentence:')
#input() is a built-in function in Python. When this command is executed, the user at the client is prompted with the words “Input lowercase sentence:” The user then uses the keyboard to input a line, which is put into the variable sentence. Now that we have a socket and a message, we will want to send the message through the socket to the destination host.

clientSocket.send(sentence.encode('utf-8'))
#As the connection has already been established, the client program simply drops the bytes in the string sentence into the TCP connection. Note the difference between UDP sendto() and TCP send() calls. In TCP we do not need to attach the destination address to the packet, as was the case with UDP sockets.

modifiedSentence = clientSocket.recv(1024)
#We wait to receive the reply from the server, store it in modifiedSentence

print('From Server:', modifiedSentence.decode('utf-8'))
#print what we have received

clientSocket.close()
#and close the socket
