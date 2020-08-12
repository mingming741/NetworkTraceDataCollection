import json

def parse_config(path):
    with open(path) as json_data_file:
        data = json.load(json_data_file)
    return data