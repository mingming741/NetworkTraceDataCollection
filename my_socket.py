import time
import socket


def doki_wait_receive_message(my_socket):
    print("Receive Peer message")
    message = ""
    while True:
        data = my_socket.recv(1024).decode("utf-8")
        message = message + data
        if "##DOKI##" in data:
            break
    message = message.replace("##DOKI##", "")
    return message

def retry_bind(my_socket, my_socket_address_port, retry_timeout=300, stable_wait_time=1):
    exit_flag = 0
    while not exit_flag:
        try:
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.bind(my_socket_address_port)
            time.sleep(stable_wait_time)
            exit_flag = 1
        except Exception as e:
            print("Exception happen when bind address: {}".format(e))
            time.sleep(retry_timeout)
            print("Retry..")

def retry_connect(my_socket, server_address_port, retry_timeout=5, stable_wait_time=1):
    print("Connect to {}".format(server_address_port))
    exit_flag = 0
    while not exit_flag:
        try:
            my_socket.connect(server_address_port)
            time.sleep(stable_wait_time)
            exit_flag = 1
        except Exception as e:
            print("Exception happen when connect to server: {}".format(e))
            time.sleep(retry_timeout)
            print("Retry..")

def retry_send(my_socket, message, retry_timeout=5, stable_wait_time=1):
    print("Send message {}".format(message))
    exit_flag = 0
    while not exit_flag:
        try:
            my_socket.send(message)
            time.sleep(stable_wait_time)
            exit_flag = 1
        except Exception as e:
            print("Exception happen send message: {}".format(e))
            time.sleep(retry_timeout)
            print("Retry..")
