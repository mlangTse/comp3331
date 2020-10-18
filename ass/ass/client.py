# python 3.7.4
import sys
import os
from socket import *
from json import dumps

HOST = gethostbyname(gethostname())
PORT = 12345

def sendMessage(clientSocket, Mtype, Mname=None, Message=None):
    message = {
        'type': Mtype,
        f'{Mname}': Message,
    }
    clientSocket.send(bytes(dumps(message), encoding='utf-8'))

def login(clientSocket):
    username = input('Enter username: ')
    sendMessage(clientSocket, 'login-N', 'username', username)

    while True:
        recvData = clientSocket.recv(1024).decode('utf-8')
        print(recvData)
        if recvData[:1] == 'Y':
            if len(recvData) == 2:
                sendMessage(clientSocket, 'login-S', 'status', 'successfully logged in')
                break
            print('Welcome to the forum')
            sendMessage(clientSocket, 'login-S', 'status', 'successful login')
            break
        elif recvData == 'N':
            print('Invalid password')
            username = input('Enter username: ')
            sendMessage(clientSocket, 'login-N', 'username', username)
        elif recvData[:2] == 'LD':
            print(recvData[2:],' has already logged in')
            username = input('Enter username: ')
            sendMessage(clientSocket, 'login-N', 'username', username)
        elif recvData == 'PWD':
            pwd = input(f'Enter password: ')
            sendMessage(clientSocket, 'login-P', 'password', pwd)
        # NU - New User
        elif recvData[:2] == 'NU':
            pwd = input(f'Enter new password for {recvData[2:]}: ')
            sendMessage(clientSocket, 'login-NP', 'password', pwd)

def client():
    global HOST
    global PORT
    # Create a TCP socket
    clientSocket = socket(AF_INET, SOCK_STREAM)

    # Connect to a TCP server
    clientSocket.connect((HOST, PORT))

    # login in to the server
    login(clientSocket)

    commandList = ['CRT', 'MSG', 'DLT', 'EDT', 'LST', 'RDT', 'UPD', 'DWN', 'RMV', 'XIT', 'SHT']

    # get command from the user
    while True:
        command = input(f'Enter one of the following commands: '+' '.join(commandList))

        if command == 'q':
            sendMessage(clientSocket, 'q')
            break

        if command == 'XIT':
            print('Goodbye')
            sendMessage(clientSocket, 'XIT')
            break

    clientSocket.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('required Server IP address and Server port number')
        exit(1)

    IPaddr =sys.argv[1]
    if IPaddr.lower() != 'localhost':
        HOST = IPaddr

    POST = int(sys.argv[2])
    client()

