# -*- coding: utf8 -*-
import random
import data
import discord
import constants as C
import check_message


# with open('torpor.json', 'r', encoding='utf-8') as torporFile:
#    torporData = json.load(torporFile)


@C.client.event
async def on_member_join(member):
    welcomeChannel = discord.Object(C.WELCOME_CHANNEL_ID)
    fmt = random.choice(data.welcomeMsgList)
    await C.client.send_message(welcomeChannel, fmt.format(member))


@C.client.event
async def on_ready():
    print('Logged in as')
    print(C.client.user.name)
    print(C.client.user.id)
    print('------')


@C.client.event
async def on_message(message):
    print('[{0}] <#{1.channel.name}> {1.author}: {1.content}'.
          format(message.timestamp.strftime("%H:%M:%S"), message))

    if message.author == C.client.user:
        return

    await check_message.reaction(message)


C.client.run(C.DISCORD_TOKEN)
