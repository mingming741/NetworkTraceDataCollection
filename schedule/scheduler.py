import socket
import subprocess
import os
import time
import logging
import json
from datetime import datetime

import utils



class TraceDataScheduler(object):
    def __init__(self, schedule_config=None, web_server_config=None, host_machine_config=None, role=None):
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
        self.scheduling_list = self.schedule_config["schedule_config"]
        self.scheduling_general_config = self.schedule_config["scheduling_general_config"]
        self.test_config_list = self.generate_test_config_list()
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
            new_config = util.merge_config(test_config, self.scheduling_general_config)
            test_config_list.append(new_config)
        return test_config_list





class TraceDataSchedulerClient(TraceDataScheduler):
    def __init__(self, schedule_config=None, web_server_config=None, host_machine_config=None, role="client"):
        super(TraceDataSchedulerClient, self).__init__(schedule_config, role)
        self.peer_hostname = self.config["peer_hostname"]
        self.peer_config = self.host_machine_config[self.peer_hostname]
        self.server_ip = self.peer_config["server_ip"]






class TraceDataSchedulerServer(TraceDataScheduler):
    def __init__(self, schedule_config=None, web_server_config=None, host_machine_config=None, role="server"):
        super(TraceDataSchedulerClient, self).__init__(schedule_config, role)
        self.server_ip = self.peer_config["server_ip"]
















if __name__ == '__main__':
    main()
