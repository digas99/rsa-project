import os

# Set YOLOv8 to quiet mode
os.environ['YOLO_VERBOSE'] = 'False'

from detection import Detector

def callback(people):
	print(f"People detected: {people}")

def main():
	detector = Detector()
	detector.stream(callback, show=True)

if __name__ == "__main__":
	main()