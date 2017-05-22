import daemon
import fetch_data
import logging
import requests
import sys
import time

import utils

CONFIG = "config"
TIMEOUT = 600
STEP = 10
LOG = logging.getLogger(__name__)


def run():
    params = utils.read_config(CONFIG, "influx")
    ping_url = "http://%(host)s:%(port)s/ping" % {"host": params.host,
                                                  "port": params.port}
    wait_c = 0
    while wait_c < TIMEOUT:
        # wait until influxdb accepts connections
        try:
            data = requests.get(ping_url)
            if data.status_code == 204:
                break
        except requests.exceptions.ConnectionError:
            time.sleep(STEP)
            LOG.info("Influxdb unreachable, sleeping for 10 seconds..")
            wait_c += STEP
    if wait_c >= TIMEOUT:
        LOG.error("Influxdb service was unreachable for %s seconds" % TIMEOUT)
        sys.exit("Influxdb unreachable, exiting")
    fetch_data.main()


run()
