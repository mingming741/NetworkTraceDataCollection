import socket

import context
import utils
from data_collection import collector, analyzer



def main():
    host_machine_config = utils.parse_config("config/host_machine_config.json")
    test_config_download = utils.parse_config("config/test_config_all.json")["iperf_tcpdump_download"]
    test_config_upload = utils.parse_config("config/test_config_all.json")["iperf_tcpdump_upload"]
    web_server_config = utils.parse_config("config/web_server_config.json")
    role = host_machine_config[socket.gethostname()]["role"]
    if role == "server":
        data_collector = collector.TraceDataCollectionServer(host_machine_config)
    if role == "client":
        data_collector = collector.TraceDataCollectionClient(host_machine_config)

    data_collector.print_attribute()

    #download_result_log = data_collector.iperf_tcpdump_download(test_config_download)
    #upload_result_log = data_collector.iperf_tcp_dump_upload(test_config_upload)

    data_analyzer = analyzer.TraceDataAnalyzer(web_server_config)
    data_analyzer.draw_graph("log/iperf_tcpdump_result/CSL_4G_download_bbr_-1/")
    data_analyzer.post_file_to_server("log/iperf_tcpdump_result/CSL_4G_download_bbr_-1/")



if __name__ == '__main__':
    main()
