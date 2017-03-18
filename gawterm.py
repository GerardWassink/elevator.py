
# ------------------------------------------------------------------------
# Program		:	gawterm.py
# Author		:	Gerard Wassink
# Date			:	March 17, 2017
#
# Function		:	supply a terminal window with panes for remote control
#					of my elevator, can also be used for other contraptions
#
# History		:	20170317 - original version
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
#				Copyright (C) 2017 Gerard Wassink
# ------------------------------------------------------------------------

# ------------------------------------------------------------------------
# Libraries used
# ------------------------------------------------------------------------

import curses
import curses.textpad
import os

class term():
	
	"""
	Screen layout:
	+--- staFrame -----------------++--- msgFrame -----------------+
	|stawin                        ||msgwin                        |
	|                              ||                              |
	|                              ||                              |
	|                              ||                              |
	|                              ||                              |
	|                              ||                              |
	+--- cmdFrame -----------------+|                              |
	|cmdwin                        ||                              |
	|                              ||                              |
	|                              ||                              |
	|                              ||                              |
	|                              ||                              |
	+------------------------------++------------------------------+
	+--- inpFrame -------------------------------------------------+
	|> inpwin                                                      |
	+--------------------------------------------------------------+

	"""

	def __init__(self):
		# ----------------------------------------------------------
		# Get terminal size from system
		# ----------------------------------------------------------
		self.termHeight, self.termWidth = \
			os.popen('stty size', 'r').read().split()
		self.termWidth = int(self.termWidth)
		self.termHeight = int(self.termHeight)

		# ----------------------------------------------------------
		# Calculate various sizes for windows
		# ----------------------------------------------------------
		self.colWidth = (self.termWidth - 4) / 2
		self.colHeight = (self.termHeight - 5)
		self.staHeight = 5
		self.cmdHeight = self.colHeight - self.staHeight - 2

		# ----------------------------------------------------------
		# Initialize curses
		# ----------------------------------------------------------
		stdscr = curses.initscr()
		curses.noecho()
		
		# ----------------------------------------------------------
		# Create frame for status window
		# ----------------------------------------------------------
		self.staFrame = curses.newwin(self.staHeight+2, self.colWidth+2, 0, 0)
		self.staFrame.border()
		self.staFrame.move(0, 5)
		self.staFrame.addstr(" Status Window ")
		self.staFrame.refresh()
		# ----------------------------------------------------------
		# Create status window
		# ----------------------------------------------------------
		self.stawin = curses.newwin(self.staHeight, self.colWidth, 1, 1)
		
		
		# ----------------------------------------------------------
		# Create frame for command window
		# ----------------------------------------------------------
		self.cmdFrame = curses.newwin(self.cmdHeight+2, \
									self.colWidth+2, \
									self.staHeight+2, 0)
		self.cmdFrame.border()
		self.cmdFrame.move(0, 5)
		self.cmdFrame.addstr(" Command Window ")
		self.cmdFrame.refresh()
		# ----------------------------------------------------------
		# Create command window
		# ----------------------------------------------------------
		self.cmdwin = curses.newwin(self.colHeight-(self.staHeight+2), self.colWidth, \
									self.staHeight+3, 1)
		
		
		# ----------------------------------------------------------
		# Create frame for message window
		# ----------------------------------------------------------
		self.msgFrame = curses.newwin(self.colHeight+2, self.colWidth+2, \
										0, self.colWidth+2)
		self.msgFrame.border()
		self.msgFrame.move(0, 5)
		self.msgFrame.addstr(" Message Window ")
		self.msgFrame.refresh()

		# ----------------------------------------------------------
		# Create message window
		# ----------------------------------------------------------
		self.msgwin = curses.newwin(self.colHeight, self.colWidth, \
										1, self.colWidth+3)
		
		# ----------------------------------------------------------
		# Create frame for input window
		# ----------------------------------------------------------
		self.inpFrame = curses.newwin(3, 2*(self.colWidth+2), \
										self.colHeight+2, 0)
		self.inpFrame.border()
		self.inpFrame.move(0, 5)
		self.inpFrame.addstr(" Input: ")
		self.inpFrame.move(1, 1)
		self.inpFrame.addstr("> ")
		self.inpFrame.refresh()

		# ----------------------------------------------------------
		# Create input window
		# ----------------------------------------------------------
		self.inpwin = curses.newwin(1, 2*(self.colWidth), self.colHeight+3, 3)
		self.inpwin.refresh()
		
		# ----------------------------------------------------------
		# Create input Textbox
		# ----------------------------------------------------------
		self.inpbox = curses.textpad.Textbox(self.inpwin, insert_mode=True)
		
		
	def inpRead(self):
		self.inpwin.clear()
		self.inpwin.move(0, 0)
		self.inpbox.edit()
		self.txt = self.inpbox.gather().strip()
		return self.txt
		
	def staPrint(self, text):
		self.stawin.move(0,0)
		self.stawin.deleteln()
		try:
			self.stawin.addstr(self.staHeight-1, 0, text)
		except curses.error:
			pass
		self.stawin.refresh()
		
	def staClear(self):
		self.stawin.clear()
		self.stawin.refresh()
		
	def cmdPrint(self, text):
		self.cmdwin.move(0,0)
		self.cmdwin.deleteln()
		try:
			self.cmdwin.addstr(self.cmdHeight-1, 0, text)
		except curses.error:
			pass
		self.cmdwin.refresh()
		
	def cmdClear(self):
		self.cmdwin.clear()
		self.cmdwin.refresh()
		
	def msgPrint(self, text):
		self.msgwin.move(0,0)
		self.msgwin.deleteln()
		try:
			self.msgwin.addstr(self.colHeight-1, 0, text)
		except curses.error:
			pass
		self.msgwin.refresh()
		
	def msgClear(self):
		self.msgwin.clear()
		self.msgwin.refresh()
		
	def Close(self):
		curses.echo()
		curses.endwin()


