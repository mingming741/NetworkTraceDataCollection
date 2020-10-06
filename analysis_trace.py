
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
test_meta_config = utils.parse_config("config/test_meta_config.json")
logging.basicConfig(level=utils.parse_logging_level(meta_config["general_config"]["logging_level"]))
logger = logging.getLogger(__name__)
analysis_category = ["PLT"]

if "PLT" in analysis_category:
    default_font_weight = "black"
    default_font_size = dict(
        title = 24,
        text = 16
    )
    plot_lines = dict(
        normal = {"linewidth" : 4, "color" : "blue", "linestyle" : "-"},
        pdf = {"linewidth" : 4, "color" : "blue", "linestyle" : "--"},
        cdf = {"linewidth" : 4, "color" : "red", "linestyle" : "-"},
        model_fit = {"linewidth" : 4, "color" : "black", "linestyle" : "-"},
        empty = {"linewidth" : 0, "color" : "white", "linestyle" : "-"}
    )
    plot_color_cycle = ["blue", "green", "red", "pink", "black"]
    figure_config = dict(
        normal = {"figsize" : (12, 12)},
        single = {"figsize" : (12, 6)},
        multiple = {"figsize" : (18, 12)},
        full = {"figsize" : (20, 12)}
    )
    plot_default_setting_params = {
        "figure.figsize" : (12, 12),
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
        "axes.formatter.limits": (-6, 5)
    }
    pylab.rcParams.update(plot_default_setting_params)

    large_data_sample_upperbound = 1000000

def main():
    parser = argparse.ArgumentParser(description='For different background job')
    parser.add_argument('function', type=str, help='the job')
    parser.add_argument('--post', type=int, help='whether post to server')
    parser.add_argument('--display', type=int, help='whether draw graph')
    parser.add_argument('--config_path', type=str, help='path of config file')

    args = parser.parse_args()
    if args.function in ["download_iperf_wireshark", "upload_iperf_wireshark"]:
        if args.config_path:
            main_config = utils.parse_config(args.config_path)[args.function]
        else:
            main_config = utils.parse_config("config/config.json")[args.function]
        if args.post == 1:
            result_generate_iperf_wireshark(main_config, post_to_server=True)
        else:
            result_generate_iperf_wireshark(main_config, post_to_server=False)
        if args.display == 1:
            result_draw_iperf_wireshark(main_config)


def result_generate_iperf_wireshark(main_config, post_to_server=False):
    trace_min_time_unit = get_trace_unit(test_meta_config)
    selected_network = main_config["network"]
    selected_direction = main_config["direction"]
    selected_variant = main_config["variant"]
    trace_generated_path = os.path.join(main_config["trace_path"], main_config["network"], main_config["direction"], main_config["variant"])
    utils.make_public_dir(trace_generated_path)
    pcap_result_subpath_variant = os.path.join(main_config["pcap_path"], main_config["task_name"], main_config["variant"])
    file_list = os.listdir(pcap_result_subpath_variant)
    file_list.sort()
    assert len(file_list) != 0, "Empty Analysis directory"
    df_main = pd.DataFrame()
    logger.info("Start read result files")
    for file in file_list:
        if file.endswith(".txt"):
            input_path = os.path.join(pcap_result_subpath_variant, file)
            logger.debug("File: {}".format(input_path))
            if trace_min_time_unit != -1:
                df_temp = pd.read_csv(input_path, names=["time", "Length"], header=None, sep="\t")
                df_temp = pd.DataFrame(data = {"time": [int(x*1000/trace_min_time_unit) for x in df_temp["time"].values], "Length": [(x * 8 * 1000 /trace_min_time_unit) for x in df_temp["Length"].values]})
                df_temp = df_temp.groupby(["time"]).sum().reset_index()
                df_main = pd.concat( [df_main, df_temp], ignore_index=True)
            else:
                df_temp = pd.read_csv(input_path, names=["time", "Length"], header=None, sep="\t")
                df_temp = pd.DataFrame(data = {"time": [int(x*1000) for x in df_temp["time"].values], "Length": df_temp["Length"].values})
                df_main = pd.concat( [df_main, df_temp], ignore_index=True)
    if trace_min_time_unit != -1:
        df_main = df_main.groupby(["time"]).sum().reset_index()
        df_main = pd.DataFrame(data = {"time" : df_main["time"].values, "datetime": [datetime.fromtimestamp(int(x * trace_min_time_unit / 1000)).strftime("%Y_%m_%d_%H") for x in df_main["time"].values], "Length" : df_main["Length"].values})
    else:
        df_main = pd.DataFrame(data = {"time" : df_main["time"].values, "datetime": [datetime.fromtimestamp(int(x / 1000)).strftime("%Y_%m_%d_%H") for x in df_main["time"].values], "Length" : df_main["Length"].values})
    logger.info("Read Files done")
    for this_datetime in df_main["datetime"].unique():
        this_file_name = "{}_{}_{}_{}.txt".format(selected_network, selected_direction, selected_variant, this_datetime)
        this_file_path = os.path.join(trace_generated_path, this_file_name)
        df_temp = df_main[df_main["datetime"] == this_datetime]
        df_temp.to_csv(this_file_path, index = False, header=False,columns=["time","Length"], sep="\t")
        if post_to_server == True:
            post_file_to_server(this_file_path, selected_network, selected_direction, selected_variant)
    logger.trace("Generate trace done~~")


def get_db_info(server_host=test_meta_config["general_config"]["web_interface_server_ip"]):
    server_url = 'http://{}/php/fields_value.php'.format(server_host)
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


def post_file_to_server(file_path, network, direction, variant, server_host=test_meta_config["general_config"]["web_interface_server_ip"]):
    logger.info("Post {}->{}->{}->{} to server".format(network, direction, variant, file_path))
    server_url = 'http://{}/php/handler.php?action=Upload_Record'.format(server_host)
    network_dict, variant_dict, direction_dict = get_db_info()
    parameters = {"Network_ID": network_dict[network], "Variant_ID": variant_dict[variant], "Direction_ID": direction_dict[direction]}
    files = {'file': open(file_path,'rb')}
    response = requests.post(server_url, files=files, data=parameters)
    logger.debug(response.json())


def get_trace_unit(test_meta_config=test_meta_config):
    valid_units_mapping = test_meta_config["vaild_config"]["trace_min_unit"]
    trace_min_time_unit = test_meta_config["general_config"]["trace_min_time_unit"]
    if trace_min_time_unit in valid_units_mapping:
        return valid_units_mapping[trace_min_time_unit]
    else:
        raise Exception("Selected trace_min_time_unit in mete config is invalid")


def result_draw_iperf_wireshark(main_config):
    # analysis result file and generate trace:
    file_list = os.listdir(os.path.join(main_config["result_generated_path"], main_config["variant"]))
    file_list.sort()
    assert len(file_list) != 0, "Empty Analysis directory"
    df_main = pd.DataFrame()
    for file in file_list:
        if file.endswith(".txt"):
            input_path = os.path.join(main_config["result_generated_path"], main_config["variant"], file)
            df_temp = pd.read_csv(input_path, names=["time", "Bandwidth"], header=None, sep="\t")
            df_main = pd.concat( [df_main, df_temp], ignore_index=True)

    logger.info("Start time: {}".format(datetime.fromtimestamp(min(df_main["time"].values))))
    logger.info("End time: {}".format(datetime.fromtimestamp(max(df_main["time"].values))))
    time_bin_size = 60
    #_para_x_range = [1, -1]
    time_list = [int(x/time_bin_size) for x in df_main["time"].values]
    start_time = min(time_list)
    time_list = [x - start_time for x in time_list]


    Bandwidth_list = [round(x/1000000,3) for x in df_main["Bandwidth"].values]
    df_main = pd.DataFrame(data = {"time": time_list, "Bandwidth": Bandwidth_list})
    df_main = df_main.groupby(["time"]).mean().reset_index()
    time_list = df_main["time"].values #[_para_x_range[0]: _para_x_range[1]]
    Bandwidth_list = df_main["Bandwidth"].values #[_para_x_range[0]: _para_x_range[1]]


    fig, axs = plt.subplots(nrows=1, ncols=1, **figure_config["single"])
    fig.suptitle('Cellular Capacity with Time')
    #axs.plot(time_list, Bandwidth_list, label='Throughput', **plot_lines["normal"])
    axs.bar(time_list, Bandwidth_list, label='Throughput')
    axs.set_xlabel('Time, Bin size = {}s'.format(time_bin_size))
    axs.set_ylabel('Throughput (Mbps)')
    axs.set_xlim(left=-1, right=(max(time_list)+1))
    axs.set_ylim(bottom=0, top=(max(Bandwidth_list) * 1.2))
    plt.show()




def result_analysis_udp_socket():
    # analysis result file and generate trace:
    main_config = utils.parse_config("config/config.json")["udp_socket"]
    #result_config = utils.parse_config(main_config["test_config_file"])
    file_list = os.listdir(main_config["result_path"])
    file_list.sort()
    assert len(file_list) != 0, "Empty Analysis directory"
    df_main = pd.DataFrame()
    for file in file_list:
        if file.endswith(".txt"):
            input_path = os.path.join(main_config["result_path"], file)
            df_temp = pd.read_csv(input_path, names=["time", "Bandwidth"], header=None, sep="\t")
            df_main = pd.concat( [df_main, df_temp], ignore_index=True)

    time_bin_size = 60
    _para_x_range = [1, -1]
    time_list = [int(x/time_bin_size) for x in df_main["time"].values]
    start_time = min(time_list)
    time_list = [x - start_time for x in time_list]
    Bandwidth_list = [round(x/1000000,3) for x in df_main["Bandwidth"].values]
    df_main = pd.DataFrame(data = {"time": time_list, "Bandwidth": Bandwidth_list})
    df_main = df_main.groupby(["time"]).mean().reset_index()
    time_list = df_main["time"].values[_para_x_range[0]: _para_x_range[1]]
    Bandwidth_list = df_main["Bandwidth"].values[_para_x_range[0]: _para_x_range[1]]


    fig, axs = plt.subplots(nrows=1, ncols=1, **figure_config["single"])
    fig.suptitle('Cellular Capacity with Time')
    axs.plot(time_list, Bandwidth_list, label='Throughput', **plot_lines["normal"])
    axs.set_xlabel('Time, Bin size = {}s'.format(time_bin_size))
    axs.set_ylabel('Throughput (Mbps)')
    axs.set_xlim(left=1, right=(max(time_list)))
    axs.set_ylim(bottom=0, top=(max(Bandwidth_list) * 1.2))
    plt.show()



def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
















if __name__ == '__main__':
    main()
