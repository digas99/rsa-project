#!/bin/bash

SOURCE=src
DATA=yolov3
python3 $SOURCE/app.py -i $1 -c $DATA/yolov3.cfg -w $DATA/yolov3.weights -cl $DATA/coco.names
