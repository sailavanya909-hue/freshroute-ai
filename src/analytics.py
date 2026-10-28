"""Shared, currency-specific analytics. Never combine INR/kg with USD/lb."""
from datetime import date
from math import isfinite


def sourcing(quotes, routes, size=80, report_date='2026-10-26', market='All',
             quantity=10000, sell_price=1.05, freight_delta=0, shrink_delta=0):
    values = [quantity, sell_price, freight_delta, shrink_delta]
    if not all(isfinite(float(x)) for x in values) or quantity <= 0 or sell_price < 0:
        raise ValueError('Use a positive quantity and a nonnegative selling price')
    route_map = {r['market']: r for r in routes}
    result=[]
    for q in quotes:
        if int(q['size_count']) != int(size) or q['report_date'] != report_date:
            continue
        if market != 'All' and q['market'] != market:
            continue
        r=route_map.get(q['market'])
        if not r:
            continue
        freight=float(r['freight_usd_lb'])+freight_delta
        shrink=float(r['shrink'])+shrink_delta
        if freight < 0 or not 0 <= shrink < 1:
            raise ValueError('Scenario would produce invalid freight or spoilage')
        buy=float(q['midpoint_usd_lb'])
        cost=quantity*(buy+freight)
        saleable=quantity*(1-shrink)
        revenue=saleable*sell_price
        result.append(dict(**q, freight_usd_lb=freight, shrink=shrink,
            quantity_lb=quantity, saleable_lb=saleable, variable_cost_usd=cost,
            modeled_revenue_usd=revenue, contribution_usd=revenue-cost,
            delivered_usd_lb=cost/saleable, low_delivered_usd_lb=(float(q['low_package'])/50+freight)/(1-shrink),
            high_delivered_usd_lb=(float(q['high_package'])/50+freight)/(1-shrink),
            feasible=quantity <= float(r['capacity_lb']), capacity_lb=float(r['capacity_lb']),
            transit_hours=float(r['transit_hours']), scenario_kind='assumption'))
    return sorted(result, key=lambda x:(not x['feasible'], x['delivered_usd_lb']))


def public_age(report_date, today=None):
    return ((today or date.today()) - date.fromisoformat(report_date)).days


def rescue(lots, markdown=0.15, expected_unsold=.25):
    if not 0 <= markdown < 1 or not 0 <= expected_unsold <= 1:
        raise ValueError('Invalid markdown or unsold fraction')
    results=[]
    for lot in sorted(lots, key=lambda x: x['remaining_days']):
        qty=float(lot['quantity_lb']); sell=float(lot['sell_usd_lb'])
        results.append(dict(**lot, hold_revenue_usd=qty*sell*(1-expected_unsold),
                            markdown_revenue_usd=qty*sell*(1-markdown),
                            incremental_revenue_usd=qty*sell*(expected_unsold-markdown)))
    return results
