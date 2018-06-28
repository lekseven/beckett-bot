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


def send_log():
    I('Sending log...')
    drop_path = '/Test_logs/' if C.Server_Test else '/Logs/'
    drop_log_name = 'log[{0}_{1}]({2}).txt'.format(
        ram.t_start.strftime('{%d|%m|%y %T}'), ram.t_finish.strftime('{%d|%m|%y %T}'), other.delta2s(ram.t_work))
    f = open(log_full, 'rb')
    dbx = dropbox.Dropbox(C.DROPBOX_ID)
    dbx.files_upload(f.read(), drop_path + drop_log_name)
    f.close()
    I('Sending log done.')


def p(*args):  #time_print
    print(*args, sep='')


def tp(*args):  #time_print
    print(other.t2s(frm='[%T]'), *args, sep='')


def tpprint(kind, *args):  #type_print
    print('<{0}>'.format(kind), *args, sep='')


def time_tpprint(kind, *args):  #time_type_print
    print('<{0}>[{1}]'.format(kind, other.t2s(frm='%T')), *args, sep='')


def D(*args):
    time_tpprint('D', ' ', *args)


def I(*args):
    time_tpprint('I', ' ', *args)


def W(*args):
    time_tpprint('W', ' ', *args)


def E(*args):
    print('!!!\t<E>[{0}]'.format(other.t2s(frm='%T')), *args)


def jD(*args):
    tpprint('D', ' ', *args)


def jI(*args):
    tpprint('I', ' ', *args)


def jW(*args):
    tpprint('W', ' ', *args)


async def mess_plus(message, save_disc_links=False, save_all_links=False):
    emb_keys = {
        'author': ['name', 'icon_url'],
        'image': ['url'],
        'fields': ['name', 'value'],
        'footer': ['icon_url', 'text'],
    }
    links = []
    if message.attachments:
        attachments = []
        for att in message.attachments:
            attachments.append('\t\t' + att['url'])
            if save_all_links or (save_disc_links and 'discordapp' in att['url']) and att['url'] not in disc_links:
                links.append(att['url'])
        if attachments:
            print('Attachments({0}):'.format(len(attachments)))
            print('\n'.join(attachments))

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
            print(text_embeds)
            if save_all_links:
                links += re.findall('https?://.*\S', text_embeds)
            elif save_disc_links:
                links += re.findall('https?://.*discordapp.*\S', text_embeds)

    if links:
        links = list(set(links).difference(disc_links))
        if links:
            disc_links.update(links)
            text = '[{t}]<{ch}> {author} ({desc})\n{links}'.format(
                t=other.t2s(), ch=str(message.channel.name), author=str(message.author),
                desc='save_all_links' if save_all_links else 'save_disc_links', links='\n'.join(links))
            await C.client.send_message(other.get_channel(C.channels['vtm_links']), content=text)


def format_mess(msg, time=False):
    """
    :type msg: discord.Message
    :param time: bool
    :rtype: str
    """
    ch_name = str(msg.channel.user) if msg.channel.is_private else str(msg.channel.name)
    t = '(from {0})'.format(other.t2s(msg.timestamp)) if time else ''
    cont = msg.content.replace('\n', '\n\t')  # type: str
    if msg.mentions:
        for user in msg.mentions:
            cont = cont.replace(user.mention, str(user))
    if msg.channel_mentions:
        for ch in msg.channel_mentions:
            cont = cont.replace(ch.mention, '#' + str(ch))
    if msg.role_mentions:
        for role in msg.role_mentions:
            cont = cont.replace(role.mention, '@' + str(role))

    return '{t}<{ch}> {author}: {cont}'.format(t=t, ch=ch_name, author=str(msg.author), cont=cont)


async def on_mess(msg, kind):
    """
    :type msg: discord.Message
    :param kind: str
    """
    desc = {'on_message': 'on_msg', 'on_message_edit': 'on_edt', 'on_message_delete': 'on_del'}
    if not C.Ready or (msg.server and msg.server.id != C.server.id) or msg.channel.id in C.ignore_channels:
        return False

    time = (kind != 'on_message')
    save_all_links = (kind == 'on_message_delete')
    save_disc_links = not save_all_links

    time_tpprint('M', '{{{0}}}'.format(desc[kind]), format_mess(msg, time))
    await mess_plus(msg, save_disc_links, save_all_links)
    return True


async def on_reaction(reaction, kind, user):
    msg = reaction.message
    emoji = reaction.emoji
    if not C.Ready or (msg.server and msg.server.id != C.server.id) or msg.channel.id in C.ignore_channels:
        return False

    desc = {'on_reaction_add': 'on_r_add', 'on_reaction_remove': 'on_r_rem'}
    text_emoji = '[{0.name}:{0.id}]'.format(emoji) if hasattr(emoji, 'id') else emoji
    time_tpprint('M', '{{{0}}} {1}: {2}\n\t{3}'.format(desc[kind], str(user), text_emoji, format_mess(msg, True)))
    await mess_plus(msg)
    return True


async def pr_news(text):
    time_tpprint('Ev', ' ', text)
    await C.client.send_message(other.get_channel(C.channels['vtm_news']), content='<Ev> ' + text)
