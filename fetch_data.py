import argparse
import csv
import datetime
import json
import logging
import sys
import time

import Adafruit_DHT as adht
import influxdb
import RPi.GPIO as IO

import display
import utils

LOG = logging.getLogger(__name__)
CONFIG = "config"
PARAMS = utils.read_config(CONFIG, "default")


def init_soil_sensor():
    # returns (vcc, dio)
    IO.setmode(IO.BCM)
    moisture_params = utils.read_config(CONFIG, "moisture")
    m_vcc, m_dio = int(moisture_params.vcc), int(moisture_params.dio)
    IO.setup(m_vcc, IO.OUT)
    IO.output(m_vcc, IO.HIGH)
    IO.setup(m_dio, IO.IN)
    return (m_vcc, m_dio)

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
    led_display = display.init_display()
    m_vcc, m_dio = init_soil_sensor()
    try:
        while True:
            data = fetch_data(parsed.dht, parsed.pin, m_vcc, m_dio)
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
            display.output(led_display, data["temperature"], data["humidity"])
            time.sleep(parsed.sleep)
    except KeyboardInterrupt:
        output.close()
        sys.exit()

def fetch_data(dht, pin, m_vcc, m_dio):
    hum, temp = adht.read_retry(dht, pin)
    # turn on soil sensor
    # IO.output(m_vcc, IO.HIGH)
    # collect data
    soil_state = IO.input(m_dio)
    # turn off soil sensor
    # IO.output(m_vcc, IO.LOW)
    if not hum or not temp:
        return None
    curr_date = datetime.datetime.now()
    date = datetime.datetime.strftime(curr_date, PARAMS.date_format)
    return {'date': date, 'temperature': temp, 'humidity': hum, 'soil_wet': (soil_state + 1) % 2}

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
