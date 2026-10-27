"""Deterministic scenario math; values are user assumptions, not predicted outcomes."""
from math import isfinite


def evaluate(quantity_kg, buy_inr_kg, sell_inr_kg, freight_inr_kg, spoilage_fraction):
    values = (quantity_kg, buy_inr_kg, sell_inr_kg, freight_inr_kg, spoilage_fraction)
    if not all(isfinite(x) for x in values):
        raise ValueError('Inputs must be finite')
    if quantity_kg <= 0 or min(buy_inr_kg, sell_inr_kg, freight_inr_kg) < 0:
        raise ValueError('Positive quantity and nonnegative prices required')
    if not 0 <= spoilage_fraction < 1:
        raise ValueError('Spoilage must be between 0 inclusive and 1 exclusive')
    saleable = quantity_kg * (1 - spoilage_fraction)
    cost = quantity_kg * (buy_inr_kg + freight_inr_kg)
    revenue = saleable * sell_inr_kg
    return dict(saleable_kg=saleable, total_cost_inr=cost,
                break_even_inr_kg=cost / saleable,
                modeled_revenue_inr=revenue, modeled_contribution_inr=revenue-cost)
