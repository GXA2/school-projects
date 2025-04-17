import paho.mqtt.client as mqtt
import json
import numpy as np
from scipy.signal import butter, filtfilt, savgol_filter, find_peaks
import ssl
import os

# === MQTT Config ===
BROKER = "172.30.194.85"
PORT = 8883
TOPIC_SIGNAL = "sensor/cs_signal"
TOPIC_HR_EST = "sensor/hr_est"
TOPIC_RR_EST = "sensor/rr_est"

# === SSL Paths ===
CA_CERT_PATH = "../mosquitto/certs/ca-root.crt"
CLIENT_CERT_PATH = "../mosquitto/certs/mosquitto.crt"
CLIENT_KEY_PATH = "../mosquitto/certs/mosquitto.key"

# === Signal Constants ===
SAMPLE_RATE = 100
WINDOW_DURATION = 10

# === Filtering Functions ===
def bandpass_filter(signal, low, high, fs=SAMPLE_RATE, order=4):
    nyq = 0.5 * fs
    b, a = butter(order, [low / nyq, high / nyq], btype='band')
    return filtfilt(b, a, signal)

def estimate_hr(signal):
    smoothed = savgol_filter(signal, window_length=41, polyorder=3)
    distance = int(0.45 * SAMPLE_RATE)
    peaks, _ = find_peaks(smoothed, distance=distance, prominence=1.2)
    return round(len(peaks) * (60 / WINDOW_DURATION), 2)

def estimate_rr(signal):
    smoothed = savgol_filter(signal, window_length=81, polyorder=3)
    distance = int(2.5 * SAMPLE_RATE)
    peaks, _ = find_peaks(smoothed, distance=distance, prominence=0)

    if len(peaks) < 2:
        return 0.0  # Not enough peaks to estimate RR

    intervals = np.diff(peaks) / SAMPLE_RATE  # seconds between peaks
    mean_interval = np.mean(intervals)
    rr = 60 / mean_interval
    return round(rr, 2)


# === Callback: When MQTT message is received ===
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        signal = np.array(payload["value"])
        timestamp = int(payload["timestamp"])

        # Filter input signal
        filtered_hr = bandpass_filter(signal, low=0.7, high=3.5)
        filtered_rr = bandpass_filter(signal, low=0.1, high=0.6)

        # Estimate HR and RR
        hr = estimate_hr(filtered_hr)
        rr = estimate_rr(filtered_rr)

        # Publish predictions
        client.publish(TOPIC_HR_EST, json.dumps({"timestamp": timestamp, "value": hr}))
        client.publish(TOPIC_RR_EST, json.dumps({"timestamp": timestamp, "value": rr}))

        print(f"[✔] HR: {hr} BPM | RR: {rr} RPM | t={timestamp}")

    except Exception as e:
        print(f"[✖] Error processing message: {e}")

# === Main MQTT Setup ===
def main():
    client = mqtt.Client()

    client.tls_set(
        ca_certs=CA_CERT_PATH, 
        certfile=CLIENT_CERT_PATH,
        keyfile=CLIENT_KEY_PATH,
        tls_version=ssl.PROTOCOL_TLSv1_2
    )
    client.tls_insecure_set(False)
    client.on_message = on_message

    client.connect(BROKER, PORT, 60)
    client.subscribe(TOPIC_SIGNAL)

    print(f"🔐 Subscribed securely to {TOPIC_SIGNAL}")
    client.loop_forever()

if __name__ == "__main__":
    main()
