import sqlite3
from datetime import datetime, timedelta
import time
import pandas as pd

conn = sqlite3.connect('factoryheatdb.sqlite')
cur = conn.cursor()

cur.executescript('''
CREATE TABLE IF NOT EXISTS Fact_Heat_d(
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    bildings_id INTEGER NOT NULL,
    fact_heat_all INTEGER,
    fact_heat_ch INTEGER,
    mass_in INTEGER,
    mass_out INTEGER,
    temp_in INTEGER,
    temp_out INTEGER,
    press_in INTEGER,
    press_out INTEGER,
    sensor_work_time INTEGER,
    sensor_off_time INTEGER
);
''')


# cur.execute("SELECT * FROM Bildings")
# bilds = cur.fetchall()
# for day, temp_out in final_data.items():
#     for bild in bilds:
#         bildings_id = bild[0]
#         type = bild[2]
#         load_h = bild[10]
#         calc_heat_d = round(calc_heat(type, load_h, temp_out),5)
#         cur.execute('''INSERT OR IGNORE INTO Calc_Heat_d
#             (bildings_id, date, temp_out, calc_heat_d)
#             VALUES (?, ?, ?, ?)''',
#             (bildings_id, day, temp_out, calc_heat_d) )
# conn.commit()
# conn.close()
