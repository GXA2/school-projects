import paho.mqtt.client as mqtt
import ssl
import json
import yaml

# Load sensor config from YAML
CONFIG_FILE = "./ai/config.yml"
with open(CONFIG_FILE, "r") as file:
    config = yaml.safe_load(file)

# MQTT Configuration
MQTT_BROKER = "172.30.194.85"  # Replace with actual IP
MQTT_PORT = 8883
MQTT_TOPIC = "sensor/#"
CA_CERT_PATH = "./mosquitto/certs/ca-root.crt"  # Path to CA certificate
CLIENT_CERT_PATH = "./mosquitto/certs/mosquitto.crt"
CLIENT_KEY_PATH = "./mosquitto/certs/mosquitto.key"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker.")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        sensor_type = msg.topic.split("/")[-1]  # Extract sensor name from topic

        if sensor_type in config["sensors"]:
            processed_data = {key: payload[key] for key in config["sensors"][sensor_type]["measurements"] if key in payload}
            print(f"Processed Data from {sensor_type}: {processed_data}")

            # Add AI processing (example: anomaly detection)
            if "temperature_f" in processed_data and processed_data["temperature_f"] > 77:
                print("⚠️ Warning: High Temperature Detected!")

        else:
            print(f"Received data from unknown sensor: {sensor_type}")

    except Exception as e:
        print(f"Error processing MQTT message: {e}")

# Initialize MQTT Client
client = mqtt.Client()
client.tls_set(
    ca_certs=CA_CERT_PATH, 
    certfile=CLIENT_CERT_PATH,
    keyfile=CLIENT_KEY_PATH,
    tls_version=ssl.PROTOCOL_TLSv1_2
)
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
