import discord
from data_emoji import emojis
import constants as C
import local_memory as ram
import other
import random
import log


# Emojis [20.11.2018]:
ems_id = {
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
    # test
    # '453173916517662720': 'z_GDAbyudG2',
}

extra_em = {}

# to color smile: smile[ok_hand]+skins[1]
skins = ['', '🏻', '🏼', '🏽', '🏾', '🏿']
skins_set = set(skins)
rand_em = set()
name_em = {}
em_set = set()
em_name = {}
hearts = {'❤', '💛', '💚', '💙', '💜', '❣', '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟',} # '💔',


def e(name):
    if name in emojis:
        return emojis[name]
    elif not C.is_test:
        log.jW('{e} there no emoji ' + name)
    return None


def get_emname(em):
    if em in em_name:
        return em_name[em]
    elif not C.is_test:
        log.jW('{e} there no name of emoji ' + em)
    return None


def em2text(text):
    text_set = set(text)
    em_text = em_set.intersection(text_set)
    for em in em_text:
         text = text.replace(em, ' ' + em_name[em] + ' ')

    for em in extra_em:
        if em in text:
            text = text.replace(em, ' ' + extra_em[em] + ' ')

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


def save_em():
    special = {
        'Natali': {'purple_heart', 'Ankh', 'Ankh_Toreador', 't_torik11', 't_torik21', 'Logo_Toreador', },
        'Doriana': {'black_heart', 'octopus', 'unicorn', 'Logo_Lasombra', },
        'Tony': {'p_Lacr', 'Logo_Ventrue', }, # 'ok_hand', 'thumbsup',
        'Manf': {'m_draniki', 'm_bulba', 'star_and_crescent'},
        #'Kuro': {'point_up', 'Logo_Tremere', }, # for test
    }
    rand = {'t_jiznbol1', 't_jiznbol2', 'm_Tarkin_f', 'slight_smile', 'joy', 'laughing', 'rofl',
               'smiley_cat', 'smile_cat', 'joy_cat', 'full_moon', 'full_moon_with_face', 'crescent_moon',
               'first_quarter_moon_with_face', 'last_quarter_moon_with_face', 'night_with_stars',
               'sun_with_face', 'sunny', 'sunrise_over_mountains', 'city_sunset', 'bat', 'Logo_Malkavian',
            'p_tetjaadmin', 't_ojwse', 'm_lopata'}

    for em in C.prm_server.emojis:  #C.client.get_all_emojis():
        #print("'{0.id}': '{0.name}',".format(em))
        extra_em['<:{0}:{1}>'.format(em.name, em.id)] = em.name
        if em.id in ems_id:
            emojis[ems_id[em.id]] = em
            # emojis['<:{0}:{1}>'.format(em.id, ems_id[em.id])] = ems_id[em.id]
        elif not C.is_test:
            log.jW('{save_em} new smile '+str(em))

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
            await C.client.add_reaction(message, emoji)
            return

    if emoji in rand_em:
        chance = random.random()
        if chance <= 0.01:
            log.jD('Copy some reaction')
            await C.client.add_reaction(message, emoji)
            return

    if server.id == C.vtm_server.id:
        if emoji == e('Logo_Gangrel') and other.find(C.vtm_server.get_member(user.id).roles, id=C.roles['Gangrel']):
            log.jD('Copy Gangrel reaction')
            await C.client.add_reaction(message, emoji)

    # len(message.reactions) < 20
    # if str(user) == 'Kuro#3777':
    #     pass
    #     await C.client.add_reaction(message, random.choice(list(emojis.values())))
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


async def on_message(message, beckett_mention):
    prob = random.random()
    author = message.author.id

    if author == C.users['Natali']:
        if beckett_mention:
            log.jD('Like Natali for Beckett')
            await C.client.add_reaction(message, e('purple_heart')) #green_heart
        elif prob < 0.01:
            log.jD('Like Natali chance 0.01')
            await C.client.add_reaction(message, e('purple_heart'))
        return

    if author == C.users['Doriana']:
        if beckett_mention and prob < 0.1:
            log.jD('Like Doriana for Beckett chance 0.1')
            await C.client.add_reaction(message, e('octopus'))
        elif prob < 0.005:
            log.jD('Like Doriana chance 0.005')
            await C.client.add_reaction(message, e('black_heart'))
        return

    if author == C.users['Tony']:
        if beckett_mention and prob < 0.1:
            log.jD('Like Tony for Beckett chance 0.1')
            await C.client.add_reaction(message, e('Logo_Ventrue'))
        # elif prob < 0.005:
        #     log.jD('Like Tony chance 0.005')
        #     await C.client.add_reaction(message, e('ok_hand'))
        return

    if author == C.users['Rainfall']:
        if beckett_mention and prob < 0.1:
            log.jD('Like Rainfall for Beckett chance 0.1')
            await C.client.add_reaction(message, e('green_heart'))
        elif prob < 0.005:
            log.jD('Like Rainfall chance 0.005')
            await C.client.add_reaction(message, e('racehorse'))
        return

    if author == '237604798499651594': # Барон Рихтер
        await C.client.add_reaction(message, e('poop'))
