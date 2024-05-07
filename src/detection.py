import cv2
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
		self.model = YOLO("yolov8/yolov8n.pt", verbose=False)
		self.people = 0

		
	def stream(self, callback, show=True):
		cap = cv2.VideoCapture(0)
		cap.set(3, 640)
		cap.set(4, 480)

		while True:
			ret, frame = cap.read()
			if not ret:
				break

			results = self.model(frame, stream=True)
			self.people = 0
			for result in results:
				boxes = result.boxes
				for box in boxes:
					cls = int(box.cls[0])
					if self.classNames[cls] == "person":
						self.people += 1
					
					if show and self.classNames[cls] == "person":
						x, y, w, h = box.xyxy[0]
						x, y, w, h = int(x), int(y), int(w), int(h)
						cv2.rectangle(frame, (x, y), (w, h), (0, 255, 0), 2)

						cv2.putText(frame, self.classNames[cls], (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)

			callback(self.people)

			if show:
				cv2.imshow("Frame", frame)
				if cv2.waitKey(1) & 0xFF == ord("q"):
					break

		cap.release()
		cv2.destroyAllWindows()