"""Local dashboard and JSON API. Run: python3 app/server.py"""
import csv
import io
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from repository import read_data
from analytics import sourcing, rescue
from assistant import answer


def filters(payload):
    return dict(size=int(payload.get('size',80)), report_date=str(payload.get('report_date','2026-10-26')),
        market=str(payload.get('market','All')), quantity=float(payload.get('quantity',10000)),
        sell_price=float(payload.get('sell_price',1.05)), freight_delta=float(payload.get('freight_delta',0)),
        shrink_delta=float(payload.get('shrink_delta',0)))


class Handler(BaseHTTPRequestHandler):
    def send(self, value, status=200, content_type='application/json'):
        body=value if isinstance(value,bytes) else json.dumps(value,allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type',content_type)
        self.send_header('Content-Length',str(len(body)))
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Cache-Control','no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path=urlparse(self.path).path
        try:
            if path=='/api/data':
                data=read_data()
                data['db_mode']=os.getenv('FRESHROUTE_DB','sqlite')
                data['assistant_mode']='OpenAI routing' if os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_MODEL') else 'Local intent matching'
                return self.send(data)
            if path=='/api/export':
                query={k:v[0] for k,v in parse_qs(urlparse(self.path).query).items()}
                rows=sourcing(**{k:v for k,v in read_data().items() if k in ('quotes','routes')},**filters(query))
                stream=io.StringIO()
                if rows:
                    writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
                    writer.writeheader(); writer.writerows(rows)
                return self.send(stream.getvalue().encode(),content_type='text/csv; charset=utf-8')
            if path=='/downloads/planner.xlsx':
                return self.send((ROOT/'excel/FreshRoute_Planner.xlsx').read_bytes(),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            if path in ('/','/index.html','/style.css','/app.js'):
                filename='index.html' if path=='/' else path.lstrip('/')
                types={'html':'text/html; charset=utf-8','css':'text/css','js':'text/javascript'}
                return self.send((ROOT/'app/static'/filename).read_bytes(),content_type=types[filename.split('.')[-1]])
            self.send({'error':'Not found'},404)
        except (ValueError,TypeError) as exc:
            self.send({'error':str(exc)},400)
        except Exception:
            self.send({'error':'Data connection unavailable. Check server configuration.'},503)

    def do_POST(self):
        # Local-only server. Reject cross-origin form submissions.
        origin=self.headers.get('Origin')
        if origin and urlparse(origin).netloc != self.headers.get('Host'):
            return self.send({'error':'Cross-origin request denied'},403)
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0 < length <= 16000:
                return self.send({'error':'Invalid request size'},413)
            payload=json.loads(self.rfile.read(length))
            data=read_data(); selected=filters(payload.get('filters',{}))
            path=urlparse(self.path).path
            if path=='/api/analyze':
                return self.send(dict(rows=sourcing(data['quotes'],data['routes'],**selected),rescue=rescue(data['lots']),filters=selected))
            if path=='/api/chat':
                return self.send(answer(payload.get('question',''),data,selected))
            return self.send({'error':'Not found'},404)
        except (ValueError,TypeError,KeyError) as exc:
            return self.send({'error':str(exc)},400)
        except Exception:
            return self.send({'error':'Analysis unavailable. Check server configuration.'},503)


if __name__=='__main__':
    port=int(os.getenv('PORT','8765'))
    print(f'FreshRoute AI: http://127.0.0.1:{port}',flush=True)
    ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()
