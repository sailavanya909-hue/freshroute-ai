"""Build reproducible public-data snapshots and explicitly labeled scenarios.

USDA terminal prices are manually transcribed, not automatically refreshed.
Never change a report date just because the application is run on a later day.
"""
import csv
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'


def build():
    # Idaho, U.S. One, Russet Norkotah, conventional, 50 lb cartons.
    # Ranges are overall quoted ranges, not the narrower "mostly" ranges.
    specifications = [
        ('Boston', '2026-10-26', 'bh_fv030', [(40,39,42),(50,39,42),(60,38,41),(70,38,41),(80,33,36),(90,30,34),(100,28,31),(120,28,30)]),
        ('Chicago', '2026-10-26', 'hx_fv030', [(40,32,35),(50,32,35),(60,30.5,35),(70,30.5,35),(80,26,30),(90,22,26),(100,20,23)]),
        ('New York', '2026-10-27', 'nx_fv030', [(40,42,45),(50,42,45),(60,40,42),(70,38,40),(80,34,36),(90,32,32),(100,28,28)]),
    ]
    quotes = []
    for market, date, report, values in specifications:
        for size, low, high in values:
            quotes.append(dict(quote_id=f'{report}_{date}_{size}', report_date=date,
                market=market, origin='Idaho', commodity='Potatoes', variety='Russet Norkotah',
                grade='U.S. One', size_count=size, package='50 lb cartons', package_lb=50,
                currency='USD', low_package=low, high_package=high,
                midpoint_package=(low+high)/2, midpoint_usd_lb=(low+high)/100,
                source_url=f'https://www.ams.usda.gov/mnreports/{report}.pdf',
                source_page=1, retrieved_date='2026-10-27', data_kind='observed',
                extraction='Manual transcription of reported overall range; midpoint derived, not modal price'))
    # These are scenarios, not actual freight quotes or inventory transactions.
    routes = [dict(market='Boston', destination='Regional distribution center', freight_usd_lb=.06, transit_hours=5, shrink=.03, capacity_lb=12000, data_kind='assumption'),
              dict(market='Chicago', destination='Regional distribution center', freight_usd_lb=.19, transit_hours=18, shrink=.06, capacity_lb=16000, data_kind='assumption'),
              dict(market='New York', destination='Regional distribution center', freight_usd_lb=.04, transit_hours=3, shrink=.025, capacity_lb=10000, data_kind='assumption')]
    lots = [dict(lot_id='DEMO-A', warehouse='Regional DC', quantity_lb=3200, remaining_days=2, purchase_usd_lb=.68, sell_usd_lb=.95, data_kind='simulated'),
            dict(lot_id='DEMO-B', warehouse='Regional DC', quantity_lb=4800, remaining_days=5, purchase_usd_lb=.73, sell_usd_lb=.99, data_kind='simulated'),
            dict(lot_id='DEMO-C', warehouse='Regional DC', quantity_lb=1800, remaining_days=9, purchase_usd_lb=.70, sell_usd_lb=1.02, data_kind='simulated')]
    DATA.mkdir(exist_ok=True)
    write_csv(DATA/'terminal_quotes.csv', quotes)
    write_csv(DATA/'route_assumptions.csv', routes)
    write_csv(DATA/'inventory_simulated.csv', lots)
    payload = dict(quotes=quotes, routes=routes, lots=lots, snapshot_date='2026-10-27',
                   coverage='Selected Idaho U.S. One Russet Norkotah quotes, 3 reports. Not a market census.',
                   date_note='Boston and Chicago: Oct 26. New York: Oct 27. Exact-date filters prevent silent mixing.',
                   refresh_mode='Archived snapshot; manual verification required before adding observations.')
    (DATA/'demo.json').write_text(json.dumps(payload, indent=2)+'\n')
    manifest = dict(snapshot_date='2026-10-27', rows=len(quotes), price_unit='USD per 50 lb carton',
                    derived_unit='USD/lb', method='manual transcription, overall range midpoint',
                    source_report_dates={m:d for m,d,_,_ in specifications},
                    source_urls=sorted({q['source_url'] for q in quotes}),
                    sha256=hashlib.sha256((DATA/'terminal_quotes.csv').read_bytes()).hexdigest())
    (DATA/'terminal_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    connection = sqlite3.connect(DATA/'freshroute.sqlite')
    for table, records in [('terminal_quote', quotes), ('route_assumption', routes), ('demo_inventory', lots)]:
        connection.execute(f'DROP TABLE IF EXISTS {table}')
        fields = records[0]
        columns = ', '.join(f'"{k}" '+('REAL' if isinstance(v,(int,float)) else 'TEXT') for k,v in fields.items())
        connection.execute(f'CREATE TABLE {table} ({columns})')
        connection.executemany(f'INSERT INTO {table} VALUES ({",".join("?" for _ in fields)})', [tuple(r.values()) for r in records])
    connection.commit()
    connection.close()
    print(f'Built {len(quotes)} source-traceable observations and labeled scenario inputs')


def write_csv(path, records):
    with path.open('w', newline='') as target:
        writer=csv.DictWriter(target, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


if __name__ == '__main__':
    build()
