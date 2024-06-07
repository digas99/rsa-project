#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <drone_id>"
  exit 1
fi

# check if fleetman/ros:galactic image exists
if [ -z "$(docker images -q fleetman/ros:galactic)" ]; then
	echo "Building fleetman/ros:galactic image"
	sudo docker build -t fleetman/ros:galactic -f deps/ros.dockerfile .
fi

CONTAINER_NAME="rsa_telem_drone_$1"

# if container exists, remove it
if [ ! -z "$(docker ps -a -q -f name=$CONTAINER_NAME)" ]; then
	echo "Removing existing container $CONTAINER_NAME"
	docker rm -f $CONTAINER_NAME
fi

docker build -t rsa/telem -f telem/telem.dockerfile ../ && \
	docker run -it --network host --name $CONTAINER_NAME rsa/telem $1
