# -*- coding: utf8 -*-
#import data
import signal
from os import environ as os__environ
from ctypes.util import find_library
from functools import partial as functools__partial
from discord import opus as discord__opus

import constants as C
import check_message
import other
import emj
import local_memory as ram
import log
import event_funs as ev

# hack to fix discord update
# TODO: update discord and rewrite the whole code (=_=)
from collections import namedtuple
from discord import channel as discord_channel
discord_channel.Overwrites = namedtuple('Overwrites', 'id allow deny type deny_new allow_new')


@C.client.event
async def on_ready():
    ram.debug = C.is_test
    await other.busy()
    log.I(f'Logged in as {C.client.user} (id: {C.client.user.id}, Test: {C.is_test})')
    prepare_const2()
    emj.prepare()
    await ev.load()
    ram.debug = ram.debug or C.is_test
    if not discord__opus.is_loaded():
        lb = find_library("opus")
        log.jD('opus lib: ', lb) # i can't find it on heroku
        if lb:
            discord__opus.load_opus(lb)
        else:
            log.jI('opus lib not load!')
    ev.start_timers()
    log.I('Beckett ready for work now, after starting at ', ram.t_start.strftime('[%d/%m/%y %T]'))
    log.p('======= ' * 10)
    await test_fun() # for debugging an testing
    C.Ready = True
    await other.test_status(ram.game)


def prepare_const():
    log.I('- prepare_const')

    st = os__environ.get('Server_Test')
    C.is_test = bool(st) and st not in ('0', 'False', 'false', '')

    C.DISCORD_TOKEN = os__environ.get('DISCORD_TOKEN')

    if not C.DISCORD_TOKEN:
        log.E('Config var DISCORD_TOKEN is not defined.')
        ev.force_exit()

    if C.is_test:
        log.jI('Bot work with Test Server')
    else:
        C.ignore_channels.update(C.test_channels)

    tst_server_key = 'TEST_SERVER_ID'
    tst_channel_key = 'TEST_CHANNEL_ID'
    vtm_server_key = 'VTM_SERVER_ID'
    vtm_channel_key = 'WELCOME_CHANNEL_ID'

    C.VTM_SERVER_ID = os__environ.get(vtm_server_key)
    C.TST_SERVER_ID = os__environ.get(tst_server_key)

    if not C.VTM_SERVER_ID:
        log.E('Config var VTM_SERVER_ID is not defined.')
        ev.force_exit()

    if not C.TST_SERVER_ID:
        log.E('Config var TST_SERVER_ID is not defined.')
        ev.force_exit()

    C.WELCOME_CHANNEL_ID = os__environ.get(vtm_channel_key)
    C.TEST_CHANNEL_ID = os__environ.get(tst_channel_key)

    if not C.WELCOME_CHANNEL_ID:
        log.E('Config var WELCOME_CHANNEL_ID is not defined.')
        ev.force_exit()

    if not C.TEST_CHANNEL_ID:
        log.E('Config var TEST_CHANNEL_ID is not defined.')
        ev.force_exit()

    C.DATABASE_URL = os__environ.get('DATABASE_URL')
    if not C.DATABASE_URL:
        log.E('Config var DATABASE_URL is not defined.')
        ev.force_exit()

    C.DROPBOX_ID = os__environ.get('DROPBOX_ID')

    ram.t_start = other.get_now()
    log.I('+ prepare_const done')


def prepare_const2():
    log.I('- prepare_const2')
    ev.upd_server()

    C.vtm_news_ch = other.get_channel(C.channels['vtm_news'])
    C.other_news_ch = other.get_channel(C.channels['other_news'])
    C.vtm_links_ch = other.get_channel(C.channels['vtm_links'])
    C.other_links_ch = other.get_channel(C.channels['other_links'])

    if not (C.vtm_news_ch and C.other_news_ch and C.vtm_links_ch and C.other_links_ch):
        log.W("Can't find some of helps channels!.")

    log.I('+ prepare_const2 done')


# Events with check_server
# region Ev.check_server
# noinspection PyUnusedLocal
@C.client.event
@ev.check_server
async def on_voice_state_update(before, after):
    return after.server


@C.client.event
@ev.check_server
async def on_member_join(member):
    return member.server


@C.client.event
@ev.check_server
async def on_member_remove(member):
    # it's triggers on 'go away', kick and ban
    return member.server


# noinspection PyUnusedLocal
@C.client.event
@ev.check_server
async def on_member_update(before, after):
    # it's triggers on changing status, game playing, avatar, nickname or roles
    return after.server


@C.client.event
@ev.check_server
async def on_member_ban(member):
    return member.server


# noinspection PyUnusedLocal
@C.client.event
@ev.check_server
async def on_member_unban(server, user):
    return server


# noinspection PyUnusedLocal
@C.client.event
@ev.check_server
async def on_server_emojis_update(before, after):
    return before[0].server


@C.client.event
@ev.check_server
async def on_server_role_create(role):
    return role.server


@C.client.event
@ev.check_server
async def on_server_role_delete(role):
    return role.server


# noinspection PyUnusedLocal
@C.client.event
@ev.check_server
async def on_server_role_update(before, after):
    return before.server
# endregion


@C.client.event
async def on_message(message:C.Types.Message):
    ev.on_user_life_signs(message.author.id)
    if await log.on_mess(message, 'on_message'):
        await check_message.reaction(message)


# noinspection PyUnusedLocal
@C.client.event
async def on_message_edit(before:C.Types.Message, after:C.Types.Message):
    ev.on_user_life_signs(after.author.id)
    if await log.on_mess(after, 'on_message_edit'):
        await check_message.reaction(after, edit=True)


@C.client.event
async def on_message_delete(message):
    if await log.on_mess(message, 'on_message_delete'):
        await check_message.delete_reaction(message)


@C.client.event
async def on_reaction_add(reaction, user):
    ev.on_user_life_signs(user.id)
    if await log.on_reaction(reaction, 'on_reaction_add', user):
        await emj.on_reaction_add(reaction, user)


@C.client.event
async def on_reaction_remove(reaction, user):
    if await log.on_reaction(reaction, 'on_reaction_remove', user):
        await emj.on_reaction_remove(reaction, user)


def main_loop():
    for sig_name in ('SIGINT', 'SIGTERM'):
        C.loop.add_signal_handler(getattr(signal, sig_name), functools__partial(ev.on_exit, sig_name))
    try:
        log.I("Start ClientRun.")
        C.client.run(C.DISCORD_TOKEN)
    except Exception as e:
        other.pr_error(e, 'ClientRun', 'Unexpected error')
    else:
        log.I("ClientRun is completed without errors.")
    finally:
        ev.on_final_exit()


async def test_fun():
    return
    pass
    pass


# main_loop[try] -> ERROR -> main_loop[except] -> main_loop[finally] -> sys.exit(0)
# main_loop[try] -> SIG -> on_exit -> main_loop[else] -> main_loop[finally] -> sys.exit(0)
#Log.log_fun(main_loop)
#Log.send_log()
prepare_const()
#main_loop()
log.log_fun(main_loop)
log.send_log()
ev.force_exit()
