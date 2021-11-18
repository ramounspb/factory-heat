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

def check_last_date():
    #возвращаем дату последнего занесения данных в таблицу Fact_Heat_d
    cur.execute("SELECT DISTINCT max(date) FROM Fact_Heat_d")
    last_date = cur.fetchall()
    if last_date[0][0] is None:
        last_date = datetime.now() - timedelta(days=365)
    else:
        last_date = datetime.strptime(last_date[0][0], '%Y-%m-%d %H:%M:%S')
    return last_date

def read_sheet(bildNum, shName,last_date):
    def drop_extra(df,last_date):
        df = df.drop(df.columns[[0]], axis=1)
        df = df.drop(range(0,9))
        df = df.drop(df.iloc[-10:,:].index)
        df.columns=['date',"fact_heat_all",'mass_in','mass_out',
        'mass_delta','temp_in','temp_out','temp_delta','press_in',
        'press_out','sensor_work_time','sensor_off_time']

        for index, row in df.iterrows():
            if row['date'] <= last_date:
                df = df.drop(index)
            else:
                if pd.isna(row['fact_heat_all']):
                    df = df.drop(index)
                else:
                    continue
        return df

    if bildNum == 3:
        #по ЗУ в выгрузке две вкладки, их нужно суммировать
        df1 = pd.read_excel("./other/Посуточная ведомость1.xlsx",sheet_name='КМ-5 ИТП1 ЗУпр')
        df1 = drop_extra(df1,last_date)
        df2 = pd.read_excel("./other/Посуточная ведомость1.xlsx",sheet_name='КМ-5 ИТП2 ЗУпр')
        df2 = drop_extra(df2,last_date)
        df3 = pd.concat([df1, df2]).groupby(['date'],as_index=False).sum()
        if len(df3.index) == 0:
            print('По ' + shName + ' новые данные отсутствуют')
        else:
            df3.iloc[:,4:]*=0.5
            df3['bildings_id'] = bildNum
            df3.to_sql('Fact_Heat_d', con = conn, if_exists='append', index=False)
            print('Данные с ' + shName + ' загружены')

    else:
        df = pd.read_excel("./other/Посуточная ведомость1.xlsx",sheet_name=shName)
        df = drop_extra(df,last_date)
        if len(df.index) == 0:
            print('По ' + shName + ' новые данные отсутствуют')
        else:
            df['bildings_id'] = bildNum
            df.to_sql('Fact_Heat_d', con = conn, if_exists='append', index=False)
            print('Данные с ' + shName + ' загружены')

last_date = check_last_date()
cur.execute("SELECT id,name FROM Bildings")
bilds = cur.fetchall()
for bild in bilds:
    bildNum = bild[0]
    name = bild[1]
    shName = "КМ-5 " + name
    read_sheet(bildNum, shName,last_date)
conn.commit()
conn.close()
