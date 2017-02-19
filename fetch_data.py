import argparse
import csv
import datetime
import json
import sys
import time

import Adafruit_DHT as adht
import influxdb

import utils

CONFIG = "config"
PARAMS = utils.read_config(CONFIG, "default")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pin', default=PARAMS.pin, help="Signal pin number, BOARD numbering")
    parser.add_argument('--dht', default=int(PARAMS.sensor))
    parser.add_argument('--sleep', default=5)
    parser.add_argument('--format', default='json', choices=['csv', 'json'],
            help="Data output format")
    parser.add_argument('--filename')
    parser.add_argument('--nowrite', action='store_true', default=False)
    parsed = parser.parse_args()
    output = open(parsed.filename, 'a') if parsed.filename else sys.stdout
    if parsed.format == 'csv':
        writer = csv.writer(output, delimiter=',')
        writer.writerow(['Date', 'Temperature', 'Humidity'])
    try:
        while True:
            data = fetch_data(parsed.dht, parsed.pin)
            if not data:
                continue
            if parsed.format == 'csv':
                writer.writerow([data['date'], data['temperature'], data['humidity']])
            elif parsed.format == 'json':
                output.write(json.dumps(data) + "\n")
            if not parsed.nowrite:
                write_to_influx(data)
            time.sleep(parsed.sleep)
    except KeyboardInterrupt:
        output.close()
        sys.exit()

def fetch_data(dht, pin):
    hum, temp = adht.read_retry(dht, pin)
    if not hum or not temp:
        return None
    curr_date = datetime.datetime.now()
    date = datetime.datetime.strftime(curr_date, PARAMS.date_format)
    return {'date': date, 'temperature': temp, 'humidity': hum}

def write_to_influx(data):
    client = influxdb.InfluxDBClient(PARAMS.influx_host, PARAMS.influx_port, PARAMS.influx_user,
            PARAMS.influx_password, PARAMS.influx_dbname)
    body = [{"measurement": 'climate',
             "fields": {"temperature" : data["temperature"],
                        "humidity": data["humidity"]}
            }]
    client.write_points(body)


if __name__ == "__main__":
    main()
