import sqlite3
import csv
import locale
locale.setlocale(locale.LC_ALL, 'ru_RU')

conn = sqlite3.connect('factoryheatdb.sqlite')
cur = conn.cursor()

cur.executescript('''
DROP TABLE IF EXISTS Bildings;

CREATE TABLE Bildings(
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT UNIQUE,
    type    TEXT,
    free_height INTEGER,
    volume INTEGER,
    coef_a INTEGER,
    coef_n INTEGER,
    coef_beta INTEGER,
    ch_heat INTEGER,
    coef_inf INTEGER,
    load_h INTEGER
);
''')

fname = input('Enter file name: ')
if ( len(fname) < 1 ) : fname = 'bilds.csv'

def ch_heat_calc(volume, coef_a, coef_n, coef_beta):
    # qo=β*a/V^(1/n)
    ch_heat = coef_beta * coef_a / (volume ** (1/coef_n))
    return ch_heat


def coef_inf_calc(type, free_height):
    # Кир=10-2*(2*g*L*(1-(273+tро)/(273+tвн))+wо2)^0,5
    g = 9.81 #acceleration of gravity
    L = free_height #average floor height
    t_calc = -24 #calculated outdoor temperature for the region
    if type=="administrative": #the temperature inside the building
        t_in = 18
    else:
        t_in = 16
    w = 2.5 #estimated wind speed during the heating season
    coef_inf = (10**-2)*((2*g*L*(1-(273+t_calc)/(273+t_in))+w**2)**0.5)
    return coef_inf

def load_h_calc(type, volume, ch_heat, coef_inf):
    # Qсо max = V*qо*(tвн-tро)*(1+Кир)*10-6
    V = volume
    if type=="administrative": #the temperature inside the building
        t_in = 18
    else:
        t_in = 16
    t_calc = -24 #calculated outdoor temperature for the region
    load_h = V * ch_heat * (t_in - t_calc)*(1+coef_inf)*(10**-6)
    return load_h

with open(fname,'r', encoding='utf-8-sig') as csvfile:
    dr = csv.DictReader(csvfile,delimiter=';')
    for row in dr:
        name = row['name']
        type = row['type']
        free_height = locale.atof(row['free_height'])
        volume = round(locale.atof(row['volume']),0)
        coef_a = locale.atof(row['coef_a'])
        coef_n = locale.atof(row['coef_n'])
        coef_beta = locale.atof(row['coef_beta'])
        ch_heat = round(ch_heat_calc(volume, coef_a, coef_n, coef_beta),5)
        coef_inf = round(coef_inf_calc(type, free_height),5)
        load_h = round(load_h_calc(type, volume, ch_heat, coef_inf),5)
        
        cur.execute('''INSERT OR IGNORE INTO Bildings
            (name, type, free_height, volume, coef_a, coef_n, coef_beta, ch_heat, coef_inf, load_h)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (name, type, free_height, volume, coef_a, coef_n, coef_beta, ch_heat, coef_inf, load_h) )

conn.commit()
conn.close()
