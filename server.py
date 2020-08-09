#! /usr/bin/python3

import socket
import time


def main():
    server_address = ('192.168.80.77', 7777)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(server_address)
    previous_connection_ip = ""
    previous_connection_port = ""
    data = ""
    client_address = ""
    file_read = open("input_file.txt")
    msg_byte = file_read.readline()[0:1000].encode()
    file_read.close()
    connection_total_time = 600
    connection_log_interval = 10
    server_socket.settimeout(5)

    connection_index = 1
    print("LTE connection server, start~~")
    while True:
        print("\nConnection [{}] start".format(connection_index))
        try:
            data, client_address = server_socket.recvfrom(2048)
        except socket.timeout:
            print("Connection [{}], Client connection setup timeout".format(connection_index))
            client_address = ""
        if len(client_address) != 0:
            client_ip = client_address[0]
            client_port = client_address[1]
            print("Connection [{}], Connection Setup success, client ip {}, client port {}".format(connection_index, client_ip, client_port))
            if previous_connection_ip == "":
                print("Initial first connection~~")
            elif previous_connection_ip != client_ip or previous_connection_port != client_port:
                print("Warning! IP and port changed: {}->{}, {}->{}".format(connection_index, previous_connection_ip, client_ip, previous_connection_port, client_port))
            previous_connection_ip = client_ip
            previous_connection_port = client_port

            connection_start_time = time.time()
            while True:
                current_time = time.time()
                if (current_time - connection_start_time) % connection_log_interval == 0:
                    print("Time {:.2f} ".format(current_time - connection_start_time))
                if len(client_address) != 0:
                    server_socket.sendto(msg_byte, client_address)
                    if current_time - connection_start_time > connection_total_time:
                        break
        else:
            print("Connection [{}], No Client connected".format(connection_index))
        connection_index = connection_index + 1
    server_socket.close()













if __name__ == '__main__':
    main()
