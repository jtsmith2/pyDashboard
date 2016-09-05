from GoogleMercatorProjection import LatLng
from PyQt4.QtGui import QColor

#API Keys

#change this to your API keys
# Weather Underground API key
wuapi = ''

# Google Maps API key
googleapi = ''   #Empty string, optional -- if you pull a small volume, you'll be ok

# Google Directions API key
directionsapi = ''


#Google Calendar Settings

# Google OAuth API Credentials
# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

calList = ['primary','other cal']                        # A list of the names of the calendars from GCal.  'primary' pulls the primary calendar
calColorList = [QColor(0,129,197),QColor(0,129,197)]    # A list of the colors assigned to each calendar in calList as RGB values

calendar_refresh = 15                                   #minutes


#YNAB Settings

ynabUser = ''                           # Example: someone@domain.com
ynabPassword = ''
ynabBudgetName = 'My Budget'            # Example:  My Budget
ynabShowKeyword = 'Show in Dashboard'   # Example: Show in Dashboard   This needs to be in 
                                        # the notes section of the subcategory in YNAB
ynab_refresh = 15                       # minutes


#Drive Time Settings

origin = "555 Main St., Someplace, CA 55555"                    # Address of the starting point for drive time calculation
dest = {}
dest["My Work"] = "555 Main St., Someplace, CA 55555"           # Name and address of destination point. Can add multiple destinations to the dest dictionary
dest["Another Work"] = "555 Main St., Someplace, CA 55555"

traffic_refresh = 5                                             # minutes


#Weather Settings


wuprefix = 'http://api.wunderground.com/api/'
wulocation = LatLng(32.58240,83.238592)       #Example: LatLng(32.58240,83.238592)
textcolor = '#bef'

metric = 0  #0 = English, 1 = Metric
radar_refresh = 10      # minutes
weather_refresh = 30    # minutes
wind_degrees = 0        # Wind in degrees instead of cardinal 0 = cardinal, 1 = degrees
satellite = 0           # Depreciated: use 'satellite' key in radar section, on a per radar basis
                        # if this is used, all radar blocks will get satellite images
                        
fontattr = ''   # gives all text additional attributes using QT style notation
                # example: fontattr = 'font-weight: bold; '
                
dimcolor = QColor('#000000')    # These are to dim the radar images, if needed.
dimcolor.setAlpha(0)            # see and try Config-Example-Bedside.py

# Language Specific wording
wuLanguage = "EN"   # Weather Undeground Language code (https://www.wunderground.com/weather/api/d/docs?d=language-support&MR=1)
DateLocale = ''  # The Python Locale for date/time (locale.setlocale) -- '' for default Pi Setting
                            # Locales must be installed in your Pi.. to check what is installed
                            # locale -a
                            # to install locales
                            # sudo dpkg-reconfigure locales
LWind = "Wind "
Lgusting = " gusting "
LFeelslike = "Feels like "


radar1 = {
    'center' : wulocation,  # the center of your radar block
    'zoom' : 7, # this is a google maps zoom factor, bigger = smaller area
    'satellite' : 0,    # 1 => show satellite images instead of radar (colorized IR images)
    'markers' : (   # google maps markers can be overlayed
        {
        'location' : wulocation,
        'color' : 'red',
        'size' : 'small',
        },          # dangling comma is on purpose.
        )
    }

    
radar2 = {
    'center' : wulocation,
    'zoom' : 11,
    'satellite' : 0,
    'markers' : (
        {
        'location' : wulocation,
        'color' : 'red',
        'size' : 'small',
        },
        )
    }
