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
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)-1s [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d:%H:%M:%S')
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
        while True:
            for i in range(0, len(self.test_config_list)):
                #print(self.test_config_list)
                test_config = self.test_config_list[i]
                test_config["experiment_id"] = datetime.fromtimestamp(time.time()).strftime("%Y_%m_%d_%H_%M_%S")
                print(test_config)
                while True:
                    # Connect to server
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.server_ACK_time_out = False
                    if not my_socket.retry_connect(client_socket, (self.server_ip, self.scheduling_server_port), max_try=10):
                        self.logger.info("Unable to connect to server, Redo current experiment...")
                        continue
                    time.sleep(1)

                    # Send test config with server
                    my_socket.retry_send(client_socket, json.dumps({"operation": "test", "test_config": test_config}))
                    message = my_socket.wait_receive_message(client_socket, timeout=30)
                    if message == None:
                        self.logger.info("Server ACK timeout, try once experiment current experiment...")
                        self.server_ACK_time_out = True
                        server_ACK_time_out_Timer = utils.DokiTimer(expired_time=min(test_config["task_time"], 600))
                    elif message == "ACK":
                        self.logger.info("Recieve Server ACK, trace collection start")

                    # Data collection
                    time.sleep(1)
                    data_collection_result = self.data_collector.data_collection(test_config)
                    time.sleep(1)

                    if self.server_ACK_time_out == True and server_ACK_time_out_Timer.is_expire() == False:
                        # Server may goes into wait connection status
                        self.logger.info("Cannot connect server iperf, Redo current experiment...")
                        continue

                    # Exchange Uploading to web Information
                    if "pcap_result_path" in data_collection_result:
                        # In this case, server will wait for next connection, so does not need to send ACK
                        if self.data_analyzer.draw_graph(data_collection_result["pcap_result_path"]):
                            self.data_analyzer.post_file_to_server(data_collection_result["pcap_result_path"])
                            self.logger.info("Send trace to web interface Done")
                        else:
                            self.logger.error("No trace is generated, Redo current experiment")
                            continue
                    else: # wait for server to do the file upload, server will upload the file so cannot setup connection in this case
                        time.sleep(int(test_config["task_time"] / 90) + 1)
                        # 1 hour trace is 150MB, server bandwidth around 30 Mbps,
                    break
                self.logger.info("Client one experiment done~")

            if loop == False:
                break
            else:
                time.sleep(self.time_for_loop_scheduling)




class TraceDataSchedulerServer(TraceDataScheduler):
    def __init__(self, schedule_config=None, web_server_config=None, host_machine_config=None, role="server"):
        super(TraceDataSchedulerServer, self).__init__(schedule_config, web_server_config, host_machine_config, role)
        self.server_ip = self.config["server_ip"]


    def scheduling(self, loop=False):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.retry_bind(server_socket, (self.server_ip, self.scheduling_server_port))
        server_socket.listen(10)
        while True:
            # Wait and setup connection
            self.logger.info("Wait for Client connection..")
            (client_socket, client_address) = server_socket.accept()
            self.logger.debug("Recieve from client {}, wait for client command".format(client_address))

            # Recieve Client test config
            message = my_socket.wait_receive_message(client_socket, timeout=60)
            if message == None:
                self.logger.error("Recieve client message Error! Redo scheduling")
                client_socket.close()
                continue
            try:
                message_json = json.loads(message)
            except Exception as e:
                self.logger.error("Cannot decode client message! Redo scheduling")
                client_socket.close()
                continue

            # Trace collection
            if message_json["operation"] == "test":
                my_socket.retry_send(client_socket, "ACK")
                time.sleep(1)
                data_collection_result = self.data_collector.data_collection(message_json["test_config"])
                time.sleep(1)

                # Upload to server or wait for peer upload
                if "pcap_result_path" in data_collection_result:
                    # Client will wait some time and reconnect to server, if server does not ready, client will keep on connect
                    if self.data_analyzer.draw_graph(data_collection_result["pcap_result_path"]):
                        self.data_analyzer.post_file_to_server(data_collection_result["pcap_result_path"])
                        self.logger.info("Send trace to web interface Done")
                    else:
                        self.logger.error("No trace is generated, Redo current experiment")
                        continue

                # If client upload the trace, then server can exist and wait for another connection
                continue

            # Exiting
            self.logger.info("One Experiment Done, back to wait connection state")
            time.sleep(5)










if __name__ == '__main__':
    main()
