#! /usr/bin/python3

import socket
import datetime
import time
import os
import json
import glob
import shutil
import requests
from datetime import datetime, timezone

import utils


def main():
    utils.init_dir()
    parser = argparse.ArgumentParser(description='For different background job')
    parser.add_argument('function', type=str, help='the job')
    args = parser.parse_args()

    #udp_socket()
    if args.function == "upload_iperf_wireshark":
        upload_iperf_wireshark()
    if args.function == "upload_iperf_wireshark":
        download_iperf_wireshark()


def upload_iperf_wireshark():
    main_config = utils.parse_config("config/config.json")["upload_iperf_wireshark"]
    print("Upload iperf client, start~~")
    for i in range(0, int(main_config["total_run"])):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(tuple(main_config["server_cmd_address"]))
        this_cmd = "Start"
        message = this_cmd + "##DOKI##"
        client_socket.send(message.encode("utf-8"))
        time.sleep(main_config["time_flow_interval"])
        if main_config["variant"] == "udp":
            os.system("iperf3 -c {} -p {} --length 1472 -u -b {}m -t {} &".format(main_config["server_ip"], main_config["iperf_port"], main_config["udp_sending_rate"],main_config["time_each_flow"]))
            time.sleep(main_config["time_each_flow"] + main_config["time_flow_interval"])
            os.system('killall iperf3')
        if main_config["variant"] != "udp" and main_config["variant"] in main_config["variants_list"]:
            os.system("sudo sysctl net.ipv4.tcp_congestion_control={}".format(main_config["variant"]))
            os.system("iperf3 -c {} -p {} -t {} &".format(main_config["server_ip"], main_config["iperf_port"], main_config["time_each_flow"]))
            time.sleep(main_config["time_each_flow"] + main_config["time_flow_interval"])
            os.system('killall iperf3')
        time.sleep(main_config["time_flow_interval"])


def download_iperf_wireshark():
    main_config = utils.parse_config("config/config.json")["download_iperf_wireshark"]
    print("Download iperf client, start~~")
    if os.path.exists(main_config["result_path"]):
        shutil.rmtree(main_config["result_path"])
    os.mkdir(main_config["result_path"])
    os.system("sudo chmod 777 {}".format(main_config["result_path"]))
    os.mkdir(os.path.join(main_config["result_path"], main_config["variant"]))
    os.system("sudo chmod 777 {}".format(os.path.join(main_config["result_path"], main_config["variant"])))

    for i in range(0, int(main_config["total_run"])):
        #os.system("tcpdump -i any udp port " + str(config['host']['desktop']['port']) + " -w " + str(config["result_directory"]) + variant[j] + "/" + str(i) + ".pcap &")
        current_datetime = datetime.fromtimestamp(time.time())
        output_pcap = os.path.join(main_config["result_path"], main_config["variant"], "{}.pcap".format(current_datetime.strftime("%Y_%m_%d_%H_%M")))
        #print(output_pcap)
        if main_config["variant"] == "udp":
            os.system("tcpdump -i any udp port {} -w {} &".format(main_config["iperf_port"], output_pcap))
            os.system("iperf3 -c {} -p {} -R --length 1472 -u -b {}m -t {} &".format(main_config["server_ip"], main_config["iperf_port"], main_config["udp_sending_rate"],main_config["time_each_flow"]))
            time.sleep(main_config["time_each_flow"] + main_config["time_flow_interval"])
            os.system('killall iperf3')
            os.system('killall tcpdump')
            os.system("python3 my_subprocess.py pcap2txt --mode udp --file-path {} &".format(output_pcap))
        if main_config["variant"] != "udp" and main_config["variant"] in main_config["variants_list"]:
            os.system("tcpdump -i any tcp src port {} -w {} &".format(main_config["iperf_port"], output_pcap))
            os.system("iperf3 -c {} -p {} -R -t {} &".format(main_config["server_ip"], main_config["iperf_port"], main_config["time_each_flow"]))
            time.sleep(main_config["time_each_flow"] + main_config["time_flow_interval"])
            os.system('killall iperf3')
            os.system('killall tcpdump')
            os.system("python3 my_subprocess.py pcap2txt --mode tcp --file-path {} &".format(output_pcap))
    print("All test done Successfully!!")


def download_socket():
    main_config = utils.parse_config("config/config.json")["download_socket"]
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





def utf8len(s):
    return len(s.decode('utf-8'))


if __name__ == '__main__':
    main()
