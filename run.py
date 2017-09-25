import daemon
import logging
import requests
import sys
import time

from savemyorchids import fetch_data
from savemyorchids import utils

LOG = logging.getLogger(__name__)


def run():
    params = utils.read_config("default")
    ping_url = "http://%(host)s:%(port)s/ping" % {"host": params.influx_host,
                                                  "port": params.influx_port}
    wait_c = 0
    timeout = params.wait_for_influx_timeout
    step = params.wait_for_influx_step
    while wait_c < timeout:
        # wait until influxdb accepts connections
        try:
            data = requests.get(ping_url)
            if data.status_code == 204:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(step)
            LOG.info("Influxdb unreachable, sleeping for 10 seconds..")
            wait_c += step
    if wait_c >= timeout:
        LOG.error("Influxdb service was unreachable for %s seconds" % timeout)
        sys.exit("Influxdb unreachable, exiting")
    fetch_data.main()


run()
