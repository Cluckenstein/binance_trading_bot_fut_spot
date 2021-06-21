#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 11:35:02 2021

@author: maximilianreihn
"""


import requests

def send_text(bot_message, bot_token, bot_chatID):
    
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    
    _ = requests.get(send_text)