#!/usr/bin/python

# ------------------------------------------------------------------------
# Program		:	elevator_remote.py
# Author		:	Gerard Wassink
# Date			:	december 2016
#
# Function		:	send control command to an elevator with four floors
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

ClientID = "ELV_REM"

# ------------------------------------------------------------------------
# The callback for when the client receives a CONNACK response from the server.
# ------------------------------------------------------------------------
def on_connect(client, userdata, flags, rc):
	print ClientID+": Connected with result code "+str(rc)
		# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe("elevator/responses")

# ------------------------------------------------------------------------
# The callback for when a PUBLISH message is received from the server.
# ------------------------------------------------------------------------
def on_publish(client, userdata, mid):
	print ClientID+": mid: "+str(mid)

# ------------------------------------------------------------------------
# The callback for when a message is received from the server.
# ------------------------------------------------------------------------
def on_message(client, userdata, msg):
	print ClientID+": response: "+msg.payload

# ------------------------------------------------------------------------
# Initialise message queue object to send command to the mqtt broker
# ------------------------------------------------------------------------
client = mqtt.Client(client_id=ClientID, clean_session=False)
client.on_connect = on_connect
client.on_publish = on_publish

client.connect("localhost", 1883, 60)

# Continue the network loop, exit when an error occurs
client.loop_start()


print ClientID+":"
print ClientID+": -----===== Elevator remote control program =====-----"
print ClientID+":"

while True:
	reply = raw_input("Remote input > ")
	reply = reply.upper()
	client.publish("elevator/commands", payload=reply, qos=2, retain=False)
	if reply == "QUIT" or reply == "Q":
		time.sleep(0.2)
		client.loop_stop()
		client.disconnect()
		break

exit()