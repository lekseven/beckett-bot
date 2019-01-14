import discord
import random
import operator
import lxml.html
import requests
import re

import data
import other
import constants as C
import local_memory as ram
import communication as com
import log
import emj
import people


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

    def _after_init(self):
        if self.is_vtm:
            people.set_last_m(self.author)

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

    @staticmethod
    async def type2sent(ch, text=None, emb=None, extra=0):
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

    def check_good_time(self, beckett):
        gt_key = com.f_gt_key(self.original, self.text, self.words.copy(), beckett)
        if gt_key:
            h18 = 64800  # 18h in sec
            if (other.get_sec_total() - self.gt[gt_key['g_key']]) > h18: # not beckett and
                phr = random.choice(com.good_time[gt_key['g_key']][gt_key['g_type']]['response'])
                str_weather = ''
                if gt_key['g_key'] == 'g_morn' and self.author in com.morning_add:
                    phr += ' ' + com.morning_add[self.author]
                    if self.author == C.users['Natali']:
                        try:
                            log.I('try get_weather for Natali')
                            str_weather = '\n:newspaper: ' + get_weather()
                        except Exception as e:
                            other.pr_error(e, 'get_weather')
                people.set_gt(self.author, gt_key['g_key'])
                return other.name_phr(self.author, phr) + str_weather
        return False

    def get_commands(self):
        # it's rewrite in check_message
        pass


async def turn_silence(user, turn=True, server=None, check=None, force=False):
    change_pr = ('send_messages', 'add_reactions',)
    server = server or C.prm_server
    new_pr = False if turn else None
    check = set(check or ())
    for ch in server.channels:  # type: discord.Channel
        if str(ch.type) == 'text':
            bot_prm = ch.permissions_for(server.me)
            if bot_prm.manage_roles:
                add_ch = False
                prm = ch.overwrites_for(user)
                for pr in change_pr:
                    if force or ((turn and getattr(prm, pr) is None) or
                                 (not turn and getattr(prm, pr) is False and ch.id not in check)):
                        setattr(prm, pr, new_pr)
                        add_ch = True
                if add_ch:
                    if prm.is_empty():
                        await C.client.delete_channel_permissions(ch, user)
                    else:
                        await C.client.edit_channel_permissions(ch, user, overwrite=prm)
                else:
                    check.add(ch.id)
    return check


async def silence_on(name, t=1.0, force=False):
    """
    :param name: string
    :param t: float
    :param force: bool
    :rtype: discord.Member
    """
    s = C.prm_server
    user = other.find_member(s, name)
    if not user:
        return None

    if user.top_role >= s.me.top_role and not force:
        return False

    t = max(t, 0.02)
    if user.id in ram.silence_users:
        check = ram.silence_users[user.id]['check']
    else:
        check = await turn_silence(user, turn=True, force=force)
    ram.silence_users[user.id] = {'time': other.get_sec_total() + t * 3600 - 1, 'check': tuple(check)}
    if not C.is_test:
        add_roles = [other.find(s.roles, id=C.roles['Silence'])]
        await C.client.add_roles(user, *add_roles)
    log.I('Silence on for ', user, ' at ', other.t2s(), ' on ', t, 'h.')
    return user


async def silence_off(name):
    """
    :param name: string
    :rtype: discord.Member
    """
    s = C.prm_server
    user = other.find_member(s, name)
    if not user:
        ram.silence_users.pop(name, 0)
        return None

    s_user = ram.silence_users.pop(user.id, False)
    if s_user:
        await turn_silence(user, turn=False, check=s_user['check'])
        if not C.is_test:
            rem_roles = [other.find(s.roles, id=C.roles['Silence'])]
            await C.client.remove_roles(user, *rem_roles)
        log.I('Silence off for ', user, ' at ', other.t2s())
        return user
    else:
        return False


async def silence_end(name):
    user = await silence_off(name)
    if user:
        await C.client.send_message(C.main_ch, content='<@{0}>, твой период молчанки подошёл к концу.'.format(user.id))
    else:
        log.W('End silence for ', name, ", but can't find user.")


async def voting(channel, text='', timeout=60, votes=None, count=3):
    votes = votes or set()
    text = text + '\n*(для согласия введите за/y/yes/д/да/+/1/:ok_hand:/:thumbsup:)*'
    yes = {'за', '1', 'y', 'yes', 'д', 'да', 'у', '+', 't_d_', 'ok_hand', 'thumbsup', '+1', 'thumbup'}
    await C.client.send_message(channel, text)
    time_end = other.get_sec_total() + timeout

    def check(msg):
        return (msg.author.id not in votes.union({C.users['bot']}) and
                    yes.intersection(emj.em2text(msg.content).lower().replace('.', '').split()))

    while len(votes) < count:
        time_left = time_end - other.get_sec_total()
        log.I('<voting> We have {0}/{1} votes, wait more for {2} sec.'.format(len(votes), count, time_left))
        ans = await C.client.wait_for_message(timeout=time_left, channel=channel, check=check)
        if ans:
                votes.add(ans.author.id)
                other.later_coro(0, C.client.add_reaction(ans, emj.e('ok_hand')))
        else:
            break
    else:
        return votes

    return False


def get_weather():
    url = 'https://weather.com/ru-RU/weather/5day/l/UPXX0017:1:UP'
    resp = requests.get(url)
    page = lxml.html.fromstring(resp.content)
    d = page.get_element_by_id('twc-scrollabe')
    tr = d.getchildren()[0].getchildren()[1].getchildren()[0]
    tr_ch = tr.getchildren()
    desc = tr_ch[2].text_content()
    t_max = tr_ch[3].getchildren()[0].getchildren()[0].text_content()
    t_min = tr_ch[3].getchildren()[0].getchildren()[2].text_content()
    rain = tr_ch[4].text_content()
    wind = re.search(r'\d+', tr_ch[5].text_content())[0] # км/ч
    hum = tr_ch[6].text_content()
    t_desc = ''
    if t_min != '--' or t_max != '--':
        t_desc = (' Температура' +
            (' от ' + t_min if t_min != '--' else '') +
            (' до ' + t_max if t_max != '--' else '') +
            '.')
    return ('Во Львове сегодня {descr}.{temp} Вероятность дождя {rain}, ветер до {wind} км/ч, влажность {hum}.'.format(
        descr=desc.lower(), temp=t_desc, rain=rain, wind=wind, hum=hum))


async def do_embrace_and_say(msg, name, clan=None):
    user = other.find_member(C.vtm_server, name)
    roles = {role.id for role in user.roles[1:]}
    if not roles.intersection(C.clan_ids):
        text = await do_embrace(user, clan=clan)
        await msg.say(C.main_ch, text)


async def do_embrace(user, clan=None):
    if user:
        if not clan:
            for r in user.roles:
                if r.id in C.clan_ids:
                    clan = C.role_by_id[r.id]
                    break
        clan = clan or random.choice(list(C.clan_names))
        roles = [other.find(C.vtm_server.roles, id=C.roles[clan])]
        pander = False
        if clan in C.sabbat_clans:
            roles.append(other.find(C.vtm_server.roles, id=C.roles['Sabbat']))
            pander = (clan == 'Noble Pander')
        try:
            await C.client.add_roles(user, *roles)
        except C.discord.Forbidden:
            log.jW("Bot can't change roles.")
        except Exception as e:
            other.pr_error(e, 'do_embrace', 'Error in changing roles')
            #print("Other error in changing roles")
        # omg
        clan_users = set()
        if not pander:
            for mem in C.client.get_all_members():
                if other.find(mem.roles, id=C.roles[clan]) and mem.id != user.id:
                    clan_users.add(mem.id)
            clan_users.difference_update(C.not_sir)
            sir = random.choice(list(clan_users))
            text = random.choice(data.embrace_msg).format(sir='<@' + sir + '>', child='<@' + user.id + '>')
        else:
            text = random.choice(data.embrace_pander).format(child='<@' + user.id + '>')

        if clan in C.sabbat_clans and not pander:
            text += "\n" + random.choice(data.embrace_sabbat)

        return text

    else:
        return False  #await msg.qanswer("Не могу найти такого пользователя.")

_roll_patt = re.compile(r'''
        [ ]*(?P<key1>[a-zA-Z_]+)?
        [ ]*(?P<count>\d+)(?:[ ]*d[ ]*(?P<type>\d+))?
        [ ]*(?P<rel>(
            (?P<ge>(>=|=>))|(?P<le>(<=|=<))|(?P<ne>(!=|=!|~=|=~|<>|><|~+|!+))|(?P<eq>[=]+)|(?P<gt>[>]+)|(?P<lt>[<]+)
        ))?
        [ ]*(?P<diff>[-+]?\d+[.,]?\d*)?
        [ ]*(?P<key2>[a-zA-Z_]+)?
        ''', re.X)


def get_dice_param(text, add_keys=''):
    count, dtype, rel, diff, par_keys, simple = None, None, None, None, None, None
    m = _roll_patt.search(text)
    rel_keys = ('ge', 'le', 'ne', 'eq', 'gt', 'lt')
    error = not m or False
    if not error:
        group = m.groupdict()
        error = not group['count']

        if not error:
            par_keys = (group['key1'] or '') + (group['key2'] or '') + add_keys
            count = int(group['count']) or 1
            dtype = (int(group['type']) or 10) if group['type'] else 10
            simple = not (group['rel'] or group['diff'])
            if not simple or set(par_keys).intersection({'s', 'sp', 'd', 'v', 'w', 'f'}):
                simple = False
                rel = [key for key in rel_keys if group[key]][0] if group['rel'] else 'ge'
                diff = int(group['diff']) if group['diff'] else int(dtype / 2 + 1)

    return error, count, dtype, rel, diff, par_keys, simple


def _get_symb(change_val, short=False):

    if short:
        if change_val > 0:
            symb = '`'
        elif change_val < 0:
            symb = '**'
        else:
            symb = '~~'
    else:
        if change_val > 0:
            symb = '+'
        elif change_val < 0:
            symb = '-'
        else:
            symb = '•'
    return symb


def get_dices(count=1, dtype=10, rel='ge', diff=6, par_keys='', simple=False, short=False, add_d=False):
    text = []
    dices = []
    for i in range(0, count):
        d = random.randint(1, dtype)
        dices.append(d)

    if simple:
        if short:
            text = [str(dice) for dice in dices]
        else:
            text = ['{:02d}d:\t{val}\n'.format(i + 1, val=dice) for i, dice in enumerate(dices)]
    else:
        if short and not add_d:
            text.append('(')
        was_success = False
        add_dices = 0
        double_ten = False
        res = 0
        for i, dice in enumerate(dices):
            succ = getattr(operator, rel)(dice, diff)
            aft = ''
            if succ:
                res += 1
                change_val = +1
                was_success = True
                if dice == dtype and dtype > 1 and par_keys:
                    if 'v' in par_keys:
                        aft = double_ten and '(++)' or ''
                        res += 2 * int(double_ten)
                        double_ten = not double_ten
                    elif 'd' in par_keys:
                        aft = double_ten and '(+)' or ''
                        res += int(double_ten)
                        double_ten = not double_ten
                    elif 'sp' in par_keys:
                        res += 1
                        aft = '(+)'
                    elif 's' in par_keys:
                        add_dices += 1
                        aft = '(*)'
            else:
                change_val = 0
                if dice == 1 and ('w' in par_keys or 'f' in par_keys):
                    res -= 1
                    change_val = -1
            if short:
                symb = _get_symb(change_val, True)
                symb2 = '__**' if aft else ''
                text.append('{symb2_1}{symb}{val}{symb}{symb2_2}'.
                            format(symb=symb, val=dice, symb2_1=symb2, symb2_2=symb2[::-1]))
            else:
                aft = ' ' + aft if aft else ''
                symb = _get_symb(change_val)
                text.append('{} {:02d}d:\t{val}{aft}\n'.format(symb, i+1, val=dice, aft=aft))
        if add_d:
            return res, text, add_dices
        while add_dices:
            if short:
                text.append(r'\|\| \*__{{{}}}__:'.format(add_dices))
            else:
                text.append('* Специализация({}):\n'.format(add_dices))
            (add_res, add_text, add_dices) = get_dices(add_dices, dtype, rel, diff, par_keys, short=short, add_d=True)
            res += add_res
            text += add_text
        if short:
            text.append('):')
            conclusion = ('**`успех ({})`**' if res > 0 else
                          'неудача' if (was_success or res == 0) else '**провал ({})**').format(res)
        else:
            conclusion = ('! Успех ({})' if res > 0 else
                      '• Неудача' if (was_success or res == 0) else '- Провал ({})').format(res)
        text.append(conclusion)

    return text


_v5_patt = re.compile(r'''
        [ ]*(?P<key1>[a-zA-Z_]+)?
        [ ]*(?P<count>\d+)?
        ([ ]+(?P<diff>\d+))?
        ([ ]+(?P<hung>\d+))?
        [ ]*(?P<key2>[a-zA-Z_]+)?
        ''', re.X)


def get_v5_param(text, add_keys=''):
    count, diff, hung, par_keys, simple = None, 0, 0, None, None
    m = _v5_patt.search(text)
    error = not m or False
    if not error:
        group = m.groupdict()
        error = not group['count']

        if not error:
            par_keys = (group['key1'] or '') + (group['key2'] or '') + add_keys
            count = int(group['count']) or 1
            simple = not group['diff']
            if not simple:
                diff = int(group['diff']) if group['diff'] else 0
                hung = int(group['hung']) if group['hung'] else 0

    return error, count, diff, hung, par_keys, simple


def _get_val_v5(dice, hunger=False, short=False):
    if dice == 10:
        symb = (('☘', r'\🍀'), ('☿', '👹'))[hunger][short]
    elif dice > 5:
        symb = '☥'
    elif hunger and dice == 1:
        symb = ('☠', '💀')[short]
    else:
        symb = ('●', '•')[short]

    if hunger:
        symb = '`' + symb + '`'
    return symb


def get_dices_v5(count=1, diff=0, hung=0, simple=False, short=False):
    text = []
    dices = []
    count_tens = 0
    for i in range(0, count):
        d = random.randint(1, 10)
        dices.append(d)
        count_tens += 1 if d == 10 else 0

    if simple:
        if short:
            text = ['{val}'.format(val=_get_val_v5(dice, short=True)) for dice in dices]
        else:
            text = ['{:02d}d:\t{val}\n'.format(i + 1, val=_get_val_v5(dice)) for i, dice in enumerate(dices)]
    else:
        if short:
            text.append('(')
        was_h1 = False
        was_h10 = False
        res = 0
        crit_tens = int(count_tens/2)*2
        norm_dices = max(count - hung, 0) # other: hung_dices
        for i, dice in enumerate(dices):
            hunger = i >= norm_dices
            succ = dice > 5
            aft = ''
            if succ:
                res += 1
                if dice == 10:
                    if crit_tens > 0:
                        aft = ' (+)'
                        res += 1
                        crit_tens -= 1
                    symb = '!'
                    was_h10 = hunger or was_h10
                else:
                    symb = '+'
            else:
                symb = '•'
                was_h1 = was_h1 or (hunger and dice == 1)
            symb = '-' if hunger else symb
            if short:
                if hunger and i == norm_dices:
                    text.append(r'\|\|')
                frm = '__' if aft else ''
                text.append('{frm}{val}{frm}'.format(val=_get_val_v5(dice, hunger, short=True), frm=frm))
            else:
                text.append('{} {:02d}d:\t{val}{aft}\n'.format(symb, i + 1, val=_get_val_v5(dice, hunger), aft=aft))

        if res >= diff:
            if count_tens > 1:
                conclusion = (('- {}', '**__`{}`__**')[short].format('Messy Critical')
                              if was_h10 else ('! {}', '**__{}__**')[short].format('Critical Win'))
            else:
                conclusion = ('+ {}', '**{}**')[short].format('Success') #'+ Win'
            conclusion = ('{} ({} {})', '{} *({} {})*')[short].format(conclusion, 'margin:', res - diff)
        else:
            if was_h1:
                conclusion = ('- {}', '**`{}`**')[short].format('Bestial Failure')
            elif res > 0:
                conclusion = ('• {} ({} {})', '{} *({} {})*')[short].format('Failure', 'win at a cost:', diff - res)
            else:
                conclusion = ('● {}', '{}')[short].format('Total Failure')

        if short:
            text.append('):')
        text.append(conclusion)
    return text
