import json
import os
import time
import copy
import socket
import random
from datetime import datetime, timezone

import utils

def main():
    meta_config = utils.parse_config("config/test_meta_config.json")
    scheduling(meta_config)


def scheduling(meta_config):
    role, current_machine_group = find_machine_role(meta_config)
    print("This machine is the {} of group {}".format(role, current_machine_group))
    schedule_profile_list = get_schedule_profile(meta_config)
    scheduling_port_range = meta_config["general_config"]["scheduling_port_range"]
    scheduling_port_zero = random.randint(scheduling_port_range[0], scheduling_port_range[1])
    #print(schedule_profile_list)
    #exit()
    while True:
        current_datetime = datetime.now()
        if (current_datetime.hour == meta_config["general_config"]["resume_time_hour"]) or meta_config["general_config"]["resume_time_hour"] == -1:
            print("Time to entering scheduling, data collection start")
            if role ==  "client":
                scheduling_client(meta_config, schedule_profile_list, current_machine_group, scheduling_port_zero)
                scheduling_port_zero = scheduling_port_zero + 1
            if role == "server":
                scheduling_server(meta_config, schedule_profile_list, current_machine_group, scheduling_port_zero)
                scheduling_port_zero = scheduling_port_zero + 1
            print("All test done Successfully~~")
        else:
            print("Scheduling will start at {} o'clock, Now is {} o'clock~~".format(meta_config["general_config"]["resume_time_hour"], current_datetime.hour))
            time.sleep(meta_config["general_config"]["resume_check_peroid"])


def scheduling_client(meta_config, schedule_profile_list, current_machine_group, communication_port):
    time.sleep(meta_config["general_config"]["resume_check_peroid"] + 30) # wait for server start
    server_ip = meta_config["current_machine_group"]["server"][current_machine_group]
    server_address_port = (server_ip, communication_port)
    for test_config in schedule_profile_list:
        print("-- Run Experiment: {}, {}, {}".format(test_config["network"], test_config["task_name"], test_config["variant"]))
        with open("config/config.json", 'w') as f:
            json.dump(test_config, f, indent = 2)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        utils.retry_connect(client_socket, server_address_port)
        utils.retry_send(client_socket, (json.dumps(test_config) + "##DOKI##").encode("utf-8"))
        message = utils.doki_wait_receive_message(client_socket)
        if message == "scheduling_start":
            print("SYN with server successfully, start to run the experiment..\n")
        else:
            print("Error!!")
        time.sleep(5)
        os.system("sudo python3 client.py {}".format(test_config["task_name"]))
        time.sleep(10)
        if test_config["task_name"] == "download_iperf_wireshark":
            print("Experiment Done, Client analyze and upload log")
            os.system("python3 analysis_trace.py download_iperf_wireshark --post=1")
        elif test_config["task_name"] == "upload_iperf_wireshark":
            print("Experiment Done, Wait for server upload the log")
        time.sleep(60)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    utils.retry_connect(client_socket, server_address_port)
    utils.retry_send(client_socket, ("scheduling_end" + "##DOKI##").encode("utf-8"))


def scheduling_server(meta_config, schedule_profile_list, communication_port):
    time.sleep(meta_config["general_config"]["resume_check_peroid"])
    server_ip = meta_config["current_machine_group"]["server"][current_machine_group]
    server_address_port = (server_ip, communication_port)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    utils.retry_bind(server_socket, server_address_port)
    server_socket.listen(10)
    while True:
        print("-- Wait client message to start the experiment")
        client_socket, client_address = server_socket.accept()
        print("Recieve from client {}".format(client_address))
        message = utils.doki_wait_receive_message(client_socket)
        if message == "scheduling_end":
            break
        else:
            test_config = json.loads(message)
            with open("config/config.json", 'w') as f:
                json.dump(test_config, f, indent = 2)
            utils.retry_send(client_socket, ("scheduling_start" + "##DOKI##").encode("utf-8"))
            print("SYN with client successfully, save client config and start to run experiment..\n")
            main_config = utils.parse_config("config/config.json")
            for key in main_config:
                task_name = key
            print("Experiment Start: {}, {}, {}".format(main_config[task_name]["network"], task_name, main_config[task_name]["variant"]))
            os.system("sudo python3 server.py {}".format(task_name))
    print("Experiment Done, start to analysis the log")
    server_socket.close()


def scheduling_org(meta_config):
    schedule_profile_list = get_schedule_profile(meta_config, utils.dict_key_to_ordered_list(meta_config["scheduling_config"]))
    this_machine = socket.gethostname()
    this_machine_profile = meta_config["test_machines"][this_machine]

    while True:
        current_datetime = datetime.now()
        if (current_datetime.hour == meta_config["general_config"]["resume_time_hour"]) or meta_config["general_config"]["resume_time_hour"] == -1:
            print("Entering scheduling, data collection start")

            if this_machine_profile["role"] ==  "client":
                time.sleep(meta_config["general_config"]["resume_check_peroid"] + 60)
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
                    utils.retry_connect(client_socket, server_address_port)
                    utils.retry_send(client_socket, (json.dumps(test_config) + "##DOKI##").encode("utf-8"))
                    message = utils.doki_wait_receive_message(client_socket)
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
                utils.retry_connect(client_socket, server_address_port)
                utils.retry_send(client_socket, ("END" + "##DOKI##").encode("utf-8"))
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
                time.sleep(meta_config["general_config"]["resume_check_peroid"] + 30)
                schedule_profile_list_from_client = []
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                utils.retry_bind(server_socket, (this_machine_profile["ip"], 1999))
                server_socket.listen(10)
                while True:
                    print("-- Wait client message to start the experiment")
                    client_socket, client_address = server_socket.accept()
                    print("Recieve from client {}".format(client_address))
                    message = utils.doki_wait_receive_message(client_socket)
                    if message == "END":
                        break
                    else:
                        test_config = json.loads(message)
                        schedule_profile_list_from_client.append(message)
                        with open("config/config.json", 'w') as f:
                            json.dump(test_config, f, indent = 2)
                        utils.retry_send(client_socket, ("Done" + "##DOKI##").encode("utf-8"))
                        print("SYN with client successfully, save client config and start to run experiment..\n")
                        main_config = utils.parse_config("config/config.json")
                        for key in main_config:
                            task_name = key
                        print("Experiment Start: {}, {}, {}".format(main_config[task_name]["network"], task_name, main_config[task_name]["variant"]))
                        os.system("sudo python3 server.py {}".format(task_name))
                print("Experiment Done, start to analysis the log")
                server_socket.close()
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
                example_config = copy.deepcopy(meta_config["scheduling_config"]["download_iperf_wireshark"])
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
