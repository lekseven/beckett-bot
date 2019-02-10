# -*- coding: utf8 -*-
import re

import data
import local_memory as ram
import beckett_commands as cmd
import constants as C
import emj
import manager
import other
import communication as com
import log

data_msgs = {}
data_typings = {}


class Msg(manager.Msg):
    def get_commands(self):
        #module_attrs = dir(cmd)
        #cmds = set(key for key in module_attrs if key[0] != '_' and callable(getattr(cmd, key)))
        cmds = cmd.all_cmds.copy()
        if self.channel.id == C.channels['primogens']:
            cmds.intersection_update(cmd.primogenat_cmds)
        elif self.admin and (not self.super or (not self.personal and not self.is_tst)):
            cmds.intersection_update(cmd.admin_cmds)
        elif not self.admin:
            free = cmd.free_cmds
            if {self.author}.intersection({C.users['Creol'], C.users['Tony']}):
                free.add('dominate')
            cmds.intersection_update(free)

        return cmds


async def reaction(message, edit=False):
    msg = Msg(message)

    if msg.author == C.users['bot']:
        if msg.original == data.tremer_joke:
            other.later_coro(20, msg.delete())
        return

    if msg.torpor:
        await msg.delete()
        return

    if C.roles['Silence'] in msg.roles:
        await msg.delete()
        ram.silence_ans[msg.author] = ram.silence_ans.setdefault(msg.author, 0) + 1
        if ram.silence_ans[msg.author] < 4:
            await msg.answer(f'Неугодный <@{msg.author}> пытается нам нечто сказать, но заноза в сердце мешает...')
        return

    # delete messages containing forbidden links
    if not msg.admin:
        if any(link in msg.text for link in data.forbiddenLinks):
            log.I(f'<reaction> forbidden Links')
            await msg.delete()
            await msg.answer(com.get_t('threats', name=msg.author))
            return

    resp = _data_msgs_check(msg)
    if edit and resp and (resp['type'].startswith('cmd_') or resp['type'] == 'gt'):
        return
    else:
        # if we have !cmd -> doing something
        if msg.text.startswith('!'):
            fun = re.match(r'!\w*', msg.text).group(0)[1:]
            if fun in msg.get_commands():
                msg.prepare(fun)
                log.I(f'<reaction> [cmd] {fun}')
                _data_msgs_add(msg, 'cmd_' + fun)
                await getattr(cmd, fun)(msg)
                return

    m_type, text = _do_reaction(msg)

    if edit:
        old_type = resp['type'] if resp else ''
        if old_type == m_type:
            return

        if old_type and not m_type:
            return

        if m_type and old_type and text:
            log.I(f'<reaction> edit [{old_type}] to [{m_type}]')
            typing = _data_tp_check(msg)
            if typing in com.msg_queue.get(msg.channel.id, ()) or old_type == 'no-response':
                com.rem_from_queue(msg.channel.id, typing)
                # and type new mess
            else:
                for mess in resp['ans']:
                    await C.client.edit_message(mess, new_content=text) # if mess>1, all will be with the same text
                resp['type'] = m_type
                return
        # elif m_type and not old_type:

    if m_type and text:
        log.I(('<reaction.edit>' if edit else '<reaction>') + f'[{m_type}]')
        save_obj = _data_msgs_add(msg, m_type)
        if m_type != 'no-response':
            _data_tp_add(msg, com.write_msg(msg.channel, text=text, save_obj=save_obj,
                                            fun=data_tp_del(msg.channel.id, msg.message.id)))
        # await msg.qanswer(text)


async def delete_reaction(message):
    typing = data_typings.setdefault(message.channel.id,{}).get(message.id, '')
    resp = data_msgs.get(message.channel.id, {}).get(message.id, {})
    type_ = resp['type'] if resp else ''
    # if resp and type_ and (not type_.startswith('cmd_') or type_ == 'cmd_help'):
    if resp and type_ and not type_.startswith('cmd_'):
        log.I(f'<delete_reaction> [{type_}]')
        com.rem_from_queue(message.channel.id, typing)
        for mess in resp['ans']:
            await com.delete_msg(mess)
        data_msgs[message.channel.id].pop(message.id)


def _do_reaction(msg:Msg) -> (str, str):

    embrace_or_return = False
    if (ram.mute_channels.intersection({msg.channel.id, 'all'})
            or msg.author in ram.ignore_users or msg.channel.id in C.ignore_channels):
        if msg.channel.id == C.channels['ask']:
            embrace_or_return = True
        else:
            return '', ''

    msg.prepare2()
    beckett_reference = bool(C.beckett_refs.intersection(msg.words))
    beckett_mention = bool(C.beckett_names.intersection(msg.words))
    beckett = beckett_reference or beckett_mention
    other.later_coro(0, emj.on_message(msg.message, beckett))

    found_keys = com.check_phrase(msg.text, msg.words)
    prob = other.rand()

    # embrace
    if msg.channel.id == C.channels['ask'] and not msg.roles.intersection(C.clan_ids):
        clan_keys = list(C.clan_names.intersection(found_keys))
        if clan_keys:
            clan = other.choice(clan_keys)
            other.later_coro(other.rand(30, 90),
                             manager.do_embrace_and_say(msg, msg.author, clan=clan))
            # return 'embrace', clan
    elif embrace_or_return:
        return '', ''

    gt = msg.check_good_time(beckett)
    if gt:
        return 'gt', gt

    if found_keys:
        if not beckett and ram.mute_light_channels.intersection({msg.channel.id, 'all'}):
            return '', ''
        response = False

        if prob < 0.2 or beckett: #beckett_reference or (beckett_mention and (prob < 0.9 or msg.admin)):
            response = True

        if response:
            ans_phr = com.get_text_obj(found_keys)
            if ans_phr['text']:
                return ans_phr['last_key'], ans_phr['text']
    else:
        if '╯' in msg.original or 'shchupalko' in msg.original:
            if '┻' in msg.original:
                if msg.admin:
                    return 'rand_tableflip', other.rand_tableflip()
                elif msg.channel.id == C.channels['bar']:
                    if {msg.author}.intersection({C.users['Buffy'], C.users['Tilia'], }):
                        if prob < 0.2:
                            return 'tableflip_phrase', com.get_t('tableflip_phrase')
                        else:
                            return 'rand_tableflip', other.rand_tableflip()
                else:
                    return 'unflip', '┬─┬ ノ( ゜-゜ノ)'
            else:
                dice_count = msg.original.count('dice') + msg.original.count('🎲')
                if dice_count > 0:
                    return 'diceflip', other.rand_diceflip(dice_count)
        elif msg.original[1:].startswith('tableflip') and (msg.admin or msg.channel.id == C.channels['bar']):
            if not {msg.author}.intersection({C.users['Buffy'], C.users['Tilia'], }) and not msg.admin and prob < 0.2:
                return 'tableflip_phrase', com.get_t('tableflip_cmd_phrase')
            else:
                return '/tableflip', '* *бросаю за <@{id}>* *\n{table}'.format(id=msg.author,
                                                                               table=other.rand_tableflip())
        elif msg.original[1:].startswith('shrug'):
            return '/shrug', r'¯\_(ツ)_/¯'

        if beckett:
            m_type = _beckett_m_type(msg)
            ans = _beckett_ans(m_type, msg.author)
            if ans:
                return m_type, ans

        if beckett_reference or (beckett_mention and other.rand() < 0.25):
            m_type = 'For_Prince' if msg.author == C.users['Natali'] and prob < 0.4 else 'beckett'
            ans_phr = com.get_t(m_type)
            return m_type, ans_phr

    return '', ''


def _beckett_m_type(msg)->str:
    yes = 'да' in msg.words
    no = 'не' in msg.words or 'нет' in msg.words
    if msg.words.intersection({'спасибо', 'благодарю'}):  #'спасибо'
        return 'wlc'
    elif msg.words.intersection(data.sm_resp['hi_plus']):
        return 'hi_plus'
    elif msg.words.intersection(data.sm_resp['fun_smiles']):
        return 'fun_smiles'
    elif msg.words.intersection(data.sm_resp['bye']):
        return 'bye'
    elif msg.words.intersection(data.sm_resp['check_like']) and not no:
        return 'love'
    elif 'любимый клан' in msg.text:
        if other.rand() > 0.09:
            return 'apoliticality'
        else:
            return 'tremer_joke'
    elif msg.words.intersection(data.sm_resp['bot_dog']):
        if msg.admin or other.rand() > 0.2:
            return 'not_funny'
        else:
            return 'bot_dog'
    elif msg.words.intersection({'как'}) and msg.words.intersection({'дела', 'делишки', 'ты', 'чё', 'че'}):
        return 'whatsup'
    # other questions must be before this
    elif msg.text.rstrip(')(.! ').endswith('?'):
        if msg.admin:
            if (yes == no) or yes:
                return 'yes'
            else:
                return 'no'
        elif len(msg.args) > 3:
            return 'question'
    elif msg.words.intersection({'скучал', 'скучала', 'скучаль'}):
        return 'boring'
    elif ('мимими' in msg.text) or len(msg.args) < 4:
        return 'no-response'


def _beckett_ans(m_type, author_id):
    prob = other.rand()
    ans = None
    keys = {'sm_resp'}
    punct = True
    name_phr = False
    if m_type == 'no-response':
        ans = 'no-response'
    elif m_type in {'wlc', 'bye', 'yes', 'no', 'hi_plus', 'not_funny', 'fun_smiles'}:
        keys.add(m_type)
        name_phr = True
    elif m_type == 'love':
        if author_id == C.users['Natali']:
            ans = (emj.e_str('a_Toreador_light'), emj.e_str('a_Toreador_wave')) if prob < 0.1 else ':purple_heart:'
        else:
            ans = (':heart:', ':hearts:', ':kissing_heart:', ':relaxed:')
        ans = other.name_phr(author_id, ans, punct=False)
    elif m_type == 'apoliticality':
        keys.add(m_type)
    elif m_type == 'tremer_joke':
        ans = data.tremer_joke
    elif m_type == 'bot_dog':
        ans = com.get_t('threats', name=author_id)
    elif m_type in {'whatsup', 'question'}:
        keys = {m_type}
    elif m_type == 'boring':
        ans = other.name_phr(author_id, 'я тоже')
    else:
        ans = ''

    if ans is None:
        text = com.get_t(all_keys=keys)
        punct = punct and text not in data.sm_resp['ans_smiles']
        ans = other.name_phr(author_id, text, punct=punct) if name_phr else text

    return ans


def _data_msgs_add(msg:Msg, type_='') -> list:
    data_msgs.setdefault(msg.channel.id,{})[msg.message.id] = {'type': type_, 'ans': []}
    return data_msgs[msg.channel.id][msg.message.id]['ans']


def _data_msgs_check(msg:Msg) -> dict:
    return data_msgs.get(msg.channel.id, {}).get(msg.message.id, {})


def _data_tp_add(msg:Msg, id_:str):
    data_typings.setdefault(msg.channel.id,{})[msg.message.id] = id_


def _data_tp_check(msg:Msg) -> str:
    return data_typings.setdefault(msg.channel.id,{}).get(msg.message.id, '')


def data_tp_del(ch_id, id_):
    # noinspection PyUnusedLocal
    def fun(messages):
        o = data_typings.get(ch_id, {})
        if id_ in o:
            o.pop(id_)
    return fun
