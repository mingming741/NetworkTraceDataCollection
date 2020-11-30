import time
import socket
import select
import logging
import utils
import os

from utils import DokiTimer


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
current_script = os.path.basename(__file__)

def wait_receive_message(my_socket, timeout=300):
    message = ""
    try:
        my_timer = DokiTimer(expired_time=timeout)
        while my_timer.is_expire() == False:
            data = my_socket.recv(1024).decode("utf-8")
            message = message + data
            if "##DOKI##" in data:
                message = message.replace("##DOKI##", "")
                return message
        return None
    except Exception as e:
        logger.warning("{}--> Exception happen when receive message {}".format(current_script, e))
        logger.debug("{}--> message is: {}".format(current_script, message))
        return None


def retry_send(my_socket, message, retry_timeout=30, max_try=10):
    message = (message + "##DOKI##").encode("utf-8")
    exit_flag = 0
    while exit_flag < max_try:
        try:
            my_socket.send(message)
            time.sleep(1)
            logger.debug("{}--> Send message {}".format(current_script, message))
            return True
        except Exception as e:
            logger.warning("{}--> Exception happen send message: {}".format(current_script, e))
            time.sleep(retry_timeout)
            logger.debug("{}--> Retry..".format(current_script))
            exit_flag = exit_flag + 1
    if exit_flag == max_try:
        logger.warning("{}--> Connect {} times but still fail!".format(current_script, max_try))
        return False


def retry_bind(my_socket, my_socket_address_port, retry_timeout=300, max_try=10):
    exit_flag = 0
    while exit_flag < max_try:
        try:
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.bind(my_socket_address_port)
            time.sleep(1)
            return True
        except Exception as e:
            logger.warning("{}--> Exception happen when bind address: {}".format(current_script, e))
            time.sleep(retry_timeout)
            logger.debug("{}--> Retry..".format(current_script))
            exit_flag = exit_flag + 1
    if exit_flag == max_try:
        logger.warning("{}--> Bind {} times but still fail!".format(current_script, max_try))
        return False


def retry_connect(my_socket, server_address_port, retry_timeout=30, max_try=10):
    exit_flag = 0
    while exit_flag < max_try:
        try:
            my_socket.connect(server_address_port)
            time.sleep(1)
            logger.debug("{}--> Connect to {} success".format(current_script, server_address_port))
            return True
        except Exception as e:
            logger.warning("{}--> Exception happen when connect to server: {}".format(current_script, e))
            time.sleep(retry_timeout)
            logger.debug("{}--> Retry..".format(current_script))
            exit_flag = exit_flag + 1
    if exit_flag == max_try:
        logger.warning("{}--> Connect {} times but still fail!".format(current_script, max_try))
        return False
