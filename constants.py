# -*- coding: utf8 -*-
import os
import sys
import discord
import string
Ready = False
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
loop = client.loop
server = discord.Server


users = {
    'Natali': '109004244689907712',
    'Manf': '95525404592316416',
    'Doriana': '347045128617197568',
    'Tony': '377091220859518988',
    'Kuro': '414384012568690688',
    'Magdavius': '203539589284102144',
    'Rainfall': '119762429969301504',
    'bot': '419678772896333824',
    'Creol': '315503918077444096',
    'Buffy': '297305326665859072',
}

channels = {
    'flood': '398645007944384513',
    'rules': '419207215472181268',
    'ask': '398728556424986624',
    '4-sop': '398728854534881280',
    'stuff': '411647652246323200',
    'test': '419968987112275979'
}

superusers = {users['Natali'], users['Kuro'], users['Magdavius'], } # Manf & Doriana checked by roles

beckett_refs = {users['bot'], '419975091544391680', } # last - role_id
beckett_names = {users['bot'], '419975091544391680', 'беккет', 'бэккет', 'beckett',} #{'беккет', 'бэккет', 'beckett', }
silent_channels = {}
ignore_channels = {}


punct2space = str.maketrans(string.punctuation, ' ' * len(string.punctuation))  # for translate
free_cmds = {'roll','help','ignore', 'dominate'}

# WARNING: Clans keys here must be the same to dataKeys (Clans) in data
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

role_by_id = {value: key for (key, value) in roles.items()}

clan_names = {'Malkavian', 'Toreador', 'Brujah', 'Ventrue', 'Nosferatu', 'Gangrel', 'Tremere',
              'Ravnos', 'Followers of Set', 'Assamite', 'Giovanni',
              'Tzimisce', 'Lasombra', 'Noble Pander',
              'Cappadocian', 'Lasombra Antitribu'}
clan_ids = { key for key in role_by_id if role_by_id[key] in clan_names}
#clan_roles = set(roles[i] for i in clan_names)
sabbat_clans = {'Tzimisce', 'Lasombra', 'Noble Pander'}
#sabbat_roles = set(roles[i] for i in sabbat_clans)
not_sir = {'235088799074484224'} # Радио "Harpy" 66.6FM
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
