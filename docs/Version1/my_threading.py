import threading
import inspect
import os
import utils
import logging
import time
from datetime import datetime
from threading import Timer

test_meta_config = utils.parse_config("config/test_meta_config.json")
log_level = utils.parse_logging_level(test_meta_config["general_config"]["logging_level"])
logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)
current_script = os.path.basename(__file__)


def Threading_tcpdump_capture_cycle(task_time, pcap_result_subpath_variant, server_iperf_port, selected_network, selected_direction, selected_variant):
    logger.debug("{}_{}--> Thread {} Start".format(current_script, inspect.currentframe().f_lineno,  inspect.stack()[0][3]))
    doki_timer = utils.DokiTimer(expired_time=task_time, repeat=True)
    output_pcap = os.path.join(pcap_result_subpath_variant, "{}.pcap".format(datetime.fromtimestamp(time.time()).strftime("%Y_%m_%d_%H_%M")))
    if selected_variant == "udp":
        logger.debug("{}_{}--> Output pcap to {}".format(current_script, inspect.currentframe().f_lineno,  output_pcap))
        os.system("tcpdump -i any udp port {} -w {} > /dev/null 2>&1 &".format(server_iperf_port, output_pcap))
        while True:
            if doki_timer.is_expire():
                os.system('killall tcpdump > /dev/null 2>&1')
                os.system("python3 my_subprocess.py pcap2txt --mode udp --file-path {} --post 1 --network {} --direction {} --variant {} &".format(output_pcap, selected_network, selected_direction, selected_variant))
                output_pcap = os.path.join(pcap_result_subpath_variant, "{}.pcap".format(datetime.fromtimestamp(time.time()).strftime("%Y_%m_%d_%H_%M")))
                logger.debug("Output pcap to {}".format(output_pcap))
                os.system("tcpdump -i any udp port {} -w {} > /dev/null 2>&1 &".format(server_iperf_port, output_pcap))
    if selected_variant != "udp":
        logger.debug("Output pcap to {}".format(output_pcap))
        os.system("tcpdump -i any tcp src port {} -w {} > /dev/null 2>&1 &".format(server_iperf_port, output_pcap))
        while True:
            if doki_timer.is_expire():
                os.system('killall tcpdump > /dev/null 2>&1')
                os.system("python3 my_subprocess.py pcap2txt --mode tcp --file-path {} --post 1 --network {} --direction {} --variant {} &".format(output_pcap, selected_network, selected_direction, selected_variant))
                output_pcap = os.path.join(pcap_result_subpath_variant, "{}.pcap".format(datetime.fromtimestamp(time.time()).strftime("%Y_%m_%d_%H_%M")))
                logger.debug("Output pcap to {}".format(output_pcap))
                os.system("tcpdump -i any tcp src port {} -w {} > /dev/null 2>&1 &".format(server_iperf_port, output_pcap))



def threading_command(command):
    os.system(command)
