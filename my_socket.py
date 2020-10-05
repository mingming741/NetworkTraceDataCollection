import time
import socket
import select


def doki_wait_receive_message(my_socket, timeout=120):
    message = ""
    my_socket.setblocking(0)
    try:
        while True:
            ready = select.select([my_socket], [], [], timeout)
            if ready[0]:
                data = my_socket.recv(1024).decode("utf-8")
            message = message + data
            if "##DOKI##" in data:
                break
        message = message.replace("##DOKI##", "")
        return message
    except Exception as e:
        print("Exception happen when receive message {}".format(e))
        print("message is: {}".format(message))
        return None


def retry_bind(my_socket, my_socket_address_port, retry_timeout=300, stable_wait_time=1, max_try=10):
    exit_flag = 0
    while exit_flag < max_try:
        try:
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.bind(my_socket_address_port)
            time.sleep(stable_wait_time)
            return True
        except Exception as e:
            print("Exception happen when bind address: {}".format(e))
            time.sleep(retry_timeout)
            print("Retry..")
            exit_flag = exit_flag + 1
    if exit_flag == max_try:
        print("Bind {} times but still fail!".format(max_try))
        return False

def retry_connect(my_socket, server_address_port, retry_timeout=5, stable_wait_time=1, max_try=30):
    print("Connect to {}".format(server_address_port))
    exit_flag = 0
    while exit_flag < max_try:
        try:
            my_socket.connect(server_address_port)
            time.sleep(stable_wait_time)
            print("Connect to {} success".format())
            return True
        except Exception as e:
            print("Exception happen when connect to server: {}".format(e))
            time.sleep(retry_timeout)
            print("Retry..")
            exit_flag = exit_flag + 1
    if exit_flag == max_try:
        print("Connect {} times but still fail!".format(max_try))
        return False

def retry_send(my_socket, message, retry_timeout=5, stable_wait_time=1, max_try=30):
    print("Send message {}".format(message))
    exit_flag = 0
    while not exit_flag < max_try:
        try:
            my_socket.send(message)
            time.sleep(stable_wait_time)
            return True
        except Exception as e:
            print("Exception happen send message: {}".format(e))
            time.sleep(retry_timeout)
            print("Retry..")
            exit_flag = exit_flag + 1
    if exit_flag == max_try:
        print("Connect {} times but still fail!".format(max_try))
        return False
