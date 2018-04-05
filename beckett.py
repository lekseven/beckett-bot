# -*- coding: utf8 -*-
import random
import data
import discord
import constants as C
import check_message
import other


# with open('torpor.json', 'r', encoding='utf-8') as torporFile:
#    torporData = json.load(torporFile)


@C.client.event
async def on_member_join(member):
    welcomeChannel = discord.Object(C.WELCOME_CHANNEL_ID)
    fmt = random.choice(data.welcomeMsgList)
    await C.client.send_message(welcomeChannel, fmt.format(member))


@C.client.event
async def on_ready():
    #C.channels['FM'] = C.client.get_channel('428784241656987669')
    print('Logged in as')
    print(C.client.user.name)
    print(C.client.user.id)
    print('------')


@C.client.event
async def on_message(message):
    # Log
    print('[{0}] <#{1.channel.name}> {1.author}: {1.content}'.
          format(message.timestamp.strftime("%H:%M:%S"), message))
    if message.attachments:
        attachments = []
        for att in message.attachments:
            attachments.append('\t\t' + att['url'])
        print('\n'.join(attachments))
    if message.embeds: # TODO Check and debug this block
        embeds = []
        i = 1
        for emb in message.embeds:
            embed = ['\tEmb_'+str(i)+':']
            embed += other.str_keys(emb, ['title', 'url', 'description'], '\t\t')
            if 'author' in emb:
                embed += ['\t\t[author]:']
                embed += other.str_keys(emb['author'], ['name', 'icon_url'], '\t\t\t')

            if emb.fields:
                j = 1
                for field in emb.fields:
                    embed += ['\t\t[field_' + str(j) + ']:']
                    embed += other.str_keys(field, ['name', 'value'], '\t\t\t')
                    j += 1

            if 'footer' in emb:
                embed += ['\t\t[footer]:']
                embed += other.str_keys(emb['footer'], ['icon_url', 'text'], '\t\t\t')

            i += 1
            embeds.append('\n'.join(embed))

        print('\n'.join(embeds))
    # End log

    if message.author == C.client.user or message.channel.id in C.ignore_channels:
        return

    # if message.author.id == '414384012568690688': # Kuro
    #     await C.client.send_file(message.channel, 'Beckett.jpg')
    #     return

    await check_message.reaction(message)


C.client.run(C.DISCORD_TOKEN)
