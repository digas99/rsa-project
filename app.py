import cv2
import argparse
import numpy as np
import os

classes = None
COLORS = None

BASE_DIR = os.path.dirname(os.path.abspath(__name__))

def main():    
	# handle command line arguments
	ap = argparse.ArgumentParser()
	ap.add_argument('-i', '--image', required=True,
					help = 'path to input image')
	ap.add_argument('-c', '--config', required=True,
					help = 'path to yolo config file')
	ap.add_argument('-w', '--weights', required=True,
					help = 'path to yolo pre-trained weights')
	ap.add_argument('-cl', '--classes', required=True,
					help = 'path to text file containing class names')
	args = ap.parse_args()

	# read input image
	image = cv2.imread(args.image)

	H, W, _ = image.shape
	scale = 0.00392

	# read classes
	with open(args.classes, 'r') as f:
		global classes
		classes = [line.strip() for line in f.readlines()]
	
	# generate different colors for different classes 
	global COLORS
	COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

	# read pre-trained model and config file
	net = cv2.dnn.readNet(args.weights, args.config)
	output_layers = net.getUnconnectedOutLayersNames()

	# create input blob
	blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)
	net.setInput(blob)
	outs = net.forward(output_layers)

	# initialization
	class_ids = []
	confidences = []
	boxes = []
	conf_threshold = 0.5
	nms_threshold = 0.4

	# for each detetion from each output layer 
	# get the confidence, class id, bounding box params
	# and ignore weak detections (confidence < 0.5)
	for out in outs:
		for detection in out:
			scores = detection[5:]
			class_id = np.argmax(scores)
			confidence = scores[class_id]
			if confidence > 0.5:
				center_x = int(detection[0] * W)
				center_y = int(detection[1] * H)
				w = int(detection[2] * W)
				h = int(detection[3] * H)
				x = center_x - w / 2
				y = center_y - h / 2
				class_ids.append(class_id)
				confidences.append(float(confidence))
				boxes.append([x, y, w, h])

	# apply non-max suppression
	indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

	# go through the detections remaining
	# after nms and draw bounding box
	for i in indices:
		box = boxes[i]
		x = box[0]
		y = box[1]
		w = box[2]
		h = box[3]
		
		draw_bounding_box(image, class_ids[i], round(x), round(y), round(x+w), round(y+h))

	# display output image    
	cv2.imshow("object detection", image)

	# wait until any key is pressed
	cv2.waitKey()
		
	# save output image to disk
	# create output directory if it doesn't exist
	output_dir = os.path.join(BASE_DIR, "output")
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	num_files = len(os.listdir(output_dir))
	cv2.imwrite(f"{output_dir}/output{num_files}.jpg", image)

	# release resources
	cv2.destroyAllWindows()


def draw_bounding_box(img, class_id, x, y, x_plus_w, y_plus_h):
	label = str(classes[class_id])
	color = COLORS[class_id]
	cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)
	cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


if __name__ == "__main__":
    main()