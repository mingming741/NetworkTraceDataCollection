import socket

import utils


class TraceDataCollector(object):
    def __init__(self, host_machine_config, role=None):
        self.host_machine_config = host_machine_config
        self.hostname = socket.gethostname()
        self.config = self.host_machine_config[self.hostname]
        if role in ["client", "server", None]:
            self.role = role
        else:
            raise Exception("Need to define a role for a trace collector")

    def print_attribute(self):
        for item in self.__dict__:
            if "config" not in item:
                print("{} : {}".format(item, self.__dict__[item]))


class TraceDataCollectionClient(TraceDataCollector):
    def __init__(self, host_machine_config, role="client"):
        super(TraceDataCollectionClient, self).__init__(host_machine_config, role)
        self.SIM = self.config["SIM"]
        self.ip_dual = self.config["ip_dual"]
        self.peer_hostname = self.config["peer_hostname"]
        self.peer_config = self.host_machine_config[self.peer_hostname]
        self.server_ip = self.peer_config["ip"]

    def iperf_tcpdump_download(self):
        pass

    def iperf_tcp_dump_upload(self):
        pass




class TraceDataCollectionServer(TraceDataCollector):
    def __init__(self, init_config, role="server"):
        super(TraceDataCollectionServer, self).__init__(init_config, role)
        self.ip = self.config["ip"]
        self.peer_hostname = self.config["peer_hostname"]
        self.peer_config = self.host_machine_config[self.peer_hostname]
        self.client_SIM = self.peer_config["SIM"]

    def iperf_tcpdump_download(self):
        pass

    def iperf_tcp_dump_upload(self):
        pass
