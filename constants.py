# -*- coding: utf8 -*-
import discord
import string
import datetime


class Types:
    User = discord.User
    Message = discord.Message
    Reaction = discord.Reaction
    Embed = discord.Embed
    CallMessage = discord.CallMessage
    GroupCall = discord.GroupCall
    Server = discord.Server
    Member = discord.Member
    VoiceState = discord.VoiceState
    Colour = discord.Colour
    Game = discord.Game
    Emoji = discord.Emoji
    Role = discord.Role
    Permissions = discord.Permissions
    PermissionOverwrite = discord.PermissionOverwrite
    Channel = discord.Channel
    PrivateChannel = discord.PrivateChannel
    Invite = discord.Invite
    Status = discord.Status
    ChannelType = discord.ChannelType
    Datetime = datetime.datetime
    Timedelta = datetime.timedelta
    Timezone = datetime.timezone


class Exceptions:
    DiscordException = discord.DiscordException
    LoginFailure = discord.LoginFailure
    HTTPException = discord.HTTPException
    Forbidden = discord.Forbidden
    NotFound = discord.NotFound
    InvalidArgument = discord.InvalidArgument
    GatewayNotFound = discord.GatewayNotFound
    ConnectionClosed = discord.ConnectionClosed
    OpusError = discord.opus.OpusError
    OpusNotLoaded = discord.opus.OpusNotLoaded


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

#   upd 25.02.2018
users = {
    'Natali': '109004244689907712',
    'Manf': '95525404592316416',
    'Doriana': '347045128617197568',
    'Hadley': '284267510835052545',
    'cycl0ne': '415648652539723787',
    'Tarkin': '325416343212130304',

    'Kuro': '414384012568690688',
    'Magdavius': '203539589284102144',

    'bot': '419678772896333824',
    'Beckett': '419678772896333824',
    'Beckett2': '399187791927574528',
    'Rythm': '235088799074484224',

    'Buffy': '297305326665859072',
    'Soul': '391952676771856385',
    'Tilia': '271496862756765698',
    'Red Queen': '418105326617755649',
    'Шаман': '263345050094796800',
    'Эйхорст': '353985635234611211',
    'Tveyn': '155752265544761344',
    'Samael': '306465564933619723',
    'miss Alex': '418047765902393365',

    #Ventrue:
    'larenYIA': '515054333625106433',
    'Transcendent traveler': '188690890384998400',
    'Englishman': '449736794049740811',
    'Jennifer': '462679802927775755',
    'SuslikNotDead': '452493525586804766',
    'ayazani': '455723335733477377',
    'vampiresnvino': '374641572614242324',
    'podushkinZ': '267656848222453761',
    'Lineyka': '220252077887062026',
    'Tony': '377091220859518988',
    'Creol': '315503918077444096',
    'verasolar': '300371564963037196',
    'YUNO': '402052211053690891',

    #Toreador:
    'Frabel': '191672412826238977',
    'Raxmaninov1994': '535460433167908865',
    'Иван': '367700291392503809',
    'GhettoDed': '399477100664455170',
    'AyrinSiverna': '149266212549951488',
    'Chiklia': '441023417940967435',
    'Hellgira': '359370370345861120',
    'Divuar': '261952969270886401',
    'OlhaT': '405815936302579722',
    'Rouge': '218763251410796546',
    'Matt the Shadow': '436258841676480525',
    'Anna Green': '259008891554234369',
    'Goldfinch01': '328189778124341248',
    'devNull': '413845623112990721',
    'clusterf_ck': '155707861597552640',
    'Svartalfr': '313838041984794624',
    'Fookin laser sights': '318123459026616320',
    'Mr.Fynjy': '283990250836197377',
    'Alt': '476813116722774029',
    'Zodiark': '67017782608277504',
    'vezavange': '400398185819799553',
    'RaaMati': '459948065713815553',

    #Tremere:
    'RedElemental': '255313516523683842',
    'Enelde': '212540512937312257',
    'Darkuzar': '342358379681021952',
    'Lot D': '252131582658215939',
    'Elerius': '527148832384090123',
    'валерьянка': '318074728361361411',
    'Paul Grav': '289098489991004162',
    'Максвель': '525820875925094411',
    'Михаил<(Protez)>': '264646288505700352',
    'Blaise': '484390925578141696',
    'lunatic': '203539589284102144',
    'Тиран и Самодур': '479388916168917012',
    'Landri': '514500851231096832',
    'Закериал Белмор': '448350731565531138',
    'Librantu': '326505395336249353',
    'Yashzik': '330355437134413824',
    'zhele': '495522243300950017',
    'Naome': '313007087754018818',
    'Letty': '454792076169576468',
    'Jurgen_Richter': '280744439876419585',
    'Плащик': '493803351138631681',
    'Eireenn': '404699364301209601',
    'M0n0chr0me': '424856536746295297',
    'Filstri': '270139573676408833',
    'GoblinKing': '262497397878292480',

    #Malkavian:
    'moonlight': '453631238851526657',
    'Maya-Maria': '392292865008467978',
    'neoshizz': '285429893125111809',
    'Insane': '204623591474462720',
    'broomstik': '446985790472585237',
    'Кацура': '285101672227667968',
    'Vasheska': '249859374581940224',
    'MyrDragon': '406899899804811266',
    'KaiNiT87': '378766849346895873',
    'Тенебра': '417870066416222209',
    'Ханако': '264005821095084033',
    'Gerindel': '519446293823881217',
    'John Barleycorn': '176285908411219968',
    'GLen69': '326046216557297668',
    'OldmanFM': '153473241761972224',
    'Ложка Сахара': '361504797528031254',
    'Трандуил': '242009548888604672',
    'KrusnikD': '231366589453303809',
    'Pomsky': '415439882333192192',
    'Anton': '129212079256240128',
    '42Kami': '213191623302053889',
    'sour__cream': '248205108913897473',
    'LadyNancyVamp-CL-Malkavian': '303611426730409995',
    'Sheon': '347082603729518593',

    #Brujah:
    'Shtrein': '172709562330120192',
    'Revan Raven': '216939965395894272',
    'Alexander Banzai': '216826927158263808',
    'iGaffari': '334333414461145098',
    'Lorkhan': '483616547487875072',
    'Sea Freya': '418886880155795466',
    'Arch': '202901174423257088',
    'Deodatus': '518785428770390027',
    'Isendur': '241539927890853898',
    'Kamilla': '443335222789144576',
    'elderdeart': '366286988426346498',
    'Элиас': '440455856484515840',
    'Vladislav Shrike': '258348562687983626',

    #Nosferatu:
    'Vanta11a': '264021123291807754',
    'jay.tee': '137495420770189312',
    'Дженетис': '238935258194640896',
    'Cyber Milos': '210876599657168906',
    'Arthuriz': '462728532095795204',
    'Тюлень Джо': '291194777037307904',
    'Тритий': '147397999654338560',
    'Olkadan': '361257890557984769',
    'ConradBulba': '377053853096345601',
    'Soviet_bear': '370294130829557760',
    'Zebub': '541006626383986689',

    #Gangrel:
    'sad_sebastian': '394566593159495692',
    'WhiterloK': '463087640074387457',
    'Всеслав': '229349037923500042',
    'Terra Destroyer': '459815166125801482',
    'Nira Jervada': '422639669436743680',
    'Neforlution Waterbird': '421374664170930197',
    'Markus Dominus Gestant C. Corvus': '221308405908766730',
    'Amalrik': '280260444650995712',
    'Kurosawa': '347805829493161984',
    'Tiele': '540861657237422095',
    'Salvia Sclarea': '419684648453668866',
    'Ириска Киска N7': '348592720723443724',
    'Даркан': '219554757583306755',
    'aleth_lavellan': '482259435574657034',

    #Lasombra Antitribu:
    'Alastor': '402165264285827072',
    'Alexej': '366586266537689098',
    'Рeach of earthquakes': '180922938659307520',

    #Lasombra:
    'Vladimir': '444202315486986260',
    'Belkaer': '401771506029428746',
    'Jesse': '536217892971085835',
    'AV': '232603519344050176',
    'Пастернакус': '341894205653909504',
    'Teo_Lasombra': '479362638606893058',
    'Джэф': '246342660003069952',
    'vagarshk_tsonek': '321210497070530561',
    'Helgi Mitrison': '215889569646772225',
    'Breganov': '228194959952445440',
    'Eladrith Ynneas': '369354857880223745',

    #Tzimisce:
    'Derbius': '240439694544863232',
    'Demian': '400538851325509633',
    'Someone': '321997635806298112',
    'Loke': '196685048907431936',
    'Aileen': '217372203933499393',
    'CrimsonKing': '271491887435612161',
    'Tillien': '259673208943280129',
    'Тася': '415240403621511178',
    'Mr P.B.': '222380372426489856',
    'Darude': '193453556773289984',
    'енотики компотики': '529322591706546196',

    #Giovanni:
    'Abrams': '503697741818626078',
    'el dia': '448036293633638402',
    'Kardero': '467031104990216202',

    #Followers of Set:
    'Ишемия колбасы': '457912299974557696',
    'Tess': '278883237022138368',

    #Ravnos:
    'NuClearSum': '153568420888182785',
    'Rainfall': '119762429969301504',
    'Мортос': '377145552414179340',
    'sparrow': '357058515753238538',
    'RailiQuin': '161300993458307072',

    #Assamite:
    'Samhael Zefearoth': '516300825484722177',
    'Azm': '438347559853883392',
    'radiacto': '216569629466689537',

    #Cappadocian:
    'Samuel Willmore': '149231405329678338',
    'Jestero': '400530803538264071',
    'CherNicko': '404359930737590303',

    #Caitiff and Pander:
    'Kwisatz Haderach': '311420250283311104',
    'Valkirius': '219794326987735040',
    'Einarr': '400567024725786626',
    'Aelali': '204608192230064128',
    'Zer': '99627685998764032',
    'UnRon': '264749600080920587',
    'Grey': '284367437888094208',
    'Дмитрий Мейнц': '415083688955478027',
    'Comrade Marshal': '294422949992071168',
    'Dewiles': '296557462171942912',
    'Vincere': '448005007477047296',
    'Rainy Berlin': '336436180885307394',
    'fridayf': '427796368606756866',
    'BismuthGarden': '280761591815733248',
    'Skyther': '421938787569106947',
    'piromant (Дмитрий)': '327333928262434816',
    'Liber': '390053631459852299',
    'V.Immortal': '427610672440803329',

    #@everyone:
    'Trueann': '237555111306592256',
    'Дракон': '361605898893787137',
    'Dr. Sadrick Eyedt': '391620209506648067',
    'Kuma': '154527657797615616',
    'SrTc': '180290961916690434',
    'Mushroom Elf': '443130332904947733',
    'Ри': '528172299350966273',
    'Сексуальный Пулемёт Любви': '311440346947256330',
    'Babayich': '421064407288643595',
    'Дональд Мак-Гилаври': '346723353253380096',
    'Juli#8002': '540106190781153282',
    'alamorf': '161884125676961792',
    'LonelyGoth': '144528639403360256',
    'хух': '394068810241409025',
    'Арен': '210428546206662656',
    'secret_brujah': '545193781503328257',
    'Tvirinum': '259159113169108992',
    'lurk': '329266524965699606',
    'Regus': '227779715010658304',
    'Габриэл': '288270745929383938',
    'сосите плывиски': '495449703161528360',
    'LEON_FULL': '267386650135494667',
    'Роман777': '547264976667279360',
    'Velvet': '539889503733547032',
    'Morellaivan': '531207756082970644',
    'Дима': '239491315421675521',
    'Nodeyr': '292735979029135361',
    'creyganlk': '434780033433731102',
    'teh_nagato': '410215440451764224',
    'Radrik(Roma)': '222773473867464704',
    'Verder': '159519806666571776',
    'никита': '375779614959599616',
    'Lamiya Dix': '505062304447201281',
    'lukan': '533337288823013387',
    'Мангуст Салаи': '422110968605048844',
    'Sardagon': '187631627705253888',
    'Juli#9995': '548602808841142292',
    'Ashiest': '186231967564562433',
    'ArtiVol': '235840190495588352',
    'Mort': '263383317209022464',
    'Heaven': '514215128992972800',
    'elm': '354687423084757016',
    'Inferno': '547724430940307456',
    'Ranizer': '379623596206587905',
    'chlrm': '524660792336056320',
    'Тёмный пластилин': '476750002316902400',
    'Iu_zloi': '294845509271814144',
    'IrinKa': '311890093394755586',
    'kaan': '500997487197421588',
    'Nuatha': '197887323462041600',
    'Ace': '323860514885337098',

    #test
    'Dummy': '452303933856153601',
    'Dracula': '491399986156666893',
}

usernames = {_id:name for name, _id in users.items()}

female = {
    users['Natali'], users['Doriana'], users['Buffy'], users['Soul'], users['Tilia'], users['Red Queen'],
    users['miss Alex'], users['verasolar'], users['YUNO'], users['Lineyka'], users['AyrinSiverna'], users['Anna Green'],
    users['Rouge'], users['Frabel'], users['Максвель'], users['валерьянка'], users['Vasheska'],
    users['broomstik'], users['Insane'], users['Тенебра'], users['Sea Freya'], users['aleth_lavellan'],
    users['Рeach of earthquakes'], users['Aileen'], users['el dia'], users['Kuma'], users['IrinKa'], users['ayazani'],
    users['Jennifer'], users['OlhaT'], users['Hellgira'], users['Alt'], users['Pomsky'], users['Ложка Сахара'],
    users['Kamilla'], users['Ириска Киска N7'], users['Тася'], users['Maya-Maria'], users['V.Immortal'],
    users['Vincere'], users['Juli#8002'], users['Juli#9995'],
}

servers = {
    'vtm': vtm_server,
    'test': tst_server,
    'Teahouse': '484780257103183883',
    'Sabbat': '425523547297808384',
    'Tilia': '493452777519841280',
}

usual_servers = {servers[key] for key in ('vtm', 'test', 'Teahouse')}

channels = {
    'flood': '398645007944384513',
    'f_wood': '461140194532524042',
    'rules': '519253006726987780',    #'419207215472181268',
    'ask': '398728556424986624',
    '4-sop': '398728854534881280',
    'bookshelf': '459295179837407242',
    'stuff': '411647652246323200',
    'music': '474650076241854474',
    'test': '419968987112275979',
    'rpg': '458975748611375104',
    'concept': '531211211514183702',
    'tender': '546992644258136065',
    'sabbat-charsheets': '667334539646861323',
    #
    'counsel': '417777460772470785',
    'primogens': '417777460772470785',
    # clan
    'chantry': '402222682403504138',
    'bar': '415646441730474007',
    'parlor': '402224879123955712',
    'gallery': '407155181050920962',
    'malknet': '402223047307952149',
    'shreknet': '402223998999461894',
    'gangrel_clan': '430309455553626123',
    'independent': '402224715844026380',
    'sabbat': '402224499480854548',
    # voice channels
    'voice': '536959039456935941',
    'radio': '536959145895526410',
    'ingame': '460752648967290900',
    'v_primogens': '548969776672931861',
    'v_sabbat': '523086022498582528',
    'nwo': '531959106659942435',
    # test channels
    'beckett': '459193166185234444',
    'vtm_news': '453172109460635658',
    'vtm_links': '461424461950877698',
    'vtm_links_archive': '498828812130189353',
    'vtm_links_info_logs': '512939377219993601',
    'other_news': '497142772415856641',
    'other_links': '497142885700075540',
    'test_mode_only': '497143071604211743',
    'test_primogenat': '673633521528471554',
    'beckett_ignore': '512952018739134504',
    'not_log': '527230130448498698',
    'not_log_test_only': '527230235146453004',
    #
    'Tilia_main': '493452778145054731',
}

superusers = {users['Kuro'], users['Magdavius'], }  # users['Natali'],  # Manf & Doriana checked by roles

beckett_refs = {users['bot'], '419975091544391680', }  # last - role_id
beckett_names = {'беккет', 'бэккет', 'бекетт', 'бэкетт', 'бэккетт', 'беккетт', 'beckett', }
#beckett_names = {'люсита', 'lucita', }
silent_channels = {}
not_log_channels = {channels['not_log'], channels['not_log_test_only']}
ignore_channels = {
    channels['vtm_news'], channels['vtm_links'], channels['other_news'], channels['other_links'],
                   channels['vtm_links_archive'], channels['vtm_links_info_logs'], channels['beckett_ignore'],
                }
test_channels = {channels['test_mode_only'], channels['not_log_test_only']}

punct2space = str.maketrans(string.punctuation + '«»🏻🏼🏽🏾🏿', ' ' * (len(string.punctuation) + 7))  # for translate

# WARNING: Clans keys here must be the same to dataKeys (Clans) in data
roles = {
    'Prince': '398223824514056202',
    'Sheriff': '398243225116213310',
    'Scourge': '420621473036632064',
    'Seneschal': '398244393003384843',
    'Harpy': '419657934293827593',
    'Primogens': '417776802535047178',
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
    'Pander': '415642642597019658',
    'Cappadocian': '421278030372012043',
    'Lasombra Antitribu': '420599142218465292',
    'Котичек': '510161887342624798',
    'Namaru': '420621473036632064',
    'New World Order': '420327469371883520',
    'Sabbat': '422166674528272384',
    'Anarch': '423408828097363978',
    'Regent': '448829797221793803',
    'Silence': '449666656143409162',
    'Priest': '451687545412124672',
    'Ductus': '451687735355375626',
    'не шабашит': '518874073099665419',
    'DJ': '524567160207573002',
    'Крыска': '557273085384851457',
    'star1': '587605268372652054',
    'star2': '587605472383729665',
    'star3': '587605550926397440',
    'food': '606177312349880350',
    'protege': '607242591464849418',
    'jihad': '701397322269196358',
    # test Server
    'Gargoyle': '453169623576084480',
    # 'Ghoul': '453130638631895072',
}

role_by_id = {value: key for (key, value) in roles.items()}

clan_names = {
    'Malkavian', 'Toreador', 'Brujah', 'Ventrue', 'Nosferatu', 'Gangrel', 'Tremere',
    'Ravnos', 'Followers of Set', 'Assamite', 'Giovanni',
    'Tzimisce', 'Lasombra', 'Pander',
    'Cappadocian', 'Lasombra Antitribu',
    # 'Котичек', 'Namaru',
    # 'Gargoyle', 'Ghoul'  # test Server
}
clan_ids = {roles[name] for name in clan_names}
sect_ids = {roles['Sabbat'], roles['Anarch']}
clan_and_sect_ids = clan_ids.union(sect_ids)
other_roles = set(roles[i] for i in ('DJ', 'star1', 'star2', 'star3', 'Silence', 'не шабашит'))
#clan_roles = set(roles[i] for i in clan_names)
sabbat_clans = {'Tzimisce', 'Lasombra', 'Pander'}
clan_channels = {
    roles['Malkavian']: channels['malknet'],
    roles['Toreador']: channels['gallery'],
    roles['Brujah']: channels['bar'],
    roles['Ventrue']: channels['parlor'],
    roles['Nosferatu']: channels['shreknet'],
    roles['Gangrel']: channels['gangrel_clan'],
    roles['Tremere']: channels['chantry'],
    roles['Ravnos']: channels['independent'],
    roles['Followers of Set']: channels['independent'],
    roles['Assamite']: channels['independent'],
    roles['Giovanni']: channels['independent'],
    roles['Cappadocian']: channels['independent'],
    roles['Tzimisce']: channels['sabbat'],
    roles['Lasombra']: channels['sabbat'],
    roles['Pander']: channels['sabbat'],
    roles['Lasombra Antitribu']: channels['gallery'],
    roles['Sabbat']: channels['sabbat'],
    # roles['Gargoyle']: channels['test_mode_only'],
}
#sabbat_roles = set(roles[i] for i in sabbat_clans)
not_sir = {users['Rythm'], users['Beckett'], '399187791927574528'}  # Радио "Harpy" 66.6FM, Beckett2
voice_alert = {users['Dummy'], users['Natali'],}
i10__42 = 10**42

events = {
    'Test': 0,
    'Test2': 1,
    'New Year': 11,
    'Valentine\'s Day': 214,
    '8 March': 308,
    'Halloween': 1031,
}

events_name = {value: key for (key, value) in events.items()}

h24 = 86400
h48 = 172800
