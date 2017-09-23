#!/bin/sh

ENV_FILE=config
INFLUX_IMAGE=hypriot/rpi-influxdb

function get_val {
    key=$1;
    echo $(cat $ENV_FILE | grep $key | head -n1 | sed 's/.*=//g');
}

# XXX this sucks but will do for a poc
influx_port=$(get_val "PORT")
influx_user=$(get_val "USER")
influx_pass=$(get_val "PASSWORD")
influx_dbname=$(get_val "DBNAME")

# start influx container
sudo docker run -d -p 8083:8083 -p "$influx_port:$influx_port" -e ADMIN_USER="$influx_user" -e INFLUXDB_INIT_PWD="$influx_pass" -e PRE_CREATE_DB="$influx_dbname" --expose 8090 --expose 8099 --name influxdb $INFLUX_IMAGE
