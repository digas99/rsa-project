#!/bin/bash

# PORT
PORT=${1:-1883}

docker build -t rsa/mosquitto -f mosquitto.dockerfile .
docker run -d -p $PORT:1883 -p 9005:9001 --name rsa_broker rsa/mosquitto
