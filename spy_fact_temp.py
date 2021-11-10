import sqlite3
import locale
from urllib.request import urlopen
import ssl
from datetime import datetime, timedelta
import time

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('factoryheatdb.sqlite')
cur = conn.cursor()

cur.executescript('''
CREATE TABLE IF NOT EXISTS Calc_Heat_d(
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    bildings_id INTEGER NOT NULL,
    date DATE,
    temp_out INTEGER,
    calc_heat_d INTEGER
);
''')

def parse_url(date_time):
    Month = date_time.strftime('%B')
    Year = datetime.now().strftime('%Y')
    # "http://weatherarchive.ru/Temperature/Saint%20Petersburg/October-2021"
    startUrl = "http://weatherarchive.ru/Temperature/Saint%20Petersburg/"
    url = startUrl + Month + "-" + Year
    table = pd.read_html(url)[2]
    table = table.drop(table.columns[[2,3,4]], axis=1)
    dictTest = pd.Series(table.Среднесуточнаятемпература.values,index=table.Деньмесяца).to_dict()
    return dictTest

def check_last_date():
    #возвращаем дату последнего занесения данных в таблицу Calc_Heat_d
    cur.execute("SELECT DISTINCT max(date) FROM Calc_Heat_d")
    last_date = cur.fetchall()
    last_date = datetime.strptime(last_date[0][0], '%Y-%m-%d %H:%M:%S')
    if last_date is None:
        last_date = datetime.now() - timedelta(days=1)
    return last_date

def manual_input():
    #в случае ошибки парсинга сайта/Pandas, внести данные по температурам вручную
    now = datetime.now()
    last = check_last_date()
    manual_dict = {}
    while last < (now - timedelta(days=2)):
        last = last + timedelta(days=1)
        while True:
            manual_temp = input('Введите температуру наружнего воздуха ' + last.strftime('%Y-%m-%d') + " :")
            try:
                manual_dict[last] = float(manual_temp)
            except ValueError:
                print("Введено некорректное значение температуры. В качестве разделителя используйте точку.")
            else:
                break
    return manual_dict

def check_change_month():
    #создаем словарь, если произошло изменение месяца (дикт за "прошлый" месяц)
    now = datetime.now()
    last = check_last_date()
    change_month_dict = {}
    if now.strftime('%m') > last.strftime('%m'):
        change_month_dict = parse_url(last)
        return change_month_dict
    else:
        return change_month_dict

def clear_from_url (dict):
#готовим данные с сайта для занесения в таблицу Calc_Heat_d
    def convert_date(day):
    #полученные строчные даты с сайта конвертируем в дату
        day_rus = day.split()
        rus_month = day_rus[1][:3]
        month = {'янв':'1','фев':'2','мар':'3','апр':'4','май':'5','июн':'6','июл':'7','авг':'8','сен':'9','окт':'10','ноя':'11','дек':'12'}
        for key, val in month.items():
            if rus_month == key:
                month_num = val
                break
        yr = datetime.now().strftime('%Y')
        day = yr +'-'+ month_num +'-'+ day_rus[0]
        day = datetime.strptime(day, '%Y-%m-%d')
        return day
    def convert_temp(temp):
    #"чистим" температуру с сайта
        temp = temp.replace("−", "-")
        temp = float(temp[:-2])
        return temp
    clear_data = {}
    for day, temp in dict.items():
        day = convert_date(day)
        temp = convert_temp(temp)
        clear_data[day] = temp
    print("==Data have been successfully cleared==")
    return clear_data

try:
    import pandas as pd
    dict = parse_url(datetime.now())
    if len(dict) > 0:
        print("==Temperatures for the current month have been successfully parsed==")
        change_month_dict = check_change_month()
        if len(change_month_dict) > 0:
            print("==Change of the month. Temperatures have been successfully parsed==")
            dict.update(change_month_dict) #если произошло изменение месяца, добавляем инф в общий дикт
        else:
            print("==The month change did not happen==")
        clear_data = clear_from_url(dict)
    else:
        print("==Parsing FAILED. Manual input==")
        dict = manual_input()

except ImportError:
    print("==Ошибка загрузки библиотеки Pandas==")
    clear_data = manual_input()

def cut_clear_date(clear_data):
#убираем из clear_data даты и температуры, которые уже есть в таблице Calc_Heat_d
    last_date = check_last_date()
    last_date = time.mktime(last_date.timetuple())
    now = datetime.now()
    now = now.replace(hour=0, minute=0, second=0, microsecond=0)
    now = time.mktime(now.timetuple())
    clear_data_new = {}
    for k, v in clear_data.items():
        if time.mktime(k.timetuple()) > last_date and time.mktime(k.timetuple()) < now:
            clear_data_new[k] = v
    if len(clear_data_new) > 0:
        print("==Data have been successfully cut==")
        return clear_data_new
    else:
        print("==NO data to add to DB==")
        exit()

final_data = cut_clear_date(clear_data)

def calc_heat(type, load_h, temp_out):
#вычисляем Гкал на основании температуры наружнего воздуха с сайта
    if type=="administrative": #the temperature inside the building
        t_in = 18
    else:
        t_in = 16
    t_calc = -24 #calculated outdoor temperature for the region
    # Qсо=Qсо max*(tвн-tср.оф)/(tвн-tро)*nо*zо
    calc_heat_d = load_h * ((t_in - temp_out)/(t_in - t_calc)) * 24
    return calc_heat_d

cur.execute("SELECT * FROM Bildings")
bilds = cur.fetchall()
for day, temp_out in final_data.items():
    for bild in bilds:
        bildings_id = bild[0]
        type = bild[2]
        load_h = bild[10]
        calc_heat_d = round(calc_heat(type, load_h, temp_out),5)
        cur.execute('''INSERT OR IGNORE INTO Calc_Heat_d
            (bildings_id, date, temp_out, calc_heat_d)
            VALUES (?, ?, ?, ?)''',
            (bildings_id, day, temp_out, calc_heat_d) )
conn.commit()
conn.close()
