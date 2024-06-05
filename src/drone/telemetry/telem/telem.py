import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from threading import Thread
import json
from telem.messages import MQTTClient  # Import the MQTT client

class TelemetryClient(MQTTClient):

    def __init__(self, broker='localhost', port=1884, topic='/telem', node=None):
        self.node = node
        self.drone = node.drone_id

        super().__init__(broker=broker, port=port, topic=topic)

    def on_message(self, client, userdata, message):
        payload = message.payload.decode()
        data = json.loads(payload)
        drone = data.get('drone_id')

        if drone != self.drone:
            print(f"[MQTT] [COORDS] {drone}: {data.get('coords')}")


class Telemetry(Node):

    def __init__(self, drone='drone01', broker='localhost', port=1884, mqtt_topic='/telem'):
        rclpy.init()
        self.topic = '/telem'
        self.drone_id = drone

        super().__init__('telemetry')

        self.subscription = self.create_subscription(String, self.topic, lambda msg: self.drone_telem_callback(msg.data), 10)
        self.mqtt_client = TelemetryClient(broker=broker, port=port, topic=mqtt_topic, node=self)

    def start(self):
        thread = Thread(target=self.init_pub)
        thread.start()

        rclpy.spin(self)

    def init_pub(self):
        self.get_logger().info('Waiting for drone "%s" telem data...' % self.drone_id)

    def drone_telem_callback(self, msg):
        try:
            telem = json.loads(msg)
            self.coords = (telem.get('position').get('lat'), telem.get('position').get('lon'))
            self.get_logger().info('%s: %s' % (self.drone_id, self.coords))

            # Publish the coordinates to the MQTT topic
            self.publish_coords(self.coords)
        except json.JSONDecodeError:
            self.get_logger().error('Failed to decode telemetry data')

    def publish_coords(self, coords):
        # Convert coordinates to a JSON string
        payload = json.dumps({'drone_id': self.drone_id, 'coords': coords})
        self.mqtt_client.publish(payload)

    def shutdown(self):
        self.get_logger().info('Shutting down...')
        self.destroy_node()
        rclpy.shutdown()
        self.mqtt_client.close()