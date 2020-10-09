#! /usr/bin/python3

import socket
import time
import os
import argparse
import logging
import threading
import inspect
from datetime import datetime, timezone
from queue import Queue

import my_socket
import utils



test_meta_config = utils.parse_config("config/test_meta_config.json")
log_level = utils.parse_logging_level(test_meta_config["general_config"]["logging_level"])
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)
current_script = os.path.basename(__file__)


def main():
    utils.init_dir()
    parser = argparse.ArgumentParser(description='For different background job')
    parser.add_argument('function', type=str, help='the job')
    parser.add_argument('--config_path', type=str, help='path of config file')
    args = parser.parse_args()

    #udp_socket()
    main_config = None
    if args.config_path:
        main_config = utils.parse_config(args.config_path)
    if args.function == "upload_iperf_wireshark":
        upload_iperf_wireshark(main_config)
    if args.function == "download_iperf_wireshark":
        download_iperf_wireshark(main_config)
    if args.function == "download_socket":
        download_socket()


def upload_iperf_wireshark(main_config = None):
    if main_config == None:
        main_config = utils.parse_config("config/config.json")
    main_config = main_config["upload_iperf_wireshark"]
    selected_network = main_config["network"]
    selected_direction = main_config["direction"]
    selected_variant = main_config["variant"]
    pcap_result_path = os.path.join(main_config["pcap_path"], main_config["task_name"])
    pcap_result_subpath_variant = os.path.join(pcap_result_path, selected_variant)

    total_run = int(main_config["total_run"])
    server_ip = main_config["server_ip"]
    server_packet_sending_port = main_config["server_packet_sending_port"]
    server_iperf_port = main_config["iperf_port"]
    iperf_logging_interval = main_config["iperf_logging_interval"]
    server_address_port = (server_ip, server_packet_sending_port)

    task_time = main_config["time_each_flow"]
    udp_sending_rate = main_config["udp_sending_rate"]

    utils.make_public_dir(pcap_result_path)
    utils.remake_public_dir(pcap_result_subpath_variant)
    time_flow_interval = 5 # wait some time to keep stability
    logger.info("Server--> upload_iperf_wireshark, Start~~")


    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.retry_bind(server_socket, server_address_port)
    server_socket.listen(10)
    while True:
        client_socket, client_address = server_socket.accept()
        logger.debug("Recieve from client {}".format(client_address))
        message = my_socket.doki_wait_receive_message(client_socket).replace("##DOKI##", "")
        if message == "upload_iperf_start":
            client_socket.close()
            current_datetime = datetime.fromtimestamp(time.time())
            output_pcap = os.path.join(pcap_result_subpath_variant, "{}.pcap".format(current_datetime.strftime("%Y_%m_%d_%H_%M")))
            os.system("iperf3 -s -p {} -i {} 2> /dev/null &".format(server_iperf_port, iperf_logging_interval))
            if selected_variant == "udp":
                os.system("tcpdump -i any udp port {} -w {} > /dev/null 2>&1 &".format(server_iperf_port, output_pcap))
                time.sleep(task_time + 2 * time_flow_interval)
                os.system('killall tcpdump > /dev/null 2>&1')
                os.system("python3 my_subprocess.py pcap2txt --mode udp --file-path {} &".format(output_pcap))
            if selected_variant != "udp":
                os.system("tcpdump -i any tcp dst port {} -w {} > /dev/null &".format(server_iperf_port, output_pcap))
                time.sleep(task_time + 2 * time_flow_interval)
                os.system('killall tcpdump > /dev/null 2>&1')
                os.system("python3 my_subprocess.py pcap2txt --mode tcp --file-path {} &".format(output_pcap))
            os.system('killall iperf3 > /dev/null 2>&1')
            logger.debug("Server One flow finished~")
        if message == "upload_iperf_end":
            client_socket.close()
            logger.info("Server--> upload_iperf_wireshark, All test Done~~")
            exit()



def download_iperf_wireshark(main_config = None):
    if main_config == None:
        main_config = utils.parse_config("config/config.json")
    main_config = main_config["download_iperf_wireshark"]
    exec_mode = main_config["mode"]
    selected_network = main_config["network"]
    selected_direction = main_config["direction"]
    selected_variant = main_config["variant"]
    server_ip = main_config["server_ip"]
    server_packet_sending_port = main_config["server_packet_sending_port"]
    server_iperf_port = main_config["iperf_port"]
    iperf_logging_interval = main_config["iperf_logging_interval"]
    server_address_port = (server_ip, server_packet_sending_port)
    pcap_result_path = os.path.join(main_config["pcap_path"], main_config["task_name"])
    pcap_result_subpath_variant = os.path.join(pcap_result_path, selected_variant)

    task_time = main_config["time_each_flow"]
    time_flow_interval = 5 # wait some time to keep stability
    if selected_variant != "udp":
        os.system("sudo sysctl net.ipv4.tcp_congestion_control={}".format(selected_variant))

    logger.info("{}--> download_iperf_wireshark, Start~~, Model: {}".format(current_script, exec_mode))
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if exec_mode == "scheduling":
        my_socket.retry_bind(server_socket, server_address_port)
        server_socket.listen(10)
        while True:
            client_socket, client_address = server_socket.accept()
            logger.debug("Recieve from client {}".format(client_address))
            message = my_socket.doki_wait_receive_message(client_socket).replace("##DOKI##", "")
            if message == "download_iperf_start":
                client_socket.close()
                current_datetime = datetime.fromtimestamp(time.time())
                os.system("iperf3 -s -p {} -i {} 2> /dev/null &".format(server_iperf_port, iperf_logging_interval))
                time.sleep(task_time + 2 * time_flow_interval)
                os.system('killall iperf3 > /dev/null 2>&1')
            if message == "download_iperf_end":
                client_socket.close()
                logger.info("Server--> download_iperf_wireshark, Done~~")
                server_socket.close()
                exit()

    if exec_mode == "continue":
        os.system("sudo kill $(sudo lsof -t -i:{})".format(server_iperf_port))
        os.system('killall iperf3 > /dev/null 2>&1')
        while True:
            logger.debug("{}_{}--> Start iperf server".format(current_script, inspect.currentframe().f_lineno))
            #os.system("iperf3 -s -p {} -i {} 2> /dev/null".format(server_iperf_port, iperf_logging_interval))
            os.system("iperf3 -s -p {} -i {}".format(server_iperf_port, iperf_logging_interval))
            logger.warning("Server iperf exit, resuming..")
            time.sleep(5)
            os.system("sudo kill $(sudo lsof -t -i:{})".format(server_iperf_port))
            os.system('killall iperf3 > /dev/null 2>&1')
            time.sleep(5)



"""
def download_socket():
    main_config = utils.parse_config("config/config.json")["download_socket"]
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
"""












if __name__ == '__main__':
    main()
