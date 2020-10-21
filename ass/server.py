# python 3.7.4
import sys
import os
from socket import *
from _thread import *
import time
import datetime as dt
from json import dumps, loads
from time import sleep

# Store clients info
clients = []
threads = {}
SHUTDOWN = False
AdminPassword = None
TCPserver = None

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

    def threadExist(self, msg=None):
        if not os.path.exists(self.request['thread']):
            message = 'Thread ' + self.request['thread'] + ' not exists'
            if msg:
                print(msg)
            else:
                print(message)
            self.conn.send(bytes(message, encoding='utf-8'))
            return False
        return True

    def HasPremission(self, msg):
        messNum = int(self.request['message_number'])
        with open(self.request['thread'], 'r') as f:
            lines = f.readlines()

        if messNum >= len(lines):
            print('Message cannot be ', msg)
            message = 'Invalid message number'
            self.sendMessage(message)
            return False

        if lines[messNum][2:2+len(self.username)] != self.username:
            print('Message cannot be ', msg)
            message = 'The message belongs to another user and cannot be ' + msg
            self.sendMessage(message)
            return False
        return True

    def sendMessage(self, msg):
        self.conn.send(bytes(msg, encoding='utf-8'))
        sleep(0.1)

    def CRT(self):
        global threads
        if os.path.exists(self.request['name']):
            message = 'Thread ' + self.request['name'] + ' exists'
            self.sendMessage(message)
            print(message)
            return

        with open(self.request['name'], 'w') as f:
            f.write(self.username)

        threads[self.request['name']] = {
            'cur_index': 1,
            'files': []
        }

        message = 'Thread ' + self.request['name'] + ' created'
        self.sendMessage(message)
        print(message)

    def MSG(self):
        global threads
        if not self.threadExist(): return

        with open(self.request['thread'], 'a') as f:
            l = threads[self.request['thread']]['cur_index']
            f.write('\n' + str(l) + ' ' + self.username + ': ' + self.request['message'])
            threads[self.request['thread']]['cur_index'] += 1

        message = 'Message posted to ' + self.request['thread'] + ' thread'
        self.sendMessage(message)
        print(message)

    def DLT(self):
        global threads
        if not self.threadExist(): return

        if not self.HasPremission('deleted'): return

        # delete message
        messNum = int(self.request['message_number'])
        with open(self.request['thread'], 'r') as f:
            lines = f.readlines()

        if len(lines) == 2:
            lines = lines[0].strip('\n')
        else:
            del lines[messNum]

        for i in range(messNum, len(lines)):
            lines[i] = str(i) + lines[i][1:]
        out = open(self.request['thread'], 'w')
        out.writelines(lines)
        out.close()

        # updata index
        threads[self.request['thread']]['cur_index'] -= 1
        message = 'Message has been deleted'
        self.sendMessage(message)
        print(message)

    def EDT(self):
        if not self.threadExist(): return
        if not self.HasPremission('edited'): return

        with open(self.request['thread'], 'r') as f:
            lines = f.readlines()

        messNum = int(self.request['message_number'])
        lines[messNum] = lines[messNum][:3+len(self.username)] + self.request['message'] + '\n'
        out = open(self.request['thread'], 'w')
        out.writelines(lines)
        out.close()
        message = 'Message has been edited'
        self.sendMessage(message)
        print(message)

    def LST(self):
        global threads
        self.sendMessage(dumps(threads))

    def RDT(self):
        if not self.threadExist('Incorrect thread specified'): return
        with open(self.request['thread'], 'r') as f:
            lines = f.readlines()

        message = 'Thread ' + self.request['thread'] + ' read'
        self.sendMessage(dumps(lines))
        print(message)

    def ExistFile(self, thread_name, filename):
        global threads
        if filename not in threads[thread_name]['files']:
            return False
        return True

    def UPD(self):
        global threads
        thread_name = self.request['thread']
        if not self.threadExist(): return
        else:
            # get username and filename
            self.sendMessage('{OK')
            sleep(0.01)

        data = self.conn.recv(1024)
        print(data)
        self.request = loads(data.decode('utf-8'))
        print(self.request)
        filename = self.request['filename']
        username = self.request['username']
        filesize = int(self.request['filesize'])
        if self.ExistFile(thread_name, filename):
            message = filename + ' already exist in Thread ' + thread_name
            self.sendMessage(message)
            print(message)
            return

        # get file's content
        self.sendMessage('{OK')
        sleep(0.01)

        with open(thread_name, 'w') as f:
            f.write(f'{username} uploaded {filename}')


        with open(f'{thread_name}-{filename}', 'w') as f:
            received = 0
            while received != filesize:
                data = self.conn.recv(1024)
                f.write(data)
                received += len(data)

        threads[thread_name]['files'].append(filename)
        message = filename + ' uploaded to ' + thread_name + ' thread'
        print(username, 'uploaded file', filename, 'to', thread_name, 'thread')
        self.sendMessage(message)

    def DWN(self):
        pass

    def RMV(self):
        global threads
        if not self.threadExist(): return
        with open(self.request['thread'], 'r') as f:
            head = f.readline()

        if head[:len(self.username)] != self.username:
            message = 'The thread was created by another user and cannot be removed'
            self.sendMessage(message)
            print('Thread ' + self.request['thread'] + ' cannot be removed')
            return

        os.remove(self.request['thread'])
        for i in threads[self.request['thread']]['files']:
            os.remove(self.request['thread']+'-'+i)
        del threads[self.request['thread']]
        message = 'The thread has been removed'
        self.sendMessage(message)
        print('Thread ' + self.request['thread'] + ' removed')

    def XIT(self):
        self.logged = False
        self.sendMessage('Goodbye')
        print(f'{self.username} exited')

    def SHT(self):
        global clients
        global threads
        global SHUTDOWN
        global AdminPassword
        global TCPserver
        if AdminPassword != self.request['AdmPassword']:
            message = 'Incorrect password'
            print(message)
            self.sendMessage(message)
            return

        for i in threads.keys():
            for j in threads[i]['files']:
                os.remove(i+'-'+j)
            os.remove(i)
        os.remove('credentials.txt')

        SHUTDOWN = True

        for c in clients:
            if not c.logged: continue
            c.sendMessage('Goodbye. Server shutting down\n>')

        print('Server shutting down\n>', end='')
        TCPserver.close()


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
        client.logged = True
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
    global SHUTDOWN
    client = None

    while True:
        sleep(0.1)
        data = conn.recv(1024)
        if SHUTDOWN:
            break
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

def server(port):
    global SHUTDOWN
    global TCPserver
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
        try:
            conn, (ip, port) = TCPserver.accept()
        except Exception:
            pass

        if SHUTDOWN:
            break

        # get a connection
        print(f'Connected to {ip}:{port}')
        # print('Client connected')
        start_new_thread(ClientThread, (conn,))

    TCPserver.close()
    sys.exit()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('required Server port and Admin password')
        exit(1)

    port = int(sys.argv[1])
    if port not in range(1023, 65537):
        print('port should be a number within [1023, 65536]')
        exit(1)

    AdminPassword = sys.argv[2]

    with open('credentials.txt', 'w') as f:
        f.close()

    clients = updateClients()
    server(port)