import sqlite3
from datetime import datetime, timedelta
import time
import pandas as pd

conn = sqlite3.connect('factoryheatdb.sqlite')
cur = conn.cursor()

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

last_date = check_last_date()
cur.execute("SELECT bildings_id, date, fact_heat_all FROM Fact_Heat_d")
dd = cur.fetchall()
for d in dd:
    print(d)
conn.commit()
conn.close()
