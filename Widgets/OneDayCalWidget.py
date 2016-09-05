import os, sys, signal
import httplib2

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

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

class OneDayCalWidget(QtGui.QWidget):
    
    def __init__(self, calOptions, config):

        self.Config = config
        
        super(OneDayCalWidget, self).__init__()

        self.eventMasterList = self.getEventList(calOptions)
        self.colors = calOptions['eventBoxColors']
        self.showCurrentTime = calOptions['showCurrentTime']
        self.syncedTitleFontSize = None

        self.calcSpan()

        self.initUI()
        
    def initUI(self):

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor(43,43,43))
        self.setPalette(p)

        self.setMinimumSize(300,100)

    def calcSpan(self):

        p = dateutil.parser

        self.hasEventsCal = {}
        self.hasEvents = False

        for i, cal in enumerate(self.eventMasterList):
                if len(cal)>0:
                        self.lastWithEvents = i
                        self.hasEventsCal[i] = True
                        self.hasEvents = True
                else:
                        self.hasEventsCal[i] = False

        if self.hasEvents:

                tz = p.parse(self.eventMasterList[self.lastWithEvents][0]['end'].get('dateTime')).tzinfo

                self.calStart = datetime.time(hour=8, tzinfo=tz)
                self.calEnd = datetime.time(hour=17, tzinfo=tz)

                for j, cal in enumerate(self.eventMasterList):
                        if self.hasEventsCal[j]:
                                if p.parse(cal[0]['start'].get('dateTime')).timetz() < self.calStart:
                                        self.calStart = p.parse(cal[0]['start'].get('dateTime')).timetz()
                                if p.parse(cal[-1]['end'].get('dateTime')).timetz() > self.calEnd:
                                        self.calEnd = p.parse(cal[-1]['end'].get('dateTime')).timetz()

                self.calStart = self.calStart.replace(minute=0,second=0,microsecond=0)
                if self.calEnd.minute>0 or self.calEnd.second>0 or self.calEnd.microsecond>0:
                        self.calEnd = self.calEnd.replace(hour=self.calEnd.hour+1,minute=0,second=0,microsecond=0)

                self.calDate = p.parse(self.eventMasterList[self.lastWithEvents][0]['start'].get('dateTime')).date()
                self.dtCalStart = datetime.datetime.combine(self.calDate,self.calStart)
                self.dtCalEnd = datetime.datetime.combine(self.calDate,self.calEnd)

                self.calSpan = self.dtCalEnd - self.dtCalStart

                for cal in self.eventMasterList:
                        for event in cal:
                                event['relHeight']=event['timespan'].total_seconds()/self.calSpan.total_seconds()
                                event['relStart']=(p.parse(event['start'].get('dateTime'))-self.dtCalStart).total_seconds()/self.calSpan.total_seconds()

        else:

                tz = datetime.datetime.now().tzinfo
                self.calDate = calOptions['date']
                self.calStart = datetime.time(hour=8, tzinfo=tz)
                self.calEnd = datetime.time(hour=17, tzinfo=tz)
                self.dtCalStart = datetime.datetime.combine(self.calDate,self.calStart)
                self.dtCalEnd = datetime.datetime.combine(self.calDate,self.calEnd)
                self.calSpan = self.dtCalEnd - self.dtCalStart


    def paintEvent(self, e):

        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawCalendar(qp)
        qp.end()

    def drawCalendar(self, qp):

        self.drawLines(qp)

        if self.hasEvents:
                self.drawEvents(qp)

    def drawLines(self, qp):

        pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)

        self.defaultFontSize = qp.fontInfo().pixelSize()
        if(self.syncedTitleFontSize is None):
                fontsize = 1
                font = qp.font()
                while(True):

                        f = QtGui.QFont(font)
                        f.setPixelSize(fontsize)
                        r = QtGui.QFontMetrics(f).boundingRect(str(self.calDate.month)+'/'+str(self.calDate.day)+"/"+str(self.calDate.year))
                        if (r.height() < self.height()-30 and r.width() < self.width()-30):
                                fontsize += 1
                        else:
                                self.titleHeight = r.height()
                                break
                fontsize = fontsize/2
        else:
                fontsize = self.syncedTitleFontSize
                
        font = qp.font()
        f = QtGui.QFont(font)
        f.setPixelSize(fontsize)
        r = QtGui.QFontMetrics(f).boundingRect(str(self.calDate.month)+'/'+str(self.calDate.day)+"/"+str(self.calDate.year))
        self.titleHeight = r.height()
        self.titleWidth = r.width()

        self.titleFontSize = fontsize
        self.syncedTitleFontSize = None
        
        font.setPixelSize(fontsize)
        qp.setFont(font)

        qp.drawText((self.width()-self.titleWidth)/2, self.titleHeight, str(self.calDate.month)+'/'+str(self.calDate.day)+"/"+str(self.calDate.year))

        font.setPixelSize(self.defaultFontSize)
        qp.setFont(font)

        hours = self.calSpan.total_seconds()/3600
        for x in xrange(int(hours+1)):
                qp.drawLine(0, 25+self.titleHeight+(self.height()-50-self.titleHeight)/hours*x, self.width(), 25+self.titleHeight+(self.height()-50-self.titleHeight)/hours*x)
                qp.drawText(5, 40+self.titleHeight+(self.height()-50-self.titleHeight)/hours*x, (self.dtCalStart+datetime.timedelta(hours=x)).strftime('%I%p').lstrip("0").replace(" 0", " "))

        pen = QtGui.QPen(QtCore.Qt.blue, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)

        if self.showCurrentTime and self.dtCalStart < datetime.datetime.now(self.dtCalStart.tzinfo) and self.dtCalEnd > datetime.datetime.now(self.dtCalEnd.tzinfo):
                span = datetime.datetime.now(self.dtCalStart.tzinfo) - self.dtCalStart
                spanHours = span.total_seconds()/3600.0
                relHeight = spanHours/hours
                qp.drawLine(0, 50+(self.height()-50)*relHeight, self.width(), 50+(self.height()-50)*relHeight)
        
    def drawEvents(self, qp):

        pen = QtGui.QPen(QtCore.Qt.white, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)

        numOfCals = len(self.eventMasterList)
        eventWidth = int((self.width()-(60+numOfCals*10))/numOfCals)

        for counter, cal in enumerate(self.eventMasterList):
                qp.setBrush(self.colors[counter])
                for event in cal:
                        r = QtCore.QRect(60+counter*(eventWidth+10), 25+self.titleHeight+(self.height()-50-self.titleHeight)*event['relStart'], eventWidth, (self.height()-50-self.titleHeight)*event['relHeight'])
                        qp.drawRect(r)
                        qp.drawText(r.left()+5, r.top()+2, r.width()-5, r.height()-2, QtCore.Qt.TextWordWrap, event['summary'])

    def setCalStartEnd(self, start, end):

        p = dateutil.parser

        self.calStart = start
        self.calEnd = end
        self.dtCalStart = datetime.datetime.combine(self.calDate,self.calStart)
        self.dtCalEnd = datetime.datetime.combine(self.calDate,self.calEnd)
        self.calSpan = self.dtCalEnd - self.dtCalStart
        
        for cal in self.eventMasterList:
                for event in cal:
                        event['relHeight']=event['timespan'].total_seconds()/self.calSpan.total_seconds()
                        event['relStart']=(p.parse(event['start'].get('dateTime'))-self.dtCalStart).total_seconds()/self.calSpan.total_seconds()

        self.update()

    def setTitleFontSize(self, fontsize):

        self.syncedTitleFontSize = fontsize

        self.update()

    def getEventList(self, calOptions):

        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)

        millis = 1288483950000
        ts = millis * 1e-3
        # local time == (utc time + utc offset)
        utc_offset = datetime.datetime.fromtimestamp(ts) - datetime.datetime.utcfromtimestamp(ts)

        morning = (datetime.datetime.combine(calOptions['date'],datetime.time.min) - utc_offset).isoformat() + 'Z'
        night = (datetime.datetime.combine(calOptions['date'],datetime.time.max) - utc_offset).isoformat() + 'Z'

        retEvents = []

        for cal in calOptions['calendars']:

                eventsResult = service.events().list(
                        calendarId=cal, timeMin=morning, timeMax=night, singleEvents=True,
                        orderBy='startTime').execute()
                events = eventsResult.get('items', [])

                daysEvents = []

                p = dateutil.parser

                if not events:
                        print('No upcoming events found.')
                for event in events:
                        if 'transparency' not in event and 'date' not in event['start']:
                                event['timespan'] = p.parse(event['end'].get('dateTime')) - p.parse(event['start'].get('dateTime'))
                                daysEvents.append(event)

                daysEvents.sort(key=lambda event: event['start'].get('dateTime', event['start'].get('date')))

                retEvents.append(daysEvents)

        return retEvents
        

    def get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
                Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
                os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                                                   'calendar-python-quickstart.json')

        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
                flow = client.flow_from_clientsecrets(self.Config.CLIENT_SECRET_FILE, self.Config.SCOPES)
                flow.user_agent = self.Config.APPLICATION_NAME
                if flags:
                        credentials = tools.run_flow(flow, store, flags)
                else: # Needed only for compatibility with Python 2.6
                        credentials = tools.run(flow, store)
                print('Storing credentials to ' + credential_path)
        return credentials

    def updateOptions(self, calOptions, config):

        self.Config = config
        self.eventMasterList = self.getEventList(calOptions)
        self.colors = calOptions['eventBoxColors']
        self.showCurrentTime = calOptions['showCurrentTime']
        self.syncedTitleFontSize = None

        self.calcSpan()

        self.update()

        
