import sqlite3
from datetime import datetime, timedelta
import time
import pandas as pd
import numpy as np
import pyromat as pm

pm.config['unit_energy'] = 'kcal'
pm.config['unit_temperature'] = 'C'
h2o = pm.get("mp.H2O")


conn = sqlite3.connect('factoryheatdb.sqlite')
cur = conn.cursor()
# cur.executescript('''
# DROP TABLE IF EXISTS CH_Fact_Heat_d
# ''')

cur.executescript('''
CREATE TABLE IF NOT EXISTS CH_Fact_Heat_d(
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    bildings_id INTEGER NOT NULL,
    date DATE,
    fact_heat_all INTEGER,
    temp_cold_water INTEGER,
    enthalpy_cold_water INTEGER,
    enthalpy_in_water INTEGER,
    enthalpy_out_water INTEGER,
    fact_heat_ch INTEGER,
    fact_heat_gvs INTEGER,
    fact_heat_ch_error INTEGER
);
''')

def check_last_date():
    #возвращаем дату последнего занесения данных в таблицу Fact_Heat_d
    cur.execute("SELECT DISTINCT max(date) FROM CH_Fact_Heat_d")
    last_date = cur.fetchall()
    if last_date[0][0] is None:
        last_date = datetime.now() - timedelta(days=365)
    else:
        last_date = datetime.strptime(last_date[0][0], '%Y-%m-%d %H:%M:%S')
    return last_date

def c_water(date):
    date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    if int(date.strftime('%m')) in [5,6,7,8,9,10]:
        return 15
    return 5

def fact_h(h_all, ent_c, ent_in, ent_out, m_in, m_d):
    ch = round(m_in * (ent_in - ent_out) /1000, 3)
    gvs = round(m_d * (ent_in - ent_c) / 1000, 3)
    er = round(100 * (ch + gvs - h_all)/h_all, 3)
    return [ch,gvs,er]


last_date = check_last_date()
cur.execute("SELECT bildings_id, date, fact_heat_all, temp_in, temp_out, \
            mass_in, mass_delta FROM Fact_Heat_d")
factData = cur.fetchall()
for rowData in factData:
    if datetime.strptime(rowData[1], '%Y-%m-%d %H:%M:%S') <= last_date:
        continue
    bildings_id = rowData[0]
    date = rowData[1]
    fact_heat_all = round(rowData[2],3)
    temp_cold_water = c_water(date)
    # enthalpy_cold_water = 5
    # enthalpy_in_water = 1
    # enthalpy_out_water = 2
    enthalpy_cold_water = round(h2o.h(T=temp_cold_water, p=1.)[0], 3)
    enthalpy_in_water = round(h2o.h(T=rowData[3], p=1.)[0], 3)
    enthalpy_out_water = round(h2o.h(T=rowData[4], p=1.)[0], 3)
    fh = fact_h(fact_heat_all, enthalpy_cold_water, enthalpy_in_water,
                enthalpy_out_water, rowData[5], rowData[6])
    if fh[0] <= 0:
        print("Ошибка в данных bildings_id=" + str(bildings_id) + " за " + date)
    cur.execute('''INSERT OR IGNORE INTO CH_Fact_Heat_d
        (bildings_id, date, fact_heat_all, temp_cold_water, enthalpy_cold_water,
        enthalpy_in_water, enthalpy_out_water, fact_heat_ch, fact_heat_gvs,
        fact_heat_ch_error)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (bildings_id, date, fact_heat_all, temp_cold_water, enthalpy_cold_water,
        enthalpy_in_water, enthalpy_out_water, fh[0], fh[1], fh[2]) )

conn.commit()
conn.close()
