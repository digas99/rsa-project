import cv2
import numpy as np

class Detector:
	def __init__(self, config, weights, classes):
		self.net = cv2.dnn.readNet(weights, config)
		self.output_layers = self.net.getUnconnectedOutLayersNames()
		self.scale = 0.00392
		self.conf_threshold = 0.5
		self.nms_threshold = 0.4
		
		with open(classes, 'r') as f:
			self.classes = [line.strip() for line in f.readlines()]
		
		self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))
		
	def detect(self, image):
		H, W, _ = image.shape
		blob = cv2.dnn.blobFromImage(image, self.scale, (416,416), (0,0,0), True, crop=False)
		self.net.setInput(blob)
		outs = self.net.forward(self.output_layers)
		
		class_ids = []
		confidences = []
		boxes = []
		
		for out in outs:
			for detection in out:
				scores = detection[5:]
				class_id = np.argmax(scores)
				confidence = scores[class_id]
				if confidence > self.conf_threshold:
					center_x = int(detection[0] * W)
					center_y = int(detection[1] * H)
					w = int(detection[2] * W)
					h = int(detection[3] * H)
					x = center_x - w / 2
					y = center_y - h / 2
					class_ids.append(class_id)
					confidences.append(float(confidence))
					boxes.append([x, y, w, h])
		
		indices = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_threshold, self.nms_threshold)
		
		for i in indices:
			box = boxes[i]
			x = box[0]
			y = box[1]
			w = box[2]
			h = box[3]
			
			self.draw_bounding_box(image, class_ids[i], round(x), round(y), round(x+w), round(y+h))
		
		return image

	def draw_bounding_box(self, img, class_id, x, y, x_plus_w, y_plus_h):
		label = str(self.classes[class_id])
		color = self.colors[class_id]
		cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)
		cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

	def show(self, image):
		cv2.imshow('Object Detection', image)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

	def export(self, image, path):
		cv2.imwrite(path, image)