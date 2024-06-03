FROM fleetman/ros:galactic

# Install Python3 and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip

RUN python3 -m pip install --upgrade pip

# Install ROS 2 dependencies
RUN apt-get update && \
    apt-get install -y \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-rosinstall-generator \
    python3-vcstool \
    build-essential

# Initialize rosdep
RUN rosdep init && \
    rosdep update

# Install rclpy
RUN apt-get update && \
    apt-get install -y ros-galactic-rclpy

# Install pip requirements
RUN python3 -m pip install \
    paho-mqtt

COPY app.py /home/
COPY telem /home/telem
COPY entrypoint.sh /home/

WORKDIR /home/

# Set the entrypoint to the wrapper script
ENTRYPOINT ["/home/entrypoint.sh"]

# Default command to run the app
CMD ["python3", "app.py", "drone01"]