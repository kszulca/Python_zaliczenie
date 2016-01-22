# -*- coding: utf-8 -*-

import sqlite3


db_path = 'temp_hist.db'
conn = sqlite3.connect(db_path)

c = conn.cursor()
#
# Tabele
#
c.execute('''
          CREATE TABLE czujnik
          ( id INTEGER PRIMARY KEY,
            serial_number NUMERIC NOT NULL,
            lokalizacja VARCHAR(100) NOT NULL
          )
          ''')
c.execute('''
          CREATE TABLE pomiar
          ( id INTEGER PRIMARY KEY,
            czujnik_id INTEGER NOT NULL,
            pomiar NUMERIC NOT NULL,
            data VARCHAR(10) NOT NULL,
           FOREIGN KEY(czujnik_id) REFERENCES czujnik(idd))
          ''')
