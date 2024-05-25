import pprint
import requests

from detection import Detector

def handle_stream(people, frame, image):
	print(f"People detected: {people}")
	response = requests.post("http://localhost:8000/upload", files={"image": image})
	pprint.pprint(response)

def main():
	detector = Detector()
	detector.stream(handle_stream, target="person")

if __name__ == "__main__":
	main()
