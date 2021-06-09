#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 11:35:02 2021

@author: maximilianreihn
"""

import telegram_send

def send_text(message):
    telegram_send.send(messages=[message])