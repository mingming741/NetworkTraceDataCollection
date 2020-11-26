import socket

import context
import utils
from collector import collector, analyzer
from schedule import scheduler



def main():
    test_scheduler()


def test_scheduler():
    host_machine_config = utils.parse_config("config/host_machine_config.json")
    role = host_machine_config[socket.gethostname()]["role"]
    if role == "server":
        my_scheduler = scheduler.TraceDataSchedulerServer()
    if role == "client":
        my_scheduler = scheduler.TraceDataSchedulerClient()

    my_scheduler.print_attribute()
    my_scheduler.scheduling()



def test_collector():
    host_machine_config = utils.parse_config("config/host_machine_config.json")
    test_config_download = utils.parse_config("config/test_config_all.json")["iperf_tcpdump_download"]
    test_config_upload = utils.parse_config("config/test_config_all.json")["iperf_tcpdump_upload"]
    role = host_machine_config[socket.gethostname()]["role"]
    if role == "server":
        data_collector = collector.TraceDataCollectionServer()
    if role == "client":
        data_collector = collector.TraceDataCollectionClient()

    data_collector.print_attribute()

    #download_result_log = data_collector.iperf_tcpdump_download(test_config_download)
    #upload_result_log = data_collector.iperf_tcp_dump_upload(test_config_upload)

    data_analyzer = analyzer.TraceDataAnalyzer()
    data_analyzer.draw_graph("log/iperf_tcpdump_result/CSL_4G_download_bbr_-1/")
    data_analyzer.post_file_to_server("log/iperf_tcpdump_result/CSL_4G_download_bbr_-1/")



if __name__ == '__main__':
    main()
