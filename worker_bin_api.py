#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  6 17:11:30 2021

@author: maximilianreihn
"""


import binance
from binance.client import Client

import sys
import os
import json 
import datetime
import telegram_bot_bin as bot
import time 
import numpy as np



class live_bot(object):
    
    def __init__(self, client,
                 look_back = 15,
                 mini_ine = 10,
                 ine_limit_look_back = 0.01,
                 ine_limit = 0.05,
                 take_profit = 0.05,
                 stop_loss = -0.25,
                 window_length = 720,
                 symbols = ['RSRUSDT', 'LINKUSDT', 'BTCUSDT', 'ETHUSDT'],
                 position_size = 10.0,
                 leverage = 3):
        
        # best [15, 10, 0.01, 0.05, 0.05, 720] @ [look_back, mini_ine , ine_limit_look_back ,ine_limit ,take_profit ,window_length]

        self.client = client
        
        self.look_back = look_back
        
        self.mini_ine = mini_ine
        
        self.ine_limit_look_back = ine_limit_look_back
        
        self.ine_limit = ine_limit
        
        self.take_profit = take_profit
        
        self.stop_loss = stop_loss
        
        self.window_length = float(window_length)
        
        self.symbols = symbols
        
        self.position_size = position_size #in USDT
        
        self.is_open_orders = {k: False for k in symbols}
        
        self.info_open_orders = {k: None for k in symbols}
        
        self.precision ={}
        
        self.keep_running = True
        
        info = self.client.futures_exchange_info()['symbols']
        
        for pair in self.symbols:
            pair_info = [k for k in info if k['symbol']==pair][0]
            self.precision[pair] = {'price': pair_info['pricePrecision'], 'quantity': pair_info['quantityPrecision']}
            
        

        for pair in self.symbols:
            try:
                self.adjust_leverage(pair, lev = leverage)
            except:
                None
            try:
                self.adjust_tye(pair)
            except:
                None

        
        
    def set_live(self, live_minutes):
        
        message = 'INFORMATION\n'
        message += 'Trading Bot is live with the following settings\n'
        message += 'Live for %i \n'%(live_minutes)
        message += 'Assets watched %s \n'%(str(self.symbols)[1:-1])
        message += 'Positions size $%.2f \n'%(self.position_size)
        message += 'Take profit @ %.3f %%\n'%(self.take_profit*100)
        message += 'Ineff. limit @ %.3f %%\n'%(self.ine_limit*100)
        message += 'Timestamp @ %s \n'%(str(datetime.datetime.now())[:-7])
        bot.send_text(message)
        
             
        starting = time.time()
        old = 0
        while (time.time()-starting)/60 < live_minutes and self.keep_running:
            
            if (time.time()-old) >= 300:
                print('Running for %.2f minutes'%((time.time()-starting)/60))
                old = time.time()
            
            try:
                self.check_open_orders()
            
                spot_resposne = abs(time.time() - self.client.get_server_time()['serverTime']/1000)
                fut_response = abs(time.time() - self.client.futures_coin_time()['serverTime']/1000)
                
                if spot_resposne + fut_response < 2.0:
                
                    for pair in self.symbols:

                        if not self.is_open_orders[pair]:
    
                            history_spot = self.client.get_klines(symbol = pair, interval = Client.KLINE_INTERVAL_1MINUTE, limit = self.look_back)
                            
                            history_fut = self.client.futures_klines(symbol = pair, interval = Client.KLINE_INTERVAL_1MINUTE, limit = self.look_back)
                            
            
                            if sum([float(history_spot[max([-p, -len(history_spot)])][1])/float(history_fut[max([-p,-len(history_fut)])][1]) - 1  > self.ine_limit_look_back for p in range(1,min([len(history_spot), len(history_fut)]))]) >= self.mini_ine:
                                                                   
                                recent_spot =  self.client.get_recent_trades(symbol=pair, limit = 10)
                                recent_fut = self.client.futures_recent_trades(symbol = pair, limit = 10)
                                
                                mark_spot = sum([float(k['price']) for k in recent_spot]) / 10 
                                mark_fut = sum([float(k['price']) for k in recent_fut]) / 10 
                                
                                diff = mark_spot/ mark_fut -1
                                
                                if diff > self.ine_limit:                           
                                    # buy future long leveraged 
                                    # types ['LIMIT', 'MARKET', 'STOP', 'STOP_MARKET', 'TAKE_PROFIT', 'TAKE_PROFIT_MARKET', 'TRAILING_STOP_MARKET']
                                    
                                    quantity = np.round(self.position_size / mark_fut, self.precision[pair]['quantity'])
                                    print(quantity)
                                    
                                    #buy leveraged pair 
                                    buy_order_response = self.client.futures_create_order(symbol=pair, side='BUY', type='MARKET', quantity = quantity)
                                    
                                    open_timestamp = buy_order_response['updateTime']/1000
                                    
                                    # get position infomartion 
                                    entry_price = -1.
                                    while entry_price <= 0.00000001:
                                        open_positions =  self.client.futures_position_information()
                                        
                                        opened_pos = [k for k in open_positions if k['symbol']==pair][0]
                                        entry_price = float(opened_pos['entryPrice'])
                                        
                                        quantity = float(opened_pos['positionAmt'])
                                    
                                    
                                    self.info_open_orders[pair] = {'entry_price': entry_price,
                                                                   'open_time': open_timestamp,
                                                                   'quantity': quantity}
                                    
                                    #take profit market sell order 
                                    self.client.futures_create_order(symbol=pair, side='SELL', type='TAKE_PROFIT_MARKET', timeInForce='GTC', stopPrice= np.round(entry_price * (self.take_profit + 1), self.precision[pair]['price']),  quantity=quantity, reduceOnly = 'true')
                                    
                                    #stop loss market sell order at defined level 
                                    self.client.futures_create_order(symbol=pair, side='SELL', type='STOP_MARKET', timeInForce='GTC', stopPrice= np.round(entry_price * (self.stop_loss + 1), self.precision[pair]['price']), quantity=quantity, reduceOnly = 'true')
                                    
                                    message = 'INFORMATION\n'
                                    message += 'Position opened for %s \n'%(pair)
                                    message += 'Notional amount $ %s \n'%(str(np.round(float(opened_pos['notional']), 2)))
                                    message += 'Ineff. difference %.3f \n'%(diff*100)
                                    message += 'Opened @ %.5f \n'%(entry_price)
                                    message += 'Take profit order @ %.5f \n'%(entry_price * (self.take_profit + 1))
                                    message += 'Timestamp @ %s \n'%(str(datetime.datetime.fromtimestamp(open_timestamp)))
                                    bot.send_text(message)
                                    
                                    self.is_open_orders[pair] = True
                                    
                                    time.sleep(10)
                                    
                else:
                    message = 'INFORMATION\n'%(pair)
                    message += 'Binance servers are not responding in time'
                    bot.send_text(message)
                    
                
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print(exc_type, exc_tb.tb_lineno)
                
                message = 'ATTENTION REQUIRED\n'
                message += 'There was a problem it raised is\n\n'
                message += str(exc_type) +'\n'
                message += 'Line %s \n'%(str(exc_tb.tb_lineno)) 
                bot.send_text(message)
                
                self.keep_running = False
                
                                

    
        
    def check_open_orders(self):
        
        open_positions =  self.client.futures_position_information()
        
        for pair in self.symbols:
            
            opened_pos = [k for k in open_positions if k['symbol']==pair][0]
            pos_quantity = np.round(float(opened_pos['positionAmt']), self.precision[pair]['quantity'])
            
            if self.is_open_orders[pair] and pos_quantity<0.000000001:
                message = 'INFORMATION\n'
                message += 'Position closed after Take Profit for %s \n'%(pair)
                message += 'Timestamp @ %s \n'%(str(datetime.datetime.now()))
                bot.send_text(message)
                
                self.is_open_orders[pair] = False
                self.info_open_orders[pair] = None
                
                

            elif self.is_open_orders[pair] or pos_quantity > 0.000000001:
                if (time.time() - self.info_open_orders[pair]['open_time']) / 60 >= self.window_length: #if position is open longer than defined window close it at market 
                    
                    # self.client.futures_create_order(symbol=pair, side='SELL', type='MARKET', quantity=max([self.info_open_orders[pair]['quantity'],pos_quantity]), reduceOnly = 'true')
                    
                    self.is_open_orders[pair] = False
                    self.info_open_orders[pair] = None
                    
                    recent_fut = self.client.futures_recent_trades(symbol = pair, limit = 10)
                    mark_fut = sum([float(k['price']) for k in recent_fut]) / 10 
                    
                    message = 'INFORMATION\n'%(pair)
                    message += 'Position closed after timeout for %s \n'%(pair)
                    message += 'Closed @ %.5f \n'%(mark_fut)
                    message += 'PL is @ %.5f %% \n'%(100* (mark_fut/self.info_open_orders[pair]['entry_price']-1))
                    message += 'Timestamp @ %s \n'%(str(datetime.datetime.now()))
                    bot.send_text(message)
                
                

    def adjust_leverage(self, symbol, lev = 5):
        _ = self.client.futures_change_leverage(symbol=symbol, leverage=lev)
    
    def adjust_type(self, symbol):
        _ = self.client.futures_change_margin_type(symbol=symbol, marginType='ISOLATED')