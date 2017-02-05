#!/usr/bin/python

# ------------------------------------------------------------------------
# Program		:	elevator.py
# Author		:	Gerard Wassink
# Date			:	december 2016
#
# Function		:	control an elevator with four floors
#					one switch per floor so we know where the cabin is
#					commands to control the elevator system
#						(see the explain() routine)
#
# History		:	20170205 -Added message queueing instead of serial
#						file to communicate between elevator and remote
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

# ------------------------------------------------------------------------
# Libraries used
# ------------------------------------------------------------------------
										# for the Motor Hat board
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
from collections import deque			# a neat queue class
import paho.mqtt.client as mqtt			# message queueing library
import atexit							# to register stuff to be executed
										#	at exit
import logging							# for logging
import pigpio							# Raspberry Pi GPIO lib
import time								# be able to tell the time

# ------------------------------------------------------------------------
# Initial stuff
# ------------------------------------------------------------------------
pi = pigpio.pi()						# Connect to the pi
mh = Adafruit_MotorHAT(addr=0x60)		# create default Motor HAT object

# ------------------------------------------------------------------------
# Global variables
# ------------------------------------------------------------------------
ON = 1
OFF = 0

forward		= Adafruit_MotorHAT.FORWARD
backward	= Adafruit_MotorHAT.BACKWARD
release		= Adafruit_MotorHAT.RELEASE

time_stamp = time.time()				# now is the time
last_time_action = time.time()			# last time there was action

# ------------------------------------------------------------------------
# 										Set logging level
# ------------------------------------------------------------------------
#LOGLEVEL = logging.NOTSET				# 0
#LOGLEVEL = logging.DEBUG				# 10
#LOGLEVEL = logging.INFO				# 20
#LOGLEVEL = logging.WARNING				# 30
#LOGLEVEL = logging.ERROR				# 40
#LOGLEVEL = logging.CRITICAL			# 50

LOGLEVEL = logging.DEBUG

# ------------------------------------------------------------------------
# 										Set logging format
# ------------------------------------------------------------------------
logging.basicConfig(level=LOGLEVEL, \
			format='%(asctime)s: %(levelname)s: %(message)s', \
			datefmt='%Y-%m-%d,%I:%M:%S')


# ------------------------------------------------------------------------
# CLASS Definitions
# ------------------------------------------------------------------------
# 										Elevator class
# ------------------------------------------------------------------------
class elevator():
	def __init__(self):
		# ------------------------------------------------------------------------
		# PREPARE OUTPUT PINS
		# ------------------------------------------------------------------------
		# 								Output LED pins (BCM Numbering)
		# ------------------------------------------------------------------------
		self.first		=	21			# LED's that
		self.second		=	20			#  indicate the
		self.third		=	16			#   floor the
		self.fourth		=	26			#    cabin is at
		
		self.green		=	17			# indicate up
		self.red		=	27			# indicate stop
		self.yellow		=	 5			# indicatie down
		
		# ----------------------------------------------------------------
		# 								Input switch pins (BCM Numbering)
		# ----------------------------------------------------------------
		self.floor_1	=	23			# input's that
		self.floor_2	=	22			#  sense the
		self.floor_3	=	24			#   cabin at
		self.floor_4	=	25			#    each floor
		
		# ------------------------------------------------------------------------
		# 								Prepare output pins for LED's
		# ------------------------------------------------------------------------
		pi.set_mode(self.first, pigpio.OUTPUT)
		pi.set_mode(self.second, pigpio.OUTPUT)
		pi.set_mode(self.third, pigpio.OUTPUT)
		pi.set_mode(self.fourth, pigpio.OUTPUT)
		
		pi.set_mode(self.red, pigpio.OUTPUT)
		pi.set_mode(self.red, pigpio.OUTPUT)
		pi.set_mode(self.yellow, pigpio.OUTPUT)
		
		# ----------------------------------------------------------------
		# 								Prepare input pins for switches
		# ----------------------------------------------------------------
		pi.set_pull_up_down(self.floor_1, pigpio.PUD_DOWN)
		pi.set_mode(self.floor_1, pigpio.INPUT)
		pi.set_pull_up_down(self.floor_2, pigpio.PUD_DOWN)
		pi.set_mode(self.floor_2, pigpio.INPUT)
		pi.set_pull_up_down(self.floor_3, pigpio.PUD_DOWN)
		pi.set_mode(self.floor_3, pigpio.INPUT)
		pi.set_pull_up_down(self.floor_4, pigpio.PUD_DOWN)
		pi.set_mode(self.floor_4, pigpio.INPUT)
		
		# ----------------------------------------------------------------
		# 								CABIN related stuff
		# ----------------------------------------------------------------
		self.position = 0				# position
		self.direction = "none"			# direction
		self.destination = 0			# destination
		self.max_floor = 4				# highest floor
		self.cab_moving = False			# are we moving?
		
		self.cabinMotor = mh.getMotor(3)	# our motor is 3
		self.upSpeed = 200				# set speed going up
		self.downSpeed = 180			# set speed going down
		self.stop()						# make sure we're not moving
		
		self.reqque = deque()			# Request queue 
		
		
		# ----------------------------------------------------------------
		# 								Prepare event handlers
		# ----------------------------------------------------------------
		# floors[] is a list that contains lists, one list per floor
		# 	floor[0] contains the floor number 
		# 	floor[1] contains the BCM pin number for the floor switch 
		# 	floor[2] contains a pointer to the callback routine 
		# ----------------------------------------------------------------
		self.floors =	[[1,self.floor_1], \
						[2,self.floor_2], \
						[3,self.floor_3], \
						[4,self.floor_4] ]
		
		for self.floor in (self.floors):
										# SET position of cab when we
										# find a floor switch pressed
			if pi.read(self.floor[1]) == 1:
				self.set_position(self.floor[0])
										# set handlers for floor switches
										# and add pointer to the list
			self.floor.append(pi.callback(self.floor[1], \
				pigpio.RISING_EDGE, \
				self.input_handler))
		
		
	# --------------------------------------------------------------------
	# 									Input event handler for
	# 										all floor switches
	# --------------------------------------------------------------------
	def input_handler(self, gpio, lvl, tick):
	
		global last_time_action
		global time_stamp				# time held globally, outside
										#	interrupt routine
		
		last_time_action = time.time()
		time_now = time.time()				# compare the time with
		if (time_now - time_stamp) >= 0.3:	#	previous; 0.3 seconds past?
											# then go, else ignore
			if gpio == self.floor_1:
				logging.debug("ELV_RPI: FIRST floor")
				if self.destination == 1:
					self.stop()
				self.set_position(1)
				pi.write(self.first, 1)
				pi.write(self.second, 0)
				pi.write(self.third, 0)
				pi.write(self.fourth, 0)
			
			elif gpio == self.floor_2:
				logging.debug("ELV_RPI: SECOND floor")
				if self.destination == 2:
					self.stop()
				self.set_position(2)
				pi.write(self.first, 0)
				pi.write(self.second, 1)
				pi.write(self.third, 0)
				pi.write(self.fourth, 0)
			
			elif gpio == self.floor_3:
				logging.debug("ELV_RPI: THIRD floor")
				if self.destination == 3:
					self.stop()
				self.set_position(3)
				pi.write(self.first, 0)
				pi.write(self.second, 0)
				pi.write(self.third, 1)
				pi.write(self.fourth, 0)
			
			elif gpio == self.floor_4:
				logging.debug("ELV_RPI: FOURTH floor")
				if self.destination == 4:
					self.stop()
				self.set_position(4)
				pi.write(self.first, 0)
				pi.write(self.second, 0)
				pi.write(self.third, 0)
				pi.write(self.fourth, 1)
			
			else:
				logging.error("ELV_RPI: invalid input")
				
		time_stamp = time_now			# save time to global
										#	for next compare
	
	
	# ----------------------------------------------------------------
	# 									Un-register event handlers
	# ----------------------------------------------------------------
	def deregister_handlers(self):
		for self.floor in (self.floors):
			self.floor[2].cancel()
	
	
	# ----------------------------------------------------------------
	# 									CABIN methods
	# ----------------------------------------------------------------	
	def go_up(self):
		self.cabinMotor.run(forward)
		self.cabinMotor.setSpeed(self.upSpeed)
		self.direction = "up"
		self.direction_leds(self.direction)
		self.cab_moving = True
	
	def go_down(self):
		self.cabinMotor.run(backward)
		self.cabinMotor.setSpeed(self.downSpeed)
		self.direction = "down"
		self.direction_leds(self.direction)
		self.cab_moving = True
	
	def stop(self):
		self.cabinMotor.setSpeed(0)
		self.cabinMotor.run(release)
		self.direction = "none"				# not moving anymore
		self.destination = 0				# no destination now
		self.direction_leds(self.direction) 
		self.cab_moving = False
	
	def set_destination(self, dest):
		self.destination = dest
		if self.destination <> self.position:
			if self.destination > self.position:
				self.go_up()
			else:
				self.go_down()
	
	def set_position(self, pos):
		self.position = pos
	
	def direction_leds(self, dir):
		if dir == "up":
			pi.write(self.green, 1)
			pi.write(self.red, 0)
			pi.write(self.yellow, 0)
		elif dir == "down":
			pi.write(self.green, 0)
			pi.write(self.red, 0)
			pi.write(self.yellow, 1)
		elif dir == "none":
			pi.write(self.green, 0)
			pi.write(self.red, 1)
			pi.write(self.yellow, 0)
		elif dir == "off":
			pi.write(self.green, 0)
			pi.write(self.red, 0)
			pi.write(self.yellow, 0)
		else:
			logging.error("ELV_RPI: invalid value received")
	
	
# ------------------------------------------------------------------------
# 									QUEUE CLASS
# ------------------------------------------------------------------------
	def que_empty(self):
		if self.reqque:
			return False
		else:
			return True
	
	def push_request(self, req):
		global last_time_action
		last_time_action = time.time()
		
		self.from_pos = int(req[0:req.find("-")])
		self.to_pos = int(req[req.find("-")+1:])
		self.reqque.append([self.from_pos, self.to_pos])
	
	def next_request(self):
		if self.reqque:
			return self.reqque.popleft()
		else:
			return [-1, -1]
	

# ------------------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# 									Disable motors on shutdown!
# ------------------------------------------------------------------------
def turnAllOff():
	mh.getMotor(1).run(release)
	mh.getMotor(2).run(release)
	mh.getMotor(3).run(release)
	mh.getMotor(4).run(release)

# ------------------------------------------------------------------------
# 									Explain commands
# ------------------------------------------------------------------------
def explain():
	print "Elevator program commands"
	print " "
	print "help | h : this help information"
	print " "
	print "up | u   : make cabin go up"
	print "down | d : make cabin go down"
	print "stop | s : make cabin stop"
	print " "
	print "1|2|3|4  : set destination to some floor and go there"
	print " "
	print "X-Y      : I'm on floor X and wanna go to floor Y"
	print " "
	print "quit | q : end the program"
	print " "


# ------------------------------------------------------------------------
# 									Show program status
# ------------------------------------------------------------------------
def show_status():
	print " "
	print "	--------------------=== STATUS ===--------------------"
	print "	position = 	", elv.position
	print "	direction =	", elv.direction
	print "	destination =	", elv.destination
	print " "
	print "	--------------------=== QUEUE  ===--------------------"
	print " "
	if elv.que_empty():						# que empty?
		print "	QUEUE IS EMPTY"
	else:
		for r in elv.reqque:
			print "	", r
	print "	--------------------=== END STATUS ===----------------"

# ------------------------------------------------------------------------
# End program
# ------------------------------------------------------------------------
def cleanup():
	logging.debug("ELV_RPI: Clearing events")
	elv.deregister_handlers()				# cancel handlers
	turnAllOff()							# turn off all engines
	elv.direction_leds("off")				# switch of other LED's

	client.loop_stop()						# Stop the msg que loop
	client.disconnect()						# disconnect from msg que

	pi.write(elv.first, 0)
	pi.write(elv.second, 0)
	pi.write(elv.third, 0)
	pi.write(elv.fourth, 0)
	pi.stop()								# disconnect from pi


# ------------------------------------------------------------------------
# Start of program
# ------------------------------------------------------------------------
print " "
print "-----=====##### Start elevator program #####=====-----"
print " "


# ------------------------------------------------------------------------
# Register the shutdown routine that switches everything off when we exit
# ------------------------------------------------------------------------
atexit.register(cleanup)

# ------------------------------------------------------------------------
# 											MAIN CODE STARTS HERE
# ------------------------------------------------------------------------

# ------------------------------------------------------------------------
# Start program
# ------------------------------------------------------------------------

elv = elevator()							# create elevator object

# ------------------------------------------------------------------------
# Show commands and initial status
# ------------------------------------------------------------------------
show_status()								# show initial status

# ------------------------------------------------------------------------
# Some initialization
# ------------------------------------------------------------------------
from_floor = -1								# at this point
to_floor = -1								# 	no request pending

if elv.position == 0:						# did we find the cabin?
	logging.info("ELV_RPI: Cabin position not defined, moving to ground floor")
	elv.position = 4						# set from to highest floor		
	elv.set_destination(1)					# move down to 1st floor
elif elv.position == 1:	pi.write(elv.first, 1)	# set floor LED
elif elv.position == 2:	pi.write(elv.second, 1)	# set floor LED
elif elv.position == 3:	pi.write(elv.third, 1)	# set floor LED
elif elv.position == 4:	pi.write(elv.fourth, 1)	# set floor LED
else:
	logging.info("ELV_RPI: Cabin position not within proper range")


# ------------------------------------------------------------------------
# 										Message queueing routines
# ------------------------------------------------------------------------

ELV_continue = True

# ------------------------------------------------------------------------
# The callback for when the client receives a CONNACK response from the server.
# ------------------------------------------------------------------------
def on_connect(client, userdata, flags, rc):
	print "ELV_RPI: Connected to msg queue with result code "+str(rc)
	
	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe("elevator/commands", qos=2)

# ------------------------------------------------------------------------
# The callback for when a PUBLISH message is received from the server.
# ------------------------------------------------------------------------
def on_publish(client, userdata, mid):
	pass

# ------------------------------------------------------------------------
# The callback for when a message is received from the server.
# ------------------------------------------------------------------------
def on_message(client, userdata, msg):
	global ELV_continue
	global elv

	reply = msg.payload						# command received
	reply = reply.upper()					# make upper case
	
	if reply <> "":							# if line entered
		if reply.find("\n") > -1:
			reply = reply[0:reply.find("\n")]	# strip newline when present

	if reply == "":	pass					# skip empty lines
	
	elif reply == "QUIT" or reply == "Q":	# End of program
		print "ELV_RPI: End of program"
		ELV_continue = False
	
	elif reply == "UP" or reply == "U":		elv.go_up()

	elif reply == "DOWN" or reply == "D":	elv.go_down()

	elif reply == "STOP" or reply == "S":	elv.stop()

	elif reply == "POP" or reply == "P":	# pop one que entry
		temp = elv.next_request()
		print "one entry: |"+str(temp[0])+"-"+str(temp[1])+"| popped from queue"
		show_status()
	
	elif reply == "?":						show_status()
	
	elif reply.isdigit():					# do we have a number?
		f = int(reply)						# convert to int
		if f > 0 and f <=4:					# is it a valid floor?
			elv.set_destination(f)			# make cab go there
		else:
			logging.warning("ELV_RPI: Invalid command, type help")
	
	elif reply.find("-") > -1:				# if we have a request in the
		elv.push_request(reply)				#	form "X-Y" then queue it
	
	elif reply == "HELP" or reply == "H":	explain()
	
	else:
		logging.warning("ELV_RPI: Invalid command, type help")


# ------------------------------------------------------------------------
# Initialise message Queue client to read new requests
# ------------------------------------------------------------------------
client = mqtt.Client(client_id="ELV_RPI", clean_session=False)
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

# Call that processes network traffic, dispatches callbacks and
# handles reconnecting.
client.loop_start()


# ------------------------------------------------------------------------
# 											Start main loop
# ------------------------------------------------------------------------
while ELV_continue:

	# --------------------------------------------------------------------
	# Handle requests from queue, if any
	# --------------------------------------------------------------------
	if 	elv.cab_moving == False:					# cab stopped?
	
		if from_floor == -1 and to_floor == -1:		#  no request running
		
			if elv.que_empty():						# queue empty?
				time_now = time.time()
													# Queue empty for longer
													# 	than 30 seconds?
													# Then push request to 
													#	go to 1st floor
				if (time_now - last_time_action) > 30:
					if elv.position <> 1:
						logging.info("ELV_RPI: No requests for 30 seconds,")
						logging.info("ELV_RPI: 	returning to first floor")
						elv.push_request(str(elv.position)+"-"+str(1))
					
					last_time_action = time_now
				
			else:									# something left in queue
				current_request = elv.next_request()	# get next request
				from_floor = current_request[0]		# Extract from
				to_floor = current_request[1]		#   and to floor
				
				logging.info("ELV_RPI: Handling request from (" + \
					str(from_floor) + ") to (" + str(to_floor) + ")")
				
				logging.info("ELV_RPI: Setting for from_floor (" + \
				str(from_floor)+")")
				elv.set_destination(from_floor)		# go to from floor
				
		else:										# Request is running
			
			if from_floor > -1:						# from floor not done?
				if elv.position == from_floor:		# r we there already?
					from_floor = -1					#  indicate done
					logging.info("ELV_RPI: Reached from_floor ("+str(elv.position)+")")
					time.sleep(2)
					
					logging.info("ELV_RPI: Setting for to_floor ("+str(to_floor)+")")
					elv.set_destination(to_floor)	# go to next floor
					
			if to_floor > -1:						# to floor not done?
				if elv.position == to_floor:		# there already?
					to_floor = -1					#  indicate done
					logging.info("ELV_RPI: Reached to_floor ("+str(elv.position)+")")
					time.sleep(2)
	
	time.sleep(1)						# sample request queue per second


# ------------------------------------------------------------------------
# End program
# ------------------------------------------------------------------------

print " "
print "-----=====##### End elevator program #####=====-----"
print " "

exit()
