import time
import paho.mqtt.client as mqtt
import board
import busio
import adafruit_adxl34x

# MQTT Configuration
MQTT_BROKER = "your-server-ip"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/temperature"

# Setup I2C connection for ADXL345
i2c = busio.I2C(board.SCL, board.SDA)
accelerometer = adafruit_adxl34x.ADXL345(i2c)

# MQTT Client Setup
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

def read_temperature():
    # Simulating temperature as ADXL345 does not provide it.
    return 25.0  # Replace with an actual method if needed.

try:
    while True:
        temperature = read_temperature()
        payload = f'{{"temperature": {temperature}}}'
        client.publish(MQTT_TOPIC, payload)
        print(f"Published: {payload}")
        time.sleep(5)  # Send data every 5 seconds
except KeyboardInterrupt:
    print("Stopping...")
    client.disconnect()
