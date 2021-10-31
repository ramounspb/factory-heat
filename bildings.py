import sqlite3
import csv
import locale
locale.setlocale(locale.LC_NUMERIC, 'ru_RU')

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

def ch_heat(volume, coef_a, coef_n, coef_beta):
    ch_heat = coef_beta * coef_a / (volume ** (1/coef_n))
    return ch_heat

with open(fname,'r', encoding='utf-8-sig') as csvfile:
    dr = csv.DictReader(csvfile,delimiter=';')
    for row in dr:
        name = row['name']
        type = row['type']
        free_height = locale.atof(row['free_height'])
        volume = locale.atof(row['volume'])
        coef_a = locale.atof(row['coef_a'])
        coef_n = locale.atof(row['coef_n'])
        coef_beta = locale.atof(row['coef_beta'])



        # ch_heat(volume, coef_a, coef_n, coef_beta)
        # print(ch_heat)

        cur.execute('''INSERT OR IGNORE INTO Bildings
            (name, type, free_height, volume, coef_a, coef_n, coef_beta)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (name, type, free_height, volume, coef_a, coef_n, coef_beta) )



conn.commit()
conn.close()
