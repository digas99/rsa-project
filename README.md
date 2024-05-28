# rsa-project

## Table of Contents

- [Setup Jetson Nano](#setup-jetson-nano-jetpack-46-l4t-r3261)
	- [Export Paths for CUDA](#export-paths-for-cuda)
	- [Build OpenCV with GStreamer support](#build-opencv-with-gstreamer-support)
	- [Create pip package for Compiled OpenCV](#create-pip-package-for-compiled-opencv)
	- [Clone ultralytics](#clone-ultralytics)
	- [Setup Python 3.8](#setup-python-38)
	- [Install PyTorch 0.11.0 and TorchVision 0.12.0](#install-pytorch-0110-and-torchvision-0120)
	- [Install ultralytics](#install-ultralytics)
- [Setup Project](#setup-project)
	- [Clone this repository](#clone-this-repository)
	- [Run Stream Server](#run-stream-server)
	- [Run Object Detection App](#run-object-detection-app)

## Setup Jetson Nano JetPack 4.6 (L4T R32.6.1) 

### Export Paths for CUDA

Add the following lines to ~/.bashrc

```bash
export PATH=/usr/local/cuda-10.2/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-10.2/lib64:$LD_LIBRARY_PATH
export FORCE_CUDA="1"
```

### Build OpenCV with GStreamer support

[Follow this guide](https://qengineering.eu/install-opencv-on-jetson-nano.html#:~:text=install%20qt5%2Ddefault-,Download%20OpenCV.,-When%20all%20third)	
(Build might take a couple of hours)

### Create pip package for Compiled OpenCV

Create a dummy package for OpenCV installed from source (to prevent pip from trying to install another version of OpenCV)

```bash
cd ~
mkdir opencv-pip
cd opencv-pip

touch setup.py
```

Add the following content to setup.py

```python
from setuptools import setup

setup(
		name='opencv-python',
		version='4.10.0-pre',
		description='Dummy package for OpenCV installed from source',
		install_requires=[],
)
```

Install dummy package
```bash
pip install --no-deps opencv-python
```

### Clone ultralytics

```bash
git clone https://github.com/ultralytics/ultralytics
cd ultralytics
```

### Setup Python 3.8
Jetson Nano comes with Python 3.6.9, but we need Python 3.8.
```bash
sudo apt-get update
sudo apt install -y python3.8 python3.8-venv python3.8-dev python3-pip libopenmpi-dev libomp-dev libopenblas-dev libblas-dev libeigen3-dev libcublas-dev
python3.8 -m venv venv --system-site-packages
source venv/bin/activate
```

### Install PyTorch 0.11.0 and TorchVision 0.12.0

Versions that work with CUDA 10.2

```bash
$ pip install -U pip wheel gdown
$ gdown https://drive.google.com/uc?id=1hs9HM0XJ2LPFghcn7ZMOs5qu5HexPXwM
$ gdown https://drive.google.com/uc?id=1m0d8ruUY8RvCP9eVjZw4Nc8LAwM8yuGV
$ python3.8 -m pip install torch-*.whl torchvision-*.whl
```

### Install ultralytics

```bash
pip install .
```

## Setup Project

Make sure you are inside the virtual environment created in the [previous steps](#setup-python-38)

### Clone this repository

```bash
git clone https://github.com/digas99/rsa-project
cd rsa-project
pip install -r requirements.txt
```

### Run Stream Server

```bash
python3 src/stream.py
```

### Run Object Detection App

```bash
python3 src/app.py
```

## Architecture Diagram

![Architecture Diagram](./diagram/rsa-project.png)
