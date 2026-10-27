"""Normalize an official AGMARKNET CSV. Never invent missing records."""
import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal

SOURCE = 'https://www.data.gov.in/catalog/current-daily-price-various-commodities-various-markets-mandi'
REQUIRED = ['State','District','Market','Commodity','Variety','Grade','Arrival_Date','Min_Price','Max_Price','Modal_Price']
FIELDS = ['price_date','state','district','market','commodity','variety','grade','min_inr_kg','modal_inr_kg','max_inr_kg','source_url','retrieved_at']


def normalize(row, retrieved_at):
    for field in REQUIRED:
        if not str(row.get(field, '')).strip():
            raise ValueError(f'Missing {field}')
    prices = [Decimal(row[k]) / 100 for k in ['Min_Price','Modal_Price','Max_Price']]
    if not all(x.is_finite() for x in prices) or not 0 <= prices[0] <= prices[1] <= prices[2]:
        raise ValueError('Invalid price ordering or non-finite value')
    date = datetime.strptime(row['Arrival_Date'], '%d/%m/%Y').date().isoformat()
    return [date] + [row[k].strip() for k in REQUIRED[:6]] + prices + [SOURCE, retrieved_at]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    with open(args.input, encoding='utf-8-sig', newline='') as source:
        reader = csv.DictReader(source)
        if not set(REQUIRED).issubset(reader.fieldnames or []):
            raise ValueError('Headers differ from documented contract; map explicitly before importing')
        rows = []
        seen = set()
        for line, row in enumerate(reader, 2):
            try:
                values = normalize(row, now)
                key = tuple(values[:7])
                if key in seen:
                    raise ValueError('Duplicate observation key; resolve source revision explicitly')
                seen.add(key)
                rows.append(values)
            except Exception as exc:
                raise ValueError(f'Input line {line}: {exc}') from exc
    if not rows:
        raise ValueError('Empty export')
    with open(args.output, 'w', encoding='utf-8', newline='') as target:
        writer = csv.writer(target)
        writer.writerow(FIELDS)
        writer.writerows(rows)
    print(f'Validated {len(rows)} observations; no rows silently dropped')


if __name__ == '__main__':
    main()
