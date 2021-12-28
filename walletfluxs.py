import requests
import json
import math
import matplotlib.pyplot as plt
from datetime import datetime
import calendar
from random import shuffle
import time
import os

def get_tor_session():
    session = requests.session()
    # Tor uses the 9050 port as the default socks port
    session.proxies = {'http':  'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'}
    return session

# Make a request through the Tor connection
# IP visible through Tor
session = get_tor_session()

def data2dict(data,price):
    wallets=dict()
    for wallet in data['holders']:
        wallets[wallet['address']]=float(wallet['balance'])*price
    return wallets

ecos=['0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',
'0xd533a949740bb3306d119cc777fa900ba034cd52',
'0x1337def16f9b486faed0293eb623dc8395dfe46a',
'0x474021845c4643113458ea4414bdb7fb74a01a77',
'0xbeab712832112bd7664226db7cd025b153d3af55'
]
while True:
    for eco in ecos:
        while True:
            try:
                x = session.get(f'https://ethplorer.io/service/service.php?refresh=holders&data={eco}&page=pageSize=100000000000%26tab%3Dtab-holders%26holders%3D0')
                rawData=json.loads(x.content)
                break
            except:
                time.sleep(60)
        #price=float(rawData['token']['price']['rate']
        price=1
        holders=data2dict(rawData,price)
        print(rawData['token']['name'],len(holders))
        tosave={
        'holders':holders,
        'decimals':int(rawData['token']['decimals']),
        'supply':int(rawData['token']['totalSupply'])
        }

        timestamp = calendar.timegm(datetime.utcnow().utctimetuple())

        if not os.path.exists('data/{}'.format(rawData['token']['name'])):
            os.makedirs('data/{}'.format(rawData['token']['name']))
        with open('data/{}/{}.json'.format(rawData['token']['name'],timestamp),'w+') as f:
            f.write(json.dumps(tosave))
    shuffle(ecos)
    time.sleep(60*60*6)

#1.7340315520471841e+26
#173,403,155.2047184
#$3,000,000,000
# 100_000_000 

