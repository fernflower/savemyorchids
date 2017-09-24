#!/bin/sh

IMAGE=savemyorchids
SERVICE_NAME=orchids

sudo docker build -t $IMAGE .
# privileged flag has to be there for gpio management
sudo docker run -i --privileged --name $SERVICE_NAME $IMAGE
