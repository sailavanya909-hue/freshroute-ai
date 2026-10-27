import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from economics import evaluate
from import_prices import normalize


class ProjectTests(unittest.TestCase):
    def test_shrink_applies_to_revenue_not_purchase_cost(self):
        result = evaluate(100, 20, 30, 2, .1)
        self.assertEqual(result['saleable_kg'], 90)
        self.assertEqual(result['modeled_contribution_inr'], 500)
        self.assertAlmostEqual(result['break_even_inr_kg'], 2200/90)

    def test_invalid_inputs(self):
        for quantity, loss in [(0, 0), (100, 1), (100, -.1), (float('nan'), 0)]:
            with self.assertRaises(ValueError):
                evaluate(quantity, 20, 30, 2, loss)

    def test_zero_loss(self):
        self.assertEqual(evaluate(100, 20, 30, 2, 0)['modeled_contribution_inr'], 800)

    def test_price_conversion(self):
        row = dict(State='Example', District='Example', Market='Example', Commodity='Tomato',
                   Variety='Example', Grade='Example', Arrival_Date='27/10/2026',
                   Min_Price='1000', Modal_Price='2000', Max_Price='3000')
        self.assertEqual(float(normalize(row, '2026-10-27 00:00:00')[8]), 20)
        row['Modal_Price'] = '4000'
        with self.assertRaises(ValueError):
            normalize(row, '2026-10-27 00:00:00')


if __name__ == '__main__':
    unittest.main()
