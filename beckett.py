# -*- coding: utf8 -*-
import random
import data
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

import local_memory as ram
#import Log

# with open('torpor.json', 'r', encoding='utf-8') as torporFile:
#    torporData = json.load(torporFile)

@C.client.event
async def on_ready():
    print('Logged in as')
    print(C.client.user.name)
    print(C.client.user.id)
    load_mem()
    await other.test_status(ram.game)
    C.server = C.client.get_server(C.VTM_SERVER_ID)
    emj.save_em() # TODO refresh when emojis were updated
    print('------')
    C.Ready = True
    pass


@C.client.event
async def on_member_join(member):
    if not C.Ready:
        return
    welcome_Channel = C.client.get_channel(C.WELCOME_CHANNEL_ID)
    fmt = random.choice(data.welcomeMsgList)
    await C.client.send_message(welcome_Channel, fmt.format(member))


@C.client.event
async def on_reaction_add(reaction, user):
    if not C.Ready:
        return
    message = reaction.message
    emoji = reaction.emoji
    print('[{0}]{{on_reaction_add}} {1}: {2}'.format(
        other.t2s(), user,
        hasattr(emoji,'id') and ('[{0.id}]({0.name})'.format(emoji)) or emoji ))
    print('{{To message}}(by {1})<#{0.channel.name}> {0.author}: {0.content}'.format(
        message, other.t2s(message.timestamp)))
    other.mess_plus(message)
    await emj.on_reaction_add(reaction, user)


@C.client.event
async def on_reaction_remove(reaction, user):
    if not C.Ready:
        return
    message = reaction.message
    emoji = reaction.emoji
    print('[{0}]{{on_reaction_remove}} {1}: {2}'.format(
        other.t2s(), user,
        hasattr(emoji,'id') and ('[{0.id}]({0.name})'.format(emoji)) or emoji ))
    print('{{From message}}(by {1})<#{0.channel.name}> {0.author}: {0.content}'.format(
        message, other.t2s(message.timestamp)))
    other.mess_plus(message)
    await emj.on_reaction_remove(reaction, user)


@C.client.event
async def on_message_edit(before, after):
    if not C.Ready:
        return
    print('[{0}]{{on_edit}}(from {2})<#{1.channel.name}> {1.author}: {1.content}'.format(
        other.t2s(), after, other.t2s(before.timestamp)))
    other.mess_plus(after)


@C.client.event
async def on_message_delete(message):
    if not C.Ready:
        return
    print('[{0}]{{on_delete}}(from {2})<#{1.channel.name}> {1.author}: {1.content}'.format(
        other.t2s(), message, other.t2s(message.timestamp)))
    other.mess_plus(message)


@C.client.event
async def on_message(message):
    if not C.Ready:
        return
    # Log
    print('[{0}]{{on_message}}<#{1.channel.name}> {1.author}: {1.content}'.
          format(other.t2s(message.timestamp), message))
    other.mess_plus(message)
    # End log

    if message.author == C.client.user or message.channel.id in C.ignore_channels:
        return

#    if message.author.id == '414384012568690688' and ram.letter: # Kuro
#     if message.author.id == '109004244689907712' and ram.letter:  # Natali
#         emb = discord.Embed(title="Передай пожалуйста Натали лично в руки.", color=0x206694)
#         emb.set_author(name="Kuro",
#                          icon_url = "https://cdn.discordapp.com/avatars/414384012568690688/f263f8762379c0ee4d5362127857fdab.png")
#         emb.set_image(url='https://cdn.discordapp.com/attachments/420056219068399617/432063393826996224/letter.jpg')
#         emb.set_footer(text='Суббота, 7 апреля 2018')
#         await C.client.send_message(message.channel,content='Мой <@&398223824514056202>, меня просили передать лично вам :love_letter:',embed=emb)
#         #await C.client.send_file(message.channel, 'Beckett.jpg')
#         ram.letter = False
#         return

    await check_message.reaction(message)


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
                except:
                    print("ast.literal_eval can't eval [%s] = '%s'"%(row['var'], row['val']))
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
    for var,val in variables.items():
        if isinstance(val,dict):
            val = {k: v for k,v in val.items() if v != set()}
        rows.append((var, repr(val),))
    try:
        conn = psycopg2.connect(C.DATABASE_URL, sslmode='require')
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("TRUNCATE TABLE memory RESTART IDENTITY")
        query = "INSERT INTO memory (var, val) VALUES (%s, %s)"
        cur.executemany(query, rows)
        conn.commit()
    except psycopg2.DatabaseError as e:
        print('DatabaseError %s' % e)
        sys.exit(1)
    else:
        print('Memory saved successfully')
    finally:
        if conn:
            conn.close()


def on_exit(signum):
    print("Call on_exit by signal %s"%signum)
    C.loop.create_task(C.client.logout())
    pass
    #C.loop.stop()


def main_loop():
    for signame in ('SIGINT', 'SIGTERM'):
        C.loop.add_signal_handler(getattr(signal, signame), functools.partial(on_exit, signame))
    try:
        print("Start ClientRun.")
        C.client.run(C.DISCORD_TOKEN)
    except:
        ei = sys.exc_info()
        print("[ClientRun] Unexpected error:", ei[0], ei[1])
    else:
        print("ClientRun is completed without errors.")
    finally:
        if C.Ready:
            save_mem()
        C.Ready = False
        print('finally exit')


# main_loop[try] -> ERROR -> main_loop[except] -> main_loop[finally] -> sys.exit(0)
# main_loop[try] -> SIG -> on_exit -> main_loop[else] -> main_loop[finally] -> sys.exit(0)
#Log.log_fun(main_loop)
#Log.send_log()
main_loop()
sys.exit(0)

