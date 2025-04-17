from influxdb_client import InfluxDBClient
import argparse

# InfluxDB Connection Details
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "tS-ZZkphsy7v2D8iEOLnqejZLOO1KrZJ5DmbXf8SBOamonOvgdwRpiwNyQuJ_GIgSS4AJm0o_BAKtl9JL8mEjw=="
INFLUX_ORG = "users"
INFLUX_BUCKET = "sensor_data"

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Query and analyze historical InfluxDB data")
parser.add_argument("--start_time", required=True, help="Start time (YYYY-MM-DD HH:MM:SS)")
parser.add_argument("--end_time", required=True, help="End time (YYYY-MM-DD HH:MM:SS)")
args = parser.parse_args()

# Convert time format for InfluxDB (RFC3339)
start_time = args.start_time.replace(" ", "T") + "Z"
end_time = args.end_time.replace(" ", "T") + "Z"

# Connect to InfluxDB
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = client.query_api()

# Define Flux Query (matching Grafana query)
query = f'''
from(bucket: "{INFLUX_BUCKET}")
  |> range(start: {start_time}, stop: {end_time})
  |> filter(fn: (r) => r["_measurement"] == "mqtt_consumer")
  |> filter(fn: (r) => r["_field"] == "altitude" or r["_field"] == "pressure" or r["_field"] == "temperature_c" or r["_field"] == "temperature_f")
  |> filter(fn: (r) => r["host"] == "cfbdf9d4e1bb")
  |> filter(fn: (r) => r["topic"] == "sensor/bmp280")
  |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
  |> yield(name: "mean")
'''

# Execute Query
result = query_api.query(org=INFLUX_ORG, query=query)

# Process and Print Results
print("\n📡 Querying InfluxDB for BMP280 Sensor Data...\n")
for table in result:
    for record in table.records:
        print(f"{record.get_time()} | {record.get_measurement()} | {record.get_field()} = {record.get_value()}")

client.close()
