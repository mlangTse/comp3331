# python 3.7.4
import sys
import os
from socket import *
from json import dumps, loads

HOST = gethostbyname(gethostname())
PORT = 12345

class CommHandle():
    def __init__(self, clientSocket):
        self.clientSocket = clientSocket
        self.recvData = None
        self.executeComm = {
            'CRT': self.CRT,
            'MSG': self.MSG,
            'DLT': self.DLT,
            'EDT': self.EDT,
            'LST': self.LST,
            'RDT': self.RDT,
            'UPD': self.UPD,
            'DWN': self.DWN,
            'RMV': self.RMV,
            'XIT': self.XIT,
            'SHT': self.SHT,
        }

    def recv(self):
        self.recvData = self.clientSocket.recv(2048).decode('utf-8')

    def CRT(self, args):
        if len(args) != 1:
            print('Invalid command')
            return

        sendMessage(self.clientSocket, 'CRT', 'name', args[0])
        self.recv()
        print(self.recvData)

    def MSG(self, args):
        if len(args) < 2:
            print('Invalid command')
            return

        message = ' '.join(args[1:])
        sendMessage(self.clientSocket, 'MSG', 'thread', args[0], 'message', message)
        self.recv()
        print(self.recvData)

    def DLT(self, args):
        sendMessage(self.clientSocket, 'DLT')
        self.recv()
        print(self.recvData)

    def EDT(self, args):
        sendMessage(self.clientSocket, 'EDT')
        self.recv()
        print(self.recvData)

    def LST(self, args):
        sendMessage(self.clientSocket, 'LST')
        self.recv()
        self.recvData = loads(self.recvData)
        if not self.recvData:
            print('No threads to list')
            return

        print('The list of active threads:')
        for i in self.recvData:
            print(i)

    def RDT(self, args):
        sendMessage(self.clientSocket, 'RDT')
        self.recv()
        print(self.recvData)

    def UPD(self, args):
        sendMessage(self.clientSocket, 'UPD')
        self.recv()
        print(self.recvData)

    def DWN(self, args):
        sendMessage(self.clientSocket, 'DWN')
        self.recv()
        print(self.recvData)

    def RMV(self, args):
        sendMessage(self.clientSocket, 'RMV')
        self.recv()
        print(self.recvData)

    def XIT(self, args):
        sendMessage(self.clientSocket, 'XIT')
        self.recv()
        print(self.recvData)

    def SHT(self, args):
        sendMessage(self.clientSocket, 'SHT')
        self.recv()
        print(self.recvData)

def sendMessage(clientSocket, Mtype, Mname=None, Message=None, Mname2=None, Message2=None):
    message = {
        'type': Mtype,
        f'{Mname}': Message,
        f'{Mname2}': Message2,
    }
    clientSocket.send(bytes(dumps(message), encoding='utf-8'))

def login(clientSocket):
    username = input('Enter username: ')
    sendMessage(clientSocket, 'login-N', 'username', username)

    while True:
        recvData = clientSocket.recv(1024).decode('utf-8')
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
    Handler = CommHandle(clientSocket)
    while Handler.recvData != 'Goodbye':
        command = input(f'Enter one of the following commands: '+' '.join(commandList))

        command = command.split(' ')

        commandType = command[0]
        if commandType not in Handler.executeComm.keys():
            print('Invalid command')
            continue
        Handler.executeComm[commandType](command[1:])

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

