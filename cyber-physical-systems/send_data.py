import time
import random
import paho.mqtt.client as mqtt
import json

# MQTT Configuration
MQTT_BROKER = "192.168.184.183"  # Replace with actual server IP
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/temperature"

# MQTT Client Setup
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

try:
    while True:
        # Generate random temperature data
        temperature = round(random.uniform(20.0, 30.0), 2)
        timestamp = int(time.time())  # UNIX timestamp in seconds

        payload = json.dumps({
            "temperature": temperature,
            "time": timestamp  # Add a timestamp field
        })

        client.publish(MQTT_TOPIC, payload)
        print(f"Published: {payload}")
        time.sleep(5)  # Send data every 5 seconds
except KeyboardInterrupt:
    print("Stopping...")
    client.disconnect()

