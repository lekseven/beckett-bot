# -*- coding: utf8 -*-
import discord
import sys
import re
import random
import constants as C
import local_memory as ram

""" 
    here only functions as bot-commands (!cmd) with obj of Msg as arg:
        def cmd(msg)
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
        cmds.intersection_update(set(msg.args[1:]))

    if cmds:
        docs = [getattr(module, cmd).__doc__ for cmd in cmds]
        lens = []
        docs2 = []
        for doc in docs:
            if doc:
                new_doc = doc.split('\n')
                docs2 += new_doc
                for doc2 in new_doc:
                    lens.append(len(re.match('.*?[:]', doc2).group(0)))

        m = max(lens)
        docs = []
        for doc in docs2:
            docs.append(doc.replace(':', ':'+(' '*(m-lens.pop(0)))+'\t'))

        docs.sort()
        print('len(docs)=', len(docs))
        docs_len = len(docs)
        count_helps = int(docs_len / 21) + 1 # 20 lines for one message
        step = int(docs_len / count_helps - 0.001) + 1
        helps = [docs[i:i + step] for i in range(0, len(docs), step)]
        texts = []
        for h in helps:
            texts.append(('```css\n' + '\n'.join(h) + '```').replace('    !', '!'))
    else:
        texts = ['Увы, с этим ничем не могу помочь :sweat:']

    for text in texts:
        await msg.answer(text)


async def channel(msg):
    """\
    !channel id1 id2 ... : сохраняет список каналов для !mute, !deny, !purge
    !channel: выводит список сохранённых каналов \
    """
    if len(msg.args) < 2:
        await msg.answer(('<#' + '>, <#'.join(msg.cmd_ch) + '>') if msg.cmd_ch else 'All')
    else:
        ram.cmd_channels.setdefault(msg.author, set()).update(set(msg.args[1:]))
        msg.cmd_ch = ram.cmd_channels.get(msg.author, set())


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


async def report(msg):
    """\
    !report id1 id2 ... : сохраняет список каналов для вывода сообщений (!say, инф от !deny)
    !report: выводит список сохранённых каналов \
    """
    if len(msg.args) < 2:
        await msg.answer(('<#' + '>, <#'.join(msg.rep_ch) + '>') if msg.rep_ch else 'None')
    else:
        ram.rep_channels.setdefault(msg.author, set()).update(set(msg.args[1:]))
        msg.rep_ch = ram.rep_channels.get(msg.author, set())


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


async def say(msg):
    """\
    !say some_text: сказать Беккетом some_text на каналах из !report \
    """
    await msg.report(msg.original.lstrip('!say '))


async def purge(msg):
    """\
    !purge: стереть последнее сообщение в каналах из !channels
    !purge N: стереть N последних сообщений в каналах из !channels (в каждом по N)
    !purge N id1 id2 ... : стереть сообщения этих юзеров из последних N сообщений в !channels \
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


async def delete(msg):
    """\
    !delete ch_id mess_id1 mess_id2: стереть сообщения (по id) в указанном канале \
    """
    if len(msg.args) < 3:
        await msg.answer("```css\n" + str(delete.__doc__) + "```")
        return

    ch = C.client.get_channel(msg.args[1])
    if not ch:
        await msg.answer("```css\n" + str(delete.__doc__) + "```")
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
        await msg.answer(":ok_hand:")


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
    nope = {C.prince_id, C.beckett_id, msg.author}
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
    !mute: выключить комменты Беккета по ключевым словам во всех каналах
    !mute id1 id2 ... : выключить комменты Беккета по ключевым словам в указанных каналах \
    """
    if len(msg.args) < 2:
        ram.mute_channels = {'All'}
    else:
        ram.mute_channels.update(set(msg.args[1:]))


async def unmute(msg):
    """\
    !unmute: включить комменты Беккета по ключевым словам во всех каналах
    !unmute id1 id2 ... : включить комменты Беккета по ключевым словам в указанных каналах \
    """
    if len(msg.args) < 2:
        ram.mute_channels = set()
    else:
        ram.mute_channels.difference_update(set(msg.args[1:]))


async def mute_list(msg):
    """\
    !mute_list: список каналов "выключенного" Беккета-комментатора \
    """
    await msg.answer(('<#' + '>, <#'.join(ram.mute_channels) + '>') if ram.mute_channels else 'None')
# endregion


async def test(msg):
    await msg.answer('test!')


async def roles(msg):
    await msg.answer(', '.join(msg.roles))


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
        await msg.answer("```" + ''.join(dices) + "```")
    else:
        await msg.answer("```css\n"+str(roll.__doc__)+"```")
