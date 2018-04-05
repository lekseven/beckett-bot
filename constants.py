# -*- coding: utf8 -*-
import os
import sys
import discord
import string

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')

if not DISCORD_TOKEN:
    print('Config var DISCORD_TOKEN is not defined.')
    sys.exit()

VTM_SERVER_ID = os.environ.get('VTM_SERVER_ID')

if not VTM_SERVER_ID:
    print('Config var VTM_SERVER_ID is not defined.')
    sys.exit()

WELCOME_CHANNEL_ID = os.environ.get('WELCOME_CHANNEL_ID')

if not WELCOME_CHANNEL_ID:
    print('Config var WELCOME_CHANNEL_ID is not defined.')
    sys.exit()

client = discord.Client()

prince_id = '109004244689907712'
beckett_id = '419678772896333824'

superusers = {'119762429969301504',  # Rainfall
              '95525404592316416',  # Манф
              '414384012568690688',  # Kuro
              '203539589284102144',  # Magdavius
              prince_id}

beckett_names = {'беккет', 'бэккет', '419678772896333824', 'beckett'}
channels = {}
silent_channels = {}
ignore_channels = {}


punct2space = str.maketrans(string.punctuation, ' ' * len(string.punctuation))  # for translate
free_cmds = {'roll','help','ignore'}
