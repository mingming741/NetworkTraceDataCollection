import socket

import context
import utils
from data_collection import trace_data_collector



def main():
    host_machine_config = utils.parse_config("config/host_machine_config.json")
    role = host_machine_config[socket.gethostname()]["role"]
    if role == "server":
        data_collector = trace_data_collector.TraceDataCollectionServer(host_machine_config)
    if role == "client":
        data_collector = trace_data_collector.TraceDataCollectionClient(host_machine_config)

    data_collector.print_attribute()

    test_config = utils.parse_config("config/test_config_all.json")["iperf_tcpdump_download"]
    data_collector.iperf_tcpdump_download(test_config)



if __name__ == '__main__':
    main()
