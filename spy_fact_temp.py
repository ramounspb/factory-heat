import sqlite3
import locale
# locale.setlocale(locale.LC_ALL, 'ru_RU')
from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
from datetime import datetime, timedelta
import time


## Ignore SSL certificate errors
# ctx = ssl.create_default_context()
# ctx.check_hostname = False
# ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('factoryheatdb.sqlite')
cur = conn.cursor()

##добавил IF NOT EXISTS
# cur.executescript('''
# CREATE TABLE IF NOT EXISTS Calc_Heat_d(
#     id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
#     bildings_id INTEGER NOT NULL,
#     date DATE,
#     temp_out INTEGER,
#     calc_heat_d INTEGER
# );
# ''')


# def parse_url(date_time):
    # currentMonth = date_time.strftime('%B')
    # currentMonth = "October"
    # currentYear = datetime.now().strftime('%Y')
    # # "http://weatherarchive.ru/Temperature/Saint%20Petersburg/October-2021"
    # startUrl = "http://weatherarchive.ru/Temperature/Saint%20Petersburg/"
    # url = startUrl + currentMonth + "-" + currentYear
    # html = urlopen(url, context=ctx).read()
    # soup = BeautifulSoup(html, "html.parser")
    # table_tag = soup.table[2].contents[0]
    # print(table_tag)
    # # for tag in tags:
    # # #     # Look at the parts of a tag
    #     # print('--->', tag.attrs)
    # #     # print('URL:', tag.get('td'))
    # #     # print(tag.contents[0])
    # # #     print('Attrs:', tag.attrs)
    #
    # # if????
#если не парсится недоступен, то внести от руки



def check_last_date():
    #возвращаем дату последнего занесения данных в таблицу Calc_Heat_d
    cur.execute("SELECT DISTINCT max(date) FROM Calc_Heat_d")
    last_date = cur.fetchall()
    last_date = last_date[0][0]
    return last_date

def manual_input():
    #в случае ошибки парсинга сайта, внести данные по температурам вручную
    now = datetime.now()
    last_date = check_last_date()
    last = datetime.strptime(last_date, '%d/%m/%Y')
    manual_dict = {}
    while last < (now - timedelta(days=2)):
        last = last + timedelta(days=1)
        last_str = last.strftime('%d/%m/%Y')
        while True:
            manual_temp = input('Введите температуру наружнего воздуха ' + last_str + " :")
            try:
                manual_dict[last_str] = float(manual_temp)
            except ValueError:
                print("Введено некорректное значение температуры. В качестве разделителя используйте точку.")
            else:
                break
# куда внести эту функцию??


def check_change_month():
    #создаем словарь, если произошло изменение месяца (дикт за "прошлый" месяц)
    now = datetime.now()
    last_date = check_last_date()
    last = datetime.strptime(last_date, '%d/%m/%Y')
    change_month_dict = {}
    if now.strftime('%m') > last.strftime('%m'):
        # change_month_dict = parse_url(last)
        change_month_dict = {'28 сентября':'+18.25°C','29 сентября':'+18.25°C','30 сентября':'+18.25°C'}
        return change_month_dict
    else:
        return change_month_dict

date_time = datetime.now()
# dict = parse_url(date_time) #try-expect
change_month_dict = check_change_month()

url = "http://weatherarchive.ru/Temperature/Saint%20Petersburg/October-2021"
dictTest = {'1 октября':'+8.25°C', '2 октября':'+9.75°C', '3 октября':'+8.88°C', '4 октября':'+7.88°C', '5 октября':'+6.88°C', '6 октября':'+5.88°C', '7 октября':'+4.88°C', '8 октября':'+3.88°C'}
dictTest.update(change_month_dict) #если произошло изменение месяца, добавляем инф в общий дикт

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
        yr = date_time.strftime('%Y')
        day = day_rus[0] +'/'+ month_num +'/'+ yr
        return day

    def convert_temp(temp):
    #"чистим" температуру с сайта
        temp = float(temp[:-2])
        return temp

    clear_data = {}
    for day, temp in dict.items():
        day = convert_date(day)
        temp = convert_temp(temp)
        clear_data[day] = temp
    return clear_data

def cut_clear_date(clear_data):
#убираем из clear_data даты и температуры, которые уже есть в таблице Calc_Heat_d
    last_date = check_last_date()
    last_date = time.mktime(datetime.strptime(last_date, "%d/%m/%Y").timetuple())
    clear_data_new = {}
    for k, v in clear_data.items():
        if time.mktime(datetime.strptime(k, "%d/%m/%Y").timetuple()) > last_date:
            clear_data_new[k] = v
    return clear_data_new

clear_data = clear_from_url(dictTest)
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
        # cur.execute('''INSERT OR IGNORE INTO Calc_Heat_d
        #     (bildings_id, date, temp_out, calc_heat_d)
        #     VALUES (?, ?, ?, ?)''',
        #     (bildings_id, day, temp_out, calc_heat_d) )
conn.commit()
conn.close()