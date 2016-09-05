from __future__ import print_function
import httplib2
import os, sys, signal

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

from PyQt4 import QtGui, QtCore, QtNetwork
from PyQt4.QtGui import QPixmap, QMovie, QBrush, QColor, QPainter
from PyQt4.QtCore import Qt, QByteArray, QUrl, QFile, QIODevice, QString, QRect
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply, QNetworkProxy
from subprocess import Popen

from pynYNAB.Client import nYnabClient
from pynYNAB.connection import nYnabConnection
from pynYNAB.schema.budget import Payee, Transaction

import datetime, time
import dateutil.parser

import urllib2
import json
import math
import random

import googlemaps

from Widgets.GoogleMercatorProjection import LatLng, Point, getCorners

from Widgets.WeatherWidget import weatherWidget
from Widgets.DriveTimeWidget import drivetimeWidget
from Widgets.ynabWidget import ynabWidget
from Widgets.OneDayCalWidget import OneDayCalWidget
from Widgets.BasicDayInfoWidget import basicDayInfoWidget

try:
        import argparse
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
        flags = None

class Dashboard(QtGui.QWidget):

    def __init__(self):

        super(Dashboard, self).__init__()

        configname = 'Config'

        if len(sys.argv) > 1: 
            configname = sys.argv[1]

        if not os.path.isfile(configname+".py"):
            print ("Config file not found %s" % configname+".py")
            exit(1)
              
        self.Config = __import__(configname)

        self.initUI()

        self.cTimer = QtCore.QTimer()
        self.cTimer.timeout.connect(self.updateCals)
        self.cTimer.start(1000*self.Config.calendar_refresh*60)

    def initUI(self):

        self.setObjectName('dashboard')
        self.setStyleSheet('#dashboard { background-color: black;}')
        

        cal1Options = {}
        cal1Options['date'] = datetime.date.today()
        cal1Options['calendars']=self.Config.calList
        cal1Options['eventBoxColors']=self.Config.calColorList
        cal1Options['showCurrentTime']=True
        self.cal1 = OneDayCalWidget(cal1Options, self.Config)

        cal2Options = {}
        cal2Options['date'] = datetime.date.today() + datetime.timedelta(days=1)
        cal2Options['calendars']=self.Config.calList
        cal2Options['eventBoxColors']=self.Config.calColorList
        cal2Options['showCurrentTime']=False
        self.cal2 = OneDayCalWidget(cal2Options, self.Config)

        self.weather = weatherWidget(self.Config)

        self.basic = basicDayInfoWidget()

        self.dist = drivetimeWidget(self.Config.origin, self.Config.dest, self.Config)

        self.ynab = ynabWidget(self.Config) 

        hbox = QtGui.QHBoxLayout()
        self.setLayout(hbox)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.basic)
        vbox.addWidget(self.ynab)
        vbox.addWidget(self.dist)

        hbox.addWidget(self.weather)
        hbox.addLayout(vbox)
        hbox.addWidget(self.cal1)
        hbox.addWidget(self.cal2)

    def syncCalAxis(self):

        if self.cal1.hasEvents and self.cal2.hasEvents:
                if self.cal1.calStart < self.cal2.calStart:
                        earliestStart = self.cal1.calStart
                else:
                        earliestStart = self.cal2.calStart

                if self.cal1.calEnd > self.cal2.calEnd:
                        latestEnd = self.cal1.calEnd
                else:
                        latestEnd = self.cal2.calEnd

        elif self.cal1.hasEvents:
                earliestStart = self.cal1.calStart
                latestEnd = self.cal1.calEnd

        else:
                earliestStart = self.cal2.calStart
                latestEnd = self.cal2.calEnd

        if self.cal1.titleFontSize < self.cal2.titleFontSize:
                smallestFont = self.cal1.titleFontSize
        else:
                smallestFont = self.cal2.titleFontSize

        self.cal1.setCalStartEnd(earliestStart,latestEnd)
        self.cal2.setCalStartEnd(earliestStart,latestEnd)
        
        self.cal1.setTitleFontSize(smallestFont)
        self.cal2.setTitleFontSize(smallestFont)

    def resizeEvent(self, e):

        #self.weather.resizeBase()

        stimer = QtCore.QTimer()
        stimer.singleShot(500, self.syncCalAxis)

    def updateCals(self):

        print("Updating Calendars at " + str(datetime.datetime.now()))

        cal1Options = {}
        cal1Options['date'] = datetime.date.today()
        cal1Options['calendars']=self.Config.calList
        cal1Options['eventBoxColors']=self.Config.calColorList
        cal1Options['showCurrentTime']=True
        self.cal1.updateOptions(cal1Options, self.Config)

        cal2Options = {}
        cal2Options['date'] = datetime.date.today() + datetime.timedelta(days=1)
        cal2Options['calendars']=self.Config.calList
        cal2Options['eventBoxColors']=self.Config.calColorList
        cal2Options['showCurrentTime']=False
        self.cal2.updateOptions(cal2Options, self.Config)

        stimer = QtCore.QTimer()
        stimer.singleShot(500, self.syncCalAxis)

def main():
        global xscale, yscale        

        app = QtGui.QApplication(sys.argv)
        desktop = app.desktop()
        rec = desktop.screenGeometry()
        height = rec.height()
        width = rec.width()
        xscale = float(width)/1440.0
        yscale = float(height)/900.0

        dash = Dashboard()

        #dash.show()

        dash.showFullScreen()
        #dash.showMaximized()
        stimer = QtCore.QTimer()
        stimer.singleShot(1000, dash.syncCalAxis)
        

        sys.exit(app.exec_())

if __name__ == '__main__':
    main()
