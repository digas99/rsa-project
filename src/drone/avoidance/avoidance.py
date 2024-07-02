import argparse
import os
import sys
import json
import requests

from geopy.distance import geodesic
from threading import Thread
from flask import Flask, request, jsonify

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from messages import MQTTClient  # Import the MQTT client

coords = {}

class AvoidanceClient(MQTTClient):

	def __init__(self, broker='localhost', port=1883, topic='/telem', drone=None, station=None):
		super().__init__(broker=broker, port=port, topic=topic)

		self.drone = drone
		self.station = station

		self.avoiding = False

	def on_message(self, client, userdata, message):
		payload = json.loads(message.payload.decode())
		drone_id = payload.get('drone_id')

		coords[drone_id] = payload.get('coords')

		# if the drone is avoiding
		if self.avoiding:
			return

		# if coords have at least two drones
		if len(coords) >= 2:
			# check if the drones are too close
			if self.check_avoidance():
				print('Avoidance needed!')
				response = requests.post(f'http://{self.station}/avoidance/{self.drone}')

				if response.status_code == 200:
					print('Avoiding...')
					self.avoiding = True
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
	
	def reset_avoidance(self):
		self.avoiding = False
		print('Avoidance complete')



# Flask server
app = Flask(__name__)
client = None

@app.route('/reset', methods=['POST'])
def reset():
	if client:
		client.reset_avoidance()
		return jsonify({'message': 'Avoidance reset'}), 200
	else:
		return jsonify({'message': 'Avoidance client not initialized'}), 400

def flask_run(port):
	app.run(port=port)



def main():
	global client
	parser = argparse.ArgumentParser(description='Telemetry node')
	parser.add_argument('drone_id', type=str, help='Drone ID')
	parser.add_argument('port', type=int, help='Port number for the Flask server')
	args = parser.parse_args()

	client = AvoidanceClient(broker='localhost', port=1884, topic=f'/telem/#', drone=args.drone_id, station='localhost:8080')
	
	# Start the Flask server
	flask_thread = Thread(target=flask_run, args=(args.port,))
	flask_thread.daemon = True
	flask_thread.start()

	# Start the MQTT client
	client.start(blocking=True)

if __name__ == '__main__':
	main()