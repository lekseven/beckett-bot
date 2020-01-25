from d.data_emoji import emojis, emojis_long, emojis_color
import data
import constants as C
import local_memory as ram
import other
import log


# Emojis [17.02.2019]:
ems_id = {
    # VtM server
    #'400662865935204363': 'm_drunk',
    '400662865972822026': 'p_Lacr',
    '400662866157502476': 'p_nosferatu',
    #'400662866371543040': 'p_janett',
    '400664721155555328': 'p_Lucta_de_Aragon',
    '418877362470518784': 'Ankh',
    '420657829007982593': 'm_Tarkin_Miliy',
    '421805633281720320': 'm_Tarkin_f',
    '421806514341281792': 't_torik21',
    '421807340233293844': 'm_torik22',
    '421813252251713548': 'Ankh_Sabbat',
    '421813252289462273': 'Logo_Nosferatu',
    '421813252776001547': 'Logo_Followers',
    '421813252788322314': 'Logo_Ventrue',
    '421813252822007823': 'Logo_Tremere',
    '421813253102895104': 'Logo_Ravnos',
    '421813253103157248': 'Logo_Assamite',
    '421813253186781194': 'Logo_Tzimisce',
    '421813253245501450': 'Logo_Malkavian',
    '421813253375524864': 'Logo_Lasombra',
    '421813253400821760': 'Logo_Gangrel',
    '421813253929435149': 'Logo_Brujah',
    '421813696939950081': 't_jiznbol1',
    '421814043465220105': 'Logo_Toreador',
    '448221067769544704': 'm_draniki',
    '448221784123244545': 'm_bulba',
    '448227584170524685': 'm_lopata',
    '448231060275462144': 'p_tetjaadmin',
    '448236736154304532': 'p_beckett1',
    '448244001703723018': 't_ojwse',
    '451507784454766603': 'Ankh_Cama',
    '451520970377789440': 'Logo_Giovanni',
    '452985737000910859': 'p_cthulhu_head',
    '460457996640714762': 's_shchupalko0',
    '460459149927514122': 's_shchupalko3',
    '460460257471102976': 's_bita',
    '460461435928182784': 's_shchupalko4',
    '460461564882059265': 's_shchupalko1',
    '460462868756692992': 'obtenebration',
    '460463331141091359': 's_shchupalko2',
    '463451501826670604': 't_d_',
    '463452141831454720': 't_net1',
    '463453817258770443': 's_dice',
    '466381128261959713': 'm_wafer',
    '472535276263047188': 's_blood_cry',
    '474353439728730112': 't_jiznbol2',
    '487767072311345172': 'p_jonesy',
    '490273371116797954': 'm_Tarkin_face',
    '490287532400050176': 'm_Tilia_fase',
    '506940161389756426': 'm_r_heart',
    '525924557102645257': 's_dice',
    # '534065125867388938': 'logo_dementation',
    '550995225808601119': 'me_today',
    '564885955602022431': 'bratajtes',
    # test
    '532673320785674317': 'sgushchenka',
    '453173916517662720': 'z_GDAbyudG2',
    '453175977011576852': 'z_Demonic_Skeleton',
    '462006076322086912': 'AnkhV20_0',
    '511958814719737903': 'Tremere_Symbol',
    '511961991787577364': 'TremereDA',
    '528228711460372480': 's_Koldun',
    '531578112383778829': 'hungry',
    '531579324126593025': 'shenRage',
    '532272830964826132': 'DD',
    '532273649747755020': 'Do',
    '532331427874734093': 'dem',
    '532331428000825365': 'dem_m',
    '532331428181180426': 'dem_r',
    '532331439828762626': 'dem_rg',
    '532366476687179776': 'thaum',
    '532366483796262922': 'thau',
    '532366493107748874': 'thaumaturgy',
    '533790911860047873': 't_net2',
    '563845218533638164': 'aleth_wink',
    # anim
    '526062214944260137': 'a_Toreador_light',
    '526062156609880064': 'a_Toreador_wave',
    '524915757419593738': 'a_Jack',
    '525015703997120533': 'a_Beckett',
    '525050014104420377': 'a_blood_cup',
    '525070843177598986': 'a_bulba',
    '525333494683926528': 'a_Tremere_red1',
    '525333561960693772': 'a_Tremere_colors',
    '525338099480395776': 'a_Tremere_red2',
    '525370411454824448': 'a_Tremere_pur1',
    '525370985847717901': 'a_Tremere_pur2',
    '525446674143772712': 'a_Tremere_colors2',
    '527473236305379338': 'a_fire',
    '527474422509207573': 'a_campfire',
    '528132608631111681': 'a_newyear',
    #---
    '552058243804037123': 'a_open_flower',
    '552058497655898114': 'a_rose_grows',
    '552060773107630080': 'a_heart_rose',
    '552065976804311040': 'a_rose_pulse',
    '552066371270344705': 'a_flower_twink',
    '552066796904120341': 'a_color_flower',
    '552068750883422218': 'a_water_lily',
    '552101578879008779': 'a_flower_chameleon',
    #---
    '629378504856961044': 't_sarcrasm',
    '629392187074805773': 't_v5',
    '629392214799286272': 't_v5_not',
    '629394881915125790': 'a_AAAAAAAAAAAA',
    '631165828372627476': 'ship_it',
    '633620856135876628': 'zhmyak',
    '633622485224652820': 'zhmak',
    '648269457277583429': 'heartttt',
    '665240275475496960': 'raja',
    '665560315898888222': 'm_amaranth',
    '665560341920612402': 'm_mouserat',
    '667127289284132880': 'sasha_grey',
    '667301831680196618': 'cat_ombra',
}

extra_em = {}
anim_em = {}

# to color smile: smile[ok_hand]+skins[1]
skins = ['', '🏻', '🏼', '🏽', '🏾', '🏿']
tones = {'tone0': '', 'tone1': '🏻', 'tone2': '🏼', 'tone3': '🏽', 'tone4': '🏾', 'tone5': '🏿'}
skins_set = set(skins)
rand_em = set()
name_em = {}
em_set = set()
em_name = {}
hearts = data.hearts

morn_add = {}


def e(name):
    if not isinstance(name, str):
        return None
    if name in emojis:
        return emojis[name]
    # elif not C.is_test:
    else:
        log.jW('{e} there no emoji ' + name)
    return None


def e_or_s(name):
    if not isinstance(name, str):
        return name
    if name in emojis:
        return emojis[name]
    if name.endswith('_tone', -6, -1):
        tone = name[-5:]
        name = name[0:-6]
        if name in emojis:
            if len(emojis[name]) > 1:
                return emojis[name][0] + tones.get(tone, '') + emojis[name][1:]
            else:
                return emojis[name] + tones.get(tone, '')
    return name


def e_str(name):
    if name in extra_em:
        return extra_em[name]
    elif name in em_name:
        return f':{em_name[name]}:'
    elif name in emojis:
        return emojis[name]
    # elif not C.is_test:
    elif name.endswith('_tone', -6, -1):
        tone = name[-5:]
        name = name[0:-6]
        if name in emojis:
            return emojis[name] + tones.get(tone, '')

    log.jW('{e} there no emoji ' + name)
    return None


def em2text(text):
    text_set = set(text)
    em_text = em_set.intersection(text_set)
    for em in em_text:
        text = text.replace(em, e_str(em))

    # for em in extra_em:
    #     if em in text:
    #         text = text.replace(em, e(extra_em[em]))

    return text


def get_em_names(text:str):
    names = set()
    txt = text
    for em in emojis_long:
        if em in txt:
            names.add(em)
            txt = txt.replace(em, '')
    names.update(em_set.intersection(txt))
    dct_names = {text.find(name):name for name in names}
    names_order = [dct_names[i] for i in sorted(dct_names)]
    return names_order


def prepare():
    log.I('Prepare emj')
    save_em()
    emojis_long.update({(em + sk) for sk in skins[1:] for em in emojis_color})
    for name in emojis:
        em_name[emojis[name]] = name
        em_set.add(emojis[name])

    i = 1
    for sk in skins[1:]:
        em_name[sk] = 'skin_' + str(i)
        em_set.add(sk)
        i += 1

    morn_to_add = {
        C.users['Kuro']: (r'\♨', ),
        C.users['Natali']: (':tea::chocolate_bar:', ),
        C.users['AyrinSiverna']: ('', ),
        C.users['miss Alex']: ('', ),
        C.users['Buffy']: (other.rand_tableflip(), ),
    }
    morn_to_add_sm = {
        C.users['Kuro']: ('tea',),
        C.users['Natali']: ('purple_heart', 'heartpulse'),
        C.users['Buffy']: (*('sun_with_face',) * 3, 'm_wafer', 'chocolate_bar', 'doughnut', 'cake'),
        C.users['Tilia']: (*('sun_with_face',) * 3, 'm_wafer', 'smiley_cat', 'sgushchenka'),
        C.users['cycl0ne']: ('p_jonesy', 'smiley_cat'),
        C.users['AyrinSiverna']: ('Logo_Toreador', 'heart', 'hearts', 'rose', 'tulip'),
        C.users['Doriana']: ('hugging', 'relaxed', 's_shchupalko0', 'black_heart'),
        C.users['CrimsonKing']: ('carrot', 'cucumber', 's_shchupalko0'),
        C.users['Vladislav Shrike']: ('punch', 'metal', 'Logo_Brujah', ),
        C.users['miss Alex']: ('sgushchenka', 's_shchupalko3', 's_shchupalko1'),
        C.users['Samael']: 'lizard',
        C.users['Creol']: 'hugging',
        C.users['Hadley']: 'smiley',
        C.users['Soul']: 'coffee',
        C.users['Lorkhan']: ('wave', 'Logo_Brujah', 'cowboy', ),
        C.users['aleth_lavellan']: ('aleth_wink', 'hugging', 'p_beckett1', 'smiley_cat'),
        C.users['Blaise']: ('m_r_heart', ),
    }
    for name in morn_to_add:
        morn_add[name] = (morn_to_add[name], ) if isinstance(morn_to_add[name], str) else tuple(morn_to_add[name])
    for name in morn_to_add_sm:
        val = (morn_to_add_sm[name], ) if isinstance(morn_to_add_sm[name], str) else tuple(morn_to_add_sm[name])
        morn_add[name] = morn_add.get(name, tuple()) + tuple((e_str(em) or '') for em in val)


def save_em():
    special = {
        'Natali': {'purple_heart', 'Ankh', 't_torik21', 'Logo_Toreador', },
        'Doriana': {'black_heart', 'octopus', 'unicorn', 'Logo_Lasombra', },
        'Tony': {'p_Lacr', 'Logo_Ventrue', }, # 'ok_hand', 'thumbsup',
        'Manf': {'m_draniki', 'm_bulba', 'star_and_crescent', },
        'Hadley': {'Logo_Toreador', 'thumbsup', },
        'Buffy': {'m_wafer', 's_bita', },
        'Tilia': {'p_jonesy', 'm_Tilia_fase', }, # 'logo_dementation',
        'aleth_lavellan': {'p_beckett1', 'smiley_cat'},
        # 'Kuro': {'point_up', 'Logo_Tremere', 'thumbsup'}, # for test
    }
    rand = {'t_jiznbol1', 't_jiznbol2', 'm_Tarkin_f', 'slight_smile', 'joy', 'laughing', 'rofl',
               'smiley_cat', 'smile_cat', 'joy_cat', 'full_moon', 'full_moon_with_face', 'crescent_moon',
               'first_quarter_moon_with_face', 'last_quarter_moon_with_face', 'night_with_stars',
               'sun_with_face', 'sunny', 'sunrise_over_mountains', 'city_sunset', 'bat', 'Logo_Malkavian',
            'p_tetjaadmin', 't_ojwse', 'm_lopata'}

    for s in C.client.servers: #type: C.Types.Server
        # log.jD(f'<emj> {s.name} check:')
        for em in s.emojis:  #type: C.Types.Emoji
            pre = 'a' if em.name.startswith('a_') else ''
            em_str = '<{1}:{0.name}:{0.id}>'.format(em, pre)
            extra_em[em_str] = em_str
            emojis_long.add(em_str)
            if pre:
                extra_em[str(em)] = em_str
                anim_em[str(em)] = em
            if em.id in ems_id:
                emojis[ems_id[em.id]] = em
                extra_em[ems_id[em.id]] = em_str
                # emojis['<:{0}:{1}>'.format(em.id, ems_id[em.id])] = ems_id[em.id]
            elif s.id in (C.vtm_server.id, C.tst_server.id):
                log.jW(f"{s.name} has new emoji\t '{em.id}': '{em.name}',")
            if em.name not in emojis:
                emojis[em.name] = em
                extra_em[em.name] = em_str
            emojis[em_str] = em
            emojis[em.id] = em
            extra_em[em.id] = em_str
            # if not C.is_test:
            #     log.jW('{save_em} new smile '+str(em))
    for id_ in ems_id:
        if ems_id[id_] not in emojis:
            log.jW(f"There are no emoji \t'{id_}': '{ems_id[id_]}'.")

    for name in special:
        name_em[C.users[name]] = set()
        for e_name in special[name]:
            em = e(e_name)
            if em:
                name_em[C.users[name]].add(em)
            else:
                log.jW("{{save_em}} can't find {0} in emojis (1)".format(e_name))

    for e_name in rand:
        em = e(e_name)
        if em:
            rand_em.add(em)
        else:
            log.jW("{{save_em}} can't find {0} in emojis (2)".format(e_name))


def is_emj(em):
    return em in em_set


async def on_reaction_add(reaction, user):
    """

    :type reaction: C.Types.Reaction
    :type user: C.Types.User
    :return:
    """
    server = reaction.message.server
    me = (server and server.me) or reaction.message.channel.me
    if server and user == me:
        return

    message = reaction.message # type: C.Types.Message
    emoji = reaction.emoji # type: C.Types.Emoji

    # cmd part (ignore "ignore" and etc)
    if user.id in ram.emoji_users and not message.channel.is_private:
        try:
            await C.client.remove_reaction(message, emoji, user)
        except Exception as er:
            other.pr_error(er, 'on_reaction_add[remove_reaction]', 'Unexpected error')

        try:
            if other.find(message.reactions, emoji=emoji, me=True):
                await C.client.remove_reaction(message, emoji, me)
            else:
                await C.client.add_reaction(message, emoji)
        except Exception as er:
            other.pr_error(er, 'on_reaction_add[remove_or_add]', 'Unexpected error')
        finally:
            return

    if user.id == C.users['Kuro'] and e('middle_finger') in emoji:
        log.D('Get *that* smile, try delete message')
        try:
            await other.delete_msg(message)
        except C.Exceptions.Forbidden:
            log.jW("Bot haven't permissions here.")

    # usual part
    if message.author in (me, user) or ram.ignore_users.intersection((message.author.id, user.id)):
        return

    # Further just copy emoji, so if one of possibility is triggered -> return
    #  (there is no sense in more copies of one emoji)

    # copy emoji for birthday messages
    if data.day_events.intersection(message.raw_mentions):
        pause_and_add(message, emoji)
        return

    if user.id in name_em:
        # emoji[0] because it can be different colors
        if (isinstance(emoji, str) and emoji[0] in name_em[user.id]) or emoji in name_em[user.id]:
            log.jD('Copy special reaction')
            pause_and_add(message, emoji)
            return

    if server and server.id == C.vtm_server.id:
        if emoji == e('Logo_Gangrel') and other.find(C.vtm_server.get_member(user.id).roles, id=C.roles['Gangrel']):
            log.jD('Copy Gangrel reaction')
            pause_and_add(message, emoji)
            return

    if emoji in rand_em:
        chance = other.rand()
        if chance <= 0.01:
            log.jD('Copy some reaction')
            pause_and_add(message, emoji)
            return

    # len(message.reactions) < 20
    # if str(user) == 'Kuro#3777':
    #     pass
    #     await C.client.add_reaction(message, other.choice(list(emojis.values())))
    #     #await C.client.add_reaction(message, emojis['LogoClanTremere'])


async def on_reaction_remove(reaction, user):
    """

        :type reaction: C.Types.Reaction
        :type user: C.Types.User
        :return:
        """
    server = reaction.message.server
    me = (server and server.me) or reaction.message.channel.me
    if user == me:
        return

    message = reaction.message  # type: C.Types.Message
    emoji = reaction.emoji  # type: C.Types.Emoji

    if message.author == me or message.author == user:
        return

    if user.id in name_em:
        # emoji[0] because it can be different colors
        if (isinstance(emoji, str) and emoji[0] in name_em[user.id]) or emoji in name_em[user.id]:
            log.jD('Remove special reaction')
            await C.client.remove_reaction(message, emoji, me)

    # if str(user) == 'Kuro#3777':
    #     await C.client.remove_reaction(message, emoji, C.server.me)


def pause_and_add(message, emoji:str or C.Types.Emoji, t=-1, all_=False):

    if not(isinstance(emoji, str) or isinstance(emoji, C.Types.Emoji)):
        emoji = list(emoji) if all_ else [other.choice(emoji)]
    else:
        emoji = [emoji]
    emoji = [e_or_s(em) for em in emoji]

    t_all = 0
    for em in emoji:
        if t < 0:
            t = other.rand(5, 10)
        t_all += t

        other.later_coro(t_all, C.client.add_reaction(message, em))


def pause_and_rem(message, emoji:str or C.Types.Emoji, member=None, t=-1, all_=False):
    member = member or message.server.me

    if not(isinstance(emoji, str) or isinstance(emoji, C.Types.Emoji)):
        emoji = list(emoji) if all_ else [other.choice(emoji)]
    else:
        emoji = [emoji]
    emoji = [e_or_s(em) for em in emoji]

    t_all = 0
    for em in emoji:
        if t < 0:
            t = other.rand(1, 5)
        t_all += t

        other.later_coro(t_all, C.client.remove_reaction(message, em, member))
