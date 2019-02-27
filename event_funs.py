import sys
import ast
import datetime
import psycopg2
import psycopg2.extras
import discord
from os.path import getmtime as os__getmtime

import constants as C
import local_memory as ram
import communication as com
import other
import emj
import people
import manager
import log
import data

timer_quarter_h_handle = None
timer_half_min_handle = None
voice_alert_msg = {}
voice_alert_ids = {}
not_embrace = set()
timer_quarter_works = 0
TMR_IN_H = 4
day_ev_check = 0

user_games = {}
VTMB = {'vampire', 'masquerade', 'bloodlines'}


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
    global voice_alert_msg
    v_old = before.voice_channel
    v_new = after.voice_channel

    if v_new:
        on_user_life_signs(after.id)

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
            await other.type2sent(after, note)

    await _del_voice_alert(after.id)
    user = None
    ch = None
    if C.is_test or (after.id in C.voice_alert and v_new):
        user = after
        ch = v_new # type: discord.Channel
    elif v_old and v_old.voice_members[0].id in C.voice_alert:
        user = v_old.voice_members[0]
        await _del_voice_alert(user.id)
        ch = v_old # type: discord.Channel

    if user and ch and len(ch.voice_members) == 1 and not other.s_in_s(('radio', 'радио'), ch.name.lower()):
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
            va_ids = voice_alert_ids.setdefault(user.id, [])
            va_msg = voice_alert_msg.setdefault(user.id, [])
            va_ids.append(com.write_msg(C.main_ch, text=com.voice_event(user, ch, s_call), save_obj=va_msg))
            # mess = await C.client.send_message(C.main_ch, com.voice_event(user, ch, s_call))
            # voice_alert_msg[user.id] = mess
            # await other.type2sent(C.main_ch, com.voice_event(user, ch, s_call))


async def _del_voice_alert(uid):
    if uid not in C.voice_alert:
        return
    com.rem_from_queue(C.main_ch.id, voice_alert_ids.setdefault(uid, []))
    voice_alert_ids.pop(uid)
    if uid in voice_alert_msg:
        while voice_alert_msg[uid]:
            try:
                await C.client.delete_message(voice_alert_msg[uid].pop())
            except Exception as e:
                other.pr_error(e, 'on_voice_state_update_u', 'delete_message error')


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
            timer_quarter_h()

    if people.Usr.check_new(member):
        not_embrace.add(uid)
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


async def on_member_update_u(before: discord.Member, after: discord.Member):
    # it's triggers on changing status, game playing, avatar, nickname or roles
    #
    if after.id == C.users['bot']:
        return

    smth_happend = False
    a_n = other.uname(after)

    if before.display_name != after.display_name or before.name != after.name:
        smth_happend = True
        b_n = other.uname(before)
        log.I(f'<on_member_update> {b_n} change nickname to {a_n}.')

    if before.game != after.game:
        smth_happend = True
        if before.game and after.game:
            log.I(f'<on_member_update> {a_n} go play from {before.game.name} to {after.game.name}.')
        elif before.game:
            log.I(f'<on_member_update> {a_n} stop play {before.game.name}.')
        elif after.game:
            log.I(f'<on_member_update> {a_n} start play {after.game.name}.')
        else:
            log.I(f'<on_member_update> {{???}} {a_n} - game change, but there are no games...')

        if after.id == C.users['Natali']:
            if before.game and C.prm_server.me.game.name == before.game.name:
                await other.set_game('')
            if after.game and not C.prm_server.me.game:
                await other.set_game(after.game.name)

        user_g = user_games.pop(after.id, {'name': '', 'h': 0})
        # degradation
        if False and other.rand() < 0.5 and (before.game and before.game.name and after.id not in ram.ignore_users and
                people.was_writing(after.id, 48) and user_g['h'] >= TMR_IN_H):
            phr = com.get_t('game', user=f'<@{after.id}>', game=f"«{user_g['name']}»")
            com.write_msg(C.main_ch, phr)

        if after.game and after.game.name:
            user_games[after.id] = {'name': after.game.name, 'h': 0}

    if before.avatar_url != after.avatar_url:
        smth_happend = True
        urls = []
        for url in (before.avatar_url, after.avatar_url):
            urls.append(' ?'.join(url.split('?', maxsplit=1)))
        b_url, a_url = urls

        if before.avatar_url and after.avatar_url:
            await log.pr_news(f'<on_member_update> {a_n} change avatar from \n{a_url} \nto\n{b_url}')
        elif before.avatar_url:
            await log.pr_news(f'<on_member_update> {a_n} delete avatar: \n{b_url}')
        elif after.avatar_url:
            await log.pr_news(f'<on_member_update> {a_n} set avatar: \n{a_url}')
        else:
            log.I(f'<on_member_update> {{???}} {a_n} - avatar change, but there are no avatar_urls...')

        # degradation
        if False and after.avatar_url and after.id not in ram.ignore_users and people.was_writing(after.id, 48):
            phr = com.get_t('new_avatar', user=f'<@{after.id}>')
            com.write_msg(C.main_ch, phr)

    if before.roles != after.roles:
        smth_happend = True
        old_roles = [('@&' + r.name) for r in before.roles if r not in after.roles]
        new_roles = [('@&' + r.name) for r in after.roles if r not in before.roles]
        if old_roles:
            log.I(f'<on_member_update> {a_n} lost role(s): {", ".join(old_roles)}.')
        if new_roles:
            log.I(f'<on_member_update> {a_n} get role(s): {", ".join(new_roles)}.')
            new_clan_roles = C.clan_ids.intersection({r.id for r in after.roles if r not in before.roles})
            if after.id not in not_embrace and len(before.roles) == 1 and new_clan_roles:
                clan_id = other.choice(new_clan_roles)
                clan_name = C.role_by_id[clan_id]
                log.jI(f'<on_member_update> {a_n} get new clan role "{clan_name}" => call do_embrace.')
                sir_id = manager.just_embrace_say(after, clan_name=clan_name)
                if sir_id:
                    if clan_id in C.clan_channels:
                        clan_ch = C.clan_channels[clan_id]
                        phr = com.get_t(all_keys=('clan_welcome', clan_ch), user=f'<@{after.id}>', sir=f'<@{sir_id}>')
                        com.write_msg(clan_ch, phr)

            elif len(before.roles) > 1 and C.roles['Pander'] in new_clan_roles:
                log.jI(f'<on_member_update> {a_n} go to Pander => delete other clan roles if it\'s exist.')
                del_clans_id = C.clan_ids.difference({C.roles['Pander']})
                rem_roles = {r for r in after.roles if r.id in del_clans_id}
                if rem_roles:
                    await C.client.remove_roles(after, *rem_roles)
                    str_rem_r = f"<@&{'>, <@&'.join(r.id for r in rem_roles)}>"
                    phr = com.get_t('to_Pander', user=f'<@{after.id}>',
                                    old_clans=str_rem_r, pander=f"<@&{C.roles['Pander']}>")
                    com.write_msg(C.main_ch, phr)

    if before.status != after.status or not smth_happend:
        people.online_change(after.id, after.status, force=before.status == after.status)
        # degradation
        g_key = False # people.online_ev(after.id) if (after.id not in ram.ignore_users) else False
        if g_key:
            gt_key = {'g_key': g_key, 'g_type': 0}
            phr = com.phrase_gt(gt_key, after.id)
            if phr:
                com.write_msg(C.main_ch, phr)
                people.set_gt(after.id, gt_key['g_key'])

    if (smth_happend or people.is_online(after.id)) and before.roles == after.roles:
        on_user_life_signs(after.id)


# noinspection PyUnusedLocal
async def on_member_update_o(server: discord.Server, before: discord.Member, after: discord.Member):
    """"""
    '''if server.id != C.vtm_server.id:
        return

    smth_happend = False
    if before.display_name != after.display_name or before.name != after.name:
        smth_happend = True

    if before.game != after.game:
        smth_happend = True

    if before.avatar_url != after.avatar_url:
        smth_happend = True

    if before.roles != after.roles:
        smth_happend = True

    if before.status != after.status or not smth_happend:
        if C.is_test and before.status == after.status and str(after.status) != 'offline':
            await log.pr_news(f'{{TEST}} <on_status_update> {other.uname(after)} change online to online!')
        # people.online_change(after.id, after.status, force=before.status == after.status)
    '''
    pass


async def on_member_ban_u(member):
    await people.on_ban(member)
    await log.pr_news('Ban {0} ({0.mention})!'.format(member))
    await C.client.send_message(C.main_ch, com.ban_msg(member.id, member.display_name))


async def on_member_ban_o(server, member):
    await log.pr_other_news(server, 'Ban {0} ({0.mention})!'.format(member))
    def_ch = other.find_def_ch(server)
    await C.client.send_message(def_ch, com.bye(member.id, member.display_name))


# noinspection PyUnusedLocal
async def on_member_unban_u(server, user):
    people.on_unban(user)
    await C.client.send_message(C.main_ch, com.unban_msg(user.id))
    await log.pr_news('Unban {0} ({0.mention})!'.format(user))


# noinspection PyUnusedLocal
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
        log.E('<ev.load_mem> DatabaseError %s' % e)
        sys.exit(1)
    else:
        log.I('+ memory loaded successfully')
    finally:
        if conn:
            conn.close()


def load_texts_used():
    log.D('+ load data_used from DB')
    conn = None
    com.d2u.data_used = []
    try:
        conn = psycopg2.connect(C.DATABASE_URL, sslmode='require')
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM data_used ORDER BY id")
        rows = cur.fetchall()
        for row in rows:
            com.d2u.data_used.append(row['value'])
    except psycopg2.DatabaseError as e:
        log.E('<ev.load_texts_used> DatabaseError %s' % e)
    else:
        log.I('+ data_used loaded successfully')
    finally:
        if conn:
            conn.close()


def save_texts_used():
    log.D('+ save data_used to DB')
    conn = None
    rows = [(i,val) for i, val in enumerate(com.d2u.data_used)]
    try:
        conn = psycopg2.connect(C.DATABASE_URL, sslmode='require')
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("TRUNCATE TABLE data_used RESTART IDENTITY")
        query = "INSERT INTO data_used (id, value) VALUES (%s, %s)"
        cur.executemany(query, rows)
        conn.commit()
    except psycopg2.DatabaseError as e:
        log.E('<ev.save_texts_used> DatabaseError %s' % e)
    else:
        log.D('+ data_used saved successfully')
    finally:
        if conn:
            conn.close()


def save_mem():
    log.D('+ save memory to DB')
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
        log.E('<ev.save_mem>  DatabaseError %s' % e)
        # sys.exit(1)
    else:
        log.D('+ memory saved successfully')
    finally:
        if conn:
            conn.close()


async def load():
    t1 = os__getmtime('data_to_process.py')
    t2 = os__getmtime('data_to_use.py')
    if t1 > t2:
        log.W(f'Date of "data_to_process.py" is {other.sec2ts(t1, "%d/%m/%y %H:%M:%S", check_utc=False)}, '
              f'when "data_to_use.py" from {other.sec2ts(t2, "%d/%m/%y %H:%M:%S", check_utc=False)} '
              f'=> try to recreate "data_to_use".')
        com.make_d2u()
    load_texts_used()
    load_mem()
    await people.get() # check=(not C.is_test)
    _check_day_ev()


def save():
    save_mem()
    people.upd()
    save_texts_used()


def stop_quarter_h_timer():
    global timer_quarter_h_handle
    if timer_quarter_h_handle:
        timer_quarter_h_handle.cancel()


def start_quarter_h_timer():
    global timer_quarter_h_handle
    t = 900
    stop_quarter_h_timer()
    timer_quarter_h_handle = other.later(t, timer_quarter_h)
    log.I('* Start new timer in {0} seconds.'.format(t))


def timer_quarter_h():
    global timer_quarter_works
    start_quarter_h_timer()
    try:
        log.D('+ Quarter hour timer event!')
        save()
        _timer_check_games()
        timer_quarter_works += 1
        log.D('+ Timer event finished!')
        mn = 4 if timer_quarter_works % TMR_IN_H == 0 else 1
        log.p('------------------------------------- ' * mn)
    except Exception as e:
        other.pr_error(e, 'timer_quarter_h')


def _timer_check_games():
    for usr in user_games:
        user_games[usr]['h'] += 1
        g_name = user_games[usr]['name'].lower()
        if (usr not in ram.ignore_users and user_games[usr]['h'] % TMR_IN_H == 0
                and all(word in g_name for word in VTMB)):
            phr = com.get_t('vtmb', user=f'<@{usr}>')
            com.write_msg(C.main_ch, phr)


def stop_half_min_timer():
    global timer_half_min_handle
    if timer_half_min_handle:
        timer_half_min_handle.cancel()


def start_half_min_timer():
    global timer_half_min_handle
    t = 30
    stop_half_min_timer()
    timer_half_min_handle = other.later(t, timer_half_min)


def timer_half_min():
    global day_ev_check
    start_half_min_timer()
    try:
        now = other.get_now()
        sec_total = int(now.timestamp())
        if now.hour == 0 and now.minute == 0 and day_ev_check != now.day:
            log.I('[=== New day! ===]')
            _check_day_ev(now, on_midnight=True)
        for uid, user in ram.silence_users.items():
            if sec_total > user['time']:
                other.later_coro(1, manager.silence_end(uid))
                other.later(15, timer_quarter_h)
    except Exception as e:
        other.pr_error(e, 'timer_half_min')


def start_timers():
    start_quarter_h_timer()
    start_half_min_timer()


def stop_timers():
    stop_quarter_h_timer()
    stop_half_min_timer()


def force_exit():
    sys.exit(0)


def on_exit(signum):
    log.I(f'Call on_exit by signal {signum}')
    C.loop.create_task(C.client.logout())
    stop_timers()
    C.was_Ready = C.Ready
    C.Ready = False


def on_final_exit():
    log.I('\n', 'People online data:')
    log.p('\n'.join(people.print_online_people()))
    ram.t_finish = other.t2utc()
    ram.t_work = (ram.t_finish - ram.t_start)
    if C.was_Ready:
        save()
    log.I('Finally exit at ', ram.t_finish.strftime('[%D %T]'),
          ', working for ', other.delta2s(ram.t_work))
    log.p('====== ' * 10)


def on_user_life_signs(uid):
    people.life_signs(uid)


async def cmd_people_time_sync():
    await people.time_sync()
    log.jD('- people.time_sync done, save mem')
    save_mem()


def _check_day_ev(now=None, on_midnight=False):
    global day_ev_check
    if not now:
        now = other.get_now()

    if on_midnight:
        for ev in data.day_events:
            if ev in C.events_name:
                log.jI(f'<Day event> {C.events_name[ev]} finished.')
            elif ev in C.usernames:
                log.jI(f'<Day event> {C.usernames[ev]} birthday finished.')

    data.day_events = set()
    ev = data.data_events.get(now.month, {}).get(now.day, ())
    if isinstance(ev, str) or isinstance(ev, int):
        ev = (ev,)
    data.day_events.update(ev)

    for ev in data.day_events:
        if ev in C.events_name:
            log.jI(f'<Day event> Today is {C.events_name[ev]}!')
        elif ev in C.usernames:
            log.jI(f'<Day event> Today is {C.usernames[ev]} birthday!')
            com.write_msg(C.users['Kuro'], f'<Day event> Today is <@{ev}> birthday!')

    day_ev_check = now.day
