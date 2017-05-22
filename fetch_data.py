import argparse
import csv
import datetime
import json
import logging
import sys
import time

import influxdb

import display
import dht
import soilsensor
import utils

LOG = logging.getLogger(__name__)
CONFIG = "config"
PARAMS = utils.read_config(CONFIG, "default")


def main():
    parser = argparse.ArgumentParser()
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
    led_display = display.FourDigitDisplay()
    dht11 = dht.DHTSensor()
    soil_sensor = soilsensor.SoilSensor()
    try:
        while True:
            data = fetch_data(dht11, soil_sensor)
            LOG.info("Data fetched: %s" % data)
            if not data:
                LOG.error("Sensor could not fetch both temperature and humidity!")
                continue
            if parsed.format == 'csv':
                writer.writerow([data['date'], data['temperature'], data['humidity']])
            elif parsed.format == 'json':
                output.write(json.dumps(data) + "\n")
            if not parsed.nowrite:
                write_to_influx(data)
            led_display.output(data["temperature"], data["humidity"])
            time.sleep(parsed.sleep)
    except KeyboardInterrupt:
        output.close()
        sys.exit()

def fetch_data(dht_sensor, soil_sensor):
    dht_data = dht_sensor.output()
    soil = soil_sensor.output()
    dht_data.update(soil)
    check_keys = ["temperature", "humidity", "soil_state"]
    if not all([dht_data.get(k) for k in check_keys]):
        return None
    curr_date = datetime.datetime.now()
    date = datetime.datetime.strftime(curr_date, PARAMS.date_format)
    return {'date': date, 'temperature': dht_data["temperature"],
            'humidity': dht_data["humidity"], 'soil_wet': (soil["soil_state"] + 1) % 2}

def write_to_influx(data):
    client = influxdb.InfluxDBClient(PARAMS.influx_host, PARAMS.influx_port, PARAMS.influx_user,
            PARAMS.influx_password, PARAMS.influx_dbname)
    body = [{"measurement": 'climate',
             "fields": {"temperature" : data["temperature"],
                        "humidity": data["humidity"]}
            },
            {"measurement": "soil",
             "fields": {"is_wet": data["soil_wet"]}},]
    client.write_points(body)


if __name__ == "__main__":
    main()
