#!/bin/sh

ENV_FILE=config.sample
GRAFANA_SOURCE_NAME=orchids
GRAFANA_DASHBOARD_FILE=grafana_dashboard.json

function get_val {
    key=$1;
    echo $(cat $ENV_FILE | grep $key | head -n1 | sed 's/.*=//g');
}

# XXX this sucks but will do for a poc
influx_port=$(get_val "PORT")
influx_user=$(get_val "USER")
influx_pass=$(get_val "PASSWORD")
influx_dbname=$(get_val "DBNAME")
grafana_user=$(get_val "GRAFANA_AUTH_USER")
grafana_pass=$(get_val "GRAFANA_AUTH_PASS")

# start influx container
sudo docker run -d -p 8083:8083 -p "$influx_port:$influx_port" -e PRE_CREATE_DB="$influx_dbname" --expose 8090 --expose 8099 --name influxdb tutum/influxdb

# start grafana container
sudo docker run -d -p 3000:3000 --link influxdb:influxdb --name grafana grafana/grafana

# wait till containers are up and running
# XXX FIXME
sleep 3

# create influxdb source in grafana
curl "http://$grafana_user:$grafana_pass@127.0.0.1:3000/api/datasources" -X POST -H 'Content-Type: application/json;charset=UTF-8' --data-binary "{\"name\":\"$GRAFANA_SOURCE_NAME\",\"type\":\"influxdb\",\"url\":\"http://localhost:$influx_port\",\"access\":\"proxy\",\"isDefault\":true,\"database\":\"$influx_dbname\",\"user\":\"$influx_user\",\"password\":\"$influx_pass\"}"

# create a grafana dashboard from a json file
curl "http://$grafana_user:$grafana_pass@127.0.0.1:3000/api/dashboards/db" -X POST -H 'Content-Type: application/json;charset=UTF-8' --data-binary "@$GRAFANA_DASHBOARD_FILE"
