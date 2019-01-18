import sys
import ast
import datetime
import psycopg2
import psycopg2.extras
import discord

import constants as C
import local_memory as ram
import communication as com
import other
import emj
import people
import manager
import log
timer_hour_handle = None
timer_min_handle = None
voice_alert = {}


def check_server(fun):
    name = fun.__name__

    async def new_fun(*args):
        if not C.Ready:
            print('Not C.Ready, abort ', name, '()')
            return

        server = await fun(*args)
        if server.id == C.prm_server.id:
            log.jD('Call Ev_u ', name)
            await globals()[name + '_u'](*args)
        elif server.id != C.vtm_server.id:
            log.jD('Call Ev_o ', name)
            await globals()[name + '_o'](server, *args)

    new_fun.__name__ = name # it's for @C.client.event
    return new_fun


def upd_server():
    log.I('Update Servers data')
    C.vtm_server = C.client.get_server(C.VTM_SERVER_ID)  # type: discord.Server
    C.tst_server = C.client.get_server(C.TST_SERVER_ID)  # type: discord.Server
    if not C.vtm_server:
        log.E("Can't find server.")
        force_exit()
    if not C.tst_server:
        log.E("Can't find test server.")
        force_exit()

    if C.is_test:
        C.prm_server = C.tst_server
        C.main_ch = C.client.get_channel(C.TEST_CHANNEL_ID)
    else:
        C.prm_server = C.vtm_server
        C.main_ch = C.client.get_channel(C.WELCOME_CHANNEL_ID)

    if not C.main_ch:
        log.E("Can't find welcome_channel.")
        force_exit()


# region on_Events
async def on_voice_state_update_u(before, after):
    global voice_alert
    v_old = before.voice_channel
    v_new = after.voice_channel

    if v_old == v_new:
        return

    if v_old and v_new:
        log.I('<voice> {0} reconnects from #{1} to #{2}.'.format(after, v_old, v_new))
    elif v_old:
        log.I('<voice> {0} disconnects from #{1}.'.format(after, v_old))
    elif v_new:
        log.I('<voice> {0} connects to #{1}.'.format(after, v_new))
        note = com.voice_note(after)
        if note:
            log.D('<voice> Note event')
            await other.type2sent(C.main_ch, note)

    if after.id in C.voice_alert:
        if after.id in voice_alert:
            try:
                await C.client.delete_message(voice_alert.pop(after.id))
            except Exception as e:
                other.pr_error(e, 'on_voice_state_update_u', 'delete_message error')

    user = None
    ch = None
    if C.is_test or (after.id in C.voice_alert and v_new and len(v_new.voice_members) == 1):
        user = after
        ch = v_new # type: discord.Channel
    elif v_old and len(v_old.voice_members) == 1 and v_old.voice_members[0].id in C.voice_alert:
        user = v_old.voice_members[0]
        ch = v_old # type: discord.Channel

    if user and ch:
        log.D('<voice> Event to @here')
        every_prm = ch.overwrites_for(ch.server.default_role)
        if every_prm.connect or (every_prm.connect is None and ch.server.default_role.permissions.connect):
            call = ['@here']
        else:
            call = []
            for obj, perm in ch.overwrites:
                if perm.connect:
                    call.append(obj.mention)
        if call:
            s_call = ', '.join(call)
            mess = await C.client.send_message(C.main_ch, com.voice_event(user, ch, s_call))
            voice_alert[user.id] = mess
            # await other.type2sent(C.main_ch, com.voice_event(user, ch, s_call))


async def on_voice_state_update_o(server, before, after):
    v_old = before.voice_channel
    v_new = after.voice_channel

    if v_old == v_new:
        return

    if v_old and v_new:
        log.I('<voice> {0} reconnects from #{1} to #{2}.'.format(after, v_old, v_new))
    elif v_old:
        log.I('<voice> {0} disconnects from #{1}.'.format(after, v_old))
    elif v_new:
        log.I('<voice> {0} connects to #{1}.'.format(after, v_new))

    if server.id == C.servers['Tilia']:
        if v_new and len(v_new.voice_members) == 1:
            user = after
            ch = v_new
            if user and ch:
                log.D('<voice other> Event to @here')
                await other.type2sent(other.get_channel('Tilia_main'), com.voice_event(user, ch))


async def on_member_join_u(member):
    uid = member.id

    if uid in ram.silence_users:
        t = ram.silence_users[uid]['time'] - other.get_sec_total()
        if t > 0:
            log.I(member, ' come, but Silence is on.')
            await manager.silence_on(uid, t/3600)

    if people.Usr.check_new(member):
        await log.pr_news('{0} ({0.mention}) comeback!'.format(member))
        await C.client.send_message(C.main_ch, com.comeback_msg(uid, people.time_out(uid), people.clan(uid)))
    else:
        await log.pr_news('{0} ({0.mention}) new!'.format(member))
        await C.client.send_message(C.main_ch, com.welcome_msg(uid))


async def on_member_join_o(server, member):
    await log.pr_other_news(server, '{0} ({0.mention}) new!'.format(member))
    def_ch = other.find_def_ch(server)
    await C.client.send_message(def_ch, com.hi(member.id))


async def on_member_remove_u(member):
    # it's triggers on 'go away', kick and ban
    if not other.find(await C.client.get_bans(C.prm_server), id=member.id):
        people.Gn.check_new(member)
        await log.pr_news('{0} ({0.mention}) go away!'.format(member))
        await C.client.send_message(C.main_ch, com.bye_msg(member.id, member.display_name))


async def on_member_remove_o(server, member):
    await log.pr_other_news(server, '{0} ({0.mention}) go away!'.format(member))
    def_ch = other.find_def_ch(server)
    await C.client.send_message(def_ch, com.bye(member.id, member.display_name))


async def on_member_ban_u(member):
    await people.on_ban(member)
    await log.pr_news('Ban {0} ({0.mention})!'.format(member))
    await C.client.send_message(C.main_ch, com.ban_msg(member.id, member.display_name))


async def on_member_ban_o(server, member):
    await log.pr_other_news(server, 'Ban {0} ({0.mention})!'.format(member))
    def_ch = other.find_def_ch(server)
    await C.client.send_message(def_ch, com.bye(member.id, member.display_name))


async def on_member_unban_u(server, user):
    people.on_unban(user)
    await C.client.send_message(C.main_ch, com.unban_msg(user.id))
    await log.pr_news('Unban {0} ({0.mention})!'.format(user))


async def on_member_unban_o(server, server_, user):
    await log.pr_other_news(server, 'Unban {0} ({0.mention})!'.format(user))


async def on_server_emojis_update_u(before, after):
    la = len(after)
    lb = len(before)
    # before, after - list of server emojis
    if la < 1 and lb < 1:
        return
    await log.pr_news('on_server_emojis_update!')
    emj.save_em()


async def on_server_emojis_update_o(server, before, after):
    la = len(after)
    lb = len(before)
    # before, after - list of server emojis
    if la < 1 and lb < 1:
        return
    await log.pr_other_news(server, 'on_server_emojis_update!')


async def on_server_role_create_u(role):
    upd_server()
    await log.pr_news('New Role: ' + role.name + ' {@&' + role.id + '}!')


async def on_server_role_create_o(server, role):
    upd_server()
    await log.pr_other_news(server, 'New Role: ' + role.name + ' {@&' + role.id + '}!')


async def on_server_role_delete_u(role):
    upd_server()
    await log.pr_news('Delete Role: ' + role.name + '!')


async def on_server_role_delete_o(server, role):
    upd_server()
    await log.pr_other_news(server, 'Delete Role: ' + role.name + '!')


async def on_server_role_update_u(before, after):
    upd_server()
    if after.position == before.position + 1 or after.position == before.position - 1:
        return
    names = (before.name + '/' + after.name + ' {@&' + after.id + '}'
        if before.name != '@everyone' else '`@everyone`')

    await log.pr_news('Update Role: ' + names + '!')


async def on_server_role_update_o(server, before, after):
    upd_server()
    if after.position == before.position + 1 or after.position == before.position - 1:
        return
    names = (before.name + '/' + after.name + ' {@&' + after.id + '}'
             if before.name != '@everyone' else '`@everyone`')
    await log.pr_other_news(server, 'Update Role: ' + names + '!')
# endregion


def load_mem():
    log.I('+ load data from memory')
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
        log.I('+ memory loaded successfully')
    finally:
        if conn:
            conn.close()


def save_mem():
    log.I('+ save memory in DB')
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
        log.I('+ memory saved successfully')
    finally:
        if conn:
            conn.close()


async def load():
    load_mem()
    await people.get(check=(not C.is_test))


def save():
    save_mem()
    people.upd()


def stop_hour_timer():
    global timer_hour_handle
    if timer_hour_handle:
        timer_hour_handle.cancel()


def start_hour_timer():
    global timer_hour_handle
    t = 3600
    stop_hour_timer()
    timer_hour_handle = other.later(t, timer_hour)
    log.I('* Start new timer in {0} seconds.'.format(t))


def timer_hour():
    start_hour_timer()
    try:
        log.D('+ Hour timer event!')
        save()
        log.D('+ Timer event finished!')
    except Exception as e:
        other.pr_error(e, 'hour_timer')


def stop_min_timer():
    global timer_min_handle
    if timer_min_handle:
        timer_min_handle.cancel()


def start_min_timer():
    global timer_min_handle
    t = 60
    stop_min_timer()
    timer_min_handle = other.later(t, timer_min)


def timer_min():
    start_min_timer()
    try:
        for uid, user in ram.silence_users.items():
            if other.get_sec_total() > user['time']:
                other.later_coro(1, manager.silence_end(uid))
    except Exception as e:
        other.pr_error(e, 'timer_min')


def start_timers():
    start_hour_timer()
    start_min_timer()


def stop_timers():
    stop_hour_timer()
    stop_min_timer()


def force_exit():
    sys.exit(0)
