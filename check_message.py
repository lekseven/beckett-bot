# -*- coding: utf8 -*-

import discord
import re
import random
import data
import check_phrase
import local_memory as ram
import beckett_commands as cmd
import constants as C
import emj
import other


class Msg:

    def __init__(self, message):

        self.author = message.author.id
        self.message = message
        self.original = message.content
        self.text = message.content.lower().replace('ё', 'е')
        self.args = []
        self.words = set()
        self.channel = message.channel
        self.roles = {role.id for role in C.server.get_member(self.author).roles[1:]}
        self.prince = self.author == C.users['Natali']
        self.super = self.author in C.superusers or (
                self.prince or C.roles['Sheriff'] in self.roles or C.roles['Scourge'] in self.roles)
        self.torpor = (not self.prince and self.author in ram.torpor_users and (
                self.channel.id in ram.torpor_users[self.author] or 'All' in ram.torpor_users[self.author]))
        self.cmd_ch = ram.cmd_channels.get(self.author, set())
        self.rep_ch = ram.rep_channels.get(self.author, set())

    def prepare(self, fun=''):
        text = self.original[len('!' + fun + ' '):]  #self.text.replace('!' + fun + ' ', '')
        self.args = ([fun] or []) + text.split()
        self.words = set(self.args)

    def prepare2(self, fun=''):
        text = self.text.replace(fun, '')
        self.args = ([fun] or []) + text.translate(C.punct2space).split()
        self.words = set(self.args)

    async def delete(self):
        try:
            await C.client.delete_message(self.message)
        except discord.Forbidden:
            print("Bot haven't permissions here.")

    async def edit(self, new_msg):  #not permissions
        await C.client.edit_message(self.message, new_msg)

    async def type2sent(self, ch, text=None, emb=None, extra=0):
        if text is None:
            await C.client.send_message(ch, content=text, embed=emb)
            return 0

        t = min(1500, len(text)) / 20 + extra
        await C.client.send_typing(ch)
        for i in range(1, int(t / 10) + 1):
            C.loop.call_later(i * 10, lambda: C.loop.create_task(C.client.send_typing(ch)))
        C.loop.call_later(t, lambda: C.loop.create_task(C.client.send_message(ch, content=text, embed=emb)))
        return t

    async def report(self, text):
        for ch_id in self.rep_ch:
            ch = C.client.get_channel(ch_id) or other.get_user(ch_id)
            if ch:
                #await C.client.send_message(ch, text)
                await self.type2sent(ch, text)
        if self.channel.id not in self.rep_ch:
            #await C.client.send_message(self.channel, text)
            await self.type2sent(self.channel, text)

    async def answer(self, text=None, emb=None):
        if isinstance(text, list):
            t = 0
            for s in text:
                #await C.client.send_message(self.channel, content=s, embed=emb)
                t += await self.type2sent(self.channel, text=s, emb=emb, extra=t)
        else:
            #await C.client.send_message(self.channel, content=text, embed=emb)
            await self.type2sent(self.channel, text=text, emb=emb)

    async def qanswer(self, text):
        if isinstance(text, list):
            for s in text:
                await C.client.send_message(self.channel, s)
        else:
            await C.client.send_message(self.channel, text)

    async def say(self, channel, text):
        #await C.client.send_message(channel, text)
        await self.type2sent(channel, text)

    async def purge(self, channel, check_count=1, check=None, aft=None, bef=None):
        try:
            count = int(check_count)
        except:
            await self.qanswer('N должно быть числом!')
            return
        mess_count = 0
        auth = set()
        first, last = None, None
        async for mess in C.client.logs_from(channel, limit=count, before=bef, after=aft):
            if not check or check(mess):
                mess_count += 1
                auth.add(mess.author.id)
                if mess_count == 1:
                    first = mess.timestamp
                    last = mess.timestamp
                else:
                    if first > mess.timestamp:
                        first = mess.timestamp
                    elif last < mess.timestamp:
                        last = mess.timestamp
        if not mess_count:
            await self.qanswer('Не найдено сообщений для purge.')
            return
        else:
            text_mess = 'сообщение' if mess_count == 1 else 'сообшения' if mess_count < 5 else 'сообщений'
            list_auth = other.get_mentions(auth)
            yes = {'1', 'y', 'yes', 'да', 'у', '+'}
            await self.qanswer(
                'Вы уверены что хотите удалить {count} {text_mess} от {list_auth} с {first} по {last}? '
                '\n*(для согласия введите 1/y/yes/да/+)*'.format(
                    count=mess_count, text_mess=text_mess, list_auth=', '.join(list_auth),
                    first=first.strftime('{%x %X}'), last=last.strftime('{%x %X}')))
            ans = await C.client.wait_for_message(timeout=60, author=self.message.author, channel=self.channel)
            if ans and yes.intersection(ans.content.lower().split()):
                try:
                    await C.client.purge_from(channel, limit=count, check=check, after=aft, before=bef)
                except discord.Forbidden:
                    print("Bot haven't permissions here.")
                else:
                    await self.qanswer(":ok_hand:")
            else:
                await self.qanswer("Отмена purge.")


async def reaction(message):
    msg = Msg(message)

    if msg.torpor:
        await msg.delete()
        return

    if C.roles['Silence'] in msg.roles:
        await msg.delete()
        ram.silence_ans[msg.author] = ram.silence_ans.setdefault(msg.author, 0) + 1
        if ram.silence_ans[msg.author] < 4:
            msg.answer('Неугодный <@' + msg.author + '> пытается нам нечто сказать, но мы его не слышим...')
        return

    # delete messages containing forbidden links
    if not msg.super:
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
                msg.prepare(fun)
                await command(msg)
                return

    maybe_embrace = False
    if (ram.mute_channels.intersection(
            {msg.channel.id, 'All'}) or msg.author in ram.ignore_users or msg.channel.id in C.ignore_channels):
        if msg.channel.id == C.channels['ask']:
            maybe_embrace = True
        else:
            return

    msg.prepare2()
    beckett_reference = C.beckett_refs.intersection(msg.words)
    beckett_mention = C.beckett_names.intersection(msg.words)  #any(name in msg.args for name in C.beckett_names)
    found_keys = check_phrase.check_args(msg.words)
    prob = random.random()

    if msg.channel.id == C.channels['ask'] and not msg.roles.intersection(C.clan_ids):
        clan_keys = list(C.clan_names.intersection(found_keys))
        if clan_keys:
            C.loop.call_later(random.randrange(30, 90), lambda: C.loop.create_task(
                other.do_embrace_and_say(msg, msg.message.author, clan=random.choice(clan_keys))))

    elif maybe_embrace:
        return

    await emj.on_message(message, beckett_mention or beckett_reference)

    if not found_keys and (beckett_reference or (beckett_mention and random.random() < 0.25)):
        if msg.author == C.users['Natali'] and prob < 0.4:
            await msg.answer(random.choice(data.specialGreetings))
        else:
            await msg.answer(random.choice(data.responsesData['beckett']))
        return

    if found_keys:
        response = False

        if prob < 0.2 or beckett_reference or (beckett_mention and (prob < 0.9 or msg.super)):
            response = True

        if response:
            await msg.answer(random.choice(data.responsesData[random.choice(found_keys)]))
            return
    else:
        if '(╯°□°）╯︵ ┻━┻' in msg.original:
            ans = ''
            if prob < 0.25 or msg.super or msg.author == C.users['Buffy']:
                ans = '(╯°□°）╯︵ ┻━┻'
            elif prob > 0.75:
                ans = '┬─┬ ノ( ゜-゜ノ)'
            if ans:
                await msg.answer(ans)
                return

        if beckett_reference or (beckett_mention and random.random() < 0.25):
            if msg.author == C.users['Natali'] and prob < 0.4:
                ans = random.choice(data.specialGreetings)
            else:
                ans = random.choice(data.responsesData['beckett'])
            await msg.answer(ans)
            return
