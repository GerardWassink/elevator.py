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
from gawterm import term				# screen class
import time								# time handling
import commands

t = term()

ClientID = "ELV_REM_" + commands.getoutput("whoami")
t.msgPrint("ClientID = " + ClientID)

# ------------------------------------------------------------------------
# The callback for when the client receives a CONNACK response from the server.
# ------------------------------------------------------------------------
def on_connect(client, userdata, flags, rc):
	t.msgPrint(ClientID+": Connected with result code "+str(rc))
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe("elevator/responses")

# ------------------------------------------------------------------------
# The callback for when a PUBLISH message is received from the server.
# ------------------------------------------------------------------------
def on_publish(client, userdata, mid):
#	t.msgPrint(ClientID+": mid: "+str(mid))
	pass
	
# ------------------------------------------------------------------------
# The callback for when a message is received from the server.
# ------------------------------------------------------------------------
def on_message(client, userdata, msg):
	t.msgPrint(msg.payload)

# ------------------------------------------------------------------------
# Initialise message queue object to send command to the mqtt broker
# ------------------------------------------------------------------------
client = mqtt.Client(client_id=ClientID, clean_session=False)
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

client.connect("localhost", 1883, 60)

# Continue the network loop, exit when an error occurs
client.loop_start()


t.msgPrint(ClientID+":")
t.msgPrint(ClientID+": ---=== Elevator remote control program ===---")
t.msgPrint(ClientID+":")

while True:
	reply = t.inpRead()
	t.cmdPrint(reply)
	reply = reply.upper()
	if reply == "EXIT" or reply == "X":
		time.sleep(0.2)
		client.loop_stop()
		client.disconnect()
		break
	else:
		client.publish("elevator/commands", payload=reply, qos=2, retain=False)


t.Close()

exit()
