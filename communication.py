import re
import hashlib

import data as D
import constants as C
import emj
import other
import log
import local_memory as ram


good_time = {}
morning_add = {}
resp_keys = {}
resp_values = {}
resp_data = {}

msg_queue = {}
msg_args = {}
msg_type_count = {}

data_used = []


def prepare():
    log.I('Prepare communication:')
    log.jI('\t -make dictionary good_type')
    for g_key in D.good_time:
        g_period = []
        for d_type in D.good_time[g_key]:
            g_type = {'simple': set(d_type['simple']), 'check_phrases': [], 'response': []}
            if 'key' in d_type:
                for noun in d_type['key']['noun']:
                    for adj in d_type['key']['adj']:
                        g_type['check_phrases'].append(noun + ' ' + adj)
                        g_type['check_phrases'].append(adj + ' ' + noun)

            for noun in d_type['noun']:
                for adj in d_type['adj']:
                    g_type['check_phrases'].append(noun + ' ' + adj)
                    g_type['check_phrases'].append(adj + ' ' + noun)
                    g_type['response'].append(adj + ' ' + noun)
                    # g_type['response'].append(adj.title() + ' ' + noun + ', <@{name}>.')
                    # g_type['response'].append('<@{name}>, ' + adj + ' ' + noun + '.')
            g_period.append(g_type)
        good_time[g_key] = g_period

    log.jI('\t -make morning add')
    morn_add = {
        'Kuro': ':tea:', 'Natali': ':tea::chocolate_bar:', 'Soul': ':coffee:',
        'Buffy': ':sun_with_face:', 'Tilia': ':sun_with_face:',
        'Doriana': ':hugging:', 'Creol': ':hugging:',
    }
    for name in morn_add:
        if name in C.users:
            morning_add[C.users[name]] = morn_add[name]

    log.jI('\t -make resp_keys')
    # searching resp_keys can be done with regex, but test show,
    # that intersection with set(words) and "in"-check(collocations) in for-cycle are faster (≈ in 10 times)
    for key in D.dataKeys:
        keys = D.dataKeys[key]
        dct = {'words': set(), 'colls': set()}
        if isinstance(keys, dict):
            if 'clear' in keys:
                dct['words'].update(keys['clear'])
            if 'noun' in keys:
                dct['words'].update(make_words(keys['noun'], D.noun_endings))
            if 'adj' in keys:
                dct['words'].update(make_words(keys['adj'], D.adj_endings))
            if 'eng' in keys:
                dct['words'].update(make_words(keys['eng'], D.eng_endings))
            if 'clear_collocation' in keys:
                dct['colls'].update(keys['clear_collocation'])
            if 'n_c' in keys:
                for coll in keys['n_c']:
                    dct['colls'].update(make_words(make_words([coll[0]], D.noun_endings), [' ' + coll[1]]))
            if 'a_c' in keys:
                for coll in keys['a_c']:
                    dct['colls'].update(make_words(make_words([coll[0]], D.adj_endings), [' ' + coll[1]]))
        else:
            dct['words'].update(keys)
        resp_keys[key] = dct
    log.jI('\t -make resp_values & resp_data')
    for key in D.responses:
        resp_values[key] = []
        for phr in D.responses[key]:
            if isinstance(phr, str):
                h = hashlib.md5(phr.encode('utf-8')).hexdigest()
                resp_data[h] = {'text': phr}
                resp_values[key] += [h]
            elif not (isinstance(phr, dict) and 'text' in phr):
                log.jW('fail phrase in response data: ', phr)
            else:
                h = hashlib.md5(phr['text'].encode('utf-8')).hexdigest()
                resp_data[h] = phr
                resp_values[key] += [h]

    log.I('Prepare communication done.')


def check_phrase(phr, words):
    f_keys = []
    for key in resp_keys:
        f_key = resp_keys[key]['words'].intersection(words)
        if not f_key:
            for coll in resp_keys[key]['colls']:
                f_key = coll in phr
                if f_key:
                    break

        if f_key:
            f_keys += [key]

    return f_keys


def get_resp(keys):
    global data_used
    error_ans = {'text': '', 'last_key': ''}
    if not keys:
        log.E('<com.get_resp> There are no keys!')
        return error_ans

    key = keys if isinstance(keys, str) else other.choice(tuple(keys))
    if key not in resp_values:
        if not isinstance(keys, str):
            new_keys = tuple(k for k in keys if k in resp_values)
            log.E(f'<com.get_resp> There are no key "{key}" try one from {len(new_keys)} keys (all: {len(keys)}).')
            return get_resp(new_keys)
        else:
            log.E(f'<com.get_resp> There are no key "{key}"!')
            return error_ans
    elif not resp_values[key]:
        log.E(f'<com.get_resp> resp_values["{key}"] is empty!')
        return error_ans

    if len(resp_values[key]) == 1:
        d_key = resp_values[key][0]
        resp_data[d_key]['last_key'] = key
        return resp_data[d_key]

    answers = set(resp_values[key])
    answers.difference_update(data_used)

    if not answers:
        # in normal way this block will never execute
        log.W(f'<com.get_resp> answers for ["{key}"] is empty '
              f'(all_vals: {len(resp_values[key])}, data_used:{len(data_used)} )!')
        data_used = [k for k in data_used if k not in resp_values[key]]
        return get_resp(key)

    # if left one phrase -> free all of used
    if len(answers) < 2:
        data_used = [k for k in data_used if k not in resp_values[key]]
    # if left less then 1/4 of phrases -> free half (early) of used
    elif len(answers)-1 < len(resp_values[key]) >> 2:
        # cycle by data_used, because we need order by time of adding
        old_data = [k for k in data_used if k in resp_values[key]]
        free_data = old_data[0:len(old_data) >> 1]
        data_used = [k for k in data_used if k not in free_data]

    ans = other.choice(tuple(answers))
    data_used.append(ans)
    resp_data[ans]['last_key'] = key
    return resp_data[ans]
    #
    # answers = resp_values[key]
    # ans_phr = resp_data[other.choice(answers)]
    # return ans_phr


def f_gt_key(orig_phrase, tr_phrase, words, bot_mention):
    """

    :type orig_phrase: basestring
    :type tr_phrase: basestring
    :type words: set
    :param bot_mention: bool
    """
    words.difference_update(emj.em_set)
    ignore = {'вам', 'всем'}
    words.difference_update(ignore)
    skin_sm = set()
    for w in words:
        if set(w).intersection(emj.skins_set):
            skin_sm.add(w)
    words.difference_update(skin_sm)

    if (orig_phrase.count('@') > 0 and not bot_mention) or len(words) < 1:
        return False

    phr = re.sub('[ ]?' + '|'.join(ignore) + '[ ]?', ' ', tr_phrase)  # delete all words from ignore
    phr = re.sub('[ ]+', ' ', phr)  # replace more than one spaces with only one
    smiles = re.findall(r'[:][\w_]*[:]', orig_phrase)
    count_sm = len(smiles) + ''.join(smiles).count('_')
    simple = len(words) < (count_sm + 2 + bot_mention)

    for g_key in good_time:
        i = 0
        for g_type in good_time[g_key]:
            if simple and words.intersection(g_type['simple']):
                return {'g_key': g_key, 'g_type': i}

            for ch_phr in g_type['check_phrases']:
                if ch_phr in phr:
                    return {'g_key': g_key, 'g_type': i}

            i += 1

    return False


def hi(uid):
    return other.name_phr(uid, D.hello)


def welcome_msg(uid):
    return '{0}\n{1} {2}\n{3}'.format(
        hi(uid),
        '{glad_to_see} {glad_ans} {because} {pause_reason} - {pause_wait}'.
            format(glad_to_see=other.choice(D.glad_to_see), glad_ans=other.choice(D.glad_ans),
                   because=other.choice(D.because), pause_reason=other.choice(D.pause_reason),
                   pause_wait=other.choice(D.pause_wait)),
        other.choice(D.rules_and_ask).format(rules=C.channels['rules'], ask=C.channels['ask']),
        other.choice(D.welcome_finish)
    )


def comeback_msg(uid, time_out=False, clan_id=False):
    return '{0} {1}{2}'.format(other.choice(D.comeback_msg).format(name=uid),
                               D.comeback_time[time_key(time_out)] or '',
                               clan_id and '\n{0}'.format(other.choice(D.comeback_clan).format(clan=clan_id)) or ''
                               )


def time_key(t):
    if not t:
        return False

    if t < 60:
        return 'min'
    elif t < 3600:
        return 'hour'
    elif t < 86400:
        return 'day'
    elif t < 604800:
        return 'week'
    elif t < 18144000:
        return 'month'
    elif t < 220752000:
        return 'year'
    else:
        return 'years'


def bye(uid, name=''):
    return other.name_phr(uid, D.bye, name=name)


def bye_msg(uid, name=''):
    return '{bye}\n{phrase}'.format(bye=bye(uid, name), phrase=other.choice(D.bye_phrase))


def ban_msg(uid, nick=''):
    nick = nick and '(' + nick + ')'
    name = '<@{uid}>{nick}'.format(uid=uid, nick=nick)
    return '{msg}\n{comment}'.format(msg=other.choice(D.ban_msg).format(name=name), comment=other.choice(D.ban_comment))


def unban_msg(uid):
    return '{msg}\n{comment}'.format(msg=other.choice(D.unban_msg).format(name=uid),
                                     comment=other.choice(D.unban_comment))


def make_words(words, endings):
    s = set()
    for w in words:
        for end in endings:
            s.add(w + end)

    return s


def voice_event(user, channel, here='@here'):
    return other.choice(D.voice_alone_messages).format(user='<@'+user.id+'>', voice='<#'+channel.id+'>', here=here)


def voice_note(user):
    if user.id in D.voice_notions:
        return other.choice(D.voice_notions[user.id]).format(user='<@' + user.id + '>')
    else:
        return False


def write_msg(ch, text=None, emb=None, extra=0, save_obj=None, fun:callable=None, a_fun:callable=None):

    if text is None:
        ti, tn = 1, 0
    else:
        ln_text = len(text) if isinstance(text, str) else sum(len(i) for i in text)
        tn = min(1500, ln_text) / 30 + extra
        ti = 0

    ident = str(other.t2utc().timestamp())
    msg_queue.setdefault(ch.id, []).append(ident)
    msg_args[ident] = (ident, ti, tn, ch, text, emb, save_obj, fun, a_fun)
    log.D(f'write_msg[add] tn = {tn}, ti = {ti}, ident = {ident}.')
    _check_queue(ch.id)
    return ident


def rem_from_queue(ch_id, ids):
    if not ids:
        return
    ids = (ids,) if isinstance(ids, str) else ids
    queue = msg_queue.get(ch_id, [])
    for id_ in ids:
        if id_ in msg_args:
            msg_args.pop(id_)
        if id_ in queue:
            queue.remove(id_)


def _check_queue(ch_id):
    queue = msg_queue.get(ch_id, [])
    if not queue:
        return
    count = msg_type_count.get(ch_id, 0)
    if count < 1:
        if queue[0] in msg_args:
            msg_type_count[ch_id] = msg_type_count.get(ch_id, 0) + 1
            other.later_coro(0, _send_msg(*msg_args.pop(queue[0])))
        else:
            log.W('com._check_queue, lost msg with id ', queue.pop(0))
            _check_queue(ch_id)


async def _send_msg(ident, ti, tn, ch, text=None, emb=None, save_obj=None, fun:callable=None, a_fun:callable=None):

    if ident not in msg_queue.get(ch.id, []):
        msg_type_count[ch.id] = msg_type_count.get(ch.id, 1) - 1
        log.D(f'write_msg[STOP] tn = {tn}, ti = {ti}, ident = {ident}, count = {msg_type_count[ch.id]}.')
        _check_queue(ch.id)
        return

    if ti < tn:
        dt = min(tn - ti, 10)
        log.D(f'write_msg[go] tn = {tn}, ti = {ti}, dt = {dt}, ident = {ident}, count = {msg_type_count[ch.id]}.')
        await C.client.send_typing(ch)
        other.later_coro(dt, _send_msg(ident, ti + dt, tn, ch, text, emb, save_obj, fun, a_fun))
    else:
        try:
            msgs = []
            msg_queue[ch.id].remove(ident)
            msg_type_count[ch.id] = msg_type_count.get(ch.id, 1) - 1
            log.D(f'write_msg[end] ident = {ident}, count = {msg_type_count[ch.id]}.')
            for txt in other.split_text(text):
                msgs.append(await C.client.send_message(ch, content=txt, embed=emb))
            if save_obj is not None:
                if isinstance(save_obj, list):
                    save_obj += msgs
                elif isinstance(save_obj, set):
                    save_obj.update(msgs)
                elif isinstance(save_obj, dict):
                    save_obj[ident] = tuple(msgs)
                elif isinstance(save_obj, tuple): # type (dict, key)
                    save_obj[0][save_obj[1]] = tuple(msgs)
            if fun:
                fun(msgs)
            if a_fun:
                await a_fun(msgs)
        except Exception as e:
            other.pr_error(e, 'com._send_msg', 'Unexpected error')
        finally:
            _check_queue(ch.id)


async def delete_msg(message=None, ch_i=None, msg_id=None):
    if not message:
        try:
            message = await C.client.get_message(other.get_channel(ch_i), msg_id)
        except Exception as e:
            other.pr_error(e, 'com.delete_msg.get_message', 'Unexpected error')
            return
    try:
        await C.client.delete_message(message)
    except Exception as e:
        other.pr_error(e, 'com.delete_msg', 'Unexpected error')
