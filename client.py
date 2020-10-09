#! /usr/bin/python3

import socket
import time
import os
import json
import shutil
import argparse
import logging
import threading
from threading import Timer
from datetime import datetime, timezone

import utils
import my_socket

test_meta_config = utils.parse_config("config/test_meta_config.json")
logging.basicConfig(level=utils.parse_logging_level(test_meta_config["general_config"]["logging_level"]))
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


def upload_iperf_wireshark(main_config=None):
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
    time_flow_interval = 5 # wait some time to keep stability


    logger.info("{}--> upload_iperf_wireshark, Start~~".format(current_script))
    for i in range(0, total_run):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.retry_connect(client_socket, server_address_port)
        my_socket.retry_send(client_socket, ("upload_iperf_start" + "##DOKI##").encode("utf-8"))
        time.sleep(time_flow_interval)
        client_socket.close()
        current_datetime = datetime.fromtimestamp(time.time())
        if selected_variant == "udp":
            os.system("iperf3 -c {} -p {} --length 1472 -u -b {}m -t {} -i {} 2> /dev/null &".format(server_ip, server_iperf_port, udp_sending_rate, task_time, iperf_logging_interval))
            time.sleep(task_time + time_flow_interval)
            os.system('killall iperf3 > /dev/null 2>&1')
        if selected_variant != "udp":
            os.system("sudo sysctl net.ipv4.tcp_congestion_control={}".format(selected_variant))
            os.system("iperf3 -c {} -p {} -t {} -i {} &".format(server_ip, server_iperf_port, task_time, iperf_logging_interval))
            time.sleep(task_time + time_flow_interval)
            os.system('killall iperf3 > /dev/null 2>&1')
        logger.info("{}--> {}, {}, {}, Done".format(current_script, selected_network, selected_direction, selected_variant))
        time.sleep(time_flow_interval)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.retry_connect(client_socket, server_address_port)
    my_socket.retry_send(client_socket, ("upload_iperf_end" + "##DOKI##").encode("utf-8"))
    client_socket.close()
    logger.info("{}--> upload_iperf_wireshark, All test Done~~".format(current_script))


def download_iperf_wireshark(main_config=None):
    if main_config == None:
        main_config = utils.parse_config("config/config.json")
    main_config = main_config["download_iperf_wireshark"]
    selected_network = main_config["network"]
    selected_direction = main_config["direction"]
    selected_variant = main_config["variant"]
    exec_mode = main_config["mode"]
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
    time_flow_interval = 5 # wait some time to keep stability

    utils.make_public_dir(pcap_result_path)
    utils.remake_public_dir(pcap_result_subpath_variant)
    logger.info("{}--> download_iperf_wireshark, Start~~".format(current_script))

    if exec_mode == "scheduling":
        for i in range(0, total_run):
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            my_socket.retry_connect(client_socket, server_address_port)
            my_socket.retry_send(client_socket, ("download_iperf_start" + "##DOKI##").encode("utf-8"))
            time.sleep(time_flow_interval)
            client_socket.close()
            current_datetime = datetime.fromtimestamp(time.time())
            output_pcap = os.path.join(pcap_result_subpath_variant, "{}.pcap".format(current_datetime.strftime("%Y_%m_%d_%H_%M")))
            if selected_variant == "udp":
                os.system("tcpdump -i any udp port {} -w {} > /dev/null 2>&1 &".format(server_iperf_port, output_pcap))
                os.system("iperf3 -c {} -p {} -R --length 1472 -u -b {}m -t {} -i {} 2> /dev/null &".format(server_ip, server_iperf_port, udp_sending_rate, task_time, iperf_logging_interval))
                time.sleep(task_time + time_flow_interval)
                os.system('killall iperf3 > /dev/null 2>&1')
                os.system('killall tcpdump > /dev/null 2>&1')
                os.system("python3 my_subprocess.py pcap2txt --mode udp --file-path {} &".format(output_pcap))
            if selected_variant != "udp":
                os.system("tcpdump -i any tcp src port {} -w {} > /dev/null 2>&1 &".format(server_iperf_port, output_pcap))
                os.system("iperf3 -c {} -p {} -R -t {} -i {} &".format(server_ip, server_iperf_port, task_time, iperf_logging_interval))
                time.sleep(task_time + time_flow_interval)
                os.system('killall iperf3 > /dev/null 2>&1')
                os.system('killall tcpdump > /dev/null 2>&1')
                os.system("python3 my_subprocess.py pcap2txt --mode tcp --file-path {} &".format(output_pcap))
            logger.info("{}--> {}, {}, {}, Done".format(current_script, selected_network, selected_direction, selected_variant))
            time.sleep(time_flow_interval)

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.retry_connect(client_socket, server_address_port)
        my_socket.retry_send(client_socket, ("download_iperf_end" + "##DOKI##").encode("utf-8"))
        client_socket.close()
        logger.info("{}--> download_iperf_wireshark, All test Done~~".format(current_script))

    if exec_mode == "continue":
        total_task_time =  31536000 # 1 year in seconds
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.retry_connect(client_socket, server_address_port)
        client_socket.close()
        while True:
            if selected_variant == "udp":
                logger.debug("{}--> iperf3 client start running".format(current_script))
                os.system("iperf3 -c {} -p {} -R --length 1472 -u -b {}m -t {} -i {} 2> /dev/null &".format(server_ip, server_iperf_port, udp_sending_rate, total_task_time, iperf_logging_interval))
                if "client_thread" not in locals():
                    client_thread = threading.Thread(target=Threading_tcpdump_capture_cycle, args=(task_time, pcap_result_subpath_variant), daemon=True)
                    client_thread.start()
                else:
                    if not client_thread.is_alive():
                        client_thread = threading.Thread(target=Threading_tcpdump_capture_cycle, args=(task_time, pcap_result_subpath_variant), daemon=True)
                        client_thread.start()


            if selected_variant != "udp":
                os.system("tcpdump -i any tcp src port {} -w {} > /dev/null 2>&1 &".format(server_iperf_port, output_pcap))
                os.system("iperf3 -c {} -p {} -R -t {} -i {} &".format(server_ip, server_iperf_port, task_time, iperf_logging_interval))
                time.sleep(task_time + time_flow_interval)
                os.system('killall iperf3 > /dev/null 2>&1')
                os.system('killall tcpdump > /dev/null 2>&1')
                os.system("python3 my_subprocess.py pcap2txt --mode tcp --file-path {} &".format(output_pcap))



def Threading_tcpdump_capture_cycle(task_time, pcap_result_subpath_variant):
    doki_timer = util.DokiTimer(expired_time=task_time, repeat=True)
    output_pcap = os.path.join(pcap_result_subpath_variant, "{}.pcap".format(datetime.fromtimestamp(time.time()).strftime("%Y_%m_%d_%H_%M")))
    os.system("tcpdump -i any udp port {} -w {} > /dev/null 2>&1 &".format(server_iperf_port, output_pcap))
    while True:
        if doki_timer.is_expire():
            os.system('killall tcpdump > /dev/null 2>&1')
            os.system("python3 my_subprocess.py pcap2txt --mode udp --file-path {} &".format(output_pcap))
            output_pcap = os.path.join(pcap_result_subpath_variant, "{}.pcap".format(datetime.fromtimestamp(time.time()).strftime("%Y_%m_%d_%H_%M")))
            os.system("tcpdump -i any udp port {} -w {} > /dev/null 2>&1 &".format(server_iperf_port, output_pcap))




def threading_command(command):
    os.system(command)





"""
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

"""


if __name__ == '__main__':
    main()
