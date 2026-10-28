import json
import sys
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app'))
from server import Handler


class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.url=f'http://127.0.0.1:{cls.server.server_port}'
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def post(self,path,payload,origin=None):
        headers={'Content-Type':'application/json'}
        if origin:headers['Origin']=origin
        return urllib.request.urlopen(urllib.request.Request(self.url+path,data=json.dumps(payload).encode(),headers=headers))
    def test_data(self):
        with urllib.request.urlopen(self.url+'/api/data') as r:self.assertEqual(len(json.load(r)['quotes']),22)
    def test_analysis_and_chat(self):
        with self.post('/api/analyze',{'filters':{}}) as r:self.assertAlmostEqual(json.load(r)['rows'][0]['contribution_usd'],2685)
        with self.post('/api/chat',{'question':'Which market is cheapest?','filters':{}}) as r:self.assertIn('Boston',json.load(r)['answer'])
    def test_invalid_scenario(self):
        with self.assertRaises(urllib.error.HTTPError) as e:self.post('/api/analyze',{'filters':{'quantity':0}})
        self.assertEqual(e.exception.code,400)
    def test_cross_origin_denied(self):
        with self.assertRaises(urllib.error.HTTPError) as e:self.post('/api/chat',{'question':'hello'},origin='https://example.com')
        self.assertEqual(e.exception.code,403)
    def test_download_and_export(self):
        with urllib.request.urlopen(self.url+'/downloads/planner.xlsx') as r:self.assertEqual(r.read(2),b'PK')
        with urllib.request.urlopen(self.url+'/api/export?size=80&report_date=2026-10-26') as r:
            text=r.read().decode();self.assertIn('Boston',text);self.assertNotIn('New York',text)
    def test_traversal_is_not_served(self):
        with self.assertRaises(urllib.error.HTTPError) as e:urllib.request.urlopen(self.url+'/../.env')
        self.assertEqual(e.exception.code,404)


if __name__=='__main__':unittest.main()
