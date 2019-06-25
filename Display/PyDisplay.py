# -*- coding: utf-8 -*-
#
#
#  https://github.com/jshiatt
#
#

import sys
import os
import platform
import signal
import datetime
import time
import json
import locale
import random

from PyQt4 import QtGui, QtCore, QtNetwork
from PyQt4.QtGui import QPixmap, QBrush, QColor
from PyQt4.QtGui import QPainter, QImage, QFont
from PyQt4.QtCore import QUrl
from PyQt4.QtCore import Qt
from PyQt4.QtNetwork import QNetworkReply
from PyQt4.QtNetwork import QNetworkRequest
from subprocess import Popen

import re
import ApiKeys
import TempScan


def tick():
	global clockface, clockrect, lasttimestr, outdoor
	global indoor, events, Alarms
	Alarms.setText(events.listText)
	indoor.setText("Inside")
	outdoor.setText("Outside")
	bottomtext = "Waiting..."
	#bottom.setText(bottomtext)
	if Config.DateLocale != "":
		try:
			locale.setlocale(locale.LC_TIME, Config.DateLocale)
		except:
			pass
	
	now = datetime.datetime.now()
	if Config.digital:
		timestr = Config.digitalformat.format(now)
		if timestr[0] == '0':
			timestr = timestr[1:99]
	if lasttimestr != timestr:
		clockface.setText(timestr.lower())
	lasttimestr = timestr

def wxfinished():
	global wxreply, wxdata, temper
	wxstr = str(wxreply.readAll())
	wxdata = json.loads(wxstr)
	f = wxdata['currently']
	temper.setText('%.0f' % (f['temperature']) + u'°F')

#def indoorFinished():
#	global tempdata, indoortemp

def getindoor():
	global tempdata, indoortemp
	serialNum = TempScan.sensor()
	tempdata = TempScan.read(serialNum)
	indoortemp.setText('%.0f' % tempdata + u'°F')

def getwx():
	global wxurl
	global wxreply
	wxurl = 'https://api.darksky.net/forecast/' + ApiKeys.dsky + '/'
	wxurl += str(Config.lat) + ',' + str(Config.lon)
	wxurl += '?units=us&lang=en'
	wxurl += '&r=' + str(random.random())
	r = QUrl(wxurl)
	r = QNetworkRequest(r)
	wxreply = manager.get(r)
	wxreply.finished.connect(wxfinished)

def buttonClick():
	global events
	#bottom.setText("Button Pushed")
	timeinfo = timebox.text()
	data = timeinfo.split()
	events.insert(textbox.text(), data[0], data[1].upper())
	textbox.setText("")
	timebox.setText("")

def qtstart():

	getwx()
	getindoor()

	global ctimer, wxtimer, indoortimer
	ctimer = QtCore.QTimer()
	ctimer.timeout.connect(tick)
	ctimer.start(1000)

	wxtimer = QtCore.QTimer()
	wxtimer.timeout.connect(getwx)
	wxtimer.start(1000 * Config.refresh * 60 + random.uniform(1000, 10000))

	indoortimer = QtCore.QTimer()
	indoortimer.timeout.connect(getindoor)
	indoortimer.start(30000)

def fullquit():
	QtGui.QApplication.exit(0)

class event:
	def __init__(self, val, time, ampm):
		self.val = val
		self.time = time
		self.ampm = ampm
		self.next = None

class eventList:

	def __init__(self):
		self.listText = ""
		self.head = None
		self.size = 0

	def insert(self, val, time, ampm):
		if len(str(val)) > 32 or val == None:
			print "string failure"
			return
		r = re.compile('.{2}:.{2} .{2}')
		if time == None or r.match(time) is None:
			print "time failure"
			return
		else:
			print time + " matches format"
			if time[0] == '0':
				time = time[1:8]
			print time
		node = event(val, time, ampm)
		if not node == None:
			if self.head == None:
				self.head = node
				self.size += 1
			else:
				a = self.head
				b = a.next
				if (node.ampm == "AM" and a.ampm == "PM"): #or (#check times
					return

	def remove(self):
		if self.head == None:
			return
		else:
			node = self.head
			node2 = node.next
			self.head = node2
			self.size -= 1
			#return node

	def printEvents(self):
		i = 1
		string = ""
		node = self.head
		string += str(node.val)
		node = node.next
		while not i == self.size:
			string += "->"
			string += str(node.val)
			i += 1
			node = node.next
		print string

class mainGui(QtGui.QWidget):
	def keyPressEvent(self, event):
		global lastkeytime
		if isinstance(event, QtGui.QKeyEvent):
			if event.key() == Qt.Key_F4:
				fullquit();

#Testing event list
events = eventList()

configname = 'Config'

if len(sys.argv) > 1:
	configname = sys.argv[1]

if not os.path.isfile(configname + ".py"):
	print "Config file not found %s" % configname + ".py"
	exit(1)

Config = __import__(configname)
lasttimestr = ""

#Start building app
app = QtGui.QApplication(sys.argv)
desktop = app.desktop()
rec = desktop.screenGeometry()
height = rec.height()
width = rec.width()
xscale = float(width) / 1440.0
yscale = float(height) / 900.0

signal.signal(signal.SIGINT, fullquit)

w = mainGui()
w.setWindowTitle(os.path.basename(__file__))
w.setStyleSheet("QWidget { background-color: black;}")

frame1 = QtGui.QFrame(w)
frame1.setObjectName("frame1")
frame1.setGeometry(0, 0, width, height)
frame1.setStyleSheet("#frame1 { background-color: black;}")

foreGround = QtGui.QFrame(frame1)
foreGround.setObjectName("foreGround")
foreGround.setStyleSheet("#foreGround { background-color: " +
												"transparent; }")
foreGround.setGeometry(0, 0, width, height)

#Top Clock
if Config.digital:
	clockface = QtGui.QLabel(foreGround)
	clockface.setObjectName("clockface")
	clockrect = QtCore.QRect(
		width / 2 - height * .4,
		height * .45 - height * .4,
		height * .9,
		height * .2)
	clockface.setGeometry(clockrect)
	dcolor = QColor(Config.digitalcolor).darker(0).name()
	lcolor = QColor(Config.digitalcolor).lighter(120).name()
        clockface.setStyleSheet("#clockface { background-color: transparent; " +
												 "font-family: sans-serif; font-weight: light; color: " + 
												 lcolor + "; background-color: transparent; font-size: " + 
												 str(int(Config.digitalsize * xscale)) + "px; " +
												 Config.fontattr + "}")
	clockface.setAlignment(Qt.AlignCenter)
	clockface.setGeometry(clockrect)

#Event List
Alarms = QtGui.QLabel(foreGround)
Alarms.setObjectName("events")
Alarms.setStyleSheet("#events { font-family: sans-serif; color: " +
											Config.digitalcolor + "; background-color: white; " +
											"font-size: " + str(int(50 * xscale)) +
											"px; }")
Alarms.setAlignment(Qt.AlignCenter)
Alarms.setGeometry(width/2-450, 250, height, height-400)

#Bottom Text
#bottom = QtGui.QLabel(foreGround)
#bottom.setObjectName("test")
#bottom.setStyleSheet("#test { font-family: sans-serif; color: " +
#										Config.digitalcolor + "; background-color: transparent; " +
#										"font-size: " + str(int(Config.digitalsize * xscale)) +
#										"px; }")
#bottom.setAlignment(Qt.AlignCenter | Qt.AlignTop)
#bottom.setGeometry(0, height - 175, width, 175)

#Button Attempt
button = QtGui.QPushButton("Push me", foreGround)
button.setObjectName('button')
button.setStyleSheet("#button { background-color: white; }")
button.setGeometry(width/2 - 50, height - 50, 100, 50)
button.clicked.connect(buttonClick)

#Textbox
textbox = QtGui.QLineEdit(foreGround)
textbox.setObjectName('textbox')
textbox.setStyleSheet("#textbox { background-color: white; }")
textbox.setGeometry(width/2-150, height - 110, 300, 25)

timebox = QtGui.QLineEdit(foreGround)
timebox.setObjectName('timebox')
timebox.setStyleSheet("#timebox { background-color: white; }")
timebox.setGeometry(width/2-50, height-80, 100, 25)

#Outdoor temperature
temper = QtGui.QLabel(foreGround)
temper.setObjectName('outdoor')
temper.setStyleSheet("#outdoor { background-color: transparent; color: " +
										Config.digitalcolor + "; font-size: " + str(int(70 * xscale)) +
										"px; }")
temper.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
temper.setGeometry(50, height/2-15, 200, 200)

outdoor = QtGui.QLabel(foreGround)
outdoor.setObjectName('outdoortemp')
outdoor.setStyleSheet("#outdoortemp { background-color: transparent; color: " +
										 Config.digitalcolor + "; font-size: " + str(int(70 * xscale))+
										 "px; }")
outdoor.setAlignment(Qt.AlignCenter)
outdoor.setGeometry(0, height/2-120, 300, 130)

#Indoor temperature
indoortemp = QtGui.QLabel(foreGround)
indoortemp.setObjectName('indoor')
indoortemp.setStyleSheet("#indoor { background-color: transparent; color: " +
												Config.digitalcolor + "; font-size: " + str(int(70 * xscale)) +
												"px; }")
indoortemp.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
indoortemp.setGeometry(width-220, height/2-15, 200, 200)

indoor = QtGui.QLabel(foreGround)
indoor.setObjectName('indoortext')
indoor.setStyleSheet("#indoortext { background-color: transparent; color: " +
										Config.digitalcolor + "; font-size: " + str(int(70 * xscale)) +
										"px; }")
indoor.setAlignment(Qt.AlignCenter)
indoor.setGeometry(width-275, height/2-120, 300, 130)

manager = QtNetwork.QNetworkAccessManager()
stimer = QtCore.QTimer()
stimer.singleShot(10, qtstart)
w.show()
w.showFullScreen()
sys.exit(app.exec_())
