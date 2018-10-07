import constants as C
import datetime as dt
import psycopg2
import psycopg2.extras
import sys
import other
import discord
import log

usrs = {} # type: dict[id, Usr]
gone = {} # type: dict[id, Gn]
bans = [] # type: list[discord.User]
bans_id = set() # type: set(discord.User.id)
other_usrs = {}


class Usr:
    def __init__(self, uid, name='', karma=0, status='', g_morn=0, g_day=0, g_ev=0, g_n=0, last_m=-1):
        self.id = uid
        self.name = name
        self.karma = karma
        self.status = status
        self.g_morn = int(g_morn)
        self.g_day = int(g_day)
        self.g_ev = int(g_ev)
        self.g_n = int(g_n)
        l_m = int(last_m)
        self.last_m = l_m if l_m>=0 else other.get_sec_total()
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
        return Usr(memb.id, name=str(memb), status=status, last_m=other.get_sec_total())

    @staticmethod
    def load(row):
        return Usr(str(row['id']), name=row['name'], karma=row['karma'], status='',
            g_morn=row['g_morn'], g_day=row['g_day'], g_ev=row['g_ev'], g_n=row['g_n'], last_m=row['last_m'])

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
        return [self.id, self.name, self.g_morn, self.g_day, self.g_ev, self.g_n, self.karma, self.last_m]

    def row_upd(self): # self.id must be in the end of array
        return [self.name, self.g_morn, self.g_day, self.g_ev, self.g_n, self.karma, self.last_m, self.id]

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

    def offline(self):
        return other.get_sec_total() - self.last_m


class Gn:
    def __init__(self, gid, name='', karma=0, status='', last=None, role='0', ban=None):
        global bans_id
        t = last or other.get_sec_total()
        self.id = gid
        self.name = name
        self.karma = karma
        self.status = status
        self.ban = ban if ban is not None else gid in bans_id
        self.last = int(t)
        self.role = role
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
        return Gn(str(row['id']), name=row['name'], karma=row['karma'], status='',
                   last=row['last'], role=str(row['role']), ban=row['ban'])

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
        return [self.id, self.name, self.ban, self.last, self.karma, self.role]

    def row_upd(self):
        return [self.name, self.ban, self.last, self.karma, self.role, self.id]

    def comeback(self, memb=None, res=False):
        global usrs
        nm = self.name
        m = memb or other.find_member(C.vtm_server, self.id)
        if m:
            nm = str(m)
            if self.role != '0':
                role = other.find(C.vtm_server.roles, id=self.role)
                if role:
                    C.loop.create_task(C.client.add_roles(m, *[role]))
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
        log.I('- load people tables')
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
            log.I('+ people tables loaded successfully')
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
    for mem in C.vtm_server.members:
        s_mems.add(mem.id)
        if mem.id not in usrs:
            if Usr.check_new(mem):
                if gone[mem.id].ban:
                    await log.pr_news('New user ' + usrs[mem.id].name + ' from ban!')
                else:
                    await log.pr_news('New user ' + usrs[mem.id].name + ' from gone!')
            else:
                await log.pr_news('New user ' + usrs[mem.id].name + '!')

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
    log.I('- start people tables')
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

    if C.is_test:
        log.I("- it's Test mode, print results and return")
        log_upd = {'change_usrs': change_usrs, 'change_gone': change_gone}
        # log.jD('change_usrs:\n', change_usrs)
        # log.jD('change_gone:\n', change_gone)
        log.jD('subjects were updated:\n',
               '\n'.join([cat + ':\n\t' +
                          '\n'.join([tp + '[{0}]:\n\t\t'.format(len(u_s)) +
                                     ',\n\t\t'.join(str(u) for u in u_s) for tp, u_s in ls.items() if u_s])
                          for cat, ls in log_upd.items() if ls]))
        print('--------------------------------------------------------')
        return

    conn = None
    log.I('- update people tables')
    try:
        conn = psycopg2.connect(C.DATABASE_URL, sslmode='require')
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if change_usrs['add']:
            query = '''INSERT INTO members (id, name, g_morn, g_day, g_ev, g_n, karma, last_m)
                                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
            cur.executemany(query, change_usrs['add'])
            conn.commit()

        if change_gone['add']:
            query = '''INSERT INTO users_gone (id, name, ban, last, karma, role) 
                                                        VALUES (%s, %s, %s, %s, %s, %s)'''
            cur.executemany(query, change_gone['add'])
            conn.commit()

        if change_usrs['upd']:
            query = '''UPDATE members SET (name, g_morn, g_day, g_ev, g_n, karma, last_m) = 
                                                          (%s, %s, %s, %s, %s, %s, %s) WHERE id = %s'''
            cur.executemany(query, change_usrs['upd'])
            conn.commit()

        if change_gone['upd']:
            query = '''UPDATE users_gone SET (name, ban, last, karma, role) = (%s, %s, %s, %s, %s) WHERE id = %s'''
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
        log.I('+ people tables updated successfully')
        log.jD('subjects were updated:\n',
               '\n'.join([cat + ':\n\t' +
                          '\n'.join([tp + '[{0}]:\n\t\t'.format(len(names)) +
                                     ', '.join(names) for tp, names in ls.items() if names])
                          for cat, ls in log_upd.items() if ls]))
        print('--------------------------------------------------------')
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
        conn = psycopg2.connect(C.DATABASE_URL, sslmode='require')
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute("TRUNCATE TABLE members RESTART IDENTITY")
        if usr_rows:
            query = '''INSERT INTO members (id, name, g_morn, g_day, g_ev, g_n, karma, last_m)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
            cur.executemany(query, usr_rows)
        conn.commit()

        cur.execute("TRUNCATE TABLE users_gone RESTART IDENTITY")
        if gn_rows:
            query = '''INSERT INTO users_gone (id, name, ban, last, karma, role) 
                                                    VALUES (%s, %s, %s, %s, %s, %s)'''
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
        if count % 10000 == 0:
            log.D('<sync> Check message {0}'.format(str(count)))
        count = count + 1
        distribute(message.author, other.get_sec_total(message.timestamp))
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
    log.D(' - {0} channels prepare to scan:'.format(len(channels)))
    for i, ch in enumerate(channels):
        pr = ch.permissions_for(ch.server.me)
        if pr.read_message_history:
            mems_i = set(mems)
            async for mess in C.client.logs_from(ch, limit=1000000):
                aid = mess.author.id
                if aid in mems_i:
                    ts = other.get_sec_total(mess.timestamp)
                    if ts > usrs[aid].last_m:
                        usrs[aid].last_m = ts
                        usrs[aid].status = 'upd'
                    mems_i.remove(aid)
                    if len(mems_i) < 1:
                        break
            log.D(' - {0}) {1} - done'.format(i+1, ch.name))
        else:
            log.D(' - {0}) {1} - not permissions for reading'.format(i+1, ch.name))
    log.I('+ Time_sync end')
    log.jD('Test results:')
    for mem in C.vtm_server.members:
        log.jD('{0} \t-\t {1}'.format(mem, other.sec2str(offline(mem.id))))


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
        return {'g_morn': usrs[uid].g_morn, 'g_day': usrs[uid].g_day, 'g_ev': usrs[uid].g_ev, 'g_n': usrs[uid].g_n}
    elif uid in other_usrs:
        return other_usrs[uid]
    else:
        return {'g_morn': 0, 'g_day': 0, 'g_ev': 0, 'g_n': 0}


def set_gt(uid, key):
    keys = {'g_morn', 'g_day', 'g_ev', 'g_n'}
    if key in keys:
        if uid in usrs:
            setattr(usrs[uid], key, other.get_sec_total())
            usrs[uid].status = 'upd'
        else:
            if uid not in other_usrs:
                other_usrs[uid] = {'g_morn': 0, 'g_day': 0, 'g_ev': 0, 'g_n': 0}
            other_usrs[uid][key] = other.get_sec_total()


def offline(uid):
    return uid in usrs and usrs[uid].offline()


def set_last_m(uid):
    if uid in usrs:
        usrs[uid].set(last_m=other.get_sec_total(), status='upd')
