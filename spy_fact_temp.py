import sqlite3
import locale
# locale.setlocale(locale.LC_ALL, 'ru_RU')
from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
from datetime import datetime


# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
#
# conn = sqlite3.connect('factoryheatdb.sqlite')
# cur = conn.cursor()
#
# cur.executescript('''
# DROP TABLE IF EXISTS Calc_Heat_d;
#
# CREATE TABLE Calc_Heat_d(
#     id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
#     bildings_id INTEGER NOT NULL UNIQUE,
#     date DATE,
#     temp_out INTEGER,
#     calc_heat_d INTEGER
# );
# ''')

# currentMonth = datetime.now().strftime('%B')
# currentYear = datetime.now().strftime('%Y')
# "http://weatherarchive.ru/Temperature/Saint%20Petersburg/October-2021"
# startUrl = "http://weatherarchive.ru/Temperature/Saint%20Petersburg/"
# url = startUrl + currentMonth + "-" + currentYear
# html = urlopen(url, context=ctx).read()
url = "C:\Users\salin_da\Desktop\DS\factory-heat-master\other\htmlTest.html"
html = urlopen(url, context=ctx).read()
soup = BeautifulSoup(html, "html.parser")
tags = soup('td')
for tag in tags:
#     # Look at the parts of a tag
#     print('TAG:', tag)
#     print('URL:', tag.get('href', None))
    print('Contents:', tag.contents[0])
#     print('Attrs:', tag.attrs)
