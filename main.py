#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  6 17:11:29 2021

@author: maximilianreihn
"""

import json 
import worker_bin_api as api


with open('secret.json','rb') as f:
    keys = json.load(f)
    
with open('telegram_secret.json','rb') as f:
    tele_keys = json.load(f)
    
bot_token = tele_keys['secret']
bot_id = str(tele_keys['id'])
    

list_coin = ['RSRUSDT', 'LINKUSDT', 'BTCUSDT', 'ETHUSDT']



trading_bot = api.live_bot(keys['key'], keys['secret'], bot_token, bot_id)

trading_bot.set_live(999999999)


#TESTER

"""
list_coin = ['RSRUSDT']

trading_bot = api.live_bot(keys['key'], keys['secret'], bot_token, bot_id,
                             look_back = 10,
                             mini_ine = 0,
                             ine_limit_look_back = 0.01,
                             ine_limit = 0.0001,
                             take_profit = 0.05,
                             stop_loss = -0.25,
                             window_length = 720,
                             symbols = list_coin,
                             position_size = 6.0,)

trading_bot.set_live(999999999)
"""