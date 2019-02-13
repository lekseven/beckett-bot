import sys
import os
import re
from contextlib import redirect_stdout, redirect_stderr
import dropbox
import constants as C
import local_memory as ram
import other
import discord

log_path = 'Logs/'
log_name = ''
log_full = ''
disc_links = set()


class LogWrite:
    def __init__(self, std, logfile):
        self.std = std
        self.logfile = logfile

    def write(self, s):
        self.std.write(s)
        self.logfile.write(s)
        # self.flush()

    def flush(self):
        self.std.flush()
        self.logfile.flush()


class ErrWrite:
    def __init__(self, std, logfile):
        self.std = std
        self.logfile = logfile

    def write(self, s):
        self.std.write(s)
        if len(s) > 2:
            self.logfile.write(other.t2s(frm='![%T]!\t') + s)
        else:
            self.logfile.write(s)
        # self.flush()

    def flush(self):
        self.std.flush()
        self.logfile.flush()


def log_fun(loop):
    global log_full, log_name
    log_name = 'log[{0}].txt'.format(ram.t_start.strftime('%d|%m|%y %T'))
    log_full = log_path + log_name
    directory = os.path.dirname(log_full)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(log_full, 'w') as logfile:
        with redirect_stdout(LogWrite(sys.stdout, logfile)):
            with redirect_stderr(ErrWrite(sys.stderr, logfile)):
                loop()


def read_log(n:1):
    global log_full
    directory = os.path.dirname(log_full)
    if not os.path.exists(directory):
        E('<log.read_log> There is no log file!')
        return []
    with open(log_full, 'r') as logfile:
        return logfile.readlines()[-n:]


def send_log():
    I('Sending log...')
    drop_path = '/Test_logs/' if C.is_test else '/Logs/'
    drop_log_name = 'log[{0}_{1}]({2}).txt'.format(
        ram.t_start.strftime('{%d|%m|%y %T}'), ram.t_finish.strftime('{%d|%m|%y %T}'), other.delta2s(ram.t_work))
    dropbox_send(log_full, drop_log_name, drop_path)
    I('Sending log done.')


def dropbox_send(f_path, f_name, drop_path):
    f = open(f_path, 'rb')
    dbx = dropbox.Dropbox(C.DROPBOX_ID)
    dbx.files_upload(f.read(), drop_path + f_name)
    f.close()


def p(*args, sep=''):  #time_print
    print(*args, sep=sep)


def tp(*args, sep=''):  #time_print
    print(other.t2s(frm='[%T]'), *args, sep=sep)


def tpprint(kind, *args, sep=''):  #type_print
    print('<{0}> '.format(kind), *args, sep=sep)


def time_tpprint(kind, *args, sep=''):  #time_type_print
    print('<{0}>[{1}] '.format(kind, other.t2s(frm='%T')), *args, sep=sep)


def D(*args, sep=''):
    if ram.debug:
        time_tpprint('D', *args, sep=sep)


def I(*args, sep=''):
    time_tpprint('I', *args, sep=sep)


def W(*args, sep=''):
    time_tpprint('W', *args, sep=sep)


def E(*args, sep=''):
    print('!!!\t<E>[{0}]'.format(other.t2s(frm='%T')), *args, sep=sep)


def jD(*args, sep=''):
    # without time
    if ram.debug:
        tpprint('D', *args, sep=sep)


def jI(*args, sep=''):
    # without time
    tpprint('I', *args, sep=sep)


def jW(*args, sep=''):
    # without time
    tpprint('W', *args, sep=sep)


async def mess_plus(message, save_disc_links=False, save_all_links=False, update_links=False, other_channel=None):
    try:
        emb_keys = {
            'author': ['name', 'icon_url'],
            'image': ['url'],
            'fields': ['name', 'value'],
            'footer': ['icon_url', 'text'],
        }
        links = []
        res = []
        if message.attachments:
            attachments = []
            for att in message.attachments:
                url = att['proxy_url'] or att['url']
                attachments.append('\t\t' + url)
                if save_all_links or (save_disc_links and 'discordapp' in url) and url not in disc_links:
                    links.append(url)
            if attachments:
                res.append('Attachments({0}):'.format(len(attachments)))
                res.append('\n'.join(attachments))

        if message.embeds:
            embeds = []
            i = 1
            for emb in message.embeds:
                embed = ['\tEmb_' + str(i) + ':']
                embed += other.str_keys(emb, ['title', 'url', 'description'], '\t\t')

                for key in emb_keys:
                    if key in emb:
                        if isinstance(emb[key], list):
                            j = 1
                            for l in emb[key]:
                                embed += ['\t\t[{0}_{1}]:'.format(key, str(j))]
                                embed += other.str_keys(l, emb_keys[key], '\t\t\t')
                                j += 1
                        else:
                            embed += ['\t\t[{0}]:'.format(key)]
                            embed += other.str_keys(emb[key], emb_keys[key], '\t\t\t')

                i += 1
                if embed:
                    embeds.append('\n'.join(embed))

            if embeds:
                text_embeds = '\n'.join(embeds)
                res.append(text_embeds)
                if save_all_links:
                    links += re.findall(r'https?://.*\S', text_embeds)
                elif save_disc_links:
                    links += re.findall(r'https?://.*discordapp.*\S', text_embeds)

        if links:
            links = list(set(links).difference(disc_links))
            if links:
                disc_links.update(links)
                if not update_links:
                    text = '[{t}]<{ch}> {author} ({desc})'.format(
                        t=other.t2s(message.timestamp, '%d|%m|%y %T'),
                        ch=str(message.channel.name or message.author),
                        author=str(message.author),
                        desc='save_all_links' if save_all_links else 'save_disc_links')
                    ch = (other_channel or
                        (C.vtm_links_ch if (message.server and message.server.id == C.vtm_server.id)
                        else C.other_links_ch))
                    await C.client.send_message(ch, content=text)
                    async for file, name, url in other.get_url_files(links):
                        try:
                            await C.client.send_file(ch, file, filename=name, content='<' + url + '>')
                        except Exception as e:
                            other.pr_error(e, 'log.mess_plus', 'send_file error')
                            try:
                                await C.client.send_message(ch, content=url)
                            except Exception as e:
                                other.pr_error(e, 'log.mess_plus', 'send_just_url error')

        return ['\n'.join(res)] if res else []
    except Exception as e:
        other.pr_error(e, 'log.mess_plus', 'mess_plus[198] error')
        return []


async def format_mess(msg, time=False, date=False, dbase=None):
    """
    :type msg: discord.Message
    :type time: Bool
    :type date: Bool
    :type dbase: dict
    :rtype: str
    """
    try:
        t_m = other.t2s(msg.timestamp)
        t_n = other.t2s()
        s_time = ('(from {0})'.format(t_m) if (time or (t_n[:-1] != t_m[:-1]) or
                                               (int(t_n[-1]) - int(t_m[-1]) > 1)) else '')
        ch_name = ('#@' + str(msg.channel.user)) if msg.channel.is_private else str(msg.channel.name)
        t = ('(from {0})'.format(other.t2s(msg.timestamp, '%d|%m|%y %T')) if date else s_time)
        cont = msg.content or (('≤System≥ ' + msg.system_content) if msg.system_content else '')
        cont = cont.replace('\n', '\n\t')  # type: str
        db = dbase if dbase is not None else {}  # we need a=={} if it is
        if msg.author.id not in db:
            db[msg.author.id] = msg.author
        if msg.raw_mentions:
            for uid in msg.raw_mentions:
                if uid in db:
                    usr = db[uid]
                else:
                    usr = other.find_member(msg.server, uid) or other.find_user(uid)
                    if not usr:
                        usr = await C.client.get_user_info(uid)
                    if usr:
                        db[uid] = usr
                    else:
                        continue
                usr_name = other.uname(usr)
                cont = cont.replace('<@' + usr.id + '>', usr_name).replace('<@!' + usr.id + '>', usr_name)
        if msg.raw_channel_mentions:
            for chid in msg.raw_channel_mentions:
                ch = C.client.get_channel(chid)
                if ch:
                    cont = cont.replace('<#' + ch.id + '>', '#' + str(ch))
        if msg.raw_role_mentions and msg.server:
            for role_id in msg.raw_role_mentions:
                role = other.find(msg.server.roles, id=role_id)
                if not role:
                    for s in C.client.servers:
                        if s.id == msg.server.id:
                            continue
                        role = other.find(s.roles, id=role_id)
                        if role:
                            break
                if role:
                    cont = cont.replace('<@&' + role.id + '>', '&' + str(role))
        a_n = other.uname(msg.author)
        return '{t}<{ch}> {author}: {cont}'.format(t=t, ch=ch_name, author=a_n, cont=cont)
    except Exception as e:
        other.pr_error(e, 'log.format_mess', 'format_mess[253] error')
        return '<format error> ' + (msg.content or (('≤System≥ ' + msg.system_content) if msg.system_content else ''))


async def on_mess(msg, kind):
    """
    :type msg: discord.Message
    :param kind: str
    """
    desc = {'on_message': 'on_msg', 'on_message_edit': 'on_edt', 'on_message_delete': 'on_del'}
    if not C.Ready or msg.channel.id in C.ignore_channels:
        return False

    if msg.channel.id in C.not_log_channels:
        return True

    s_server = ''
    if msg.server:
        if C.is_test and msg.server.id == C.vtm_server.id:
            return False
        if msg.server.id != C.prm_server.id:
            s_server = '<{0}>'.format(msg.server.name)

    time = (kind != 'on_message')
    save_all_links = (kind == 'on_message_delete')
    save_disc_links = not save_all_links
    time_tpprint('M', s_server, '{{{0}}}'.format(desc[kind]), await format_mess(msg, time))
    pl = await mess_plus(msg, save_disc_links, save_all_links)
    if pl:
        print(pl[0])
    return True


async def on_reaction(reaction, kind, user):
    msg = reaction.message
    emoji = reaction.emoji
    if not C.Ready or msg.channel.id in C.ignore_channels:
        return False

    if msg.channel.id in C.not_log_channels:
        return True

    s_server = ''
    if msg.server:
        if C.is_test and msg.server.id == C.vtm_server.id:
            return False
        if msg.server.id != C.prm_server.id:
            s_server = '<{0}>'.format(msg.server.name)

    desc = {'on_reaction_add': 'on_r_add', 'on_reaction_remove': 'on_r_rem'}
    text_emoji = '[{0.name}:{0.id}]'.format(emoji) if hasattr(emoji, 'id') else emoji
    time_tpprint('M', s_server, '{{{0}}} {1}: {2}\n\t{3}'
                 .format(desc[kind], str(user), text_emoji, await format_mess(msg, True)))
    pl = await mess_plus(msg)
    if pl:
        print(pl[0])
    return True


async def pr_news(text):
    time_tpprint('Ev', ' ', text)
    await C.client.send_message(C.vtm_news_ch, content='<Ev> ' + text)


async def pr_other_news(server, text):
    time_tpprint('Ev', '<', server.name, '> ', text)
    await C.client.send_message(C.other_news_ch, content='<Ev from {0}> {1}'.format(server.name, text))


def debug():
    return ram.debug
