#!/bin/bash
# Source the ROS 2 setup script
source /opt/ros/galactic/setup.bash

# Execute the passed command
exec python3 /home/app.py "$@"