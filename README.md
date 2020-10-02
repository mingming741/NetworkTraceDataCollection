# Network Trace Data Collection Tools
Just a brief description about this tool.

### Working Environment
1. Ubuntu Linux, (Ubuntu16.04 is recommended)
2. python3.5 or higher version


### Machine requirements
1. Logging Server: Static ip with 103.49.160.136, has a web interface, all trace can be downloaded from this logging server.
2. Packet sending Client: Can in whatever network environment, better support SIM card.
3. Packet sending Server: Need a public IP, better in wired network.

Packet sending Client/Server are in pairs. Multiple pair of packet sending client/server can be set at the same time.


### Setup
1. For Packet sending Client/Server, run "sudo sh init_env.sh" can install corresponding packet.
2. If you want to setup a loggin server, you need to run "sudo sh www/html/init_env.sh", and move all staff from www to /var/www, and setup you own apache server.


### Config a test
All test config file are at "config/test_meta_config.json". Make sure each Packet sending Server/Client share the same "config/test_meta_config.json" file content.

Here is the interpretation of "config/test_meta_config.json"

"general_config" contain the whole test config, which contains:
1. web_interface_server_ip: the ip of Logging Server
2. trace_min_time_unit: the unit about the trace data timestamp, select "milliseconds" for better accuracy, select "seconds" for save logging space.
3. resume_time_hour: After all test done, when should the next scheduling start. e.g., 12 means packet sending server/client will wait until 12:00 to resume the packet sending. -1 means do not wait.    


"scheduling_config" contain the task and its corresponding config, currently "download_iperf_wireshark" will collect the downlink trace at client side, "upload_iperf_wireshark" will collect the uplink trace at the server side.
1. enable: whether this task will be run in scheduling
2. udp_sending_rate: control the max sending rate for udp task, need to be larger than the client capacity.
3. total_run: In one test (before resume), how many time for this task will be run.
4. time_each_flow:  in seconds, time for each iperf task

"vaild_config" contain the supported values
1. variants_list: "value" = 1 means this variant will be covered in the task.
2. trace_min_unit (DO NOT modify): the reference value of "general_config-->trace_min_time_unit"


"test_machines_group" specify the packet sending server/client information.
1. For each pair, add a host with group name "gx" in both server and client, need the "hostname" to be the return of "socket.gethostname()"
2. For server list, need server public IP
3. For client list, need the network status of the client.


For example, I want to collect SIM card "CSL_4G", TCP cubic downlink trace, each run I collect 1 hours, each experiment I run 3 times. I want this experiment resume at 0:00am everyday.
1. Setup 2 machine, config test_machines_group, add a group "g3" (or other name), and add the packet sending server/client information, make sure you have a CSL_4G SIM adapter.
2. Set "general_config-->resume_time_hour" = 0
3. Set "scheduling_config-->download_iperf_wireshark-->enable" = 1 and "scheduling_config-->upload_iperf_wireshark-->enable" = 0, to only run the downlink task
4. edit "scheduling_config-->upload_iperf_wireshark", set "total_run" = 3, and "time_each_flow" = 3600 (3600 second is 1 hour)
5. edit "vaild_config-->variants_list", for set "cubic" = 1, others = 0, or simply deleted others.
6 Then try to run a test.


### Run a test
1. For packet sending server, run "sudo python3 schedule.py"
2. For packet sending client, run "sudo python3 schedule.py"

If success, then you have done, other things will be done automatically.




### Notification
This tool is just developed and have may issues out of my expectation. If you find problem, please just tell me, I will make some improvements.  












### END
