import constants as C

# ev = {months: {days: events}} # keys:int
date_events = {key:{} for key in range(1, 13)}
# January
date_events[1][1] = C.events['New Year']
date_events[1][13] = C.users['Soul']
date_events[1][18] = C.users['Rainfall']
date_events[1][20] = C.users['Zodiark']
# February
date_events[2][14] = C.events['Valentine\'s Day']
date_events[2][20] = C.users['Tarkin']
# March
date_events[3][8] = C.events['8 March']
# April
date_events[4][3] = C.users['Tilia']
date_events[4][14] = C.users['Natali']
date_events[4][16] = (C.users['Tveyn'], C.users['aleth_lavellan'])
date_events[4][27] = C.users['Vladislav Shrike']
# May
date_events[5][11] = C.users['Ace']
date_events[5][20] = C.users['vagarshk_tsonek']
date_events[5][25] = C.users['Rouge']
date_events[5][27] = C.users['Anna Green']
# June
date_events[6][1] = C.users['Demian']
date_events[6][3] = C.users['Hadley']
date_events[6][15] = C.users['Vasheska']
date_events[6][19] = C.users['Darude']
date_events[6][22] = C.users['Samael']
date_events[6][24] = (C.users['Tony'], C.users['Svartalfr'])
# July
date_events[7][23] = C.users['Blaise']
date_events[7][26] = C.users['broomstik']
# August
# September
date_events[9][6] = C.users['miss Alex']
date_events[9][25] = C.users['AyrinSiverna']
# October
date_events[10][10] = C.users['Buffy']
date_events[10][23] = C.users['vampiresnvino']
date_events[10][24] = (C.users['Red Queen'], C.users['Matt the Shadow'])
date_events[10][31] = C.events['Halloween']
# November
# December
date_events[12][27] = C.users['Doriana']

# for test
# date_events[3][1] = (C.events['Test2'], C.users['Dummy'])
# date_events[3][2] = C.events['Test']
# date_events[3][3] = C.events['Test2']