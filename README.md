# pyDashboard
A morning dashboard pulling information from around the web

## Background

This project started as a modification of [PiClock](http://www.github.com/n0bel/piClock) which is basically a clock/weather
radio replacement with forecasts and radar.  I thought that was a pretty cool idea, but I didn\'t need so much weather info, but
would really have liked other info.  And so pyDashboard was born.  

## The Basics

pyDashboard pulls information from the following sources:

-Weather Underground (for weather)
-Google Maps (for drive times)
-Google Calendar (for calendar events)
-You Need a Budget (for the budget categories)

### Weather Widget

This information requires you to sign up for an API key from Weather Underground at the Anvil Plan level.  This is free for
small usage and so you should be fine. The two radar areas are customizable as to the location shown and zoom level (see 
Config.py for settings)

### Drive Times Widget

You must sign up for a Google Directions server API key.  Again, this is free for small usage.  You can specifiy multiple
locations in Config.py to get drive times to multiple destinations.

### Calendar Widget

This widget uses OAuth2 and so the first time you use the software, it should ask you for your Google credentials and store
those locally so that you won\'t be prompted again.  You can pull multiple calendars from your Google account (including those
shared with you) and specify different colors to display each.

### YNAB Widget

This widget requires the username/password combo to be put into Config.py.  It will connect to YNAB server and pull down all 
current info.  I use the notes field for categories to determine which ones to pull into the dashboard.  By default, if the
notes field contains "Show in Dashboard", it will be pulled in.  This phrase is editable in Config.py.

## Prerequisites

The following must be installed on the system:
-Python 2.7 (not 3)
-PyQt4
-Google Maps Python Client
-Google Calendar Python Client

### Python 2.7

Can be downloaded from [Python.org](https://www.python.org/download/releases/2.7/)

### PyQt4

Can be downloaded from [PyQt4](https://www.riverbankcomputing.com/software/pyqt/download)

### Google Maps Client

See [Google Maps Client Website](https://github.com/googlemaps/google-maps-services-python)

### Google Calendar Client

See [Google Developer](https://developers.google.com/google-apps/calendar/quickstart/python)

## About Me

I\'m a stats professor by day in the Atlanta metro area.  You can find me on twitter 
at http://www.twitter.com/jtsmith2 or on FB at http://facebook.com/jtsmith2
