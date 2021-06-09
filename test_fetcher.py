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
import time


with open('secret.json','rb') as f:
    keys = json.load(f)
     
client = Client(keys['key'], keys['secret'])

# a = client.get_klines(symbol='RSRUSDT', interval=Client.KLINE_INTERVAL_1MINUTE, limit = 20)

# a3 = client.futures_klines(symbol='RSRUSDT', interval=Client.KLINE_INTERVAL_1MINUTE, limit = 20)

# a4 = client.futures_mark_price(symbol="RSRUSDT")

def adjust_leverage( symbol, lev = 5):
    _ = client.futures_change_leverage(symbol=symbol, leverage=lev)

def adjust_type(symbol):
    _ = client.futures_change_margin_type(symbol=symbol, marginType='ISOLATED')



# b = time.time()

# print(b-a[-1][0]/1000)
# print(b-a2[-1].openTime/1000)
# print()
# print(max([float(a[k][1])- float(a2[k].open) for k in range(len(a2))]))
# print(datetime.datetime.fromtimestamp(a2[-1].openTime/1000), " ", datetime.datetime.fromtimestamp(a2[-1].openTime/1000) )
# print( float(a2[-1].open), float(a[-1][1]))


# pair_list = ['RSRUSDT', 'LINKUSDT', 'BTCUSDT', 'ETHUSDT']
# window_length = 120

# coin_hist = {}

# for pair in pair_list:
#     print(pair)
#     history_spot = []
#     history_fut = []
#     date = None
#     for month in [4,5,6]:
#         if month == 4:
#             amount = 30
#         elif month == 5:
#             amount = 31
#         elif month == 6:
#             amount = 5
#         for j in range(1, amount):
            
#             day = j
#             start = str(datetime.datetime(2021, month, day, 0, 0, 0, 0)).replace(" ", "T")
#             end = str(datetime.datetime(2021, month, day+1, 0, 0, 0, 0)).replace(" ", "T")
           
#             hist_spot = client.get_historical_klines(symbol=pair, interval = Client.KLINE_INTERVAL_1MINUTE,
#                                                      start_str = start, end_str = end, limit = 1000, klines_type = binance.enums.HistoricalKlinesType.SPOT)
            
#             hist_fut = client.get_historical_klines(symbol=pair, interval = Client.KLINE_INTERVAL_1MINUTE,
#                                                     start_str = start, end_str = end, limit = 1000, klines_type = binance.enums.HistoricalKlinesType.FUTURES)
            
  
#             history_spot.extend(hist_spot)
#             history_fut.extend(hist_fut)

                

#     coin_hist[pair] = {'fut':history_fut, 'spot':history_spot}
    
# with open('history_4_5_6'+str(pair_list)+'.pickle', 'wb') as handle:
#     pickle.dump(coin_hist, handle, protocol=pickle.HIGHEST_PROTOCOL)