#! /bin/sh
# Replace "ethX" with your network interface
ethtool -K ethX tso off gso off gro off
