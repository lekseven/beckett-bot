import re

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
import log
import emj


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

roll_patt = re.compile(r'''
        [ ]*(?P<key1>[a-zA-Z_]+)?
        [ ]*(?P<count>\d+)(?:[ ]*d[ ]*(?P<type>\d+))?
        [ ]*(?P<rel>(
            (?P<ge>(>=|=>))|(?P<le>(<=|=<))|(?P<ne>(!=|=!|~=|=~|<>|><|~+|!+))|(?P<eq>[=]+)|(?P<gt>[>]+)|(?P<lt>[<]+)
        ))?
        [ ]*(?P<diff>[-+]?\d+[.,]?\d*)?
        [ ]*(?P<key2>[a-zA-Z_]+)?
        ''', re.X)


def get_dices(count=1, dtype=10, rel='ge', diff=6, par_keys='', wr='long', simple=False, add_d=False):
    text = []
    dices = []
    for i in range(0, count):
        d = random.randint(1, dtype)
        dices.append(d)
    if wr == 'long':
        if simple:
            text = ['{:02d}d:\t{val}\n'.format(i+1, val=dice) for i, dice in enumerate(dices)]
        else:
            was_success = False
            add_dices = 0
            double_ten = False
            res = 0
            for i, dice in enumerate(dices):
                succ = getattr(operator, rel)(dice, diff)
                aft = ''
                if succ:
                    res += 1
                    symb = '+'
                    was_success = True
                    if dice == dtype and par_keys:
                        if 'd' in par_keys:
                            aft = double_ten and ' (+)' or ''
                            res += int(double_ten)
                            double_ten = not double_ten
                        elif 'sp' in par_keys:
                            res += 1
                            aft = ' (+)'
                        elif 's' in par_keys:
                            add_dices += 1
                            aft = ' (*)'
                else:
                    symb = '•'
                    if dice == 1 and ('w' in par_keys or 'f' in par_keys):
                        res -= 1
                        symb = '-'
                text.append('{} {:02d}d:\t{val}{aft}\n'.format(symb, i+1, val=dice, aft=aft))
            if add_d:
                return res, text, add_dices
            while add_dices:
                text.append('* Специализация({}):\n'.format(add_dices))
                (add_res, add_text, add_dices) = get_dices(add_dices, dtype, rel, diff, par_keys, wr, add_d=True)
                res += add_res
                text += add_text

            conclusion = ('! Успех ({})' if res > 0 else
                          '• Неудача' if (was_success or res == 0) else '- Провал ({})').format(res)
            text.append(conclusion)

    return text


v5_patt = re.compile(r'''
        [ ]*(?P<count>\d+)?
        ([ ]+(?P<diff>\d+))?
        ([ ]+(?P<hung>\d+))?
        ''', re.X)


def get_val_v5(dice, hunger=False):
    if dice == 10:
        return hunger and '☿' or '☘'
    elif dice > 5:
        return '☥'
    elif hunger and dice == 1:
        return '☠'
    else:
        return '●'


def get_dices_v5(count=1, diff=0, hung=0, wr='long', simple=False):
    text = []
    dices = []
    count_tens = 0
    for i in range(0, count):
        d = random.randint(1, 10)
        dices.append(d)
        count_tens += 1 if d == 10 else 0
    if wr == 'long':
        if simple:
            text = ['{:02d}d:\t{val}\n'.format(i+1, val=get_val_v5(dice)) for i, dice in enumerate(dices)]
        else:
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
                text.append('{} {:02d}d:\t{val}{aft}\n'.format(symb, i+1, val=get_val_v5(dice, hunger), aft=aft))

            if res >= diff:
                if count_tens > 1:
                    conclusion = '- Messy Critical' if was_h10 else '! Critical Win'
                else:
                    conclusion = '+ Success' #'+ Win'
                conclusion = '{} (margin: {})'.format(conclusion, res - diff)
            else:
                if was_h1:
                    conclusion = '- Bestial Failure'
                elif res > 0:
                    conclusion = '• Failure (win at a cost: {})'.format(diff - res)
                else:
                    conclusion = '● Total Failure'
            text.append(conclusion)
    return text
