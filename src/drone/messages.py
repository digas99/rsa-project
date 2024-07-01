import paho.mqtt.client as mqtt

class MQTTClient:
	def __init__(self, broker, port, topic):
		self.broker = broker
		self.port = port
		self.topic = topic
		self.client = mqtt.Client()

		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message

		self.client.connect(broker, port, 60)
		
	def start(self, blocking=False):
		if blocking:
			self.client.loop_forever()
		else:
			self.client.loop_start()
	
	def publish(self, message):
		self.client.publish(self.topic, message)

	def close(self):
		self.client.loop_stop()
		self.client.disconnect()

	def on_message(self, client, userdata, message):
		print(f"Received message: {message.payload.decode()} on topic {message.topic}")

	def on_connect(self, client, userdata, flags, rc):
		print(f"Connected with result code {rc}")
		self.client.subscribe(self.topic)

