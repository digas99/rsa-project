# rsa-project

## Setup

On the Raspberry Pi, you need to install the following packages, **using sudo**:

1. Picamera2

```bash
sudo apt install -y python3-picamera2
```

2. OpenCV

```bash
sudo apt-get install python3-opencv
```

3. Ultralytics

```bash
sudo pip3 install --break-system-packages ultralytics
```

4. Flask

```bash
sudo apt install python3-flask
```

## Run

On the root directory of the project, run the following command:

```bash
sudo python3 src/app.py
```

## Architecture Diagram

![Architecture Diagram](./diagram/rsa-project.png)