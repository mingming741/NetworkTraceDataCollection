import json
import os
import time
import copy
import socket
import random
from datetime import datetime, timezone

import utils
import my_socket

def main():
    meta_config = utils.parse_config("config/test_meta_config.json")
    scheduling(meta_config)


def scheduling(meta_config):
    role, current_machine_group = find_machine_role(meta_config)
    print("This machine is the {} of group {}".format(role, current_machine_group))
    schedule_profile_list = get_schedule_profile(meta_config)
    scheduling_port_zero = meta_config["general_config"]["scheduling_port_zero"]
    while True:
        current_datetime = datetime.now()
        if (current_datetime.hour == meta_config["general_config"]["resume_time_hour"]) or meta_config["general_config"]["resume_time_hour"] == -1:
            print("\n------------------------------------")
            print("Time to entering scheduling, data collection start")
            if role ==  "client":
                time.sleep(10) # wait for server start
                scheduling_client(meta_config, schedule_profile_list, current_machine_group, scheduling_port_zero)
                scheduling_port_zero = scheduling_port_zero + 1
            if role == "server":
                scheduling_server(meta_config, schedule_profile_list, current_machine_group, scheduling_port_zero)
                scheduling_port_zero = scheduling_port_zero + 1
            print("All test done Successfully~~")
            print("------------------------------------\n")
        else:
            print("Scheduling will start at {} o'clock, Now is {} o'clock~~".format(meta_config["general_config"]["resume_time_hour"], current_datetime.hour))
            time.sleep(meta_config["general_config"]["resume_check_peroid"])


def scheduling_client(meta_config, schedule_profile_list, current_machine_group, communication_port):
    temp_config_file = meta_config["general_config"]["temp_config_file"]
    server_ip = meta_config["test_machines_group"]["server"][current_machine_group]["ip"]
    server_address_port = (server_ip, communication_port)
    index = 0
    while index < len(schedule_profile_list):
        main_config = schedule_profile_list[index]
        for key in main_config:
            task_name = key
        print("-- Run Experiment: {}, {}, {}".format(main_config[task_name]["network"], task_name, main_config[task_name]["variant"]))
        with open(temp_config_file, 'w') as f:
            json.dump(main_config, f, indent = 2)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not my_socket.retry_connect(client_socket, server_address_port):
            utils.fail_and_wait("Connect Fail, redo secheduling", 60)
            continue
        if not my_socket.retry_send(client_socket, (json.dumps(main_config) + "##DOKI##").encode("utf-8")):
            utils.fail_and_wait("Send Fail, redo secheduling", 60)
            continue
        message = my_socket.doki_wait_receive_message(client_socket)
        if message == "scheduling_start":
            print("SYN with server successfully, start to run the experiment..\n")
        else:
            print("Error with message: {}".format(message))
            utils.fail_and_wait("Receive Fail, redo secheduling", 60)
            continue
        time.sleep(5)
        os.system("sudo python3 client.py {} --config_path={}".format(task_name, temp_config_file))
        print("-- Experiment: {}, {}, {} Done".format(main_config[task_name]["network"], task_name, main_config[task_name]["variant"]))
        time.sleep(10)
        index =  index + 1

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.retry_connect(client_socket, server_address_port)
    my_socket.retry_send(client_socket, ("scheduling_end" + "##DOKI##").encode("utf-8"))
    time.sleep(10)
    print("All Experiment Done, Start to analysis the log")
    for main_config in schedule_profile_list:
        if "download_iperf_wireshark" in main_config:
            with open(temp_config_file, 'w') as f:
                json.dump(main_config, f, indent = 2)
            os.system("python3 analysis_trace.py download_iperf_wireshark --post=1 --config_path={}".format(temp_config_file))
            time.sleep(10)


def scheduling_server(meta_config, schedule_profile_list, current_machine_group, communication_port):
    temp_config_file = meta_config["general_config"]["temp_config_file"]
    server_ip = meta_config["test_machines_group"]["server"][current_machine_group]["ip"]
    server_address_port = (server_ip, communication_port)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.retry_bind(server_socket, server_address_port)
    server_socket.listen(10)
    schedule_profile_list = []
    while True:
        print("-- Wait client message to start the experiment")
        client_socket, client_address = server_socket.accept()
        print("Recieve from client {}".format(client_address))
        message = my_socket.doki_wait_receive_message(client_socket)
        if message == None:
            print("Recieve client message Error!")
            continue
        if message == "scheduling_end":
            break
        else:
            main_config = json.loads(message)
            schedule_profile_list.append(main_config)
            for key in main_config:
                task_name = key
            with open(temp_config_file, 'w') as f:
                json.dump(main_config, f, indent = 2)
            if not my_socket.retry_send(client_socket, ("scheduling_start" + "##DOKI##").encode("utf-8")):
                continue
            print("SYN with client successfully, save client config and start to run experiment..\n")
            print("Experiment Start: {}, {}, {}".format(main_config[task_name]["network"], task_name, main_config[task_name]["variant"]))
            os.system("sudo python3 server.py {} --config_path={}".format(task_name, temp_config_file))
            print("-- Experiment: {}, {}, {} Done".format(main_config[task_name]["network"], task_name, main_config[task_name]["variant"]))

    print("All Experiment Done, Start to analysis the log")
    for main_config in schedule_profile_list:
        if "upload_iperf_wireshark" in main_config:
            with open(temp_config_file, 'w') as f:
                json.dump(main_config, f, indent = 2)
            os.system("python3 analysis_trace.py upload_iperf_wireshark --post=1 --config_path={}".format(temp_config_file))
            time.sleep(10)
    server_socket.close()


def get_schedule_profile(meta_config):
    tasks_list = utils.dict_key_to_ordered_list(meta_config["scheduling_config"])
    variants_list = get_valid_variants_list(meta_config)
    if len(variants_list) == 0:
        raise Exception("Invalid TCP/UDP variant config, no variant is selected")

    server_client_packet_sending_port_range = meta_config["general_config"]["server_client_packet_sending_port_range"]
    server_client_packet_sending_port_zero = random.randint(server_client_packet_sending_port_range[0], server_client_packet_sending_port_range[1])
    role, test_machines_group = find_machine_role(meta_config)
    server_ip = meta_config["test_machines_group"]["server"][test_machines_group]["ip"]
    client_network = meta_config["test_machines_group"]["client"][test_machines_group]["network"]
    schedule_profile_list = list()

    if "download_iperf_wireshark" in tasks_list:
        if meta_config["scheduling_config"]["download_iperf_wireshark"]["enable"] == 1:
            for variant in variants_list:
                example_config = copy.deepcopy(meta_config["scheduling_config"]["download_iperf_wireshark"])
                example_config["variant"] =  variant
                example_config["server_ip"] =  server_ip
                example_config["network"] =  client_network
                example_config["server_packet_sending_port"] =  server_client_packet_sending_port_zero
                schedule_profile_list.append({"download_iperf_wireshark" : example_config})
                server_client_packet_sending_port_zero = server_client_packet_sending_port_zero + 1
    if "upload_iperf_wireshark" in tasks_list:
        if meta_config["scheduling_config"]["upload_iperf_wireshark"]["enable"] == 1:
            for variant in variants_list:
                example_config = copy.deepcopy(meta_config["scheduling_config"]["upload_iperf_wireshark"])
                example_config["variant"] =  variant
                example_config["server_ip"] =  server_ip
                example_config["network"] =  client_network
                example_config["server_packet_sending_port"] =  server_client_packet_sending_port_zero
                schedule_profile_list.append({"upload_iperf_wireshark" : example_config})
                server_client_packet_sending_port_zero = server_client_packet_sending_port_zero + 1
    return schedule_profile_list


def get_valid_variants_list(meta_config):
    variants_dict = meta_config["vaild_config"]["variants_list"]
    valid_variants_list = list()
    for variant in variants_dict:
        if variants_dict[variant] == 1:
            valid_variants_list.append(variant)
    return valid_variants_list


def find_machine_role(meta_config):
    # find the machine role by username
    this_machine = socket.gethostname()
    test_machines_group = meta_config["test_machines_group"]
    for role in test_machines_group:
        for machine_group in test_machines_group[role]:
            if this_machine == test_machines_group[role][machine_group]["hostname"]:
                return role, machine_group


if __name__ == '__main__':
    main()
