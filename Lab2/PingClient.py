# python 3.7.4 

from socket import *
import sys
import time
import statistics

def ping (host, port):
    clientSocket = socket(AF_INET, SOCK_DGRAM)

    # create UDP clent socket
    seq = 3331
    pingtime = 0
    rrts = []
    while (pingtime < 15):
        pingtime += 1
        start = time.time() * 1000
        message = 'PING' + str(seq) + str(start) + '\r\n'
        clientSocket.sendto(message.encode('utf-8'), (host, port))
        # wait up to 600 ms to receive a reply
        clientSocket.settimeout(0.6)

        try:
            modified, addr = clientSocket.recvfrom(2048)
            gettime = time.time() * 1000
            used = gettime - start
            rrts.append(used)
            print(f'Ping to {host}, seq = {seq}, time = {int(used)}')
            seq += 1
        except timeout:
            print(f'Ping to {host}, seq = {seq}, timeout')
            seq += 1
        
    print('transmission finished')

    if len(rrts) > 0:
        avg = round(statistics.mean(rrts), 3)
        print(f'rtt min/avg/max = {round(min(rrts), 3)}/{avg}/{round(max(rrts), 3)} ms \n')
    else:
        print('ALL TIME OUT, Check Host Port again\n')
        
    # close the client
    clientSocket.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('required host port')
        exit(1)
    host = sys.argv[1]
    port = int(sys.argv[2])
    ping(host, port)