# python 3.7.4
import sys
import os
from socket import *
from _thread import *
import time
import datetime as dt
from json import dumps, loads

# Store clients info
clients = []
thread = []

class Client():
    def __init__(self, username, pwd):
        self.username = username
        self.pwd = pwd
        self.conn = None
        self.request = None
        self.logged = False
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

    def CRT(self):
        global thread
        if os.path.exists(self.request['name']):
            message = 'Thread ' + self.request['name'] + ' exists'
            print(message)
            self.conn.send(bytes(message, encoding='utf-8'))
            return

        with open(self.request['name'], 'w') as f:
            f.write(self.username)
            f.close
        thread.append(self.request['name'])
        message = 'Thread ' + self.request['name'] + ' created'
        self.conn.send(bytes(message, encoding='utf-8'))

    def MSG(self):
        if not os.path.exists(self.request['thread']):
            message = 'Thread ' + self.request['thread'] + ' not exists'
            print(message)
            self.conn.send(bytes(message, encoding='utf-8'))
            return

        def file_len(fname):
            with open(fname) as f:
                for i, l in enumerate(f):
                    continue
            return str(i + 1)

        with open(self.request['thread'], 'a') as f:
            l = file_len(self.request['thread'])
            f.write('\n' + l + ' ' + self.username + ': ' + self.request['message'])
            f.close

        message = 'Message posted to ' + self.request['thread'] + ' thread'
        print(message)
        self.conn.send(bytes(message, encoding='utf-8'))

    def DLT(self):
        pass

    def EDT(self):
        pass

    def LST(self):
        global thread
        print(f'{self.username} issued LST command')
        self.conn.send(bytes(dumps(thread), encoding='utf-8'))

    def RDT(self):
        pass

    def UPD(self):
        pass

    def DWN(self):
        pass

    def RMV(self):
        pass

    def XIT(self):
        self.logged = False
        print(f'{self.username} exited')
        self.conn.send(bytes('Goodbye', encoding='utf-8'))

    def SHT(self):
        pass

def signIn(conn, request, client):
    if request['type'] == 'login-N':
        client = [i for i in clients if i.username == request['username']]

        # A new client
        if not client:
            client = Client(request['username'], None)
            client.conn = conn
            clients.append(client)
            conn.send(bytes('NU' + request['username'], encoding='utf-8'))
            return client

        client = client[0]
        client.conn = conn
        if not client.logged:
            conn.send(bytes('PWD', encoding='utf-8'))
        else:
            conn.send(bytes('LD', encoding='utf-8'))
    elif request['type'] == 'login-P':
        if client.pwd == request['password']:
            client.logged = True
            conn.send(bytes('Y', encoding='utf-8'))
        else:
            print('Incorrect password')
            conn.send(bytes('N', encoding='utf-8'))
    elif request['type'] == 'login-NP':
        client.pwd = request['password']
        with open('credentials.txt', 'a') as f:
            f.write(f'{client.username} {client.pwd}\n')
        conn.send(bytes('YN', encoding='utf-8'))
    elif request['type'] == 'login-S':
        print(client.username, request['status'])

    return client

def updateClients():
    global clients
    with open('credentials.txt') as f:
        for line in f.readlines():
            username, pwd = line.split(' ')
            newClient = Client(username.strip(), pwd.strip())
            clients.append(newClient)
    return clients

def ClientThread(conn):
    global clients
    client = None

    while True:
        data = conn.recv(1024)
        print(f'received: {data}')
        if not data:
            print('Waiting for clients')
            break

        request = loads(data.decode('utf-8'))

        if request['type'].startswith('login'):
            client = signIn(conn, request, client)
        elif client:
            if request['type'] != 'XIT':
                print(f'{client.username} issued ', request['type'], ' command')
            client.request = request
            client.executeComm[request['type']]()

def web_server(port):
    # Get host
    host = gethostbyname(gethostname())
    # Create a TCP socket
    TCPserver = socket(AF_INET, SOCK_STREAM)
    TCPserver.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    # Bind the socket to the port
    print(f'starting up on {host}:{port}')
    TCPserver.bind((host, port))

    # Listen for incming connections
    TCPserver.listen(4)

    while True:
        # Wait for a connection
        # print('Waiting for a connection from TCP clients')
        # print('Waiting for clients')
        conn, (ip, port) = TCPserver.accept()

        # get a connection
        print(f'Connected to {ip}:{port}')
        # print('Client connected')
        start_new_thread(ClientThread, (conn,))

    TCPserver.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('required Server port and Admin password')
        exit(1)

    port = int(sys.argv[1])
    if port not in range(1023, 65537):
        print('port should be a number within [1023, 65536]')
        exit(1)

    Admpass = sys.argv[2]

    clients = updateClients()
    web_server(port)
