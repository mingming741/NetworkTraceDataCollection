# Network Trace Data Collection Tools
Just a brief description about this tool.

### Working Environment
1. Ubuntu Linux, (Ubuntu16.04 is recommended)
2. python3.5 or higher version


### Machine requirements
1. Logging Server: Static ip with 103.49.160.136, has a web interface, all trace can be downloaded from this logging server.
2. Packet sending Client: Can in whatever network environment, better support SIM card.
3. Packet sending Server: Need a public IP, better in wired network.

Packet sending Client/Server are in pairs. Multiple pair of packet sending client/server can be set at the same time by configuring "config/host_machine_config.json"


### Setup
1. For Packet sending Client/Server, run "sudo sh init_env.sh" can install corresponding packet.
2. Disable TSO/GSO/GRO for you host machine pair
3. Test config file are at "config/schedule_config.json". You can keep it as default. If you want to configure the scheduling logic, edit "scheduling_list" in "config/schedule_config.json"



### Run a test
For both server/client side, run "sudo python3 test/test.py". If success, then you have done, other things will be done automatically.


### Notification
This tool is just developed and have may issues out of my expectation. If you find problem, please just tell me, I will make some improvements.  









### END
