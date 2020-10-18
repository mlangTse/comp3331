# python 3.7.4
import sys
import os
from socket import *
from _thread import *
import time
import datetime as dt
import json

# Store clients info
clients = []
client = None

class Client():
    def __init__(self, username, pwd):
        self.username = username
        self.pwd = pwd
        self.logged = False

def signIn(conn, request):
    global client
    if request['type'] == 'login-N':
        client = [i for i in clients if i.username == request['username']]

        # A new client
        if not client:
            client = Client(request['username'], None)
            clients.append(client)
            conn.send(bytes('NU' + request['username'], encoding='utf-8'))
            return

        client = client[0]
        if not client.logged:
            conn.send(bytes('PWD', encoding='utf-8'))
        else:
            conn.send(bytes('LD', encoding='utf-8'))
    elif request['type'] == 'login-P':
        if client.pwd == request['password']:
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
    global client
    clients = updateClients()

    while True:
        data = conn.recv(1024)
        print(f'received: {data}')
        if not data:
            print('Waiting for clients')
            break

        request = json.loads(data.decode('utf-8'))

        if request['type'] == 'q':
            client.logged = False
            break

        if request['type'].startswith('login'):
            signIn(conn, request)

        if request['type'] == 'CRT':
            pass
        elif request['type'] == 'MSG':
            pass
        elif request['type'] == 'DLT':
            pass
        elif request['type'] == 'EDT':
            pass
        elif request['type'] == 'LST':
            print(f'{client.username} issued {LST} command')
        elif request['type'] == 'RDT':
            pass
        elif request['type'] == 'UPD':
            pass
        elif request['type'] == 'DWN':
            pass
        elif request['type'] == 'RMV':
            pass
        elif request['type'] == 'XIT':
            client.logged = False
            print(f'{client.username} exited')
        elif request['type'] == 'SHT':
            pass



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

    web_server(port)
