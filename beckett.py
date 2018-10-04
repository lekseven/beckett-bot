# -*- coding: utf8 -*-
#import random
#import data
import os
from ctypes.util import find_library
import psycopg2
import psycopg2.extras
import sys
import ast
import signal
import functools
import datetime
import discord

import communication as com
import constants as C
import check_message
import other
import emj
import people
import local_memory as ram
import log
import event_funs as ev


@C.client.event
async def on_ready():
    await other.busy()
    log.I('Logged in as ', C.client.user, ' (', C.client.user.id, ')')
    prepare_const2()
    emj.prepare()
    log.I('load data from memory')
    load_mem()
    await people.get(check=(not C.is_test))
    com.prepare()
    if not discord.opus.is_loaded():
        lb = find_library("opus")
        log.jD('opus lib: ', lb) # i can't find it on heroku
        if lb:
            discord.opus.load_opus(lb)
        else:
            log.jW('opus lib not load!')
    other.later(3600, hour_timer())
    log.I('Ready to work at ', ram.t_start.strftime('[%D %T]'))
    log.p('------ ------ ------')
    C.Ready = True
    await other.test_status(ram.game)

    pass
    pass
    # sys.exit(0)


def prepare_const():
    log.I('- prepare_const')

    C.is_test = os.environ.get('Server_Test') or False

    C.DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')

    if not C.DISCORD_TOKEN:
        log.E('Config var DISCORD_TOKEN is not defined.')
        sys.exit()

    if C.is_test:
        log.jI('Bot work with Test Server')

    tst_server_key = 'TEST_SERVER_ID'
    tst_channel_key = 'TEST_CHANNEL_ID'
    vtm_server_key = 'VTM_SERVER_ID'
    vtm_channel_key = 'WELCOME_CHANNEL_ID'

    C.VTM_SERVER_ID = os.environ.get(vtm_server_key)
    C.TST_SERVER_ID = os.environ.get(tst_server_key)

    if not C.VTM_SERVER_ID:
        log.E('Config var VTM_SERVER_ID is not defined.')
        sys.exit()

    if not C.TST_SERVER_ID:
        log.E('Config var TST_SERVER_ID is not defined.')
        sys.exit()

    C.WELCOME_CHANNEL_ID = os.environ.get(vtm_channel_key)
    C.TEST_CHANNEL_ID = os.environ.get(tst_channel_key)

    if not C.WELCOME_CHANNEL_ID:
        log.E('Config var WELCOME_CHANNEL_ID is not defined.')
        sys.exit()

    if not C.TEST_CHANNEL_ID:
        log.E('Config var TEST_CHANNEL_ID is not defined.')
        sys.exit()

    C.DATABASE_URL = os.environ.get('DATABASE_URL')
    if not C.DATABASE_URL:
        log.E('Config var DATABASE_URL is not defined.')
        sys.exit()

    C.DROPBOX_ID = os.environ.get('DROPBOX_ID')

    ram.t_start = other.get_now()
    log.I('+ prepare_const done')


def prepare_const2():
    log.I('- prepare_const2')
    C.vtm_server = C.client.get_server(C.VTM_SERVER_ID)  # type: discord.Server
    C.tst_server = C.client.get_server(C.TST_SERVER_ID)  # type: discord.Server
    if not C.vtm_server:
        log.E("Can't find server.")
        sys.exit()
    if not C.tst_server:
        log.E("Can't find test server.")
        sys.exit()

    if C.is_test:
        C.prm_server = C.tst_server
        C.main_ch = C.client.get_channel(C.TEST_CHANNEL_ID)
    else:
        C.prm_server = C.vtm_server
        C.main_ch = C.client.get_channel(C.WELCOME_CHANNEL_ID)

    if not C.main_ch:
        log.E("Can't find welcome_channel.")
        sys.exit()

    C.vtm_news_ch = other.get_channel(C.channels['vtm_news'])
    C.other_news_ch = other.get_channel(C.channels['other_news'])
    C.vtm_links_ch = other.get_channel(C.channels['vtm_links'])
    C.other_links_ch = other.get_channel(C.channels['other_links'])

    if not (C.vtm_news_ch and C.other_news_ch and C.vtm_links_ch and C.other_links_ch):
        log.W("Can't find some of helps channels!.")

    log.I('+ prepare_const2 done')


async def hour_timer():
    # just for test now
    try:
        log.D('[{0}]'.format(other.t2s()), 'Hour timer!')
    except Exception as e:
        other.pr_error(e, 'hour_timer')
    finally:
        other.later(3600, hour_timer())

# Events with check_server
# region Ev.check_server
@C.client.event
async def on_member_join(member):
    await ev.check_server(member.server, ev.on_member_join_u, ev.on_member_join_o, member)


@C.client.event
async def on_member_remove(member):
    # it's triggers on 'go away', kick and ban
    await ev.check_server(member.server, ev.on_member_remove_u, ev.on_member_remove_o, member)


@C.client.event
async def on_member_ban(member):
    await ev.check_server(member.server, ev.on_member_ban_u, ev.on_member_ban_o, member)


@C.client.event
async def on_member_unban(server, user):
    await ev.check_server(server, ev.on_member_unban_u, ev.on_member_unban_o, user)


@C.client.event
async def on_server_emojis_update(before, after):
    await ev.check_server(before[0].server, ev.on_server_emojis_update_u, ev.on_server_emojis_update_o, before, after)


@C.client.event
async def on_server_role_create(role):
    await ev.check_server(role.server, ev.on_server_role_create_u, ev.on_server_role_create_o, role)


@C.client.event
async def on_server_role_delete(role):
    await ev.check_server(role.server, ev.on_server_role_delete_u, ev.on_server_role_delete_o, role)


@C.client.event
async def on_server_role_update(before, after):
    await ev.check_server(before.server, ev.on_server_emojis_update_u, ev.on_server_emojis_update_o, before, after)
# endregion


@C.client.event
async def on_message(message):
    if await log.on_mess(message, 'on_message'):
        await check_message.reaction(message)


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


def load_mem():
    log.I('check memory in DB')
    not_load = {'t_start', 't_finish', 't_work'}
    module = sys.modules[ram.__name__]
    module_attrs = dir(module)
    variables = set(key for key in module_attrs if key[0] != '_' and not callable(getattr(module, key)))
    conn = None
    try:
        conn = psycopg2.connect(C.DATABASE_URL, sslmode='require')
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM memory")
        rows = cur.fetchall()
        for row in rows:
            #print("%s %s %s" % (row["id"], row["var"], row["val"]))
            if row['var'] in variables and not row['var'] in not_load:
                try:
                    if row['val'] == 'set()':
                        v = set()
                    else:
                        v = ast.literal_eval(row['val'])
                except Exception as e:
                    other.pr_error(e, 'load_mem')
                    log.jW("ast.literal_eval can't eval [%s] = '%s'" % (row['var'], row['val']))
                else:
                    setattr(module, row['var'], v)
    except psycopg2.DatabaseError as e:
        log.E('DatabaseError %s' % e)
        sys.exit(1)
    else:
        log.I('memory loaded successfully')
    finally:
        if conn:
            conn.close()


def save_mem():
    log.I('save memory in DB')
    module = sys.modules[ram.__name__]
    module_attrs = dir(module)
    variables = {key: getattr(module, key)
                 for key in module_attrs if key[0] != '_' and not callable(getattr(module, key))}
    conn = None
    rows = []
    for var, val in variables.items():
        if isinstance(val, dict):
            val = {k: v for k, v in val.items() if v != set()}
        if isinstance(val, (datetime.datetime, datetime.timedelta)):
            val = str(val)
        rows.append((var, repr(val),))
    try:
        conn = psycopg2.connect(C.DATABASE_URL, sslmode='require')
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("TRUNCATE TABLE memory RESTART IDENTITY")
        query = "INSERT INTO memory (var, val) VALUES (%s, %s)"
        cur.executemany(query, rows)
        conn.commit()
    except psycopg2.DatabaseError as e:
        log.E('[save_mem] <memory> DatabaseError %s' % e)
        sys.exit(1)
    else:
        log.I('Memory saved successfully')
    finally:
        if conn:
            conn.close()


def on_exit(signum):
    log.I("Call on_exit by signal %s" % signum)
    C.loop.create_task(C.client.logout())
    pass
    #C.loop.stop()


def main_loop():
    for signame in ('SIGINT', 'SIGTERM'):
        C.loop.add_signal_handler(getattr(signal, signame), functools.partial(on_exit, signame))
    try:
        log.I("Start ClientRun.")
        C.client.run(C.DISCORD_TOKEN)
    except Exception as e:
        other.pr_error(e, 'ClientRun', 'Unexpected error')
    else:
        log.I("ClientRun is completed without errors.")
    finally:
        ram.t_finish = other.get_now()
        ram.t_work = (ram.t_finish-ram.t_start)
        if C.Ready:
            C.Ready = False
            save_mem()
            if not C.is_test:
                people.upd()
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
sys.exit(0)
