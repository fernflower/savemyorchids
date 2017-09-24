# Pull base image
FROM resin/rpi-raspbian:wheezy

COPY . /savemyorchids

# Install dependencies
RUN apt-get update && apt-get install -y \
        git \
        build-essential \
        python \
        python-dev \
        python-pip \
        python-virtualenv \
        --no-install-recommends && \
        rm -rf /var/lib/apt/lists/* && \
        chmod +x /savemyorchids/entrypoint.sh && \
        virtualenv -p /usr/bin/python2.7 /venv && \
        # this is a workaround to install python-daemon without errors
        /venv/bin/pip install docutils && \
        git clone https://github.com/adafruit/Adafruit_Python_DHT && \
        cd Adafruit_Python_DHT && /venv/bin/python setup.py install && \
        /venv/bin/pip install -r /savemyorchids/requirements.txt

# Define working directory
WORKDIR /savemyorchids

ENTRYPOINT ["/savemyorchids/entrypoint.sh"]

# Define default command
CMD ["bash"]
