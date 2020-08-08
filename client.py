import socket  
import datetime 
import time 
import errno
import sys

file_name = sys.argv[1]
print(file_name) 


def utf8len(s):
    return len(s.encode('utf-8'))


# the first half, mainly to get the IP address and port number from the peer
address = ('103.49.160.139', 33333)  
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
s.settimeout(0.1)
msg = "to get the ip address and port of the peer"


starting_time = time.time()

sent = 0
throughput_begin = time.time() + 1
data = ""
temp = 0



while True:
    fw = open(file_name, "a")
    
    s.sendto(msg, address)
    print("sending request now!!!!!!!!!!")
    fw.write("sending request now!!!!!!!!!\n")
    begin = time.time()
    throughput_begin = time.time() + 1

    while True:
        try:
            data, addr = s.recvfrom(10000000)
        except socket.timeout:
            print 'caught a timeout'
            #fw.write("caught a timeout\n")
        now = time.time()
        if now - begin > 30:
            break
            print("break")


        if now - throughput_begin  > 1:
            sent = sent + utf8len(data)
            #print(data)
            temp = sent * 8 
            print("bandwidth=  "),
            print(temp , now - starting_time)
            fw.write("bandwidth: " + str(temp) + "\n")
            sent = 0
            throughput_begin  = throughput_begin  + 1
        else:
            sent = sent + utf8len(data)
            #print(data)



        if now - starting_time > 60:
            break
    now = time.time()
    if now - starting_time > 60:
        break


        
    fw.close()
s.close()
fw.close()
