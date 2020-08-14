#! /usr/bin/python3

import socket
import time
import utils

main_config = utils.parse_config("config/config.json")

def main():
    #udp_socket()


def iperf_wireshark():
    pass()



def udp_socket():
    server_address = tuple(main_config["server_address"])
    connection_total_time = main_config["connection_total_time"]
    server_connection_log_interval = 1000000
    server_timeout_value = main_config["server_timeout_value"]

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(server_address)
    server_socket.settimeout(server_timeout_value)
    previous_connection_ip = ""
    previous_connection_port = ""
    data = ""
    client_address = ""
    file_read = open("input_file")
    msg_byte = file_read.readline()[0:1000].encode()
    file_read.close()


    connection_index = 1
    print("LTE connection server, start~~")
    while True:
        print("\nConnection [{}] start".format(connection_index))
        data = ""
        try:
            data, client_address = server_socket.recvfrom(2048)
        except socket.timeout:
            print("Connection [{}], Client connection setup timeout".format(connection_index))
            client_address = ""
        if len(data) != 0:
            client_ip = client_address[0]
            client_port = client_address[1]
            print("Connection [{}], Connection Setup success, client ip "
                  "{}, client port {}".format(connection_index, client_ip, client_port))
            if previous_connection_ip == "":
                print("Initial first connection~~")
            elif previous_connection_ip != client_ip or previous_connection_port != client_port:
                print("Warning! IP and port changed: {}->{}, {}->{}".format(previous_connection_ip, client_ip, previous_connection_port, client_port))
            previous_connection_ip = client_ip
            previous_connection_port = client_port

            connection_start_time = time.time()
            data_count = 0
            while True:
                if len(client_address) != 0:
                    server_socket.sendto(msg_byte, client_address)
                    data_count = data_count + 1
                    if data_count % server_connection_log_interval == 0:
                        print("Time {:.2f}, data sent {} million counts".format(time.time() - connection_start_time, data_count/server_connection_log_interval))
                if time.time() - connection_start_time >= connection_total_time:
                    break
        else:
            print("Connection [{}], No Client connected".format(connection_index))
        connection_index = connection_index + 1
    server_socket.close()













if __name__ == '__main__':
    main()
