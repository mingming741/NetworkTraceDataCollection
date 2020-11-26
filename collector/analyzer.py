import json
import os
import time
import logging
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
from datetime import datetime, timezone
import argparse

import requests
import utils

if "PLT" in ["PLT"]:
    plot_lines = dict(
        normal = {"linewidth" : 4, "color" : "blue", "linestyle" : "-"},
        pdf = {"linewidth" : 4, "color" : "blue", "linestyle" : "--"},
        cdf = {"linewidth" : 4, "color" : "red", "linestyle" : "--"},
        model_fit = {"linewidth" : 4, "color" : "black", "linestyle" : "-"},
        empty = {"linewidth" : 0, "color" : "white", "linestyle" : "-"}
    )
    plot_color_cycle = ["blue", "green", "red", "pink", "black"]
    figure_config = dict(
        single = {"figsize" : (20, 8)},
        full = {"figsize" : (20, 12)},
    )
    default_font_weight = "black"
    default_font_size = dict(
        title = 0,
        text = 22
    )
    plot_default_setting_params = {
        "figure.figsize" : (20, 12),
        "figure.titlesize" : default_font_size["title"],
        "figure.titleweight" : default_font_weight,
        "font.size" : default_font_size["text"],
        "font.weight" : default_font_weight,
        "xtick.labelsize": default_font_size["text"],
        "ytick.labelsize": default_font_size["text"],
        "axes.labelsize": default_font_size["text"],
        "axes.labelweight": default_font_weight,
        "legend.fontsize" : default_font_size["text"],
        "legend.loc" : 'upper right',
        "axes.formatter.limits": (-5, 4),
        "figure.subplot.left": 0.08,
        "figure.subplot.right": 0.92,
        "figure.subplot.bottom": 0.095,
        "figure.subplot.top": 0.95
    }
    pylab.rcParams.update(plot_default_setting_params)


class TraceDataAnalyzer(object):
    def __init__(self, web_server_config):
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)-1s [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d:%H:%M:%S')
        self.logger = logging.getLogger(__name__)
        self.web_server_config = web_server_config
        self.web_server_ip = self.web_server_config["web_interface_server_ip"]
        self.web_interface_dir = self.web_server_config["web_interface_dir"]

    def draw_graph(self, test_result_path, time_scale=None):
        # time_scale, 1 is second, 1000 is milli second, 60 is minutes
        test_result = utils.parse_config(os.path.join(test_result_path, "experiment_result.json"))
        df_result = pd.read_csv(test_result["trace_file_name"], names=["time", "packet_size"], header=None, delimiter='\t')

        pre_config_timescale = {"hour": 3600, "minute": 60, "second":1, "millisecond": 0.001}
        if time_scale in pre_config_timescale:
            time_scale_unit = pre_config_timescale[time_scale]
        else:
            task_time = test_result["task_time"] # also in seconds
            if task_time / 3600 >= 2: # more than 4 hours trace
                time_scale = "hour"
                time_scale_unit = pre_config_timescale[time_scale]
            elif task_time / 60 >= 10: # more than 10 minutes
                time_scale = "minute"
                time_scale_unit = pre_config_timescale[time_scale]
            elif task_time / 1 >= 10: # more than 10 secods
                time_scale = "second"
                time_scale_unit = pre_config_timescale[time_scale]
            else:
                time_scale = "millisecond"
                time_scale_unit = pre_config_timescale[time_scale]
        df_result = pd.DataFrame(data={"time" : [int(x/time_scale_unit) for x in df_result["time"].values], "packet_size" : df_result["packet_size"].values}).groupby("time").sum().reset_index()
        df_throughput = pd.DataFrame(data={"time" : df_result["time"].values, "throughput" : [int(x/(1000000*time_scale_unit)) for x in df_result["packet_size"].values]}) # throughput in Mbps
        x_plot = df_throughput["time"].values
        count_list = df_throughput["throughput"].values
        fig, axs = plt.subplots(nrows = 1, ncols = 1, **figure_config["single"])
        axs.bar(x = x_plot, height = count_list, width = 0.8, label="Throughput")
        axs.set_ylabel("Throughput (Mbps)")
        axs.set_xlabel('Time ({})'.format(time_scale))
        axs.set_ylim(bottom=0, top=max(count_list) * 1.2)
        axs.set_xlim(left=min(x_plot)-1, right=max(x_plot)+1)
        plt.savefig(test_result["graph_path"])
        plt.close()


    def get_db_info(self):
        server_url = 'http://{}/{}fields_value.php'.format(self.web_server_ip, self.web_interface_dir)
        data = requests.get(server_url, dict(field='Network')).json()
        network_dict = {}
        for i in range(0, len(data)):
            network_dict[data[i]["Network"]] = data[i]["ID"]
        data = requests.get(server_url, dict(field='Variant')).json()
        variant_dict = {}
        for i in range(0, len(data)):
            variant_dict[data[i]["Variant"]] = data[i]["ID"]
        data = requests.get(server_url, dict(field='Direction')).json()
        direction_dict = {}
        for i in range(0, len(data)):
            direction_dict[data[i]["Direction"]] = data[i]["ID"]
        return network_dict, variant_dict, direction_dict


    def post_file_to_server(self, test_result_path):
        self.logger.info("Post {} to server".format(test_result_path))
        server_url = 'http://{}/{}handler.php?action=Upload_Record'.format(self.web_server_ip, self.web_interface_dir )
        test_result = utils.parse_config(os.path.join(test_result_path, "experiment_result.json"))
        network = test_result['network']
        variant = test_result['variant']
        direction = test_result['direction']
        Start_Time = test_result['start_time']
        Task_Time = test_result['task_time']
        Task_Name = test_result['task_name']
        file_path = test_result['trace_file_name']
        graph_path = test_result['graph_path']
        network_dict, variant_dict, direction_dict = self.get_db_info()
        parameters = {"Network_ID": network_dict[network], "Variant_ID": variant_dict[variant], "Direction_ID": direction_dict[direction], "Start_Time": Start_Time,"Task_Time": Task_Time,"Task_Name": Task_Name}
        files = {'file': open(file_path,'rb'), 'graph': open(graph_path,'rb')}
        response = requests.post(server_url, files=files, data=parameters)
        self.logger.debug(response.json())







if __name__ == '__main__':
    main()
