# -*- coding: utf8 -*-
import discord
import string

Ready = False
was_Ready = False
is_test = False

DISCORD_TOKEN = ''
VTM_SERVER_ID = ''
TST_SERVER_ID = ''
WELCOME_CHANNEL_ID = ''
TEST_CHANNEL_ID = ''
DATABASE_URL = ''
DROPBOX_ID = ''

client = discord.Client()
loop = client.loop
vtm_server = None  # type: discord.Server
tst_server = None  # type: discord.Server
prm_server = None  # type: discord.Server
main_ch = None  # type: discord.Channel
test_ch = None  # type: discord.Channel
vtm_news_ch = None  # type: discord.Channel
other_news_ch = None  # type: discord.Channel
vtm_links_ch = None  # type: discord.Channel
other_links_ch = None  # type: discord.Channel
voice = None # type: discord.VoiceClient
player = None # type: type(discord.VoiceClient.create_stream_player())

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
    'Soul': '391952676771856385',
    'Tilia': '271496862756765698',
}

channels = {
    'flood': '398645007944384513',
    'f_wood': '461140194532524042',
    'rules': '419207215472181268',
    'ask': '398728556424986624',
    '4-sop': '398728854534881280',
    'counsel': '417777460772470785',
    'bookshelf': '459295179837407242',
    'stuff': '411647652246323200',
    'test': '419968987112275979',
    'rpg': '458975748611375104',
    'chantry': '402222682403504138',
    'bar': '415646441730474007',
    #
    'primogens': '417777460772470785',
    # voice channels
    'voice': '422157208017436673',
    'garden': '423559892759085072',
    'ingame': '460752648967290900',
    'v_sabbat': '421986369783463946',
    # test channels
    'beckett': '459193166185234444',
    'vtm_news': '453172109460635658',
    'vtm_links': '461424461950877698',
    'vtm_links_archive': '498828812130189353',
    'vtm_links_info_logs': '512939377219993601',
    'other_news': '497142772415856641',
    'other_links': '497142885700075540',
    'test_mode_only': '497143071604211743',
    'beckett_ignore': '512952018739134504',
}

superusers = {users['Kuro'], users['Magdavius'], }  # users['Natali'],  # Manf & Doriana checked by roles

beckett_refs = {users['bot'], '419975091544391680', }  # last - role_id
beckett_names = {'беккет', 'бэккет', 'бекетт', 'бэкетт', 'бэккетт', 'беккетт', 'beckett', }
#beckett_names = {'люсита', 'lucita', }
silent_channels = {}
ignore_channels = {
    channels['vtm_news'], channels['vtm_links'], channels['other_news'], channels['other_links'],
                   channels['vtm_links_archive'], channels['vtm_links_info_logs'], channels['beckett_ignore'],
                }

punct2space = str.maketrans(string.punctuation + '«»🏻🏼🏽🏾🏿', ' ' * (len(string.punctuation) + 7))  # for translate

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
         'Regent': '448829797221793803',
         'Silence': '449666656143409162',
         'Priest': '451687545412124672',
         'Ductus': '451687735355375626',
         # 'Gargoyle': '453169623576084480',  # test Server
         }

role_by_id = {value: key for (key, value) in roles.items()}

clan_names = {'Malkavian', 'Toreador', 'Brujah', 'Ventrue', 'Nosferatu', 'Gangrel', 'Tremere',
              'Ravnos', 'Followers of Set', 'Assamite', 'Giovanni',
              'Tzimisce', 'Lasombra', 'Noble Pander',
              'Cappadocian', 'Lasombra Antitribu',
              # 'Gargoyle',  # test Server
              }
clan_ids = {key for key in role_by_id if role_by_id[key] in clan_names}
#clan_roles = set(roles[i] for i in clan_names)
sabbat_clans = {'Tzimisce', 'Lasombra', 'Noble Pander'}
#sabbat_roles = set(roles[i] for i in sabbat_clans)
not_sir = {'235088799074484224'}  # Радио "Harpy" 66.6FM
