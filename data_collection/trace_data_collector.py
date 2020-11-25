import socket
import time
import os
import json
import shutil
import argparse
import logging
import threading
import my_threading
import inspect
from threading import Timer
from datetime import datetime, timezone


import utils
import my_socket


class TraceDataCollector(object):
    def __init__(self, init_config, role=None):
        self.config = init_config
        if role in ["client", "server", None]:
            self.role = role
        else:
            raise Exception("Need to define a role for a trace collector")



class TraceDataCollectionClient(TraceDataCollector):
    def __init__(self, init_config, role="client"):
        super(TraceDataCollectionClient, self).__init__(init_config, role)
        self.hostname = self.config["hostname"]
        self.ip = self.config["ip"]
        self.ip_dual = self.config["ip_dual"]
        self.hostname_peer = self.config["hostname_peer"]
        self.ip_peer = self.config["ip_peer"]

    def iperf_tcpdump_download(self):
        pass

    def iperf_tcp_dump_upload(self):
        pass




class TraceDataCollectionServer(TraceDataCollector):
    def __init__(self, init_config, role="client"):
        super(TraceDataCollectionClient, self).__init__(init_config, role)
        self.hostname = self.config["hostname"]
        self.ip = self.config["ip"]
        self.ip_dual = self.config["ip_dual"]
        self.hostname_peer = self.config["hostname_peer"]
        self.ip_peer = self.config["ip_peer"]

    def iperf_tcpdump_download(self):
        pass

    def iperf_tcp_dump_upload(self):
        pass
