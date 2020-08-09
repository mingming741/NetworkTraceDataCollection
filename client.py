#! /usr/bin/python3

import socket
import datetime
import time
import errno
import sys
import os


def main():
    udp_socket()


def udp_socket():
    file_name = 'result/udp_client_recieve.txt'
    if os.path.exists(file_name):
        os.remove(file_name)
    #server_address = ('192.168.80.77', 7777)
    server_address = ('103.49.160.131', 7777)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(3)

    process_starting_time = time.time()
    file_write = open(file_name, "w")
    process_total_time = 120
    connection_total_time = 30
    throughput_calculation_interval = 1
    connection_index = 1
    print("LTE connection server, start~~")
    while True:
        print("\nConnection [{}] start".format(connection_index))
        client_socket.sendto("Client Set Up connection message to server".encode(), server_address)
        file_write.write("Connection [{}]\n".format(connection_index))
        connection_start_time = time.time()
        throughput_calculation_begin_time = time.time()# + throughput_calculation_interval
        sent = 0
        data = ""
        exit = 0
        while True:
            try:
                data, server_address = client_socket.recvfrom(10000000)
            except socket.timeout:
                print('Connection [{}] Time out'.format(connection_index))
                exit = 1
            if len(data) != 0:
                if time.time() - throughput_calculation_begin_time  > throughput_calculation_interval:
                    sent = sent + utf8len(data)
                    bandwidth = (sent * 8) / throughput_calculation_interval
                    print("Bandwidth = {:.0f}. time {:.2f}".format(bandwidth, time.time() - connection_start_time))
                    file_write.write("BW:{}\n".format(bandwidth))
                    sent = 0
                    throughput_calculation_begin_time  = throughput_calculation_begin_time  + throughput_calculation_interval
                else:
                    sent = sent + utf8len(data)
            if time.time() - connection_start_time > connection_total_time:
                break
            if exit == 1:
                break
        connection_index = connection_index + 1
        if time.time() - process_starting_time >= process_total_time:
            break

    client_socket.close()
    file_write.close()


def utf8len(s):
    return len(s.decode('utf-8'))


if __name__ == '__main__':
    main()
