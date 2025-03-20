import time
import board
import busio
import adafruit_bmp280
import paho.mqtt.client as mqtt
import json
import ssl

# MQTT Configuration
MQTT_BROKER = "172.30.194.85"  # Replace with actual IP
MQTT_PORT = 8883  # Secure MQTT port
MQTT_TOPIC = "sensor/bmp280"
CA_CERT_PATH = "./mosquitto/certs/ca-root.crt"  # Path to CA certificate
CLIENT_CERT_PATH = "./mosquitto/certs/mosquitto.crt"
CLIENT_KEY_PATH = "./mosquitto/certs/mosquitto.key"
# Initialize I2C Bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize BMP280 Sensor
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x77)  # Change to 0x77 if needed

# Optional: Adjust sea-level pressure for more accurate altitude
bmp280.sea_level_pressure = 1013.25  # Adjust based on your location

# MQTT Client Setup
client = mqtt.Client()

# Enable TLS
client.tls_set(
    ca_certs=CA_CERT_PATH, 
    certfile=CLIENT_CERT_PATH,
    keyfile=CLIENT_KEY_PATH,
    tls_version=ssl.PROTOCOL_TLSv1_2
)

# Connect to MQTT Broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

try:
    while True:
        temperature_c = bmp280.temperature  # °C
        temperature_f = round((temperature_c * 9/5) + 32, 2)  # Convert to °F
        pressure = round(bmp280.pressure, 2)  # hPa
        altitude = round(bmp280.altitude, 2)  # meters
        timestamp = int(time.time())  # Unix timestamp

        payload = json.dumps({
            "temperature_c": round(temperature_c, 2),
            "temperature_f": temperature_f,
            "pressure": pressure,
            "altitude": altitude,
            "time": timestamp
        })

        client.publish(MQTT_TOPIC, payload)
        print(f"Published: {payload}")

        time.sleep(5)  # Send data every 5 seconds

except KeyboardInterrupt:
    print("Stopping...")
    client.disconnect()
