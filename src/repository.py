"""Same read interface for portable SQLite and MySQL 8 deployments."""
import os
import sqlite3
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def read_data():
    if os.getenv('FRESHROUTE_DB','sqlite') == 'mysql':
        import pymysql
        con=pymysql.connect(host=os.getenv('MYSQL_HOST','127.0.0.1'), port=int(os.getenv('MYSQL_PORT','3306')),
            user=os.getenv('MYSQL_USER','freshroute_reader'), password=os.environ['MYSQL_PASSWORD'],
            database=os.getenv('MYSQL_DATABASE','freshroute'), cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=5, read_timeout=10)
    else:
        con=sqlite3.connect(ROOT/'data/freshroute.sqlite')
        con.row_factory=sqlite3.Row
    try:
        result={}
        # Table names are fixed in code, never supplied by a user or model.
        for key, table in [('quotes','terminal_quote'),('routes','route_assumption'),('lots','demo_inventory')]:
            cursor=con.cursor()
            cursor.execute(f'SELECT * FROM {table} LIMIT 50000')
            result[key]=[{k:(v.isoformat() if isinstance(v,(date,datetime)) else float(v) if isinstance(v,Decimal) else v)
                          for k,v in dict(r).items()} for r in cursor.fetchall()]
            cursor.close()
        return result
    finally:
        con.close()
