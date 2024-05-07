import argparse
import cv2
import os

from detection import Detector

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def handle_image(people, frame):
	print(f"People detected: {people}")

	output_dir = os.path.join(BASE_DIR, "../output")
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)
	
	num_files = len(os.listdir(output_dir))
	cv2.imwrite(f"{output_dir}/output{num_files}.jpg", frame)

def handle_stream(people, frame):
	print(f"People detected: {people}")


def main():
	# handle command line arguments
	ap = argparse.ArgumentParser()
	ap.add_argument('-i', '--image', required=False,
					help = 'path to input image')
	
	args = ap.parse_args()
	
	detector = Detector()
	
	if args.image:
		image = cv2.imread(args.image)
		detector.detect(handle_image, image, object="person")
	else:
		detector.stream(handle_stream, object="person")

if __name__ == "__main__":
	main()