#! /usr/bin/python3

import socket
import datetime
import time
import errno
import sys


def utf8len(s):
    return len(s.decode('utf-8'))

def main():
    file_name = 'temp/client_recieve_temp.txt'
    server_address = ('192.168.80.77', 7777)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(3)

    starting_time = time.time()
    throughput_begin = time.time() + 1
    file_write = open(file_name, "a")

    sent = 0
    data = ""
    temp = 0

    connection_index = 1
    print("LTE connection server, start~~")
    while True:
        print("")
        client_socket.sendto("Client Set Up connection message to server".encode(), server_address)

        file_write.write("sending request now!!!!!!!!!\n")
        begin = time.time()
        throughput_begin = time.time() + 1
        while True:
            try:
                data, addr = client_socket.recvfrom(10000000)
            except socket.timeout:
                print('caught a timeout')
            now = time.time()
            if now - begin > 30:
                break
                print("break")


            if now - throughput_begin  > 1:
                sent = sent + utf8len(data)
                temp = sent * 8
                print("bandwidth=  "),
                print(temp , now - starting_time)
                file_write.write("bandwidth: " + str(temp) + "\n")
                sent = 0
                throughput_begin  = throughput_begin  + 1
            else:
                sent = sent + utf8len(data)
            if now - starting_time > 60:
                break
        now = time.time()
        if now - starting_time > 60:
            break
    client_socket.close()
    file_write.close()





if __name__ == '__main__':
    main()
