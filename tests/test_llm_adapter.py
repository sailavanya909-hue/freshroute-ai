import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from assistant import llm_intent


class FakeResponse:
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self):return json.dumps({'output':[{'type':'message','content':[{'type':'output_text','text':'{"intent":"source"}'}]}]}).encode()


class LLMAdapterTests(unittest.TestCase):
    @patch.dict(os.environ,{'OPENAI_API_KEY':'unit-test-placeholder','OPENAI_MODEL':'configured-test-model'})
    @patch('urllib.request.urlopen',return_value=FakeResponse())
    def test_intent_request_contract_without_live_api(self,request):
        self.assertEqual(llm_intent('Which market should I source from?'),'source')
        payload=json.loads(request.call_args.args[0].data)
        self.assertFalse(payload['store'])
        self.assertEqual(payload['text']['format']['schema']['properties']['intent']['enum'][-1],'unknown')
        self.assertEqual(payload['input'],'Which market should I source from?')
        self.assertNotIn('quotes',payload)


if __name__=='__main__':unittest.main()
