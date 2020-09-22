#! /usr/bin/python3
# -*- coding: UTF-8 -*-

import cgi
import os
import json
import pandas as pd
from datetime import datetime
import matplotlib
import matplotlib.pylab as pylab
import matplotlib.pyplot as plt
from urllib.parse import parse_qs
import sys

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

html_dir = "/var/www/html/"
html_type = "html"
#html_type = "json"

def main():
    #default_content()
    content()
    #draw_graph("CSL_4G", "download", "udp", "2020_09_22_11", "2020_09_22_13")
    #test_image()



def content():
    header(html_type)
    try:
        if 'QUERY_STRING' in os.environ:
            get_query = os.environ['QUERY_STRING']
            querys = parse_qs(get_query)
            if "operation" in querys:
                if querys['operation'][0] == "draw_graph":
                    if ('network' in querys) and ('direction' in querys) and ('variant' in querys) and ('start_time' in querys) and ('end_time' in querys):
                        if 'scale' in querys:
                            if RepresentsInt(querys['scale'][0]) == True:
                                draw_graph(querys['network'][0], querys['direction'][0], querys['variant'][0], querys['start_time'][0], querys['end_time'][0], int(querys['scale'][0]))
                            else:
                                log_sentence("Scale need to be integer")
                        else:
                            draw_graph(querys['network'][0], querys['direction'][0], querys['variant'][0], querys['start_time'][0], querys['end_time'][0])
                    else:
                        log_sentence("Incomplete query string")
                if "operation" == "change_variant":
                    if 'variant' in querys:
                        handler_select_tcp_variants(querys['variant'][0])
                    else:
                        log_sentence("Incomplete query string")
            else:
                log_sentence("Please Select operation.")
    except Exception as e:
        print(e)
    footer(html_type)


def draw_graph(network, direction, variant, start_time, end_time, scale=None):
    start_datetime = datetime.strptime(start_time, "%Y_%m_%d_%H")
    end_datetime = datetime.strptime(end_time, "%Y_%m_%d_%H")
    start_timestamp = int(datetime.timestamp(start_datetime))
    end_timestamp = int(datetime.timestamp(end_datetime))

    log_sentence("Throughput for {}, {}, {}".format(network, direction, variant))
    log_sentence("Start at {} (ts:{}),  End at {} (ts:{})".format(start_datetime, end_datetime, end_time, end_timestamp))

    target_directory = "{}trace/{}/{}/{}/".format(html_dir, network, direction, variant)
    file_list = os.listdir(target_directory)
    file_list.sort()
    df_main = pd.DataFrame()
    for file in file_list:
        if file.endswith(".txt"):
            #log_sentence("Find record {}".format(file), 5)
            df_temp = pd.read_csv(os.path.join(target_directory, file), names=["time", "Bandwidth"], header=None, sep="\t")
            df_temp = df_temp[(df_temp["time"] >= start_timestamp) & (df_temp["time"] <= end_timestamp)]
            df_main = pd.concat( [df_main, df_temp], ignore_index=True)
    if scale ==  None:
        total_scale = int(max(df_main["time"].values) - min(df_main["time"].values))
        if total_scale <= 600:
            scale = 1
        elif total_scale > 600 and total_scale <= 36000:
            scale = 60
        elif total_scale > 36000 and total_scale <= 864000:
            scale = 3600
        elif total_scale > 864000:
            scale = 86400
    log_sentence("Scale: {}".format(scale))
    if df_main.shape[0] > 0:
        time_list = [int(x/scale) for x in df_main["time"].values]
        list_start_time = min(time_list)
        list_end_time = max(time_list)
        time_list = [x - list_start_time for x in time_list]
        Bandwidth_list = [round(x/1000000,3) for x in df_main["Bandwidth"].values]
        df_main = pd.DataFrame(data = {"time": time_list, "Bandwidth": Bandwidth_list})
        df_main = df_main.groupby(["time"]).mean().reset_index()
        time_list = df_main["time"].values #[_para_x_range[0]: _para_x_range[1]]
        Bandwidth_list = df_main["Bandwidth"].values #[_para_x_range[0]: _para_x_range[1]]

        fig, axs = plt.subplots(nrows=1, ncols=1, **figure_config["single"])
        fig.suptitle('Cellular Capacity with Time')
        axs.bar(time_list, Bandwidth_list, label='Throughput')
        axs.set_xlabel('Time, Bin size = {}s'.format(scale))
        axs.set_ylabel('Throughput (Mbps)')
        axs.set_xlim(left=-1, right=(max(time_list)+1))
        axs.set_ylim(bottom=0, top=(max(Bandwidth_list) * 1.2))
        fig_html_path = "graph/{}_{}_{}_{}_to_{}.png".format(network, direction, variant, start_time, end_time)
        fig_path = os.path.join(html_dir, fig_html_path)
        fig.savefig(fig_path, dpi=fig.dpi)
        print('<img src= ../{}>'.format(fig_html_path))
        #log_sentence("Save graph to {}".format(fig_path))
    else:
        log_sentence("The range you select has no record")


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False



def handler_select_tcp_variants(variant):
    try:
        command = "sudo /sbin/sysctl net.ipv4.tcp_congestion_control=" + variant + " > /dev/null &"
        if html_type == "html":
            print(command)
            log_sentence('Change TCP variant to ' + variant)
        return_value = os.system(command)
        if html_type == "json":
            return_json = {}
            return_json["variant"] = variant
            return_json["state"] = return_value
            print(json.dumps(return_json))

    except Exception as e:
        print(e)

def log_sentence(sentence, size=3):
    print('<h{}> {} </h{}>'.format(size, sentence, size))

def default_content():
    header("html")
    print('<h2> Testing for cgi work </h2>')
    footer("html")

def header(type):
    if type == "html":
        print("Content-type:text/html\n")
        print("\n")
        print('<html> <head> <meta charset="utf-8">')
        print('<title> Testing Handler </title>')
        print('</head> <body> ')
    if type == "json":
        print("Content-type:application/json\n")

def footer(type):
    if type == "html":
        print('</body> </html>')
    if type == "json":
        pass

if __name__ == '__main__':
    main()
