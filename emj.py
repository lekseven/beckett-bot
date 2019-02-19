import discord

from data_emoji import emojis
import constants as C
import local_memory as ram
import other
import log


# Emojis [17.02.2019]:
ems_id = {
    # VtM server
    '400662865935204363': 'm_drunk',
    '400662865972822026': 'p_Lacr',
    '400662866157502476': 'p_nosferatu',
    '400662866371543040': 'p_janett',
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
    '534065125867388938': 'logo_dementation',
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
}

extra_em = {}
anim_em = {}

# to color smile: smile[ok_hand]+skins[1]
skins = ['', '🏻', '🏼', '🏽', '🏾', '🏿']
skins_set = set(skins)
rand_em = set()
name_em = {}
em_set = set()
em_name = {}
hearts = {'❤', '💛', '💚', '💙', '💜', '❣', '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟', '♥', } # '💔',

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


def e_str(name):
    if name in extra_em:
        return extra_em[name]
    elif name in em_name:
        return f':{em_name[name]}:'
    elif name in emojis:
        return emojis[name]
    # elif not C.is_test:
    else:
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


def prepare():
    log.I('Prepare emj')
    save_em()
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
        C.users['Buffy']: (other.rand_tableflip(), )
    }
    morn_to_add_sm = {
        C.users['Kuro']: ('tea',),
        C.users['Natali']: ('purple_heart', 'heartpulse'),
        C.users['Buffy']: (*('sun_with_face',) * 3, 'm_wafer', 'chocolate_bar', 'doughnut', 'cake'),
        C.users['Tilia']: (*('sun_with_face',) * 3, 'm_Tilia_fase', 'm_wafer', 'smiley_cat', 'sgushchenka'),
        C.users['cycl0ne']: ('p_jonesy', 'smiley_cat'),
        C.users['AyrinSiverna']: ('Logo_Toreador', 'heart', 'hearts', 'rose', 'tulip'),
        C.users['Doriana']: ('hugging', 'relaxed', 's_shchupalko0'),
        C.users['CrimsonKing']: ('carrot', 'cucumber', 's_shchupalko0'),
        C.users['Vladislav Shrike']: ('punch', 'metal', 'Logo_Brujah', ),
        C.users['miss Alex']: ('sgushchenka', 's_shchupalko3', 's_shchupalko1'),
        C.users['Samael']: 'lizard', C.users['Creol']: 'hugging',
        C.users['Hadley']: 'smiley', C.users['Soul']: 'coffee',
        C.users['Lorkhan']: ('wave', 'Logo_Brujah', 'cowboy', )
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
        'Tilia': {'p_jonesy', 'logo_dementation', },
        # 'Kuro': {'point_up', 'Logo_Tremere', 'thumbsup'}, # for test
    }
    rand = {'t_jiznbol1', 't_jiznbol2', 'm_Tarkin_f', 'slight_smile', 'joy', 'laughing', 'rofl',
               'smiley_cat', 'smile_cat', 'joy_cat', 'full_moon', 'full_moon_with_face', 'crescent_moon',
               'first_quarter_moon_with_face', 'last_quarter_moon_with_face', 'night_with_stars',
               'sun_with_face', 'sunny', 'sunrise_over_mountains', 'city_sunset', 'bat', 'Logo_Malkavian',
            'p_tetjaadmin', 't_ojwse', 'm_lopata'}

    for s in C.client.servers: #type: discord.Server
        # log.jD(f'<emj> {s.name} check:')
        for em in s.emojis:  #type: discord.Emoji
            pre = 'a' if em.name.startswith('a_') else ''
            em_str = '<{1}:{0.name}:{0.id}>'.format(em, pre)
            extra_em[em_str] = em_str
            if pre:
                extra_em[str(em)] = em_str
                anim_em[str(em)] = em
            if em.id in ems_id:
                emojis[ems_id[em.id]] = em
                extra_em[ems_id[em.id]] = em_str
                # emojis['<:{0}:{1}>'.format(em.id, ems_id[em.id])] = ems_id[em.id]
            else:
                # log.p(f"'{em.id}': '{em.name}',")
                pass
            if em.name not in emojis:
                emojis[em.name] = em
                extra_em[em.name] = em_str
            emojis[em.id] = em
            extra_em[em.id] = em_str
            # if not C.is_test:
            #     log.jW('{save_em} new smile '+str(em))

    for name in special:
        name_em[C.users[name]] = set()
        for e_name in special[name]:
            em = e(e_name)
            if em:
                name_em[C.users[name]].add(em)
            elif not C.is_test:
                log.jW("{{save_em}} can't find {0} in emojis (1)".format(e_name))

    for e_name in rand:
        em = e(e_name)
        if em:
            rand_em.add(em)
        elif not C.is_test:
            log.jW("{{save_em}} can't find {0} in emojis (2)".format(e_name))


def is_emj(em):
    return em in em_set


async def on_reaction_add(reaction, user):
    """

    :type reaction: discord.Reaction
    :type user: discord.User
    :return:
    """
    server = reaction.message.server
    if user == server.me:
        return

    message = reaction.message # type: discord.Message
    emoji = reaction.emoji # type: discord.Emoji

    if user.id in ram.emoji_users and not message.channel.is_private:
        if other.find(message.reactions, emoji=emoji, me=True):
            await C.client.remove_reaction(message, emoji, user)
            await C.client.remove_reaction(message, emoji, server.me)
        else:
            await C.client.remove_reaction(message, emoji, user)
            await C.client.add_reaction(message, emoji)
        return

    if user.id == C.users['Kuro'] and e('middle_finger') in emoji:
        log.D('Get *that* smile, try delete message')
        try:
            await C.client.delete_message(message)
        except discord.Forbidden:
            log.jW("Bot haven't permissions here.")

    if message.author == server.me or message.author == user:
        return

    if user.id in name_em:
        # emoji[0] because it can be different colors
        if (isinstance(emoji, str) and emoji[0] in name_em[user.id]) or emoji in name_em[user.id]:
            log.jD('Copy special reaction')
            pause_and_add(message, emoji)
            return

    if emoji in rand_em:
        chance = other.rand()
        if chance <= 0.01:
            log.jD('Copy some reaction')
            pause_and_add(message, emoji)
            return

    if server.id == C.vtm_server.id:
        if emoji == e('Logo_Gangrel') and other.find(C.vtm_server.get_member(user.id).roles, id=C.roles['Gangrel']):
            log.jD('Copy Gangrel reaction')
            pause_and_add(message, emoji)

    # len(message.reactions) < 20
    # if str(user) == 'Kuro#3777':
    #     pass
    #     await C.client.add_reaction(message, other.choice(list(emojis.values())))
    #     #await C.client.add_reaction(message, emojis['LogoClanTremere'])


async def on_reaction_remove(reaction, user):
    """

        :type reaction: discord.Reaction
        :type user: discord.User
        :return:
        """
    server = reaction.message.server
    if user == server.me:
        return

    message = reaction.message  # type: discord.Message
    emoji = reaction.emoji  # type: discord.Emoji

    if message.author == server.me or message.author == user:
        return

    if user.id in name_em:
        # emoji[0] because it can be different colors
        if (isinstance(emoji, str) and emoji[0] in name_em[user.id]) or emoji in name_em[user.id]:
            log.jD('Remove special reaction')
            await C.client.remove_reaction(message, emoji, server.me)

    # if str(user) == 'Kuro#3777':
    #     await C.client.remove_reaction(message, emoji, C.server.me)


async def on_message(message: discord.Message, beckett_mention):
    author = message.author.id
    if author in ram.ignore_users:
        return

    prob = other.rand()

    if message.channel.id == C.channels['stuff'] and (message.attachments or message.embeds):
        log.jD(f'emj.in_staff, prob = {prob}.')
        if author == C.users['Natali'] and prob < 0.9:
            log.jD('Like Natali in staff')
            pause_and_add(message, ('purple_heart', 'heart_eyes', 'heart_eyes_cat', 'heartpulse'))
        elif author in {C.users['Doriana'], C.users['Tilia'], C.users['Buffy']} and prob < 0.4:
            log.jD('Like Doriana or Tilia or Buffy in staff')
            pause_and_add(message, ('heart', 'hearts', 'heart_eyes', 'black_heart'))
        elif author in {C.users['Hadley'], C.users['cycl0ne'], C.users['Magdavius']} and prob < 0.4:
            log.jD('Like Hadley or cycl0ne or Magdavius in staff')
            pause_and_add(message, ('thumbsup', 'ok_hand', 'heart_eyes_cat'))

    if prob > 0.5:
        for sm in ('((', 'Т_Т', 'T_T', ':С', ':C', '😭', '😢', '😣', '😖', '😫', '😩', 's_blood_cry'):
            if sm in message.content:
                log.jD(f'Add jiznbol for {sm}.')
                pause_and_add(message, ('t_jiznbol1', 't_jiznbol2'))
                break
        else:
            for sm in ('))', ':D', 'XD', '😃', '😁', '😀', '😄', 'm_wafer', 'm_Tilia_fase', '😂', '😆', '😹', '🤣'):
                if sm in message.content:
                    log.jD(f'Add fun for {sm}.')
                    pause_and_add(message, ('smiley', 'slight_smile', 'grin', 'grinning', 'smile', 'upside_down'))
                    break

    if author == C.users['Natali']:
        if beckett_mention:
            log.jD('Like Natali for Beckett')
            pause_and_add(message, (*('purple_heart',) * 5, 'relaxed', 'blush',
                                                'kissing_closed_eyes', 'kissing_heart', 'slight_smile'))
        elif prob < 0.01:
            log.jD('Like Natali chance 0.01')
            pause_and_add(message, ('purple_heart', 'heart_eyes', 'heart_eyes_cat'))

    elif author == C.users['Doriana']:
        if beckett_mention and prob < 0.1:
            log.jD('Like Doriana for Beckett chance 0.1')
            pause_and_add(message, e('octopus'))
        elif prob < 0.005:
            log.jD('Like Doriana chance 0.005')
            pause_and_add(message, e('black_heart'))

    elif author == C.users['Hadley']:
        if beckett_mention and prob < 0.1:
            log.jD('Like Hadley for Beckett chance 0.1')
            pause_and_add(message, (e_str('a_Toreador_light'), e_str('a_Toreador_wave')))
        elif prob < 0.005:
            log.jD('Like Hadley chance 0.005')
            pause_and_add(message, e('Logo_Toreador'))

    elif author == C.users['Tony']:
        if beckett_mention and prob < 0.1:
            log.jD('Like Tony for Beckett chance 0.1')
            pause_and_add(message, e('Logo_Ventrue'))
        # elif prob < 0.005:
        #     log.jD('Like Tony chance 0.005')
        #     await C.client.add_reaction(message, e('ok_hand'))

    elif author == C.users['Rainfall']:
        if beckett_mention and prob < 0.1:
            log.jD('Like Rainfall for Beckett chance 0.1')
            pause_and_add(message, e('green_heart'))
        elif prob < 0.005:
            log.jD('Like Rainfall chance 0.005')
            pause_and_add(message, e('racehorse'))

    elif author == '237604798499651594': # Барон Рихтер
        await C.client.add_reaction(message, e('poop'))

    if other.t2s(frm='%d.%m') == '14.02':   # Valentine's Day
        if author in {C.users['Natali'], C.users['Tilia']}:
            pause_and_add(message, {'❤', '💛', '💙', '💜', '❣', '💕', '💞', '💓', '💗', '💖', '💝', '♥'})
        elif prob < 0.1:
            pause_and_add(message, {'💌', '💟', })


def pause_and_add(message, emoji:str or discord.Emoji, t=-1):

    if not(isinstance(emoji, str) or isinstance(emoji, discord.Emoji)):
        emoji = other.choice(emoji)
    emoji = e(emoji) or emoji

    if t < 0:
        t = other.rand(5, 10)

    other.later_coro(t, C.client.add_reaction(message, emoji))
