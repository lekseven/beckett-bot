# -*- coding: utf8 -*-
import discord
import sys
import random
import other
import constants as C
import local_memory as ram
import data

""" 
    here only functions as bot-commands (!cmd) with obj of Msg as arg:
        async def cmd(msg)
"""

    # region Interaction commands


async def help(msg):    # TODO rewrite help, may be?
    """\
    !help: выводит данный хелп (неожиданно,да?)
    !help cmd1 cmd2: выводит хелп по указанным командам \
    """
    module = sys.modules[__name__]
    module_attrs = dir(module)
    cmds = set(key for key in module_attrs if key[0] != '_' and callable(getattr(module, key)))
    if not msg.super:
        cmds.intersection_update(C.free_cmds)

    if len(msg.args) > 1:
        cmds.intersection_update(set(msg.text.split()[1:]))

    if cmds:
        docs = [getattr(module, cmd).__doc__ for cmd in cmds]
        texts = other.comfortable_help(docs)
    else:
        texts = 'Увы, с этим ничем не могу помочь :sweat:'

    await msg.qanswer(texts)


'''
async def song(msg):
    await C.client.send_message(C.channels['FM'], "+np")

    def check(m):
        return m.embeds and 'Now Playing ♪' in m.embeds[0]['author']['name']

    message = await C.client.wait_for_message(timeout=5, channel=C.channels['FM'], check=check)
    if not message: # None
        await msg.answer('Не играет нынче ничего в данном домене.')
    else:
        embed = message.embeds[0]
        em = C.discord.Embed(**embed)
        em.set_thumbnail(url=embed['thumbnail']['url'])
        em.set_author(name=embed['author']['name'], url=embed['author']['url'], icon_url=embed['author']['icon_url'])
        await msg.answer(emb=em)
'''


async def channel(msg):
    """\
    !channel id1 id2 ... : сохраняет список каналов для !mute, !deny, !purge
    !channel: выводит список сохранённых каналов \
    """
    if len(msg.args) > 1:
        ram.cmd_channels.setdefault(msg.author, set()).update(set(msg.args[1:]))
        msg.cmd_ch = ram.cmd_channels.get(msg.author, set())

    await msg.qanswer(('<#' + '>, <#'.join(msg.cmd_ch) + '>') if msg.cmd_ch else 'All')


async def unchannel(msg):
    """\
    !unchannel id1 id2 ... : удаляет каналы из сохранённого списка
    !unchannel: отчищает список сохранённых каналов \
    """
    if len(msg.args) < 2:
        ram.cmd_channels[msg.author] = set()
    else:
        ram.cmd_channels.setdefault(msg.author, set()).difference_update(set(msg.args[1:]))

    msg.cmd_ch = ram.cmd_channels.get(msg.author, set())
    await msg.qanswer(('<#' + '>, <#'.join(msg.cmd_ch) + '>') if msg.cmd_ch else 'All')


async def report(msg):
    """\
    !report id1 id2 ... : сохраняет список каналов для вывода сообщений (!say, инф от !deny)
    !report: выводит список сохранённых каналов \
    """
    if len(msg.args) > 1:
        ram.rep_channels.setdefault(msg.author, set()).update(set(msg.args[1:]))
        msg.rep_ch = ram.rep_channels.get(msg.author, set())

    await msg.qanswer(('<#' + '>, <#'.join(msg.rep_ch) + '>') if msg.rep_ch else 'None')



async def unreport(msg):
    """\
    !unreport id1 id2 ... : удаляет каналы из сохранённого списка
    !unreport: отчищает список сохранённых каналов \
    """
    if len(msg.args) < 2:
        ram.rep_channels[msg.author] = set()
    else:
        ram.rep_channels.setdefault(msg.author, set()).difference_update(set(msg.args[1:]))

    msg.rep_ch = ram.rep_channels.get(msg.author, set())
    await msg.qanswer(('<#' + '>, <#'.join(msg.rep_ch) + '>') if msg.rep_ch else 'None')


async def say(msg):
    """\
    !say some_text: сказать Беккетом some_text на каналах из !report \
    """
    await msg.report(msg.original.lstrip('!say '))


async def emoji(msg):
    """\
    !emoji: вкл/выкл эмоджи Беккета за пользователя \
    """
    if msg.author in ram.emoji_users:
        ram.emoji_users.discard(msg.author)
        await msg.qanswer('Emoji mode off')
    else:
        ram.emoji_users.add(msg.author)
        await msg.qanswer('Emoji mode on')


async def purge(msg):
    """\
    !purge: del последнее сообщение в каналах из !channels
    !purge N: del N последних сообщений в каналах из !channels (в каждом по N)
    !purge N id1 id2 ... : del сообщения этих юзеров из последних N сообщений в !channels \
    """
    channels = msg.cmd_ch or {msg.channel.id}
    count = msg.args[1] if len(msg.args) > 1 else 1
    check = None

    if len(msg.args) > 2:
        def check_user(m):
            check_set = set(msg.args[2:])
            return m.author.id in check_set

        check = check_user

    for ch in channels:
        await msg.purge(C.client.get_channel(ch), count, check=check)


async def purge_aft(msg):
    """\
    !purge_aft ch_id msg_id: del миллион сообщений после msg в ch
    !purge_aft ch_id msg_id N: del N сообщений после mess в ch
    !purge_aft ch_id msg_id N id1 ... : del сообщения юзеров из N сообщений после msg в ch \
    """
    err = len(msg.args)<3

    ch = {}
    if not err:
        ch = C.client.get_channel(msg.args[1])
        err = not ch

    mess={}
    if not err:
        mess = await C.client.get_message(ch, msg.args[2])
        err = not mess

    if err:
        await msg.qanswer(other.comfortable_help([str(purge_aft.__doc__)]))
        return

    count = msg.args[3] if len(msg.args) > 3 else 1000000
    check = None

    if len(msg.args) > 4:
        def check_user(m):
            check_set = set(msg.args[4:])
            return m.author.id in check_set

        check = check_user

    await msg.purge(ch, count, check=check, aft=mess)


async def purge_ere(msg):
    """\
    !purge_ere ch_id msg_id: del одно сообщение перед msg в ch
    !purge_ere ch_id msg_id N: del N сообщений перед mess в ch
    !purge_ere ch_id msg_id N id1 ... : del сообщения юзеров из N сообщений перед msg в ch \
    """
    err = len(msg.args)<3

    ch = {}
    if not err:
        ch = C.client.get_channel(msg.args[1])
        err = not ch

    mess={}
    if not err:
        mess = await C.client.get_message(ch, msg.args[2])
        err = not mess

    if err:
        await msg.qanswer(other.comfortable_help([str(purge_ere.__doc__)]))
        return

    count = msg.args[3] if len(msg.args) > 3 else 1
    check = None

    if len(msg.args) > 4:
        def check_user(m):
            check_set = set(msg.args[4:])
            return m.author.id in check_set

        check = check_user

    await msg.purge(ch, count, check=check, bef=mess)


async def purge_bet(msg):
    """\
    !purge_bet ch_id msg_id1 msg_id2: del сообщения между msg1 и msg2 в ch
    !purge_bet ch_id msg_id1 msg_id2 id1 ... : del сообщения юзеров между msg1 и msg2 в ch \
    """
    err = len(msg.args)<4

    ch = {}
    if not err:
        ch = C.client.get_channel(msg.args[1])
        err = not ch

    msg1 = {}
    if not err:
        msg1 = await C.client.get_message(ch, msg.args[2])
        err = not msg1

    msg2 = {}
    if not err:
        msg2 = await C.client.get_message(ch, msg.args[3])
        err = not msg2

    if err:
        await msg.qanswer(other.comfortable_help([str(purge_bet.__doc__)]))
        return

    check = None

    if len(msg.args) > 4:
        def check_user(m):
            check_set = set(msg.args[4:])
            return m.author.id in check_set

        check = check_user

    await msg.purge(ch, 1000000, check=check, aft=msg1, bef=msg2)


async def delete(msg):
    """\
    !delete ch_id mess_id1 mess_id2: del сообщения (по id) в указанном канале \
    """

    #await msg.answer(other.comfortable_help([str(purge_after.__doc__)]))
    # await msg.answer("```css\n" + str(delete.__doc__) + "```")
    #return
    err = len(msg.args) < 3
    ch = None
    if not err:
        ch = C.client.get_channel(msg.args[1])
        err = not ch

    if err:
        await msg.qanswer(other.comfortable_help([str(delete.__doc__)]))
        return

    done = False
    for mess_id in msg.args[2:]:
        try:
            mess = await C.client.get_message(ch, mess_id)
            await C.client.delete_message(mess)
            done = True
        except discord.Forbidden:
            print("Bot haven't permissions here.")
        except discord.NotFound:
            print("Bot can't find message.")

    if done:
        await msg.qanswer(":ok_hand:")


async def ignore(msg): # TODO more phrases here
    """\
    !ignore: вкл/выкл комментирования Беккетом своих сообщений \
    """
    if msg.author in ram.ignore_users:
        ram.ignore_users.remove(msg.author)
        await msg.answer("Что, кто-то по мне соскучился :relaxed:?")
    else:
        ram.ignore_users.add(msg.author)
        await msg.answer("Не хочешь разговаривать, ну и не надо :confused:.")


async def embrace(msg):
    """\
    !embrace usr: где usr - никнейм (любой), id или упоминание\
    """
    if len(msg.args) < 2:
        # get help
        return

    if len(msg.args) < 3:
        name = msg.args[1]
    else:
        name = msg.original.lstrip('!embrace ')
    user = other.get_user(name)
    if user:
        clan = random.choice(list(C.clan_names))
        roles = [C.discord.utils.get(C.server.roles, id=C.roles[clan])]
        pander = False
        if clan in C.sabbat_clans:
            roles.append(C.discord.utils.get(C.server.roles, id=C.roles['Sabbat']))
            pander = (clan == 'Noble Pander')
        try:
            await C.client.add_roles(user, *roles)
        except C.discord.Forbidden:
            print("Bot can't change roles.")
        except:
            print("Other error in changing roles")
        # omg
        clan_users=[]
        text = ''
        if not pander:
            for mem in C.client.get_all_members():
                if C.discord.utils.get(mem.roles, id=C.roles[clan]):
                    clan_users.append(mem.id)
            sir = random.choice(clan_users)
            text = random.choice(data.embrace_msg).format(sir='<@'+sir+'>',child='<@'+user.id+'>')
        else:
            text = random.choice(data.embrace_pander).format(child='<@' + user.id + '>')

        if clan in C.sabbat_clans and not pander:
            text += "\n" + random.choice(data.embrace_sabbat)

        await msg.report(text)

    else:
        await msg.qanswer("Не могу найти такого пользователя.")


async def clear_clans(msg):
    if len(msg.args) < 2:
        # get help
        return

    user= other.get_user(msg.original.lstrip('!embrace '))
    if user:
        #C.clan_names
        roles = []
        for clan in C.clan_names:
            roles.append(C.discord.utils.get(C.server.roles, id=C.roles[clan]))
        roles.append(C.discord.utils.get(C.server.roles, id=C.roles['Sabbat']))
        await C.client.add_roles(user,*roles)

    else:
        msg.qanswer("Не могу найти такого пользователя.")

# endregion

    # region Deny commands


async def deny(msg):
    """\
    !deny: список замьютенных юзеров
    !deny id1 id2 ... : замьютить указанных юзеров в каналах из !channel \
    """
    # without args - show deny list
    if len(msg.args) < 2:
        if not ram.torpor_users:
            await msg.report('**Свобода царит в местных доменах.**')
        else:
            await msg.report('\n'.join(
                '<@' + user + '>:\t<#' + '>, <#'.join(ram.torpor_users[user]) + '>' for user in ram.torpor_users))

    # else - deny by id (from args) in channels (from mem.cmd_channels)
    nope = {C.users['Natali'], C.users['bot'], msg.author}
    ch = msg.cmd_ch or {'All'}
    members = []

    for user in msg.args[1:]:
        if user not in nope:
            ram.torpor_users.setdefault(user, set()).update(ch)
            members.append('<@' + user + '>')

    if not members:
        return

    if ch == {'All'}:
        mess = ('**Сородич {0} был отправлен в торпор. Отныне он не произнесет ни слова.**' if len(
            members) < 2 else '**Сородичи {0} были отправлены в торпор. Отныне они не произнесут ни слова.**')
        await msg.report(mess.format(', '.join(members)))
    else:
        s_domains = 'домена <#%s>' % ch.pop() if len(ch) < 2 else 'доменов <#%s>' % ('>, <#'.join(ch))
        mess = ('**Сородич {0} был изгнан из {1}. Отныне там мы его не услышим.**' if len(
            members) < 2 else '**Сородичи {0} был изгнаны из {1}. Отныне там мы их не услышим.**')
        await msg.report(mess.format(', '.join(members), s_domains))


async def undeny(msg):
    """\
    !undeny: размьютить всех
    !undeny id1 id2 ... : размьютить указанных юзеров в каналах из !channel \
    """
    # without args - undeny all in everywhere
    if len(msg.args) < 2 and ram.torpor_users:
        ram.torpor_users = {}
        await msg.report('**```АМНИСТИЮ ДЛЯ ВСЕХ, ДАРОМ, И ПУСТЬ НИКТО НЕ УЙДЁТ ОБИЖЕННЫЙ!```**')
        return

    # else - undeny by id (from args) in channels (from mem.cmd_channels)
    members = []
    ch = msg.cmd_ch or {'All'}
    for user in msg.args[1:]:
        if user in ram.torpor_users:
            if ch == {'All'}:
                del ram.torpor_users[user]
                members.append('<@' + user + '>')
            elif ram.torpor_users[user].intersection(ch):
                ram.torpor_users[user].difference_update(ch)
                members.append('<@' + user + '>')
                if not ram.torpor_users[user]:
                    del ram.torpor_users[user]

    if not members:
        return

    if ch == {'All'}:
        mess = ('**Сородич {0} был пробуждён и ему дозволено говорить.**' if len(
            members) < 2 else '**Сородичи {0} были пробуждены и им дозволено говорить.**')
        await msg.report(mess.format(', '.join(members)))
    else:
        s_domains = 'домене <#%s>' % ch.pop() if len(ch) < 2 else 'доменах <#%s>' % ('>, <#'.join(ch))
        mess = ('**Сородичу {0} даровано помилование в {1} и он может там общаться.**' if len(
            members) < 2 else '**Сородичам {0} даровано помилование в {1} и они могут там общаться.**')
        await msg.report(mess.format(', '.join(members), s_domains))
# endregion

    # region Mute commands
# TODO Becketts comments to *mute commands


async def mute(msg):
    """\
    !mute: выключить комменты Беккета во всех каналах
    !mute id1 id2 ... : выключить комменты Беккета в указанных каналах \
    """
    if len(msg.args) < 2:
        ram.mute_channels = {'All'}
    else:
        ram.mute_channels.update(set(msg.args[1:]))

    await mute_list(msg)


async def unmute(msg):
    """\
    !unmute: включить комменты Беккета во всех каналах
    !unmute id1 id2 ... : включить комменты Беккета в указанных каналах \
    """
    if len(msg.args) < 2:
        ram.mute_channels = set()
    else:
        ram.mute_channels.difference_update(set(msg.args[1:]))

    await mute_list(msg)


async def mute_list(msg):
    """\
    !mute_list: список каналов "выключенного" Беккета-комментатора \
    """
    await msg.qanswer(('<#' + '>, <#'.join(ram.mute_channels) + '>') if ram.mute_channels else 'None')
# endregion


async def test(msg):
    #await msg.answer('test!')
    # ch = C.client.get_channel('419968987112275979')
    # mess = await C.client.get_message(ch, msg.args[1])
    # await C.client.purge_from(channel=ch, limit=5, after=mess)

    if len(msg.args)>1:
        N = int(msg.args[1])
    else:
        N = 10
    for i in range(0,N):
        await msg.qanswer('Тест ' + str(i+1))


async def roles(msg):
    #await msg.answer(', '.join(msg.roles))
    return


async def roll(msg):
    """\
    !roll хdу: кинуть x кубиков-y \
    """
    if len(msg.args) < 2:
        msg.args.append('1d10')
    rollrange = msg.args[1].split('d')
    if len(rollrange) == 2 and all(i.isdigit() for i in rollrange):
        count, dice = int(rollrange[0]), int(rollrange[1])
        if count > 21:
            await msg.answer('Перебор, я выиграл :slight_smile:')
            return

        dices = []
        for i in range(0, count):
            dices += ['{:02d}'.format(i + 1), 'd:\t', str(random.randint(1, dice)), '\n']
        await msg.qanswer("```" + ''.join(dices) + "```")
    else:
        await msg.qanswer("```css\n"+str(roll.__doc__)+"```")
