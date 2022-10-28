#!/bin/bash


echo "killing mind monitor"
ID=$(ps faux | grep python | grep osc_broadcast_server | awk '{print $2 }')

kill -9 $ID

sleep 10

rm -f /tmp/mind_monitor.log

echo "starting mind monitor"
export  PYTHONUNBUFFERED=x
cd /home/pi/biofeedback-jam/; /usr/bin/python3 osc_broadcast_server.py >> /tmp/osc_broadcast_server.log 2>&1 &

