# -*- coding: utf8 -*-
import datetime as dt
import re
import random
import discord
import data
import check_phrase
import local_memory as ram
import beckett_commands as cmd
import constants as C
import emj
import other
import communication as com
import people
import log


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
        self.gt = people.get_gt(self.author)

    def prepare(self, fun=''):
        text = self.original[len('!' + fun + ' '):]  #self.text.replace('!' + fun + ' ', '')
        self.args = ([fun] or []) + text.split()
        self.words = set(self.args).difference({'', ' '})

    def prepare2(self, fun=''):
        text = self.text.replace(fun, '')
        self.args = ([fun] or []) + text.translate(C.punct2space).split()
        self.words = set(self.args).difference({'', ' '})

    async def delete(self):
        try:
            await C.client.delete_message(self.message)
        except discord.Forbidden:
            log.jW("Bot haven't permissions here.")

    async def edit(self, new_msg):  #not permissions
        await C.client.edit_message(self.message, new_msg)

    async def type2sent(self, ch, text=None, emb=None, extra=0):
        if text is None:
            await C.client.send_message(ch, content=text, embed=emb)
            return 0

        t = min(1500, len(text)) / 20 + extra
        await C.client.send_typing(ch)
        for i in range(1, int(t / 10) + 1):
            other.later(i * 10, C.client.send_typing(ch))
        other.later(t, C.client.send_message(ch, content=text, embed=emb))
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
        except Exception as e:
            other.pr_error(e, 'purge')
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
            yes = await self.question(
                'Вы уверены что хотите удалить {count} {text_mess} от {list_auth} с {first} по {last} в <#{channel}>? '
                .format(
                    count=mess_count, text_mess=text_mess, list_auth=', '.join(list_auth),
                    first=other.t2s(first, '{%x %X}'), last=other.t2s(last, '{%x %X}'), channel=channel.id))
            if yes:
                try:
                    await C.client.purge_from(channel, limit=count, check=check, after=aft, before=bef)
                except discord.Forbidden:
                    log.jW("Bot haven't permissions here.")
                else:
                    await self.qanswer(":ok_hand:")
            else:
                await self.qanswer("Отмена purge.")

    async def question(self, text):
        yes = {'1', 'y', 'yes', 'да', 'у', '+'}
        await self.qanswer(text + '\n*(для согласия введите 1/y/yes/да/+)*')
        ans = await C.client.wait_for_message(timeout=60, author=self.message.author, channel=self.channel)
        return ans and yes.intersection(ans.content.lower().split())


async def reaction(message):
    msg = Msg(message)

    if msg.author == C.users['bot']:
        if msg.original == data.tremer_joke:
            other.later(20, msg.delete())
        return

    # TO#DO del check me =)
    # if msg.author != C.users['Kuro']:
    #     return # for test

    if msg.torpor:
        await msg.delete()
        return

    if C.roles['Silence'] in msg.roles:
        await msg.delete()
        ram.silence_ans[msg.author] = ram.silence_ans.setdefault(msg.author, 0) + 1
        if ram.silence_ans[msg.author] < 4:
            await msg.answer('Неугодный <@' + msg.author + '> пытается нам нечто сказать, но мы его не слышим...')
        return

    # delete messages containing forbidden links
    if not msg.super:
        if any(link in msg.text for link in data.forbiddenLinks):
            await msg.delete()
            await msg.answer(random.choice(data.threats).format(name=msg.author))
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
    if (ram.mute_channels.intersection({msg.channel.id, 'All'})
            or msg.author in ram.ignore_users or msg.channel.id in C.ignore_channels):
        if msg.channel.id == C.channels['ask']:
            maybe_embrace = True
        else:
            return

    msg.prepare2()
    beckett_reference = bool(C.beckett_refs.intersection(msg.words))
    beckett_mention = bool(C.beckett_names.intersection(msg.words))  #any(name in msg.args for name in C.beckett_names)
    beckett = beckett_reference or beckett_mention
    found_keys = check_phrase.check_args(msg.words)
    prob = random.random()

    if msg.channel.id == C.channels['ask'] and not msg.roles.intersection(C.clan_ids):
        clan_keys = list(C.clan_names.intersection(found_keys))
        if clan_keys:
            other.later(random.randrange(30, 90),
                        other.do_embrace_and_say(msg, msg.author, clan=random.choice(clan_keys)))

    elif maybe_embrace:
        return

    await emj.on_message(message, beckett)

    if found_keys:
        response = False

        if prob < 0.2 or beckett_reference or (beckett_mention and (prob < 0.9 or msg.super)):
            response = True

        if response:
            await msg.answer(random.choice(data.responsesData[random.choice(found_keys)]))
            return
    else:
        if '(╯°□°）╯︵ ┻━┻' in msg.original or '(╯°益°)╯彡┻━┻' in msg.original:
            ans = ''
            if msg.super or msg.author == C.users['Buffy']:
                ans = '(╯°□°）╯︵ ┻━┻'
            elif prob > 0.2:
                ans = '┬─┬ ノ( ゜-゜ノ)'
            if ans:
                await msg.answer(ans)
                return

        gt_key = com.f_gt_key(msg.original, msg.text, msg.words, beckett)
        if gt_key:
            h18 = 64800  # 18h in sec
            if (dt.datetime.now().timestamp() - msg.gt[gt_key['g_key']]) > h18: # not beckett and
                phr = random.choice(com.good_time[gt_key['g_key']][gt_key['g_type']]['response'])
                str_weather = ''
                if gt_key['g_key'] == 'g_morn' and msg.author in com.morning_add:
                    phr += ' ' + com.morning_add[msg.author]
                    if msg.author == C.users['Natali']:
                        try:
                            log.I('try get_weather for Natali')
                            str_weather = '\n:newspaper: ' + other.get_weather()
                        except Exception as e:
                            other.pr_error(e, 'get_weather')

                await msg.answer(other.name_phr(msg.author, phr) + str_weather)
                people.set_gt(msg.author, gt_key['g_key'])
            return

        if beckett:
            yes = 'да' in msg.words
            no = 'не' in msg.words or 'нет' in msg.words
            ans = ''
            if msg.words.intersection({'спасибо', 'благодарю'}):    #'спасибо'
                ans = other.name_rand_phr(msg.author, data.sm_resp['wlc'])
            elif msg.words.intersection(data.sm_resp['hi']) or msg.words.intersection(data.sm_resp['hi_smiles']):
                m = data.sm_resp['hi'].copy()
                m.append([(':' + w + ':') for w in data.sm_resp['hi_smiles']])
                ans = other.name_rand_phr(msg.author, m)
            elif msg.words.intersection(data.sm_resp['bye']):
                ans = other.name_rand_phr(msg.author, data.sm_resp['bye'])
            elif msg.words.intersection(data.sm_resp['love']) and not no:
                if msg.author == C.users['Natali']:
                    ans = ':purple_heart:'
                else:
                    ans = ':heart:'
            elif 'любимый клан' in msg.text:
                if prob > 0.09:
                    ans = random.choice(data.sm_resp['apoliticality'])
                else:
                    ans = data.tremer_joke
            elif msg.words.intersection(data.sm_resp['bot_dog']):
                if msg.super or prob > 0.2:
                    ans = other.name_rand_phr(msg.author, data.sm_resp['not_funny'])
                else:
                    ans = random.choice(data.threats).format(name=msg.author)
            elif yes != no and msg.text.endswith('?') and msg.super:
                if yes:
                    ans = other.name_rand_phr(msg.author, data.sm_resp['yes'])
                else:
                    ans = other.name_rand_phr(msg.author, data.sm_resp['no'])
            elif 'мимими' in msg.text:
                return

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
