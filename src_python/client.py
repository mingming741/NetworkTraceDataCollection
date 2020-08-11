#! /usr/bin/python3

import socket
import datetime
import time
import os
import json
import glob
import shutil

import utils

main_config = utils.parse_config("config/config.json")

def main():
    initial_dir()
    udp_socket()

def udp_socket():
    result_path = main_config["result_path"]
    result_file_prefix = os.path.join(result_path, "udp_client_recieve_")
    result_file_ext = ".txt"
    server_address = tuple(main_config["server_address"])
    client_timeout_value = main_config["client_timeout_value"]
    process_total_time = main_config["process_total_time"]
    connection_total_time = main_config["connection_total_time"]
    throughput_calculation_interval = main_config["throughput_calculation_interval"]

    shutil.rmtree(result_path)
    os.mkdir(result_path)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(client_timeout_value)
    client_start_time = time.time()
    output_config = {"client_start_time": client_start_time, "process_total_time": process_total_time, "connection_total_time": connection_total_time,
                     "server_address": server_address, "throughput_calculation_interval": throughput_calculation_interval, "client_timeout_value": client_timeout_value}
    with open(main_config["test_config_file"], 'w') as f:
        json.dump(output_config, f)


    connection_index = 1
    print("LTE connection server, start~~")
    current_output_file_name = ""
    while True:
        current_datetime = datetime.datetime.now()
        file_name = "{}{}{}".format(result_file_prefix, current_datetime.strftime("%Y_%m_%d_%H"), result_file_ext)
        print(file_name)
        if file_name != current_output_file_name:
            try:
                file_write.close()
            except:
                print("No file to close")
            current_output_file_name = file_name
            file_write = open(current_output_file_name, "w")
        print("\nConnection [{}] start".format(connection_index))
        client_socket.sendto("Client Set Up connection message to server".encode(), server_address)
        connection_start_time = time.time()
        throughput_calculation_begin_time = time.time()
        data = ""
        sent = 0
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
                    print("Bandwidth = {:.0f}. time {:.2f}, current time {}".format(bandwidth, time.time() - connection_start_time, datetime.datetime.now()))
                    file_write.write("{:.3f}\t{}\n".format(time.time(), bandwidth))
                    sent = 0
                    throughput_calculation_begin_time  = throughput_calculation_begin_time  + throughput_calculation_interval
                if time.time() - connection_start_time > connection_total_time:
                    break
                else:
                    sent = sent + utf8len(data)
            if exit == 1:
                break
        connection_index = connection_index + 1
        if time.time() - client_start_time >= process_total_time and process_total_time != -1: # -1 means run all over the time
            break
    client_socket.close()



def initial_dir():
    if not os.path.exists("output_trace"):
        os.mkdir("output_trace")
    if not os.path.exists("result"):
        os.mkdir("result")


def utf8len(s):
    return len(s.decode('utf-8'))


if __name__ == '__main__':
    main()
