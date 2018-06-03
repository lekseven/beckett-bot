import constants as C
import datetime as dt
import psycopg2
import psycopg2.extras

usrs = {}
gone = {}
bans = []


def distribute(smb, t = None):
    if not smb:
        return False
    if smb.id in usrs or smb.id in gone:
        return smb.id in usrs
    if C.server.get_member(smb.id):
        usrs[smb.id] = {
            'name': str(smb),
            'g_morn': 0,
            'g_day': 0,
            'g_ev': 0,
            'g_n': 0,
            'karma': 0,
            'status': '',
        }
        return True
    else:
        last = t or dt.datetime.now()
        gone[smb.id] = {
            'name': str(smb),
            'ban': smb in bans,
            'last': last.timestamp(),
            'karma': 0,
            'status': '',
         }
        return False


async def sync():
    print('Sync Start')
    ch = C.client.get_channel(C.WELCOME_CHANNEL_ID)
    count = 0
    # print('[{0}] TEST'.format(other.t2s()))
    for mem in C.client.get_all_members():
        distribute(mem)

    async for message in C.client.logs_from(ch, limit=1000000):
        if count % 10000 == 0:
            print('<sync> Check message {0}'.format(str(count)))
        count = count + 1
        distribute(message.author, message.timestamp)
        # for i in message.raw_mentions:
        #     distribute(await C.client.get_user_info(i), message.timestamp)

    for usr in bans:
        distribute(usr)
    print('<sync> MESS COUNT = {0}'.format(str(count)))

    mem_rows = []
    usr_rows = []
    for id, mem in usrs.items():
        mem_rows.append([id, *[mem[k] for k in mem if k != 'status']])
    for id, usr in gone.items():
        usr_rows.append([id, *[usr[k] for k in usr if k != 'status']])
    conn = None
    try:
        conn = psycopg2.connect(C.DATABASE_URL, sslmode='require')
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cur.execute("TRUNCATE TABLE members RESTART IDENTITY")
        query = '''INSERT INTO members (id, name, g_morn, g_day, g_ev, g_n, karma)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)'''
        cur.executemany(query, mem_rows)
        conn.commit()

        cur.execute("TRUNCATE TABLE users_gone RESTART IDENTITY")
        query = '''INSERT INTO users_gone (id, name, ban, last, karma) 
                                            VALUES (%s, %s, %s, %s, %s)'''
        cur.executemany(query, usr_rows)
        conn.commit()

    except psycopg2.DatabaseError as e:
        print('[sync] DatabaseError %s' % e)
    else:
        print('Members sync successfully')
    finally:
        if conn:
            conn.close()

    print('Sync End')

    pass
    pass