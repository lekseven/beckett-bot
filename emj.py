from data_emoji import emojis
import constants as C
import local_memory as ram
import other
import random

# Emojis [31.05.2018]:
ems_id = {
    '400662865935204363': 'm_drunk',
    '400662865972822026': 'p_Lacr',
    '400662866044387328': 'p_sad',
    '400662866157502476': 'p_nosferatu',
    '400662866371543040': 'p_janett',
    '400664721155555328': 'p_Lucta_de_Aragon',
    '418877362470518784': 'Ankh',
    '418882342078119957': 't_torik11',
    '418882717413933056': 'm_torik12',
    '420657829007982593': 'm_Tarkin_Miliy',
    '421805633281720320': 'm_Tarkin_f',
    '421806514341281792': 't_torik21',
    '421807340233293844': 'm_torik22',
    '421807808032407565': 't_jiznbol2',
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
    '448237255484506134': 'p_beckett2',
    '448244001703723018': 't_ojwse',
    '451506010054590464': 'Ankh_Toreador',
    '451507128004509697': 'Ankh_Anarch',
    '451507784454766603': 'Ankh_Cama',
    '451510597503287296': 'Ankh_Ashirra',
    '451513393753620482': 'Ankh_Setite',
    '451514227971194900': 'Ankh_Davis',
    '451515142107299850': 'Aankh_GD',
    '451520926471946242': 'Logo_Caitiff',
    '451520970377789440': 'Logo_Giovanni',
    '451534670325088287': '0_Demonic_Skeleton',
    '451537898504716289': '0_GDAbyudG',
    '452982621509779456': 'p_cthulhu',
    '452985737000910859': 'p_cthulhu_head',
}

# to color smile: smile[ok_hand]+skins[1]
skins = ['', '🏻', '🏼', '🏽', '🏾', '🏿']
rand_em = set()
name_em = {}


def e(name):
    if name in emojis:
        return emojis[name]
    else:
        print('Warn: [e] there no emoji ' + name)
        return None


def save_em():
    special = {
        'Natali': {'purple_heart', 'Ankh', 'Ankh_Toreador', 't_torik11', 't_torik21', 'Logo_Toreador', },
        'Doriana': {'black_heart', 'octopus', 'unicorn', 'Logo_Lasombra', },
        'Tony': {'p_Lacr', 'ok_hand', 'thumbsup', 'Logo_Ventrue', },
        'Manf': {'m_draniki', 'm_bulba', 'star_and_crescent'},
        #'Kuro': {'point_up', 'Logo_Tremere', }, # for test
    }
    rand = {'t_jiznbol1', 't_jiznbol2', 'm_Tarkin_f', 'slight_smile', 'joy', 'laughing', 'rofl',
               'smiley_cat', 'smile_cat', 'joy_cat', 'full_moon', 'full_moon_with_face', 'crescent_moon',
               'first_quarter_moon_with_face', 'last_quarter_moon_with_face', 'night_with_stars',
               'sun_with_face', 'sunny', 'sunrise_over_mountains', 'city_sunset', 'bat', 'Logo_Malkavian',
            'p_tetjaadmin', 't_ojwse', 'm_lopata'}

    for em in C.server.emojis:  #C.client.get_all_emojis():
        #print("'{0.id}': {0.name},".format(em))
        if em.id in ems_id:
            emojis[ems_id[em.id]] = em
        else:
            print('Warn: new smile '+str(em))


    for name in special:
        name_em[C.users[name]] = set()
        for em_name in special[name]:
            em = e(em_name)
            if em:
                name_em[C.users[name]].add(em)
            else:
                print("Warn: can't find {0} in emojis (1)".format(em_name))

    for em_name in rand:
        em = e(em_name)
        if em:
            rand_em.add(em)
        else:
            print("Warn: can't find {0} in emojis (2)".format(em_name))


async def on_reaction_add(reaction, user):
    if user == C.server.me:
        return

    message = reaction.message
    emoji = reaction.emoji

    if user.id in ram.emoji_users and not message.channel.is_private:
        if other.find(message.reactions, emoji=emoji, me=True):
            await C.client.remove_reaction(message, emoji, user)
            await C.client.remove_reaction(message, emoji, C.server.me)
        else:
            await C.client.remove_reaction(message, emoji, user)
            await C.client.add_reaction(message, emoji)
        return

    if message.author == C.server.me or message.author == user:
        return

    if user.id in name_em:
        # emoji[0] because it can be different colors
        if (isinstance(emoji, str) and emoji[0] in name_em[user.id]) or emoji in name_em[user.id]:
            print('Copy special reaction')
            await C.client.add_reaction(message, emoji)
            return

    if emoji in rand_em:
        chance = random.random()
        if chance <= 0.01:
            print('Copy some reaction')
            await C.client.add_reaction(message, emoji)
            return

    if emoji == e('Logo_Gangrel') and other.find(C.server.get_member(user.id).roles, id=C.roles['Gangrel']):
        print('Copy Gangrel reaction')
        await C.client.add_reaction(message, emoji)

    # len(message.reactions) < 20
    # if str(user) == 'Kuro#3777':
    #     pass
    #     await C.client.add_reaction(message, random.choice(list(emojis.values())))
    #     #await C.client.add_reaction(message, emojis['LogoClanTremere'])


async def on_reaction_remove(reaction, user):
    if user == C.server.me:
        return

    message = reaction.message
    emoji = reaction.emoji

    if message.author == C.server.me or message.author == user:
        return

    if user.id in name_em:
        # emoji[0] because it can be different colors
        if (isinstance(emoji, str) and emoji[0] in name_em[user.id]) or emoji in name_em[user.id]:
            print('Remove special reaction')
            await C.client.remove_reaction(message, emoji, C.server.me)

    # if str(user) == 'Kuro#3777':
    #     await C.client.remove_reaction(message, emoji, C.server.me)


async def on_message(message, beckett_mention):
    prob = random.random()
    author = message.author.id

    if author == C.users['Natali']:
        if beckett_mention:
            print('Like Natali for Beckett')
            await C.client.add_reaction(message, e('purple_heart')) #green_heart
        elif prob < 0.01:
            print('Like Natali chance 0.01')
            await C.client.add_reaction(message, e('purple_heart'))
        return

    if author == C.users['Doriana']:
        if beckett_mention and prob < 0.1:
            print('Like Doriana for Beckett chance 0.1')
            await C.client.add_reaction(message, e('octopus'))
        elif prob < 0.005:
            print('Like Doriana chance 0.005')
            await C.client.add_reaction(message, e('black_heart'))
        return

    if author == C.users['Tony']:
        if beckett_mention and prob < 0.1:
            print('Like Tony for Beckett chance 0.1')
            await C.client.add_reaction(message, e('Logo_Ventrue'))
        elif prob < 0.005:
            print('Like Tony chance 0.005')
            await C.client.add_reaction(message, e('ok_hand'))
        return

    if author == C.users['Rainfall']:
        if beckett_mention and prob < 0.1:
            print('Like Rainfall for Beckett chance 0.1')
            await C.client.add_reaction(message, e('green_heart'))
        elif prob < 0.005:
            print('Like Rainfall chance 0.005')
            await C.client.add_reaction(message, e('green_heart'))
        return

    if author == '237604798499651594': # Барон Рихтер
        await C.client.add_reaction(message, e('poop'))