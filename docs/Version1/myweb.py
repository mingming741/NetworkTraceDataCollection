#! /usr/bin/python3

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
logging.basicConfig(level=utils.parse_logging_level(test_meta_config["general_config"]["logging_level"]))
logger = logging.getLogger(__name__)
current_script = os.path.basename(__file__)



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


def post_file_to_server(file_path, network, direction, variant, trace_source = 0, server_host=test_meta_config["general_config"]["web_interface_server_ip"]):
    logger.info("Post {}->{}->{}->{} to server".format(network, direction, variant, file_path))
    server_url = 'http://{}/php/handler.php?action=Upload_Record'.format(server_host)
    network_dict, variant_dict, direction_dict = get_db_info()
    parameters = {"Network_ID": network_dict[network], "Variant_ID": variant_dict[variant], "Direction_ID": direction_dict[direction], "Trace_Source": trace_source}
    files = {'file': open(file_path,'rb')}
    response = requests.post(server_url, files=files, data=parameters)
    logger.debug(response.json())
