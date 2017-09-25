import csv
import json
import sys

import influxdb

from savemyorchids import utils


class PlainWriter(object):
    def __init__(self, data_format, filename=None):
        if data_format not in ["csv", "json"]:
            raise NotImplemented()
        self.format = data_format
        self.stream = open(filename, 'a') if filename else sys.stdout
        if self.format == "csv":
            self.writer = csv.writer(self.stream, delimiter=',')
            self.writer.writerow(['Date', 'Temperature', 'Humidity', 'Soil'])

    def write(self, data):
        if self.format == 'csv':
            self.writer.writerow([data['date'], data['temperature'],
                data['humidity'], data['soil_wet']])
        elif self.format == 'json':
            self.stream.write(json.dumps(data) + "\n")

    def close(self):
        self.stream.close()


class InfluxDBWriter(object):

    def __init__(self, config_section="default"):
        self.params = utils.read_config(config_section)
        self.client = influxdb.InfluxDBClient(self.params.influx_host,
                                              int(self.params.influx_port),
                                              self.params.influx_user,
                                              self.params.influx_password,
                                              self.params.influx_dbname)

    def write(self, data):
        body = [{"measurement": "climate",
                 "fields": {"temperature" : data["temperature"],
                            "humidity": data["humidity"]}
                },
                {"measurement": "soil",
                 "fields": {"is_wet": data["soil_wet"]}},]
        self.client.write_points(body)

