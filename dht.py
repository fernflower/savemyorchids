import Adafruit_DHT as adht

import extdevinterface


class DHTSensor(extdevinterface.ExternalDevice):
    def __init__(self):
        super(DHTSensor, self).__init__(config_section="dht")
        self._signal_pin = int(self.params.pin)
        self._sensor_type = int(self.params.dht_type)

    def output(self):
        hum, temp = adht.read_retry(self._sensor_type, self._signal_pin)
        return {"temperature": temp, "humidity": hum}
