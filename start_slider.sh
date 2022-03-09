#!/bin/bash

echo "killing web browser"
pkill -o chromium


echo "killing slider"
ID2=$(ps faux | grep python | grep main.py | awk '{print $2 }')

kill -9 $ID2

sleep 5

echo "starting slider"

rm /tmp/slider.log

cd /home/pi/biofeedback-jam/slider/; nohup /usr/bin/python3 main.py >> /tmp/slider.log 2>&1 &



