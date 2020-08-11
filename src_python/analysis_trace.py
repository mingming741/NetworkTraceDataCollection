
import json
import os
import utils
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab

main_config = utils.parse_config("config/config.json")
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
    result_analysis()

def result_analysis():
    # analysis result file and generate trace:
    result_config = utils.parse_config(main_config["test_config_file"])
    file_list = os.listdir(main_config["result_path"])
    file_list.sort()
    assert len(file_list) != 0, "Empty Analysis directory"
    df_main = pd.DataFrame()
    for file in file_list:
        if file.endswith(".txt"):
            input_path = os.path.join(main_config["result_path"], file)
            df_temp = pd.read_csv(input_path, names=["time", "Bandwidth"], header=None, sep="\t")
            df_main = pd.concat( [df_main, df_temp], ignore_index=True)

    time_list = [int(x) for x in df_main["time"].values]
    start_time = min(time_list)
    time_list = [x - start_time for x in time_list]
    Bandwidth_list = [round(x/1000000,3) for x in df_main["Bandwidth"].values]

    fig, axs = plt.subplots(nrows=1, ncols=1, sharex=False, sharey=False, num=1)
    fig.suptitle('Cellular Capacity with Time')
    axs.plot(time_list, Bandwidth_list, label='Throughput', **plot_lines["normal"])
    axs.set_xlabel('Time')
    axs.set_ylabel('Throughput')
    plt.show()



    
















if __name__ == '__main__':
    main()