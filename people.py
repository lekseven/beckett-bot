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


class Usr:
    def __init__(self, uid, name='', karma=0, status='', g_morn=0, g_day=0, g_ev=0, g_n=0):
        self.id = uid
        self.name = name
        self.karma = karma
        self.status = status
        self.g_morn = int(g_morn)
        self.g_day = int(g_day)
        self.g_ev = int(g_ev)
        self.g_n = int(g_n)
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
        return Usr(memb.id, name=str(memb), status=status)

    @staticmethod
    def load(row):
        return Usr(str(row['id']), name=row['name'], karma=row['karma'], status='',
            g_morn=row['g_morn'], g_day=row['g_day'], g_ev=row['g_ev'], g_n=row['g_n'])

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
        return [self.id, self.name, self.g_morn, self.g_day, self.g_ev, self.g_n, self.karma]

    def row_upd(self):
        return [self.name, self.g_morn, self.g_day, self.g_ev, self.g_n, self.karma, self.id]

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


class Gn:
    def __init__(self, gid, name='', karma=0, status='', last=None, role='0', ban=None):
        global bans_id
        t = last or dt.datetime.now().timestamp()
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
        m = memb or other.get_user(self.id)
        if m:
            nm = str(m)
            if self.role != '0':
                role = other.find(C.server.roles, id=self.role)
                if role:
                    C.loop.create_task(C.client.add_roles(m, *[role]))
        self.status = 'del'
        usr = Usr(self.id, name=nm, karma=self.karma, status='add')
        if res:
            return usr
        else:
            usrs[self.id] = usr

        #'id': smb.id, 'name': str(smb), 'g_morn': 0, 'g_day': 0, 'g_ev': 0, 'g_n': 0, 'karma': 0, 'status': status,
    def time_out(self):
        return int(dt.datetime.now().timestamp()) - self.last


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
    for mem in C.server.members:
        s_mems.add(mem.id)
        if mem.id not in usrs:
            if Usr.check_new(mem):
                if gone[mem.id].ban:
                    await other.pr_say('New user ' + usrs[mem.id].name + ' from ban!')
                else:
                    await other.pr_say('New user ' + usrs[mem.id].name + ' from gone!')
            else:
                await other.pr_say('New user ' + usrs[mem.id].name + '!')

    for usr in usrs:
        if usr not in s_mems:
            usrs[usr].go()
            await other.pr_say('User ' + usrs[usr].name + ' disappeared! [Ban: ' + str(gone[usr].ban) + ']')

    for u_ban in bans:
        if u_ban.id not in gone:
            if Gn.check_new(u_ban):
                await other.pr_say('New ban user ' + gone[u_ban.id].name + ' from users!')
            else:
                await other.pr_say('New ban user ' + gone[u_ban.id].name + ' from somewhere!')
        else:
            if gone[u_ban.id].toban(True):
                await other.pr_say('New ban user ' + gone[u_ban.id].name + ' from gone!')

    for gn in gone:
        if gn not in bans_id:
            if gone[gn].toban(False):
                await other.pr_say('User ' + gone[gn].name + ' not in ban now!')

    log.I('+ finished check people')


def upd():
    t = load(res=True)

    change_usrs = {'add': [], 'upd': [], 'del': []}
    for uid, usr in usrs.items():
        if usr.status == 'add' or usr.status == 'upd':
            if uid in t['usrs']:
                change_usrs['upd'].append(usr.row_upd())
            else:
                change_usrs['add'].append(usr.row_add())
        elif usr.status == 'del':
            if uid in t['usrs']:
                change_usrs['del'].append([uid])

    change_gone = {'add': [], 'upd': [], 'del': []}
    for uid, gn in gone.items():
        if gn.status == 'add' or gn.status == 'upd':
            if uid in t['gone']:
                change_gone['upd'].append(gn.row_upd())
            else:
                change_gone['add'].append(gn.row_add())
        elif gn.status == 'del':
            if uid in t['gone']:
                change_gone['del'].append([uid])

    conn = None
    log.I('- update people tables')
    try:
        conn = psycopg2.connect(C.DATABASE_URL, sslmode='require')
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if change_usrs['add']:
            query = '''INSERT INTO members (id, name, g_morn, g_day, g_ev, g_n, karma)
                                            VALUES (%s, %s, %s, %s, %s, %s, %s)'''
            cur.executemany(query, change_usrs['add'])
            conn.commit()

        if change_gone['add']:
            query = '''INSERT INTO users_gone (id, name, ban, last, karma, role) 
                                                        VALUES (%s, %s, %s, %s, %s, %s)'''
            cur.executemany(query, change_gone['add'])
            conn.commit()

        if change_usrs['upd']:
            query = '''UPDATE members SET (name, g_morn, g_day, g_ev, g_n, karma) = 
                                                          (%s, %s, %s, %s, %s, %s) WHERE id = %s'''
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
            query = '''INSERT INTO members (id, name, g_morn, g_day, g_ev, g_n, karma)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s)'''
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
    if C.server.get_member(smb.id):
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
    log.I('Sync Start')
    count = 0
    # print('[{0}] TEST'.format(other.t2s()))
    for mem in C.client.get_all_members():
        distribute(mem)

    async for message in C.client.logs_from(C.main_ch, limit=1000000):
        if count % 10000 == 0:
            log.D('<sync> Check message {0}'.format(str(count)))
        count = count + 1
        distribute(message.author, message.timestamp.timestamp())
        # for i in message.raw_mentions:
        #     distribute(await C.client.get_user_info(i), message.timestamp)

    for usr in bans:
        distribute(usr)
    log.D('<sync> MESS COUNT = {0}'.format(str(count)))
    rewrite()
    log.I('Sync End')


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
    bans = await C.client.get_bans(C.server)
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
    else:
        return {'g_morn': 0, 'g_day': 0, 'g_ev': 0, 'g_n': 0}


def set_gt(uid, key):
    keys = {'g_morn', 'g_day', 'g_ev', 'g_n'}
    if uid in usrs and key in keys:
        setattr(usrs[uid], key, int(dt.datetime.now().timestamp()))
        usrs[uid].status = 'upd'
