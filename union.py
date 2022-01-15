import sqlite3
from datetime import datetime, timedelta
import time
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt

conn = sqlite3.connect('factoryheatdb.sqlite')
cur = conn.cursor()

def check_last_date_tbl(tbl_name):
    #возвращаем дату последнего занесения данных в таблицу
    cur.execute("SELECT DISTINCT max(date) FROM "+tbl_name)
    last_date = cur.fetchall()
    if last_date[0][0] is None:
        last_date = "таблица пустая"
    else:
        last_date = last_date[0][0]
    return last_date

tbl_list = ['Calc_Heat_d', 'Fact_Heat_d', 'CH_Fact_Heat_d']
print("Последняя дата обновления таблиц: ")
for table in tbl_list:
    print(table + ": " + check_last_date_tbl(table)[:10])
print("\n")
sql_query = pd.read_sql_query ('''
SELECT
    CH_Fact_Heat_d.bildings_id as bild,
    CH_Fact_Heat_d.date as datetime,
    CH_Fact_Heat_d.fact_heat_ch as fact,
    Calc_Heat_d.bildings_id,
    Calc_Heat_d.date,
    Calc_Heat_d.calc_heat_d as calc,
    Calc_Heat_d.temp_out,
    Bildings.name as bildname
FROM CH_Fact_Heat_d
JOIN Calc_Heat_d
    ON Calc_Heat_d.bildings_id = CH_Fact_Heat_d.bildings_id
    AND Calc_Heat_d.date = CH_Fact_Heat_d.date
JOIN Bildings
    ON CH_Fact_Heat_d.bildings_id = Bildings.id
ORDER BY bild, datetime
''', conn)
df = pd.DataFrame(sql_query, columns = ['bildname', 'datetime',  "fact", 'calc'])
print(df)
