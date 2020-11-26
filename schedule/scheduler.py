import socket
import subprocess
import os
import time
import logging
import json
import my_socket
from datetime import datetime

import utils



class TraceDataScheduler(object):
    def __init__(self, schedule_config=None, web_server_config=None, host_machine_config=None, role=None):
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)-1s [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d:%H:%M:%S')
        self.logger = logging.getLogger(__name__)
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
        if role in ["client", "server", None]:
            self.role = role
        else:
            raise Exception("Need to define a role for a trace collector")


    def print_attribute(self):
        for item in self.__dict__:
            if "config" not in item:
                self.logger.debug("{} : {}".format(item, self.__dict__[item]))


    def generate_test_config_list(self):
        test_config_list = []
        for test_config in self.scheduling_list:
            new_config = utils.merge_config(test_config, self.scheduling_general_config)
            test_config_list.append(new_config)
        return test_config_list



class TraceDataSchedulerClient(TraceDataScheduler):
    def __init__(self, schedule_config=None, web_server_config=None, host_machine_config=None, role="client"):
        super(TraceDataSchedulerClient, self).__init__(schedule_config, role)
        self.peer_hostname = self.config["peer_hostname"]
        self.peer_config = self.host_machine_config[self.peer_hostname]
        self.server_ip = self.peer_config["server_ip"]


    def scheduling(self):
        for i in range(0, len(self.test_config_list)):
            test_config = self.test_config_list[i]

            while True:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if not my_socket.retry_connect(client_socket, (self.server_ip, self.scheduling_server_port)):
                    logger.error("Connect To server Fail, retry")
                    time.sleep(60)
                    continue
                message = json.dumps({"operation": "test", "test_config": test_config})
                if not my_socket.retry_send(client_socket, message):
                    logger.error("Connect Send Message, retry")
                    time.sleep(60)
                    continue
                data_collector = collector.TraceDataCollectionClient(self.host_machine_config)
                data_collector.data_collection(test_config)
                break


class TraceDataSchedulerServer(TraceDataScheduler):
    def __init__(self, schedule_config=None, web_server_config=None, host_machine_config=None, role="server"):
        super(TraceDataSchedulerServer, self).__init__(schedule_config, role)
        self.server_ip = self.peer_config["server_ip"]


    def scheduling(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.retry_bind(server_socket, (self.server_ip, self.scheduling_server_port))
        server_socket.listen(10)
        while True:
            self.logger.info("Wait for client command")
            client_socket, client_address = server_socket.accept()
            self.logger.debug("Recieve from client {}".format(client_address))
            message = my_socket.wait_receive_message(client_socket)
            if message == None:
                self.logger.error("Recieve client message Error! Redo scheduling")
                client_socket.close()
                continue
            else:
                try:
                    message_json = json.loads(message)
                    if message_json["operation"] == "end":
                        break
                    if message_json["operation"] == "test":
                        test_config =  message_json["test_config"]
                        data_collector = collector.TraceDataCollectionServer(self.host_machine_config)
                        data_collector.data_collection(test_config)
                except Exception as e:
                    self.logger.error("Cannot decode client message! Redo scheduling")
                    client_socket.close()
                    continue
        self.logger.info("Server Exit Scheduling, Experiment Done")














if __name__ == '__main__':
    main()
