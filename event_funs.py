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
import log
timer_handle = None


async def check_server(server, usual_fun, other_fun, *args):
    """
    :type server: discord.Server
    :type usual_fun: Function
    :type other_fun: Function
    """
    if not C.Ready:
        return

    if server.id == C.prm_server.id:
        await usual_fun(*args)
    elif server.id != C.vtm_server.id:
        await other_fun(server, *args)


# region on_Events
async def on_member_join_u(member, *args):
    uid = member.id
    if people.Usr.check_new(member):
        await C.client.send_message(C.main_ch, com.comeback_msg(uid, people.time_out(uid), people.clan(uid)))
        await log.pr_news('{0} ({0.mention}) comeback!'.format(member))
    else:
        await C.client.send_message(C.main_ch, com.welcome_msg(uid))
        await log.pr_news('{0} ({0.mention}) new!'.format(member))


async def on_member_join_o(server, member, *args):
    await log.pr_other_news(server, '{0} ({0.mention}) new!'.format(member))


async def on_member_remove_u(member, *args):
    # it's triggers on 'go away', kick and ban
    if not other.find(await C.client.get_bans(C.prm_server), id=member.id):
        people.Gn.check_new(member)
        await C.client.send_message(C.main_ch, com.bye_msg(member.id))
        await log.pr_news('{0} ({0.mention}) go away!'.format(member))


async def on_member_remove_o(server, member, *args):
    await log.pr_other_news(server, '{0} ({0.mention}) go away!'.format(member))


async def on_member_ban_u(member, *args):
    await people.on_ban(member)
    await C.client.send_message(C.main_ch, com.ban_msg(member.id))
    await log.pr_news('Ban {0} ({0.mention})!'.format(member))


async def on_member_ban_o(server, member, *args):
    await log.pr_other_news(server, 'Ban {0} ({0.mention})!'.format(member))


async def on_member_unban_u(user, *args):
    people.on_unban(user)
    await C.client.send_message(C.main_ch, com.unban_msg(user.id))
    await log.pr_news('Unban {0} ({0.mention})!'.format(user))


async def on_member_unban_o(server, user, *args):
    await log.pr_other_news(server, 'Unban {0} ({0.mention})!'.format(user))


async def on_server_emojis_update_u(before, after, *args):
    la = len(after)
    lb = len(before)
    # before, after - list of server emojis
    if la < 1 and lb < 1:
        return
    await log.pr_news('on_server_emojis_update!')
    emj.save_em()


async def on_server_emojis_update_o(server, before, after, *args):
    la = len(after)
    lb = len(before)
    # before, after - list of server emojis
    if la < 1 and lb < 1:
        return
    await log.pr_other_news(server, 'on_server_emojis_update!')


async def on_server_role_create_u(role, *args):
    await log.pr_news('New Role: ' + role.name + '!')


async def on_server_role_create_o(server, role, *args):
    await log.pr_other_news(server, 'New Role: ' + role.name + '!')


async def on_server_role_delete_u(role, *args):
    await log.pr_news('Delete Role: ' + role.name + '!')


async def on_server_role_delete_o(server, role, *args):
    await log.pr_other_news(server, 'Delete Role: ' + role.name + '!')


async def on_server_role_update_u(before, after, *args):
    await log.pr_news('Update Role: ' + before.name + '/' + after.name + '!')


async def on_server_role_update_o(server, before, after, *args):
    await log.pr_other_news(server, 'Update Role: ' + before.name + '/' + after.name + '!')
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


def stop_timer():
    global timer_handle
    if timer_handle:
        timer_handle.cancel()


def start_timer():
    global timer_handle
    t = 3600
    stop_timer()
    timer_handle = other.later(t, timer)
    log.I('* Start new timer in {0} seconds.'.format(t))


def timer():
    start_timer()
    try:
        log.D('+ Hour timer event!')
        save()
        log.D('+ Timer event finished!')
    except Exception as e:
        other.pr_error(e, 'hour_timer')


def force_exit():
    sys.exit(0)
