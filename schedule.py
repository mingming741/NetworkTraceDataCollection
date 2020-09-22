import json
import os
import time
import getpass
import copy
import socket
import random
from datetime import datetime, timezone

import utils



def main():
    meta_config = utils.parse_config("config/test_meta_config.json")
    tasks_list = utils.dict_key_to_ordered_list(meta_config["scheduling_config"])
    schedule_profile_list = get_schedule_profile(meta_config, tasks_list)
    schedule_profile_list_from_client = []
    this_machine = socket.gethostname()
    this_machine_profile = meta_config["test_machines"][this_machine]

    while True:
        current_datetime = datetime.now()
        if current_datetime.hour == meta_config["general_config"]["resume_time_hour"]:
            print("Entering scheduling, data collection start")

            if this_machine_profile["role"] ==  "client":
                time.sleep(meta_config["general_config"]["resume_check_peroid"] + 10)
                peer_machine = this_machine_profile["peer_machine"]
                peer_machine_profile = meta_config["test_machines"][peer_machine]
                server_address_port = (peer_machine_profile["ip"], 1999)
                for task in schedule_profile_list:
                    test_config = {}
                    test_config[task["name"]] = task["config"]
                    print("-- Run Experiment: {}, {}, {}".format(task["config"]["network"], task["name"], task["config"]["variant"]))
                    with open("config/config.json", 'w') as f:
                        json.dump(test_config, f, indent = 2)
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    retry_connect(client_socket, server_address_port)
                    retry_send(client_socket, (json.dumps(test_config) + "##DOKI##").encode("utf-8"))
                    message = doki_wait_receive_message(client_socket)
                    if message == "Done":
                        print("SYN with server successfully, start to run the experiment..\n")
                    else:
                        print("Error!!")
                    time.sleep(5)
                    main_config = utils.parse_config("config/config.json")
                    for key in main_config:
                        task_name = key
                    print("Experiment Start: {}, {}, {}".format(main_config[task_name]["network"], task_name, main_config[task_name]["variant"]))
                    os.system("sudo python3 client.py {}".format(task_name))
                    time.sleep(5)
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                retry_connect(client_socket, server_address_port)
                retry_send(client_socket, ("END" + "##DOKI##").encode("utf-8"))
                print("Experiment Done, start to analysis the log")
                time.sleep(5)
                for task in schedule_profile_list:
                    test_config = {}
                    test_config[task["name"]] = task["config"]
                    if task["name"] == "download_iperf_wireshark":
                        with open("config/config.json", 'w') as f:
                            json.dump(test_config, f, indent = 2)
                        time.sleep(3)
                        os.system("python3 analysis_trace.py download_iperf_wireshark --post=1")
                        time.sleep(3)

            if this_machine_profile["role"] == "server":
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                retry_bind(server_socket, (this_machine_profile["ip"], 1999))
                server_socket.listen(10)
                while True:
                    print("-- Wait client message to start the experiment")
                    client_socket, client_address = server_socket.accept()
                    print("Recieve from client {}".format(client_address))
                    message = doki_wait_receive_message(client_socket)
                    if message == "END":
                        break
                    else:
                        test_config = json.loads(message)
                        schedule_profile_list_from_client.append(message)
                        with open("config/config.json", 'w') as f:
                            json.dump(test_config, f, indent = 2)
                        retry_send(client_socket, ("Done" + "##DOKI##").encode("utf-8"))
                        print("SYN with client successfully, save client config and start to run experiment..\n")
                        main_config = utils.parse_config("config/config.json")
                        for key in main_config:
                            task_name = key
                        print("Experiment Start: {}, {}, {}".format(main_config[task_name]["network"], task_name, main_config[task_name]["variant"]))
                        os.system("sudo python3 server.py {}".format(task_name))
                print("Experiment Done, start to analysis the log")
                for test_config in schedule_profile_list_from_client:
                    if "upload_iperf_wireshark" in test_config:
                        with open("config/config.json", 'w') as f:
                            json.dump(json.loads(test_config), f, indent = 2)
                        time.sleep(3)
                        os.system("python3 analysis_trace.py upload_iperf_wireshark --post=1")
                        time.sleep(3)
            print("All test done Successfully~~")
        else:
            print("Scheduling will start at {} o'clock, Now is {} o'clock~~".format(meta_config["general_config"]["resume_time_hour"], current_datetime.hour))
            time.sleep(meta_config["general_config"]["resume_check_peroid"])


def doki_wait_receive_message(my_socket):
    print("Receive Peer message")
    message = ""
    while True:
        data = my_socket.recv(1024).decode("utf-8")
        message = message + data
        if "##DOKI##" in data:
            break
    message = message.replace("##DOKI##", "")
    return message



def retry_bind(my_socket, my_socket_address_port, retry_timeout=60, stable_wait_time=1):
    exit_flag = 0
    while not exit_flag:
        try:
            my_socket.bind(my_socket_address_port)
            time.sleep(stable_wait_time)
            exit_flag = 1
        except Exception as e:
            print("Exception happen when bind address: ".format(e))
            time.sleep(retry_timeout)
            print("Retry..")


def retry_connect(my_socket, server_address_port, retry_timeout=5, stable_wait_time=1):
    print("Connect to {}".format(server_address_port))
    exit_flag = 0
    while not exit_flag:
        try:
            my_socket.connect(server_address_port)
            time.sleep(stable_wait_time)
            exit_flag = 1
        except Exception as e:
            print("Exception happen when connect to server: ".format(e))
            time.sleep(retry_timeout)
            print("Retry..")


def retry_send(my_socket, message, retry_timeout=5, stable_wait_time=1):
    print("Send message {}".format(message))
    exit_flag = 0
    while not exit_flag:
        try:
            my_socket.send(message)
            time.sleep(stable_wait_time)
            exit_flag = 1
        except Exception as e:
            print("Exception happen send message: ".format(e))
            time.sleep(retry_timeout)
            print("Retry..")


def get_schedule_profile(meta_config, tasks_list):
    variants_list = utils.dict_key_to_ordered_list(meta_config["vaild_config"]["variants_list"])

    this_machine = socket.gethostname()
    this_machine_profile = meta_config["test_machines"][this_machine]
    peer_machine = this_machine_profile["peer_machine"]
    peer_machine_profile = meta_config["test_machines"][peer_machine]
    if this_machine_profile["role"] ==  "client":
        server_ip = peer_machine_profile["ip"]
    else:
        server_ip = peer_machine_profile["ip"]
    client_network = this_machine_profile["network"]
    schedule_profile_list = list()

    server_cmd_address_port_zero = random.randint(2000, 3000)
    if "download_iperf_wireshark" in tasks_list:
        for variant in variants_list:
            example_config = copy.deepcopy(meta_config["scheduling_config"]["download_iperf_wireshark"])
            example_config["server_ip"] =  server_ip
            example_config["server_cmd_address"] =  [server_ip, server_cmd_address_port_zero]
            server_cmd_address_port_zero = server_cmd_address_port_zero + 1
            example_config["variant"] =  variant
            example_config["network"] =  client_network
            example_config["variants_list"] =  variants_list
            example_config["result_generated_path"] =  os.path.join("trace", client_network, "download")
            schedule_profile_list.append({"name": "download_iperf_wireshark", "config": example_config})
    if "upload_iperf_wireshark" in tasks_list:
        for variant in variants_list:
            example_config = copy.deepcopy(meta_config["scheduling_config"]["upload_iperf_wireshark"])
            example_config["server_ip"] =  server_ip
            example_config["server_cmd_address"] =  [server_ip, server_cmd_address_port_zero]
            server_cmd_address_port_zero = server_cmd_address_port_zero + 1
            example_config["variant"] =  variant
            example_config["network"] =  client_network
            example_config["variants_list"] =  variants_list
            example_config["result_generated_path"] =  os.path.join("trace", client_network, "upload")
            schedule_profile_list.append({"name": "upload_iperf_wireshark", "config": example_config})
    return schedule_profile_list






if __name__ == '__main__':
    main()
