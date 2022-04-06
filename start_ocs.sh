#!/bin/bash

while :
do
	echo "killing ocs"
	ID=$(ps faux | grep python | grep ocs | awk '{print $2 }')

	kill -9 $ID
	sleep 60

	echo "starting ocs emulator"
	export  PYTHONUNBUFFERED=x
	cd /home/pi/biofeedback-jam/; /usr/bin/python3 ocs_emulator.py &

	sleep 300
done


