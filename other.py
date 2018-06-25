import re
#import time
import constants as C
import datetime
import discord
import random
import data

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
            ans.append(pre + '[' + key + '] = ' + ch_dict[key])
    return '\n'.join(ans) if ans else []


def mess_plus(message):
    if message.attachments:
        attachments = []
        for att in message.attachments:
            attachments.append('\t\t' + att['url'])
        print('\n'.join(attachments))
    if message.embeds:
        embeds = []
        i = 1
        for emb in message.embeds:
            embed = ['\tEmb_' + str(i) + ':']
            embed += [str_keys(emb, ['title', 'url', 'description'], '\t\t')]
            if 'author' in emb:
                embed += ['\t\t[author]:']
                embed += [str_keys(emb['author'], ['name', 'icon_url'], '\t\t\t')]

            if 'fields' in emb:
                j = 1
                for field in emb['fields']:
                    embed += ['\t\t[field_' + str(j) + ']:']
                    embed += [str_keys(field, ['name', 'value'], '\t\t\t')]
                    j += 1

            if 'footer' in emb:
                embed += ['\t\t[footer]:']
                embed += [str_keys(emb['footer'], ['icon_url', 'text'], '\t\t\t')]

            i += 1
            embeds.append('\n'.join(embed))

        print('\n'.join(embeds))


def t2s(timedata=None, frm="%H:%M:%S"):
    timedata = timedata or datetime.datetime.utcnow()
    timedata = timedata.replace(tzinfo=timedata.tzinfo or datetime.timezone.utc)
    return timedata.astimezone(datetime.timezone(datetime.timedelta(hours=3))).strftime(frm)


async def get_ban_user(s_name):
    user_bans = await C.client.get_bans(C.server)
    user_bans.reverse()
    names = {s_name, s_name.translate(C.punct2space).replace(' ', ''), s_name.strip(' '), s_name.replace('@', '')}
    for b_u in user_bans:
        for n in names:
            if b_u.id == n or b_u.name == n or b_u.mention == n or b_u.display_name == n or str(b_u) == n:
                return b_u
    return None


# noinspection PyArgumentList
def get_user(i):  # i must be id, server nickname, true nickname or full nickname (SomeName#1234)
    """
    :param i:
    :return C.discord.Member:
    """
    p_name1 = i.translate(C.punct2space).replace(' ', '')
    return (C.server.get_member(i) or C.server.get_member(p_name1) or
            C.server.get_member_named(i.strip(' ')) or C.server.get_member_named(i) or
            C.server.get_member_named(i.replace('@', '')) or
            C.server.get_member_named(p_name1))


def get_users(names):
    """
    :param iterator names:
    :rtype: set
    """
    res = set()
    for name in names:
        usr = get_user(name)
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


async def test_status(test):
    if test:
        game = discord.Game(name='«Тестирование идёт...»')
        await C.client.change_presence(game=game, status=discord.Status.dnd, afk=False)
    else:
        await C.client.change_presence(game=None, status=discord.Status.online, afk=False)


async def busy():
    await C.client.change_presence(game=None, status=discord.Status.idle, afk=True)


# async def Ready():
#     while not C.Ready:
#         time.sleep(1)
#     return

def ch_list(id_list):
    text = []
    for uid in id_list:
        ch = C.client.get_channel(uid) or get_user(uid)
        if ch:
            text.append(ch.mention)
    return text


async def do_embrace(user, clan=None):
    if user:
        if not clan:
            for r in user.roles:
                if r.id in C.clan_ids:
                    clan = C.role_by_id[r.id]
                    break
        clan = clan or random.choice(list(C.clan_names))
        roles = [find(C.server.roles, id=C.roles[clan])]
        pander = False
        if clan in C.sabbat_clans:
            roles.append(find(C.server.roles, id=C.roles['Sabbat']))
            pander = (clan == 'Noble Pander')
        try:
            await C.client.add_roles(user, *roles)
        except C.discord.Forbidden:
            print("Bot can't change roles.")
        except Exception as e:
            print('Error in changing roles: ', e)
            #print("Other error in changing roles")
        # omg
        clan_users = set()
        if not pander:
            for mem in C.client.get_all_members():
                if find(mem.roles, id=C.roles[clan]) and mem.id != user.id:
                    clan_users.add(mem.id)
            clan_users.difference_update(C.not_sir)
            sir = random.choice(list(clan_users))
            text = random.choice(data.embrace_msg).format(sir='<@' + sir + '>', child='<@' + user.id + '>')
        else:
            text = random.choice(data.embrace_pander).format(child='<@' + user.id + '>')

        if clan in C.sabbat_clans and not pander:
            text += "\n" + random.choice(data.embrace_sabbat)

        return text

    else:
        return False  #await msg.qanswer("Не могу найти такого пользователя.")


async def do_embrace_and_say(msg, name, clan=None):
    user = get_user(name)
    roles = {role.id for role in user.roles[1:]}
    if not roles.intersection(C.clan_ids):
        text = await do_embrace(user, clan=clan)
        await msg.say(C.main_ch, text)


def issuper(usr):
    """

    :param discord.Member usr:
    :return:
    """
    if (usr.id in C.superusers or usr.id == C.users['bot'] or
            find(usr.roles, id=C.roles['Sheriff']) or find(usr.roles, id=C.roles['Scourge'])):
        return True


async def pr_say(text):
    print(text)
    if not C.Server_Test:
        await C.client.send_message(get_user(C.users['Kuro']), content=text)


def name_pat():
    patterns = ['{ph}, <@{id}>.', '<@{id}>, {ph}.']
    return random.choice(patterns)


def name_phr(uid, phr):
    return name_pat().format(id=uid, ph=phr).capitalize()


def name_rand_phr(uid, arr):
    return name_phr(uid, random.choice(arr))


def later(t, coro):
    """

    :param t: int
    :param coro: coroutine object
    """
    C.loop.call_later(t, lambda: C.loop.create_task(coro))
