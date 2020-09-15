import json
import os

def parse_config(path):
    with open(path) as json_data_file:
        data = json.load(json_data_file)
    return data

def init_dir():
    if not os.path.exists("result"):
        os.mkdir("result")
        os.system("sudo chmod 777 result")
    if not os.path.exists("trace"):
        os.mkdir("trace")
        os.system("sudo chmod 777 trace")


def dict_key_to_ordered_list(input_dict):
        newlist = list()
        for i in input_dict.keys():
            newlist.append(i)
        newlist.sort()
        return newlist


def init_apache_dir():
    pass
