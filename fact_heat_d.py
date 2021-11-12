import sqlite3
from datetime import datetime, timedelta
import time
import pandas as pd

conn = sqlite3.connect('factoryheatdb.sqlite')
cur = conn.cursor()

cur.executescript('''
DROP TABLE IF EXISTS Fact_Heat_d;
CREATE TABLE Fact_Heat_d(
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    bildings_id INTEGER NOT NULL,
    date DATE,
    fact_heat_all INTEGER,
    mass_in INTEGER,
    mass_out INTEGER,
    mass_delta INTEGER,
    temp_in INTEGER,
    temp_out INTEGER,
    temp_delta INTEGER,
    press_in INTEGER,
    press_out INTEGER,
    sensor_work_time INTEGER,
    sensor_off_time INTEGER
    fact_heat_ch INTEGER
);
''')

# cur.executescript('''
# CREATE TABLE IF NOT EXISTS Fact_Heat_d(
#     id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
#     bildings_id INTEGER NOT NULL,
#     date DATE,
#     fact_heat_all INTEGER,

#     mass_in INTEGER,
#     mass_out INTEGER,
#     mass_delta INTEGER,
#     temp_in INTEGER,
#     temp_out INTEGER,
    # temp_delta INTEGER,
#     press_in INTEGER,
#     press_out INTEGER,
#     sensor_work_time INTEGER,
#     sensor_off_time INTEGER
#     fact_heat_ch INTEGER
# );
# ''')

def read_sheet(bildNum, shName):
    if bildNum == 3:
        df1 = pd.read_excel("./other/Посуточная ведомость1.xlsx",sheet_name='КМ-5 ИТП1 ЗУпр')
        df1 = df1.drop(df1.columns[[0]], axis=1)
        df1 = df1.drop(range(0,9))
        df1 = df1.drop(range(40,50))
        df1.columns=['date',"fact_heat_all",'mass_in','mass_out',
        'mass_delta','temp_in','temp_out','temp_delta','press_in',
        'press_out','sensor_work_time','sensor_off_time']

        df2= pd.read_excel("./other/Посуточная ведомость1.xlsx",sheet_name='КМ-5 ИТП2 ЗУпр')
        df2 = df2.drop(df2.columns[[0]], axis=1)
        df2 = df2.drop(range(0,9))
        df2 = df2.drop(range(40,50))
        df2.columns=['date',"fact_heat_all",'mass_in','mass_out',
        'mass_delta','temp_in','temp_out','temp_delta','press_in',
        'press_out','sensor_work_time','sensor_off_time']

        df3 = pd.concat([df1, df2]).groupby(['date']).sum()
        df3.iloc[:,4:]*=0.5
        df3['bildings_id'] = bildNum
        print(df3)
        df3.to_sql('Fact_Heat_d', con = conn, if_exists='append', index=False)
        #дата не грузится в БД, проверить старый код ниже на ошибки


    # df = pd.read_excel("./other/Посуточная ведомость1.xlsx",sheet_name=shName)
    # df = df.drop(df.columns[[0]], axis=1)
    # df = df.drop(range(0,9))
    # df = df.drop(range(40,50))
    # df.columns=['date',"fact_heat_all",'mass_in','mass_out',
    # 'mass_delta','temp_in','temp_out','temp_delta','press_in',
    # 'press_out','sensor_work_time','sensor_off_time']
    # df['bildings_id'] = bildNum
    # df.to_sql('Fact_Heat_d', con = conn, if_exists='append', index=False)
    # print(df)

read_sheet(3, 'КМ-5 24 цех')

# cur.execute("SELECT id,name FROM Bildings")
# bilds = cur.fetchall()
# print(bilds)
# for bild in bilds:
#     bildNum = bild[0]
#     name = bild[1]
#     shName = "КМ-5 " + name

# conn.commit()
# conn.close()
