import constants as C

hearts = {'❤', '💛', '💚', '💙', '💜', '🖤', '❣', '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟', '♥', } # '💔',

sm_resp = {
    'wlc': ('всегда пожалуйста', 'всегда рад', 'обращайся',),
    'hi': ('привет', 'салют', 'здравствуй',),
    'hi_smiles': ('🤗', '👋', ), # 'hugging', 'wave'
    'fun_smiles': ('🙂', '😃', '😁', '😀', '😄', '😏', '😉', '🙃'),
    'bye': ('пока', 'покеда', 'до свидания', 'всего хорошего',),
    'love': ('нравишься', 'люблю', 'классный', 'heart', 'love', ),
    'yes': ('да', 'да, конечно', 'разумеется', 'определённо', ),
    'no': ('нет', 'конечно нет', 'разумеется нет', 'определённо нет', ),
    'bot_dog': ('мальчик', 'фас', 'песик', 'пес', 'апорт', 'сидеть', 'лежать', 'голос', 'угол', 'лапу', 'собака',
                'блохастый', 'блохастик', 'сучка',),
    'apoliticality': (
        'Я - Сородич. То, как другие называют и определяют себя, касается меня только в тех случаях, '
            'когда связано с местными обычаями.',
    ),
    'not_funny_sm': (
        ':confused:', ':neutral_face:', ':unamused:',
    ),
    'not_funny_t': (
        ':confused:', ':neutral_face:', ':unamused:',
        'обхохочешься', '*очень смешно*', 'скажи, когда надо смеяться', 'ну, не уметь в юмор не самое страшное',
    ),
}
sm_resp['hi_plus'] = sm_resp['hi'] + sm_resp['hi_smiles']
sm_resp['not_funny'] = sm_resp['not_funny_sm'] + sm_resp['not_funny_t']
sm_resp['check_like'] = set(sm_resp['love']).union(hearts).union({'😘'})
sm_resp['ans_smiles'] = set(sm_resp['hi_smiles']).union(sm_resp['not_funny_sm']).union(sm_resp['fun_smiles'])

tremer_joke = 'Если вы переспросите, то я буду всё отрицать, но Тремер – мой любимый клан.'

forbiddenLinks = {
    'wod.su',
    'sabbat.su',
    'вот.су',
    'вод.су',
    'саббат.су',
}

# Dynamic data (not saved memory)

day_events = set()

# ev = {months: {days: events}} # keys:int
data_events = {key:{} for key in range(1,13)}
# January
data_events[1][1] = C.events['New Year']
data_events[1][13] = C.users['Soul']
data_events[1][18] = C.users['Rainfall']
data_events[1][20] = C.users['Zodiark']
# February
data_events[2][14] = C.events['Valentine\'s Day']
data_events[2][20] = C.users['Tarkin']
# March
data_events[3][8] = C.events['8 March']
# April
data_events[4][3] = C.users['Tilia']
data_events[4][14] = C.users['Natali']
data_events[4][16] = C.users['Tveyn']
# May
data_events[5][25] = C.users['Rouge']
data_events[5][20] = C.users['vagarshk_tsonek']
# June
data_events[6][1] = C.users['Demian']
data_events[6][3] = C.users['Hadley']
data_events[6][15] = C.users['Vasheska']
data_events[6][19] = C.users['Darude']
data_events[6][22] = C.users['Samael']
data_events[6][24] = (C.users['Tony'], C.users['Svartalfr'])
# July
data_events[7][23] = C.users['Blaise']
data_events[7][26] = C.users['broomstik']
# August
# September
data_events[9][6] = C.users['miss Alex']
data_events[9][25] = C.users['AyrinSiverna']
# October
data_events[10][10] = C.users['Buffy']
data_events[10][23] = C.users['vampiresnvino']
data_events[10][24] = (C.users['Red Queen'], C.users['Matt the Shadow'])
data_events[10][31] = C.events['Halloween']
# November
# December
data_events[12][27] = C.users['Doriana']

# for test
data_events[2][28] = (C.events['Test2'], C.users['Dummy'])
data_events[3][1] = C.events['Test']
data_events[3][3] = C.events['Test2']
