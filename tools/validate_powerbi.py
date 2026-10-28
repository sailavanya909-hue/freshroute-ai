"""Validate PBIR files against Microsoft's public schemas; check field bindings."""
import hashlib
import json
import os
import urllib.request
from pathlib import Path
from urllib.parse import urlparse
import jsonschema

ROOT=Path(__file__).resolve().parents[1]
CACHE=Path(os.getenv('PBI_SCHEMA_CACHE',str(ROOT/'.cache/schemas')))


def fetch(url):
    if urlparse(url).hostname!='developer.microsoft.com':raise ValueError('Unexpected schema host')
    # Microsoft's embedded visual schema declares a dotted $id but is served
    # with a hyphen in its filename. Both identify the same official schema.
    url=url.replace('/schema.embedded.json','/schema-embedded.json')
    CACHE.mkdir(parents=True,exist_ok=True)
    path=CACHE/(hashlib.sha256(url.encode()).hexdigest()+'.json')
    if not path.exists():
        with urllib.request.urlopen(url,timeout=30) as r:path.write_bytes(r.read())
    return json.loads(path.read_text())


def validate():
    files=[];errors=[]
    for path in (ROOT/'powerbi').rglob('*'):
        if path.suffix not in ('.json','.pbip','.pbir','.pbism'):continue
        value=json.loads(path.read_text())
        if '$schema' not in value:continue
        url=value['$schema'];schema=fetch(url)
        resolver=jsonschema.RefResolver(base_uri=url,referrer=schema,handlers={'https':fetch})
        validator=jsonschema.validators.validator_for(schema)(schema,resolver=resolver)
        for error in validator.iter_errors(value):errors.append(f'{path.relative_to(ROOT)}: {list(error.path)}: {error.message}')
        files.append(path)
    model=json.loads((ROOT/'powerbi/FreshRoute.SemanticModel/model.bim').read_text())
    entities={t['name']:{c['name'] for c in t['columns']}|{m['name'] for m in t.get('measures',[])} for t in model['model']['tables']}
    def walk(node):
        if isinstance(node,dict):
            for kind in ('Column','Measure'):
                if kind in node:
                    item=node[kind];entity=item.get('Expression',{}).get('SourceRef',{}).get('Entity');prop=item.get('Property')
                    if entity and prop not in entities.get(entity,set()):errors.append(f'Unbound field: {entity}.{prop}')
            for v in node.values():walk(v)
        elif isinstance(node,list):
            for v in node:walk(v)
    visuals=list((ROOT/'powerbi/FreshRoute.Report').rglob('visual.json'))
    for path in visuals:walk(json.loads(path.read_text()))
    if errors:raise ValueError('\n'.join(errors))
    print(f'PASS: {len(files)} schema-validated Power BI files; {len(visuals)} visual bindings checked. Desktop rendering is not tested.')


if __name__=='__main__':validate()
