# -*- coding: utf8 -*-
"""
    here only functions as bot-commands (!cmd) with obj of check_message.Msg as arg:
        async def cmd(msg)
"""
import discord
import sys

import other
import constants as C
import local_memory as ram
import people
import log
import event_funs as ev
import manager
import emj
import communication as com

_Msg = manager.Msg
roll_cmds = {'roll', 'rollw', 'rollv', 'r', 'rw', 'rv', }
free_cmds = {'help', 'ignore', }
free_cmds.update(roll_cmds)
admin_cmds = {
    'unsilence_all',
    'channel', 'unchannel', 'report', 'unreport', 'say', 'sayf', 'emoji', 'dominate',
    'purge', 'purge_aft', 'purge_ere', 'purge_bet', 'embrace', 'get_offtime', 'get_offlines',
    'deny', 'undeny', 'mute', 'unmute', 'mute_list', 'mute_l', 'unmute_l', 'mute_l_list',
}
admin_cmds.update(free_cmds)
primogenat_cmds = {'help', 'silence', 'unsilence', 'kick'}


# region Free
async def help(msg: _Msg):
    """\
    !help: выводит данный хелп
    !help cmd*: поиск хелпа по категориям и командам \
    """
    module = sys.modules[__name__]
    # module_attrs = dir(module)
    # cmds = set(key for key in module_attrs if key[0] != '_' and callable(getattr(module, key)))
    # if not msg.admin:
    #     cmds.intersection_update(free_cmds)
    cmds = msg.get_commands()
    flt = {'free': free_cmds, 'admin': admin_cmds, 'super': only_super,
           'primogenat': primogenat_cmds, 'primogen': primogenat_cmds,
           'r': {'r', 'rw', 'rv'}, }
    if len(msg.args) > 1:
        ln = 1
        if msg.args[1] in flt:
            cmds.intersection_update(flt[msg.args[1]])
            ln = 2
        if msg.args[ln:]:
            cmds = {cmd for cmd in cmds if any(arg in cmd for arg in msg.args[ln:])}
        # cmds.intersection_update(set(msg.text.split()[1:]))

    texts = []
    comf_help = ''
    docs = []
    if cmds:
        if msg.admin and any((cmds == all_cmds, cmds == only_super, cmds == admin_cmds)):
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
            ```''').replace('            ', ''))
        if cmds.intersection(roll_cmds):
            texts.append((r'''```css
            Хелп по броскам дайсов (!roll, !rollw, !rollv, !r, !rw, !rv):
                !roll, !rollw, !rollv - выводят результат бросков в столбец;
                !r, !rw, !rv - имеют тот же синтаксис, что и команды выше, 
                    но выводят кубы в строку, что позволяет бросать больше кубов за раз;
                !команда хdу - прости кинет x кубов y, без подсчёта результатов
                    (если ну указан dу - берётся d10)
                • если указана сложность, тип сравнения или некоторые доп параметры,
                то будут подсчитываться успехи (по умолчанию сложность y/2+1,
                сравнение - '>=')
                !roll +N xdy - к каждому кубу добавится N
                !roll -N xdy - к каждому кубу вычтется N
                !roll xdy+ - подсчитать сумму броска
                !roll xdy+N - подсчитать сумму броска и добавить N
                    если при подсчёте суммы указана проверка по сложности,
                    то будут суммироваться только проходящие по ней броски;
                !roll x1dy1 x2dy2 x3dy3... - бросить несколько разных кубов за раз
                    если хоть у одного будет считаться сумма, то будет считаться у всех;
                    если где-то указана сложность и не считается сумма, будет сумма успехов;
                !roll x1dy1 - x2dy2
                    вычесть из результатов первого броска результаты второго;
                    применимы правила касательно подсчёта суммы и успехов;
            ```''').replace('            ', ''))
            texts.append((r'''```css
                Доп параметры указываются сразу после команды (для всех бросков) 
                    или последними (для данного броска).
                Между собой смешиваются в любом порядке, без пробелов,
                    например: 'sh', 'fsph', 'hf3', 'f1vh' и тому подобное;
                sp/p/v/s - 'бонусы' при макс грани куба (10 для d10) если это успех:
                    sp - +1 доп успех
                    p - +1 доп успех за каждую пару (для d10 - всего 3 успеха за две 10)
                    v - +2 доп успеха за каждую пару (аля механика V5)
                    s - доп броски (рекурсивно), специализация в МТ
                    • любой из них вкл подсчёт успехов, даже если указано лишь кол-во кубов
                    • из всех них за раз работает лишь один доп параметр
                fx  - отнимает успехи за броски меньше или равно x; вкл подсчёт успехов;
                f   - аналогично 'f1'; 
                    • !rollw (!rw) идёт с вкл 'f' по умолчанию
                h   - вывод кубов с тэгом @here 
                    (что включит жёлтую подсветку для всех - удобно для строчных команд);
                !rollw (!rw) полностью идентична !roll (!r), но уже со включенным 'f'
                    (и потому всегда будет считать успехи)
                !rollv (!rv) бросает кубы по правилам V5 (пиктограммы вместо цифр),
                    потому все доп параметры кроме 'h' не имеют для неё смысла
                !команда (без других параметров) - выведет хелп только по этой команде
            ```''').replace('            ', ''))
        docs = [getattr(module, cmd).__doc__ for cmd in cmds]
        comf_help = other.comfortable_help(docs)

    if not cmds or not comf_help:
        texts = 'Увы, с этим ничем не могу помочь :sweat:'
    else:
        texts += other.comfortable_help(docs)

    await msg.qanswer(texts)


async def ignore(msg: _Msg): # TODO more phrases here
    """\
    !ignore: вкл/выкл комментирования Беккетом своих сообщений \
    """
    if msg.author in ram.ignore_users:
        ram.ignore_users.remove(msg.author)
        if msg.author == C.users['cycl0ne']:
            await msg.answer("Мяв, время амнистии 😺?")
        else:
            await msg.answer("Что, кто-то по мне соскучился :relaxed:?")
    else:
        ram.ignore_users.add(msg.author)
        if msg.author == C.users['cycl0ne']:
            await msg.answer("Я к тебе со всей душой, а ты... 😿")
        else:
            await msg.answer("Не хочешь разговаривать, ну и не надо :confused:.")


# async def roll(msg: _msg):
#     """\
#     !roll хdу: кинуть x кубиков-y \
#     """
#     if len(msg.args) < 2:
#         msg.args.append('1d10')
#     rollrange = msg.args[1].split('d')
#     if len(rollrange) == 2 and all(i.isdigit() for i in rollrange):
#         count, dice = int(rollrange[0]), int(rollrange[1])
#         if count > 21:
#             await msg.answer('Перебор, я выиграл :slight_smile:')
#             return
#
#         dices = []
#         for i in range(0, count):
#             dices += ['{:02d}'.format(i + 1), 'd:\t', str(random.randint(1, dice)), '\n']
#         await msg.qanswer("```" + ''.join(dices) + "```")
#     else:
#         await msg.qanswer(other.comfortable_help([str(roll.__doc__)]))


async def roll(msg: _Msg):
    """\
    !roll х: кинуть x кубов d10
    !roll dу: кинуть один куб y
    !roll хdу: кинуть x кубиков-y
    !roll х diff: кинуть x кубов d10 >= (больше или равно) к сложности diff
    !roll хdу diff: кинуть x кубов y >= (больше или равно) к сложности diff
    !roll хdу rel: кинуть x кубов y rel(>,<,==, etc) к сложности (y/2+1)
    !roll хdу rel diff: кинуть x кубов y по отношению rel(>,<,==, etc) к diff сложности
    !roll -//- [spvfh]: кинуть кубы с доп параметрами (см. !help roll)
    !roll +(-)A -//-//-: к результату каждого куба добавить (отнять) A
    !roll хdу+ -//-//- : суммировать результат (только подходящее по сложности, если дана)
    !roll хdу+(-)B -//-: суммировать результат и добавить (отнять) B
    """

    error, count, max_dtype, all_flags, simple, calc_sum, rolls_args = manager.get_dice_param(msg.text[len('!roll '):])

    if not error:

            if count > 21:
                if count > 121:
                    await msg.answer('<@{}>, у тебя перебор, я выиграл 🙂'.format(msg.author))
                else:
                    await msg.answer('Так много кубов... может стоит `!r` попробовать, <@{}>? 🤔'.format(msg.author))
                return

            if max_dtype > C.i10__42:
                await msg.answer('Ну, <@{}>, **таких** дайсов мне не завезли 😕'.format(msg.author))
                return

            text = [('<@{}>, @here,\n```diff\n' if 'h' in all_flags else '<@{}>,\n```diff\n').format(msg.author)]
            text += manager.get_dices(rolls_args, simple=simple, calc_sum=calc_sum)
            text.append('```')

            await msg.qanswer(''.join(text))

    if error:
        await msg.qanswer(other.comfortable_help([str(roll.__doc__)]))
        return


async def r(msg: _Msg):
    """\
    !r х: кинуть x кубов d10
    !r dу: кинуть один куб y
    !r хdу: кинуть x кубиков-y
    !r х diff: кинуть x кубов d10 >= (больше или равно) к сложности diff
    !r хdу diff: кинуть x кубов y >= (больше или равно) к сложности diff
    !r хdу rel: кинуть x кубов y rel(>,<,==, etc) к сложности (y/2+1)
    !r хdу rel diff: кинуть x кубов y по отношению rel(>,<,==, etc) к diff сложности
    !r -//- [spvfh]: кинуть кубы с доп параметрами (см. !help r)
    !r +(-)A -//-//-: к результату каждого куба добавить (отнять) A
    !r хdу+ -//-//- : суммировать результат (только подходящее по сложности, если дана)
    !r хdу+(-)B -//-: суммировать результат и добавить (отнять) B
    """
    error, count, max_dtype, all_flags, simple, calc_sum, rolls_args = manager.get_dice_param(msg.text[len('!r '):])

    if not error:

            if count > 121:
                await msg.answer(r'Увы, <@{}>, столько дайсов у меня нет ¯\_(ツ)_/¯'.format(msg.author))
                return

            if max_dtype > 1000:
                if max_dtype > C.i10__42:
                    await msg.answer('Ну, <@{}>, **таких** дайсов мне не завезли 😕'.format(msg.author))
                else:
                    await msg.answer('Ого, какие кубища... может `!roll` попробовать, <@{}>? 🤔'.format(msg.author))
                return

            text = ['<@{}>:'.format(msg.author)]
            text += manager.get_dices(rolls_args, short=True, simple=simple, calc_sum=calc_sum)
            if 'h' in all_flags:
                text.append('@here')

            await msg.qanswer(' '.join(text))

    if error:
        await msg.qanswer(other.comfortable_help([str(r.__doc__)]))
        return

    pass


async def rw(msg: _Msg):
    """\
    !rw х: кинуть x кубов d10 к сложности 6 с вычетом единиц
    !rw хdу: кинуть x кубиков-y к сложности (y/2+1) с вычетом единиц
    !rw х diff: кинуть x кубов d10 >= (больше или равно) к сложности diff с вычетом единиц
    !rw хdу diff: кинуть x кубов y >= (больше или равно) к сложности diff с вычетом единиц
    !rw хdу rel: кинуть x кубов y rel(>,<,==, etc) к сложности (y/2+1) с вычетом единиц
    !rw хdу rel diff: -//- к сложности diff с вычетом единиц
    !rw -//- [spvh] : кинуть кубы с вычетом единиц и с доп параметрами (см. !help rw)
    """
    t = msg.text[len('!rw '):]
    error, count, max_dtype, all_flags, simple, calc_sum, rolls_args = manager.get_dice_param(t, 'f')

    if not error:

            if count > 121:
                await msg.answer(r'Увы, <@{}>, столько дайсов у меня нет ¯\_(ツ)_/¯'.format(msg.author))
                return

            if max_dtype > 1000:
                if max_dtype > C.i10__42:
                    await msg.answer('Ну, <@{}>, **таких** дайсов мне не завезли 😕'.format(msg.author))
                else:
                    await msg.answer('Ого, какие кубища... может `!rollw` попробовать, <@{}>? 🤔'.format(msg.author))
                return

            text = ['<@{}>:'.format(msg.author)]
            text += manager.get_dices(rolls_args, short=True, simple=simple, calc_sum=calc_sum)
            if 'h' in all_flags:
                text.append('@here')

            await msg.qanswer(' '.join(text))

    if error:
        await msg.qanswer(other.comfortable_help([str(rw.__doc__)]))
        return

    pass


async def rollw(msg: _Msg):
    """\
    !rollw х: кинуть x кубов d10 к сложности 6 с вычетом единиц
    !rollw хdу: кинуть x кубиков-y к сложности (y/2+1) с вычетом единиц
    !rollw х diff: кинуть x кубов d10 >= (больше или равно) к сложности diff с вычетом единиц
    !rollw хdу diff: кинуть x кубов y >= (больше или равно) к сложности diff с вычетом единиц
    !rollw хdу rel: кинуть x кубов y rel(>,<,==, etc) к сложности (y/2+1) с вычетом единиц
    !rollw хdу rel diff: -//- к сложности diff с вычетом единиц
    !rollw -//- [spvh] : кинуть кубы с вычетом единиц и с доп параметрами (см. !help rw)
    """
    t = msg.text[len('!rollw '):]
    error, count, max_dtype, all_flags, simple, calc_sum, rolls_args = manager.get_dice_param(t, 'f')
    if not error:

            if count > 21:
                if count > 121:
                    await msg.answer('<@{}>, у тебя перебор, я выиграл 🙂'.format(msg.author))
                else:
                    await msg.answer('Так много кубов... может стоит `!rw` попробовать, <@{}>? 🤔'.format(msg.author))
                return

            if max_dtype > C.i10__42:
                await msg.answer('Ну, <@{}>, **таких** дайсов мне не завезли 😕'.format(msg.author))
                return

            text = [('<@{}>, @here,\n```diff\n' if 'h' in all_flags else '<@{}>,\n```diff\n').format(msg.author)]
            text += manager.get_dices(rolls_args, simple=simple, calc_sum=calc_sum)
            text.append('```')

            await msg.qanswer(''.join(text))

    if error:
        await msg.qanswer(other.comfortable_help([str(rollw.__doc__)]))
        return


async def rollv(msg: _Msg):
    """\
    !rollv х: просто кинуть x дайсов v5
    !rollv х diff: кинуть x дайсов v5 против сложности diff
    !rollv х diff hunger: кинуть x дайсов v5 против сложности diff с голодом hunger
    """
    error, count, diff, hung, par_keys, simple = manager.get_v5_param(msg.text[len('!rollv '):])

    if not error:
            if count > 21:
                if count > 121:
                    await msg.answer('<@{}>, у тебя перебор, я выиграл 🙂'.format(msg.author))
                else:
                    await msg.answer('Так много кубов... может стоит `!rv` попробовать, <@{}>? 🤔'.format(msg.author))
                return

            text = [('<@{}>, @here,\n```diff\n' if 'h' in par_keys else '<@{}>,\n```diff\n').format(msg.author)]
            text += manager.get_dices_v5(count, diff, hung, simple)
            text.append('```')

            await msg.qanswer(''.join(text))

    if error:
        await msg.qanswer(other.comfortable_help([str(rollv.__doc__)]))
        return


async def rv(msg: _Msg):
    """\
    !rv х: просто кинуть x дайсов v5
    !rv х diff: кинуть x дайсов v5 против сложности diff
    !rv х diff hunger: кинуть x дайсов v5 против сложности diff с голодом hunger
    !rv х diff hunger h: кинуть x дайсов v5 против сложности diff с голодом hunger и @here;
    """
    error, count, diff, hung, par_keys, simple = manager.get_v5_param(msg.text[len('!rv '):])

    if not error:
            if count > 121:
                await msg.answer('<@{}>, у тебя перебор, я выиграл 🙂'.format(msg.author))
                return

            text = ['<@{}>:'.format(msg.author)]
            text += manager.get_dices_v5(count, diff, hung, simple, short=True)
            if 'h' in par_keys:
                text.append('@here')

            await msg.qanswer(' '.join(text))

    if error:
        await msg.qanswer(other.comfortable_help([str(rv.__doc__)]))
        return

# endregion


# region Primogenat
async def silence(msg: _Msg):
    """\
    !silence N username: включить молчанку username на N часов \
    """
    s_N = ''
    err = len(msg.args) < 3
    if not err:
        s_N = msg.args[1].replace(',', '.')
        err = not other.is_float(s_N)

    if err:
        await msg.qanswer(other.comfortable_help([str(silence.__doc__)]))
        return

    name = msg.original[len('!silence ') + len(s_N) + 1:]
    t = max(float(s_N), 0.02)

    await C.client.add_reaction(msg.message, emj.e('ok_hand'))
    user = await manager.silence_on(name, t)
    if user:
        text = 'По решению Примогената, <@{0}> отправлен в торпор на {1} ч.'.format(user.id, t)
        await msg.qanswer(text)
        await msg.say(C.main_ch, text)
        ev.timer_hour()
    elif user is False:
        await msg.qanswer(name + " имеет слишком высокую роль.")
        return
    elif user is None:
        await msg.qanswer("Не могу найти пользователя " + name + ".")
        return


async def silence_f(msg: _Msg):
    """\
    !silence_f N username: включить молчанку username на N часов, тихая и игнорит уровень роли \
    """
    s_N = ''
    err = len(msg.args) < 3
    if not err:
        s_N = msg.args[1].replace(',', '.')
        err = not other.is_float(s_N)

    if err:
        await msg.qanswer(other.comfortable_help([str(silence_f.__doc__)]))
        return

    name = msg.original[len('!silence_f ') + len(s_N) + 1:]
    t = max(float(s_N), 0.02)

    await C.client.add_reaction(msg.message, emj.e('ok_hand'))
    user = await manager.silence_on(name, t, force=True)
    if user:
        text = '<@{0}> отправлен в торпор на {1} ч.'.format(user.id, t)
        await msg.qanswer(text)
        ev.timer_hour()
    else:
        await msg.qanswer("Не могу найти пользователя " + name + ".")
        return


async def unsilence(msg: _Msg):
    """\
    !unsilence username: выключить молчанку для username\
    """

    err = len(msg.args) < 2
    if err:
        await msg.qanswer(other.comfortable_help([str(unsilence.__doc__)]))
        return

    name = msg.original[len('!unsilence '):]
    await C.client.add_reaction(msg.message, emj.e('ok_hand'))
    user = await manager.silence_off(name)
    if user:
        text = 'По решению Примогената, <@{0}> уже выведен из торпора.'.format(user.id)
        await msg.say(C.main_ch, text)
        ev.timer_hour()
    elif user is False:
        await msg.qanswer("Нет пользователя " + name + " в молчанке.")
    elif user is None:
        await msg.qanswer("Не могу найти пользователя " + name + ".")
        return


async def unsilence_all(msg: _Msg):
    """\
    !unsilence_all: выключить запрет на чтения всего для всех пользоателей (не ролей)\
    """
    # await msg.qanswer("Начинаем...")
    await C.client.add_reaction(msg.message, emj.e('ok_hand'))
    for memb in C.prm_server.members:
        await manager.turn_silence(memb, False, force=True)

    await msg.qanswer('Из торпора выведены все.')
    ev.timer_hour()


async def kick(msg: _Msg):
    """\
    !kick username: кикнуть username посредством голосования\
    """
    err = len(msg.args) < 2
    if err:
        await msg.qanswer(other.comfortable_help([str(kick.__doc__)]))
        return

    name = msg.original[len('!kick '):]
    user = other.find_member(C.prm_server, name)
    if not user:
        await msg.qanswer("Не могу найти пользователя " + name + ".")
        return

    if user.top_role >= C.prm_server.me.top_role:
        await msg.qanswer('<@{0}> имеет слишком высокую роль.'.format(user.id))
        return

    text = ('<@{0}> вынес на рассмотрение изгнание <@{1}>. Для принятия решения необходимо __ещё 3 голоса__ "за".'
            '\nНа голосование у вас 10 минут.').format(msg.author, user.id)

    votes = await manager.voting(msg.channel, text=text, timeout=600, votes={msg.author}, count=4)
    if votes:
        text1 = 'Голосами от <@{0}> решение о кике <@{1}> **принято**.'.format('>, <@'.join(votes), user.id)
        await msg.qanswer(text1)
        text2 = 'По решению Примогената, <@{0}> изгоняется из домена.'.format(user.id)
        await msg.say(C.main_ch, text2)
        other.later_coro(15, C.client.kick(user))
    else:
        text1 = 'Голосование окончено, решение о кике <@{0}> **не принято**.'.format(user.id)
        await msg.qanswer(text1)


# endregion


# region Admin
async def dominate(msg: _Msg):
    """\
    !dominate usr text: доминирование (✺_✺) \
    """
    if len(msg.args) < 2:
        await msg.qanswer(other.comfortable_help([str(dominate.__doc__)]))
        return
    if not msg.admin and msg.author != C.users['Creol']:
        await msg.answer(r'Нет у вас доминирования ¯\_(ツ)_/¯')
        return

    auth = other.find_member(C.vtm_server, msg.author)
    who = other.find_member(C.vtm_server, msg.args[1])
    if not auth or not who:
        await msg.qanswer(other.comfortable_help([str(dominate.__doc__)]))
        return
    emb = discord.Embed(title=msg.original[len('!dominate ' + msg.args[1] + ' '):], color=auth.color)
    emb.set_author(name=auth.nick or auth.name, icon_url=auth.avatar_url)
    emb.set_image(url='https://cdn.discordapp.com/attachments/420056219068399617/450428811725766667/dominate.gif')
    #emb.set_footer(text='')
    # ch = other.get_channel(C.channels['sabbat'])
    await msg.type2sent(C.main_ch, text=who.mention, emb=emb)
    #await C.client.send_message(ch, content=who.mention, embed=emb)


async def get_offtime(msg: _Msg):
    """\
    !get_offtime username: узнать, как долго пользователь ничего не пишет
    """
    if len(msg.args) < 2:
        await msg.qanswer(other.comfortable_help([str(get_offtime.__doc__)]))
        return
    name = msg.original[len('!get_offtime '):]
    usr = other.find_member(C.vtm_server, name)
    if not usr:
        await msg.qanswer('Пользователь не найден.')
        return
    await msg.qanswer('{0} последний раз писал(а) {1} назад.'
                      .format(usr.mention, other.sec2str(people.offline(usr.id))))


async def get_offlines(msg: _Msg):
    """\
    !get_offlines d: узнать, кто не пишет уже в течении d дней
    """
    s_ds = msg.original[len('!get_offlines '):].replace(',', '.').replace(' ', '')
    if len(msg.args) < 2 or not other.is_float(s_ds):
        await msg.qanswer(other.comfortable_help([str(get_offlines.__doc__)]))
        return
    r_users = {}
    for role_ in C.vtm_server.role_hierarchy:
        r_users[role_.name] = {}
    ds = float(s_ds)
    check_t = int(ds * 24 * 3600)
    count = 0
    for uid, usr in people.usrs.items():
        t_off = people.offline(usr.id)
        if t_off >= check_t:
            count += 1
            u = other.find_member(C.vtm_server, uid)
            r_users[u.top_role.name][usr.last_m] = ('{0} - писал(а) {1} назад.'
                                       .format(u.mention, other.sec2str(t_off)))
    s_num = str(ds if ds != int(ds) else int(ds))
    if count:
        s_users = 'Пользователи[{0}] не пишущие'.format(count) if count > 1 else 'Уникум не пишущий'
        s_days = ['дней', 'день', 'дня', 'дня', 'дня']
        end_s_num = int(s_num[-1])
        ans = ['{0} уже {1} {2}:'.format(s_users, s_num, s_days[end_s_num < 5 and end_s_num])]
        r_users['Без ролей'] = r_users.pop('@everyone')
        for role_ in r_users:
            if r_users[role_]:
                sorted_users = [r_users[role_][key] for key in sorted(r_users[role_])]
                ans.append('**```{0}[{1}]:```**{2}'.format(role_, len(r_users[role_]), sorted_users[0]))
                ans += sorted_users[1:]
        ans_20 = other.split_list(ans, 20)
        ans = ['\n'.join(v) for v in ans_20]
        await msg.qanswer(ans)
    else:
        await msg.qanswer('Пользователей не пишущих уже {0} дней нет :slight_smile:.'.format(s_num))


# region Interaction commands
async def channel(msg: _Msg):
    """\
    !channel ch*: сохраняет список каналов для !mute, !deny, !purge
    !channel: выводит список сохранённых каналов \
    """
    if len(msg.args) > 1:
        #ram.cmd_channels.setdefault(msg.author, set()).update(set(msg.args[1:]))
        # ram.cmd_channels.setdefault(msg.author, set()).update(other.get_channels(msg.args[1:]))
        ram.cmd_channels.setdefault(msg.author, set()).update(other.find_channels_or_users(msg.args[1:]))
        msg.cmd_ch = ram.cmd_channels.get(msg.author, set())

    # await msg.qanswer(('<#' + '>, <#'.join(msg.cmd_ch) + '>') if msg.cmd_ch else 'All')
    text = other.ch_list(msg.cmd_ch)
    await msg.qanswer((', '.join(text)) if text else 'All')


async def unchannel(msg: _Msg):
    """\
    !unchannel ch* : удаляет каналы из сохранённого списка
    !unchannel: отчищает список сохранённых каналов \
    """
    if len(msg.args) < 2:
        ram.cmd_channels[msg.author] = set()
    else:
        ram.cmd_channels.setdefault(msg.author, set()).difference_update(other.get_channels(msg.args[1:]))

    msg.cmd_ch = ram.cmd_channels.get(msg.author, set())
    # await msg.qanswer(('<#' + '>, <#'.join(msg.cmd_ch) + '>') if msg.cmd_ch else 'All')
    text = other.ch_list(msg.cmd_ch)
    await msg.qanswer((', '.join(text)) if text else 'All')


async def report(msg: _Msg):
    """\
    !report ch* : сохраняет каналы для вывода сообщений (!say !deny !embrace)
    !report: выводит список сохранённых каналов \
    """
    if len(msg.args) > 1:
        ram.rep_channels.setdefault(msg.author, set()).update(other.find_channels_or_users(msg.args[1:]))
        msg.rep_ch = ram.rep_channels.get(msg.author, set())

    text = other.ch_list(msg.rep_ch)
    await msg.qanswer((', '.join(text)) if text else 'None')


async def unreport(msg: _Msg):
    """\
    !unreport ch* : удаляет каналы из сохранённого списка
    !unreport: отчищает список сохранённых каналов \
    """
    if len(msg.args) < 2:
        ram.rep_channels[msg.author] = set()
    else:
        ram.rep_channels.setdefault(msg.author, set()).difference_update(other.find_channels_or_users(msg.args[1:]))

    msg.rep_ch = ram.rep_channels.get(msg.author, set())
    text = other.ch_list(msg.rep_ch)
    await msg.qanswer((', '.join(text)) if text else 'None')


async def say(msg: _Msg):
    """\
    !say text: сказать Беккетом text на каналах из !report \
    """
    await msg.report(msg.original[len('!say '):])


async def sayf(msg: _Msg):
    """\
    !sayf text: сказать Беккетом text во #flood \
    """
    await msg.say(C.main_ch, msg.original[len('!sayf '):])


async def say_wait(msg: _Msg):
    """\
    !say_wait username msg: написать сообщение в ответ на сообщение от username
    !say_wait role msg: написать сообщение в ответ на сообщение от кого-то с role
    !say_wait d msg: написать сообщение через d минут в report
    """
    if len(msg.args) < 3:
        await msg.qanswer(other.comfortable_help([str(say_wait.__doc__)]))
        return

    # user = msg.


async def emoji(msg: _Msg):
    """\
    !emoji: вкл/выкл эмоджи Беккета за пользователя \
    """
    if msg.author in ram.emoji_users:
        ram.emoji_users.discard(msg.author)
        await msg.qanswer('Emoji mode off')
    else:
        ram.emoji_users.add(msg.author)
        await msg.qanswer('Emoji mode on')


async def purge(msg: _Msg):
    """\
    !purge: стереть последнее сообщение в каналах из !channels
    !purge N: стереть N последних сообщений в каждом из каналов из !channel
    !purge N usr*: стереть сообщения юзеров из последних N сообщений в !channel \
    """
    channels = msg.cmd_ch or {msg.channel.id}
    count = msg.args[1] if len(msg.args) > 1 else 1
    check = None

    if len(msg.args) > 2:
        check_set = other.find_users(msg.args[2:])   #set(msg.args[2:])

        def check_user(m):
            return m.author.id in check_set

        check = check_user
    chs = await other.get_channels_or_users(channels)
    for ch in chs:
        await msg.purge(ch, count, check=check)


async def purge_aft(msg: _Msg):
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
        check_set = other.find_members(mess.server, msg.args[4:])

        def check_user(m):
            return m.author.id in check_set

        check = check_user

    await msg.purge(ch, count, check=check, aft=mess)


async def purge_ere(msg: _Msg):
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
        check_set = other.find_members(mess.server, msg.args[4:])

        def check_user(m):
            return m.author.id in check_set

        check = check_user

    await msg.purge(ch, count, check=check, bef=mess)


async def purge_bet(msg: _Msg):
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
        check_set = other.find_members(msg1.server, msg.args[4:])

        def check_user(m):
            return m.author.id in check_set

        check = check_user

    await msg.purge(ch, 1000000, check=check, aft=msg1, bef=msg2)


async def embrace(msg: _Msg):
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
        role = other.find(C.vtm_server.roles, id=msg.args[1])
        ln = 0
        if not role:
            for role_ in C.vtm_server.roles:
                if role_.name in msg.original:
                    if not role or len(role_.name) > len(role.name):
                        role = role_
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
    user = other.find_member(C.vtm_server, name)
    text = await manager.do_embrace(user, clan)
    if text:
        await msg.report(text)
    else:
        await msg.qanswer("Не могу найти такого пользователя.")

# endregion

# region Deny commands


async def deny(msg: _Msg):
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
    users = other.find_users(msg.args[1:]).difference(nope)
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


async def undeny(msg: _Msg):
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
    users = other.find_users(msg.args[1:]).intersection(ram.torpor_users.keys())
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

# endregion

# region Mute commands
# TODO Becketts comments to *mute commands


async def mute(msg: _Msg):
    """\
    !mute: список каналов "выключенного" Беккета-комментатора
    !mute all: выключить комменты Беккета во всех каналах
    !mute ch*. : выключить комменты Беккета в указанных каналах \
    """
    if len(msg.args) > 1:
        if 'all' in msg.args:
            ram.mute_channels.add('all')
        ram.mute_channels.update(other.get_channels(msg.args[1:]))

    await mute_list(msg)


async def unmute(msg: _Msg):
    """\
    !unmute all: включить комменты Беккета для остальных каналов
    !unmute: включить комменты Беккета вообще во всех каналах
    !unmute ch* : включить комменты Беккета в указанных каналах \
    """
    if len(msg.args) < 2:
        ram.mute_channels = set()
    else:
        if 'all' in msg.args:
            ram.mute_channels.difference_update({'all'})
        ram.mute_channels.difference_update(other.get_channels(msg.args[1:]))

    await mute_list(msg)


async def mute_list(msg: _Msg):
    """\
    !mute_list: список каналов "выключенного" Беккета-комментатора \
    """
    await msg.qanswer(('<#' + '>, <#'.join(ram.mute_channels) + '>') if ram.mute_channels else 'None')


async def mute_l(msg: _Msg):
    """\
    !mute_l: список каналов "выключенного" Беккета-комментатора без упоминания
    !mute_l all: выключить комменты Беккета без упоминания во всех каналах
    !mute_l ch*. : выключить комменты Беккета без упоминания в указанных каналах \
    """
    if len(msg.args) > 1:
        if 'all' in msg.args:
            ram.mute_light_channels.add('all')
        ram.mute_light_channels.update(other.get_channels(msg.args[1:]))

    await mute_l_list(msg)


async def unmute_l(msg: _Msg):
    """\
    !unmute_l all: включить комменты Беккета без упоминания для остальных каналов
    !unmute_l: включить комменты Беккета без упоминания вообще во всех каналах
    !unmute_l ch* : включить комменты Беккета без упоминания в указанных каналах \
    """
    if len(msg.args) < 2:
        ram.mute_light_channels = set()
    else:
        if 'all' in msg.args:
            ram.mute_light_channels.difference_update({'all'})
        ram.mute_light_channels.difference_update(other.get_channels(msg.args[1:]))

    await mute_l_list(msg)


async def mute_l_list(msg: _Msg):
    """\
    !mute_light_list: список каналов "выключенного" Беккета-комментатора без упоминания \
    """
    await msg.qanswer(('<#' + '>, <#'.join(ram.mute_light_channels) + '>') if ram.mute_light_channels else 'None')
# endregion
# endregion

# region Super


async def kick_f(msg: _Msg):
    if len(msg.args) < 2:
        return

    name = msg.original[len('!kick_f '):]
    usr = msg.find_member(name)
    if not usr:
        await msg.qanswer('Пользователь не найден.')
    else:
        if other.issuper(usr):
            await msg.qanswer('Пользователя нельзя кикнуть.')
        else:
            await C.client.kick(usr)


async def ban(msg: _Msg):
    if len(msg.args) < 2:
        return

    name = msg.original[len('!ban '):]
    usr = msg.find_member(name)
    if not usr:
        await msg.qanswer('Пользователь не найден.')
    else:
        if other.issuper(usr):
            await msg.qanswer('Пользователя нельзя банить.')
        else:
            await C.client.ban(usr, delete_message_days=0)


async def unban(msg: _Msg):
    if len(msg.args) < 2:
        return

    usr = await other.get_ban_user(msg.cmd_server, msg.original[len('!unban '):])
    if not usr:
        await msg.qanswer('Пользователь не найден.')
    else:
        await C.client.unban(msg.cmd_server, usr)


async def pin(msg: _Msg):
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
            log.jW("Bot haven't permissions here.")
        except discord.NotFound:
            log.jW("Bot can't find message.")


async def unpin(msg: _Msg):
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
            log.jW("Bot haven't permissions here.")
        except discord.NotFound:
            log.jW("Bot can't find message.")


async def delete(msg: _Msg):
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
            log.jW("Bot haven't permissions here.")
        except discord.NotFound:
            log.jW("Bot can't find message.")

    if done:
        await msg.qanswer(":ok_hand:")


# Delete msgs from private channel:
    # m = await C.client.send_message(other.get_user(C.users['Kuro']), content='Тест')
    # ch = m.channel
    # async for message in C.client.logs_from(ch, limit=10):
    #     print(message.id, str(message.author), message.content)
    #     if message.author.id == C.users['bot']:
    #         await C.client.delete_message(message)

async def nickname(msg: _Msg):
    if len(msg.args) > 1:
        name = msg.original[len('!nickname '):]
    else:
        name = 'Beckett'
    await C.client.change_nickname(msg.cmd_server.me, name)  # Beckett


async def test(msg: _Msg):
    ram.game = not ram.game
    await other.test_status(ram.game)


async def play(msg: _Msg):
    game = None
    if len(msg.args) > 1:
        ram.game = msg.original[len('!play '):]
        game = discord.Game(name=ram.game)
    else:
        ram.game = False
    # status = (discord.Status.dnd if ram.game else discord.Status.online)
    await C.client.change_presence(game=game, status=discord.Status.online, afk=False)


async def info(msg: _Msg):
    ans = []
    for s in C.client.servers:  # type: discord.Server
        ans.append(s.name + ' {' + s.id + '}')
        ans.append('\tOwner: ' + str(s.owner) + ' (' + s.owner.mention + ')')
        ans.append('\tCount: ' + str(s.member_count))
        ans.append('\tRoles: ')
        for role_ in s.role_hierarchy:
            ans.append('\t\t' + role_.name + ' {' + role_.mention + '}')
        v = {}
        t = {}
        for ch in s.channels: # type: discord.Channel
            if str(ch.type) == 'text':
                t[ch.position] = '\t\t' + ch.name + ' {' + ch.id + '}'
            elif str(ch.type) == 'voice':
                v[ch.position] = '\t\t' + ch.name + ' {' + ch.id + '}'
            # if ch.type == 4:
            #     continue  # group
        ans.append('\tChannels: ')
        ans += [t[k] for k in sorted(t)]
        ans.append('\tVoices: ')
        ans += [v[k] for k in sorted(v)]
        ans.append('\tMembers: ')
        for m in s.members: # type: discord.Member
            usr_name = str(m) + ('(' + m.display_name + ')' if m.name != m.display_name else '')
            ans.append('\t\t' + usr_name + ' {' + m.mention + '}')
    f_name = 'info[{0}].txt'.format(other.t2utc().strftime('%d|%m|%y %T'))
    with open(f_name, "w") as file:
        print(*ans, file=file, sep="\n")

    log.I('Sending info...')
    log.dropbox_send(f_name, f_name, '/Info/')
    log.I('Sending info done.')
    await msg.qanswer(":ok_hand:")


async def add_role(msg: _Msg):
    if len(msg.args) < 3:
        await msg.qanswer("!add_role user role1 role2 ...")
        return

    usr = msg.find_member(msg.args[1])
    if not usr:
        await msg.qanswer("Can't find user " + msg.args[1])
        return

    new_roles = []
    not_roles = []
    for i in range(2, len(msg.args)):
        role = other.find(msg.cmd_server.roles, id=msg.args[i])
        if not role:
            role = other.find(msg.cmd_server.roles, name=msg.args[i])
        if not role:
            not_roles.append(msg.args[i])
        else:
            new_roles.append(role)

    if not_roles:
        await msg.qanswer("Can't find roles: " + ', '.join(not_roles))
    if not new_roles:
        await msg.qanswer("Can't find any roles!")
        return

    await C.client.add_roles(usr, *new_roles)
    await msg.qanswer(":ok_hand:")


async def rem_role(msg: _Msg):
    if len(msg.args) < 3:
        await msg.qanswer("!rem_role user role1 role2 ...")
        return

    usr = msg.find_member(msg.args[1])
    if not usr:
        await msg.qanswer("Can't find user " + msg.args[1])
        return

    old_roles = []
    not_roles = []
    for i in range(2, len(msg.args)):
        role = other.find(msg.cmd_server.roles, id=msg.args[i])
        if not role:
            role = other.find(msg.cmd_server.roles, name=msg.args[i])
        if not role:
            not_roles.append(msg.args[i])
        else:
            old_roles.append(role)

    if not_roles:
        await msg.qanswer("Can't find roles: " + ', '.join(not_roles))
    if not old_roles:
        await msg.qanswer("Can't find any roles!")
        return

    await C.client.remove_roles(usr, *old_roles)
    await msg.qanswer(":ok_hand:")


async def clear_clans(msg: _Msg):
    if len(msg.args) < 2:
        # get help
        return

    user = other.find_member(C.vtm_server, msg.original[len('!clear_clans '):])
    if user:
        #C.clan_names
        rls = []
        for clan in C.clan_names:   #TODO check for existing role on server
            rls.append(other.find(C.vtm_server.roles, id=C.roles[clan]))
        rls.append(other.find(C.vtm_server.roles, id=C.roles['Sabbat']))
        await C.client.remove_roles(user, *rls)

    else:
        await msg.qanswer("Не могу найти такого пользователя.")


async def read(msg: _Msg):
    """
    !read ch N: прочитать N сообщений в ch
    """
    if len(msg.args) < 3:
        await msg.qanswer(other.comfortable_help([str(read.__doc__)]))
        return

    if msg.args[2].isnumeric():
        num = int(msg.args[2])
    else:
        await msg.qanswer(other.comfortable_help([str(read.__doc__)]))
        return

    if msg.args[1] == 'log':
        log.D('* <read> read from log_file')
        mess = log.read_log(num)
        await msg.qanswer('`' + '`\n`'.join(mess) + '`')
        await msg.qanswer(":ok_hand:")
        return

    ch = await other.get_channel_or_user(msg.args[1])  # type: discord.Channel
    if not ch:
        await msg.qanswer("Can't find channel " + msg.args[1])
        return

    if not ch.is_private:
        pr = ch.permissions_for(ch.server.me)  # type: discord.Permissions
        if not pr.read_message_history:
            await msg.qanswer("No permissions for reading <#{0}>!".format(ch.id))
            return

    log.D('- <read> for {0}({1}) start'.format(ch, ch.id))
    messages = []
    count = 0
    async for message in C.client.logs_from(ch, limit=num):
        messages.append(message)
        count += 1
        if count % 10000 == 0:
            log.D('- - <read> save messages: ', count)
    log.D('- <read> end save with {0} messages'.format(count))
    messages.reverse()
    log.D('- <read> start format messages')
    mess = ['Read from {0} ({1}) at [{2}] with {3} messages:\n'
                .format(ch, ch.id, other.t2utc().strftime('%d|%m|%y %T'), count)]
    base = {}
    for i, message in enumerate(messages):
        mess.append(await log.format_mess(message, date=True, dbase=base))
        mess += (await log.mess_plus(message, save_all_links=False))
        if (i+1) % 10000 == 0:
            log.D('- - <read> format messages: ', i+1)
    log.D('- <read> end format messages')
    await msg.qanswer('\n'.join(mess))
    await msg.qanswer(":ok_hand:")


async def log_channel(msg: _Msg):
    if len(msg.args) < 2:
        await msg.qanswer("!log_channel channel")
        return

    ch = other.get_channel(msg.args[1]) # type: discord.Channel
    if not ch:
        await msg.qanswer("Can't find channel " + msg.args[1])
        return

    pr = ch.permissions_for(ch.server.me) # type: discord.Permissions
    if not pr.read_message_history:
        await msg.qanswer("No permissions for reading <#{0}>!".format(ch.id))
        return

    save_links = len(msg.args) > 2
    ans = await msg.question(('Вы запустили создание лога для канала <#{0}> [{0}] (' +
        ('**с сохранением** изображений' if save_links else '**без сохранения** изображений') + '). '
                             'Это может занять значительное время, если там много сообщений. '
                             'Вы *уверены*, что желаете продолжить?').format(ch.id))
    if ans:
        await msg.qanswer("Хорошо, начинаем...")
    else:
        await msg.qanswer("Отмена log_channel.")
        return

    log.D('- log_channel for #{0}({1}) start'.format(ch.name, ch.id))
    count = 0
    messages = []
    async for message in C.client.logs_from(ch, limit=1000000):
        messages.append(message)
        count += 1
        if count % 10000 == 0:
            log.D('- - <log_channel> save messages: ', count)
    log.D('- log_channel end save with {0} messages'.format(count))
    messages.reverse()

    log.D('- log_channel start format messages')
    mess = ['Log from {0} ({1}) at [{2}] with {3} messages:\n'
                .format(ch.name, ch.id, other.t2utc().strftime('%d|%m|%y %T'), count)]

    channel_links = other.get_channel(C.channels['vtm_links_info_logs'])
    if save_links:
        link_messages = []
        log.D('- log_channel start scan vtm_links_info_logs')
        async for message in C.client.logs_from(channel_links, limit=1000000):
            link_messages.append(message)
        log.D('- log_channel end scan')
        log.D('- log_channel start update links')
        for message in link_messages:
            await log.mess_plus(message, save_all_links=True, update_links=True)
        log.D('- log_channel end update links')
    base = {}
    for i, message in enumerate(messages):
        mess.append(await log.format_mess(message, date=True, dbase=base))
        mess += (await log.mess_plus(message, save_all_links=save_links, other_channel=channel_links))
        if (i+1) % 10000 == 0:
            log.D('- - <log_channel> format messages: ', i+1)
    log.D('- log_channel end format messages')
    # log.jD('base count: ', len(base))
    f_name = 'log_channel({0})[{1}].txt'.format(ch.name, other.t2utc().strftime('%d|%m|%y %T'))
    with open(f_name, "w") as file:
        print(*mess, file=file, sep="\n")

    log.I('Sending log...')
    log.dropbox_send(f_name, f_name, '/Info/')
    log.I('Sending log done.')
    await msg.qanswer(":ok_hand:")


async def server(msg: _Msg):
    ans = ['All servers:']
    for s in C.client.servers:  # type: discord.Server
        ans.append('\t{0.name} [{0.id}] ({0.owner} [{0.owner.id}])'.format(s))

    serv = None
    if len(msg.args) > 1:
        i = msg.original[len('!server '):]
        for s in C.client.servers:
            if s.name == i or s.id == i:
                serv = s
                break
        if serv:
            ram.cmd_server[msg.author] = serv.id
            ans.append('\nYou choose {0.name} now.'.format(serv))
        elif msg.author in ram.cmd_server:
            ram.cmd_server.pop(msg.author)
            ans.append('\nNo command server.')
    else:
        serv = msg.author in ram.cmd_server and C.client.get_server(ram.cmd_server[msg.author])
        if serv:
            ans.append('\nNow command server is {0.name}'.format(serv))
        else:
            ans.append('\nNo command server.')

    await msg.qanswer('\n'.join(ans))


async def info_channels(msg: _Msg):
    ans = []
    servs = (msg.author in ram.cmd_server and [C.client.get_server(ram.cmd_server[msg.author])]) or C.client.servers
    for s in servs:  # type: discord.Server
        ans.append('{0.name} [{0.id}] ({0.owner} [{0.owner.id}]):'.format(s))
        v = {}
        t = {}
        for ch in s.channels:  # type: discord.Channel
            if str(ch.type) == 'text':
                t[ch.position] = ch.name + ' {' + ch.id + '}'
            elif str(ch.type) == 'voice':
                v[ch.position] = ch.name + ' {' + ch.id + '}'
            # if ch.type == 4:
            #     continue  # group
        ans.append('\tChannels: ' + ', '.join([t[k] for k in sorted(t)]))
        ans.append('\tVoices: ' + ', '.join([v[k] for k in sorted(v)]))

    res = '\n'.join(ans)
    try:
        await msg.qanswer(res)
    except Exception as e:
        other.pr_error(e, 'info_channels', 'error')
        print(res)
        await msg.qanswer('Check log.')


async def go_timer(msg: _Msg):
    log.D('Start timer by command.')
    ev.timer_hour()
    if C.is_test:
        await msg.qanswer('Done, look the log.')
    else:
        await msg.qanswer(":ok_hand:")


# region People
async def people_clear(msg: _Msg):
    ans = await msg.question('ВЫ СОБИРАЕТЕСЬ СТЕРЕТЬ ВСЕ ТАБЛИЦЫ ПОЛЬЗОВАТЕЛЕЙ. ЭТО ДЕЙСТВИЕ НЕВОЗМОЖНО ОТМЕНИТЬ.'
                             'ВЫ ТОЧНО ЖЕЛАЕТЕ ПРОДОЛЖИТЬ?')
    if ans:
        people.clear()
        await msg.qanswer(":ok_hand:")
    else:
        await msg.qanswer("Отмена people_clear.")


async def people_sync(msg: _Msg):
    ans = await msg.question('Это займёт некоторое время и полностью перезапишет Базу Данных пользователей. '
                             'Вы **точно** уверены, что *действительно желаете* продолжить?')
    if ans:
        await msg.qanswer("Хорошо, начинаем, наберитесь терпения...")
        await people.sync()
        await msg.qanswer(":ok_hand:")
    else:
        await msg.qanswer("Отмена people_sync.")


async def people_time_sync(msg: _Msg):
    ans = await msg.question('Это займёт некоторое время и перезапишет время последних сообщений пользователей. '
                             'Вы **точно** уверены, что *действительно желаете* продолжить?')
    if ans:
        await msg.qanswer("Хорошо, начинаем, наберитесь терпения...")
        await people.time_sync()
        await msg.qanswer(":ok_hand:")
    else:
        await msg.qanswer("Отмена people_time_sync.")


async def full_update(msg: _Msg):
    log.D('Start full update of people by command.')
    for usr in people.usrs.values():
        if {'add', 'upd', 'del'}.difference(usr.status):
            usr.status = 'upd'

    for gn in people.gone.values():
        if {'add', 'upd', 'del'}.difference(gn.status):
            gn.status = 'upd'

    await go_timer(msg)
# endregion


# region Voice
async def connect(msg: _Msg):
    """
    !connect ch: подсоедениться к войсу
    """
    if len(msg.args) > 1:
        ch = other.get_channel(' '.join(msg.args[1:]))
        if ch:
            if ch.type == discord.ChannelType.voice:
                if C.voice and C.voice.is_connected():
                    await C.voice.move_to(ch)
                else:
                    try:
                        C.voice = await C.client.join_voice_channel(ch)
                    except Exception as e:
                        other.pr_error(e, 'connect')
                        C.voice = C.client.voice_client_in(msg.cmd_server)
            else:
                await msg.qanswer("Канал - не войс")
        else:
            await msg.qanswer("Не найден канал")
    else:
        await msg.qanswer(other.comfortable_help([str(connect.__doc__)]))


async def disconnect(msg: _Msg):
    """
    !disconnect: отлючится от войса
    """
    if C.voice and C.voice.is_connected():
        await C.voice.disconnect()


async def haha1(msg: _Msg):
    if C.voice and C.voice.is_connected():
        C.player = C.voice.create_ffmpeg_player('sound/laugh0.mp3')
        C.player.start()


async def haha2(msg: _Msg):
    if C.voice and C.voice.is_connected():
        C.player = C.voice.create_ffmpeg_player('sound/sabbatlaugh1.mp3')
        C.player.start()
# endregion


# region Test
keys = []
msgs = {}


async def tst(msg: _Msg):
    # t = com.get_resp('test')
    # if t:
    #     await msg.qanswer(t['text'])
    t = ('И помни: индивидуализм - это путь, преграждаемый множеством препятствий и иногда агрессивно настроенной '
            'толпой, но, при всей его сложности - единственно стоящий.',
         'Рад с тобой познакомиться, но мне еще предстоит проверить некоторые слухи.',)
    # t *= 20
    p = 10

    def call(msgs):
        for m in msgs: #type: discord.Message
            print('call:', m.channel, m.content)

    async def a_call(msgs):
        for m in msgs: #type: discord.Message
            await C.client.pin_message(m)

    print(com.msg_queue)
    print(com.msg_args)
    print('---')
    keys.append(com.write_msg(msg.channel, t, extra=p, save_obj=msgs, fun=call))
    print(com.msg_queue)
    print(com.msg_args)
    com.write_msg(msg.channel, 'Ха-ха-ха!', extra=p, save_obj=msgs, fun=call)
    print(com.msg_queue)
    print(com.msg_args)
    # await C.client.add_reaction(msg.message, emj.extra_em[emj.e('a_Tremere_colors2')])
    # await msg.qanswer('<:p_tetjaadmin:448231060275462144> <a:Tremere_red1:525333494683926528>')

    # text = '\n'.join([str(i*10) + ') ' + (('1234 ' * 20) * 30) for i in range(3)])
    # await msg.qanswer(text)
    pass
    pass


async def tst2(msg: _Msg):
    print('tst2')
    com.rem_from_queue(msg.channel.id, keys)
    print(com.msg_queue)
    print(com.msg_args)
    # com.msg_args = {}
    # for k in keys:
    #     if k in com.msg_queue.get(msg.channel.id, []):
    #         com.msg_queue[msg.channel.id].remove(k)


async def tst3(msg: _Msg):
    print(msgs)


async def tst4(msg: _Msg):
    for o in msgs:
        for m in msgs[o]:
            await C.client.delete_message(m)


async def tst_2(msg: _Msg):
    if len(msg.args) < 2:
        await msg.qanswer(other.comfortable_help([str(dominate.__doc__)]))
        return
    if not msg.admin and msg.author != C.users['Creol']:
        await msg.answer(r'Нет у вас доминирования ¯\_(ツ)_/¯')
        return

    auth = msg.find_member(msg.author)
    who = msg.find_member(msg.args[1])
    if not auth or not who:
        await msg.qanswer(other.comfortable_help([str(dominate.__doc__)]))
        return
    emb = discord.Embed(title=msg.original[len('!dominate ' + msg.args[1] + ' '):], color=auth.color)
    emb.set_author(name=auth.nick or auth.name, icon_url=auth.avatar_url)
    emb.set_image(url='https://cdn.discordapp.com/attachments/420056219068399617/450428811725766667/dominate.gif')
    emb.add_field(name='f1', value='it is f1')
    emb.add_field(name='f2', value='it is f2')
    emb.set_footer(text='it is footer', icon_url=msg.cmd_server.me.avatar_url)
    #emb.set_footer(text='')
    await msg.answer(text=who.mention, emb=emb)
    # ch = C.client.get_channel('398645007944384513')
    # await C.client.send_typing(ch)
    # await C.client.send_typing(ch)
    # await C.client.send_file(ch, 'pic/mushroom spores.jpg',content=
    # '*Беккет нынче по лесу гулял,\nГрибочки по тихому он собирал,'
    # '\nНочь вся прошла - Бекки устал,\nИ споры грибные он тут услыхал...*')


async def roles(msg: _Msg):
    #await msg.answer(', '.join(msg.roles))
    return


async def get_invite(msg: _Msg):
    # invs = await C.client.invites_from(msg.server)
    # await msg.qanswer(msg.server.name + ':\n\t' + '\n\t'.join([inv.code for inv in invs]))
    inv = await C.client.create_invite(msg.cmd_server) # Not working with server?
    await msg.qanswer(msg.cmd_server.name + ': ' + inv.code)

'''
async def song(msg: _msg):
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
# endregion
# endregion

all_cmds = set(key for key in dir(sys.modules[__name__]) if key[0] != '_' and callable(getattr(sys.modules[__name__], key)))
only_super = all_cmds.difference(admin_cmds.union(primogenat_cmds).union(free_cmds))
