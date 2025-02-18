import time
import random
import paho.mqtt.client as mqtt

# MQTT Configuration (Set your server IP)
MQTT_BROKER = "127.0.0.1"  # Replace with actual server IP
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/temperature"

# MQTT Client Setup
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

try:
    while True:
        # Generate random temperature data
        temperature = round(random.uniform(20.0, 30.0), 2)
        payload = f'{{"temperature": {temperature}}}'
        client.publish(MQTT_TOPIC, payload)
        print(f"Published: {payload}")
        time.sleep(5)  # Send data every 5 seconds
except KeyboardInterrupt:
    print("Stopping...")
    client.disconnect()
