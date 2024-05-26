import paho.mqtt.client as mqtt

# Define the callback for when a message is received
def on_message(client, userdata, message):
    print(f"Received message: {message.payload.decode()} on topic {message.topic}")

# Create an MQTT client instance
client = mqtt.Client()

# Attach the message callback
client.on_message = on_message

# Connect to the broker
client.connect("localhost", 1883, 60)

# Subscribe to a topic
client.subscribe("rsa/count")
client.subscribe("rsa/coordinates")

# Start the loop
client.loop_start()

# Publish a message
client.publish("rsa/count", "23 people")
client.publish("rsa/coordinates","1.3434234; 2.432452352")

# Keep the script running
while True:
    pass

