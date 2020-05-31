import aiohttp
import re
import sys
import random
import copy
from io import BytesIO as io_BytesIO
from ast import literal_eval as ast__literal_eval
from discord.utils import get as find

import constants as C
import log
import manager
import local_memory as ram

# for weather

#import local_memory as ram


def comfortable_help(docs):
    help = {}
    text = []
    lens = set()
    for doc in docs:
        if not doc:
            continue

        key = re.search('!?[a-zA-Z_]+?[: ]', doc)
        if key:
            key = key.group(0)[0:-1]
            if key.startswith('!'):
                key = '¡' + key
            help[key] = {}
            for cmd in doc.split('\n'):  # type: str
                s = cmd.find('!')
                s = s if s > -1 else 0
                i = cmd.find(':')
                if i > 0:
                    help[key][cmd[s:i]] = cmd[i + 1:]
                    lens.add(len(cmd[s:i]))
        else:
            text.append(doc)

    if not lens:
        return False

    key_len = max(lens) + 1
    keys = sorted(help.keys())
    for k in keys:
        cmds = sorted(help[k].keys(), key=len)
        for cmd in cmds:
            t_cmd = cmd
            text.append((t_cmd + ':').ljust(key_len, ' ') + help[k][cmd])
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
    td = timedata or C.Types.Datetime.utcnow()
    td = td.replace(tzinfo=td.tzinfo or C.Types.Timezone.utc)
    td = td.astimezone(C.Types.Timezone(C.Types.Timedelta(hours=3)))
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


def s2s(total_sec):
    sec_in = {'years': 31557600, 'd': 86400, 'h': 3600, 'min': 60, 'sec': 1}
    t = {}
    s = []
    for k, v in sec_in.items():
        t[k] = int(total_sec / v)
        if s or t[k] > 0:
            total_sec -= t[k] * v
            s.append(f'{t[k]} {k}')
    return ', '.join(s) if s else 'flash'


def sec2ts(total_sec, frm="%H:%M:%S", check_utc=True):
    if total_sec == 0:
        return '0'
    timedata = C.Types.Datetime.fromtimestamp(int(total_sec))
    return (t2utc(timedata) if check_utc else timedata).strftime(frm)


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
    :rtype: C.Types.Member
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
    :rtype: set(C.Types.Member)
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


def get_channels(names, return_channels=False):
    """
    :param iterator names:
    :param bool return_channels:
    :rtype: set
    """
    res = set()
    for name in names:
        ch = get_channel(name)
        if ch:
            if return_channels:
                res.add(ch)
            else:
                res.add(ch.id)

    return res


def find_channels_or_users(names, return_objects=False):
    """
       :param iterator names:
       :param bool return_objects:
       :rtype: set
       """
    res = set()
    for name in names:
        s = get_channel(name) or find_user(name)
        if s:
            if return_objects:
                res.add(s)
            else:
                res.add(s.id)

    return res


async def get_channel_or_user(name):
    """
       :param str name:
       :rtype: C.Types.Channel
       """
    s = get_channel(name)
    if not s:
        user = find_user(name)
        if user:
            try:
                mess = await C.client.send_message(user, '.')
                s = mess.channel
                await delete_msg(mess)
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
                    await delete_msg(mess)
                except Exception as e:
                    pr_error(e, 'get_channels_or_users', 'send_message error')
                    continue

        if s:
            res.add(s)

    return res


async def test_status(state):
    game = None
    status = C.Types.Status.online
    if isinstance(state, str):
        game = C.Types.Game(name=state)
    elif state:
        game = C.Types.Game(name='«Тестирование идёт...»')
        status = C.Types.Status.do_not_disturb
    # else:
    #     await C.client.change_presence(game=None, status=C.Types.Status.online, afk=False)
    await C.client.change_presence(game=game, status=status, afk=False)


async def set_game(name=''):
    game = C.Types.Game(name=name) if name else None
    ram.game = name or False
    status = C.prm_server.me.status
    await C.client.change_presence(game=game, status=status, afk=False)


async def busy():
    await C.client.change_presence(game=None, status=C.Types.Status.idle, afk=True)


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


def is_admin(usr):
    """

    :param C.Types.Member usr:
    :return:
    """
    if (usr.id in C.superusers or usr.id in {C.users['bot'], C.users['Natali']} or
            find(usr.roles, id=C.roles['Sheriff']) or find(usr.roles, id=C.roles['Scourge'])):
        return True


def name_phr(uid, phr, name='', punct=True):
    if not(isinstance(phr, str) or isinstance(phr, C.Types.Emoji)):
        phr = choice(phr)
    name = f'({name})' if name else ''
    pun = (',', '.') if punct else ('', '')
    pattern = choice('{ph}{pun[0]} <@{id}>{name}{pun[1]}', '<@{id}>{name}{pun[0]} {ph}{pun[1]}')
    return pattern.format(id=uid, ph=phr, pun=pun, name='{name}').capitalize().format(name=name)


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
    log.E("{{{cat}}} {text}: {e}\n\t!!! {ei[0]} {ei[1]}".format(cat=cat, text=text, e=e, ei=ei))


def is_float(num):
    try:
        float(num)
    except ValueError:
        return False
    return True


def is_int(num):
    try:
        int(num)
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
    for ch in server.channels:  # type: C.Types.Channel
        if str(ch.type) == 'text':
            t[ch.position] = ch

    channels = [t[k] for k in sorted(t)]
    return channels[0]


def rand_flip(len_wave=0):
    eye = choice('°', '•', '◕', '⊙', '◉', '❍', '◔', '~', '・', '￣', 'ᵔ', '^', '-', '❛', 'ಠ', '≖', '👁', )
    mouth = choice('□', '◡', 'o', '‿', r'\_', '︿', '∀', '▽', '。', 'ᴥ', ':nose::skin-tone-1:', 'ヮ', 'ᗩ', )
    hand = choice('╯', '/', 'ﾉ', '/¯', '༼ ', 'つ', 'ง', 'ᕤ ', '┘')
    if len_wave > 1:
        wave = '︵' * len_wave
    else:
        wave = choice('彡', *('︵' * rand(1, 10),) * 4)
    return '({2}{0}{1}{0}){2}{3}'.format(eye, mouth, hand, wave)


def rand_tableflip(len_wave=0, len_table=0):
    # (╯°□°）╯︵ ┻━┻
    table = f'┻{"━" * (len_table if len_table > 1 else rand(1,10))}┻'
    return '{0} {1}'.format(rand_flip(len_wave), table)


def check_fliproll(txt):
    hands = {hand for hand in ('shchupalko', '╯', '/', 'ﾉ', '/¯', '༼ ', 'つ', 'ง', 'ᕤ ', '┘',) if hand in txt}
    return bool(hands)


def rand_diceflip(count=1):
    dices = '`' + '` `'.join(manager.get_dice(count, simple=True, short=True)) + '`'
    return '{0} {1}'.format(rand_flip(), dices)


async def get_url_files(url_i):
    """
    :rtype: asynciterable(file, name, url)
    :type url_i: iterator
    """
    async with aiohttp.ClientSession() as session:
        for url in url_i:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        yield io_BytesIO(await resp.read()), url.rpartition('/')[-1], url
            except Exception as e:
                pr_error(e, 'other.get_url_files', 'error with url: ' + url)
                continue


async def type2sent(ch, text=None, emb=None, extra=0):
    if text is None:
        await C.client.send_message(ch, content=text, embed=emb)
        return 0

    t = min(1500, len(text)) / 20 + extra
    await C.client.send_typing(ch)
    for i in range(1, int(t / 10) + 1):
        later_coro(i * 10, C.client.send_typing(ch))
    later_coro(t, C.client.send_message(ch, content=text, embed=emb))
    return t


def split_text(text, pre_split=''):
    if not text:
        return []

    MAX_LEN = 2000

    tst_text = pre_split.join(text) if not isinstance(text, str) else text
    if (tst_text.count('*') + tst_text.count('_') + tst_text.count('`')) > len(tst_text)/2:
        MAX_LEN = MAX_LEN/2

    if not isinstance(text, str):
        if pre_split:
            if len(text[0]) >= MAX_LEN:
                yield from split_text(text[0])
                yield from split_text(text[1:], pre_split)
            elif sum((len(t)+len(pre_split) for t in text)) <= MAX_LEN:
                yield pre_split.join(text)
            else:
                new_text = [text[0]]
                ln_spl = len(pre_split)
                new_len = len(text[0]) + ln_spl
                i = 1
                for i, t in enumerate(text[1:], 1):
                    if (new_len + len(t) + ln_spl) >= MAX_LEN:
                        break
                    else:
                        new_text.append(t)
                        new_len += len(t) + ln_spl

                yield pre_split.join(new_text) + (pre_split[0] if len(pre_split) > 1 else '')
                yield from split_text(text[i:], pre_split)
        else:
            for t in text:
                yield from split_text(t)
    elif len(text) < MAX_LEN:
        yield text
    else:
        spls = ('\n', '. ', '.', ' ')
        for spl in spls:
            if spl in text:
                yield from split_text(text.split(spl), spl)
                break
        else:
            for i in range(0, len(text), MAX_LEN):
                yield text[i:i + MAX_LEN]


def obj2int(obj):
    if not obj:
        return 0
    else:
        return int(obj)


def try_sum(s:str):
    if not s:
        return 0

    s = s.replace(',', '.')
    # noinspection PyBroadException
    try:
        res = ast__literal_eval(s)
    except Exception:
        return 0
    else:
        return res


def _prepare_list_args(args):
    if len(args) == 1 and hasattr(args[0], '__len__') and not isinstance(args[0], str):
        ls = tuple(args[0])
    else:
        ls = tuple(args)
    return ls


def choice(*args):
    """Alias for random.choice"""
    ls = _prepare_list_args(args)
    return random.choice(ls)


def shuffle(*args):
    """Alias for random.shuffle"""
    ls = list(_prepare_list_args(args))
    random.shuffle(ls)
    return  ls


def rand(a:int=None, b:int=None):
    """Alias for random.random() and random.randint(a, b)"""
    if a is None or b is None:
        return random.random()
    else:
        return random.randint(a, b)


def uname(memb:C.Types.Member):
    return str(memb) + ('(' + memb.display_name + ')' if memb.name != memb.display_name else '')


def deepcopy(o):
    return copy.deepcopy(o)


def s_in_s(s_child, s_parent, all_=False):
    if not(s_child or s_parent):
        return False
    for s in s_child:
        if s in s_parent:
            if not all_:
                return s
        else:
            if all_:
                return False
    return all_


async def delete_msg(message, reason='-'):
    """

    :param C.Types.Message message:
    :param reason: string
    """
    log.I(f"Bot will try delete message in #{message.channel.name}. Reason: {reason}.")
    try:
        await C.client.delete_message(message)
    except C.Exceptions.Forbidden:
        log.jW("Bot haven't permissions to delete messages here.")
    except C.Exceptions.NotFound:
        log.jW("Can't find the message to delete.")
    except Exception as e:
        pr_error(e, 'delete_msg', 'Unexpected error')


def get_roles(role_names_or_ids, server_roles=None):
    server_roles = server_roles or C.prm_server.roles
    new_roles = []
    for i in role_names_or_ids:
        role = find(server_roles, id=i)
        if not role:
            role = find(server_roles, name=i)
        if role:
            new_roles.append(role)
    return new_roles


def has_roles(member, role_ids, has_all=False):
    """
    :type member: C.Types.Member
    :param role_ids: str|list
    :param has_all: boolean
    """

    if not role_ids:
        return True

    if not isinstance(role_ids, list):
        role_ids = [role_ids]

    count = 0
    for r in member.roles: # type: C.Types.Role
        if r.id in role_ids:
            if not has_all:
                return True
            count += 1

    return count == len(role_ids)


def change_roles(callback, member, roles, error_msg='add_roles', delay=0, by_id=False, server_roles=None):

    if not roles:
        return

    if isinstance(roles, set):
        roles = list(roles)
    elif not isinstance(roles, list):
        roles = [roles]

    if by_id:
        roles = get_roles(roles, server_roles)
    log.D('Try {t} to @{m.display_name} roles ({r}).'.format(
        m=member, t=callback.__name__, r=', '.join([r.name for r in roles])))
    later_coro(delay, callback(member, roles, error_msg))


def add_roles(member, roles, error_msg='rem_roles', delay=0, by_id=False, server_roles=None):
    change_roles(_add_roles_coro, member, roles, error_msg, delay, by_id, server_roles)


def rem_roles(member, roles, error_msg='rem_roles', delay=0, by_id=False, server_roles=None):
    change_roles(_rem_roles_coro, member, roles, error_msg, delay, by_id, server_roles)


async def _add_roles_coro(member, roles, error_msg='add_roles'):
        try:
            await C.client.add_roles(member, *roles)
        except C.Exceptions.Forbidden:
            log.jW("[{}] Bot can't change roles.".format(error_msg))
        except Exception as e:
            pr_error(e, error_msg, 'Error in changing roles')


async def _rem_roles_coro(member, roles, error_msg='rem_roles'):
        try:
            await C.client.remove_roles(member, *roles)
        except C.Exceptions.Forbidden:
            log.jW("[{}] Bot can't change roles.".format(error_msg))
        except Exception as e:
            pr_error(e, error_msg, 'Error in changing roles')


def user_list(users_id):
    return '<@' + '>, <@'.join(users_id) + '>'


def channel_list(channels_id):
    return '<#' + '>, <#'.join(channels_id) + '>'


def it2list(item):
    if item:
        if hasattr(item, '__len__') and not isinstance(item, str):
            item = list(item)
        else:
            item = [item]
    else:
        item = []

    return item
