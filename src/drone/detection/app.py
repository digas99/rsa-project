import pprint
import requests
import json

from detection import Detector

from messages import MQTTClient  # Import the MQTT client

class CounterClient(MQTTClient):

    def __init__(self, broker='localhost', port=1883, topic='/counter', node=None):
        super().__init__(broker=broker, port=port, topic=topic)

    def on_message(self, client, userdata, message):
        pass


client = CounterClient(broker="10.1.1.4", port=1883, topic='/counter/device1')

def handle_stream(people, frame, image):
	print(f"People detected: {people}")
	response = requests.post(f'http://10.1.1.4:8080/upload?device=device1', files={"image": image})
	pprint.pprint(response)

	payload = json.dumps({'people': people})
	client.publish(payload)

def main():
	detector = Detector()
	detector.stream_picam(handle_stream, target="person", show=False)

if __name__ == "__main__":
	main()
