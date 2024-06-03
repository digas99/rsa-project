import argparse

from telem.telem import Telemetry

def main():
	parser = argparse.ArgumentParser(description='Telemetry node')
	parser.add_argument('drone_id', type=str, help='Drone ID')
	args = parser.parse_args()

	telem = Telemetry(drone=args.drone_id, broker='localhost', port=1883, mqtt_topic='/telem')
	
	try:
		telem.start()
	except KeyboardInterrupt:
		telem.shutdown()

if __name__ == '__main__':
    main()