import socket
import subprocess
import os
import time
import logging

import utils


class TraceDataCollector(object):
    def __init__(self, host_machine_config, role=None):
        self.host_machine_config = host_machine_config
        self.hostname = socket.gethostname()
        self.config = self.host_machine_config[self.hostname]
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)-1s [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d:%H:%M:%S')
        self.logger = logging.getLogger(__name__)
        if role in ["client", "server", None]:
            self.role = role
        else:
            raise Exception("Need to define a role for a trace collector")

    def print_attribute(self):
        for item in self.__dict__:
            if "config" not in item:
                self.logger.info("{} : {}".format(item, self.__dict__[item]))



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


        #os.system("tcpdump -i any tcp src port {} -w {} > /dev/null 2>&1 &".format(server_iperf_port, output_pcap))
        try:
            while True:
                P_iperf_client = subprocess.Popen("exec iperf3 -c {} -p {} -R -t {} -i {}".format(self.server_ip, iperf_port, task_time, iperf_logging_interval) , shell=True)
                P_iperf_client.wait(task_time)
                if P_iperf_client.poll() == 0:
                    logger.debug(P_iperf_client.communicate()[1])
                    break
                else:
                    logger.warning("Error to connect with iperf3 server, retry...")
                    time.sleep(1)
        except subprocess.TimeoutExpired as timeout:
            if P_iperf_server.poll() == None:
                self.logger.info("Time up, Let iperf End")
                P_iperf_server.terminate()

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
        iperf_logging_interval = test_config["iperf_logging_interval"]
        task_time = test_config["task_time"]
        iperf_port = test_config["iperf_port"]

        os.system("sudo sysctl net.ipv4.tcp_congestion_control={}".format(test_config["variant"]))
        try:
            P_iperf_server = subprocess.Popen("exec iperf3 -s -p {} -i {}".format(iperf_port, iperf_logging_interval), shell=True)
            P_iperf_server.wait(task_time)
        except subprocess.TimeoutExpired as timeout:
            if P_iperf_server.poll() == None:
                self.logger.info("Time up, Let iperf End")
                P_iperf_server.terminate()
        except Exception as e:
            if P_iperf_server.poll() == 0:
                self.logger.error("Exception happen, Let Server End")
                P_iperf_server.terminate()

    def iperf_tcp_dump_upload(self, test_config):
        pass











if __name__ == '__main__':
    main()
