import cv2
import argparse
import numpy as np
import os

from detection import Detector

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

	detector = Detector(args.config, args.weights, args.classes)
	
	image = cv2.imread(args.image)
	image = detector.detect(image)

	output_dir = os.path.join(BASE_DIR, "output")
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	num_files = len(os.listdir(output_dir))
	detector.export(image, f"{output_dir}/output{num_files}.jpg")

	detector.show(image)


if __name__ == "__main__":
	main()