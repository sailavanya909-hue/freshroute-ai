import os
import unittest


@unittest.skipUnless(os.getenv('RUN_MYSQL_TESTS')=='1','Requires MySQL service; run in CI or local Docker')
class MySQLTests(unittest.TestCase):
    def test_mysql_view_and_constraints(self):
        import pymysql
        con=pymysql.connect(host=os.getenv('MYSQL_HOST','127.0.0.1'),port=int(os.getenv('MYSQL_PORT','3306')),
            user='root',password=os.environ['MYSQL_ROOT_PASSWORD'],database='freshroute')
        try:
            with con.cursor() as cur:
                cur.execute('SELECT COUNT(*) FROM terminal_quote');self.assertEqual(cur.fetchone()[0],22)
                cur.execute("SELECT market,delivered_usd_lb FROM terminal_sourcing_base WHERE report_date='2026-10-26' AND size_count=80 ORDER BY cost_rank")
                rows=cur.fetchall();self.assertEqual(rows[0][0],'Boston');self.assertAlmostEqual(float(rows[0][1]),.75/.97,places=6)
                with self.assertRaises(pymysql.MySQLError):cur.execute("UPDATE route_assumption SET shrink=1 WHERE market='Boston'")
            con.rollback()
        finally:con.close()


if __name__=='__main__':unittest.main()
