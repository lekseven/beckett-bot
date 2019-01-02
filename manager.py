import re

import discord
import random
import lxml.html
import requests

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
                    if force or ((turn and getattr(prm,pr) is None) or
                                 (not turn and getattr(prm,pr) is False and not ch.id in check)):
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
    :rtype: discord.Member
    """
    s = C.prm_server
    user = other.find_member(s, name)
    if not user:
        return None

    if user.top_role >= s.me.top_role and not force:
        return False

    t = max(t, 0.02)
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
    wind = re.search('\d+', tr_ch[5].text_content())[0] # км/ч
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