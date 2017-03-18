#!/usr/bin/python

# ------------------------------------------------------------------------
# Program		:	elevator_monitor.py
# Author		:	Gerard Wassink
# Date			:	january 2017
#
# Function		:	monitor msg queue broker for elevator/#
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

keep_going = True
subscr_topic = "elevator/#"

print "ELV_MON:  "
print "ELV_MON: -----===== Elevator monitor program =====-----"
print "ELV_MON:  "

# ------------------------------------------------------------------------
# The callback for when the client receives a CONNACK response from the server.
# ------------------------------------------------------------------------
def on_connect(client, userdata, flags, rc):
	print "ELV_MON: Connected with result code "+str(rc)
	
										# Subscribing in on_connect() means that
										# if we lose the connection and
										# reconnect then subscriptions will be
										# renewed.
	print "ELV_MON: Subscribing"
	client.subscribe(subscr_topic, qos=2)

# ------------------------------------------------------------------------
# The callback for when a message is received from the server.
# ------------------------------------------------------------------------
def on_message(client, userdata, msg):
	global keep_going
	print "ELV_MON: "+": "+msg.payload
	if msg.payload.upper() == "QUIT" or msg.payload.upper() == "Q":
		keep_going = False

# ------------------------------------------------------------------------
# Initialise broker client object
# ------------------------------------------------------------------------

										# create the client object
client = mqtt.Client(client_id="ELV_MON", clean_session=False)

										# register callback routines
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)	# connect client to broker

client.loop_start()						# Continue the network loop, exit when
										# an error occurs

# ------------------------------------------------------------------------
# Main loop (to catch callbacks)
# ------------------------------------------------------------------------

while keep_going:						# loop until Q command
	time.sleep(0.2)


# ------------------------------------------------------------------------
# End of program
# ------------------------------------------------------------------------
time.sleep(0.2)							# allow for some time
print "ELV_MON: Unsubscribing"
client.unsubscribe(subscr_topic)		# unsubscribe the topic
client.loop_stop()						# stop the client loop
client.disconnect()						# disconnect from broker
print "ELV_MON: Disconnected"
exit()									# leave