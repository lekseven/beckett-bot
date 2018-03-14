# -*- coding: utf8 -*-

import discord
import random
import json
import string
import os
import sys
import checkPhrase

from data import *

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN', None)

if DISCORD_TOKEN is None:
    print('Config var DISCORD_TOKEN is not defined.')
    sys.exit()

VTM_SERVER_ID = os.environ.get('VTM_SERVER_ID', None)

if VTM_SERVER_ID is None:
    print('Config var VTM_SERVER_ID is not defined.')
    sys.exit()
    
WELCOME_CHANNEL_ID = os.environ.get('WELCOME_CHANNEL_ID', None)

if WELCOME_CHANNEL_ID is None:
    print('Config var WELCOME_CHANNEL_ID is not defined.')
    sys.exit()

client = discord.Client()

msgChannel = {}
torpor = set()
serverMembers = {}

creatorId = '203539589284102144'
princeId = '109004244689907712'

superusers = {
    '119762429969301504',  # Rainfall
    '95525404592316416',   # Манф
    '414384012568690688',  # Kuro // just for testing, really 
    creatorId,
    princeId
}

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

    server = client.get_server(VTM_SERVER_ID)

    for member in server.members:
        serverMembers[member.id] = member
      
#    serverRoles = []
#    for role in server.roles:
#        serverRoles.append(role.name)
#    print(serverRoles)
#   ['Prince', 'Sheriff', 
#    'Seneschal', 'Tzimisce', 'Malkavian', 'Lasombra', 'Toreador', 'Brujah', 'Ravnos', 'Ventrue', 'Nosferatu', 
#    'Gangrel', 'Tremere', 'Beckett', 'Followers of Set', 'Assamite', 'Giovanni', 'Noble Pander', 
#    'Primogens and Emissary', 'Harpy', 'Beckett', 'New World Order', 'Lasombra Antitribu', 'Scourge', 
#    'Cappadocian', 'Sabbat', 'Anarch']
    


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content.lower()
    msg = msg.replace('ё', 'е')
    for ch in string.punctuation:
        msg = msg.replace(ch, ' ')
    args = msg.split()

    print('Message from {0.author}: {0.content}'.format(message))
    # print(args)

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
        # !purge N - delete N last messages in chosen chanell (from !channel)
        # !purge N ID - delete all messages by ID from in N last messages in chosen chanell (from !channel)
        if message.author.id not in superusers:
            await client.delete_message(message)
            return
        try:
            if len(args)>2:
                def check_user(m):
                     return m.author.id == args[2]
                    
                await client.purge_from(discord.Object(msgChannel[message.author.id]), limit=int(args[1]),check=check_user)
            else: await client.purge_from(discord.Object(msgChannel[message.author.id]), limit=int(args[1]))    
        except:
            await client.send_message(message.channel, 'Unknown channel.')
    elif message.content.startswith('!test'):
        # just test
        if message.author.id not in superusers:
            await client.delete_message(message)
            return
        
        ans = ""
        i = 0
        for arg in args:
            ans = ans+str(i)+") "+str(arg)+"\n"
            i = i+1
            
        await client.send_message(message.channel, ans)
    elif message.content.startswith('!roles'):
        if message.author.id not in superusers:
            await client.delete_message(message)
            return
        #member = server.get_member(args[1])
        member = serverMembers[args[1]]
        # first role is always @everybody
        ans=''
        if member:
            for role in member.roles[1:]:
                ans = ans+role.name+"\n"
        else: ans = 'Member is not found'
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
            if args[1] in serverMembers:
                await client.send_message(message.channel,
                                          "Сородич " + serverMembers[args[1]].mention
                                          + " отправлен в торпор по поручению Князя."
                                          + " Отныне он не произнесет ни слова.")
    elif message.content.startswith('!undeny'):
        if message.author.id not in superusers:
            await client.delete_message(message)
            return

        if 1 < len(args) and args[1] in torpor:
                torpor.remove(args[1])
                await client.send_message(message.channel,
                                          "Сородич " + serverMembers[args[1]].mention
                                          + " пробужден. Теперь он может говорить.")

    # Process plain messages
    if message.author.id in torpor:
        await client.delete_message(message)
        return

    found_key = ''
    beckettMention = 'беккет' in args or 'бэккет' in args or '419678772896333824' in args or 'beckett' in args 
    
    member = serverMembers[args[1]]
        # first role is always @everybody
        # message.author.roles
        memberRoles = set()
        for role in message.author.roles[1:]:
            memberRoles.add(role.name)
#    for key in args:
#        if key in responsesData:
#            found_key = key
#            break
    found_key = checkPhrase.checkArgs(args)

    if not found_key and beckettMention:
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

        if beckettMention:
            if message.author.id in superusers or prob < 0.9:
                response = True

        if response:
            await client.send_message(message.channel, random.choice(responsesData[found_key]))
            
        if 'Tremere' in memberRoles:
            await client.send_message(message.channel, "О, я знаю, ты Тремер!")

client.run(DISCORD_TOKEN)
