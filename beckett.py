# -*- coding: utf8 -*-
#import random
#import data
from ctypes.util import find_library
import communication as com
import psycopg2
import psycopg2.extras
import sys
import ast
import signal
import functools
import discord
import constants as C
import check_message
import other
import emj
import people

import local_memory as ram


#import Log


@C.client.event
async def on_ready():
    await other.busy()
    print('Logged in as')
    print(C.client.user.name)
    print(C.client.user.id)
    C.server = C.client.get_server(C.VTM_SERVER_ID)   # type: discord.Server
    C.main_ch = C.client.get_channel(C.WELCOME_CHANNEL_ID)
    emj.prepare()
    print('load data from memory')
    #await C.client.change_nickname(C.server.me, 'Beckett') # Beckett
    load_mem()
    await people.get(check=(not C.Server_Test))
    com.prepare()
    if not discord.opus.is_loaded():
        lb = find_library("opus")
        print('opus: ', lb)
        discord.opus.load_opus(lb)
    other.later(3600, hour_timer())
    print('------ ------ ------')
    C.Ready = True
    await other.test_status(ram.game)

    pass
    pass


async def hour_timer():
    # just for test now
    try:
        print('[{0}]'.format(other.t2s()),'Hour timer!')
    except Exception as e:
        print('[hour_timer] Error: ', e)
    finally:
        other.later(3600, hour_timer())



@C.client.event
async def on_member_join(member):
    if not C.Ready or member.server.id != C.server.id:
        return
    uid = member.id
    if people.Usr.check_new(member):
        await C.client.send_message(C.main_ch, com.comeback_msg(uid, people.time_out(uid), people.clan(uid)))
        await other.pr_say(str(member) + ' comeback!')
    else:
        #fmt = random.choice(data.welcomeMsgList)
        await C.client.send_message(C.main_ch, com.welcome_msg(uid))
        await other.pr_say(str(member) + ' new!')


@C.client.event
async def on_member_remove(member):
    # it's triggers on 'go away', kick and ban
    if not C.Ready or member.server.id != C.server.id:
        return

    #if member.id not in people.gone or people.gone[member.id].status == 'del':
    if not other.find(await C.client.get_bans(C.server), id=member.id):
        people.Gn.check_new(member)
        await C.client.send_message(C.main_ch, com.bye_msg(member.id))
        await other.pr_say(str(member) + ' go away!')


@C.client.event
async def on_member_ban(member):
    if not C.Ready or member.server.id != C.server.id:
        return
    # people.bans += await C.client.get_user_info(member.id)
    # if member.id in people.usrs:
    #     people.usrs[member.id]['status'] = 'del'
    await people.on_ban(member)
    await C.client.send_message(C.main_ch, com.ban_msg(member.id))
    await other.pr_say('Ban ' + str(member))


@C.client.event
async def on_member_unban(server, user):
    if not C.Ready or server.id != C.server.id:
        return
    people.on_unban(user)
    await C.client.send_message(C.main_ch, com.unban_msg(user.id))
    await other.pr_say('Unban ' + str(user))


@C.client.event
async def on_reaction_add(reaction, user):
    if not C.Ready or (getattr(user, 'server', None) and user.server.id != C.server.id):
        return
    message = reaction.message
    emoji = reaction.emoji
    print('[{0}]{{on_reaction_add}} {1}: {2}'.format(
        other.t2s(), user,
        hasattr(emoji, 'id') and ('[{0.id}]({0.name})'.format(emoji)) or emoji))
    print('{{To message}}(by {1})<#{0.channel.name}> {0.author}: {0.content}'.format(
        message, other.t2s(message.timestamp)))
    other.mess_plus(message)
    await emj.on_reaction_add(reaction, user)


@C.client.event
async def on_reaction_remove(reaction, user):
    if not C.Ready or (getattr(user, 'server', None) and user.server.id != C.server.id):
        return
    message = reaction.message
    emoji = reaction.emoji
    print('[{0}]{{on_reaction_remove}} {1}: {2}'.format(
        other.t2s(), user,
        hasattr(emoji, 'id') and ('[{0.id}]({0.name})'.format(emoji)) or emoji))
    print('{{From message}}(by {1})<#{0.channel.name}> {0.author}: {0.content}'.format(
        message, other.t2s(message.timestamp)))
    other.mess_plus(message)
    await emj.on_reaction_remove(reaction, user)


@C.client.event
async def on_server_emojis_update(before, after):
    la = len(after)
    lb = len(before)
    # before, after - list of server emojis
    if ((la < 1 and lb < 1) or
            (lb > 0 and before[0].server != C.server.id) or (la > 0 and after[0].server != C.server.id)):
        return
    await other.pr_say('on_server_emojis_update!')
    emj.save_em()


@C.client.event
async def on_message(message):
    if not C.Ready or (message.server and message.server.id != C.server.id):
        return
    # Log
    print('[{0}]{{on_message}}<#{1.channel.name}> {1.author}: {1.content}'.
          format(other.t2s(message.timestamp), message))
    other.mess_plus(message)
    # End log

    if message.channel.id in C.ignore_channels: # message.author == C.client.user or
        return

#    if message.author.id == '414384012568690688' and ram.letter: # Kuro
#     if message.author.id == '109004244689907712' and ram.letter:  # Natali
#         emb = discord.Embed(title="Передай пожалуйста Натали лично в руки.", color=0x206694)
#         emb.set_author(name="Kuro",
#           icon_url = "https://cdn.discordapp.com/avatars/414384012568690688/f263f8762379c0ee4d5362127857fdab.png")
#         emb.set_image(url='https://cdn.discordapp.com/attachments/420056219068399617/432063393826996224/letter.jpg')
#         emb.set_footer(text='Суббота, 7 апреля 2018')
#         await C.client.send_message(message.channel,
#                   content='Мой <@&398223824514056202>, меня просили передать лично вам :love_letter:',embed=emb)
#         #await C.client.send_file(message.channel, 'Beckett.jpg')
#         ram.letter = False
#         return

    await check_message.reaction(message)


@C.client.event
async def on_message_edit(before, after):
    if not C.Ready or (after.server and after.server.id != C.server.id):
        return
    print('[{0}]{{on_edit}}(from {2})<#{1.channel.name}> {1.author}: {1.content}'.format(
        other.t2s(), after, other.t2s(before.timestamp)))
    other.mess_plus(after)


@C.client.event
async def on_message_delete(message):
    if not C.Ready or (message.server and message.server.id != C.server.id):
        return
    print('[{0}]{{on_delete}}(from {2})<#{1.channel.name}> {1.author}: {1.content}'.format(
        other.t2s(), message, other.t2s(message.timestamp)))
    other.mess_plus(message)


@C.client.event
async def on_server_role_create(role):
    if not C.Ready or role.server.id != C.server.id:
        return
    await other.pr_say('New Role' + role.name + '!')


@C.client.event
async def on_server_role_delete(role):
    if not C.Ready or role.server.id != C.server.id:
        return
    await other.pr_say('Delete Role' + role.name + '!')


@C.client.event
async def on_server_role_update(before, after):
    if not C.Ready or after.server.id != C.server.id:
        return
    await other.pr_say('Update Role' + before.name + '/' + after.name + '!')


def load_mem():
    print('check memory in DB')
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
            if row['var'] in variables:
                try:
                    if row['val'] == 'set()':
                        v = set()
                    else:
                        v = ast.literal_eval(row['val'])
                except Exception as e:
                    print('Error: ', e)
                    print("ast.literal_eval can't eval [%s] = '%s'" % (row['var'], row['val']))
                else:
                    setattr(module, row['var'], v)
    except psycopg2.DatabaseError as e:
        print('DatabaseError %s' % e)
        sys.exit(1)
    else:
        print('Memory loaded successfully')
    finally:
        if conn:
            conn.close()


def save_mem():
    print('save memory in DB')
    module = sys.modules[ram.__name__]
    module_attrs = dir(module)
    variables = {key: getattr(module, key)
                 for key in module_attrs if key[0] != '_' and not callable(getattr(module, key))}
    conn = None
    rows = []
    for var, val in variables.items():
        if isinstance(val, dict):
            val = {k: v for k, v in val.items() if v != set()}
        rows.append((var, repr(val),))
    try:
        conn = psycopg2.connect(C.DATABASE_URL, sslmode='require')
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("TRUNCATE TABLE memory RESTART IDENTITY")
        query = "INSERT INTO memory (var, val) VALUES (%s, %s)"
        cur.executemany(query, rows)
        conn.commit()
    except psycopg2.DatabaseError as e:
        print('[save_mem] <memory> DatabaseError %s' % e)
        sys.exit(1)
    else:
        print('Memory saved successfully')
    finally:
        if conn:
            conn.close()


def on_exit(signum):
    print("Call on_exit by signal %s" % signum)
    C.loop.create_task(C.client.logout())
    pass
    #C.loop.stop()


def main_loop():
    for signame in ('SIGINT', 'SIGTERM'):
        C.loop.add_signal_handler(getattr(signal, signame), functools.partial(on_exit, signame))
    try:
        print("Start ClientRun.")
        C.client.run(C.DISCORD_TOKEN)
    except Exception as e:
        print('Error: ', e)
        ei = sys.exc_info()
        print("[ClientRun] Unexpected error:", ei[0], ei[1])
    else:
        print("ClientRun is completed without errors.")
    finally:
        if C.Ready:
            save_mem()
            if not C.Server_Test:
                people.upd()
        C.Ready = False
        print('finally exit')


# main_loop[try] -> ERROR -> main_loop[except] -> main_loop[finally] -> sys.exit(0)
# main_loop[try] -> SIG -> on_exit -> main_loop[else] -> main_loop[finally] -> sys.exit(0)
#Log.log_fun(main_loop)
#Log.send_log()
main_loop()
sys.exit(0)
