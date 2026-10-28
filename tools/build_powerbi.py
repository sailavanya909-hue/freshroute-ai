"""Generate an editable PBIP/PBIR report with a self-contained snapshot model.

JSON schema validation is separate from Windows Power BI rendering validation.
"""
import json
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PBI=ROOT/'powerbi'
REPORT=PBI/'FreshRoute.Report'
MODEL=PBI/'FreshRoute.SemanticModel'
BASE='https://developer.microsoft.com/json-schemas/fabric/item/report/'


def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2)+'\n')


def mliteral(value):
    if isinstance(value,bool):return str(value).lower()
    if isinstance(value,(int,float)):return str(value)
    if isinstance(value,date):return f'#date({value.year},{value.month},{value.day})'
    return '"'+str(value).replace('"','""')+'"'


def mtable(records,types):
    header=', '.join(f'{k}={t}' for k,t in types.items())
    rows=',\n'.join('{'+','.join(mliteral(date.fromisoformat(r[k]) if types[k]=='date' else r[k]) for k in types)+'}' for r in records)
    return f'#table(type table [{header}], {{\n{rows}\n}})'


def table(name,records,types,source=None):
    dtype={'text':'string','number':'double','Int64.Type':'int64','date':'dateTime'}
    columns=[dict(name=k,dataType=dtype[t],sourceColumn=k,summarizeBy='none',**({'formatString':'yyyy-MM-dd'} if t=='date' else {})) for k,t in types.items()]
    for c in columns:
        if c['name']=='source_url':c['dataCategory']='WebUrl'
    return dict(name=name,columns=columns,partitions=[dict(name=name,mode='import',source=dict(type='m',expression=source or mtable(records,types)))])


def field(table,column,measure=False):
    kind='Measure' if measure else 'Column'
    return {'field':{kind:{'Expression':{'SourceRef':{'Entity':table}},'Property':column}},'queryRef':table+'.'+column,'nativeQueryRef':column}


def literal(value):
    if isinstance(value,bool):value=str(value).lower()
    elif isinstance(value,str):value="'"+value.replace("'","''")+"'"
    else:value=str(value)+'D'
    return {'expr':{'Literal':{'Value':value}}}


def visual(page,name,kind,title,x,y,w,h,roles,objects=None):
    conf=dict(visualType=kind,query={'queryState':{role:{'projections':items} for role,items in roles.items()}},
        visualContainerObjects={'title':[{'properties':{'show':literal(True),'text':literal(title),'fontSize':literal(13)}}],
        'background':[{'properties':{'show':literal(True),'color':{'solid':{'color':literal('#FFFFFF')}},'transparency':literal(0)}}]},drillFilterOtherVisuals=True)
    if objects:conf['objects']=objects
    if kind=='slicer' and name in ('date','size','market'):
        conf['syncGroup']={'groupName':'FreshRoute_'+name,'fieldChanges':True,'filterChanges':True}
    save(REPORT/f'definition/pages/{page}/visuals/{name}/visual.json',{
        '$schema':BASE+'definition/visualContainer/2.1.0/schema.json','name':name,
        'position':dict(x=x,y=y,z=0,height=h,width=w,tabOrder=0),'visual':conf})


def build():
    data=json.loads((ROOT/'data/demo.json').read_text())
    route={r['market']:r for r in data['routes']}
    records=[{**q,**{k:v for k,v in route[q['market']].items() if k!='data_kind'}} for q in data['quotes']]
    types={'quote_id':'text','report_date':'date','market':'text','commodity':'text','variety':'text','origin':'text','grade':'text','size_count':'Int64.Type','low_package':'number','high_package':'number','midpoint_usd_lb':'number','source_url':'text','freight_usd_lb':'number','shrink':'number','capacity_lb':'number','transit_hours':'number'}
    snapshot=mtable(records,types)
    select='{'+','.join('"'+k+'"' for k in types)+'}'
    source='let\n Snapshot = '+snapshot+',\n Source = if UseMySQL then MySQL.Database(MySQLServer, "freshroute", [ReturnSingleDatabase=true]){[Schema="freshroute",Item="terminal_sourcing_base"]}[Data] else Snapshot,\n Selected=Table.SelectColumns(Source,'+select+')\nin Selected'
    quotes=table('Quotes',records,types,source)
    measures={
      'Selected Date':'SELECTEDVALUE(Quotes[report_date], DATE(2026,10,26))',
      'Selected Size':'SELECTEDVALUE(Quotes[size_count],80)',
      'Purchased lb':'SELECTEDVALUE(Quantity[Value],10000)',
      'Sell USD per lb':'SELECTEDVALUE(SellPrice[Value],1.05)',
      'Freight Delta':'SELECTEDVALUE(FreightDelta[Value],0)',
      'Shrink Delta':'SELECTEDVALUE(ShrinkDelta[Value],0)',
      'Selection Valid':'(NOT ISFILTERED(Quotes[report_date]) || HASONEVALUE(Quotes[report_date])) && (NOT ISFILTERED(Quotes[size_count]) || HASONEVALUE(Quotes[size_count]))',
      'Selection Label':'"USDA " & FORMAT([Selected Date],"yyyy-MM-dd") & " | " & FORMAT([Selected Size],"0") & " count | freight / shrink assumed"',
      'Quoted Midpoint USD per lb':'''VAR D=[Selected Date] VAR S=[Selected Size]
VAR R=FILTER(Quotes,Quotes[report_date]=D && Quotes[size_count]=S)
RETURN IF([Selection Valid] && COUNTROWS(R)=1,MAXX(R,Quotes[midpoint_usd_lb]))''',
      'Scenario Delivered USD per lb':'''VAR D=[Selected Date] VAR S=[Selected Size] VAR Q=[Purchased lb]
VAR R=FILTER(Quotes,Quotes[report_date]=D && Quotes[size_count]=S)
VAR F=MAXX(R,Quotes[freight_usd_lb])+[Freight Delta]
VAR L=MAXX(R,Quotes[shrink])+[Shrink Delta]
RETURN IF([Selection Valid] && COUNTROWS(R)=1 && Q<=MAXX(R,Quotes[capacity_lb]) && F>=0 && L>=0 && L<1,
DIVIDE(MAXX(R,Quotes[midpoint_usd_lb])+F,1-L))''',
      'Scenario Contribution USD':'''VAR D=[Selected Date] VAR S=[Selected Size] VAR Q=[Purchased lb]
VAR R=FILTER(Quotes,Quotes[report_date]=D && Quotes[size_count]=S)
VAR F=MAXX(R,Quotes[freight_usd_lb])+[Freight Delta]
VAR L=MAXX(R,Quotes[shrink])+[Shrink Delta]
RETURN IF(NOT ISBLANK([Scenario Delivered USD per lb]),Q*((1-L)*[Sell USD per lb]-MAXX(R,Quotes[midpoint_usd_lb])-F))''',
      'Best Delivered USD per lb':'MINX(VALUES(Quotes[market]),CALCULATE([Scenario Delivered USD per lb]))',
      'Best Market':'''VAR R=FILTER(ADDCOLUMNS(VALUES(Quotes[market]),"Cost",CALCULATE([Scenario Delivered USD per lb])),NOT ISBLANK([Cost]))
RETURN CONCATENATEX(TOPN(1,R,[Cost],ASC,Quotes[market],ASC),Quotes[market],", ")''',
      'Best Contribution USD':'''VAR R=FILTER(ADDCOLUMNS(VALUES(Quotes[market]),"Cost",CALCULATE([Scenario Delivered USD per lb])),NOT ISBLANK([Cost]))
RETURN MAXX(TOPN(1,R,[Cost],ASC,Quotes[market],ASC),CALCULATE([Scenario Contribution USD]))''',
      'Report Age Days':'DATEDIFF(MAX(Quotes[report_date]),TODAY(),DAY)',
      'Snapshot Observations':'COUNTROWS(Quotes)',
    }
    quotes['measures']=[dict(name=k,expression=v,**({'formatString':'$#,##0.0000'} if 'per lb' in k else {'formatString':'$#,##0.00'} if k.endswith('USD') else {})) for k,v in measures.items()]
    tables=[quotes]
    for name,values in [('Quantity',[5000,10000,15000,20000]),('SellPrice',[.9,1,1.05,1.1,1.2]),('FreightDelta',[0,.03,.06,.09,.12,.15]),('ShrinkDelta',[0,.03,.06,.09,.12,.15])]:
        tables.append(table(name,[{'Value':v} for v in values],{'Value':'number'}))
    inventory=table('DemoInventory',data['lots'],{'lot_id':'text','warehouse':'text','quantity_lb':'number','remaining_days':'Int64.Type','purchase_usd_lb':'number','sell_usd_lb':'number','data_kind':'text'})
    inventory['measures']=[dict(name='Hold Revenue USD',expression='SUMX(DemoInventory,DemoInventory[quantity_lb]*DemoInventory[sell_usd_lb]*0.75)',formatString='$#,##0'),dict(name='Markdown Revenue USD',expression='SUMX(DemoInventory,DemoInventory[quantity_lb]*DemoInventory[sell_usd_lb]*0.85)',formatString='$#,##0')]
    tables.append(inventory)
    model=dict(name='FreshRoute',compatibilityLevel=1601,model=dict(culture='en-US',defaultPowerBIDataSourceVersion='powerBI_V3',tables=tables,
        expressions=[dict(name='UseMySQL',kind='m',expression='false meta [IsParameterQuery=true, Type="Logical", IsParameterQueryRequired=true]'),dict(name='MySQLServer',kind='m',expression='"localhost" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]')]))
    save(MODEL/'model.bim',model)
    save(MODEL/'definition.pbism',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json','version':'1.0','settings':{}})
    save(PBI/'FreshRoute.pbip',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json','version':'1.0','artifacts':[{'report':{'path':'FreshRoute.Report'}}],'settings':{'enableAutoRecovery':True}})
    save(REPORT/'definition.pbir',{'$schema':BASE+'definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':'../FreshRoute.SemanticModel'}}})
    save(REPORT/'definition/version.json',{'$schema':BASE+'definition/versionMetadata/1.0.0/schema.json','version':'2.0.0'})
    save(REPORT/'definition/report.json',{'$schema':BASE+'definition/report/2.0.0/schema.json','themeCollection':{'baseTheme':{'name':'CY24SU06','reportVersionAtImport':'5.55','type':'SharedResources'}},'settings':{'useStylableVisualContainerHeader':True,'exportDataMode':'AllowSummarized','defaultDrillFilterOtherVisuals':True}})
    pages=[('DecisionDesk','Sourcing decision desk'),('ScenarioLab','Freight & shrink lab'),('Inventory','Inventory rescue (simulated)'),('Evidence','Source evidence')]
    save(REPORT/'definition/pages/pages.json',{'$schema':BASE+'definition/pagesMetadata/1.0.0/schema.json','pageOrder':[p[0] for p in pages],'activePageName':'DecisionDesk'})
    for name,label in pages:
        save(REPORT/f'definition/pages/{name}/page.json',{'$schema':BASE+'definition/page/2.0.0/schema.json','name':name,'displayName':label,'displayOption':'FitToPage','height':900,'width':1440})
    def v(p,n,k,t,x,y,w,h,roles):visual(p,n,k,t,x,y,w,h,roles)
    def c(prop):return field('Quotes',prop)
    def m(prop):return field('Quotes',prop,True)
    def slicer(p,n,t,x,y,w,entity,column):v(p,n,'slicer',t,x,y,w,100,{'Values':[field(entity,column)]})
    for p in ['DecisionDesk','ScenarioLab']:
        v(p,'context','card','Selected context (no selection defaults to Oct 26, 80 count)',25,15,1390,85,{'Values':[m('Selection Label')]})
        slicer(p,'date','Report date · select one',25,110,320,'Quotes','report_date')
        slicer(p,'size','Carton count · select one',365,110,280,'Quotes','size_count')
        slicer(p,'market','Market · optional comparison filter',665,110,350,'Quotes','market')
    v('DecisionDesk','bestmarket','card','Best feasible sourcing market',25,235,440,125,{'Values':[m('Best Market')]})
    v('DecisionDesk','cost','card','Best delivered cost (USD / saleable lb)',490,235,440,125,{'Values':[m('Best Delivered USD per lb')]})
    v('DecisionDesk','contribution','card','Modeled contribution (USD)',955,235,460,125,{'Values':[m('Best Contribution USD')]})
    v('DecisionDesk','costchart','clusteredBarChart','Quoted midpoint versus scenario delivered cost (USD/lb)',25,385,1390,235,{'Category':[c('market')],'Y':[m('Quoted Midpoint USD per lb'),m('Scenario Delivered USD per lb')]})
    v('DecisionDesk','shortlist','tableEx','Same-date, same-size sourcing shortlist · select a market to cross-filter',25,645,1390,230,{'Values':[c('market'),m('Quoted Midpoint USD per lb'),m('Scenario Delivered USD per lb'),m('Scenario Contribution USD')]})
    slicer('ScenarioLab','qty','Purchased quantity (lb)',25,235,320,'Quantity','Value')
    slicer('ScenarioLab','sell','Selling price (USD/lb)',365,235,320,'SellPrice','Value')
    slicer('ScenarioLab','freight','Extra freight (USD/lb)',705,235,320,'FreightDelta','Value')
    slicer('ScenarioLab','shrink','Extra spoilage (fraction)',1045,235,370,'ShrinkDelta','Value')
    v('ScenarioLab','scenariochart','clusteredBarChart','Contribution by feasible route · all route inputs are assumed',25,355,1390,250,{'Category':[c('market')],'Y':[m('Scenario Contribution USD')]})
    v('ScenarioLab','matrix','pivotTable','Freight × shrink sensitivity · filter to one market',25,630,1390,245,{'Rows':[field('FreightDelta','Value')],'Columns':[field('ShrinkDelta','Value')],'Values':[m('Best Contribution USD')]})
    v('Inventory','lots','tableEx','SIMULATED inventory · hold assumes 25% unsold, markdown assumes 15% discount and all stock sells',25,30,1390,560,{'Values':[field('DemoInventory',x) for x in ['lot_id','warehouse','quantity_lb','remaining_days','data_kind']]+[field('DemoInventory','Hold Revenue USD',True),field('DemoInventory','Markdown Revenue USD',True)]})
    v('Inventory','expiry','clusteredBarChart','Simulated pounds by lot · review shortest remaining shelf life first',25,620,1390,250,{'Category':[field('DemoInventory','lot_id')],'Y':[{'field':{'Aggregation':{'Expression':{'Column':{'Expression':{'SourceRef':{'Entity':'DemoInventory'}},'Property':'quantity_lb'}},'Function':0}},'queryRef':'Sum(DemoInventory.quantity_lb)','nativeQueryRef':'Pounds'}]})
    v('Evidence','observations','card','Selected observations in archived snapshot',25,30,650,120,{'Values':[m('Snapshot Observations')]})
    v('Evidence','age','card','Latest report age in days · not a live feed',700,30,715,120,{'Values':[m('Report Age Days')]})
    v('Evidence','sources','tableEx','USDA overall quote ranges · midpoint is derived; USD per 50 lb carton',25,180,1390,690,{'Values':[c(x) for x in ['report_date','market','size_count','low_package','high_package','grade','origin','source_url','quote_id']]})
    print('Generated Power BI project: 4 pages, 24 visual definitions, synced filters, embedded snapshot + optional MySQL source')


if __name__=='__main__':build()
