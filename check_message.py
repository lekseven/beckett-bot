# -*- coding: utf8 -*-

import discord
#import asyncio
import re
import random
import data
import check_phrase
import local_memory as ram
import beckett_commands as cmd
import constants as C


class Msg:

    def __init__(self, message):
        server = C.client.get_server(C.VTM_SERVER_ID)

        self.author = message.author.id
        self.message = message
        self.original = message.content
        self.text = message.content.lower().replace('ё', 'е')
        self.args = []
        self.words = set()
        self.channel = message.channel
        self.roles = [role.name for role in server.get_member(self.author).roles[1:]]
        self.prince = self.author == C.prince_id
        self.super = self.author in C.superusers or self.prince
        self.torpor = (not self.prince and self.author in ram.torpor_users and
                       (self.channel.id in ram.torpor_users[self.author] or 'All' in ram.torpor_users[self.author]))
        self.cmd_ch = ram.cmd_channels.get(self.author, set())
        self.rep_ch = ram.rep_channels.get(self.author, set())

    def prepare(self):
        self.args = self.text.translate(C.punct2space).split()
        self.words = set(self.args)

    async def delete(self):
        try:
            await C.client.delete_message(self.message)
        except discord.Forbidden:
            print("Bot haven't permissions here.")

    async def edit(self, new_msg): #not permissions
        await C.client.edit_message(self.message, new_msg)

    async def report(self, text):
        for ch_id in self.rep_ch:
            ch = C.client.get_channel(ch_id)
            if ch:
                await C.client.send_message(ch, text)
        if self.channel.id not in self.rep_ch:
            await C.client.send_message(self.channel, text)

    async def answer(self, text):
        await C.client.send_message(self.channel, text)

    async def say(self, channel, text):
        await C.client.send_message(channel, text)

    async def purge(self, channel, check_count=1, check=None):
        try:
            await C.client.purge_from(channel, limit=int(check_count), check=check)
        except discord.Forbidden:
            print("Bot haven't permissions here.")


async def reaction(message):
    msg = Msg(message)

    if msg.torpor:
        await msg.delete()
        return

    # delete messages containing forbidden links
    if not msg.super or True:
        if any(link in msg.text for link in data.forbiddenLinks):
            await msg.delete()
            return
        '''str = msg.text
        for link in data.forbiddenLinks:
            str = re.sub('(?i)'+link, "**`ЦЕНЗУРА`**", str)
        if str != msg.text:
            await msg.edit(str)
            return'''

    # if we have !cmd -> doing something
    if msg.text.startswith('!'):
        fun = re.match('!\w*', msg.text).group(0)[1:]
        if fun and hasattr(cmd, fun):
            command = getattr(cmd, fun)
            if callable(command) and (fun in C.free_cmds or msg.super):
                msg.prepare()
                await command(msg)
                return

    if ram.mute_channels.intersection({msg.channel.id, 'All'}) or msg.author in ram.ignore_users:
        return

    msg.prepare()
    beckett_mention = C.beckett_names.intersection(msg.words) #any(name in msg.args for name in C.beckett_names)
    found_key = check_phrase.check_args(msg.words)
    prob = random.random()

    if not found_key and beckett_mention:
        if msg.author == C.prince_id and prob < 0.4:
            await msg.answer(random.choice(data.specialGreetings))
        else:
            await msg.answer(random.choice(data.responsesData['beckett']))
        return

    if found_key:
        response = False

        if prob < 0.2 or (beckett_mention and prob < 0.9 or msg.author in C.superusers):
            response = True

        if response:
            await msg.answer(random.choice(data.responsesData[found_key]))

#    if 'Tremere' in memberRoles:
#        await client.send_message(message.channel, "О, я знаю, ты Тремер!")
