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

import ApiKeys


def tick():
	global clockface, clockrect, lasttimestr, bottom
	bottomtext = "Waiting..."
	bottom.setText(bottomtext)
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

def buttonClick():
	#bottom.setText("Button Pushed")
  bottom.setText(textbox.text())

def qtstart():
	global ctimer
	ctimer = QtCore.QTimer()
	ctimer.timeout.connect(tick)
	ctimer.start(1000)

def fullquit():
	QtGui.QApplication.exit(0)

class mainGui(QtGui.QWidget):
	def keyPressEvent(self, event):
		global lastkeytime
		if isinstance(event, QtGui.QKeyEvent):
			if event.key() == Qt.Key_F4:
				fullquit();

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

#Bottom Text
bottom = QtGui.QLabel(foreGround)
bottom.setObjectName("test")
bottom.setStyleSheet("#test { font-family: sans-serif; color: " +
										Config.digitalcolor + "; background-color: transparent; " +
										"font-size: " + str(int(Config.digitalsize * xscale)) +
										"px; }")
bottom.setAlignment(Qt.AlignCenter | Qt.AlignTop)
bottom.setGeometry(0, height - 175, width, 175)

#Button Attempt
button = QtGui.QPushButton("Push me", foreGround)
button.setObjectName('button')
button.setStyleSheet("#button { background-color: white; }")
button.setGeometry(width/2 - 50, height/2 - 25, 100, 50)
button.clicked.connect(buttonClick)

#Textbox
textbox = QtGui.QLineEdit(foreGround)
textbox.setObjectName('textbox')
textbox.setStyleSheet("#textbox { background-color: white; }")
textbox.setGeometry(width/2-80, height/2-55, 160, 25)

manager = QtNetwork.QNetworkAccessManager()
stimer = QtCore.QTimer()
stimer.singleShot(10, qtstart)
w.show()
w.showFullScreen()
sys.exit(app.exec_())
