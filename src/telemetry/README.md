# Drone Telemetry

## Setup with scripts

### Broker

```bash
./broker.sh
```

### Telemetry

```bash
./telem.sh <drone_id>
```

## Setup manually 

### Build ROS image

```bash
docker build -t fleetman/ros:galactic -f deps/ros.dockerfile .
```

### Build and run broker

```bash
docker build -t rsa/mosquitto -f broker/mosquitto.dockerfile broker
docker run -d -p 1884:1883 -p 9001:9001 --name rsa_broker rsa/mosquitto
```

### Build and run telemetry app

```bash
docker build -t rsa/telem -f telem/telem.dockerfile telem
docker run -it --network host --name rsa_telem rsa/telem <drone_id>
```