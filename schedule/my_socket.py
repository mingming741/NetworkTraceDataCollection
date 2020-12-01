import time
import socket
import select
import logging
import utils
import os

from utils import DokiTimer


logging.basicConfig(level=logging.DEBUG, format='%(levelname)-1s [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d:%H:%M:%S')
logger = logging.getLogger(__name__)


def wait_receive_message(my_socket, timeout=120):
    message = ""
    my_socket.setblocking(0)
    try:
        my_timer = DokiTimer(expired_time=timeout)
        while my_timer.is_expire() == False:
            # this line only wait for 10 seconds, if no message come in, will resume itself until timeout
            ready = select.select([my_socket], [], [], 10)
            if ready[0]:
                data = my_socket.recv(1024).decode("utf-8")
                message = message + data
                if "##DOKI##" in data:
                    message = message.replace("##DOKI##", "")
                    return message
        return None
    except Exception as e:
        logger.warning("Exception happen when receive message {}".format(e))
        return None



def retry_send(my_socket, message, retry_timeout=10, max_try=3):
    # Send does not go to retry in general, so the return value of this function does not take effect.
    message = (message + "##DOKI##").encode("utf-8")
    exit_flag = 0
    while exit_flag < max_try:
        try:
            my_socket.send(message)
            time.sleep(1)
            logger.debug("Send message {}".format(message))
            return True
        except Exception as e:
            logger.warning("Exception happen send message: {}, Retry..".format(e))
            time.sleep(retry_timeout)
            exit_flag = exit_flag + 1
    if exit_flag == max_try:
        logger.warning("Send message {} times but still fail!".format(max_try))
        return False



def retry_bind(my_socket, my_socket_address_port, retry_timeout=300, max_try=3):
    # Bind will fail if address is already uses, so need to read the return value of this function
    exit_flag = 0
    while exit_flag < max_try:
        try:
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.bind(my_socket_address_port)
            time.sleep(1)
            return True
        except Exception as e:
            logger.warning("Exception happen when bind address: {}, Retry..".format(e))
            time.sleep(retry_timeout)
            exit_flag = exit_flag + 1
    if exit_flag == max_try:
        logger.warning("Bind {} times but still fail!".format(max_try))
        return False


def retry_connect(my_socket, server_address_port, retry_timeout=10, max_try=3):
    # Connect will fail if server side is not ready, in general retry is OK.
    exit_flag = 0
    while exit_flag < max_try:
        try:
            my_socket.connect(server_address_port)
            time.sleep(1)
            logger.debug("Connect to {} success".format(server_address_port))
            return True
        except Exception as e:
            logger.warning("Exception happen when connect to server: {}, Retry".format(e))
            time.sleep(retry_timeout)
            exit_flag = exit_flag + 1
    if exit_flag == max_try:
        logger.warning("Connect {} times but still fail!".format(max_try))
        return False
