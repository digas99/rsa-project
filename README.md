# rsa-project

## Setup

1. Create a python virtual environment and activate it

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install the requirements

```bash
pip3 install -r requirements.txt
```

3. Download YOLOv3 weights and configuration

```bash
chmod +x get_yolov3.sh 
./get_yolov3.sh
```

4. Run the app

```bash
python3 src/app.py -i <image> -c yolov3/yolov3.cfg -w yolov3/yolov3.weights -cl yolov3/coco.names
```
or
```bash
./run.sh <image>
```

## Architecture Diagram

![Architecture Diagram](./diagram/rsa-project.png)