import argparse
import os
import sys
import json
import requests

from geopy.distance import geodesic

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from messages import MQTTClient  # Import the MQTT client

coords = {}

class AvoidanceClient(MQTTClient):

	def __init__(self, broker='localhost', port=1883, topic='/telem', drone=None, station=None):
		super().__init__(broker=broker, port=port, topic=topic)

		self.drone = drone
		self.station = station

	def on_message(self, client, userdata, message):
		payload = json.loads(message.payload.decode())
		drone_id = payload.get('drone_id')

		coords[drone_id] = payload.get('coords')

		# if coords have at least two drones
		if len(coords) >= 2:
			# check if the drones are too close
			if self.check_avoidance():
				print('Avoidance needed!')
				requests.post(f'http://{self.station}/avoidance/{self.drone}')
			else:
				print('No avoidance needed')

	def check_avoidance(self):
		# self drone coordinates
		coords1 = coords.get(self.drone)
		coords2 = [v for k, v in coords.items() if k != self.drone][0]	

		# if the drones are less than 1m apart
		if self.distance(coords1, coords2) < 5:
			return True

		return False
	
	def distance(self, coords1, coords2):
		distance = geodesic(coords1, coords2).meters
		print(f'Distance: %.2f m' % distance)
		return distance

def main():
	parser = argparse.ArgumentParser(description='Telemetry node')
	parser.add_argument('drone_id', type=str, help='Drone ID')
	args = parser.parse_args()

	client = AvoidanceClient(broker='localhost', port=1884, topic=f'/telem/#', drone=args.drone_id, station='localhost:8080')
	client.start(blocking=True)

if __name__ == '__main__':
	main()