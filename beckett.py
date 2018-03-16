# -*- coding: utf8 -*-

import os
import random
import string
import sys

import discord

import checkPhrase
from data import *

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

client = discord.Client()

msgChannel = {}
torpor = set()

princeId = '109004244689907712'

superusers = {
    '119762429969301504',  # Rainfall
    '95525404592316416',   # Манф
    '414384012568690688',  # Kuro // just for testing, really
    '203539589284102144',  # Magdavius
    princeId
}

beckett_names = {
    'беккет',
    'бэккет',
    '419678772896333824',
    'beckett'
}

punct2space = str.maketrans(string.punctuation,' '*len(string.punctuation)) # for translate

# with open('torpor.json', 'r', encoding='utf-8') as torporFile:
#    torporData = json.load(torporFile)


@client.event
async def on_member_join(member):
    welcomeChannel = discord.Object(WELCOME_CHANNEL_ID)
    fmt = random.choice(welcomeMsgList)
    await client.send_message(welcomeChannel, fmt.format(member))


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    print('Message from {0.author}: {0.content}'.format(message))

    if message.author == client.user:
        return

    msg = message.content.lower().replace('ё', 'е')

    # delete messages containing forbidden links
    if message.author.id not in superusers:
        if any(link in msg for link in forbiddenLinks):
            await client.delete_message(message)
            return

    args = msg.translate(punct2space).split()

    """
    for word in filterData:
        if word.lower() in [x.lower() for x in args]:
            userid = message.author.id

            with open(warndb, 'r') as warnFile:
                warnData = json.load(warnFile)

            if userid in warnData:
                warnData[userid] += 1
            else:
                warnData[userid] = 1

            if warnData[userid] < 4:
                msg = message.author.name + random.choice([
                    ', мои здешние агенты докладывают, что в ночном воздухе носится нечно странное, похожее на угрозу или напряжение....\n',
                    ', не то чтобы я против брани, но здешнее руководство не одобряет.',
                    ', на твоем месте, неонат, я бы выбирал другие выражения.'
                ])
            else:
                msg = message.author.name + ', доброй ночи, дитя. Встречай свою Окончательную Cмерть.\n'

            await client.send_message(message.channel, msg)

            with open(warndb, 'w') as warnFile:
                json.dump(warnData, warnFile)

            if warnData[userid] > 3:
                warnData[userid] = 0
                with open(warndb, 'w') as warnFile:
                    json.dump(warnData, warnFile)
                await client.kick(message.author)

            await client.delete_message(message)
            break"""

    server = client.get_server(VTM_SERVER_ID)

    # Process commands
    if message.content.startswith('!channel'):
        global msgChannel

        if message.author.id not in superusers:
            await client.delete_message(message)
            return

        msgChannel[message.author.id] = args[1]
    elif message.content.startswith('!say'):
        if message.author.id not in superusers:
            await client.delete_message(message)
            return

        try:
            await client.send_message(discord.Object(msgChannel[message.author.id]), message.content.lstrip('!say '))
        except:
            await client.send_message(message.channel, 'Unknown channel.')
    elif message.content.startswith('!purge'):
        # !purge N - delete N last messages in chosen channel (from !channel)
        # !purge N ID - delete all messages by ID from in N last messages in chosen channel (from !channel)
        if message.author.id not in superusers:
            await client.delete_message(message)
            return
        try:
            if len(args) > 2:
                def check_user(m):
                    return m.author.id == args[2]

                await client.purge_from(discord.Object(msgChannel[message.author.id]), limit=int(args[1]),
                                        check=check_user)
            else:
                await client.purge_from(discord.Object(msgChannel[message.author.id]), limit=int(args[1]))
        except:
            await client.send_message(message.channel, 'Unknown channel.')
    elif message.content.startswith('!test'):
        # just test
        if message.author.id not in superusers:
            await client.delete_message(message)
            return
        ch = client.get_channel(msgChannel[message.author.id])  # discord.Object(msgChannel[message.author.id])
        await client.edit_channel(ch, **{'name': args[1], 'topic': ch.topic, 'user_limit': ch.user_limit,
                                         'bitrate': ch.bitrate})
    elif message.content.startswith('!roles'):
        if message.author.id not in superusers:
            await client.delete_message(message)
            return
        # member = server.get_member(args[1])
        member = server.get_member(args[1])
        # first role is always @everybody
        ans = ''
        if member:
            for role in member.roles[1:]:
                ans = ans + role.name + "\n"
        else:
            ans = 'Member is not found'
        await client.send_message(message.channel, ans)
    elif message.content.startswith('!roll'):
        for x in args:
            if 'd' in x:
                rollrange = x.split('d')
                if len(rollrange) == 2:
                    msg = ''
                    for z in range(0, int(rollrange[0])):
                        msg = msg + str(random.randrange(1, int(rollrange[1]) + 1)) + '\n'
                    await client.send_message(message.channel, msg)
    elif message.content.startswith('!deny'):
        global torpor

        if message.author.id not in superusers:
            await client.delete_message(message)
            return

        if 1 < len(args) and args[1] not in superusers and args[1] != client.user.id and args[1] != message.author.id:
            torpor.add(args[1])
            member = server.get_member(args[1])
            if member:
                channel = message.channel
                if message.author.id in msgChannel:
                    channel = discord.Object(msgChannel[message.author.id])
                await client.send_message(channel, "Сородич " + member.mention + " отправлен в торпор."
                                          + " Отныне он не произнесет ни слова.")
    elif message.content.startswith('!undeny'):
        if message.author.id not in superusers:
            await client.delete_message(message)
            return

        if 1 < len(args) and args[1] in torpor:
            torpor.remove(args[1])
            member = server.get_member(args[1])
            if member:
                channel = message.channel
                if message.author.id in msgChannel:
                    channel = discord.Object(msgChannel[message.author.id])
                await client.send_message(channel, "Сородич " + member.mention + " пробужден. Ему позволено говорить.")

    # Process plain messages
    if message.author.id in torpor:
        await client.delete_message(message)
        return

    beckett_mention = any(name in args for name in beckett_names)

    # first role is always @everybody
    member_roles = [role.name for role in server.get_member(message.author.id).roles[1:]]

    found_key = checkPhrase.checkArgs(args)

    if not found_key and beckett_mention:
        if message.author.id == princeId:
            await client.send_message(message.channel, random.choice(specialGreetings))
        else:
            await client.send_message(message.channel, random.choice(responsesData['beckett']))
        return

    if found_key:
        response = False
        prob = random.random()

        if prob < 0.2:
            response = True

        if beckett_mention:
            if message.author.id in superusers or prob < 0.9:
                response = True

        if response:
            await client.send_message(message.channel, random.choice(responsesData[found_key]))


#    if 'Tremere' in memberRoles:
#        await client.send_message(message.channel, "О, я знаю, ты Тремер!")

client.run(DISCORD_TOKEN)
