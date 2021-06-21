#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 17:47:14 2021

@author: maximilianreihn
"""


import binance
from binance.client import Client

import json 
import datetime
import pickle


with open('conf/secret.json','rb') as f:
    keys = json.load(f)
     
client = Client(keys['key'], keys['secret'])



pair_list = ['RSRUSDT', 'LINKUSDT', 'BTCUSDT', 'ETHUSDT']


coin_hist = {}

for pair in pair_list:
    print(pair)
    history_spot = []
    history_fut = []
    date = None
    for month in [6]:#[4,5,6]:
        if month == 4:
            amount = 30
        elif month == 5:
            amount = 31
        elif month == 6:
            amount = 19
        for j in range(14, amount):
            
            day = j
            start = str(datetime.datetime(2021, month, day, 0, 0, 0, 0)).replace(" ", "T")
            end = str(datetime.datetime(2021, month, day+1, 0, 0, 0, 0)).replace(" ", "T")
           
            hist_spot = client.get_historical_klines(symbol=pair, interval = Client.KLINE_INTERVAL_1MINUTE,
                                                      start_str = start, end_str = end, limit = 1000, klines_type = binance.enums.HistoricalKlinesType.SPOT)
            
            hist_fut = client.get_historical_klines(symbol=pair, interval = Client.KLINE_INTERVAL_1MINUTE,
                                                    start_str = start, end_str = end, limit = 1000, klines_type = binance.enums.HistoricalKlinesType.FUTURES)
            
  
            history_spot.extend(hist_spot)
            history_fut.extend(hist_fut)

                

    coin_hist[pair] = {'fut':history_fut, 'spot':history_spot}
    
    
with open('data/history_14-19_6'+str(pair_list)+'.pickle', 'wb') as handle:
    pickle.dump(coin_hist, handle, protocol=pickle.HIGHEST_PROTOCOL)