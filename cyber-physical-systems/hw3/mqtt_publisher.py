import paho.mqtt.client as mqtt
import time
import json
import numpy as np
import ssl
import os

BROKER = "172.30.194.85"
PORT = 8883
TOPIC_SIGNAL = "sensor/cs_signal"
TOPIC_HR = "sensor/hr"
TOPIC_RR = "sensor/rr"

CA_CERT_PATH = "../mosquitto/certs/ca-root.crt"  # Path to CA certificate
CLIENT_CERT_PATH = "../mosquitto/certs/mosquitto.crt"
CLIENT_KEY_PATH = "../mosquitto/certs/mosquitto.key"

def publish_data(client, data):
    for i in range(data.shape[0]):
        current_time = int(time.time())

        signal = data[i, :1000].tolist()
        hr = float(data[i, -5])
        rr = float(data[i, -4])

        # Publish each message with the current timestamp
        client.publish(TOPIC_SIGNAL, json.dumps({"timestamp": current_time, "value": signal}))
        client.publish(TOPIC_HR, json.dumps({"timestamp": current_time, "value": hr}))
        client.publish(TOPIC_RR, json.dumps({"timestamp": current_time, "value": rr}))

        print(f"[MQTT] Frame {i} sent | HR={hr} | RR={rr} | Time={current_time}")
        time.sleep(1)

if __name__ == "__main__":
    data = np.load(os.path.join(os.path.dirname(__file__), "dataset_non_sensorweb.npy"))
    client = mqtt.Client()

    # Enable TLS
    client.tls_set(
        ca_certs=CA_CERT_PATH, 
        certfile=CLIENT_CERT_PATH,
        keyfile=CLIENT_KEY_PATH,
        tls_version=ssl.PROTOCOL_TLSv1_2
    )
    client.connect(BROKER, PORT, 60)

    publish_data(client, data)
