import socket
import subprocess
import os
import time
import logging
import json
import threading
from datetime import datetime

import context
import utils
from collector import collector, analyzer
from schedule import my_socket



class TraceDataScheduler(object):
    def __init__(self, schedule_config=None, web_server_config=None, host_machine_config=None, role=None):
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)-1s [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d:%H:%M:%S')
        self.logger = logging.getLogger(__name__)
        if role in ["client", "server", None]:
            self.role = role
        else:
            raise Exception("Need to define a role for a trace collector")
        if web_server_config != None:
            self.web_server_config = web_server_config
        else:
            self.web_server_config = utils.parse_config("config/web_server_config.json")
        if host_machine_config != None:
            self.host_machine_config = host_machine_config
        else:
            self.host_machine_config = utils.parse_config("config/host_machine_config.json")
        if schedule_config != None:
            self.schedule_config = schedule_config
        else:
            self.schedule_config = utils.parse_config("config/schedule_config.json")
        self.hostname = socket.gethostname()
        self.config = self.host_machine_config[self.hostname]
        self.scheduling_list = self.schedule_config["scheduling_list"]
        self.scheduling_general_config = self.schedule_config["scheduling_general_config"]
        self.test_config_list = self.generate_test_config_list()
        self.scheduling_server_port = self.schedule_config["scheduling_server_port"]
        if self.role == "client":
            self.data_collector = collector.TraceDataCollectionClient(host_machine_config=self.host_machine_config)
        else:
            self.data_collector = collector.TraceDataCollectionServer(host_machine_config=self.host_machine_config)
        self.data_analyzer = analyzer.TraceDataAnalyzer(web_server_config=self.web_server_config)
        self.time_wait_peer_operation = self.schedule_config["time_wait_peer_operation"] # in seconds



    def print_attribute(self):
        for item in self.__dict__:
            if "config" not in item and "list" not in item:
                self.logger.debug("{} : {}".format(item, self.__dict__[item]))


    def generate_test_config_list(self):
        test_config_list = []
        for test_config in self.scheduling_list:
            new_config = utils.merge_config(test_config, self.scheduling_general_config)
            new_config["experiment_id"] = datetime.fromtimestamp(time.time()).strftime("%Y_%m_%d_%H_%M_%S")
            test_config_list.append(new_config)
        return test_config_list



class TraceDataSchedulerClient(TraceDataScheduler):
    def __init__(self, schedule_config=None, web_server_config=None, host_machine_config=None, role="client"):
        super(TraceDataSchedulerClient, self).__init__(schedule_config, web_server_config, host_machine_config, role)
        self.peer_hostname = self.config["peer_hostname"]
        self.peer_config = self.host_machine_config[self.peer_hostname]
        self.server_ip = self.peer_config["server_ip"]
        self.time_for_loop_scheduling = self.schedule_config["time_for_loop_scheduling"] # in seconds


    def scheduling(self, loop=False):
        self.exit = False
        while self.exit == False:
            for i in range(0, len(self.test_config_list)):
                test_config = self.test_config_list[i]

                while self.exit == False:
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    if not my_socket.retry_connect(client_socket, (self.server_ip, self.scheduling_server_port), max_try=10):
                        raise Exception("Unable to connect to server, exiting scheduling")
                    time.sleep(1)

                    # Exchange config with server
                    while self.exit == False:
                        if not my_socket.retry_send(client_socket, json.dumps({"operation": "test", "test_config": test_config})):
                            continue
                        message = my_socket.wait_receive_message(client_socket, timeout=30)
                        if message == None:
                            self.logger.info("Server ACK timeout, resend test config")
                            continue
                        elif message == "ACK":
                            self.logger.info("Recieve Server ACK, trace collection start")
                            break

                    # Data collection
                    data_collection_result = self.data_collector.data_collection(test_config)

                    # Exchange Uploading to web Information
                    if "pcap_result_path" in data_collection_result and self.exit == False:
                        self.data_analyzer.draw_graph(data_collection_result["pcap_result_path"])
                        self.data_analyzer.post_file_to_server(data_collection_result["pcap_result_path"])
                        while self.exit == False:
                            if not my_socket.retry_send(client_socket, "ACK"):
                                continue
                            message = my_socket.wait_receive_message(client_socket, timeout=30)
                            if message == None:
                                self.logger.info("Server ACK timeout, resend ACK")
                                continue
                            elif message == "ACK":
                                self.logger.info("Recieve Server ACK, current trace collection end")
                                break
                    else: # wait somethings for server to do operation
                        message = my_socket.wait_receive_message(client_socket, timeout=-1)
                        if message == "ACK":
                            if not my_socket.retry_send(client_socket, "ACK"):
                                continue
                    break

            if loop == False:
                self.exit = True
            else:
                time.sleep(self.time_for_loop_scheduling)

        self.logger.info("Client Exit Scheduling, Experiment Done")


class TraceDataSchedulerServer(TraceDataScheduler):
    def __init__(self, schedule_config=None, web_server_config=None, host_machine_config=None, role="server"):
        super(TraceDataSchedulerServer, self).__init__(schedule_config, web_server_config, host_machine_config, role)
        self.server_ip = self.config["server_ip"]


    def scheduling(self, loop=False):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.retry_bind(server_socket, (self.server_ip, self.scheduling_server_port))
        server_socket.listen(10)
        while True:
            self.logger.info("Wait for client connection..")
            (client_socket, client_address) = server_socket.accept()
            if self.is_running == False: # Create sub threading
                client_thread = threading.Thread(target=handle_client_connection, args=(client_socket, client_address), daemon=True)
                client_thread.start()
            elif self.is_running == True: # Discard current sub threading
                self.is_running = False
                while True:
                    if self.handle_client_connection_return == True: # wait for current sub threading exit
                        client_thread = threading.Thread(target=handle_client_connection, args=(client_socket, client_address), daemon=True)
                        client_thread.start()
                        break


    def handle_client_connection(self, client_socket, client_address):
        self.is_running = True
        self.handle_client_connection_return = False
        while self.is_running:
            self.logger.debug("Recieve from client {}, wait for client command".format(client_address))
            message = my_socket.wait_receive_message(client_socket)
            if message == None:
                self.logger.error("Recieve client message Error! Redo scheduling")
                client_socket.close()
                self.is_running = False
                break
            else:
                try:
                    message_json = json.loads(message)
                    if message_json["operation"] == "test" and self.is_running == True:
                        message = "ACK"
                        if not my_socket.retry_send(client_socket, message):
                            self.logger.error("Send Message, retry")
                            time.sleep(60)
                            continue
                        data_collection_result = self.data_collector.data_collection(message_json["test_config"])
                        if "pcap_result_path" in data_collection_result and self.is_running == True:
                            self.data_analyzer.draw_graph(data_collection_result["pcap_result_path"])
                            self.data_analyzer.post_file_to_server(data_collection_result["pcap_result_path"])
                            while self.is_running == True:
                                if not my_socket.retry_send(client_socket, "ACK"):
                                    continue
                                message = my_socket.wait_receive_message(client_socket, timeout=30)
                                if message == None:
                                    self.logger.info("Client ACK timeout, resend ACK")
                                    continue
                                elif message == "ACK":
                                    self.logger.info("Recieve Client ACK, current trace collection end")
                                    break
                        else:
                            message = my_socket.wait_receive_message(client_socket, timeout=-1)
                            if message == "ACK":
                                if not my_socket.retry_send(client_socket, "ACK"):
                                    continue

                except Exception as e:
                    self.logger.error("Cannot decode client message! Redo scheduling")
                    client_socket.close()
                    self.is_running = False
                    break
        self.handle_client_connection_return = True
        self.logger.info("Handler client connection threading exit..")















if __name__ == '__main__':
    main()
