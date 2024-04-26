import cv2
import argparse
import numpy as np

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

	W, H, _ = image.shape
	scale = 0.00392

	# read classes
	classes = None
	with open(args.classes, 'r') as f:
		classes = [line.strip() for line in f.readlines()]

	# read pre-trained model and config file
	net = cv2.dnn.readNet(args.weights, args.config)

	# create input blob
	blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)
	net.setInput(blob)
    
	# TODO: continue

if __name__ == "__main__":
    main()