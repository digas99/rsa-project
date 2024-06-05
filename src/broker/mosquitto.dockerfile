FROM eclipse-mosquitto:latest

# MQTT port + WS port
EXPOSE 1884
EXPOSE 9001

# Copy the configuration file
COPY mosquitto.conf /mosquitto/config/mosquitto.conf

# Start the broker
CMD ["/usr/sbin/mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]