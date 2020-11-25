import socket
import subprocess
import os
import time

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
        self.client_ip_dual = self.config["client_ip_dual"]
        self.peer_hostname = self.config["peer_hostname"]
        self.peer_config = self.host_machine_config[self.peer_hostname]
        self.server_ip = self.peer_config["server_ip"]

    def iperf_tcpdump_download(self, test_config):
        task_name = test_config["task_name"]
        network = self.SIM
        direction = "download"
        variant = test_config["variant"]
        experiment_id = test_config["experiment_id"]
        pcap_result_path = os.path.join(test_config["pcap_path"], "".format(test_config["task_name"], variant, experiment_id))

        iperf_logging_interval = test_config["iperf_logging_interval"]
        udp_sending_rate = test_config["udp_sending_rate"]
        task_time = test_config["task_time"]
        iperf_port = test_config["iperf_port"]

        os.system("sudo sysctl net.ipv4.tcp_congestion_control={}".format(variant))
        #os.system("tcpdump -i any tcp src port {} -w {} > /dev/null 2>&1 &".format(server_iperf_port, output_pcap))
        while True:
            P_iperf_client = subprocess.Popen("iperf3 -c {} -p {} -R -t {} -i {}".format(self.server_ip, iperf_port, task_time, iperf_logging_interval) , shell=True)
            P_iperf_client.wait(1)
            if P_iperf_client.poll() == 0:
                print(P_iperf_client.communicate()[1])
                break
            else:
                print("Error to connect with iperf3 server, retry...")
                time.sleep(1)


    def iperf_tcp_dump_upload(self, test_config):
        pass




class TraceDataCollectionServer(TraceDataCollector):
    def __init__(self, init_config, role="server"):
        super(TraceDataCollectionServer, self).__init__(init_config, role)
        self.server_ip = self.config["server_ip"]
        self.peer_hostname = self.config["peer_hostname"]
        self.peer_config = self.host_machine_config[self.peer_hostname]
        self.SIM = self.peer_config["SIM"]

    def iperf_tcpdump_download(self, test_config):
        task_name = test_config["task_name"]
        network = self.SIM
        direction = "download"
        variant = test_config["variant"]
        experiment_id = test_config["experiment_id"]
        pcap_result_path = os.path.join(test_config["pcap_path"], "".format(test_config["task_name"], variant, experiment_id))

        total_run = int(test_config["total_run"])
        iperf_logging_interval = test_config["iperf_logging_interval"]
        udp_sending_rate = test_config["udp_sending_rate"]
        task_time = test_config["task_time"]
        iperf_port = test_config["iperf_port"]

        process_iperf = subprocess.Popen("iperf3 -s -p {} -i {} 2> /dev/null &".format(iperf_port, iperf_logging_interval), shell=True)

    def iperf_tcp_dump_upload(self, test_config):
        pass











if __name__ == '__main__':
    main()
