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
            if {self.auid}.intersection({C.users['Creol'], C.users['Tony']}):
                free.add('dominate')
            cmds.intersection_update(free)

        return cmds


async def reaction(message, edit=False):
    msg = Msg(message)

    if msg.auid == C.users['bot']:
        if msg.original == data.tremer_joke:
            other.later_coro(20, msg.delete())
        return

    if msg.torpor:
        await msg.delete()
        return

    if C.roles['Silence'] in msg.roles:
        await msg.delete()
        ram.silence_ans[msg.auid] = ram.silence_ans.setdefault(msg.auid, 0) + 1
        if ram.silence_ans[msg.auid] < 4:
            await msg.answer(f'Неугодный <@{msg.auid}> пытается нам нечто сказать, но заноза в сердце мешает...')
        return

    # delete messages containing forbidden links
    if not msg.admin:
        if any(link in msg.text for link in data.forbiddenLinks):
            log.I(f'<reaction> forbidden Links')
            await msg.delete()
            await msg.answer(com.get_t('threats', name=msg.auid))
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
        if text != 'no-response':
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
    m_type = None
    embrace_or_return = False

    msg.prepare2()
    beckett_reference = bool(C.beckett_refs.intersection(msg.words))
    beckett_mention = bool(C.beckett_names.intersection(msg.words))
    beckett = beckett_reference or beckett_mention or msg.personal
    _emj_on_message(msg, beckett)

    if (ram.mute_channels.intersection({msg.channel.id, 'all'})
            or msg.auid in ram.ignore_users or msg.channel.id in C.ignore_channels):
        if msg.channel.id == C.channels['ask']:
            embrace_or_return = True
        else:
            return '', ''

    found_keys = com.check_phrase(msg.text, msg.words)
    prob = other.rand()

    # embrace
    if msg.channel.id == C.channels['ask'] and not msg.roles.intersection(C.clan_ids):
        clan_keys = list(C.clan_names.intersection(found_keys))
        if clan_keys:
            clan = other.choice(clan_keys)
            other.later_coro(other.rand(20, 50), manager.do_check_and_embrace(msg.auid, clan_name=clan))
            # get 100% to comment of chosen clan
            beckett = True
            found_keys = clan
    elif embrace_or_return:
        return '', ''

    gt = msg.check_good_time(beckett)
    if gt:
        return 'gt', gt
    elif gt == '':
        m_type = 'was-good-time no-response'

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
                    if C.roles['Primogens'] in msg.roles or prob < 0.01:
                        if other.rand() < 0.2:
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
            if not C.roles['Primogens'] in msg.roles and not msg.admin and prob < 0.2:
                return 'tableflip_phrase', com.get_t('tableflip_cmd_phrase', user=f'<@{msg.auid}>')
            else:
                return '/tableflip', '* *бросаю за <@{id}>* *\n{table}'.format(id=msg.auid,
                                                                               table=other.rand_tableflip())
        elif msg.original[1:].startswith('shrug'):
            return '/shrug', r'¯\_(ツ)_/¯'

        if beckett:
            m_type = m_type or _beckett_m_type(msg)
            ans = _beckett_ans(m_type, msg.auid)
            if ans:
                return m_type, ans

        if beckett_reference or (beckett and other.rand() < 0.25):
            m_type = 'For_Prince' if msg.auid == C.users['Natali'] and prob < 0.4 else 'beckett'
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
    if m_type is None:
        ans = ''
    elif 'no-response' in m_type:
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


def _emj_on_message(msg:Msg, beckett):
    message = msg.message
    author = msg.auid

    if author in ram.ignore_users:
        return

    pause_and_add, e, e_str = emj.pause_and_add, emj.e, emj.e_str
    prob = other.rand()

    sm_for_beckett = {
        C.users['Natali']: (*('purple_heart',) * 5, 'relaxed', 'blush',
                                                        'kissing_closed_eyes', 'kissing_heart', 'slight_smile'),
        C.users['Doriana']: ('octopus',),
        C.users['Hadley']: ('a_Toreador_light', 'a_Toreador_wave',),
        C.users['AyrinSiverna']: ('Ankh_Sabbat', 't_torik21', 'Logo_Toreador', 'hearts',),
        C.users['Rainfall']: ('green_heart',),
        C.users['Tony']: ('Logo_Ventrue',),
    }
    prob_for_beckett = {
        C.users['Natali']: 0.4,
    }
    sm_for_nothing = {
        C.users['Natali']: ('purple_heart', 'heart_eyes', 'heart_eyes_cat'),
        C.users['Doriana']: ('black_heart',),
        C.users['Hadley']: ('Logo_Toreador',),
        C.users['AyrinSiverna']: ('Logo_Toreador',),
        C.users['Rainfall']: ('racehorse',),
    }
    prob_for_nothing = {
        C.users['Natali']: 0.01,
    }
    sm_by_jiznbol = ('((', 'Т_Т', 'T_T', ':С', ':C', '😭', '😢', '😣', '😖', '😫', '😩', 's_blood_cry')
    sm_by_fun = ('))', ':D', 'XD', '😃', '😁', '😀', '😄', 'm_wafer', 'm_Tilia_fase', '😂', '😆', '😹', '🤣')

    if msg.chid == C.channels['stuff'] and (message.attachments or message.embeds):
        log.jD(f'emj.in_staff, prob = {prob}.')
        if author == C.users['Natali'] and prob < 0.5:
            log.jD('Like Natali in staff')
            pause_and_add(message, ('purple_heart', 'heart_eyes', 'heart_eyes_cat', 'heartpulse'))
        elif author in {C.users['Doriana'], C.users['Tilia'], C.users['Buffy']} and prob < 0.2:
            log.jD('Like Doriana or Tilia or Buffy in staff')
            pause_and_add(message, ('heart', 'hearts', 'heart_eyes', 'black_heart'))
        elif author in {C.users['Hadley'], C.users['cycl0ne'], C.users['Magdavius']} and prob < 0.2:
            log.jD('Like Hadley or cycl0ne or Magdavius in staff')
            pause_and_add(message, ('thumbsup', 'ok_hand', 'heart_eyes_cat'))

    if prob > 0.99:
        if other.s_in_s(sm_by_jiznbol, msg.original):
            pause_and_add(message, ('t_jiznbol1', 't_jiznbol2'))
        elif other.s_in_s(sm_by_fun, msg.original):
            pause_and_add(message, ('smiley', 'slight_smile', 'grin', 'grinning', 'smile', 'upside_down'))

    if beckett and author in sm_for_beckett and prob < prob_for_beckett.get(author, 0.25):
        log.jD(f'Like {C.usernames[author]} for Beckett with chance {prob_for_beckett.get(author, 0.25)}.')
        pause_and_add(message, sm_for_beckett[author])
    elif author in sm_for_nothing and prob < prob_for_nothing.get(author, 0.005):
        log.jD(f'Like {C.usernames[author]} with chance {prob_for_nothing.get(author, 0.005)}.')
        pause_and_add(message, sm_for_nothing[author])

    # Day Events

    # if birthday user is mentioned in msg -> copy emoji from msg under this msg
    if data.day_events.intersection(message.raw_mentions):
        em_in_text = emj.get_em_names(msg.original)
        pause_and_add(message, em_in_text, 1, all_=True)
    # birthday emojis to birthday user
    if author in data.day_events:
        pause_and_add(message, ('🎂', '🍰', '🎈', '🎁', '🎊', '🎉', '💰', '💸', '💵', '💴', '💶', '💷',
                                '🖼', '🌠', '🎇', '🎆', '📯', '🆙', '🎯', '🎰', '🥇', '🏅', '🎖', '🏆', '💛',))

    if C.events['Valentine\'s Day'] in data.day_events:
        prob = other.rand()
        if author in {C.users['Natali'], C.users['Tilia']}:
            pause_and_add(message, {'❤', '💛', '💙', '💜', '❣', '💕', '💞', '💓', '💗', '💖', '💝', '♥'})
        elif prob < 0.1:
            pause_and_add(message, {'💌', '💟', })

    elif C.events['8 March'] in data.day_events:
        prob = other.rand()
        if author == C.users['Natali'] and prob < 0.1:
            pause_and_add(message, ('a_Toreador_light', 'a_Toreador_wave'))
        elif C.roles['Tzimisce'] in msg.roles:
            pause_and_add(message, 'wilted_rose')
        elif author in C.female:
            if C.roles['Toreador'] in msg.roles and prob < 0.1:
                pause_and_add(message, 'Logo_Toreador')
            else:
                pause_and_add(message, ('🌺', '🌻', '🌹', '🌷', '🌼', '🌸', '💐'))

    if C.events['Test'] in data.day_events:
        if message.server.id == C.tst_server.id:
            em_in_text = emj.get_em_names(msg.original)
            pause_and_add(message, em_in_text, 0, all_=True)
            # pause_and_add(message, '😃')

    if C.events['Test2'] in data.day_events:
        if message.server.id == C.tst_server.id:
            pause_and_add(message, 'relaxed')
