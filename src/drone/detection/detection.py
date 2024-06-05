import cv2
import numpy as np
import sys
import libcamera

from picamera2 import Picamera2
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

	def detect(self, callback, frame, target, stream=False, show=True):
		results = self.model(frame, stream)
		counter = 0
		frame = np.ascontiguousarray(frame)

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

		if show:
			cv2.imshow("Frame", frame)
			
			if stream:
				return
			
			cv2.waitKey(0)
			cv2.destroyAllWindows()

		return counter

	def stream_picam(self, callback, target="person", show=True):
		cap = Picamera2()
		preview_config = cap.create_preview_configuration(main={
			"size": (640, 480),
			"format": 'RGB888'
		})
		preview_config["transform"] = libcamera.Transform(hflip=1, vflip=1)
		cap.configure(preview_config)

		cap.start()

		while True:
			frame = cap.capture_array("main")

			self.detect(callback, frame, target, stream=True, show=show)

			if cv2.waitKey(1) & 0xFF == ord("q"):
				cv2.destroyAllWindows()
				break

		cap.stop()
		cv2.destroyAllWindows()


	def stream(self, callback, target="person", show=True):
		cap = cv2.VideoCapture(0)
		cap.set(3, 640)
		cap.set(4, 480)

		while True:
			ret, frame = cap.read()
			if not ret:
				break

			self.detect(callback, frame, target, stream=True, show=show)

			if cv2.waitKey(1) & 0xFF == ord("q"):
				cv2.destroyAllWindows()
				break

		cap.release()
		cv2.destroyAllWindows()