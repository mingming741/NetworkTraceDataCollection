
import json
import os
import utils
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
from datetime import datetime, timezone
import pathlib


analysis_category = ["CIF", "VC", "NTC", "APPU", "IDX", "PLT"]

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
    args = parser.parse_args()
    main_config = utils.parse_config("config/config.json")[args.function]
    result_generate_iperf_wireshark(main_config)
    #result_draw_iperf_wireshark(main_config)


def result_generate_iperf_wireshark(main_config):
    time_unit_trace = main_config["time_unit_trace"] # default is 1000, minimum unit is s, can also be ms
    file_list = os.listdir(os.path.join(main_config["result_path"], main_config["variant"]))
    file_list.sort()
    assert len(file_list) != 0, "Empty Analysis directory"
    df_main = pd.DataFrame()
    print("Start read result files")
    for file in file_list:
        if file.endswith(".txt"):
            input_path = os.path.join(main_config["result_path"],  main_config["variant"], file)
            print("File: {}".format(input_path))
            df_temp = pd.read_csv(input_path, names=["time", "Length"], header=None, sep="\t")
            df_temp = pd.DataFrame(data = {"time": [int(x*1000/time_unit_trace) for x in df_temp["time"].values], "Bandwidth": [(x * 8 * 1000 /time_unit_trace) for x in df_temp["Length"].values]})
            df_temp = df_temp.groupby(["time"]).sum().reset_index() # Bandwidth in bps
            df_main = pd.concat( [df_main, df_temp], ignore_index=True)
    df_main = df_main.groupby(["time"]).sum().reset_index() # Bandwidth in bps
    print("Read Files done")

    df_main = pd.DataFrame(data = {"time" : df_main["time"].values, "datetime": [datetime.fromtimestamp(x).strftime("%Y_%m_%d_%H") for x in df_main["time"].values], "Bandwidth" : df_main["Bandwidth"].values})
    pathlib.Path(os.path.join(main_config["result_generated_path"], main_config["variant"])).mkdir(parents=True, exist_ok=True)
    for this_datetime in df_main["datetime"].unique():
        this_file_path = os.path.join(main_config["result_generated_path"], main_config["variant"],"download_{}_{}.txt".format(main_config["variant"], this_datetime))
        df_temp = df_main[df_main["datetime"] == this_datetime]
        df_temp.to_csv(this_file_path, index = False, header=False,columns=["time","Bandwidth"], sep="\t")
    print("Generate trace done~~")


def result_draw_iperf_wireshark(main_config):
    # analysis result file and generate trace:
    file_list = os.listdir(os.path.join(main_config["result_generated_path"], main_config["variant"]))
    file_list.sort()
    assert len(file_list) != 0, "Empty Analysis directory"
    df_main = pd.DataFrame()
    for file in file_list:
        if file.endswith(".txt"):
            input_path = os.path.join(main_config["result_generated_path"], main_config["variant"], file)
            #print(input_path)
            df_temp = pd.read_csv(input_path, names=["time", "Bandwidth"], header=None, sep="\t")
            df_main = pd.concat( [df_main, df_temp], ignore_index=True)

    print("Start time: {}".format(datetime.fromtimestamp(min(df_main["time"].values))))
    print("End time: {}".format(datetime.fromtimestamp(max(df_main["time"].values))))
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
