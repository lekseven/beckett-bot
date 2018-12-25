import re
import sys
import constants as C
import datetime
import discord
import random
import log
import aiohttp
from io import BytesIO as io_BytesIO

# for weather

#import local_memory as ram

find = discord.utils.get


# def comfortable_help1(docs):
#     lens = []
#     docs2 = []
#     for doc in docs:
#         if doc:
#             new_doc = doc.split('\n')
#             docs2 += new_doc
#             for doc2 in new_doc:
#                 lens.append(len(re.match('.*?[:]', doc2).group(0)))
#
#     m = max(lens)
#     docs = []
#     for doc in docs2:
#         docs.append(doc.replace(':', ':' + (' ' * (m - lens.pop(0))) + '\t'))
#
#     docs.sort()
#     #print('len(docs)=', len(docs))
#     docs_len = len(docs)
#     count_helps = int(docs_len / 21) + 1  # 20 lines for one message
#     step = int(docs_len / count_helps - 0.001) + 1
#     helps = [docs[i:i + step] for i in range(0, len(docs), step)]
#     texts = []
#     for h in helps:
#         texts.append(('```css\n' + '\n'.join(h) + '```').replace('    !', '!'))
#
#     return texts


def comfortable_help(docs):
    help = {}
    lens = set()
    for doc in docs:
        if doc:
            key = re.search('![a-zA-Z_]*?[: ]', doc).group(0)[1:-1]
            help[key] = {}
            for cmd in doc.split('\n'):  # type: str
                s = cmd.find('!')
                if s > -1:
                    i = cmd.find(':')
                    help[key][cmd[s:i]] = cmd[i + 1:]
                    lens.add(len(cmd[s:i]))
    if not lens:
        return False
    key_len = max(lens) + 1
    keys = sorted(help.keys())
    text = []
    for k in keys:
        cmds = sorted(help[k].keys(), key=len)
        for cmd in cmds:
            text.append((cmd + ':').ljust(key_len, ' ') + help[k][cmd])
            # text.append('**`' + cmd + '`**:' + help[k][cmd])

    text_len = len(text)
    count_helps = int(text_len / 21) + 1  # 20 lines for one message
    step = int(text_len / count_helps - 0.001) + 1
    texts = [text[i:i + step] for i in range(0, text_len, step)]
    helps = []
    for t in texts:
        helps.append(('```css\n' + '\n'.join(t) + '```'))
        # helps.append(('\n'.join(t)))

    return helps


def str_keys(ch_dict, keys, pre=''):
    ans = []
    for key in keys:
        if key in ch_dict:
            ans.append('{0}[{1}] = {2}'.format(pre, key, ch_dict[key]))
    return ['\n'.join(ans)] if ans else []


def t2utc(timedata=None):
    td = timedata or datetime.datetime.utcnow()
    td = td.replace(tzinfo=td.tzinfo or datetime.timezone.utc)
    td = td.astimezone(datetime.timezone(datetime.timedelta(hours=3)))
    return td


def get_now():
    return t2utc()


def get_sec_total(td=None):
    return int(t2utc(td).timestamp())


def t2s(timedata=None, frm="%H:%M:%S"):
    return t2utc(timedata).strftime(frm)


def delta2s(timedelta):
    total_sec = timedelta.total_seconds()
    hours = int(total_sec/3600)
    total_sec -= hours*3600
    mins = int(total_sec / 60)
    total_sec -= mins * 60
    return '{0}:{1}:{2}'.format(hours, mins, int(total_sec))


def sec2str(total_sec):
    s_names = {
        'years': ['лет', 'год', 'года', 'года', 'года'],
        'days': ['дней', 'день', 'дня', 'дня', 'дня'],
        'hours': ['часов', 'час', 'часа', 'часа', 'часа'],
        'mins': ['минут', 'минуту', 'минуты', 'минуты', 'минуты'],
        'sec': ['секунд', 'секунду', 'секунды', 'секунды', 'секунды'],
     }
    sec_in = {'years': 31557600, 'days': 86400, 'hours': 3600, 'mins': 60, 'sec': 1}
    t = {}
    s = []
    for k, v in s_names.items():
        t[k] = int(total_sec / sec_in[k])
        if s or t[k] > 0:
            total_sec -= t[k] * sec_in[k]
            l_numb = int(str(t[k])[-1])
            s.append(str(t[k]) + ' ' + (v[l_numb < 5 and l_numb]))
    return ', '.join(s) if s else 'мгновение'


async def get_ban_user(server, s_name):
    user_bans = await C.client.get_bans(server)
    user_bans.reverse()
    names = {s_name, s_name.translate(C.punct2space).replace(' ', ''), s_name.strip(' '), s_name.replace('@', '')}
    for b_u in user_bans:
        for n in names:
            if b_u.id == n or b_u.name == n or b_u.mention == n or b_u.display_name == n or str(b_u) == n:
                return b_u
    return None


# noinspection PyArgumentList
def find_member(server, i):  # i must be id, server nickname, true nickname or full nickname (SomeName#1234)
    """
    :param server:
    :param i:
    :rtype: discord.Member
    """
    if server:
        p_name1 = i.translate(C.punct2space).replace(' ', '')
        return (server.get_member(i) or server.get_member(p_name1) or
            server.get_member_named(i.strip(' ')) or server.get_member_named(i) or
            server.get_member_named(i.replace('@', '')) or
            server.get_member_named(p_name1))
    else:
        return find_user(i)


def find_members(server, names):
    """
    :param server:
    :param iterator names:
    :rtype: set(discord.Member)
    """
    res = set()
    for name in names:
        usr = find_member(server, name)
        if usr:
            res.add(usr.id)

    return res


def find_user(i):
    m = find_member(C.vtm_server, i)
    if m:
        return m
    ps = {i, i.translate(C.punct2space).replace(' ', ''), i.strip(' '), i.replace('@', '')}
    for m in C.client.get_all_members():
        if ps.intersection({str(m), m.id, m.display_name, m.mention, m.name, m.nick}):
            return m
    return None


def find_users(names):
    """
    :param iterator names:
    :rtype: set
    """
    res = set()
    for name in names:
        usr = find_user(name)
        if usr:
            res.add(usr.id)

    return res


def get_mentions(users):
    """
    :param iterator users:
    :rtype: list
    """
    return ['<@' + uid + '>' for uid in users]


def get_channel(i):
    p_i = C.channels[i] if i in C.channels else i
    return (C.client.get_channel(p_i) or C.client.get_channel(p_i.translate(C.punct2space).replace(' ', '')) or
            find(C.client.get_all_channels(), name=i) or find(C.client.get_all_channels(), name=i.replace('#', '')))


def get_channels(names):
    """
    :param iterator names:
    :rtype: set
    """
    res = set()
    for name in names:
        ch = get_channel(name)
        if ch:
            res.add(ch.id)

    return res


def find_channels_or_users(names):
    """
       :param iterator names:
       :rtype: set
       """
    res = set()
    for name in names:
        s = get_channel(name) or find_user(name)
        if s:
            res.add(s.id)

    return res


async def get_channel_or_user(name):
    """
       :param str name:
       :rtype: Discord.Channel
       """
    s = get_channel(name)
    if not s:
        user = find_user(name)
        if user:
            try:
                mess = await C.client.send_message(user, '.')
                s = mess.channel
                await C.client.delete_message(mess)
            except Exception as e:
                pr_error(e, 'get_channels_or_users', 'send_message error')
    return s or None


async def get_channels_or_users(names):
    """
       :param iterator names:
       :rtype: set
       """
    res = set()
    for name in names:
        s = get_channel(name)
        if not s:
            user = find_user(name)
            if user:
                try:
                    mess = await C.client.send_message(user, '.')
                    s = mess.channel
                    await C.client.delete_message(mess)
                except Exception as e:
                    pr_error(e, 'get_channels_or_users', 'send_message error')
                    continue

        if s:
            res.add(s)

    return res


async def test_status(state):
    game = None
    status = discord.Status.online
    if isinstance(state, str):
        game = discord.Game(name=state)
    elif state:
        game = discord.Game(name='«Тестирование идёт...»')
        status = discord.Status.do_not_disturb
    # else:
    #     await C.client.change_presence(game=None, status=discord.Status.online, afk=False)
    await C.client.change_presence(game=game, status=status, afk=False)


async def busy():
    await C.client.change_presence(game=None, status=discord.Status.idle, afk=True)


# async def Ready():
#     while not C.Ready:
#         time.sleep(1)
#     return

def ch_list(id_list):
    text = []
    for uid in id_list:
        ch = C.client.get_channel(uid) or find_user(uid)
        if ch:
            text.append(ch.mention)
    return text


def issuper(usr):
    """

    :param discord.Member usr:
    :return:
    """
    if (usr.id in C.superusers or usr.id == C.users['bot'] or
            find(usr.roles, id=C.roles['Sheriff']) or find(usr.roles, id=C.roles['Scourge'])):
        return True


def name_pat():
    patterns = ['{ph}, <@{id}>{name}.', '<@{id}>{name}, {ph}.']
    return random.choice(patterns)


def name_phr(uid, phr, name=''):
    name = name and '(' + name + ')'
    return name_pat().format(id=uid, ph=phr, name='{name}').capitalize().format(name=name)


def name_rand_phr(uid, arr, name=''):
    return name_phr(uid, random.choice(arr), name)


def later_coro(t, coro):
    """
    :return: asyncio.TimerHandle
    :param t: int
    :param coro: coroutine object
    """
    return C.loop.call_later(t, lambda: C.loop.create_task(coro))


def later(t, fun):
    """
    :return: asyncio.TimerHandle
    :param t: int
    :param fun: Function
    """
    return C.loop.call_later(t, fun)


def pr_error(e, cat='beckett', text='Error'):
    ei = sys.exc_info()
    log.E("{{{cat}}} {text}:".format(cat=cat, text=text), e, ei[0], ei[1])


def is_float(num):
    try:
        float(num)
    except ValueError:
        return False
    return True


def floor(num):
    i_num = int(num)
    return i_num if i_num == num else i_num + 1


def split_list(ls, by_i):
    """
    Return list from lists, with by_i elements (from ls) in each
    :type ls: list
    :type by_i: int

    :rtype: list
    """
    ln = len(ls)
    return [ls[i * by_i:min((i + 1) * by_i, ln)] for i in range(0, floor(ln / by_i))]


def find_def_ch(server):
    if server.default_channel:
        return server.default_channel
    t = {}
    for ch in server.channels:  # type: discord.Channel
        if str(ch.type) == 'text':
            t[ch.position] = ch

    channels = [t[k] for k in sorted(t)]
    return channels[0]


def rand_tableflip():
    # (╯°□°）╯︵ ┻━┻
    eye = random.choice(('°', '•', '◕', '~', '・', '￣', 'ᵔ', '^', '-', '❛', 'ಠ', '≖'))
    mouth = random.choice(('□', '◡', 'o', '‿', '\_', '︿', '∀', '▽', '。', 'ᴥ',))
    wave = random.choice(('彡', '︵', '︵︵', '︵︵︵', ))
    table = random.choice(('┻━┻', '┻━━┻', '┻━━━┻', '┻━━━━┻', '┻━━━━━┻', '┻━━━━━━┻', '┻━━━━━━━┻', ))
    return '(╯{0}{1}{0}）╯{2} {3}'.format(eye, mouth, wave, table)


async def get_url_files(url_i):
    """
    :rtype: asynciterable(file, name, url)
    :type url_i: iterator
    """
    async with aiohttp.ClientSession() as session:
        for url in url_i:
            async with session.get(url) as resp:
                if resp.status == 200:
                    yield io_BytesIO(await resp.read()), url.rpartition('/')[-1], url
