# -*- coding: utf8 -*-
import discord
import sys
import random
import other
import constants as C
import local_memory as ram
import people
#import data

""" 
    here only functions as bot-commands (!cmd) with obj of check_message.Msg as arg:
        async def cmd(msg)
"""

    # region Interaction commands


async def help(msg):
    """\
    !help: выводит данный хелп (неожиданно,да?)
    !help cmd*: выводит хелп по указанным командам \
    """
    module = sys.modules[__name__]
    module_attrs = dir(module)
    cmds = set(key for key in module_attrs if key[0] != '_' and callable(getattr(module, key)))
    if not msg.super:
        cmds.intersection_update(C.free_cmds)

    if len(msg.args) > 1:
        cmds.intersection_update(set(msg.text.split()[1:]))

    if cmds:
        texts = []
        if len(msg.args) < 2 and msg.super:
            texts.append(('''```css
            Условные обозначения аргументов:
                ch - id, обращение (#channel) или имя канала без пробелов;
                usr - id, обращение (@name), или любой из ников без пробела 
                    (например Soul, Soulcapturer или Soulcapturer#2253);
                username - аналогично usr, но можно и ники с пробелами;
                role - id, обращение (@role) или имя роли без пробелов ;
                msg - id сообщения;
                cmd - имя команды, известной боту;
                text - просто любой текст;
                * - бесконечно повторение последнего аргумента разделённого пробелом
                (например ch* = ch1 ch2 ch3...; usr* = usr1 usr2 usr3...);
            ```''').replace('            ',''))
        docs = [getattr(module, cmd).__doc__ for cmd in cmds]
        texts += other.comfortable_help(docs)
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
    !channel ch*: сохраняет список каналов для !mute, !deny, !purge
    !channel: выводит список сохранённых каналов \
    """
    if len(msg.args) > 1:
        #ram.cmd_channels.setdefault(msg.author, set()).update(set(msg.args[1:]))
        ram.cmd_channels.setdefault(msg.author, set()).update(other.get_channels(msg.args[1:]))
        msg.cmd_ch = ram.cmd_channels.get(msg.author, set())

    await msg.qanswer(('<#' + '>, <#'.join(msg.cmd_ch) + '>') if msg.cmd_ch else 'All')


async def unchannel(msg):
    """\
    !unchannel ch* : удаляет каналы из сохранённого списка
    !unchannel: отчищает список сохранённых каналов \
    """
    if len(msg.args) < 2:
        ram.cmd_channels[msg.author] = set()
    else:
        ram.cmd_channels.setdefault(msg.author, set()).difference_update(other.get_channels(msg.args[1:]))

    msg.cmd_ch = ram.cmd_channels.get(msg.author, set())
    await msg.qanswer(('<#' + '>, <#'.join(msg.cmd_ch) + '>') if msg.cmd_ch else 'All')


async def report(msg):
    """\
    !report ch* : сохраняет каналы для вывода сообщений (!say !deny !embrace)
    !report: выводит список сохранённых каналов \
    """
    if len(msg.args) > 1:
        ram.rep_channels.setdefault(msg.author, set()).update(other.get_channels(msg.args[1:]))
        msg.rep_ch = ram.rep_channels.get(msg.author, set())

    text = other.ch_list(msg.rep_ch)
    await msg.qanswer((', '.join(text)) if text else 'None')


async def unreport(msg):
    """\
    !unreport ch* : удаляет каналы из сохранённого списка
    !unreport: отчищает список сохранённых каналов \
    """
    if len(msg.args) < 2:
        ram.rep_channels[msg.author] = set()
    else:
        ram.rep_channels.setdefault(msg.author, set()).difference_update(other.get_channels(msg.args[1:]))

    msg.rep_ch = ram.rep_channels.get(msg.author, set())
    text = other.ch_list(msg.rep_ch)
    await msg.qanswer((', '.join(text)) if text else 'None')


async def say(msg):
    """\
    !say text: сказать Беккетом text на каналах из !report \
    """
    await msg.report(msg.original[len('!say '):])


async def sayf(msg):
    """\
    !sayf text: сказать Беккетом text во #flood \
    """
    await msg.say(C.main_ch, msg.original[len('!sayf '):])


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
    !purge: стереть последнее сообщение в каналах из !channels
    !purge N: стереть N последних сообщений в каждом из каналов из !channel
    !purge N usr*: стереть сообщения юзеров из последних N сообщений в !channel \
    """
    channels = msg.cmd_ch or {msg.channel.id}
    count = msg.args[1] if len(msg.args) > 1 else 1
    check = None

    if len(msg.args) > 2:
        check_set = other.get_users(msg.args[2:])   #set(msg.args[2:])

        def check_user(m):
            return m.author.id in check_set

        check = check_user

    for ch in channels:
        await msg.purge(C.client.get_channel(ch), count, check=check)


async def purge_aft(msg):
    """\
    !purge_aft ch msg: стереть миллион сообщений после msg в ch
    !purge_aft ch msg N: стереть N сообщений после msg в ch
    !purge_aft ch msg N usr*: стереть сообщения юзеров из N сообщений после msg в ch \
    """
    err = len(msg.args) < 3

    ch = {}
    if not err:
        ch = other.get_channel(msg.args[1]) #C.client.get_channel(msg.args[1])
        err = not ch

    mess = {}
    if not err:
        mess = await C.client.get_message(ch, msg.args[2])
        err = not mess

    if err:
        await msg.qanswer(other.comfortable_help([str(purge_aft.__doc__)]))
        return

    count = msg.args[3] if len(msg.args) > 3 else 1000000
    check = None

    if len(msg.args) > 4:
        check_set = other.get_users(msg.args[4:])

        def check_user(m):
            return m.author.id in check_set

        check = check_user

    await msg.purge(ch, count, check=check, aft=mess)


async def purge_ere(msg):
    """\
    !purge_ere ch msg: стереть одно сообщение перед msg в ch
    !purge_ere ch msg N: стереть N сообщений перед msg в ch
    !purge_ere ch msg N usr*: стереть сообщения юзеров из N сообщений перед msg в ch \
    """
    err = len(msg.args) < 3

    ch = {}
    if not err:
        ch = other.get_channel(msg.args[1])
        err = not ch

    mess = {}
    if not err:
        mess = await C.client.get_message(ch, msg.args[2])
        err = not mess

    if err:
        await msg.qanswer(other.comfortable_help([str(purge_ere.__doc__)]))
        return

    count = msg.args[3] if len(msg.args) > 3 else 1
    check = None

    if len(msg.args) > 4:
        check_set = other.get_users(msg.args[4:])

        def check_user(m):
            return m.author.id in check_set

        check = check_user

    await msg.purge(ch, count, check=check, bef=mess)


async def purge_bet(msg):
    """\
    !purge_bet ch msg1 msg2: стереть сообщения между msg1 и msg2 в ch
    !purge_bet ch msg1 msg2 usr*: стереть сообщения юзеров между msg1 и msg2 в ch \
    """
    err = len(msg.args) < 4

    ch = {}
    if not err:
        ch = other.get_channel(msg.args[1]) # C.client.get_channel(msg.args[1])
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
        check_set = other.get_users(msg.args[4:])

        def check_user(m):
            return m.author.id in check_set

        check = check_user

    await msg.purge(ch, 1000000, check=check, aft=msg1, bef=msg2)


async def delete(msg):
    """
    !delete ch msg*: стереть сообщения в указанном канале
    """

    #await msg.answer(other.comfortable_help([str(purge_after.__doc__)]))
    # await msg.answer("```css\n" + str(delete.__doc__) + "```")
    #return
    err = len(msg.args) < 3
    ch = None
    if not err:
        ch = other.get_channel(msg.args[1]) #C.client.get_channel(msg.args[1])
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
    !embrace username: случайно (если нет клана) обратить пользователя, выдать сира, сообщить в !reports
    !embrace role username: обратить пользователя в role, выдать сира, сообщить в !report
    """
    if len(msg.args) < 2:
        # get help
        return

    clan = None
    if len(msg.args) < 3:
        name = msg.original[len('!embrace '):]
    else:
        role = other.find(C.server.roles, id=msg.args[1])
        ln = 0
        if not role:
            for r in C.server.roles:
                if r.name in msg.original:
                    if not role or len(r.name) > len(role.name):
                        role = r
            if role:
                ln = len('!embrace ') + len(role.name) + 1
        else:
            ln = msg.original.find(' ', len('!embrace ') + 1) + 1
        if role:
            clan = C.role_by_id.get(role.id, None)
            if clan in C.clan_names:
                name = msg.original[ln:]
            else:
                await msg.qanswer("It's not clan role")
                return
        else:
            name = msg.original[len('!embrace '):]
    user = other.get_user(name)
    text = await other.do_embrace(user, clan)
    if text:
        await msg.report(text)
    else:
        await msg.qanswer("Не могу найти такого пользователя.")


async def clear_clans(msg):
    if len(msg.args) < 2:
        # get help
        return

    user = other.get_user(msg.original[len('!clear_clans '):])
    if user:
        #C.clan_names
        rls = []
        for clan in C.clan_names:
            rls.append(other.find(C.server.roles, id=C.roles[clan]))
        rls.append(other.find(C.server.roles, id=C.roles['Sabbat']))
        await C.client.remove_roles(user, *rls)

    else:
        await msg.qanswer("Не могу найти такого пользователя.")

# endregion

    # region Deny commands


async def deny(msg):
    """\
    !deny: список замьютенных юзеров
    !deny usr* : замьютить указанных юзеров в каналах из !channel \
    """
    # without args - show deny list
    if len(msg.args) < 2:
        if not ram.torpor_users:
            await msg.qanswer('**Свобода царит в местных доменах.**')
        else:
            await msg.qanswer('\n'.join(
                '<@' + user + '>:\t<#' + '>, <#'.join(ram.torpor_users[user]) + '>' for user in ram.torpor_users))

    # else - deny by id (from args) in channels (from mem.cmd_channels)
    nope = {C.users['Natali'], C.users['bot'], msg.author}
    ch = msg.cmd_ch or {'All'}
    users = other.get_users(msg.args[1:]).difference(nope)
    members = other.get_mentions(users)
    for usr in users:
        ram.torpor_users.setdefault(usr, set()).update(ch)
    # for user in msg.args[1:]:
    #     if user not in nope:
    #         ram.torpor_users.setdefault(user, set()).update(ch)
    #         members.append('<@' + user + '>')

    if not members:
        return

    if ch == {'All'}:
        mess = ('**Сородич {0} был отправлен в торпор. Отныне он не произнесет ни слова.**' if len(
            members) < 2 else '**Сородичи {0} были отправлены в торпор. Отныне они не произнесут ни слова.**')
        await msg.report(mess.format(', '.join(members)))
    else:
        s_domains = 'домена <#%s>' % ch.copy().pop() if len(ch) < 2 else 'доменов <#%s>' % ('>, <#'.join(ch))
        mess = ('**Сородич {0} был изгнан из {1}. Отныне там мы его не услышим.**' if len(
            members) < 2 else '**Сородичи {0} был изгнаны из {1}. Отныне там мы их не услышим.**')
        await msg.report(mess.format(', '.join(members), s_domains))


async def undeny(msg):
    """\
    !undeny: размьютить всех
    !undeny usr* : размьютить указанных юзеров в каналах из !channel \
    """
    # without args - undeny all in everywhere
    if len(msg.args) < 2 and ram.torpor_users:
        ram.torpor_users = {}
        await msg.report('**```АМНИСТИЮ ДЛЯ ВСЕХ, ДАРОМ, И ПУСТЬ НИКТО НЕ УЙДЁТ ОБИЖЕННЫЙ!```**')
        return

    # else - undeny by id (from args) in channels (from mem.cmd_channels)
    ch = msg.cmd_ch or {'All'}
    users = other.get_users(msg.args[1:]).intersection(ram.torpor_users.keys())
    if ch == {'All'}:
        members = other.get_mentions(users)
        ram.torpor_users = {usr: ram.torpor_users[usr] for usr in ram.torpor_users if usr not in users}
    else:
        members = []
        for user in users:
            if ram.torpor_users[user].intersection(ch):
                ram.torpor_users[user].difference_update(ch)
                members.append('<@' + user + '>')
                if not ram.torpor_users[user]:
                    del ram.torpor_users[user]

    # members = []    # other.get_mentions(users)
    # for user in users:
    #     if user in ram.torpor_users:
    #         if ch == {'All'}:
    #             del ram.torpor_users[user]
    #             members.append('<@' + user + '>')
    #         elif ram.torpor_users[user].intersection(ch):
    #             ram.torpor_users[user].difference_update(ch)
    #             members.append('<@' + user + '>')
    #             if not ram.torpor_users[user]:
    #                 del ram.torpor_users[user]

    if not members:
        return

    if ch == {'All'}:
        mess = ('**Сородич {0} был пробуждён и ему дозволено говорить.**' if len(
            members) < 2 else '**Сородичи {0} были пробуждены и им дозволено говорить.**')
        await msg.report(mess.format(', '.join(members)))
    else:
        s_domains = 'домене <#%s>' % ch.copy().pop() if len(ch) < 2 else 'доменах <#%s>' % ('>, <#'.join(ch))
        mess = ('**Сородичу {0} даровано помилование в {1} и он может там общаться.**' if len(
            members) < 2 else '**Сородичам {0} даровано помилование в {1} и они могут там общаться.**')
        await msg.report(mess.format(', '.join(members), s_domains))


async def kick(msg):
    if len(msg.args) < 2:
        return

    name = msg.original[len('!kick '):]
    usr = other.get_user(name)
    if not usr:
        await msg.qanswer('Пользователь не найден.')
    else:
        if other.issuper(usr):
            await msg.qanswer('Пользователя нельзя кикнуть.')
        else:
            await C.client.kick(usr)


async def ban(msg):
    if len(msg.args) < 2:
        return

    name = msg.original[len('!ban '):]
    usr = other.get_user(name)
    if not usr:
        await msg.qanswer('Пользователь не найден.')
    else:
        if other.issuper(usr):
            await msg.qanswer('Пользователя нельзя банить.')
        else:
            await C.client.ban(usr, delete_message_days=0)


async def unban(msg):
    if len(msg.args) < 2:
        return

    usr = await other.get_ban_user(msg.original[len('!unban '):])
    if not usr:
        await msg.qanswer('Пользователь не найден.')
    else:
        await C.client.unban(C.server, usr)

# endregion

    # region Mute commands
# TODO Becketts comments to *mute commands


async def mute(msg):
    """\
    !mute: выключить комменты Беккета во всех каналах
    !mute ch*. : выключить комменты Беккета в указанных каналах \
    """
    if len(msg.args) < 2:
        ram.mute_channels = {'All'}
    else:
        ram.mute_channels.update(other.get_channels(msg.args[1:]))

    await mute_list(msg)


async def unmute(msg):
    """\
    !unmute: включить комменты Беккета во всех каналах
    !unmute ch* : включить комменты Беккета в указанных каналах \
    """
    if len(msg.args) < 2:
        ram.mute_channels = set()
    else:
        ram.mute_channels.difference_update(other.get_channels(msg.args[1:]))

    await mute_list(msg)


async def mute_list(msg):
    """\
    !mute_list: список каналов "выключенного" Беккета-комментатора \
    """
    await msg.qanswer(('<#' + '>, <#'.join(ram.mute_channels) + '>') if ram.mute_channels else 'None')
# endregion


async def test(msg):
    ram.game = not ram.game
    await other.test_status(ram.game)

    #await msg.answer('test!')
    # ch = C.client.get_channel('419968987112275979') #398645007944384513
    # mess = await C.client.get_message(ch, msg.args[1])
    # await C.client.purge_from(channel=ch, limit=5, after=mess)

    # if len(msg.args)>1:
    #     N = int(msg.args[1])
    # else:
    #     N = 10
    # for i in range(0,N):
    #     await msg.qanswer('Тест ' + str(i+1))


async def issuper(msg):
    if len(msg.args) < 2:
        return

    name = msg.original[len('!super '):]
    usr = other.get_user(name)
    if other.issuper(usr):
        await msg.qanswer('yes')
    else:
        await msg.qanswer('no')
    pass
    # ch = C.client.get_channel('398645007944384513')
    # await C.client.send_typing(ch)
    # await C.client.send_typing(ch)
    # await C.client.send_file(ch, 'pic/mushroom spores.jpg',content=
    # '*Беккет нынче по лесу гулял,\nГрибочки по тихому он собирал,'
    # '\nНочь вся прошла - Бекки устал,\nИ споры грибные он тут услыхал...*')


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


async def pin(msg):
    err = len(msg.args) < 3
    ch = None
    if not err:
        ch = other.get_channel(msg.args[1]) #C.client.get_channel(msg.args[1])
        err = not ch

    if err:
        #await msg.qanswer(other.comfortable_help([str(pin.__doc__)]))
        return

    for mess_id in msg.args[2:]:
        try:
            mess = await C.client.get_message(ch, mess_id)
            await C.client.pin_message(mess)
        except discord.Forbidden:
            print("Bot haven't permissions here.")
        except discord.NotFound:
            print("Bot can't find message.")


async def unpin(msg):
    err = len(msg.args) < 3
    ch = None
    if not err:
        ch = other.get_channel(msg.args[1]) #C.client.get_channel(msg.args[1])
        err = not ch

    if err:
        #await msg.qanswer(other.comfortable_help([str(pin.__doc__)]))
        return

    for mess_id in msg.args[2:]:
        try:
            mess = await C.client.get_message(ch, mess_id)
            await C.client.unpin_message(mess)
        except discord.Forbidden:
            print("Bot haven't permissions here.")
        except discord.NotFound:
            print("Bot can't find message.")


async def dominate(msg):
    """\
    !dominate usr text: доминирование, только для избранных \
    """
    if len(msg.args) < 2:
        await msg.qanswer(other.comfortable_help([str(dominate.__doc__)]))
        return
    if not msg.super and msg.author != C.users['Creol']:
        await msg.answer('Нет у вас доминирования ¯\_(ツ)_/¯')
        return

    auth = other.get_user(msg.author)
    who = other.get_user(msg.args[1])
    if not auth or not who:
        await msg.qanswer(other.comfortable_help([str(dominate.__doc__)]))
        return
    emb = discord.Embed(title=msg.original[len('!dominate ' + msg.args[1] + ' '):], color=auth.color)
    emb.set_author(name=auth.nick or auth.name, icon_url=auth.avatar_url)
    emb.set_image(url='https://cdn.discordapp.com/attachments/420056219068399617/450428811725766667/dominate.gif')
    #emb.set_footer(text='')
    await msg.type2sent(C.main_ch, text=who.mention, emb=emb)
    #await C.client.send_message(ch, content=who.mention, embed=emb)


async def people_clear(msg):
    ans = await msg.question('ВЫ СОБИРАЕТЕСЬ СТЕРЕТЬ ВСЕ ТАБЛИЦЫ ПОЛЬЗОВАТЕЛЕЙ. ЭТО ДЕЙСТВИЕ НЕВОЗМОЖНО ОТМЕНИТЬ.'
                             'ВЫ ТОЧНО ЖЕЛАЕТЕ ПРОДОЛЖИТЬ?')
    if ans:
        people.clear()
        await msg.qanswer(":ok_hand:")
    else:
        await msg.qanswer("Отмена people_clear.")


async def people_sync(msg):
    ans = await msg.question('Это займёт некоторое время и полностью перезапишет Базу Данных пользователей. '
                             'Вы **точно** уверены, что *действительно* желаете продолжить?')
    if ans:
        await people.sync()
        await msg.qanswer(":ok_hand:")
    else:
        await msg.qanswer("Отмена people_sync.")


# Delete msgs from private channel:
    # m = await C.client.send_message(other.get_user(C.users['Kuro']), content='Тест')
    # ch = m.channel
    # async for message in C.client.logs_from(ch, limit=10):
    #     print(message.id, str(message.author), message.content)
    #     if message.author.id == C.users['bot']:
    #         await C.client.delete_message(message)
