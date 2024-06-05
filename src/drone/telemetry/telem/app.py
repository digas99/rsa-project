import argparse

from telem import Telemetry

def main():
	parser = argparse.ArgumentParser(description='Telemetry node')
	parser.add_argument('drone_id', type=str, help='Drone ID')
	args = parser.parse_args()

	telem = Telemetry(drone=args.drone_id, broker='10.1.1.4', port=1883, mqtt_topic='/telem')
	
	try:
		telem.start()
	except KeyboardInterrupt:
		telem.shutdown()

if __name__ == '__main__':
    main()
