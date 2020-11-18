# python 3.7.4
import sys
import os
from socket import *
from _thread import start_new_thread, exit
from json import dumps, loads
from time import sleep

HOST = '127.0.0.1'
PORT = 12345
UserName = None

class CommHandle():
    def __init__(self, clientSocket):
        self.clientSocket = clientSocket
        self.recvData = None
        self.notPrint = False
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

    # a thread is opened for this function
    # which will keep calling this function to recv data from the server
    def recv(self):
        if self.notPrint: return
        self.recvData = self.clientSocket.recv(1024).decode('utf-8')
        
        # differece between XIT and SHT
        if self.recvData == 'Goodbye. Server shutting down\n>':
            print(self.recvData)
            self.recvData = 'Goodbye'
            return
        
        # if the received data is a dictionary or a list
        # do not print it out
        if self.recvData[0] in ['{', '[']: return
        print(self.recvData)

    def CRT(self, args):
        if len(args) != 1:
            print('Invalid command')
            return

        sendMessage(self.clientSocket, 'CRT', 'name', args[0])

    def MSG(self, args):
        if len(args) < 2:
            print('Invalid command')
            return

        message = ' '.join(args[1:])
        sendMessage(self.clientSocket, 'MSG', 'thread', args[0], 'message', message)

    def DLT(self, args):
        if len(args) < 2:
            print('Invalid command')
            return

        sendMessage(self.clientSocket, 'DLT', 'thread', args[0], 'message_number', args[1])

    def EDT(self, args):
        if len(args) < 3:
            print('Invalid command')
            return

        message = ' '.join(args[2:])
        sendMessage(self.clientSocket, 'EDT', 'thread', args[0], 'message_number', args[1], 'message', message)

    def LST(self, args):
        sendMessage(self.clientSocket, 'LST')
        sleep(0.1)
        self.recvData = loads(self.recvData)
        if not self.recvData:
            print('No threads to list')
            return

        print('The list of active threads:')
        for i in self.recvData.keys():
            print(i)

    def RDT(self, args):
        if len(args) != 1:
            print('Invalid command')
            return

        sendMessage(self.clientSocket, 'RDT', 'thread', args[0])
        
        # wait for the server's response
        sleep(0.01)
        
        self.recvData = loads(self.recvData)
        if not self.recvData[1:]:
            print('Thread', args[0], 'is empty')
            return

        for i in self.recvData[1:]:
            print(i.strip('\n'))

    def UPD(self, args):
        global UserName
        if len(args) < 2:
            print('Invalid command')
            return
        
        # check if the file exist in client's machine
        if not os.path.exists(args[1]):
            print(f'File \'{args[1]}\' does not exist')
            return

        # send thread's name first
        sendMessage(self.clientSocket, 'UPD', 'thread', args[0])
        
        # wait for the server's response 
        sleep(0.01)
        
        filesize = os.stat(args[1]).st_size
        
        # if the server responses '{OK'
        # the thread exist
        if self.recvData != '{OK': return
        self.recvData = ''
        
        # send user's name, file's name, and file's size to the server
        sendMessage(self.clientSocket, 'UPD', 'username', UserName, 'filename', args[1], 'filesize', filesize)

        # wait for server's response
        sleep(0.2)
        
        if self.recvData != '{OK': return
        
        # start send file's data
        with open(args[1], 'rb') as f:
            sent = 0
            while sent != filesize:
                data = f.read(1024)
                self.clientSocket.sendall(data)
                # wait for server to receive data
                sleep(0.01)
                sent += len(data)

    def DWN(self, args):
        global UserName
        if len(args) < 2:
            print('Invalid command')
            return

        thread_name = args[0]
        filename = args[1]
        # send the thread's name, and file's name (which file the client want to download)
        sendMessage(self.clientSocket, 'DWN', 'thread', thread_name, 'filename', filename)
        
        # wait for the server's response
        sleep(0.1)
        
        # if the server's response is start with 'File', it means the file does not exist
        if self.recvData.startswith('File'): return

        self.recvData = loads(self.recvData)
        filesize = self.recvData['filesize']
        
        # stop the thread (closeConn), which is keep receiving date from the server
        self.notPrint = True
        
        # wait for the server's response
        sleep(0.1)

        # start to download file's data from the server
        with open(filename, 'wb') as f:
            received = 0
            while received != filesize:
                data = self.clientSocket.recv(1024)
                f.write(data)
                received += len(data)

        # start the thread (closeConn)
        self.notPrint = False

    def RMV(self, args):
        if len(args) != 1:
            print('Invalid command')
            return

        sendMessage(self.clientSocket, 'RMV', 'thread', args[0])
        sleep(0.1)

    def XIT(self, args):
        sendMessage(self.clientSocket, 'XIT')

    def SHT(self, args):
        if len(args) != 1:
            print('Invalid command')
            return

        sendMessage(self.clientSocket, 'SHT', 'AdmPassword', args[0])

# keep calling recv() to receive data from the server
# if the receiving data is 'Goodbye', stop receiving data from the server
def closeConn(clientSocket, Handler):
    while Handler.recvData != 'Goodbye':
        try:
            Handler.recv()
        except Exception:
            break

def getCommand(Handler):
    commandList = ['CRT', 'MSG', 'DLT', 'EDT', 'LST', 'RDT', 'UPD', 'DWN', 'RMV', 'XIT', 'SHT']
    
    while Handler.recvData != 'Goodbye':
        # assume the input comand will be correct
        command = input(f'Enter one of the following commands: '+' '.join(commandList)+':\n')

        command = command.strip()
        command = command.split(' ')

        commandType = command[0]
        
        # command is not one of 
        # ('CRT', 'MSG', 'DLT', 'EDT', 'LST', 'RDT', 'UPD', 'DWN', 'RMV', 'XIT', 'SHT')
        if commandType not in Handler.executeComm.keys() or not command:
            print('Invalid command')
            continue

        Handler.executeComm[commandType](command[1:])
        sleep(0.2)

# seed message to the server
def sendMessage(clientSocket, *args):
    message = {
        'type': args[0]
    }

    for i in range(1, len(args[1:]), 2):
        message[f'{args[i]}'] = args[i+1]

    clientSocket.sendall(bytes(dumps(message), encoding='utf-8'))

def login(clientSocket):
    global UserName
    UserName = input('Enter username: ')
    UserName = UserName.strip()
    sendMessage(clientSocket, 'login-N', 'username', UserName)

    while True:
        recvData = clientSocket.recv(1024).decode('utf-8')
        # Y - user logged in
        if recvData[:1] == 'Y':
            # len(recvData) = 2 - new user logged in
            if len(recvData) == 2:
                sendMessage(clientSocket, 'login-S', 'status', 'successfully logged in')
                break
            print('Welcome to the forum')
            sendMessage(clientSocket, 'login-S', 'status', 'successful login')
            break
        # N - invalid password
        elif recvData == 'N':
            print('Invalid password')
            UserName = input('Enter username: ')
            sendMessage(clientSocket, 'login-N', 'username', UserName)
        # LD - user has already logged in
        elif recvData[:2] == 'LD':
            print(recvData[2:],' has already logged in')
            UserName = input('Enter username: ')
            sendMessage(clientSocket, 'login-N', 'username', UserName)
        # PWD - enter password
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

    # get command from the user
    Handler = CommHandle(clientSocket)
    
    # start a thread to keep receiving data from the server
    start_new_thread(closeConn, (clientSocket, Handler,))
    # start a thread to keep getting command from the user
    start_new_thread(getCommand, (Handler,))

    while Handler.recvData != 'Goodbye':
        continue

    clientSocket.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('required Server IP address and Server port number')
        exit(1)

    IPaddr =sys.argv[1]
    if IPaddr.lower() != 'localhost':
        HOST = IPaddr

    PORT = int(sys.argv[2])
    client()
