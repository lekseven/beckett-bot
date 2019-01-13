# -*- coding: utf8 -*-
import re
import random
import discord
import data
import local_memory as ram
import beckett_commands as cmd
import constants as C
import emj
import manager
import other
import communication as com
import people
import log


class Msg:

    def __init__(self, message):
        """

        :type message: discord.Message
        """
        self.author = message.author.id
        self.member = C.vtm_server.get_member(self.author)
        self.personal = not message.server
        self.cmd_server = ((self.author in ram.cmd_server and C.client.get_server(ram.cmd_server[self.author])) or
                           (C.prm_server if self.personal else message.server))
        self.server_id = None if self.personal else message.server.id
        self.is_vtm = self.server_id == C.vtm_server.id
        self.is_tst = self.server_id == C.tst_server.id
        self.message = message
        self.original = message.content
        self.text = message.content.lower().replace('ё', 'е')
        self.args = []
        self.words = set()
        self.channel = message.channel
        self.roles = {role.id for role in self.member.roles[1:]} if (self.member and self.is_vtm) else set()
        self.prince = self.author == C.users['Natali']
        self.super = self.author in C.superusers
        self.admin = self.super or self.prince or self.roles.intersection({C.roles['Sheriff'], C.roles['Scourge']})
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
        return await other.type2sent(ch, text, emb, extra)

    async def report(self, text):
        for ch_id in self.rep_ch:
            ch = C.client.get_channel(ch_id) or other.find_user(ch_id)
            if ch:
                #await C.client.send_message(ch, text)
                await self.type2sent(ch, text)
        if self.channel.id not in self.rep_ch:
            #await C.client.send_message(self.channel, text)
            await self.type2sent(self.channel, text)

    async def answer(self, text=None, emb=None):
        t = 0
        for txt in other.split_text(text):
            t += await self.type2sent(self.channel, text=txt, emb=emb, extra=t)
        return t

    async def qanswer(self, text):
        for t in other.split_text(text):
            await C.client.send_message(self.channel, t)

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
                'Вы уверены что хотите удалить {count} {text_mess} от {list_auth} с {first} по {last} в {channel}? '
                .format(
                    count=mess_count, text_mess=text_mess, list_auth=', '.join(list_auth),
                    first=other.t2s(first, '{%x %X}'), last=other.t2s(last, '{%x %X}'), channel=channel))
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

    def find_member(self, i):
        return other.find_member(self.cmd_server, i)

    def find_members(self, names):
        return other.find_members(self.cmd_server, names)

    def get_commands(self):
        #module_attrs = dir(cmd)
        #cmds = set(key for key in module_attrs if key[0] != '_' and callable(getattr(cmd, key)))
        cmds = cmd.all_cmds.copy()
        if self.channel.id == C.channels['primogens']:
            cmds.intersection_update(cmd.primogenat_cmds)
        elif self.admin and (not self.super or (not self.personal and not self.is_tst)):
            cmds.intersection_update(cmd.admin_cmds)
        elif not self.admin:
            free = cmd.free_cmds
            if {self.author}.intersection({C.users['Creol'], C.users['Tony']}):
                free.add('dominate')
            cmds.intersection_update(free)

        return cmds


async def reaction(message):
    msg = Msg(message)

    if msg.is_vtm:
        people.set_last_m(msg.author)

    if msg.author == C.users['bot']:
        if msg.original == data.tremer_joke:
            other.later_coro(20, msg.delete())
        return

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
    if not msg.admin:
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
        if fun in msg.get_commands():
            msg.prepare(fun)
            await getattr(cmd, fun)(msg)
            return
        # if fun and hasattr(cmd, fun):
        #     command = getattr(cmd, fun)
        #     if callable(command) and (fun in C.free_cmds or msg.admin):
        #         msg.prepare(fun)
        #         await command(msg)
        #         return

    embrace_or_return = False
    if (ram.mute_channels.intersection({msg.channel.id, 'all'})
            or msg.author in ram.ignore_users or msg.channel.id in C.ignore_channels):
        if msg.channel.id == C.channels['ask']:
            embrace_or_return = True
        else:
            return

    msg.prepare2()
    beckett_reference = bool(C.beckett_refs.intersection(msg.words))
    beckett_mention = bool(C.beckett_names.intersection(msg.words))  #any(name in msg.args for name in C.beckett_names)
    beckett = beckett_reference or beckett_mention
    # found_keys = check_phrase.check_args(msg.words)
    found_keys = com.check_phrase(msg.text, msg.words)
    prob = random.random()

    # embrace
    if msg.channel.id == C.channels['ask'] and not msg.roles.intersection(C.clan_ids):
        clan_keys = list(C.clan_names.intersection(found_keys))
        if clan_keys:
            other.later_coro(random.randrange(30, 90),
                             manager.do_embrace_and_say(msg, msg.author, clan=random.choice(clan_keys)))
    elif embrace_or_return:
        return

    await emj.on_message(message, beckett)

    if found_keys:
        if not beckett and ram.mute_light_channels.intersection({msg.channel.id, 'all'}):
            return
        response = False

        if prob < 0.2 or beckett_reference or (beckett_mention and (prob < 0.9 or msg.admin)):
            response = True

        if response:
            ans_phr = com.get_resp(found_keys)
            await msg.answer(ans_phr['text'])
            return
    else:
        ans = ''
        if '╯' in msg.original:
            if '┻' in msg.original:
                if msg.admin:
                    ans = other.rand_tableflip()
                elif msg.channel.id == C.channels['bar']:
                    if {msg.author}.intersection({C.users['Buffy'], C.users['Tilia'], }):
                        ans = other.rand_tableflip()
                    else:
                        return
                else:
                    ans = '┬─┬ ノ( ゜-゜ノ)'
            else:
                dice_count = msg.original.count('dice') + msg.original.count('🎲')
                if dice_count > 0:
                    ans = other.rand_diceflip(dice_count)
        elif msg.original[1:].startswith('tableflip') and (msg.admin or msg.channel.id == C.channels['bar']):
            ans = '* *бросаю за <@{id}>* *\n{table}'.format(id=msg.author, table=other.rand_tableflip())

        if ans:
            await msg.answer(ans)
            return

        gt_key = com.f_gt_key(msg.original, msg.text, msg.words.copy(), beckett)
        if gt_key:
            h18 = 64800  # 18h in sec
            if (other.get_sec_total() - msg.gt[gt_key['g_key']]) > h18: # not beckett and
                phr = random.choice(com.good_time[gt_key['g_key']][gt_key['g_type']]['response'])
                str_weather = ''
                if gt_key['g_key'] == 'g_morn' and msg.author in com.morning_add:
                    phr += ' ' + com.morning_add[msg.author]
                    if msg.author == C.users['Natali']:
                        try:
                            log.I('try get_weather for Natali')
                            str_weather = '\n:newspaper: ' + manager.get_weather()
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
                m += data.sm_resp['hi_smiles'].copy()
                ans = other.name_rand_phr(msg.author, m)
            elif msg.words.intersection(data.sm_resp['bye']):
                ans = other.name_rand_phr(msg.author, data.sm_resp['bye'])
            elif (msg.words.intersection(data.sm_resp['love']) or msg.words.intersection(emj.hearts)) and not no:
                if msg.author == C.users['Natali']:
                    ans = ':purple_heart:'
                else:
                    ans = ':heart:'
                ans = other.name_phr(msg.author, ans)
            elif 'любимый клан' in msg.text:
                if prob > 0.09:
                    ans = random.choice(data.sm_resp['apoliticality'])
                else:
                    ans = data.tremer_joke
            elif msg.words.intersection(data.sm_resp['bot_dog']):
                if msg.admin or prob > 0.2:
                    ans = other.name_rand_phr(msg.author, data.sm_resp['not_funny'])
                else:
                    ans = random.choice(data.threats).format(name=msg.author)
            elif msg.words.intersection({'как'}) and msg.words.intersection({'дела', 'ты'}):
                ans = random.choice(data.responses['whatsup'])
            # other questuons must be before this
            elif msg.text.endswith('?'):
                if msg.admin:
                    if (yes == no) or yes:
                        ans = other.name_rand_phr(msg.author, data.sm_resp['yes'])
                    else:
                        ans = other.name_rand_phr(msg.author, data.sm_resp['no'])
                elif len(msg.args) > 3:
                    ans = random.choice(data.responses['question'])
            elif msg.words.intersection({'скучал', 'скучала', 'скучаль'}):
                ans = other.name_phr(msg.author, 'я тоже')
            elif ('мимими' in msg.text) or len(msg.args) < 4:
                return

            if ans:
                await msg.answer(ans)
                return

        if beckett_reference or (beckett_mention and random.random() < 0.25):
            if msg.author == C.users['Natali'] and prob < 0.4:
                ans_phr = com.get_resp(['For_Prince'])
            else:
                ans_phr = com.get_resp(['beckett'])
            ans = ans_phr['text']
            await msg.answer(ans)
            return
