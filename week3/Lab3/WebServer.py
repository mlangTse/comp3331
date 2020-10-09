# python 3.7.4

from socket import *
import sys

def web_server(port):
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('localhost', port))
    serverSocket.listen(1)
    print(f'The server is ready on http://127.0.0.1:{port}/index.html')
    while True:
        conn, addr = serverSocket.accept()
        response(conn)

def response(conn):
    sentence = conn.recv(1024)
    if sentence == b'': return

    try:
        filename = sentence.split()[1][1:]
        data = open(filename, 'rb').read()
        print(f'request {filename}')
        conn.send(b'HTTP/1.1 200 OK\r\n')
        if 'png' in str(filename):
            conn.send(b'Content-Type: image/png \r\n\r\n')
        else:
            conn.send(b'Content-Type: text/html \r\n\r\n')
        conn.send(data)
        conn.close()
    except IOError:
        conn.send(b'HTTP/1.1 404 Not Found\r\n')
        conn.send(b'Content-Type: text/html \r\n\r\n')
        conn.send(b'<html><h1>404 File Not Found Try index.html or myimage.png</h1></html>')
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 1 :
        print('required port')
        exit(1)

    port = int(sys.argv[1])
    web_server(port)