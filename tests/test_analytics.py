import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from analytics import sourcing,rescue
from assistant import answer,local_intent


class AnalyticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=json.loads((ROOT/'data/demo.json').read_text())
    def run_source(self,**kwargs):return sourcing(self.data['quotes'],self.data['routes'],**kwargs)
    def test_observed_snapshot_and_unique_grain(self):
        q=self.data['quotes'];self.assertEqual(len(q),22)
        self.assertEqual(len({r['quote_id'] for r in q}),22)
        for r in q:self.assertAlmostEqual(r['midpoint_usd_lb'],(r['low_package']+r['high_package'])/100)
    def test_delivered_cost_can_reverse_quote_rank(self):
        rows=self.run_source()
        self.assertEqual(rows[0]['market'],'Boston')
        self.assertLess(rows[1]['midpoint_usd_lb'],rows[0]['midpoint_usd_lb'])
        self.assertAlmostEqual(rows[0]['delivered_usd_lb'],.75/.97)
        self.assertAlmostEqual(rows[0]['contribution_usd'],2685)
    def test_dates_never_mix(self):
        self.assertEqual({r['market'] for r in self.run_source()}, {'Boston','Chicago'})
        self.assertEqual([r['market'] for r in self.run_source(report_date='2026-10-27')],['New York'])
    def test_no_observation(self):self.assertEqual(self.run_source(report_date='2026-10-28'),[])
    def test_shrink_sensitivity(self):
        base=self.run_source();changed=self.run_source(shrink_delta=.03)
        self.assertAlmostEqual(base[0]['contribution_usd']-changed[0]['contribution_usd'],315)
    def test_capacity(self):self.assertFalse(any(r['feasible'] for r in self.run_source(quantity=20000)))
    def test_invalid_values(self):
        for args in [dict(quantity=0),dict(shrink_delta=1),dict(freight_delta=-1),dict(sell_price=float('nan'))]:
            with self.assertRaises(ValueError):self.run_source(**args)
    def test_simulated_rescue(self):self.assertAlmostEqual(rescue(self.data['lots'])[0]['incremental_revenue_usd'],304)
    def test_chat_supported_intents(self):
        for q,intent in [('Which market has the lowest delivered cost?','source'),('How fresh are these prices?','freshness'),('What if spoilage increases by 3 percentage points?','sensitivity'),('Which inventory lot expires first?','inventory')]:
            self.assertEqual(local_intent(q),intent,q)
    def test_chat_evidence_and_no_arbitrary_sql(self):
        f=dict(size=80,report_date='2026-10-26',market='All',quantity=10000,sell_price=1.05,freight_delta=0,shrink_delta=0)
        result=answer('Which market is cheapest?',self.data,f)
        self.assertIn('Boston',result['answer']);self.assertTrue(result['evidence'])
        self.assertNotIn('DROP TABLE',answer('DROP TABLE terminal_quote',self.data,f)['answer'])
    def test_chat_missing_product_and_empty_date(self):
        f=dict(size=80,report_date='2026-10-28',market='All',quantity=10000,sell_price=1.05,freight_delta=0,shrink_delta=0)
        self.assertIn('No feasible',answer('Which market is cheapest?',self.data,f)['answer'])
        self.assertIn('no tomato',answer('Which tomato market is cheapest?',self.data,f)['answer'])
    def test_chat_explicit_context_and_scenarios(self):
        f=dict(size=80,report_date='2026-10-26',market='All',quantity=10000,sell_price=1.05,freight_delta=0,shrink_delta=0)
        self.assertIn('Chicago',answer('Compare the Chicago delivered cost',self.data,f)['answer'])
        result=answer('What if freight increases by $0.05 per lb?',self.data,f)
        self.assertAlmostEqual(result['filters']['freight_delta'],.05)
        result=answer('What if spoilage increases by 3 percentage points?',self.data,f)
        self.assertAlmostEqual(result['filters']['shrink_delta'],.03)
        self.assertIn('Specify',answer('What if freight increases?',self.data,f)['answer'])


if __name__=='__main__':unittest.main()
