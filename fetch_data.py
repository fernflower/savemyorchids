import argparse
import datetime
import logging
import sys
import time


import display
import dht
import soilsensor
import writers

LOG = logging.getLogger(__name__)
DATE_FORMAT="%d/%m/%Y %H:%M:%S"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sleep', default=5)
    parser.add_argument('--format', default='json', choices=['csv', 'json'],
            help="Data output format")
    parser.add_argument('--filename')
    parser.add_argument('--nowrite', action='store_true', default=False)
    parsed = parser.parse_args()

    writer = writers.PlainWriter(data_format=parsed.format, filename=parsed.filename)
    influx_writer = writers.InfluxDBWriter() if not parsed.nowrite else None
    led_display = display.FourDigitDisplay()
    dht11 = dht.DHTSensor()
    soil_sensor = soilsensor.SoilSensor()
    try:
        while True:
            data = fetch_data(dht11, soil_sensor)
            LOG.info("Data fetched: %s" % data)
            if not data:
                LOG.error("Sensor could not fetch any data!")
                continue
            writer.write(data)
            if influx_writer:
                influx_writer.write(data)
            led_display.output(data["temperature"], data["humidity"])
            time.sleep(parsed.sleep)
    except KeyboardInterrupt:
        writer.close()
        sys.exit()

def fetch_data(dht_sensor, soil_sensor):
    dht_data = dht_sensor.output()
    soil = soil_sensor.output()
    dht_data.update(soil)
    check_keys = ["temperature", "humidity", "soil_state"]
    if not any([dht_data.get(k) for k in check_keys]):
        return None
    curr_date = datetime.datetime.now()
    date = datetime.datetime.strftime(curr_date, DATE_FORMAT)
    return {'date': date, 'temperature': dht_data["temperature"],
            'humidity': dht_data["humidity"], 'soil_wet': (soil["soil_state"] + 1) % 2}


if __name__ == "__main__":
    main()
