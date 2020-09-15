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
    this_machine = socket.gethostname()
    this_machine_profile = meta_config["test_machines"][this_machine]

    if this_machine_profile["role"] ==  "client":
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
            client_socket.connect(server_address_port)
            print("Start sending config to server {}".format(server_address_port))
            message = json.dumps(test_config) + "##DOKI##"
            client_socket.send(message.encode("utf-8"))
            print("Wait for server ACK")
            message = ""
            while True:
                data = client_socket.recv(1024).decode("utf-8")
                message = message + data
                if "##DOKI##" in data:
                    break
            message = message.replace("##DOKI##", "")
            if message == "Done":
                print("SYN with server successfully, start to run the experiment..")
            print("\n")

            time.sleep(5)

            main_config = utils.parse_config("config/config.json")
            for key in main_config:
                task_name = key
            print("Experiment Start: {}, {}, {}".format(main_config[task_name]["network"], task_name, main_config[task_name]["variant"]))
            this_cmd = "sudo python3 client.py {}".format(task_name)
            os.system(this_cmd)

            time.sleep(10)
            if task_name == "download_iperf_wireshark":
                os.system("python3 analysis_trace.py {} &".format(task_name))
            time.sleep(10)



    if this_machine_profile["role"] == "server":
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address_port = (this_machine_profile["ip"], 1999)
        server_socket.bind(server_address_port)
        server_socket.listen(10)
        while True:
            print("-- Wait client message to start the experiment")
            client_socket, client_address = server_socket.accept()
            print("Recieve from client {}".format(client_address))
            message = ""
            while True:
                data = client_socket.recv(1024).decode("utf-8")
                message = message + data
                if "##DOKI##" in data:
                    break
            test_config = json.loads(message.replace("##DOKI##", ""))
            with open("config/config.json", 'w') as f:
                    json.dump(test_config, f, indent = 2)
            print("Receive client config file successfully, send ACK back to client")
            message = "Done" + "##DOKI##"
            client_socket.send(message.encode("utf-8"))
            print("SYN with client successfully, save client config and start to run experiment..")
            print("\n")

            time.sleep(5)

            main_config = utils.parse_config("config/config.json")
            for key in main_config:
                task_name = key
            print("Experiment Start: {}, {}, {}".format(main_config[task_name]["network"], task_name, main_config[task_name]["variant"]))
            this_cmd = "sudo python3 server.py {}".format(task_name)
            os.system(this_cmd)

            time.sleep(10)
            if task_name == "upload_iperf_wireshark":
                os.system("python3 analysis_trace.py {} &".format(task_name))
            time.sleep(10)


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
