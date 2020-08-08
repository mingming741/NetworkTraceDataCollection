import socket
import time
address = ('103.49.160.139', 33333)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(address)
s.settimeout(0.01)
addr = ()
port = ""
data = ""
client_ip = ""

previous_ip = ""
previous_port = ""
fr = open("input_file.txt")
msg = fr.readline()
while 1:
        try:
                data, addr = s.recvfrom(2048)
        except socket.timeout:
                print("caught a timeout")

        if addr !=  ():
                client_ip = addr[0]
                port = addr[1]

        if data == "":
                print("No client connected")
        elif previous_ip == client_ip and previous_port == port:
                print("IP and port do not changed:", client_ip, port)
        else:
                print("Warning! IP and port do changed:", client_ip, port)

        previous_ip = client_ip
        previous_port = port

        msg = msg[0:1000]
        #print(msg)


        now = time.time()
        count = 1
        while 1:
                current_time = time.time()
                if current_time - now > 5 * count:
                        print(current_time - now)
                        count = count + 1
                if addr != ():
                        s.sendto(msg, addr)
                        #time.sleep(8000/20000000)
                        if (count % 10 == 0):
                                print("sending data... counting: "),
                                print(count)
                if current_time - now > 30:
                        break
s.close()
