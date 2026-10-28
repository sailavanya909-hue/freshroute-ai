"""Initialize schema, seed public snapshot, optionally create a SELECT-only account."""
import json
import os
from pathlib import Path
import pymysql

ROOT=Path(__file__).resolve().parents[1]


def setup():
    con=pymysql.connect(host=os.getenv('MYSQL_HOST','127.0.0.1'),port=int(os.getenv('MYSQL_PORT','3306')),
        user=os.getenv('MYSQL_ADMIN_USER','root'),password=os.environ['MYSQL_ROOT_PASSWORD'])
    try:
        with con.cursor() as cursor:
            for path in [ROOT/'sql/schema.sql',ROOT/'sql/terminal_schema.sql']:
                for statement in path.read_text().split(';'):
                    if statement.strip():cursor.execute(statement)
            data=json.loads((ROOT/'data/demo.json').read_text())
            for key,table in [('quotes','terminal_quote'),('routes','route_assumption'),('lots','demo_inventory')]:
                records=data[key];columns=list(records[0])
                # Fixed table/column names from the checked-in contract; values are parameters.
                names=','.join('`'+c+'`' for c in columns)
                updates=','.join(f'`{c}`=VALUES(`{c}`)' for c in columns)
                cursor.executemany(f'INSERT INTO {table} ({names}) VALUES ({",".join("%s" for _ in columns)}) ON DUPLICATE KEY UPDATE {updates}', [tuple(row[c] for c in columns) for row in records])
            if os.getenv('MYSQL_READER_PASSWORD'):
                cursor.execute("CREATE USER IF NOT EXISTS 'freshroute_reader'@'%%' IDENTIFIED BY %s",(os.environ['MYSQL_READER_PASSWORD'],))
                cursor.execute("ALTER USER 'freshroute_reader'@'%%' IDENTIFIED BY %s",(os.environ['MYSQL_READER_PASSWORD'],))
                cursor.execute("GRANT SELECT ON freshroute.* TO 'freshroute_reader'@'%'")
        con.commit()
        print('MySQL initialized with 22 public quote observations and labeled scenario inputs')
    finally:
        con.close()


if __name__=='__main__':setup()
