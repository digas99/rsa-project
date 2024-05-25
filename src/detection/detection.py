import cv2
import numpy as np
import sys

from ultralytics import YOLO

class Detector:
	def __init__(self):
		self.classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"
              ]
		self.model = YOLO("yolov8/yolov8n.pt")

	def detect(self, callback, frame, target):
		results = self.model(frame, True)
		counter = 0

		for result in results:
			boxes = result.boxes
			for box in boxes:
				cls = int(box.cls[0])
				if self.classNames[cls] == target:
					counter += 1
				
				if self.classNames[cls] == target:
					x, y, w, h = box.xyxy[0]
					x, y, w, h = int(x), int(y), int(w), int(h)
					cv2.rectangle(frame, (x, y), (w, h), (0, 255, 0), 2)

					cv2.putText(frame, self.classNames[cls], (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
				pass

		# jpeg version of the image
		image = cv2.imencode(".jpg", frame)[1].tobytes()
		
		if callback:
			callback(counter, frame, image)

		return counter

	def stream(self, callback, target="person"):
		# Define the GStreamer pipeline
		gst_pipeline = (
			"nvarguscamerasrc ! "
			"video/x-raw(memory:NVMM),width=640,height=480,framerate=21/1,format=NV12 ! "
			"nvvidconv ! "
			"video/x-raw,format=(string)I420 ! "
			"videoconvert ! "
			"appsink"
		)

		while True:
			# Open the camera using the GStreamer pipeline
			cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)
			if not cap.isOpened():
				print("Error: Could not open video stream.")
				break

			while True:
				ret, frame = cap.read()
				if not ret:
					print("Error: Could not read frame.")
					break

				try:
					self.detect(callback, frame, target)
				except Exception as e:
					print(f"Error during detection: {e}")
					break

			cap.release()
			print("Stream stopped, attempting to restart...")