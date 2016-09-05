from __future__ import print_function
import httplib2
import os, sys, signal

from PyQt4 import QtGui, QtCore, QtNetwork
from PyQt4.QtGui import QPixmap, QMovie, QBrush, QColor, QPainter
from PyQt4.QtCore import Qt, QByteArray, QUrl, QFile, QIODevice, QString, QRect
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply, QNetworkProxy
from subprocess import Popen

import datetime, time
import dateutil.parser

import urllib2
import json
import math
import random

import googlemaps

class drivetimeWidget(QtGui.QWidget):

    def __init__(self, origin, destinations, config):

        self.Config = config
        self.origin = origin
        self.destinations = destinations

        super(drivetimeWidget,self).__init__()

        self.initUI()

    def initUI(self):

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor(43,43,43))
        self.setPalette(p)

        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)

        self.fillTimes()
        
        self.stimer = QtCore.QTimer()
        self.stimer.timeout.connect(self.fillTimes)
        self.stimer.start(1000*self.Config.traffic_refresh*60)

    def fillTimes(self):

        print('Pulling new drive times at' + str(datetime.datetime.now()))

        self.clearLayout(self.vbox)

        gmaps = googlemaps.Client(key=self.Config.directionsapi)
        
        for dest in self.destinations:

                now = datetime.datetime.now()
                directions_result = gmaps.directions(self.origin, self.destinations[dest], mode="driving",departure_time=now,alternatives=True)

                lab = QtGui.QLabel("Time to " + dest + " via ")
                lab.setObjectName("lab")
                lab.setStyleSheet("#lab { background-color: transparent; color: white; font-size: "+str(int(20))+"px;}")
                self.vbox.addWidget(lab)

                for route in directions_result:
                        lab = QtGui.QLabel("    " + route['summary'] + ": " + route['legs'][0]['duration_in_traffic']['text'])
                        lab.setObjectName("lab")
                        lab.setStyleSheet("#lab { background-color: transparent; color: white; font-size: "+str(int(14))+"px;}")
                        self.vbox.addWidget(lab)
                        self.vbox.addWidget(lab)

    def clearLayout(self,layout):
        while layout.count():
            child = layout.takeAt(0)
            child.widget().deleteLater()
