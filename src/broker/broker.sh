#!/bin/bash

# PORT
PORT=${1:-1883}

docker build -t rsa/mosquitto -f broker/mosquitto.dockerfile broker
docker run -d -p $PORT:1883 -p 9001:9001 --name rsa_broker rsa/mosquitto