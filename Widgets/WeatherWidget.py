# -*- coding: cp1252 -*-
from __future__ import print_function
import signal

from PyQt4 import QtGui, QtCore, QtNetwork
from PyQt4.QtGui import QPixmap, QMovie, QBrush, QColor, QPainter
from PyQt4.QtCore import Qt, QByteArray, QUrl, QFile, QIODevice, QString, QRect
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply, QNetworkProxy
from subprocess import Popen

import datetime, time
import urllib2
import json
import random

from GoogleMercatorProjection import LatLng, Point, getCorners

class Radar(QtGui.QLabel):

    def __init__(self, parent, radar, rect, myname, config):
              
        self.Config = config

        self.manager = QtNetwork.QNetworkAccessManager()
        self.lastapiget = time.time()
        
        global xscale, yscale
        self.myname = myname
        self.rect = rect
        self.satellite = self.Config.satellite
        try: 
            if radar["satellite"]:
                self.satellite = 1
        except KeyError:
            pass
        self.baseurl = self.mapurl(radar, rect, False)
        #print "google map base url: "+self.baseurl
        self.wxurl = self.radarurl(radar, rect)
        #print "radar url: "+self.wxurl
        QtGui.QLabel.__init__(self, parent)
        self.interval = self.Config.radar_refresh*60
        self.lastwx = 0
        
        self.setObjectName("radar")
        self.setGeometry(rect)
        self.setStyleSheet("#radar { background-color: transparent; }")    
        self.setAlignment(Qt.AlignCenter)

        self.wwx = QtGui.QLabel(self)
        self.wwx.setObjectName("wx")
        self.wwx.setStyleSheet("#wx { background-color: transparent; }")
        self.setAlignment(Qt.AlignCenter)
        self.wwx.setGeometry(0, 0, rect.width(), rect.height())

        self.wxmovie = QMovie()

    def mapurl(self, radar,rect,markersonly):
        #'https://maps.googleapis.com/maps/api/staticmap?maptype=hybrid&center='+rcenter.lat+','+rcenter.lng+'&zoom='+rzoom+'&size=300x275'+markersr;
        urlp = [];
        
        if len(self.Config.googleapi) > 0: urlp.append('key='+self.Config.googleapi)
        urlp.append('center='+str(radar['center'].lat)+','+str(radar['center'].lng))
        zoom = radar['zoom']
        rsize = rect.size()
        if rsize.width() > 640 or rsize.height() > 640:
            rsize = QtCore.QSize(rsize.width()/2,rsize.height()/2)
            zoom -= 1
        urlp.append('zoom='+str(zoom))
        urlp.append('size='+str(rsize.width())+'x'+str(rsize.height()))
        if markersonly:
            urlp.append('style=visibility:off') 
        else:
            urlp.append('maptype=hybrid')
        for marker in radar['markers']:
            marks = []
            for opts in marker:
                if opts != 'location':
                    marks.append(opts + ':' + marker[opts])
            marks.append(str(marker['location'].lat)+','+str(marker['location'].lng))
            urlp.append('markers='+'|'.join(marks))

        print(urlp)
        
        return 'http://maps.googleapis.com/maps/api/staticmap?'+'&'.join(urlp)


    def radarurl(self,radar,rect):
        #wuprefix = 'http://api.wunderground.com/api/';
        #wuprefix+wuapi+'/animatedradar/image.gif?maxlat='+rNE.lat+'&maxlon='+rNE.lng+'&minlat='+rSW.lat+'&minlon='+rSW.lng+wuoptionsr;
        #wuoptionsr = '&width=300&height=275&newmaps=0&reproj.automerc=1&num=5&delay=25&timelabel=1&timelabel.y=10&rainsnow=1&smooth=1';
        rr = getCorners(radar['center'],radar['zoom'],rect.width(),rect.height())
        if self.satellite:
            return (self.Config.wuprefix+self.Config.wuapi+'/animatedsatellite/lang:'+self.Config.wuLanguage+'/image.gif'+
                '?maxlat='+str(rr['N'])+
                '&maxlon='+str(rr['E'])+
                '&minlat='+str(rr['S'])+
                '&minlon='+str(rr['W'])+
                '&width='+str(rect.width())+
                '&height='+str(rect.height())+
                '&newmaps=0&reproj.automerc=1&num=5&delay=25&timelabel=1&timelabel.y=10&smooth=1&key=sat_ir4_bottom'
                )
        else:
            return (self.Config.wuprefix+self.Config.wuapi+'/animatedradar/lang:'+self.Config.wuLanguage+'/image.gif'+
                '?maxlat='+str(rr['N'])+
                '&maxlon='+str(rr['E'])+
                '&minlat='+str(rr['S'])+
                '&minlon='+str(rr['W'])+
                '&width='+str(rect.width())+
                '&height='+str(rect.height())+
                '&newmaps=0&reproj.automerc=1&num=5&delay=25&timelabel=1&timelabel.y=10&rainsnow=1&smooth=1&radar_bitmap=1&xnoclutter=1&xnoclutter_mask=1&cors=1'
                )
            
    
    def basefinished(self):
        if self.basereply.error() != QNetworkReply.NoError: return
        self.basepixmap = QPixmap()
        self.basepixmap.loadFromData(self.basereply.readAll())
        if self.basepixmap.size() != self.rect.size():
            self.basepixmap = self.basepixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        if self.satellite:
            p = QPixmap(self.basepixmap.size())
            p.fill(Qt.transparent)
            painter = QPainter()
            painter.begin(p)
            painter.setOpacity(0.6)
            painter.drawPixmap(0,0,self.basepixmap)
            painter.end()
            self.basepixmap = p
            self.wwx.setPixmap(self.basepixmap)
        else:
            self.setPixmap(self.basepixmap)

    def wxfinished(self):
        if self.wxreply.error() != QNetworkReply.NoError:
            #print "get radar error "+self.myname+":"+str(self.wxreply.error())
            self.lastwx = 0
            return
        #print "radar map received:"+self.myname+":"+time.ctime()
        self.wxmovie.stop()
        self.wxdata = QtCore.QByteArray(self.wxreply.readAll())
        self.wxbuff = QtCore.QBuffer(self.wxdata)
        self.wxbuff.open(QtCore.QIODevice.ReadOnly)
        mov = QMovie(self.wxbuff, 'GIF')
        #print "radar map frame count:"+self.myname+":"+str(mov.frameCount())
        if mov.frameCount() > 2:
            self.lastwx = time.time()
        else:
            # radar image retreval failed
            self.lastwx = 0
            # retry in 5 seconds
            QtCore.QTimer.singleShot(5*1000, self.getwx)
            return
        self.wxmovie = mov
        if self.satellite:
            self.setMovie( self.wxmovie)
        else:
            self.wwx.setMovie( self.wxmovie)
        if self.parent().isVisible():
            self.wxmovie.start()

    def getwx(self):
        i = 0.1
        # making sure there is at least 2 seconds between radar api calls
        self.lastapiget += 2
        if time.time() > self.lastapiget: self.lastapiget = time.time()
        else: i = self.lastapiget - time.time()
        #print "get radar api call spacing oneshot get i="+str(i)
        QtCore.QTimer.singleShot(i*1000, self.getwx2)

    def getwx2(self):
        try:
            if self.wxreply.isRunning(): return
        except Exception:
            pass
        #print "getting radar map "+self.myname+":"+time.ctime()
        self.wxreq = QNetworkRequest(QUrl(self.wxurl+'&rrrand='+str(time.time())))
        self.wxreply = self.manager.get(self.wxreq)
        QtCore.QObject.connect(self.wxreply, QtCore.SIGNAL("finished()"),self.wxfinished)

    def getbase(self):
        self.basereq = QNetworkRequest(QUrl(self.baseurl))
        self.basereply = self.manager.get(self.basereq)
        QtCore.QObject.connect(self.basereply,QtCore.SIGNAL("finished()"),self.basefinished)
        
    def start(self, interval=0):
        if interval > 0: self.interval = interval
        self.getbase()
        self.timer = QtCore.QTimer()
        QtCore.QObject.connect(self.timer,QtCore.SIGNAL("timeout()"), self.getwx)
       
    def wxstart(self):
        #print "wxstart for "+self.myname
        if (self.lastwx == 0 or (self.lastwx+self.interval) < time.time()): self.getwx()
        # random 1 to 10 seconds added to refresh interval to spread the queries over time
        i = (self.interval+random.uniform(1,10))*1000
        self.timer.start(i)
        self.wxmovie.start()
        QtCore.QTimer.singleShot(1000, self.wxmovie.start)
        
    def wxstop(self):
        #print "wxstop for "+self.myname
        self.timer.stop()
        self.wxmovie.stop()
        
    def stop(self):
        try:
            self.timer.stop()
            self.timer = None
            if self.wxmovie: self.wxmovie.stop()
        except Exception:
            pass

class weatherWidget(QtGui.QWidget):

    def __init__(self,config):

        self.Config = config

        super(weatherWidget, self).__init__()

        self.manager = QtNetwork.QNetworkAccessManager()
  
        stimer = QtCore.QTimer()
        stimer.singleShot(2000, self.qtstart)

    def initUI(self):

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor(43,43,43))
        self.setPalette(p)

        self.frame1 = QtGui.QFrame()
        self.frame1.setObjectName("frame1")
        #self.frame1.setGeometry(0,0,300,900)

        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)

        print(self.width())

        radarHeight = (self.height() - 400)/2

        self.radar1rect = QtCore.QRect(3, 344, self.width(), radarHeight)
        self.objradar1 = Radar(self.frame1, self.Config.radar1, self.radar1rect, "radar1", self.Config)

        self.radar2rect = QtCore.QRect(3, 622, self.width(), radarHeight)
        self.objradar2 = Radar(self.frame1, self.Config.radar2, self.radar2rect, "radar2", self.Config)

        self.temper = QtGui.QLabel(self.frame1)
        self.temper.setObjectName("temper")
        self.temper.setStyleSheet("#temper { background-color: transparent; color: "+self.Config.textcolor+"; font-size: "+str(int(70))+"px; "+self.Config.fontattr+"}")
        self.temper.setAlignment(Qt.AlignHCenter | Qt.AlignTop);

        self.vbox.addWidget(self.temper)

        self.wind2 = QtGui.QLabel(self.frame1)
        self.wind2.setObjectName("wind2")
        self.wind2.setStyleSheet("#wind2 { background-color: transparent; color: "+self.Config.textcolor+"; font-size: "+str(int(20))+"px; "+self.Config.fontattr+"}")
        self.wind2.setAlignment(Qt.AlignHCenter | Qt.AlignTop);

        self.vbox.addWidget(self.wind2)
        
        self.wind = QtGui.QLabel(self.frame1)
        self.wind.setObjectName("wind")
        self.wind.setStyleSheet("#wind { background-color: transparent; color: "+self.Config.textcolor+"; font-size: "+str(int(20))+"px; "+self.Config.fontattr+"}")
        self.wind.setAlignment(Qt.AlignHCenter | Qt.AlignTop);

        self.vbox.addWidget(self.wind)

        self.todayHead = QtGui.QLabel(self.frame1)
        self.todayHead.setObjectName("todayHead")
        self.todayHead.setStyleSheet("#todayHead { background-color: transparent; color: "+self.Config.textcolor+"; font-size: "+str(int(50))+"px; "+self.Config.fontattr+"}")
        self.todayHead.setAlignment(Qt.AlignHCenter | Qt.AlignTop);
        self.todayHead.setText('Today')

        self.vbox.addWidget(self.todayHead)

        self.todayForecast = QtGui.QLabel(self.frame1)
        self.todayForecast.setObjectName("todayForecast")
        self.todayForecast.setStyleSheet("#todayForecast { background-color: transparent; color: "+self.Config.textcolor+"; font-size: "+str(int(20))+"px; "+self.Config.fontattr+"}")
        self.todayForecast.setAlignment(Qt.AlignHCenter | Qt.AlignTop);

        self.vbox.addWidget(self.todayForecast)

        self.tomorrowHead = QtGui.QLabel(self.frame1)
        self.tomorrowHead.setObjectName("tomorrowHead")
        self.tomorrowHead.setStyleSheet("#tomorrowHead { background-color: transparent; color: "+self.Config.textcolor+"; font-size: "+str(int(50))+"px; "+self.Config.fontattr+"}")
        self.tomorrowHead.setAlignment(Qt.AlignHCenter | Qt.AlignTop);
        self.tomorrowHead.setText('Tomorrow')

        self.vbox.addWidget(self.tomorrowHead)

        self.tomorrowForecast = QtGui.QLabel(self.frame1)
        self.tomorrowForecast.setObjectName("tomorrowForecast")
        self.tomorrowForecast.setStyleSheet("#tomorrowForecast { background-color: transparent; color: "+self.Config.textcolor+"; font-size: "+str(int(20))+"px; "+self.Config.fontattr+"}")
        self.tomorrowForecast.setAlignment(Qt.AlignHCenter | Qt.AlignTop);

        self.vbox.addWidget(self.tomorrowForecast)

        self.vbox.addWidget(self.objradar1)
        self.vbox.addWidget(self.objradar2)

    def qtstart(self):

        self.initUI()

        self.getallwx()

        self.objradar1.start(self.Config.radar_refresh*60)
        self.objradar1.wxstart()
        self.objradar2.start(self.Config.radar_refresh*60)
        self.objradar2.wxstart()

        self.wxtimer = QtCore.QTimer()
        self.wxtimer.timeout.connect(self.getallwx)
        self.wxtimer.start(1000*self.Config.weather_refresh*60+random.uniform(1000,10000))

    def wxfinished(self):

        self.wxstr = str(self.wxreply.readAll())
        self.wxdata = json.loads(self.wxstr)
        f = self.wxdata['current_observation']

        if self.Config.metric:
                self.temper.setText(str(f['temp_c'])+u'°C')
                self.wd = f['wind_dir']
                if self.Config.wind_degrees: self.wd = str(f['wind_degrees'])+u'°'
                self.wind.setText(self.Config.LWind+self.wd+' '+str(f['wind_kph'])+self.Config.Lgusting+str(f['wind_gust_kph']))
                self.wind2.setText(self.Config.LFeelslike+str(f['feelslike_c']) )
        else:
                self.temper.setText(str(f['temp_f'])+u'°F')
                self.wd = f['wind_dir']
                if self.Config.wind_degrees: self.wd = str(f['wind_degrees'])+u'°'
                self.wind.setText(self.Config.LWind+self.wd+' '+str(f['wind_mph'])+self.Config.Lgusting+str(f['wind_gust_mph']))
                self.wind2.setText(self.Config.LFeelslike+str(f['feelslike_f']) )

        todayf = self.wxdata['forecast']['simpleforecast']['forecastday'][0]
        tommf = self.wxdata['forecast']['simpleforecast']['forecastday'][1]

        if self.Config.metric:
                todayHigh = str(todayf['high']['celsius'])+u'°C'
                todayLow = str(todayf['low']['celsius'])+u'°C'
                todayPop = str(todayf['pop'])
                tommHigh = str(tommf['high']['celsius'])+u'°C'
                tommLow = str(tommf['low']['celsius'])+u'°C'
                tommPop = str(tommf['pop'])
        else:
                todayHigh = str(todayf['high']['fahrenheit'])+u'°F'
                todayLow = str(todayf['low']['fahrenheit'])+u'°F'
                todayPop = str(todayf['pop'])
                tommHigh = str(tommf['high']['fahrenheit'])+u'°F'
                tommLow = str(tommf['low']['fahrenheit'])+u'°F'
                tommPop = str(tommf['pop'])

        self.todayForecast.setText('High:' + todayHigh + ' Low:' + todayLow + ' Rain:' + todayPop +'%')
        self.tomorrowForecast.setText('High:' + tommHigh + ' Low:' + tommLow + ' Rain:' + tommPop +'%')
       
        
    def getwx(self):
        self.wxurl = self.Config.wuprefix + self.Config.wuapi + '/conditions/astronomy/hourly10day/forecast10day/lang:'+self.Config.wuLanguage+'/q/' 
        self.wxurl += str(self.Config.wulocation.lat)+','+str(self.Config.wulocation.lng)+'.json' 
        self.wxurl += '?r=' + str(random.random())
        r = QUrl(self.wxurl)
        r = QNetworkRequest(r)
        self.wxreply = self.manager.get(r)
        self.wxreply.finished.connect(self.wxfinished)    

    def getallwx(self):
        self.getwx()

    def resizeBase(self):
        self.objradar1.basefinished()
        self.objradar2.basefinished()
