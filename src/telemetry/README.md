# Drone Telemetry

## Build and run Docker container

```bash
docker build -t fleetman/ros -f ros.dockerfile .
docker build -t fleetman/telem -f telem.dockerfile .
docker run -it --network host fleetman/telem
```

## Run app

```bash
python3 telem.py
```
