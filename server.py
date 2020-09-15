#! /usr/bin/python3

import socket
import time
import utils
import os
import shutil
import threading
import argparse
from datetime import datetime, timezone

main_config = utils.parse_config("config/config.json")

def main():
    utils.init_dir()
    parser = argparse.ArgumentParser(description='For different background job')
    parser.add_argument('function', type=str, help='the job')
    args = parser.parse_args()

    #udp_socket()
    if args.function == "upload_iperf_wireshark":
        upload_iperf_wireshark()
    if args.function == "download_iperf_wireshark":
        download_iperf_wireshark()


def upload_iperf_wireshark():
    main_config = utils.parse_config("config/config.json")["upload_iperf_wireshark"]
    print("Upload iperf server, start~~")
    if os.path.exists(main_config["result_path"]):
        shutil.rmtree(main_config["result_path"])
    os.mkdir(main_config["result_path"])
    os.system("sudo chmod 777 {}".format(main_config["result_path"]))
    os.mkdir(os.path.join(main_config["result_path"], main_config["variant"]))
    os.system("sudo chmod 777 {}".format(os.path.join(main_config["result_path"], main_config["variant"])))
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(tuple(main_config["server_cmd_address"]))
    server_socket.listen(10)
    while True:
        client_socket, client_address = server_socket.accept()
        print("Recieve from client {}".format(client_address))
        count = 0
        message = ""
        while True:
            count = count + 1
            data = client_socket.recv(1024).decode("utf-8")
            message = message + data
            if "##DOKI##" in data:
                break
        client_socket.close()
        message = message.replace("##DOKI##", "")
        print(message)
        if message == "Start":
            os.system("iperf3 -s -p 7777 &")
            current_datetime = datetime.fromtimestamp(time.time())
            output_pcap = os.path.join(main_config["result_path"], main_config["variant"], "{}.pcap".format(current_datetime.strftime("%Y_%m_%d_%H_%M")))
            if main_config["variant"] == "udp":
                os.system("tcpdump -i any udp port {} -w {} &".format(main_config["iperf_port"], output_pcap))
                time.sleep(main_config["time_each_flow"] + 2 * main_config["time_flow_interval"])
                os.system('killall tcpdump')
                os.system("python3 my_subprocess.py pcap2txt --mode udp --file-path {} &".format(output_pcap))
            if main_config["variant"] != "udp" and main_config["variant"] in main_config["variants_list"]:
                os.system("tcpdump -i any tcp dst port {} -w {} &".format(main_config["iperf_port"], output_pcap))
                time.sleep(main_config["time_each_flow"] + 2 * main_config["time_flow_interval"])
                os.system('killall tcpdump')
                os.system("python3 my_subprocess.py pcap2txt --mode tcp --file-path {} &".format(output_pcap))
            os.system('killall iperf3')
            print("Server One flow finished~")
        if message == "END":
            print("Client Test done, exit")
            server_socket.close()
            exit()



def download_iperf_wireshark():
    print("Download iperf server, start~~")
    main_config = utils.parse_config("config/config.json")["download_iperf_wireshark"]
    if main_config["variant"] in main_config["variants_list"] and main_config["variant"] != "udp":
        os.system("sudo sysctl net.ipv4.tcp_congestion_control={}".format(main_config["variant"]))
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(tuple(main_config["server_cmd_address"]))
    server_socket.listen(10)
    while True:
        client_socket, client_address = server_socket.accept()
        print("Recieve from client {}".format(client_address))
        count = 0
        message = ""
        while True:
            count = count + 1
            data = client_socket.recv(1024).decode("utf-8")
            message = message + data
            if "##DOKI##" in data:
                break
        client_socket.close()
        message = message.replace("##DOKI##", "")
        if message == "Start":
            os.system("iperf3 -s -p 7777 &")
            time.sleep(main_config["time_each_flow"] + 2 * main_config["time_flow_interval"])
            os.system('killall iperf3')
            print("Server One flow finished~")
        if message == "END":
            print("Client Test done, exit")
            server_socket.close()
            exit()




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













if __name__ == '__main__':
    main()
