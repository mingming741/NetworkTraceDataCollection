import socket
import subprocess
import os
import time
import logging
import json
from datetime import datetime

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
                self.logger.debug("{} : {}".format(item, self.__dict__[item]))


    def pcap_to_txt(self, file_full_path, output_file_name):
        if os.path.exists(file_full_path):
            os.system("tshark -r " + file_full_path + " -T fields -e frame.time_epoch -e frame.len > " + output_file_name)
            #os.system("rm " + file_full_path)
        else:
            self.logger.error("Output trace data:{} to {}".format(file_full_path, output_file_name))



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
        direction = test_config["direction"]
        variant = test_config["variant"]
        experiment_id = test_config["experiment_id"]
        pcap_result_path = os.path.join(test_config["pcap_path"], "{}_{}_{}_{}".format(network, direction, variant, experiment_id))

        iperf_logging_interval = test_config["iperf_logging_interval"]
        udp_sending_rate = test_config["udp_sending_rate"]
        task_time = test_config["task_time"]
        iperf_port = test_config["iperf_port"]

        utils.remake_public_dir(pcap_result_path)
        experiment_start_time = datetime.fromtimestamp(time.time()).strftime("%Y_%m_%d_%H_%M_%S")
        output_pcap = os.path.join(pcap_result_path, "{}_{}_{}_{}.pcap".format(network, direction, variant, experiment_start_time))

        if variant != "udp":
            os.system("tcpdump -i any tcp -s 96 src port {} -w {} > /dev/null 2>&1 &".format(iperf_port, output_pcap))
        else:
            os.system("tcpdump -i any udp -s 96 port {} -w {} > /dev/null 2>&1 &".format(iperf_port, output_pcap))
        client_timer = utils.DokiTimer(expired_time=task_time)
        while not client_timer.is_expire():
            try:
                if "retry_start_time" not in locals():
                    retry_start_time = time.time()
                if variant != "udp":
                    P_iperf_client = subprocess.Popen("exec iperf3 -c {} -p {} -R -t {} -i {}".format(self.server_ip, iperf_port, task_time, iperf_logging_interval) , shell=True)
                else:
                    P_iperf_client = subprocess.Popen("exec iperf3 -c {} -p {} -R --length 1472 -u -b {}m -t {} -i {}".format(self.server_ip, iperf_port, udp_sending_rate, task_time, iperf_logging_interval) , shell=True)
                P_iperf_client.wait(task_time)
                if time.time() - retry_start_time <= 5: # assume no experiment is running, retry
                    retry_start_time = time.time()
                    self.logger.warning("Error to connect with iperf3 server, retry...")
                    time.sleep(1)
                else:
                    break
            except subprocess.TimeoutExpired as timeout:
                if P_iperf_client.poll() == None:
                    self.logger.debug("Time up, Let iperf End")
                    P_iperf_client.terminate()
                    break
            except Exception as e:
                if P_iperf_client.poll() == 0:
                    self.logger.error("Exception happen, Let Server End")
                    P_iperf_client.terminate()
                    break
        self.logger.debug("Trace Send Done, start to analyze")
        output_txt_file_name = "{}txt".format(output_pcap[0:-4])
        trace_log = {"task_name": task_name, "network": network, "direction": direction, "variant": variant, "start_time": experiment_start_time, "task_time": task_time, "trace_file_name": output_txt_file_name, "udp_sending_rate": udp_sending_rate}
        with open(os.path.join(pcap_result_path ,"experiment_result.json"), "w") as f:
            json.dump(trace_log, f)
        self.pcap_to_txt(output_pcap, output_txt_file_name)
        self.logger.info("Download Client Done")
        return {"pcap_result_path": pcap_result_path, "status": 0}


    def iperf_tcp_dump_upload(self, test_config):
        task_name = test_config["task_name"]
        network = self.SIM
        direction = test_config["direction"]
        variant = test_config["variant"]
        experiment_id = test_config["experiment_id"]
        pcap_result_path = os.path.join(test_config["pcap_path"], "{}_{}_{}_{}".format(network, direction, variant, experiment_id))

        iperf_logging_interval = test_config["iperf_logging_interval"]
        udp_sending_rate = test_config["udp_sending_rate"]
        task_time = test_config["task_time"]
        iperf_port = test_config["iperf_port"]

        os.system("sudo sysctl net.ipv4.tcp_congestion_control={}".format(variant))
        client_timer = utils.DokiTimer(expired_time=task_time)
        while not client_timer.is_expire():
            try:
                if "retry_start_time" not in locals():
                    retry_start_time = time.time()
                if variant != "udp":
                    P_iperf_client = subprocess.Popen("exec iperf3 -c {} -p {} -t {} -i {}".format(self.server_ip, iperf_port, task_time, iperf_logging_interval) , shell=True)
                else:
                    P_iperf_client = subprocess.Popen("exec iperf3 -c {} -p {} --length 1472 -u -b {}m -t {} -i {}".format(self.server_ip, iperf_port, udp_sending_rate, task_time, iperf_logging_interval) , shell=True)
                P_iperf_client.wait(task_time)
                if time.time() - retry_start_time <= 5: # assume no experiment is running, retry
                    retry_start_time = time.time()
                    self.logger.warning("Error to connect with iperf3 server, retry...")
                    time.sleep(1)
                else:
                    break
            except subprocess.TimeoutExpired as timeout:
                if P_iperf_client.poll() == None:
                    self.logger.debug("Time up, Let iperf End")
                    P_iperf_client.terminate()
                    break
            except Exception as e:
                if P_iperf_client.poll() == 0:
                    self.logger.error("Exception happen, Let Server End")
                    P_iperf_client.terminate()
                    break
        self.logger.info("Upload Client Done")
        return {"status" : 0}



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
                self.logger.debug("Time up, Let iperf End")
                P_iperf_server.terminate()
        except Exception as e:
            if P_iperf_server.poll() == 0:
                self.logger.error("Exception happen, Let Server End")
                P_iperf_server.terminate()
        self.logger.info("Download Server Done")
        return {"status" : 0}


    def iperf_tcp_dump_upload(self, test_config):
        task_name = test_config["task_name"]
        network = self.SIM
        direction = test_config["direction"]
        variant = test_config["variant"]
        experiment_id = test_config["experiment_id"]
        pcap_result_path = os.path.join(test_config["pcap_path"], "{}_{}_{}_{}".format(network, direction, variant, experiment_id))

        iperf_logging_interval = test_config["iperf_logging_interval"]
        udp_sending_rate = test_config["udp_sending_rate"]
        task_time = test_config["task_time"]
        iperf_port = test_config["iperf_port"]

        utils.remake_public_dir(pcap_result_path)
        experiment_start_time = datetime.fromtimestamp(time.time()).strftime("%Y_%m_%d_%H_%M_%S")
        output_pcap = os.path.join(pcap_result_path, "{}_{}_{}_{}.pcap".format(network, direction, variant, experiment_start_time))

        if variant != "udp":
            os.system("tcpdump -i any tcp -s 96 src port {} -w {} > /dev/null 2>&1 &".format(iperf_port, output_pcap))
        else:
            os.system("tcpdump -i any udp -s 96 port {} -w {} > /dev/null 2>&1 &".format(iperf_port, output_pcap))

        try:
            P_iperf_server = subprocess.Popen("exec iperf3 -s -p {} -i {}".format(iperf_port, iperf_logging_interval), shell=True)
            P_iperf_server.wait(task_time)
        except subprocess.TimeoutExpired as timeout:
            if P_iperf_server.poll() == None:
                self.logger.debug("Time up, Let iperf End")
                P_iperf_server.terminate()
        except Exception as e:
            if P_iperf_server.poll() == 0:
                self.logger.error("Exception happen, Let Server End")
                P_iperf_server.terminate()

        self.logger.debug("Trace Send Done, start to analyze")
        output_txt_file_name = "{}txt".format(output_pcap[0:-4])
        trace_log = {"task_name": task_name, "network": network, "direction": direction, "variant": variant, "start_time": experiment_start_time, "task_time": task_time, "trace_file_name": output_txt_file_name, "udp_sending_rate": udp_sending_rate}
        with open(os.path.join(pcap_result_path ,"experiment_result.json"), "w") as f:
            json.dump(trace_log, f)
        self.pcap_to_txt(output_pcap, output_txt_file_name)
        self.logger.info("Upload Server Done")
        return {"pcap_result_path": pcap_result_path, "status": 0}





if __name__ == '__main__':
    main()
