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

DATABASE_URL = os.environ.get('DATABASE_URL')

client = discord.Client()
server = {} #server

prince_id = '109004244689907712'
beckett_id = '419678772896333824'

superusers = {'414384012568690688',  # Kuro
              '203539589284102144',  # Magdavius
              #'119762429969301504',  # Rainfall
              #'95525404592316416',  # Манф // check by role
              prince_id}

beckett_names = {'беккет', 'бэккет', '419678772896333824', 'beckett'}
channels = {}
silent_channels = {}
ignore_channels = {}


punct2space = str.maketrans(string.punctuation, ' ' * len(string.punctuation))  # for translate
free_cmds = {'roll','help','ignore'}

roles = {'Prince': '398223824514056202',
         'Sheriff': '398243225116213310',
         'Scourge': '420621473036632064',
         'Seneschal': '398244393003384843',
         'Harpy': '419657934293827593',
         'Primogens and Emissary': '417776802535047178',
         'Malkavian': '398972693480996886',
         'Toreador': '398974249659924480',
         'Brujah': '398974429012426762',
         'Ventrue': '399173942033776640',
         'Nosferatu': '399181594356613134',
         'Gangrel': '399187455334547466',
         'Tremere': '399189123123904512',
         'Ravnos': '398974681782157312',
         'Followers of Set': '399313856020611074',
         'Assamite': '402130684128395264',
         'Giovanni': '402141570389770262',
         'Tzimisce': '398971806695817219',
         'Lasombra': '398973052475408389',
         'Noble Pander': '415642642597019658',
         'Cappadocian': '421278030372012043',
         'Lasombra Antitribu': '420599142218465292',
         'New World Order': '420327469371883520',
         'Sabbat': '422166674528272384',
         'Anarch': '423408828097363978',
}

clan_names = {'Malkavian', 'Toreador', 'Brujah', 'Ventrue', 'Nosferatu', 'Gangrel', 'Tremere',
              'Ravnos', 'Followers of Set', 'Assamite', 'Giovanni',
              'Tzimisce', 'Lasombra', 'Noble Pander',
              'Cappadocian', 'Lasombra Antitribu'}
#clan_roles = set(roles[i] for i in clan_names)
sabbat_clans = {'Tzimisce', 'Lasombra', 'Noble Pander'}
#sabbat_roles = set(roles[i] for i in sabbat_clans)

'''
Role_names [09.05.2018]:

@everyone = 398212610870345728

Prince = 398223824514056202
Sheriff = 398243225116213310
Seneschal = 398244393003384843
Harpy = 419657934293827593
Scourge = 420621473036632064
Primogens and Emissary = 417776802535047178
Beckett = 419975091544391680
Beckett = 399291400434221068

Malkavian = 398972693480996886
Toreador = 398974249659924480
Brujah = 398974429012426762
Ventrue = 399173942033776640
Nosferatu = 399181594356613134
Gangrel = 399187455334547466
Tremere = 399189123123904512

Ravnos = 398974681782157312
Followers of Set = 399313856020611074
Assamite = 402130684128395264
Giovanni = 402141570389770262

Tzimisce = 398971806695817219
Lasombra = 398973052475408389
Noble Pander = 415642642597019658

Cappadocian = 421278030372012043
Lasombra Antitribu = 420599142218465292

New World Order = 420327469371883520
Sabbat = 422166674528272384
Anarch = 423408828097363978

'''
