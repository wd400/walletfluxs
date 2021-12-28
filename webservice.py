from datetime import datetime
from blacksheep.server import Application
from blacksheep.messages import Response
from pathlib import Path
from blacksheep.server.responses import json
import os
import re
import math
from collections import defaultdict
from dataclasses import dataclass
import sys
from urllib.parse import unquote
icopattern = re.compile("^[A-Za-z 0-9]+$")
import json as js

CATS=20
#gunicorn webservice:app -k uvicorn.workers.UvicornWorker --log-level debug

from blacksheep.server.bindings import FromJSON


@dataclass
class SomethingInput:
    token: str
    start: str
    stop: str
    mini: int
    maxi: int

#gunicorn webservice:app

#uvicorn api:app --port 5000 --reload
app = Application(debug=True)

app.use_cors(
    allow_methods="*",
    allow_origins="*",
    allow_headers="* Authorization",
    max_age=300,
)


def balance2idx(balance,mini,maxi):
    if balance<=10**mini:
        return 0
    if balance>=10**maxi:
        return CATS-1
    return math.floor((CATS-1) * (math.log10( balance)-mini)/(maxi-mini) )

def legend(idx,mini,maxi,decimals):
    if idx==0:
        return {
    'bsup':10**(mini + (maxi-mini)/CATS - decimals),
    'binf': '0',
    }
    if idx==CATS-1:
        return {
    'bsup':'+inf',
    'binf': 10**(maxi - (maxi-mini)/CATS -decimals),
    }

    return {
    'bsup':10**(mini + (idx+1)*(maxi-mini)/CATS -decimals),
    'binf': 10**(mini + idx*(maxi-mini)/CATS - decimals),
    }


@app.route("/tokens",methods=['GET'])
async def availableTokens():
    print("ici",file=sys.stderr)
    icopath = Path('data')
    ico = [e.name for e in icopath.iterdir() if e.is_dir()]
    return json({"tokens":ico})

@app.route("/dates/{str:token}",methods=['GET'])
async def availableDates(token:str):
    token=unquote(token)
    print(token)
    if not icopattern.match(token):
        return Response(500)
    dates=[]
    print("là")
    for x in os.listdir(f'data/{token}'):
        if x.endswith(".json"):
            # Prints only text file present in My Folder
            dates.append(int(x[:-5]))
    return json({'dates':sorted(dates)})

@app.route("/data",methods=['POST'])
async def computeFlux(input: FromJSON[SomethingInput]):
    data=input.value
    if type(data.token)!=str or not icopattern.match(data.token):
        return Response(500)
    token=data.token
    start=int(data.start)
    stop=int(data.stop)
    
    
    


    with  open(f'data/{token}/{start}.json') as fstart:
        dictBefore=js.loads(fstart.read())
    
    with  open(f'data/{token}/{stop}.json') as fstop:
        dictAfter=js.loads(fstop.read())
    
    histBefore=[0 for _ in range(CATS)]
    histAfter=[0 for _ in range(CATS)]
    newAfter=[0 for _ in range(CATS)]
    supply=dictBefore['supply']
    decimals=dictBefore['decimals']

    mini=int(data.mini)+decimals
    maxi=int(data.maxi)+decimals

    if supply<10**maxi:
        maxi=math.log10(supply)
   
  #  flux=[[0 for _ in range(CATS)] for _ in range(CATS)]
    flux=defaultdict(lambda :defaultdict(lambda :0))
    for addressBefore in dictBefore['holders']:
        idxBefore=balance2idx(dictBefore['holders'][addressBefore],mini,maxi)
        
        histBefore[idxBefore]+=1
        if addressBefore not in dictAfter['holders']:
            idxAfter=0
        else:
            idxAfter=balance2idx(dictAfter['holders'][addressBefore],mini,maxi)
            dictAfter['holders'].pop(addressBefore)
        
        histAfter[idxAfter]+=1
        flux[idxBefore][idxAfter]+=1
        

        

    """
    for i in range(CATS):
        total=histBefore[i]
        if total==0:
            continue
        for j in range(CATS):
            flux[i][j]/=total
    """


    for remaningAddress in dictAfter['holders']:
        idx=balance2idx(dictAfter['holders'][remaningAddress],mini,maxi)
        newAfter[idx]+=1

  #  print(histBefore)
  #  print(histAfter)
  #  print(newAfter)
  #  print(flux)

    links=[]
    for k1 in flux:
        for k2 in flux[k1]:
            links.append({'source':k1,'target':CATS+k2,'value':flux[k1][k2]})
    return json({
        'nodes':[legend(idx,mini,maxi,decimals) for idx in range(CATS)]*2,
        'links':links,
        'supply':supply
    })

