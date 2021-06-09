#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  6 17:11:29 2021

@author: maximilianreihn
"""

import json 
import worker_bin_api as api
import binance
from binance.client import Client



with open('secret.json','rb') as f:
    keys = json.load(f)
    
client = Client(keys['key'], keys['secret'])    
    
    

list_coin = ['RSRUSDT', 'LINKUSDT', 'BTCUSDT', 'ETHUSDT']

trading_bot = api.live_bot(client)

trading_bot.set_live(99999)
    
    