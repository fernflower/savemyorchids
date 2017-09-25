import utils


class ExternalDevice(object):
    """A base class for any peripheral device to be connected to RPi"""
    def __init__(self, config_section):
        self.params = utils.read_config(config_section)
        self._device = self.init()

    def init(self):
        """Performs initialization, sets and returns a device object
        
        Initialization means setting proper pins as 
        input\output\pullup or pulldown registers.
        """
        pass

    def output(self, *args, **kwargs):
        """Output data in some form.
        
        In case of display -> show the data;
        In case of sensor of any kind -> Return a dictionary representing current state
        """
        pass
