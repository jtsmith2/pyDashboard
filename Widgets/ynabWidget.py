from __future__ import print_function
import httplib2
import os, sys, signal

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

class ynabWidget(QtGui.QWidget):

    def __init__(self, config):

        super(ynabWidget,self).__init__()

        self.Config = config

        self.initUI()

    def initUI(self):

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor(43,43,43))
        self.setPalette(p)

        self.vbox = QtGui.QVBoxLayout()
        self.setLayout(self.vbox)

        self.getBudget()

        self.stimer = QtCore.QTimer()
        self.stimer.timeout.connect(self.updateBudget)
        self.stimer.start(1000*self.Config.ynab_refresh*60)

    def getBudget(self):

        self.connection = nYnabConnection(self.Config.ynabUser, self.Config.ynabPassword)
        self.client = nYnabClient(self.connection, self.Config.ynabBudgetName)

        self.fillBudget()

    def updateBudget(self):

        self.client.sync()

        self.fillBudget()

    def fillBudget(self):

        self.clearLayout(self.vbox)

        self.cats = {}
        self.subs = {}
        self.balances = {}

        #Creates hiarichy structure of category/subcategory and only those that have the keyword in YNAB subcategory notes section
        for cat in self.client.budget.be_master_categories:
                self.cats[cat.name]=cat
                self.subs[cat.name+'_subs'] = {}
                for subcat in self.client.budget.be_subcategories:
                        if subcat.note is not None:
                                if subcat.entities_master_category_id == cat.id and self.Config.ynabShowKeyword in subcat.note:
                                        self.subs[cat.name+'_subs'][subcat.name] = subcat
        
        #Gets current month budget calculations
        for b in self.client.budget.be_monthly_subcategory_budget_calculations:
                if b.entities_monthly_subcategory_budget_id[4:11]==(datetime.datetime.now().strftime('%Y-%m')):
                        self.balances[b.entities_monthly_subcategory_budget_id[12:]]=b
        
        #Displays the balance for each subcategory in the subs dict
        for cat in self.cats:
                if len(self.subs[cat+'_subs'])>0:
                        lab = QtGui.QLabel(cat)
                        lab.setObjectName("lab")
                        lab.setStyleSheet("#lab { background-color: transparent; color: white; font-size: "+str(int(20))+"px;}")
                        self.vbox.addWidget(lab)
                        for scat in self.subs[cat+"_subs"]:
                                lab = QtGui.QLabel("    "+ scat + ': ' + str(self.balances[self.subs[cat+"_subs"][scat].id].balance))
                                lab.setObjectName("lab")
                                lab.setStyleSheet("#lab { background-color: transparent; color: white; font-size: "+str(int(20))+"px;}")
                                self.vbox.addWidget(lab)

    def clearLayout(self,layout):
        while layout.count():
            child = layout.takeAt(0)
            child.widget().deleteLater()
            
