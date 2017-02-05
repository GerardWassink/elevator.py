#!/usr/bin/python

# ------------------------------------------------------------------------
# Program		:	elevator_monitor.py
# Author		:	Gerard Wassink
# Date			:	january 2017
#
# Function		:	monitor msg queue broker for elevator/*
#
# ------------------------------------------------------------------------
# 						GNU LICENSE CONDITIONS
# ------------------------------------------------------------------------
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# ------------------------------------------------------------------------
#				Copyright (C) 2016 Gerard Wassink
# ------------------------------------------------------------------------

import paho.mqtt.client as mqtt			# msg queueing
import time								# time handling

print "ELV_MON:  "
print "ELV_MON: -----===== Elevator monitor program =====-----"
print "ELV_MON:  "

time.sleep(0.5)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	print "ELV_MON: Connected with result code "+str(rc)
	
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	print "ELV_MON: Asking for subscription"
	client.subscribe("elevator/#", qos=2)

# The callback for when a message is received from the server.
def on_message(client, userdata, msg):
	print "ELV_MON: "+": "+msg.payload

client = mqtt.Client(client_id="ELV_MON", clean_session=False)
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

# Continue the network loop, exit when an error occurs
client.loop_start()

while True:
	reply = raw_input("Monitor command (Q to Quit): ")
	print "\n"
	reply = reply.upper()
	if reply == "Q":
		time.sleep(0.2)
		client.loop_stop()
		client.disconnect()
		break

exit()