#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  6 17:11:28 2021

@author: maximilianreihn
"""

import matplotlib.pyplot as plt 
import pickle
import numpy as np 


pair_list = ['RSRUSDT', 'LINKUSDT', 'BTCUSDT', 'ETHUSDT']
    
with open('history_4_5_6'+str(pair_list)+'.pickle', 'rb') as handle:
    coin_hist = pickle.load(handle)

look_back = 15 #min of time in which minimum of 'mini_ine' must be over 'ine_limit'
mini_ine = 10
ine_limit_look_back = 0.01
ine_limit = 0.05
take_profit = 0.05
window_length = 720

# best [15, 10, 0.01, 0.05, 0.05, 720] @ [look_back, mini_ine , ine_limit_look_back ,ine_limit ,take_profit ,window_length]


# combi_list = []
# zahl = 0
# for ine_limit in [ 0.01, 0.05]:
#     for take_profit in [0.05,  0.10, 0.15 ]:
#         for window_length in [180, 360, 720, 1440]:
            # print(zahl)
            # zahl += 1
endi = []


for pair in pair_list:
    minutes_observed = min([len(coin_hist[pair]['spot']), len(coin_hist[pair]['fut'])])
    # print(pair)

    end_of_trade = 0
    for i in range(minutes_observed):
        if i < end_of_trade:
            continue
           
        open_spot = float(coin_hist[pair]['spot'][i][1])
        
        open_fut = float(coin_hist[pair]['fut'][i][1])
        

        diff = open_spot/ open_fut -1
        
        
        if sum([float(coin_hist[pair]['spot'][max([i-p,0])][1])/float(coin_hist[pair]['fut'][max([i-p,0])][1]) -1  > ine_limit_look_back for p in range(1,look_back)]) >=mini_ine:
            if diff > ine_limit:
                # buy future long leveraged 
                minute_returns = [float(coin_hist[pair]['fut'][min([i+k,minutes_observed-1])][1])/open_fut - 1  for k in range(1,window_length)]

                try:
                    indi = min([minute_returns.index(k) for k in minute_returns if k >= take_profit])
                except:
                    indi = len(minute_returns) - 1
                    
                end_of_trade = indi + i 
                    
                end_ret = minute_returns[indi]

                endi.append(end_ret*100)
                
                    
# print('avg. ',sum(endi)/len(endi))
# print('max. ',max(endi))
# print('min. ',min(endi))
# print('trades  ',len(endi))

# kombi = [look_back, mini_ine , ine_limit_look_back ,ine_limit ,take_profit ,window_length]

# combi_list.append((endi, str(kombi)))
            
# with open('backtest_returns.pickle', 'wb') as handle:
#     pickle.dump(combi_list, handle, protocol=pickle.HIGHEST_PROTOCOL)
                
    
# ploter
#############
# returns = []
# var = []

# with open('backtest_returns_1.pickle', 'rb') as handle:
#     hist = pickle.load(handle)
    
# with open('backtest_returns_2.pickle', 'rb') as handle:
#     hist.extend(pickle.load(handle))
    
    
# for komb in hist:
#     returns.append(sum(komb[0])/len(komb[0]))
#     var.append(np.var(komb[0]))
    
# plt.plot(returns,var,'.')

'''
[
  [
    1499040000000,      // Open time
    "0.01634790",       // Open
    "0.80000000",       // High
    "0.01575800",       // Low
    "0.01577100",       // Close
    "148976.11427815",  // Volume
    1499644799999,      // Close time
    "2434.19055334",    // Quote asset volume
    308,                // Number of trades
    "1756.87402397",    // Taker buy base asset volume
    "28.46694368",      // Taker buy quote asset volume
    "17928899.62484339" // Ignore.
  ]
]
'''
    

'''
[
  [
    1499040000000,      // Open time
    "0.01634790",       // Open
    "0.80000000",       // High
    "0.01575800",       // Low
    "0.01577100",       // Close
    "148976.11427815",  // Volume
    1499644799999,      // Close time
    "2434.19055334",    // Quote asset volume
    308,                // Number of trades
    "1756.87402397",    // Taker buy base asset volume
    "28.46694368",      // Taker buy quote asset volume
    "17928899.62484339" // Ignore.
  ]
]
'''