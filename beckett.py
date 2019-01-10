# -*- coding: utf8 -*-
#import random
#import data
from os import environ as os__environ
import signal
from ctypes.util import find_library
from functools import partial as functools__partial
import discord

import constants as C
from communication import prepare as com__prepare
from check_message import reaction as check_message__reaction
import other
import emj
import local_memory as ram
import log
import event_funs as ev


@C.client.event
async def on_ready():
    await other.busy()
    log.I('Logged in as ', C.client.user, ' (', C.client.user.id, ')')
    prepare_const2()
    emj.prepare()
    await ev.load()
    com__prepare()
    if not discord.opus.is_loaded():
        lb = find_library("opus")
        log.jD('opus lib: ', lb) # i can't find it on heroku
        if lb:
            discord.opus.load_opus(lb)
        else:
            log.jW('opus lib not load!')
    ev.start_timers()
    log.I('Beckett ready for work now, after starting at ', ram.t_start.strftime('[%D %T]'))
    log.p('------ ------ ------')
    C.Ready = True
    await other.test_status(ram.game)
    server = C.vtm_server
    # ch = other.get_channel('chantry')
    # prm = ch.permissions_for(C.vtm_server.me)
    # prm2 = ch.overwrites_for(C.vtm_server.me)
    # for ch in server.channels:
    #     bot_prm = ch.permissions_for(server.me)
    #     if bot_prm.manage_roles:
    #         print(ch)


    pass
    pass
    # ev.force_exit()


def prepare_const():
    log.I('- prepare_const')

    C.is_test = os__environ.get('Server_Test') or False

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

    ram.t_start = other.t2utc()
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


@C.client.event
@ev.check_server
async def on_member_ban(member):
    return member.server


@C.client.event
@ev.check_server
async def on_member_unban(server, user):
    return server


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


@C.client.event
@ev.check_server
async def on_server_role_update(before, after):
    return before.server
# endregion


@C.client.event
async def on_message(message):
    if await log.on_mess(message, 'on_message'):
        await check_message__reaction(message)


@C.client.event
async def on_message_edit(before, after):
    await log.on_mess(after, 'on_message_edit')


@C.client.event
async def on_message_delete(message):
    await log.on_mess(message, 'on_message_delete')


@C.client.event
async def on_reaction_add(reaction, user):
    if await log.on_reaction(reaction, 'on_reaction_add', user):
        await emj.on_reaction_add(reaction, user)


@C.client.event
async def on_reaction_remove(reaction, user):
    if await log.on_reaction(reaction, 'on_reaction_remove', user):
        await emj.on_reaction_remove(reaction, user)


def on_exit(signum):
    log.I("Call on_exit by signal %s" % signum)
    C.loop.create_task(C.client.logout())
    ev.stop_timers()
    C.was_Ready = C.Ready
    C.Ready = False
    pass
    #C.loop.stop()


def main_loop():
    for signame in ('SIGINT', 'SIGTERM'):
        C.loop.add_signal_handler(getattr(signal, signame), functools__partial(on_exit, signame))
    try:
        log.I("Start ClientRun.")
        C.client.run(C.DISCORD_TOKEN)
    except Exception as e:
        other.pr_error(e, 'ClientRun', 'Unexpected error')
    else:
        log.I("ClientRun is completed without errors.")
    finally:
        ram.t_finish = other.t2utc()
        ram.t_work = (ram.t_finish-ram.t_start)
        if C.was_Ready:
            ev.save()
        log.I('Finally exit at ', ram.t_finish.strftime('[%D %T]'),
              ', working for ', other.delta2s(ram.t_work))
        log.p('------ ------ ------')


# main_loop[try] -> ERROR -> main_loop[except] -> main_loop[finally] -> sys.exit(0)
# main_loop[try] -> SIG -> on_exit -> main_loop[else] -> main_loop[finally] -> sys.exit(0)
#Log.log_fun(main_loop)
#Log.send_log()
prepare_const()
#main_loop()
log.log_fun(main_loop)
log.send_log()
ev.force_exit()
