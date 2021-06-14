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
import string



class live_bot(object):
    
    def __init__(self, client_key,
                 client_secret,
                 bot_token,
                 bot_chat_id,
                 look_back = 15,
                 mini_ine = 10,
                 ine_limit_look_back = 0.01,
                 ine_limit = 0.035,
                 take_profit = 0.05,
                 stop_loss = -0.20,
                 window_length = 720,
                 symbols = ['RSRUSDT', 'LINKUSDT', 'BTCUSDT', 'ETHUSDT', 'DOGEUSDT'],
                 position_size = 15.0,
                 leverage = 4):
        
        # best [15, 10, 0.01, 0.05, 0.05, 720] @ [look_back, mini_ine , ine_limit_look_back ,ine_limit ,take_profit ,window_length]

        self.client_key = client_key

        self.client_secret = client_secret
        
        self.client = Client(self.client_key, self.client_secret)  
        
        self.bot_token = bot_token
        
        self.bot_chat_id = bot_chat_id
        
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
            
        self.leverage = leverage

        for pair in self.symbols:
            try:
                self.adjust_leverage(pair, lev = leverage)
            except:
                None
            try:
                self.adjust_tye(pair)
            except:
                None
                
        alp = string.ascii_uppercase + string.ascii_lowercase + '@#$%&*!?~'
        cur = datetime.datetime.now()
        
        self.bot_id = alp[cur.year-2000] + alp[cur.month] + alp[cur.day] + alp[cur.hour] + alp[cur.minute]
        

        
        
    def set_live(self, live_minutes):
        
        message = 'INFORMATION\n'
        message += 'Trading Bot is live\n'
        message += 'Live for %i min.\n'%(live_minutes)
        message += 'Assets watched %s \n'%(str(self.symbols)[1:-1])
        message += 'Positions size $%.2f \n'%(self.position_size)
        message += 'Leverage %ix\n'%(int(self.leverage)) 
        message += 'Take profit @ %.1f %%\n'%(self.take_profit*100)
        message += 'Ineff. limit @ %.1f %%\n'%(self.ine_limit*100)
        message += 'Timestamp @ %s \n'%(str(datetime.datetime.now())[:-7])
        message += 'Bot ID %s'%(self.bot_id)
        bot.send_text(message, self.bot_token, self.bot_chat_id)
        
        starting = time.time()
        old = 0
        fluct_message = {k:0 for k in self.symbols}
        old_run = 0

        while (time.time()-starting)/60 < live_minutes and self.keep_running:

            if (time.time()-old_run) >= int(180):
                print('running')
                old_run = time.time()
            
            if (time.time()-old) >= int(60*60*8):
                run_min = round((time.time()-starting)/60)
                hours = np.floor(run_min/60)
                days = int(np.floor(hours/24))

                hour=hours%24

                print('Live for %i day(s) %i hours'%(days, hour))
                message = 'INFORMATION\nLive %i day(s) %i hours\n'%(days, hour)
                message += 'Bot ID %s'%(self.bot_id)
                bot.send_text(message, self.bot_token, self.bot_chat_id)
                old = time.time()

                self.reset_client()

            
            try:
                self.check_open_orders() #connection error can occur 
            
                try:
                    spot_resposne = abs(time.time() - self.client.get_server_time()['serverTime']/1000)
                    fut_response = abs(time.time() - self.client.futures_coin_time()['serverTime']/1000)
                except:
                    print('Connection error while getting pings')
                    spot_resposne = 3.0
                    fut_response = 3.0
                    continue
                
                if spot_resposne + fut_response < 2.0:
                
                    for pair in self.symbols:

                        if not self.is_open_orders[pair]:
                            
                            try:
    
                                history_spot = self.client.get_klines(symbol = pair, interval = Client.KLINE_INTERVAL_1MINUTE, limit = int(2*self.look_back)) #connection error can occur 
                                
                                history_fut = self.client.futures_klines(symbol = pair, interval = Client.KLINE_INTERVAL_1MINUTE, limit = int(2*self.look_back)) #connection error can occur 
                                
                            except:
                                print('Connection error while getting klines')
                                continue
  

                            dates_spot = []
                            for spot in history_spot:
                                date = datetime.datetime.fromtimestamp(spot[0]/1000)
                                spot[0] = datetime.datetime(date.year, date.month, date.day, date.hour, date.minute)
                                dates_spot.append(spot[0])
                                
                            
                            dates_fut = []
                            for fut in history_fut:
                                date = datetime.datetime.fromtimestamp(fut[0]/1000)
                                fut[0] = datetime.datetime(date.year, date.month, date.day, date.hour, date.minute)
                                dates_fut.append(fut[0])
                                
                            
                            
                            if max(dates_fut) > max(dates_spot):    
                                print('here fut candles are newer than spot candles')
                                history_spot = [history_spot[-i-1].copy() for i in range(self.look_back)]
                                
                                max_indi_fut = [k for k in history_fut if k[0]<=max(dates_spot)]
                                
                                history_fut = [max_indi_fut[-i-1].copy() for i in range(self.look_back)] 
                            
                            elif max(dates_spot) > max(dates_fut):
                                print('here spot candles are newer than fut candles')
                                history_fut = [history_fut[-i-1].copy() for i in range(self.look_back)]
                                
                                max_indi_spot = [k for k in history_spot if k[0]<=max(dates_fut)]
                                
                                history_spot = [max_indi_spot[-i-1].copy() for i in range(self.look_back)] 
                                
                            elif max(dates_fut) == max(dates_spot):
                                
                                history_spot = [history_spot[-i-1].copy() for i in range(self.look_back)]
                                history_fut = [history_fut[-i-1].copy() for i in range(self.look_back)]
                                 
                            else:
                                print('Some thing went wrong with getting the candles and their datetimes')
                                message = 'ATTENTION REQUIRED\n'
                                message += 'Some thing went wrong with getting the candles and their datetimes\n'
                                message += 'Bot ID %s'%(self.bot_id)
                                bot.send_text(message, self.bot_token, self.bot_chat_id)
                                continue
                            
                            
                            fluctuations_over_limit = [abs(float(history_spot[-p][1])/float(history_fut[-p][1]) - 1) > self.ine_limit_look_back for p in range(1,self.look_back+1)]
                            flucts = sum(fluctuations_over_limit)

                            """
                            if pair == 'RSRUSDT':
                                print([abs(float(history_spot[max([-p, -len(history_spot)])][1])/float(history_fut[max([-p,-len(history_fut)])][1]) - 1)*100 for p in range(1,min_len)])
                                recent_spot =  self.client.get_recent_trades(symbol=pair, limit = 10)
                                recent_fut = self.client.futures_recent_trades(symbol = pair, limit = 10)
                        
                                mark_spot = sum([float(k['price']) for k in recent_spot]) / 10 
                                mark_fut = sum([float(k['price']) for k in recent_fut]) / 10 

                                print(100*(mark_spot/ mark_fut -1))

                            """

                            if flucts > 0 and (time.time()-fluct_message[pair])/60>= 1.:
                                fluct_message[pair] = time.time()
                                print('INFORMATION\nFluctuations occuringr for %s\n%i fluctuation(s) detected\n%i is treshold'%(pair, int(flucts), int(self.mini_ine)))
                                message = 'INFORMATION\nFluctuations occuringr for %s\n%i fluctuation(s) detected\n%i is treshold\n'%(pair, int(flucts), int(self.mini_ine))
                                message += 'Bot ID %s'%(self.bot_id)
                                bot.send_text(message, self.bot_token, self.bot_id)


                            if flucts >= self.mini_ine:
                                                                   
                                recent_spot =  self.client.get_recent_trades(symbol=pair, limit = 10)
                                recent_fut = self.client.futures_recent_trades(symbol = pair, limit = 10)
                        
                                mark_spot = sum([float(k['price']) for k in recent_spot]) / 10 
                                mark_fut = sum([float(k['price']) for k in recent_fut]) / 10 
                                
                                diff = mark_spot/ mark_fut -1
                                
                                if diff > self.ine_limit:                           
                                    # buy future long leveraged 
                                    # types ['LIMIT', 'MARKET', 'STOP', 'STOP_MARKET', 'TAKE_PROFIT', 'TAKE_PROFIT_MARKET', 'TRAILING_STOP_MARKET']                          
                                    quantity = np.round(self.position_size / mark_fut, self.precision[pair]['quantity'])
                                           
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
                                    message += 'Ineff. difference %.3f %%\n'%(diff*100)
                                    message += 'Opened @ %.5f \n'%(entry_price)
                                    message += 'Take profit order @ %.5f \n'%(entry_price * (self.take_profit + 1))
                                    message += 'Stop loss order @ %.5f \n'%(entry_price * (self.stop_loss + 1))
                                    message += 'Timestamp @ %s \n'%(str(datetime.datetime.fromtimestamp(open_timestamp)))
                                    message += 'Bot ID %s'%(self.bot_id)
                                    bot.send_text(message, self.bot_token, self.bot_chat_id)
                                    
                                    self.is_open_orders[pair] = True
                                    
                                    
                                    
                else:
                    message = 'INFORMATION\n'
                    message += 'Binance servers are not responding in time'
                    bot.send_text(message, self.bot_token, self.bot_chat_id)
                    
                
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print(exc_type, exc_tb.tb_lineno)
                
                message = 'ATTENTION REQUIRED\n'
                message += 'There was a problem it raised is\n\n'
                message += str(exc_type) +'\n'
                message += 'Line %s \n'%(str(exc_tb.tb_lineno)) 
                message += 'Bot ID %s'%(self.bot_id)
                bot.send_text(message, self.bot_token, self.bot_chat_id)
                
                self.keep_running = False

        message = 'Turned of after %i days %i hours\n'%(days, hours)
        message += 'Bot ID %s'%(self.bot_id)
        bot.send_text(message, self.bot_token, self.bot_chat_id)
                
                                

    
        
    def check_open_orders(self):
        
        try:
        
            open_positions =  self.client.futures_position_information() #connection error can occur 
            temp_symbols = self.symbols.copy()
        
        except:
            print('Connection error while getting future position info')
            temp_symbols = []

        
        
        for pair in temp_symbols:
            
            opened_pos = [k for k in open_positions if k['symbol']==pair][0]
            pos_quantity = np.round(float(opened_pos['positionAmt']), self.precision[pair]['quantity'])
            
            if self.is_open_orders[pair] and pos_quantity<0.000000001:
                message = 'INFORMATION\n'
                message += 'Position closed after Take Profit for %s \n'%(pair)
                message += 'Timestamp @ %s \n'%(str(datetime.datetime.now()))
                message += 'Bot ID %s'%(self.bot_id)
                bot.send_text(message, self.bot_token, self.bot_chat_id)
                
                self.is_open_orders[pair] = False
                self.info_open_orders[pair] = None
                
                

            elif self.is_open_orders[pair] or pos_quantity > 0.000000001:
                if (time.time() - self.info_open_orders[pair]['open_time']) / 60 >= self.window_length: #if position is open longer than defined window close it at market 
                    
                    # self.client.futures_create_order(symbol=pair, side='SELL', type='MARKET', quantity=max([self.info_open_orders[pair]['quantity'],pos_quantity]), reduceOnly = 'true')
                    
                    self.is_open_orders[pair] = False
                    self.info_open_orders[pair] = None
                    
                    recent_fut = self.client.futures_recent_trades(symbol = pair, limit = 10)
                    mark_fut = sum([float(k['price']) for k in recent_fut]) / 10 
                    
                    message = 'INFORMATION\n'
                    message += 'Position closed after timeout for %s \n'%(pair)
                    message += 'Closed @ %.5f \n'%(mark_fut)
                    message += 'PL is @ %.5f %% \n'%(100* (mark_fut/self.info_open_orders[pair]['entry_price']-1))
                    message += 'Timestamp @ %s \n'%(str(datetime.datetime.now()))
                    message += 'Bot ID %s'%(self.bot_id)
                    bot.send_text(message, self.bot_token, self.bot_chat_id)
                
                
    def reset_client(self):
        self.client = None
        self.client = Client(self.client_key, self.client_secret)   

    def adjust_leverage(self, symbol, lev = 5):
        _ = self.client.futures_change_leverage(symbol=symbol, leverage=lev)
    
    def adjust_type(self, symbol):
        _ = self.client.futures_change_margin_type(symbol=symbol, marginType='ISOLATED')