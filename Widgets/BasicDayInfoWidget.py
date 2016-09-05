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

class basicDayInfoWidget(QtGui.QWidget):

    def __init__(self):

        super(basicDayInfoWidget, self).__init__()

        self.initUI()

    def initUI(self):

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor(43,43,43))
        self.setPalette(p)

        self.vbox = QtGui.QVBoxLayout()

        self.label = QtGui.QLabel(datetime.datetime.strftime(datetime.datetime.now(),'%A, %B %d'))
        p = self.label.palette()
        p.setColor(self.label.foregroundRole(), QtCore.Qt.white)
        self.label.setPalette(p)

        self.clock = QtGui.QLCDNumber(8)

        self.vbox.addWidget(self.label)
        self.vbox.addWidget(self.clock)

        self.setLayout(self.vbox)

        ctimer = QtCore.QTimer(self)
        ctimer.timeout.connect(self.tick)
        ctimer.start(1000)

        palette = self.clock.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(255, 255, 255))
        palette.setColor(palette.Light, QtGui.QColor(0, 0, 0))
        palette.setColor(palette.Dark, QtGui.QColor(0, 0, 0))
        self.clock.setPalette(palette)

    def tick(self):
        time = datetime.datetime.now()
        text = datetime.datetime.strftime(time,'%I:%M:%S')
        self.clock.display(text)
        self.label.setText(datetime.datetime.strftime(datetime.datetime.now(),'%A, %B %d'))

    def resizeEvent(self, e):

        fontsize = 1

        font = self.label.font()

        while(True):
                

                f = QtGui.QFont(font)
                f.setPixelSize(fontsize)
                r = QtGui.QFontMetrics(f).boundingRect(self.label.text())
                if (r.height() < self.height()-30 and r.width() < self.width()-30):
                        fontsize += 1
                else:
                        break

        font.setPixelSize(fontsize)
        self.label.setFont(font)
