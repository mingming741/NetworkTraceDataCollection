import json
import os
import pathlib
import time
import logging
import random
import string
import copy


def parse_config(path):
    with open(path) as json_data_file:
        data = json.load(json_data_file)
    return data


def merge_config(new_config, old_config):
    config = copy.deepcopy(old_config)
    if new_config is not None:
        config.update(new_config)
    return config

def parse_logging_level(logging_level_string):
    if logging_level_string == "debug":
        return logging.DEBUG
    elif logging_level_string == "info":
        return logging.INFO


def make_public_dir(dir_path):
    # if not exist, create,
    # Always change to 777
    if not os.path.exists(dir_path):
        pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
    os.system("sudo chmod -R 777 {}".format(dir_path))


def remake_public_dir(dir_path):
    if os.path.exists(dir_path):
        os.system("sudo rm -rf {}".format(dir_path))
    make_public_dir(dir_path)


def init_dir():
    make_public_dir("log")
    make_public_dir("trace")



def dict_key_to_ordered_list(input_dict):
    newlist = list()
    for i in input_dict.keys():
        newlist.append(i)
    newlist.sort()
    return newlist


def fail_and_wait(fail_reason, timeout = 60):
    print(fail_reason)
    time.sleep(timeout)


def init_apache_dir():
    pass


def generate_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


class DokiTimer:
    def __init__(self, expired_time, repeat=False):
        self._start_time = time.perf_counter()
        self._expired_time = expired_time
        self._repeat = repeat


    def is_expire(self):
        if self.expired_time == -1: # -1 is pre-config never expired timer
            return False
        current_time = time.perf_counter()
        if (current_time - self._start_time) >=  self._expired_time:
            if self._repeat == True:
                self._start_time = current_time
            return True
        else:
            return False





class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""
