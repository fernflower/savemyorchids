import RPi.GPIO as IO

import extdevinterface


class SoilSensor(extdevinterface.ExternalDevice):
    def __init__(self):
        super(SoilSensor, self).__init__(config_section="soil")

    def init(self):
        self._vcc = int(self.params.vcc)
        self._dio = int(self.params.dio)
        # board ordering is used for this project
        IO.setmode(IO.BCM)
        IO.setup(self._vcc, IO.OUT)
        IO.output(self._vcc, IO.HIGH)
        IO.setup(self._dio, IO.IN)

    def output(self):
        # turn on soil sensor
        # IO.output(m_vcc, IO.HIGH)
        # collect data
        soil_state = IO.input(self._dio)
        # turn off soil sensor
        # IO.output(m_vcc, IO.LOW)
        # 1 is ok and 0 not
        return {"soil_state": soil_state}
