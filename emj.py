from data_emoji import emojis
import constants as C
import local_memory as ram
import discord
import random

'''
Emojis [15.05.2018]:

<:drunk:400662865935204363>
<:Lacr:400662865972822026>
<:sad:400662866044387328>
<:nosferatu:400662866157502476>
<:janett:400662866371543040>
<:Lucta_de_Aragon:400664721155555328>
<:kama:418877362470518784>
<:torik1:418882342078119957>
<:torik2:418882717413933056>
<:Miliy_Tarkin:420657829007982593>
<:tarkinsredniy:421805633281720320>
<:torik2_1:421806514341281792>
<:Mishka2:421807340233293844>
<:7qht:421807808032407565>
<:301pxLogoSectSabbat:421813252251713548>
<:472pxLogoClanNosferatu:421813252289462273>
<:LogoClanFollowersofSet:421813252776001547>
<:LogoClanVentrue:421813252788322314>
<:LogoClanTremere:421813252822007823>
<:LogoClanRavnos:421813253102895104>
<:830pxLogoClanAssamite:421813253103157248>
<:LogoClanTzimisce:421813253186781194>
<:LogoClanMalkavian:421813253245501450>
<:LogoClanLasombra:421813253375524864>
<:LogoClanGangrel:421813253400821760>
<:LogoClanBrujah:421813253929435149>
<:jiznbol:421813696939950081>
<:LogoClanToreador:421814043465220105>
'''

# to color smile: smile[ok_hand]+skins[1]
skins = ['', '🏻', '🏼', '🏽', '🏾', '🏿']
rand_em = set()
name_em = {}


def save_em():
    special = {
        'Natali': {'purple_heart', 'kama', 'torik1', 'torik2_1', 'LogoClanToreador', },
        'Doriana': {'black_heart', 'octopus', 'unicorn', 'LogoClanLasombra', },
        'Tony': {'Lacr', 'ok_hand', 'thumbsup', 'LogoClanVentrue', },
        #'Kuro': {'point_up', 'LogoClanTremere', }, # for test
    }
    rand = {'jiznbol', '7qht', 'tarkinsredniy', 'slight_smile', 'joy', 'laughing', 'rofl',
               'smiley_cat', 'smile_cat', 'joy_cat', 'full_moon', 'full_moon_with_face', 'crescent_moon',
               'first_quarter_moon_with_face', 'last_quarter_moon_with_face', 'night_with_stars',
               'sun_with_face', 'sunny', 'sunrise_over_mountains', 'city_sunset', 'bat', 'LogoClanMalkavian', }

    for em in C.client.get_all_emojis():
        if em.id == '421806514341281792':
            emojis['torik2_1'] = em # has copy name torik2
        else:
            emojis[em.name] = em

    for name in special:
        name_em[C.users[name]] = set()
        for em_name in special[name]:
            if em_name in emojis:
                name_em[C.users[name]].add(emojis[em_name])
            else:
                print("Warn: can't find {0} in emojis (1)".format(em_name))

    for em in rand:
        if em in emojis:
            rand_em.add(emojis[em])
        else:
            print("Warn: can't find {0} in emojis (2)".format(em))


async def on_reaction_add(reaction, user):
    if user == C.server.me:
        return

    message = reaction.message
    emoji = reaction.emoji

    if user.id in ram.emoji_users and not message.channel.is_private:
        if discord.utils.get(message.reactions, emoji=emoji, me=True):
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

    if emoji == emojis['LogoClanGangrel'] and discord.utils.get(C.server.get_member(user.id).roles, id=C.roles['Gangrel']):
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
            await C.client.add_reaction(message, emojis['purple_heart']) #green_heart
        elif prob < 0.01:
            print('Like Natali chance 0.01')
            await C.client.add_reaction(message, emojis['purple_heart'])
        return

    if author == C.users['Doriana']:
        if beckett_mention and prob < 0.1:
            print('Like Doriana for Beckett chance 0.1')
            await C.client.add_reaction(message, emojis['octopus'])
        elif prob < 0.005:
            print('Like Doriana chance 0.005')
            await C.client.add_reaction(message, emojis['black_heart'])
        return

    if author == C.users['Tony']:
        if beckett_mention and prob < 0.1:
            print('Like Tony for Beckett chance 0.1')
            await C.client.add_reaction(message, emojis['LogoClanVentrue'])
        elif prob < 0.005:
            print('Like Tony chance 0.005')
            await C.client.add_reaction(message, emojis['ok_hand'])
        return