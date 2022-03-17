#!/bin/bash


echo "killing mind monitor"
ID=$(ps faux | grep python | grep mind_monitor | awk '{print $2 }')

kill -9 $ID

sleep 10

rm -f /tmp/mind_monitor.log

echo "starting mind monitor"
export  PYTHONUNBUFFERED=x
cd /home/pi/biofeedback-jam/; /usr/bin/python3 mind_monitor_osc_server.py >> /tmp/mind_monitor.log 2>&1 &

