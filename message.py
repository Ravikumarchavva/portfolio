from flask_sqlalchemy import *
import json
import sqlite3
with open("config.json") as f:
    par=json.load(f)['params']

    con=sqlite3.connect(par['db_uri'])
    cur=con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for table in cur.fetchall():
        print(table[0])