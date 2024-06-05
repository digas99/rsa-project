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

docker build -t rsa/telem -f telem/telem.dockerfile telem
docker run -it --network host --name rsa_telem rsa/telem $1
