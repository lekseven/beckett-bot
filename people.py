import constants as C
import psycopg2
import psycopg2.extras
import sys
import other
import discord
import log

gt_keys = {'g_morn', 'g_day', 'g_ev', 'g_n'}

usrs = {} # type: dict[id, Usr]
gone = {} # type: dict[id, Gn]
bans = [] # type: list[discord.User]
bans_id = set() # type: {discord.User.id}
other_usrs = {}
users_online = {} # type: dict[id, list]


class Usr:
    upd_props = ('name', 'karma', 'g_morn', 'g_day', 'g_ev', 'g_n',
             'last_m', 'last_st', 'online', 'prev_st')

    def __init__(self, uid, name='', karma=0, status='', g_morn=0, g_day=0, g_ev=0, g_n=0,
                 last_m=-1, last_st=-1, online=True, prev_st=0):
        self.id = str(uid)
        self.name = name
        self.karma = int(karma)
        self.status = status
        self.g_morn = int(g_morn)
        self.g_day = int(g_day)
        self.g_ev = int(g_ev)
        self.g_n = int(g_n)
        l_m = int(last_m)
        self.last_m = l_m if l_m >= 0 else other.get_sec_total()
        self.online = bool(online)
        l_st = int(last_st)
        self.last_st = l_st if l_st >= 0 else other.get_sec_total() # when changes last user state
        self.prev_st = int(prev_st) # length of prev user state
        # Not save data
        self.maybe_invisible = False
        self.prev_inv = False
        self.prev_onl = not online
        self.was_invisible = False
        self.last_force_check = self.last_st
        self.life_signs_t = other.get_sec_total()
        # usrs[id] = self

    def set(self, **kwargs):
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
        return self

    @staticmethod
    def add(memb, status=''):
        """

        :param discord.Member memb:
        :param str status:
        :return Usr:
        """
        return Usr(memb.id, name=other.uname(memb), status=status, last_m=other.get_sec_total())

    @staticmethod
    def load(row):
        d = {key: row.get(key, '') for key in Usr.upd_props}
        return Usr((row['id']), **d)

    @staticmethod
    def check_new(memb):
        #global usrs, gone
        if memb.id in usrs and usrs[memb.id].status != 'del':
            return True
        if memb.id in gone:
            gone[memb.id].comeback(memb)
            return True
        else:
            usrs[memb.id] = Usr.add(memb, 'add')
            return False

    def row_add(self):
        tp = (getattr(self, key) for key in Usr.upd_props)
        return [self.id, *tp]

    def row_upd(self): # self.id must be in the end of array
        tp = (getattr(self, key) for key in Usr.upd_props)
        return [*tp, self.id]

    def go(self, memb=None, res=False):
        """

        :param discord.Member memb:
        :param  boolean res:
        :return:
        """
        global gone
        role = '0'
        nm = self.name
        if memb:
            if hasattr(memb, 'roles'):
                for r in memb.roles: # type: discord.Role
                    if r.id in C.clan_ids:
                        role = r.id
                        break
            nm = str(memb)

        self.status = 'del'
        gn = Gn(self.id, name=nm, karma=self.karma, status='add', role=role)
        if res:
            return gn
        else:
            gone[self.id] = gn

    def offtime(self):
        return other.get_sec_total() - self.last_m

    def set_invisible(self, inv=True, was_inv=False):
        if self.maybe_invisible == inv:
            self.prev_inv = False
            return

        self.prev_inv = self.maybe_invisible
        self.maybe_invisible = inv
        self.was_invisible = inv or was_inv
        if inv:
            if self.last_force_check > self.last_st:
                self.prev_st = self.last_force_check - self.last_st
                self.last_st = self.last_force_check
            usr_online = users_online.setdefault(self.id, [[f'{{!{other.t2s()}!}}']])
            if not usr_online[-1][-1].startswith('{'):
                usr_online[-1][-1] = f'{{{usr_online[-1][-1]}}}'

    def life_signs(self):
        self.life_signs_t = other.get_sec_total()
        if not(self.online or self.maybe_invisible):
            log.jD(f' ~ think {self.name} in invisible')
            self.set_invisible(True)

    def stable_for(self):
        return other.get_sec_total() - self.last_st

    def is_stable_for(self, h:[float, int]=1):
        return self.stable_for() > (h * 3600 - 1)

    def was_stable_for(self, h: [float, int]=1):
        return self.prev_st > (h * 3600 - 1)

    def was_writing(self, h: [float, int]=1):
        return self.offtime() < (h * 3600)

    def gt_was_for(self, key, h:[float, int]=1):
        if key not in {'g_morn', 'g_day', 'g_ev', 'g_n'}:
            return False

        t = other.get_sec_total() - getattr(self, key)
        return t < (h * 3600)

    def gt_passed_for(self, key, h:[float, int]=1):
        if key not in {'g_morn', 'g_day', 'g_ev', 'g_n'}:
            return False

        t = other.get_sec_total() - getattr(self, key)
        return t > (h * 3600 - 1)


class Gn:
    upd_props = ('name', 'karma', 'last', 'role', 'ban')

    def __init__(self, gid, name='', karma=0, status='', last=None, role='0', ban=None):
        global bans_id
        t = last or other.get_sec_total()
        self.id = gid
        self.name = name
        self.karma = int(karma)
        self.status = status
        self.ban = ban if ban is not None else gid in bans_id
        self.last = int(t)
        self.role = str(role)
        # gone[id] = self

    def set(self, **kwargs):
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
        return self

    @staticmethod
    def add(memb, status=''):
        """

        :param discord.Member memb:
        :param str status:
        :return Gn:
        """
        role = '0'
        if hasattr(memb, 'roles'):
            for r in memb.roles:  # type: discord.Role
                if r.id in C.clan_ids:
                    role = r.id
                    break

        return Gn(memb.id, name=str(memb), status=status, role=role)

    @staticmethod
    def load(row):
        d = {key: row.get(key, '') for key in Gn.upd_props}
        return Gn(str(row['id']), **d)

    @staticmethod
    def check_new(memb):
        #global usrs, gone
        if memb.id in gone and gone[memb.id].status != 'del':
            return True
        if memb.id in usrs:
            usrs[memb.id].go(memb)
            return True
        else:
            gone[memb.id] = Gn.add(memb, 'add')
            return False

    def toban(self, b=True):
        if self.ban != b and self.status != 'del':
            self.ban = b
            self.status = 'upd'
            return True
        return False

    def row_add(self):
        tp = (getattr(self, key) for key in Gn.upd_props)
        return [self.id, *tp]

    def row_upd(self): # self.id must be in the end of array
        tp = (getattr(self, key) for key in Gn.upd_props)
        return [*tp, self.id]

    def comeback(self, memb=None, res=False):
        global usrs
        nm = self.name
        m = memb or other.find_member(C.vtm_server, self.id)
        if m:
            nm = other.uname(m)
            if self.role != '0':
                role = other.find(C.vtm_server.roles, id=self.role)
                if role:
                    other.later_coro(5, C.client.add_roles(m, *[role]))
        self.status = 'del'
        usr = Usr(self.id, name=nm, karma=self.karma, status='add', last_m=other.get_sec_total())
        if res:
            return usr
        else:
            usrs[self.id] = usr

        #'id': smb.id, 'name': str(smb), 'g_morn': 0, 'g_day': 0, 'g_ev': 0, 'g_n': 0, 'karma': 0, 'status': status,
    def time_out(self):
        return other.get_sec_total() - self.last


async def test():
    global usrs, gone
    test1() # get test tables, write to DB
    test2() # change usrs, gone, upd to DB
    usrs = {}
    gone = {}
    load() # get data form DB
    await check_now()  # check data with current situation on server
    test3() # replace usrs with gone
    await check_now() # check replaces data with current situation on server
    upd()
    pass
    pass


def test1():
    #global usrs, gone
    for s in {'111', '222', '333'}:
        usrs[s] = Usr(s, 'name_' + s)

    for s in {'555', '666', '777'}:
        gone[s] = Gn(s, 'name_' + s)

    gone['666'].ban = True
    rewrite()
    # usrs = {1}
    # gone = {2}


def test2():
    usrs['222'].set(name='222_name', g_n=12, status='upd')
    usrs['333'].status = 'del'
    usrs['444'] = Usr('444', 'name_444', karma=44, status='add')

    gone['666'].set(name='666_name', ban=False, status='upd')
    gone['777'].status = 'del'
    gone['888'] = Gn('888', 'name_888', status='add')

    upd()


def test3():
    global usrs, gone

    new_gone = {}
    for usr in usrs:
        new_gone[usr] = usrs[usr].go(res=True).set(last=123)

    new_usrs = {}
    for gn in gone:
        new_usrs[gn] = gone[gn].comeback(res=True).set(g_morn=321)

    usrs = new_usrs
    gone = new_gone
    log.p('===========================================')


def load(res=False):
    usrs_l = {}
    gone_l = {}
    conn = None
    if not res:
        log.D('- load people tables')
    try:
        conn = psycopg2.connect(C.DATABASE_URL, sslmode='require')
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM members")
        rows = cur.fetchall()
        for row in rows: # type: dict
            u = Usr.load(row)
            usrs_l[u.id] = u

        cur.execute("SELECT * FROM users_gone")
        rows = cur.fetchall()
        for row in rows:  # type: dict
            g = Gn.load(row)
            gone_l[g.id] = g

    except psycopg2.DatabaseError as e:
        log.E('DatabaseError %s' % e)
        sys.exit(1)
    else:
        if not res:
            log.D('+ people tables loaded successfully')
    finally:
        if conn:
            conn.close()

    if res:
        return {'usrs': usrs_l, 'gone': gone_l}
    else:
        global usrs, gone
        usrs = usrs_l
        gone = gone_l


async def check_now():
    log.I('- start check people')
    s_mems = set()
    # noinspection PyTypeChecker
    for mem in C.vtm_server.members: # type: discord.Member
        s_mems.add(mem.id)
        uname = other.uname(mem)
        if mem.id not in usrs:
            if Usr.check_new(mem):
                if gone[mem.id].ban:
                    await log.pr_news(f'New user {uname} from ban!')
                else:
                    await log.pr_news(f'New user {uname} from gone!')
            else:
                await log.pr_news(f'New user {uname}!')
        elif usrs[mem.id].name != uname:
            usrs[mem.id].set(name=uname, status='upd')

        online_now = str(mem.status) != 'offline'
        sec_now = other.get_sec_total()
        frm = '[%d.%m.%y]%H:%M:%S' if (sec_now - usrs[mem.id].last_st) >= 86400 else '%H:%M:%S'
        s_now = f'~{other.sec2ts(sec_now, frm=frm)}~'

        if usrs[mem.id].online and online_now:
            users_online[mem.id] = [[other.sec2ts(usrs[mem.id].last_st, frm=frm), s_now]]
        elif online_now:
            users_online[mem.id] = []
        elif usrs[mem.id].online:
            users_online[mem.id] = [[other.sec2ts(usrs[mem.id].last_st, frm=frm)]]
        else:
            users_online[mem.id] = [[f'{{{s_now}}}']]

        online_change(mem.id, status=str(mem.status), st_now=s_now)

    for usr in usrs:
        if usr not in s_mems:
            usrs[usr].go()
            await log.pr_news('User ' + usrs[usr].name + ' disappeared! [Ban: ' + str(gone[usr].ban) + ']')

    for u_ban in bans:
        if u_ban.id not in gone:
            if Gn.check_new(u_ban):
                await log.pr_news('New ban user ' + gone[u_ban.id].name + ' from users!')
            else:
                await log.pr_news('New ban user ' + gone[u_ban.id].name + ' from somewhere!')
        else:
            if gone[u_ban.id].toban(True):
                await log.pr_news('New ban user ' + gone[u_ban.id].name + ' from gone!')

    for gn in gone:
        if gn not in bans_id:
            if gone[gn].toban(False):
                await log.pr_news('User ' + gone[gn].name + ' not in ban now!')

    log.I('+ finished check people')


def upd():
    t = load(res=True)
    log.D('- start upd people tables')
    log_upd = {'change_usrs': {'add': [], 'upd': [], 'del': []}, 'change_gone': {'add': [], 'upd': [], 'del': []}}
    change_usrs = {'add': [], 'upd': [], 'del': []}
    for uid in list(usrs.keys()):
        usr = usrs[uid]
        if usr.status == 'add' or usr.status == 'upd':
            if uid in t['usrs']:
                change_usrs['upd'].append(usr.row_upd())
                log_upd['change_usrs']['upd'].append(usr.name)
            else:
                change_usrs['add'].append(usr.row_add())
                log_upd['change_usrs']['add'].append(usr.name)
            usr.status = ''
        elif usr.status == 'del':
            if uid in t['usrs']:
                change_usrs['del'].append([uid])
                log_upd['change_usrs']['del'].append(usr.name)
            usrs.pop(uid)

    change_gone = {'add': [], 'upd': [], 'del': []}
    for uid in list(gone.keys()):
        gn = gone[uid]
        if gn.status == 'add' or gn.status == 'upd':
            if uid in t['gone']:
                change_gone['upd'].append(gn.row_upd())
                log_upd['change_gone']['upd'].append(gn.name)
            else:
                change_gone['add'].append(gn.row_add())
                log_upd['change_gone']['add'].append(gn.name)
            gn.status = ''
        elif gn.status == 'del':
            if uid in t['gone']:
                change_gone['del'].append([uid])
                log_upd['change_gone']['del'].append(gn.name)
            gone.pop(uid)

    if log.debug():
        if C.is_test:
            log.D("- it's Test mode, print results and return")
        log_upd = {'change_usrs': change_usrs, 'change_gone': change_gone}
        log.jD('subjects were updated:\n',
               '\n'.join([cat + ':\n\t' +
                          '\n'.join([tp + '[{0}]:\n\t\t'.format(len(u_s)) +
                                     ',\n\t\t'.join(str(u) for u in u_s) for tp, u_s in ls.items() if u_s])
                          for cat, ls in log_upd.items() if ls]))
        # log.p('--------------------------------------------------------')
        if C.is_test:
            return

    conn = None
    log.D('- update people tables')
    try:
        ch_usrs_par = ', '.join(Usr.upd_props)
        ch_usrs_par_s = ', '.join(('%s',) * len(Usr.upd_props))
        ch_gone_par = ', '.join(Gn.upd_props)
        ch_gone_par_s = ', '.join(('%s',) * len(Gn.upd_props))
        conn = psycopg2.connect(C.DATABASE_URL, sslmode='require')
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if change_usrs['add']:
            query = f'''INSERT INTO members (id, {ch_usrs_par})
                                            VALUES (%s, {ch_usrs_par_s})'''
            cur.executemany(query, change_usrs['add'])
            conn.commit()

        if change_gone['add']:
            query = f'''INSERT INTO users_gone (id, {ch_gone_par}) 
                                                        VALUES (%s, {ch_gone_par_s})'''
            cur.executemany(query, change_gone['add'])
            conn.commit()

        if change_usrs['upd']:
            query = f'''UPDATE members SET ({ch_usrs_par}) = 
                                                          ({ch_usrs_par_s}) WHERE id = %s'''
            cur.executemany(query, change_usrs['upd'])
            conn.commit()

        if change_gone['upd']:
            query = f'''UPDATE users_gone SET ({ch_gone_par}) = ({ch_gone_par_s}) WHERE id = %s'''
            cur.executemany(query, change_gone['upd'])
            conn.commit()

        if change_usrs['del']:
            query = '''DELETE FROM members WHERE id = %s'''
            cur.executemany(query, change_usrs['del'])
            conn.commit()

        if change_gone['del']:
            query = '''DELETE FROM users_gone WHERE id = %s'''
            cur.executemany(query, change_gone['del'])
            conn.commit()

    except psycopg2.DatabaseError as e:
        log.E('DatabaseError %s' % e)
        sys.exit(1)
    else:
        log.D('+ people tables updated successfully')
        log.jD('subjects were updated:\n',
               '\n'.join([cat + ':\n\t' +
                          '\n'.join([tp + '[{0}]:\n\t\t'.format(len(u_s)) +
                                     ',\n\t\t'.join(str(u) for u in u_s) for tp, u_s in ls.items() if u_s])
                          for cat, ls in log_upd.items() if ls]))
    finally:
        if conn:
            conn.close()


def rewrite():
    usr_rows = []
    gn_rows = []
    for uid, usr in usrs.items():
        usr_rows.append(usr.row_add())
    for uid, gn in gone.items():
        gn_rows.append(gn.row_add())
    conn = None
    try:
        ch_usrs_par = ', '.join(Usr.upd_props)
        ch_usrs_par_s = ', '.join(('%s',) * len(Usr.upd_props))
        ch_gone_par = ', '.join(Gn.upd_props)
        ch_gone_par_s = ', '.join(('%s',) * len(Gn.upd_props))
        conn = psycopg2.connect(C.DATABASE_URL, sslmode='require')
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute("TRUNCATE TABLE members RESTART IDENTITY")
        if usr_rows:
            query = f'''INSERT INTO members (id, {ch_usrs_par})
                                        VALUES (%s, {ch_usrs_par_s})'''
            cur.executemany(query, usr_rows)
        conn.commit()

        cur.execute("TRUNCATE TABLE users_gone RESTART IDENTITY")
        if gn_rows:
            query = f'''INSERT INTO users_gone (id, {ch_gone_par}) 
                                                    VALUES (%s, {ch_gone_par_s})'''
            cur.executemany(query, gn_rows)
        conn.commit()

    except psycopg2.DatabaseError as e:
        log.E('{{rewrite}} DatabaseError %s' % e)
    else:
        log.I('Members rewrite successfully')
    finally:
        if conn:
            conn.close()


def distribute(smb, t=None):
    """

    :param discord.Member or discord.User smb:
    :param dt.datetime.datetime t:
    :return:
    """
    if not smb:
        return False
    # noinspection PyArgumentList
    if C.vtm_server.get_member(smb.id):
        if smb.id in usrs:
            return True
        usrs[smb.id] = Usr(smb.id, str(smb))
        return True
    else:
        if smb.id in gone:
            return False
        gone[smb.id] = Gn(smb.id, str(smb), last=t)
        return False


async def sync():
    # scan chat and get users array from messages in history
    log.I('+ Sync Start')
    count = 0
    # print('[{0}] TEST'.format(other.t2s()))
    for mem in C.client.get_all_members():
        distribute(mem)

    async for message in C.client.logs_from(C.main_ch, limit=1000000):
        distribute(message.author, other.get_sec_total(message.timestamp))
        count += 1
        if count % 10000 == 0:
            log.D('<sync> Check message: ', count)
        # for i in message.raw_mentions:
        #     distribute(await C.client.get_user_info(i), message.timestamp)

    for usr in bans:
        distribute(usr)
    log.D('<sync> MESS COUNT = {0}'.format(str(count)))
    rewrite()
    log.I('+ Sync End')


async def time_sync():
    # scan chat and get users time of last_message from history
    log.I('+ Time_sync start')
    t = {}
    mems = [mem.id for mem in C.vtm_server.members]
    for ch in C.vtm_server.channels:
        if str(ch.type) == 'text':
            t[ch.position] = ch
    channels = [t[k] for k in sorted(t)]
    log.D('- {0} channels prepare to scan:'.format(len(channels)))
    for i, ch in enumerate(channels):
        pr = ch.permissions_for(ch.server.me)
        if pr.read_message_history:
            log.D('+ {0}) {1} - check'.format(i + 1, ch.name))
            mems_i = set(mems)
            count = 0
            messes = []
            async for mess in C.client.logs_from(ch, limit=1000000):
                messes.append(mess)

            for mess in messes:
                aid = mess.author.id
                if aid in mems_i:
                    ts = other.get_sec_total(mess.timestamp)
                    if ts > usrs[aid].last_m:
                        usrs[aid].last_m = ts
                        usrs[aid].status = 'upd'

                    mems_i.remove(aid)
                    if len(mems_i) < 1:
                        break
                count += 1
                if count % 10000 == 0:
                    log.D('- - <time_sync> check messages: ', count, ', mems_i: ', len(mems_i))
            log.D('+ {0}) {1} - done'.format(i+1, ch.name))
        else:
            log.D('-- {0}) {1} - not permissions for reading'.format(i+1, ch.name))
    log.I('+ Time_sync end')
    log.jD('Test results:')
    for mem in C.vtm_server.members:
        log.jD('{0} \t-\t {1}'.format(mem, other.sec2str(offtime(mem.id))))


def clear():
    global usrs, gone
    log.I('CLEAR people tables')
    usrs = {}
    gone = {}
    rewrite()
    log.I('CLEAR done')


async def get_bans():
    log.I('- get bans')
    global bans, bans_id
    bans = await C.client.get_bans(C.vtm_server)
    bans_id = set(ban.id for ban in bans)
    log.I('+ get bans done')


async def get(check=True):
    log.I('Get people data')
    await get_bans()
    load()
    if check:
        await check_now()


async def on_ban(memb):
    bans.append(await C.client.get_user_info(memb.id))
    bans_id.add(memb.id)
    Gn.check_new(memb)


def on_unban(user):
    if user in bans:
        bans.remove(user)
    bans_id.difference_update({user.id})
    if user.id in gone:
        gone[user.id].toban(False)
    else:
        Gn.check_new(user)


def time_out(uid):
    return uid in gone and gone[uid].time_out()


def clan(uid):
    return uid in gone and gone[uid].role != '0' and gone[uid].role


def get_gt(uid):
    if uid in usrs:
        return {key: getattr(usrs[uid], key) for key in gt_keys}
    elif uid in other_usrs:
        return other_usrs[uid]
    else:
        return {key:0 for key in gt_keys}


def set_gt(uid, key):
    if key in gt_keys:
        if uid in usrs:
            setattr(usrs[uid], key, other.get_sec_total())
            usrs[uid].status = 'upd'
        else:
            if uid not in other_usrs:
                other_usrs[uid] = {key:0 for key in gt_keys}
            other_usrs[uid][key] = other.get_sec_total()


def gt_passed_for(uid, key, h:[float, int]=1):
    if uid not in usrs:
        return False
    return usrs[uid].gt_passed_for(key, h)


def offtime(uid):
    return uid in usrs and usrs[uid].offtime()


def set_last_m(uid):
    if uid in usrs:
        usrs[uid].set(last_m=other.get_sec_total(), status='upd')


def online_change(uid, status, force=False, st_now=''):
    if uid not in usrs:
        return False

    usr = usrs[uid]
    online_now = str(status) != 'offline'

    if not(usr.online != online_now or force):
        return True

    usr_online = users_online.setdefault(uid, [['!']])
    t_now = other.get_now()
    sec_now = other.get_sec_total(t_now)
    frm = '[%d.%m.%y]%H:%M:%S' if (sec_now - usr.last_st) >= 86400 else '%H:%M:%S'
    s_now = st_now or f'{other.t2s(t_now, frm)}'

    if force:
        ''' if offline -> offline - it can be go in/out invisible user
            if online -> online - open app with open tab in browser
        '''
        if not online_now:  # offline -> offline
            if usr.maybe_invisible:
                usr_online[-1].append(f'{{{s_now}}}')
            else:
                usr_online.append([f'{{{s_now}}}'])

            if usr.was_invisible:
                usr.set_invisible(not usr.maybe_invisible, True)
            else:
                usr.set_invisible(False, False)
            usr.prev_onl = False

        usr.last_force_check = sec_now

    elif online_now:
        if usr.maybe_invisible:
            usr_online[-1].append(f'{s_now}')
        else:
            usr_online.append([f'{s_now}'])
    else:
        usr_online[-1].append(f'{s_now}')

    if not force:
        usr.prev_onl = usr.online
        usr.set_invisible(False)

    if usr.online != online_now or usr.maybe_invisible != usr.prev_inv:
        usr.prev_st = sec_now - usr.last_st
        usr.last_st = sec_now
        # log.jI(f"{usr.name} is {('offline', 'online')[online_now]} now after {other.s2s(usr.prev_st)}")
        usr.online = online_now
        usr.status = 'upd'
        get_for_now = False
    else:
        get_for_now = force and not online_now

    if uid in {C.users[usr] for usr in ('Dummy', 'Tilia', 'Natali', 'Doriana', 'cycl0ne')}:
        log_f = log.jI if st_now else log.I
        log_f('<on_status_update> ' + get_online_info_now(uid, get_for_now=get_for_now))

    return True


def get_online_info(uid, t_now=None):
    if uid not in usrs or uid not in users_online:
        return ''

    usr = usrs[uid]
    sec_now = t_now if t_now is not None else other.get_sec_total()
    frm = '[%d.%m.%y]%H:%M:%S' if (sec_now - usr.last_st) >= 86400 else '%H:%M:%S'
    s_now = other.sec2ts(sec_now, frm)
    usr_online = other.deepcopy(users_online[uid])
    if usr.online:
        usr_online[-1].append(f'~{s_now}~')
    elif usr.maybe_invisible:
        usr_online[-1].append(f'~{{{s_now}}}~')

    return f'''{usr.name}: {', '.join((f'({" - ".join(ls)})' if len(ls) > 1 else ls[0]) for ls in usr_online)}'''


def print_online_people():
    sec_now = other.get_sec_total()
    info = {}
    for uid in users_online:
        inf = get_online_info(uid, sec_now)
        if not inf:
            continue
        info[usrs[uid].name] = inf

    return [info[key] for key in sorted(info)]


def get_online_info_now(uid, get_for_now=True):
    if uid not in usrs or uid not in users_online:
        return ''

    usr = usrs[uid]
    onl_now = usr.online
    s_prev = other.s2s(usr.prev_st)
    s_onl = ('offline', 'online')
    st_now = 'invisible' if usr.maybe_invisible else s_onl[onl_now]
    st_old = ('invisible' if usr.prev_inv else
              s_onl[usr.prev_onl] if usr.maybe_invisible else s_onl[not onl_now])
    for_now = f' for {other.s2s(usr.stable_for())}' if get_for_now else ''
    return f'{usr.name} is {st_now} now{for_now} (after be {st_old} for {s_prev}).'


def life_signs(uid):
    if uid not in usrs:
        return False

    usrs[uid].life_signs()


def is_online(uid):
    if uid not in usrs:
        return False

    return usrs[uid].online


def is_stable_for(uid, h:[float, int]=1):
    if uid not in usrs:
        return False

    return usrs[uid].is_stable_for(h)


def was_stable_for(uid, h: [float, int]=1):
    if uid not in usrs:
        return False

    return usrs[uid].was_stable_for(h)


def was_writing(uid, h: [float, int]=1):
    if uid not in usrs:
        return False

    return usrs[uid].was_writing(h)


def online_ev(uid):
    if uid not in usrs:
        return False
    usr = usrs[uid]
    if (usr.online and usr.was_stable_for(5) and usr.was_writing(48) and
            any({usr.gt_was_for(key, 48) for key in {'g_morn', 'g_day', 'g_ev'}})):
        corr = 0
        if usr.id == C.users['Tony']:
            corr = -8
        h = other.get_now().hour + corr
        t_day = {'g_morn': (4, 12), 'g_day': (12, 18), 'g_ev': (18, 24)}

        for g_key in t_day:
            t_min, t_max = t_day[g_key]
            if t_min <= h < t_max:
                return g_key if usr.gt_passed_for(g_key, 16) else False
    return False
