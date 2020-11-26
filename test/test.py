import socket

import context
import utils
from data_collection import collector, analyzer



def main():
    host_machine_config = utils.parse_config("config/host_machine_config.json")
    test_config = utils.parse_config("config/test_config_all.json")["iperf_tcpdump_download"]
    web_server_config = utils.parse_config("config/web_server_config.json")
    role = host_machine_config[socket.gethostname()]["role"]
    if role == "server":
        data_collector = collector.TraceDataCollectionServer(host_machine_config)
    if role == "client":
        data_collector = collector.TraceDataCollectionClient(host_machine_config)

    data_collector.print_attribute()

    #data_collector.iperf_tcpdump_download(test_config)
    data_collector.iperf_tcp_dump_upload(test_config)



if __name__ == '__main__':
    main()
